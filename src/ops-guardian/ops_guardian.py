"""
Ops Guardian Agent - Intelligent Infrastructure Monitoring & Auto-Scaling

This service monitors the Bank of Anthos infrastructure, predicts traffic patterns,
and makes intelligent scaling decisions while coordinating with other Guardian agents.
Think of it as your DevOps teammate who never sleeps and always knows when to scale!
"""

import os
import json
import logging
import asyncio
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from threading import Thread, Lock
import uuid

from flask import Flask, request, jsonify
import requests
import google.generativeai as genai
from kubernetes import client, config
from kubernetes.client.rest import ApiException

# Configure logging with a friendly format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

@dataclass
class ServiceMetrics:
    """Represents current metrics for a Bank of Anthos service"""
    service_name: str
    cpu_usage: float
    memory_usage: float
    current_replicas: int
    desired_replicas: int
    response_time_avg: float
    request_rate: float
    error_rate: float
    timestamp: datetime
    
    def to_dict(self):
        return {
            **asdict(self),
            'timestamp': self.timestamp.isoformat()
        }

@dataclass
class ScalingDecision:
    """Represents a scaling decision made by the AI"""
    service_name: str
    current_replicas: int
    target_replicas: int
    reason: str
    confidence: float
    coordination_needed: bool
    estimated_impact: str
    timestamp: datetime
    
    def to_dict(self):
        return {
            **asdict(self),
            'timestamp': self.timestamp.isoformat()
        }

class KubernetesMonitor:
    """Monitors Kubernetes cluster metrics and manages scaling operations"""
    
    def __init__(self):
        self.k8s_apps_v1 = None
        self.k8s_core_v1 = None
        self.metrics_cache = {}
        self.cache_lock = Lock()
        self.initialize_kubernetes()
        
        # Bank of Anthos services we monitor and can scale
        self.monitored_services = [
            'frontend', 'balancereader', 'ledgerwriter', 
            'transactionhistory', 'userservice', 'contacts'
        ]
    
    def initialize_kubernetes(self):
        """Initialize Kubernetes client - works both in-cluster and locally"""
        try:
            # Try in-cluster config first (when running in Kubernetes)
            config.load_incluster_config()
            logger.info("Using in-cluster Kubernetes configuration")
        except config.ConfigException:
            try:
                # Fall back to local kubeconfig (for development)
                config.load_kube_config()
                logger.info("Using local kubeconfig for Kubernetes access")
            except config.ConfigException as e:
                logger.error(f"Failed to load Kubernetes config: {e}")
                return
                
        self.k8s_apps_v1 = client.AppsV1Api()
        self.k8s_core_v1 = client.CoreV1Api()
        logger.info("Kubernetes client initialized successfully")
    
    def get_service_metrics(self, service_name: str) -> Optional[ServiceMetrics]:
        """Fetch current metrics for a specific service"""
        try:
            # Get deployment info
            deployment = self.k8s_apps_v1.read_namespaced_deployment(
                name=service_name, 
                namespace='default'
            )
            
            current_replicas = deployment.status.ready_replicas or 0
            desired_replicas = deployment.spec.replicas or 1
            
            # Get pod metrics (simplified - in production you'd use metrics-server)
            pods = self.k8s_core_v1.list_namespaced_pod(
                namespace='default',
                label_selector=f'app={service_name}'
            )
            
            # Calculate basic metrics
            cpu_usage = min(85.0, max(10.0, hash(service_name + str(int(time.time() / 60))) % 80 + 10))
            memory_usage = min(90.0, max(15.0, hash(service_name + str(int(time.time() / 30))) % 75 + 15))
            
            # Simulate realistic response times and request rates
            base_response_time = 100 + (hash(service_name) % 50)
            response_time_avg = base_response_time + (cpu_usage - 50) * 2
            
            request_rate = max(10, 50 + (hash(service_name + str(int(time.time() / 120))) % 100))
            error_rate = max(0, min(5, (cpu_usage - 70) * 0.5)) if cpu_usage > 70 else 0
            
            return ServiceMetrics(
                service_name=service_name,
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                current_replicas=current_replicas,
                desired_replicas=desired_replicas,
                response_time_avg=response_time_avg,
                request_rate=request_rate,
                error_rate=error_rate,
                timestamp=datetime.now(timezone.utc)
            )
            
        except ApiException as e:
            logger.warning(f"Could not fetch metrics for {service_name}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching metrics for {service_name}: {e}")
            return None
    
    def scale_service(self, service_name: str, target_replicas: int) -> bool:
        """Scale a service to the target number of replicas"""
        try:
            # Update the deployment's replica count
            body = {'spec': {'replicas': target_replicas}}
            self.k8s_apps_v1.patch_namespaced_deployment(
                name=service_name,
                namespace='default',
                body=body
            )
            
            logger.info(f"Successfully scaled {service_name} to {target_replicas} replicas")
            return True
            
        except ApiException as e:
            logger.error(f"Failed to scale {service_name}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error scaling {service_name}: {e}")
            return False

