#!/usr/bin/env python3

"""
Dashboard Client - Helper for Guardian agents to send data to the dashboard
"""

import asyncio
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import httpx
import structlog

logger = structlog.get_logger()

class DashboardClient:
    """Client for sending data to the Guardian Dashboard"""
    
    def __init__(self, dashboard_url: str = "http://guardian-dashboard:8080"):
        self.dashboard_url = dashboard_url
        self.agent_name = None
        
    def set_agent_name(self, name: str):
        """Set the agent name for this client"""
        self.agent_name = name
        
    async def send_conversation(
        self,
        message: str,
        to_agent: Optional[str] = None,
        message_type: str = "conversation",
        correlation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Send a conversation message to the dashboard"""
        if not self.agent_name:
            logger.warning("Agent name not set, skipping conversation")
            return
            
        payload = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "from_agent": self.agent_name,
            "to_agent": to_agent,
            "message_type": message_type,
            "content": message,
            "correlation_id": correlation_id,
            "metadata": metadata or {}
        }
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    f"{self.dashboard_url}/api/conversations",
                    json=payload
                )
                if response.status_code == 200:
                    logger.debug("Conversation sent to dashboard", message=message[:50])
                else:
                    logger.warning("Failed to send conversation", status=response.status_code)
        except Exception as e:
            logger.debug("Could not send conversation to dashboard", error=str(e))
    
    async def send_api_call(
        self,
        method: str,
        endpoint: str,
        request_data: Dict[str, Any],
        response_data: Dict[str, Any],
        duration_ms: int,
        status_code: int,
        correlation_id: Optional[str] = None
    ):
        """Send API call data to the dashboard"""
        if not self.agent_name:
            logger.warning("Agent name not set, skipping API call")
            return
            
        payload = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": self.agent_name,
            "method": method,
            "endpoint": endpoint,
            "request_data": request_data,
            "response_data": response_data,
            "duration_ms": duration_ms,
            "status_code": status_code,
            "correlation_id": correlation_id
        }
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    f"{self.dashboard_url}/api/api-calls",
                    json=payload
                )
                if response.status_code == 200:
                    logger.debug("API call sent to dashboard", endpoint=endpoint)
                else:
                    logger.warning("Failed to send API call", status=response.status_code)
        except Exception as e:
            logger.debug("Could not send API call to dashboard", error=str(e))

# Decorator for automatic API call logging
def log_api_call(dashboard_client: DashboardClient, correlation_id: Optional[str] = None):
    """Decorator to automatically log API calls to the dashboard"""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            start_time = asyncio.get_event_loop().time()
            
            # Extract request data from function arguments
            request_data = {}
            if hasattr(func, '__annotations__'):
                # Try to extract meaningful request data
                if 'request' in kwargs:
                    request_data = getattr(kwargs['request'], 'dict', lambda: {})()
                elif len(args) > 1:
                    request_data = {"args": str(args[1:])[:200]}
            
            try:
                result = await func(*args, **kwargs)
                end_time = asyncio.get_event_loop().time()
                duration_ms = int((end_time - start_time) * 1000)
                
                # Extract response data
                response_data = {}
                if hasattr(result, 'dict'):
                    response_data = result.dict()
                elif isinstance(result, dict):
                    response_data = result
                else:
                    response_data = {"result": str(result)[:200]}
                
                # Send to dashboard
                await dashboard_client.send_api_call(
                    method="POST",  # Assume POST for async functions
                    endpoint=f"/{func.__name__}",
                    request_data=request_data,
                    response_data=response_data,
                    duration_ms=duration_ms,
                    status_code=200,
                    correlation_id=correlation_id
                )
                
                return result
                
            except Exception as e:
                end_time = asyncio.get_event_loop().time()
                duration_ms = int((end_time - start_time) * 1000)
                
                await dashboard_client.send_api_call(
                    method="POST",
                    endpoint=f"/{func.__name__}",
                    request_data=request_data,
                    response_data={"error": str(e)},
                    duration_ms=duration_ms,
                    status_code=500,
                    correlation_id=correlation_id
                )
                
                raise
                
        def sync_wrapper(*args, **kwargs):
            # For sync functions, create a simple wrapper
            import time
            start_time = time.time()
            
            request_data = {"args": str(args[1:])[:200] if len(args) > 1 else {}}
            
            try:
                result = func(*args, **kwargs)
                end_time = time.time()
                duration_ms = int((end_time - start_time) * 1000)
                
                response_data = {}
                if hasattr(result, 'dict'):
                    response_data = result.dict()
                elif isinstance(result, dict):
                    response_data = result
                else:
                    response_data = {"result": str(result)[:200]}
                
                # Send to dashboard (sync version)
                try:
                    import requests
                    requests.post(
                        f"{dashboard_client.dashboard_url}/api/api-calls",
                        json={
                            "id": str(uuid.uuid4()),
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "service": dashboard_client.agent_name,
                            "method": "POST",
                            "endpoint": f"/{func.__name__}",
                            "request_data": request_data,
                            "response_data": response_data,
                            "duration_ms": duration_ms,
                            "status_code": 200,
                            "correlation_id": correlation_id
                        },
                        timeout=5
                    )
                except:
                    pass  # Fail silently
                
                return result
                
            except Exception as e:
                end_time = time.time()
                duration_ms = int((end_time - start_time) * 1000)
                
                try:
                    import requests
                    requests.post(
                        f"{dashboard_client.dashboard_url}/api/api-calls",
                        json={
                            "id": str(uuid.uuid4()),
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "service": dashboard_client.agent_name,
                            "method": "POST",
                            "endpoint": f"/{func.__name__}",
                            "request_data": request_data,
                            "response_data": {"error": str(e)},
                            "duration_ms": duration_ms,
                            "status_code": 500,
                            "correlation_id": correlation_id
                        },
                        timeout=5
                    )
                except:
                    pass  # Fail silently
                
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

# Global dashboard client instance
dashboard_client = DashboardClient()

# Convenience functions
async def log_conversation(message: str, to_agent: str = None, correlation_id: str = None):
    """Quick function to log a conversation message"""
    await dashboard_client.send_conversation(
        message=message,
        to_agent=to_agent,
        correlation_id=correlation_id
    )

async def log_coordination_event(message: str, correlation_id: str, agents: list):
    """Log a multi-agent coordination event"""
    await dashboard_client.send_conversation(
        message=f"🤝 Coordination: {message}",
        to_agent=", ".join(agents),
        message_type="coordination",
        correlation_id=correlation_id,
        metadata={"agents": agents}
    )

async def log_fraud_detection(transaction_id: str, fraud_score: float, action: str, correlation_id: str = None):
    """Log a fraud detection event"""
    await dashboard_client.send_conversation(
        message=f"🚨 Fraud detected: Transaction {transaction_id} (score: {fraud_score:.2f}) → {action}",
        to_agent="ops-guardian",
        message_type="fraud_alert",
        correlation_id=correlation_id,
        metadata={"transaction_id": transaction_id, "fraud_score": fraud_score, "action": action}
    )

async def log_scaling_event(service: str, old_replicas: int, new_replicas: int, reason: str, correlation_id: str = None):
    """Log a scaling event"""
    direction = "↗️" if new_replicas > old_replicas else "↘️"
    await dashboard_client.send_conversation(
        message=f"{direction} Scaling {service}: {old_replicas} → {new_replicas} replicas ({reason})",
        to_agent="financial-guardian",
        message_type="scaling_event",
        correlation_id=correlation_id,
        metadata={"service": service, "old_replicas": old_replicas, "new_replicas": new_replicas, "reason": reason}
    )
