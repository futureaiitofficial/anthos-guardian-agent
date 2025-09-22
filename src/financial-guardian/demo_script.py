#!/usr/bin/env python3
"""
Financial Guardian Demo Script
Demonstrates fraud detection capabilities with realistic scenarios
"""

import requests
import json
import time
from datetime import datetime, timedelta

# Configuration
FINANCIAL_GUARDIAN_URL = "http://localhost:8081"  # Change if deployed differently
DEMO_ACCOUNT = "alice_demo_123"

def print_banner(title):
    """Print a nice banner for demo sections"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_response(response_data, title="Response"):
    """Pretty print JSON response"""
    print(f"\n{title}:")
    print(json.dumps(response_data, indent=2))

def check_service_health():
    """Verify Financial Guardian is running"""
    print_banner("🏥 HEALTH CHECK")
    
    try:
        response = requests.get(f"{FINANCIAL_GUARDIAN_URL}/ready", timeout=5)
        if response.status_code == 200:
            print("✅ Financial Guardian is READY!")
            print_response(response.json())
        else:
            print("❌ Service not ready")
            return False
            
        response = requests.get(f"{FINANCIAL_GUARDIAN_URL}/healthy", timeout=5)
        if response.status_code == 200:
            print("✅ Financial Guardian is HEALTHY!")
            print_response(response.json())
            return True
        else:
            print("❌ Service not healthy")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to Financial Guardian: {e}")
        print("\n💡 Make sure to run:")
        print("   kubectl port-forward service/financial-guardian 8081:8081")
        return False

def start_monitoring():
    """Start monitoring the demo account"""
    print_banner("👁️ START MONITORING")
    
    payload = {"account_id": DEMO_ACCOUNT}
    
    try:
        response = requests.post(
            f"{FINANCIAL_GUARDIAN_URL}/monitor/start",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"✅ Started monitoring account: {DEMO_ACCOUNT}")
            print_response(response.json())
        else:
            print(f"❌ Failed to start monitoring: {response.status_code}")
            print_response(response.json())
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error starting monitoring: {e}")

def demo_normal_transaction():
    """Demo a normal transaction that should be allowed"""
    print_banner("✅ NORMAL TRANSACTION DEMO")
    
    transaction = {
        "fromAccountNum": DEMO_ACCOUNT,
        "fromRoutingNum": "883745000",
        "toAccountNum": "merchant_coffee_shop",
        "toRoutingNum": "883745000", 
        "amount": 550,  # $5.50 for coffee
        "timestamp": datetime.now().isoformat(),
        "uuid": f"normal_tx_{int(time.time())}"
    }
    
    print("🧾 Transaction Details:")
    print(f"   Amount: ${transaction['amount']/100:.2f}")
    print(f"   From: {transaction['fromAccountNum']}")
    print(f"   To: {transaction['toAccountNum']}")
    print(f"   Time: {transaction['timestamp']}")
    
    try:
        response = requests.post(
            f"{FINANCIAL_GUARDIAN_URL}/fraud/check",
            json=transaction,
            timeout=15
        )
        
        if response.status_code == 200:
            analysis = response.json()
            print_response(analysis, "🤖 AI Analysis")
            
            # Interpret results
            recommendation = analysis.get('analysis', {}).get('recommendation', 'UNKNOWN')
            risk_level = analysis.get('analysis', {}).get('risk_level', 'UNKNOWN')
            fraud_score = analysis.get('analysis', {}).get('fraud_score', 0)
            
            print(f"\n📊 Summary:")
            print(f"   Fraud Score: {fraud_score:.2f}/1.0")
            print(f"   Risk Level: {risk_level}")
            print(f"   Recommendation: {recommendation}")
            
            if recommendation == "ALLOW":
                print("   ✅ Transaction would be ALLOWED")
            else:
                print("   ⚠️ Unexpected result for normal transaction!")
                
        else:
            print(f"❌ Failed to analyze transaction: {response.status_code}")
            print_response(response.json())
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error analyzing transaction: {e}")

def demo_suspicious_transaction():
    """Demo a suspicious transaction that should be flagged"""
    print_banner("⚠️ SUSPICIOUS TRANSACTION DEMO")
    
    transaction = {
        "fromAccountNum": DEMO_ACCOUNT,
        "fromRoutingNum": "883745000",
        "toAccountNum": "online_casino_xyz",
        "toRoutingNum": "123456789",
        "amount": 75000,  # $750.00 - much larger than normal
        "timestamp": (datetime.now().replace(hour=23, minute=45)).isoformat(),  # Late night
        "uuid": f"suspicious_tx_{int(time.time())}"
    }
    
    print("🧾 Transaction Details:")
    print(f"   Amount: ${transaction['amount']/100:.2f} 💰")
    print(f"   From: {transaction['fromAccountNum']}")
    print(f"   To: {transaction['toAccountNum']} 🎰")
    print(f"   Time: {transaction['timestamp']} 🌙")
    
    try:
        response = requests.post(
            f"{FINANCIAL_GUARDIAN_URL}/fraud/check",
            json=transaction,
            timeout=15
        )
        
        if response.status_code == 200:
            analysis = response.json()
            print_response(analysis, "🤖 AI Analysis")
            
            # Interpret results
            analysis_data = analysis.get('analysis', {})
            recommendation = analysis_data.get('recommendation', 'UNKNOWN')
            risk_level = analysis_data.get('risk_level', 'UNKNOWN')
            fraud_score = analysis_data.get('fraud_score', 0)
            red_flags = analysis_data.get('red_flags', [])
            
            print(f"\n📊 Summary:")
            print(f"   Fraud Score: {fraud_score:.2f}/1.0")
            print(f"   Risk Level: {risk_level}")
            print(f"   Recommendation: {recommendation}")
            
            if red_flags:
                print(f"   🚩 Red Flags:")
                for flag in red_flags:
                    print(f"      • {flag}")
            
            if recommendation in ["FLAG", "BLOCK"]:
                print("   ⚠️ Transaction would be FLAGGED/BLOCKED")
            else:
                print("   ❓ AI determined this is acceptable")
                
        else:
            print(f"❌ Failed to analyze transaction: {response.status_code}")
            print_response(response.json())
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error analyzing transaction: {e}")

def demo_fraud_transaction():
    """Demo a clear fraud transaction that should be blocked"""
    print_banner("🚫 FRAUD TRANSACTION DEMO")
    
    transaction = {
        "fromAccountNum": DEMO_ACCOUNT,
        "fromRoutingNum": "883745000",
        "toAccountNum": "cash_advance_nigeria",
        "toRoutingNum": "999888777",
        "amount": 500000,  # $5,000.00 - way too large
        "timestamp": (datetime.now().replace(hour=3, minute=22)).isoformat(),  # 3:22 AM
        "uuid": f"fraud_tx_{int(time.time())}"
    }
    
    print("🧾 Transaction Details:")
    print(f"   Amount: ${transaction['amount']/100:.2f} 💸")
    print(f"   From: {transaction['fromAccountNum']}")
    print(f"   To: {transaction['toAccountNum']} 🌍")
    print(f"   Time: {transaction['timestamp']} 🌃")
    
    try:
        response = requests.post(
            f"{FINANCIAL_GUARDIAN_URL}/fraud/check",
            json=transaction,
            timeout=15
        )
        
        if response.status_code == 200:
            analysis = response.json()
            print_response(analysis, "🤖 AI Analysis")
            
            # Interpret results
            analysis_data = analysis.get('analysis', {})
            recommendation = analysis_data.get('recommendation', 'UNKNOWN')
            risk_level = analysis_data.get('risk_level', 'UNKNOWN')
            fraud_score = analysis_data.get('fraud_score', 0)
            explanation = analysis_data.get('explanation', 'No explanation provided')
            
            print(f"\n📊 Summary:")
            print(f"   Fraud Score: {fraud_score:.2f}/1.0")
            print(f"   Risk Level: {risk_level}")
            print(f"   Recommendation: {recommendation}")
            print(f"   Explanation: {explanation}")
            
            if recommendation == "BLOCK":
                print("   🚫 Transaction would be BLOCKED immediately!")
            elif recommendation == "FLAG":
                print("   ⚠️ Transaction would be FLAGGED for review")
            else:
                print("   ❓ Unexpected result - this should be blocked!")
                
        else:
            print(f"❌ Failed to analyze transaction: {response.status_code}")
            print_response(response.json())
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error analyzing transaction: {e}")

def check_fraud_alerts():
    """Check for any fraud alerts generated"""
    print_banner("📋 FRAUD ALERTS CHECK")
    
    try:
        response = requests.get(
            f"{FINANCIAL_GUARDIAN_URL}/fraud/alerts",
            params={"account_id": DEMO_ACCOUNT},
            timeout=10
        )
        
        if response.status_code == 200:
            alerts_data = response.json()
            alerts = alerts_data.get('alerts', [])
            
            if alerts:
                print(f"🚨 Found {len(alerts)} fraud alert(s) for {DEMO_ACCOUNT}")
                print_response(alerts_data)
                
                for i, alert in enumerate(alerts, 1):
                    print(f"\n   Alert #{i}:")
                    print(f"      Time: {alert.get('timestamp', 'Unknown')}")
                    print(f"      Action: {alert.get('action_taken', 'Unknown')}")
                    if 'analysis' in alert and 'risk_level' in alert['analysis']:
                        print(f"      Risk: {alert['analysis']['risk_level']}")
            else:
                print(f"📭 No fraud alerts found for {DEMO_ACCOUNT}")
                print_response(alerts_data)
                
        else:
            print(f"❌ Failed to get alerts: {response.status_code}")
            print_response(response.json())
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error getting alerts: {e}")

def stop_monitoring():
    """Stop monitoring the demo account"""
    print_banner("⏹️ STOP MONITORING")
    
    payload = {"account_id": DEMO_ACCOUNT}
    
    try:
        response = requests.post(
            f"{FINANCIAL_GUARDIAN_URL}/monitor/stop",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"✅ Stopped monitoring account: {DEMO_ACCOUNT}")
            print_response(response.json())
        else:
            print(f"❌ Failed to stop monitoring: {response.status_code}")
            print_response(response.json())
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error stopping monitoring: {e}")

def main():
    """Run the complete demo"""
    print_banner("🤖 FINANCIAL GUARDIAN DEMO")
    print("This demo shows how Financial Guardian detects fraud using AI")
    print("We'll test 3 scenarios: Normal, Suspicious, and Fraud transactions")
    
    # Check if service is running
    if not check_service_health():
        print("\n❌ Cannot proceed - Financial Guardian is not available")
        print("\n🔧 Setup Instructions:")
        print("1. Make sure Financial Guardian is deployed")
        print("2. Run: kubectl port-forward service/financial-guardian 8081:8081")
        print("3. Run this demo again")
        return
    
    # Wait a moment
    time.sleep(2)
    
    # Start monitoring
    start_monitoring()
    time.sleep(2)
    
    # Demo scenarios
    demo_normal_transaction()
    time.sleep(3)
    
    demo_suspicious_transaction() 
    time.sleep(3)
    
    demo_fraud_transaction()
    time.sleep(3)
    
    # Check alerts
    check_fraud_alerts()
    time.sleep(2)
    
    # Clean up
    stop_monitoring()
    
    print_banner("🎉 DEMO COMPLETE")
    print("Financial Guardian successfully demonstrated:")
    print("✅ Real-time fraud detection")
    print("✅ AI-powered transaction analysis") 
    print("✅ Risk-based decision making")
    print("✅ Detailed explanations")
    print("✅ Alert management")
    print("\nYour banking system is now protected by AI! 🛡️🤖")

if __name__ == "__main__":
    main()
