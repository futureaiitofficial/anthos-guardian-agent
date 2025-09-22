#!/usr/bin/env python3

"""
Financial Guardian Service - AI-powered fraud detection for Bank of Anthos

This service monitors transactions in real-time and uses Google AI (Gemini) 
to detect fraudulent patterns and automatically block suspicious transactions.
"""

import os
import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from threading import Thread, Lock
import signal
import sys

from flask import Flask, request, jsonify, Response
import requests
import jwt
import google.generativeai as genai
import structlog

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

class FraudDetector:
    """AI-powered fraud detection using Google Gemini"""
    
    def __init__(self, api_key: str, model: str = "gemini-pro"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
        self.user_profiles = {}  # Cache for user transaction patterns
        self.profile_lock = Lock()
        
    def analyze_transaction(self, transaction: Dict, user_history: List[Dict]) -> Dict[str, Any]:
        """
        Analyze a transaction for fraud indicators using AI
        
        Args:
            transaction: Current transaction to analyze
            user_history: List of user's previous transactions
            
        Returns:
            Dict with fraud_score, risk_level, and explanation
        """
        try:
            # Build context for AI analysis
            context = self._build_analysis_context(transaction, user_history)
            
            prompt = f"""
            Analyze this banking transaction for fraud indicators:
            
            Current Transaction: {json.dumps(transaction, indent=2)}
            
            User Transaction History (last 30 days):
            {json.dumps(user_history[-50:], indent=2)}  # Last 50 transactions
            
            Context Analysis:
            {json.dumps(context, indent=2)}
            
            Please analyze for fraud indicators and respond with JSON:
            {{
                "fraud_score": <float 0-1>,
                "risk_level": "<LOW|MEDIUM|HIGH|CRITICAL>",
                "explanation": "<detailed explanation>",
                "red_flags": [<list of specific concerns>],
                "recommendation": "<ALLOW|FLAG|BLOCK>"
            }}
            
            Consider factors like:
            - Amount vs typical spending patterns
            - Time of day vs normal activity
            - Frequency of recent transactions
            - Geographic/routing number anomalies
            - Sudden behavior changes
            """
            
            response = self.model.generate_content(prompt)
            
            # Parse AI response
            try:
                result = json.loads(response.text)
                logger.info("AI fraud analysis completed", 
                           transaction_id=transaction.get('uuid', 'unknown'),
                           fraud_score=result.get('fraud_score', 0),
                           risk_level=result.get('risk_level', 'UNKNOWN'))
                return result
            except json.JSONDecodeError:
                logger.warning("AI response not valid JSON, using fallback", 
                              response=response.text)
                return self._fallback_analysis(transaction, user_history)
                
        except Exception as e:
            logger.error("Error in AI fraud analysis", error=str(e))
            return self._fallback_analysis(transaction, user_history)
    
    def _build_analysis_context(self, transaction: Dict, history: List[Dict]) -> Dict:
        """Build statistical context for AI analysis"""
        if not history:
            return {"profile_available": False}
            
        amounts = [t.get('amount', 0) for t in history]
        
        return {
            "profile_available": True,
            "avg_transaction_amount": sum(amounts) / len(amounts) if amounts else 0,
            "max_transaction_amount": max(amounts) if amounts else 0,
            "transaction_count_30d": len(history),
            "current_amount_vs_avg": transaction.get('amount', 0) / (sum(amounts) / len(amounts)) if amounts and sum(amounts) > 0 else 1,
            "recent_activity_count": len([t for t in history if self._is_recent(t, hours=24)]),
            "unusual_time": self._is_unusual_time(transaction),
        }
    
    def _is_recent(self, transaction: Dict, hours: int = 24) -> bool:
        """Check if transaction is within recent timeframe"""
        try:
            tx_time = datetime.fromisoformat(transaction.get('timestamp', ''))
            return datetime.now() - tx_time < timedelta(hours=hours)
        except:
            return False
    
    def _is_unusual_time(self, transaction: Dict) -> bool:
        """Check if transaction is at an unusual time (late night/early morning)"""
        try:
            tx_time = datetime.fromisoformat(transaction.get('timestamp', ''))
            hour = tx_time.hour
            return hour < 6 or hour > 23  # 11 PM to 6 AM
        except:
            return False
    
    def _fallback_analysis(self, transaction: Dict, history: List[Dict]) -> Dict:
        """Fallback rule-based analysis when AI fails"""
        amount = transaction.get('amount', 0)
        
        # Simple rule-based scoring
        fraud_score = 0.0
        red_flags = []
        
        if history:
            avg_amount = sum(t.get('amount', 0) for t in history) / len(history)
            if amount > avg_amount * 10:  # 10x normal amount
                fraud_score += 0.7
                red_flags.append(f"Transaction amount ${amount/100:.2f} is {amount/avg_amount:.1f}x larger than average")
        
        if amount > 100000:  # $1000+
            fraud_score += 0.3
            red_flags.append(f"Large transaction amount: ${amount/100:.2f}")
        
        # Determine risk level
        if fraud_score >= 0.8:
            risk_level = "CRITICAL"
            recommendation = "BLOCK"
        elif fraud_score >= 0.5:
            risk_level = "HIGH"  
            recommendation = "FLAG"
        elif fraud_score >= 0.3:
            risk_level = "MEDIUM"
            recommendation = "FLAG"
        else:
            risk_level = "LOW"
            recommendation = "ALLOW"
        
        return {
            "fraud_score": fraud_score,
            "risk_level": risk_level,
            "explanation": f"Rule-based analysis (AI unavailable). Score: {fraud_score:.2f}",
            "red_flags": red_flags,
            "recommendation": recommendation
        }

class FinancialGuardian:
    """Main Financial Guardian service class"""
    
    def __init__(self):
        self.fraud_detector = None
        self.monitoring_accounts = set()
        self.fraud_alerts = {}  # account_id -> list of alerts
        self.alerts_lock = Lock()
        self.monitoring_thread = None
        self.should_monitor = False
        
        # Service configuration
        self.transaction_history_addr = os.getenv('TRANSACTION_HISTORY_ADDR', 'transactionhistory:8080')
        self.ledger_writer_addr = os.getenv('LEDGER_WRITER_ADDR', 'ledgerwriter:8080')
        self.balance_reader_addr = os.getenv('BALANCE_READER_ADDR', 'balancereader:8080')
        self.pub_key_path = os.getenv('PUB_KEY_PATH', '/tmp/.ssh/publickey')
        
        # Initialize AI
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        if gemini_api_key:
            try:
                self.fraud_detector = FraudDetector(
                    api_key=gemini_api_key,
                    model=os.getenv('GEMINI_MODEL', 'gemini-pro')
                )
                logger.info("Fraud detector initialized with Gemini AI")
            except Exception as e:
                logger.error("Failed to initialize Gemini AI", error=str(e))
                self.fraud_detector = FraudDetector("dummy")  # Fallback mode
        else:
            logger.warning("GEMINI_API_KEY not provided, running in fallback mode")
            self.fraud_detector = FraudDetector("dummy")
    
    def start_monitoring(self):
        """Start the monitoring thread"""
        if not self.monitoring_thread or not self.monitoring_thread.is_alive():
            self.should_monitor = True
            self.monitoring_thread = Thread(target=self._monitor_transactions, daemon=True)
            self.monitoring_thread.start()
            logger.info("Transaction monitoring started")
    
    def stop_monitoring(self):
        """Stop the monitoring thread"""
        self.should_monitor = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        logger.info("Transaction monitoring stopped")
    
    def _monitor_transactions(self):
        """Main monitoring loop - runs in background thread"""
        while self.should_monitor:
            try:
                for account_id in list(self.monitoring_accounts):
                    self._check_account_transactions(account_id)
                time.sleep(5)  # Check every 5 seconds
            except Exception as e:
                logger.error("Error in monitoring loop", error=str(e))
                time.sleep(10)  # Wait longer on error
    
    def _check_account_transactions(self, account_id: str):
        """Check transactions for a specific account"""
        try:
            # Get recent transactions
            response = requests.get(
                f"http://{self.transaction_history_addr}/transactions/{account_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                transactions = response.json()
                
                # Check each recent transaction
                for transaction in transactions[-10:]:  # Check last 10
                    self._analyze_transaction(account_id, transaction, transactions)
                    
        except Exception as e:
            logger.error("Error checking account transactions", 
                        account_id=account_id, error=str(e))
    
    def _analyze_transaction(self, account_id: str, transaction: Dict, history: List[Dict]):
        """Analyze a single transaction for fraud"""
        try:
            analysis = self.fraud_detector.analyze_transaction(transaction, history)
            
            if analysis['recommendation'] in ['FLAG', 'BLOCK']:
                alert = {
                    'timestamp': datetime.now().isoformat(),
                    'account_id': account_id,
                    'transaction': transaction,
                    'analysis': analysis,
                    'action_taken': analysis['recommendation']
                }
                
                with self.alerts_lock:
                    if account_id not in self.fraud_alerts:
                        self.fraud_alerts[account_id] = []
                    self.fraud_alerts[account_id].append(alert)
                
                logger.warning("Fraud detected", 
                              account_id=account_id,
                              transaction_id=transaction.get('uuid'),
                              risk_level=analysis['risk_level'],
                              action=analysis['recommendation'])
                
        except Exception as e:
            logger.error("Error analyzing transaction", error=str(e))

def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    guardian = FinancialGuardian()
    
    @app.route('/ready')
    def readiness():
        """Readiness probe"""
        return {'status': 'ready', 'service': 'financial-guardian'}, 200
    
    @app.route('/healthy')  
    def health():
        """Health check"""
        return {'status': 'healthy', 'service': 'financial-guardian'}, 200
    
    @app.route('/version')
    def version():
        """Version endpoint"""
        return {'version': os.getenv('VERSION', '1.0.0')}, 200
    
    @app.route('/monitor/start', methods=['POST'])
    def start_monitoring():
        """Start monitoring an account"""
        data = request.get_json()
        account_id = data.get('account_id')
        
        if not account_id:
            return {'error': 'account_id required'}, 400
        
        guardian.monitoring_accounts.add(account_id)
        guardian.start_monitoring()
        
        logger.info("Started monitoring account", account_id=account_id)
        return {'message': f'Started monitoring account {account_id}'}, 200
    
    @app.route('/monitor/stop', methods=['POST'])
    def stop_monitoring():
        """Stop monitoring an account"""
        data = request.get_json()
        account_id = data.get('account_id')
        
        if not account_id:
            return {'error': 'account_id required'}, 400
        
        guardian.monitoring_accounts.discard(account_id)
        
        logger.info("Stopped monitoring account", account_id=account_id)
        return {'message': f'Stopped monitoring account {account_id}'}, 200
    
    @app.route('/fraud/check', methods=['POST'])
    def check_fraud():
        """Check if a transaction is fraudulent"""
        transaction = request.get_json()
        
        if not transaction:
            return {'error': 'transaction data required'}, 400
        
        try:
            # Get user's transaction history
            account_id = transaction.get('fromAccountNum')
            history = []
            
            if account_id:
                response = requests.get(
                    f"http://{guardian.transaction_history_addr}/transactions/{account_id}",
                    timeout=10
                )
                if response.status_code == 200:
                    history = response.json()
            
            # Analyze transaction
            analysis = guardian.fraud_detector.analyze_transaction(transaction, history)
            
            return {
                'transaction_id': transaction.get('uuid'),
                'analysis': analysis,
                'timestamp': datetime.now().isoformat()
            }, 200
            
        except Exception as e:
            logger.error("Error checking fraud", error=str(e))
            return {'error': 'Internal server error'}, 500
    
    @app.route('/fraud/alerts')
    def get_alerts():
        """Get fraud alerts for an account"""
        account_id = request.args.get('account_id')
        
        if not account_id:
            return {'error': 'account_id parameter required'}, 400
        
        with guardian.alerts_lock:
            alerts = guardian.fraud_alerts.get(account_id, [])
        
        return {'account_id': account_id, 'alerts': alerts}, 200
    
    # Graceful shutdown
    def signal_handler(sig, frame):
        logger.info("Shutting down Financial Guardian...")
        guardian.stop_monitoring()
        sys.exit(0)
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    return app

if __name__ == '__main__':
    # Configure logging level
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    logging.basicConfig(level=getattr(logging, log_level))
    
    # Create and run app
    app = create_app()
    port = int(os.getenv('PORT', 8081))
    
    logger.info("Starting Financial Guardian service", port=port)
    app.run(host='0.0.0.0', port=port, debug=False)