class TrafficPredictor:
    """Uses AI to predict traffic patterns and scaling needs"""
    
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.model_name = model_name
        self.genai_model = None
        self.historical_data = []
        self.initialize_ai()
    
    def initialize_ai(self):
        """Initialize Gemini AI for traffic prediction"""
        try:
            if self.api_key and self.api_key != "dummy":
                genai.configure(api_key=self.api_key)
                self.genai_model = genai.GenerativeModel(self.model_name)
                logger.info("Gemini AI initialized for traffic prediction")
            else:
                logger.warning("No valid Gemini API key - using rule-based predictions")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini AI: {e}")
            self.genai_model = None
    
    def predict_scaling_need(self, metrics: ServiceMetrics, historical_context: List[Dict]) -> ScalingDecision:
        """Predict if a service needs scaling based on current metrics and AI analysis"""
        
        # Gather context for AI analysis
        current_time = datetime.now(timezone.utc)
        hour_of_day = current_time.hour
        day_of_week = current_time.weekday()
        
        # Use AI prediction if available
        if self.genai_model:
            try:
                ai_decision = self._get_ai_scaling_decision(metrics, historical_context, hour_of_day, day_of_week)
                if ai_decision:
                    return ai_decision
            except Exception as e:
                logger.warning(f"AI prediction failed, falling back to rules: {e}")
        
        # Fallback to rule-based scaling
        return self._get_rule_based_decision(metrics, hour_of_day, day_of_week)
    
    def _get_ai_scaling_decision(self, metrics: ServiceMetrics, historical_context: List[Dict], 
                                hour: int, day: int) -> Optional[ScalingDecision]:
        """Get scaling decision from Gemini AI"""
        
        # Prepare context for the AI
        context = {
            "service": metrics.service_name,
            "current_metrics": {
                "cpu_usage": metrics.cpu_usage,
                "memory_usage": metrics.memory_usage,
                "response_time": metrics.response_time_avg,
                "request_rate": metrics.request_rate,
                "error_rate": metrics.error_rate,
                "current_replicas": metrics.current_replicas
            },
            "time_context": {
                "hour_of_day": hour,
                "day_of_week": day,
                "is_business_hours": 9 <= hour <= 17,
                "is_weekend": day >= 5
            },
            "historical_patterns": historical_context[-5:] if historical_context else []
        }
        
        prompt = f"""
        You are an expert DevOps engineer analyzing whether to scale a banking service.
        
        Service: {metrics.service_name}
        Current State:
        - CPU Usage: {metrics.cpu_usage:.1f}%
        - Memory Usage: {metrics.memory_usage:.1f}%
        - Response Time: {metrics.response_time_avg:.1f}ms
        - Request Rate: {metrics.request_rate:.1f} req/s
        - Error Rate: {metrics.error_rate:.1f}%
        - Current Replicas: {metrics.current_replicas}
        
        Time Context:
        - Hour: {hour}:00 ({"business hours" if 9 <= hour <= 17 else "off hours"})
        - Day: {"Weekend" if day >= 5 else "Weekday"}
        
        Banking Context:
        - High availability is critical for financial services
        - Scale up early to prevent customer impact
        - Consider typical banking traffic patterns (lunch rush, end-of-month, paydays)
        - Error rates above 1% are concerning for banking
        
        Decide if scaling is needed and respond with JSON:
        {{
            "should_scale": true/false,
            "target_replicas": number,
            "confidence": 0.0-1.0,
            "reason": "brief explanation",
            "coordination_needed": true/false,
            "estimated_impact": "description of expected outcome"
        }}
        """
        
        try:
            response = self.genai_model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Parse AI response (handle markdown formatting)
            if '```json' in response_text:
                start_idx = response_text.find('```json') + 7
                end_idx = response_text.find('```', start_idx)
                if end_idx != -1:
                    response_text = response_text[start_idx:end_idx].strip()
            
            ai_result = json.loads(response_text)
            
            # Validate AI response
            if not ai_result.get('should_scale', False):
                target_replicas = metrics.current_replicas
            else:
                target_replicas = max(1, min(10, ai_result.get('target_replicas', metrics.current_replicas)))
            
            return ScalingDecision(
                service_name=metrics.service_name,
                current_replicas=metrics.current_replicas,
                target_replicas=target_replicas,
                reason=ai_result.get('reason', 'AI-based scaling decision'),
                confidence=max(0.0, min(1.0, ai_result.get('confidence', 0.7))),
                coordination_needed=ai_result.get('coordination_needed', False),
                estimated_impact=ai_result.get('estimated_impact', 'Improved performance expected'),
                timestamp=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            logger.warning(f"Failed to parse AI scaling decision: {e}")
            return None
    
    def _get_rule_based_decision(self, metrics: ServiceMetrics, hour: int, day: int) -> ScalingDecision:
        """Fallback rule-based scaling decision"""
        
        should_scale_up = (
            metrics.cpu_usage > 75 or 
            metrics.memory_usage > 80 or
            metrics.response_time_avg > 500 or
            metrics.error_rate > 1.0
        )
        
        should_scale_down = (
            metrics.cpu_usage < 30 and 
            metrics.memory_usage < 40 and
            metrics.response_time_avg < 200 and
            metrics.error_rate < 0.1 and
            metrics.current_replicas > 1
        )
        
        # Business hours logic - be more conservative
        is_business_hours = 9 <= hour <= 17 and day < 5
        
        if should_scale_up:
            target_replicas = min(10, metrics.current_replicas + 1)
            reason = f"High resource usage detected (CPU: {metrics.cpu_usage:.1f}%, Memory: {metrics.memory_usage:.1f}%)"
            coordination_needed = metrics.error_rate > 2.0  # Coordinate if errors are high
        elif should_scale_down and not is_business_hours:
            target_replicas = max(1, metrics.current_replicas - 1)
            reason = f"Low resource usage during off-hours (CPU: {metrics.cpu_usage:.1f}%)"
            coordination_needed = False
        else:
            target_replicas = metrics.current_replicas
            reason = "Metrics within acceptable ranges"
            coordination_needed = False
        
        return ScalingDecision(
            service_name=metrics.service_name,
            current_replicas=metrics.current_replicas,
            target_replicas=target_replicas,
            reason=reason,
            confidence=0.8,
            coordination_needed=coordination_needed,
            estimated_impact=f"Expected to {'improve' if target_replicas > metrics.current_replicas else 'optimize'} performance",
            timestamp=datetime.now(timezone.utc)
        )

class OpsGuardian:
    """Main Ops Guardian service orchestrating monitoring and scaling"""
    
    def __init__(self):
        self.k8s_monitor = KubernetesMonitor()
        self.traffic_predictor = TrafficPredictor(
            api_key=os.getenv("GEMINI_API_KEY", "dummy"),
            model_name=os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        )
        
        self.monitoring_active = False
        self.monitoring_thread = None
        self.metrics_history = {}
        self.scaling_decisions = []
        
        # Check if auto-scaling should be disabled via environment variable
        auto_scaling_disabled = os.getenv("DISABLE_AUTO_SCALING", "true").lower() == "true"
        self.coordination_paused = auto_scaling_disabled
        self.pause_reason = "Auto-scaling disabled by DISABLE_AUTO_SCALING environment variable" if auto_scaling_disabled else ""
        
        # Integration endpoints
        self.explainer_agent_url = os.getenv("EXPLAINER_AGENT_URL", "http://explainer-agent:8082")
        self.financial_guardian_url = os.getenv("FINANCIAL_GUARDIAN_URL", "http://financial-guardian:8081")
        
        logger.info("Ops Guardian initialized and ready for intelligent infrastructure management")
    
    def start_monitoring(self):
        """Start continuous infrastructure monitoring"""
        if self.monitoring_active:
            return {"status": "already_running"}
        
        self.monitoring_active = True
        self.monitoring_thread = Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        # Register with Explainer Agent
        self._register_with_explainer()
        
        logger.info("Infrastructure monitoring started - keeping watch over your services!")
        return {"status": "monitoring_started", "message": "Ops Guardian is now watching your infrastructure"}
    
    def stop_monitoring(self):
        """Stop infrastructure monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5)
        
        logger.info("Infrastructure monitoring stopped")
        return {"status": "monitoring_stopped"}
    
    def pause_coordination(self, reason: str = "External coordination request"):
        """Pause scaling operations for coordination with other agents"""
        self.coordination_paused = True
        self.pause_reason = reason
        logger.info(f"Scaling operations paused: {reason}")
        
        # Notify Explainer Agent about the coordination
        self._notify_explainer_coordination("scaling_paused", {
            "reason": reason,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    def resume_coordination(self):
        """Resume normal scaling operations"""
        self.coordination_paused = False
        self.pause_reason = ""
        logger.info("Scaling operations resumed")
        
        # Notify Explainer Agent
        self._notify_explainer_coordination("scaling_resumed", {
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    def _monitoring_loop(self):
        """Main monitoring loop - runs continuously"""
        logger.info("Starting infrastructure monitoring loop")
        
        while self.monitoring_active:
            try:
                # Collect metrics from all monitored services
                current_metrics = {}
                for service in self.k8s_monitor.monitored_services:
                    metrics = self.k8s_monitor.get_service_metrics(service)
                    if metrics:
                        current_metrics[service] = metrics
                        
                        # Store in history
                        if service not in self.metrics_history:
                            self.metrics_history[service] = []
                        self.metrics_history[service].append(metrics.to_dict())
                        
                        # Keep only last 100 entries per service
                        if len(self.metrics_history[service]) > 100:
                            self.metrics_history[service] = self.metrics_history[service][-100:]
                
                # Make scaling decisions
                for service, metrics in current_metrics.items():
                    if not self.coordination_paused:
                        historical_context = self.metrics_history.get(service, [])
                        decision = self.traffic_predictor.predict_scaling_need(metrics, historical_context)
                        
                        if decision.target_replicas != decision.current_replicas:
                            self._execute_scaling_decision(decision)
                    
                # Sleep before next monitoring cycle
                time.sleep(30)  # Monitor every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(60)  # Wait longer on error
    
    def _execute_scaling_decision(self, decision: ScalingDecision):
        """Execute a scaling decision and handle coordination"""
        
        # Check if coordination is needed
        if decision.coordination_needed:
            # Check with Financial Guardian for any active investigations
            fraud_status = self._check_fraud_investigations()
            if fraud_status.get("active_investigations", 0) > 0:
                logger.info(f"Skipping scaling of {decision.service_name} - active fraud investigations")
                self._notify_explainer_coordination("scaling_deferred", {
                    "service": decision.service_name,
                    "reason": "Active fraud investigations take priority",
                    "decision": decision.to_dict()
                })
                return
        
        # Execute the scaling
        success = self.k8s_monitor.scale_service(decision.service_name, decision.target_replicas)
        
        if success:
            self.scaling_decisions.append(decision)
            # Keep only last 50 decisions
            if len(self.scaling_decisions) > 50:
                self.scaling_decisions = self.scaling_decisions[-50:]
            
            logger.info(f"Scaled {decision.service_name} from {decision.current_replicas} to {decision.target_replicas} replicas")
            
            # Notify Explainer Agent about the scaling event
            self._notify_explainer_event("system_scaling", {
                "service_name": decision.service_name,
                "from_replicas": decision.current_replicas,
                "to_replicas": decision.target_replicas,
                "reason": decision.reason,
                "confidence": decision.confidence,
                "estimated_impact": decision.estimated_impact
            })
        else:
            logger.error(f"Failed to scale {decision.service_name}")
    
    def _check_fraud_investigations(self) -> Dict:
        """Check with Financial Guardian for active fraud investigations"""
        try:
            response = requests.get(
                f"{self.financial_guardian_url}/fraud/alerts",
                timeout=5
            )
            if response.status_code == 200:
                alerts = response.json()
                # Count active/high-priority alerts
                active_count = len([a for a in alerts.get("alerts", []) if a.get("priority") == "high"])
                return {"active_investigations": active_count}
        except Exception as e:
            logger.warning(f"Could not check fraud investigations: {e}")
        
        return {"active_investigations": 0}
    
    def _register_with_explainer(self):
        """Register this agent with the Explainer Agent"""
        try:
            registration_data = {
                "agent_name": "ops-guardian",
                "state": {
                    "status": "active",
                    "capabilities": ["infrastructure_monitoring", "auto_scaling", "traffic_prediction"],
                    "monitored_services": self.k8s_monitor.monitored_services,
                    "coordination_enabled": True
                }
            }
            
            response = requests.post(
                f"{self.explainer_agent_url}/explain/register-agent-state",
                json=registration_data,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("Successfully registered with Explainer Agent")
            else:
                logger.warning(f"Failed to register with Explainer Agent: {response.status_code}")
                
        except Exception as e:
            logger.warning(f"Could not register with Explainer Agent: {e}")
    
    def _notify_explainer_event(self, event_type: str, context: Dict):
        """Notify Explainer Agent about scaling events"""
        try:
            event_data = {
                "event_type": event_type,
                "source_service": "ops-guardian",
                "severity": "medium",
                "context": context,
                "audience": "operator",
                "correlation_id": str(uuid.uuid4())
            }
            
            requests.post(
                f"{self.explainer_agent_url}/explain/event",
                json=event_data,
                timeout=5
            )
            
        except Exception as e:
            logger.debug(f"Could not notify Explainer Agent: {e}")
    
    def _notify_explainer_coordination(self, coordination_type: str, context: Dict):
        """Notify Explainer Agent about coordination events"""
        try:
            coordination_data = {
                "event_type": coordination_type,
                "source_service": "ops-guardian",
                "severity": "medium",
                "context": context,
                "audience": "operator",
                "coordination_details": {
                    "coordinating_with": ["financial-guardian"],
                    "coordination_type": "resource_priority",
                    "expected_conflicts": ["scaling_vs_investigation"]
                }
            }
            
            requests.post(
                f"{self.explainer_agent_url}/explain/coordination-event",
                json=coordination_data,
                timeout=5
            )
            
        except Exception as e:
            logger.debug(f"Could not notify coordination: {e}")

# Initialize the Ops Guardian
ops_guardian = OpsGuardian()

# Flask Routes
@app.route('/ready')
def ready():
    """Health check endpoint"""
    return jsonify({"service": "ops-guardian", "status": "ready"})

@app.route('/healthy')
def healthy():
    """Detailed health check"""
    health_status = {
        "service": "ops-guardian",
        "status": "healthy",
        "monitoring_active": ops_guardian.monitoring_active,
        "coordination_paused": ops_guardian.coordination_paused,
        "kubernetes_connected": ops_guardian.k8s_monitor.k8s_apps_v1 is not None,
        "ai_enabled": ops_guardian.traffic_predictor.genai_model is not None,
        "monitored_services": len(ops_guardian.k8s_monitor.monitored_services)
    }
    return jsonify(health_status)

@app.route('/monitoring/start', methods=['POST'])
def start_monitoring():
    """Start infrastructure monitoring"""
    result = ops_guardian.start_monitoring()
    return jsonify(result)

@app.route('/monitoring/stop', methods=['POST'])
def stop_monitoring():
    """Stop infrastructure monitoring"""
    result = ops_guardian.stop_monitoring()
    return jsonify(result)

@app.route('/monitoring/status')
def monitoring_status():
    """Get current monitoring status"""
    return jsonify({
        "monitoring_active": ops_guardian.monitoring_active,
        "coordination_paused": ops_guardian.coordination_paused,
        "pause_reason": ops_guardian.pause_reason,
        "monitored_services": ops_guardian.k8s_monitor.monitored_services,
        "recent_decisions": [d.to_dict() for d in ops_guardian.scaling_decisions[-10:]]
    })

@app.route('/metrics')
def get_metrics():
    """Get current infrastructure metrics"""
    current_metrics = {}
    
    for service in ops_guardian.k8s_monitor.monitored_services:
        metrics = ops_guardian.k8s_monitor.get_service_metrics(service)
        if metrics:
            current_metrics[service] = metrics.to_dict()
    
    return jsonify({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metrics": current_metrics,
        "coordination_paused": ops_guardian.coordination_paused
    })

@app.route('/scaling/decision', methods=['POST'])
def make_scaling_decision():
    """Make a scaling decision for a specific service"""
    data = request.get_json()
    service_name = data.get('service_name')
    
    if not service_name:
        return jsonify({"error": "service_name required"}), 400
    
    if service_name not in ops_guardian.k8s_monitor.monitored_services:
        return jsonify({"error": f"Service {service_name} not monitored"}), 400
    
    # Get current metrics
    metrics = ops_guardian.k8s_monitor.get_service_metrics(service_name)
    if not metrics:
        return jsonify({"error": f"Could not fetch metrics for {service_name}"}), 500
    
    # Get historical context
    historical_context = ops_guardian.metrics_history.get(service_name, [])
    
    # Make scaling decision
    decision = ops_guardian.traffic_predictor.predict_scaling_need(metrics, historical_context)
    
    return jsonify({
        "service": service_name,
        "current_metrics": metrics.to_dict(),
        "scaling_decision": decision.to_dict(),
        "will_execute": not ops_guardian.coordination_paused
    })

@app.route('/coordination/pause', methods=['POST'])
def pause_coordination():
    """Pause scaling operations for coordination"""
    data = request.get_json() or {}
    reason = data.get('reason', 'Manual coordination request')
    
    ops_guardian.pause_coordination(reason)
    return jsonify({"status": "paused", "reason": reason})

@app.route('/coordination/resume', methods=['POST'])
def resume_coordination():
    """Resume normal scaling operations"""
    ops_guardian.resume_coordination()
    return jsonify({"status": "resumed"})

@app.route('/scaling/manual', methods=['POST'])
def manual_scale():
    """Manually scale a service"""
    data = request.get_json()
    service_name = data.get('service_name')
    target_replicas = data.get('target_replicas')
    
    if not service_name or target_replicas is None:
        return jsonify({"error": "service_name and target_replicas required"}), 400
    
    if service_name not in ops_guardian.k8s_monitor.monitored_services:
        return jsonify({"error": f"Service {service_name} not monitored"}), 400
    
    target_replicas = max(1, min(10, int(target_replicas)))
    
    success = ops_guardian.k8s_monitor.scale_service(service_name, target_replicas)
    
    if success:
        # Notify about manual scaling
        ops_guardian._notify_explainer_event("manual_scaling", {
            "service_name": service_name,
            "target_replicas": target_replicas,
            "operator": "manual_request"
        })
        
        return jsonify({
            "status": "success",
            "service": service_name,
            "target_replicas": target_replicas
        })
    else:
        return jsonify({"error": f"Failed to scale {service_name}"}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8083))
    app.run(host='0.0.0.0', port=port, debug=False)
