#!/usr/bin/env python3

"""
Demo Integration Examples - Show how to integrate existing agents with the dashboard
"""

import asyncio
import uuid
from dashboard_client import dashboard_client, log_conversation, log_coordination_event, log_fraud_detection, log_scaling_event

async def demo_financial_guardian_integration():
    """Example of how Financial Guardian would integrate with dashboard"""
    
    # Set agent name
    dashboard_client.set_agent_name("financial-guardian")
    
    # Simulate fraud detection workflow
    correlation_id = str(uuid.uuid4())
    
    # Step 1: Fraud detection
    await log_conversation(
        "🔍 Analyzing suspicious transaction: $50,000 to 'Suspicious Store'",
        to_agent="system",
        correlation_id=correlation_id
    )
    
    await asyncio.sleep(1)
    
    # Step 2: AI analysis
    await log_conversation(
        "🧠 Gemini AI analysis complete: High fraud probability detected",
        to_agent="system", 
        correlation_id=correlation_id
    )
    
    await asyncio.sleep(1)
    
    # Step 3: Coordination request
    await log_coordination_event(
        "Requesting ops coordination for fraud investigation",
        correlation_id=correlation_id,
        agents=["ops-guardian", "explainer-agent"]
    )
    
    await asyncio.sleep(1)
    
    # Step 4: Fraud detection result
    await log_fraud_detection(
        transaction_id="tx_123456",
        fraud_score=0.95,
        action="BLOCKED",
        correlation_id=correlation_id
    )

async def demo_ops_guardian_integration():
    """Example of how Ops Guardian would integrate with dashboard"""
    
    # Set agent name
    dashboard_client.set_agent_name("ops-guardian")
    
    # Simulate scaling workflow
    correlation_id = str(uuid.uuid4())
    
    # Step 1: Metrics analysis
    await log_conversation(
        "📊 High CPU detected: frontend service at 85% utilization",
        to_agent="system",
        correlation_id=correlation_id
    )
    
    await asyncio.sleep(1)
    
    # Step 2: AI prediction
    await log_conversation(
        "🧠 Gemini AI predicts: Lunch rush pattern detected, recommend proactive scaling",
        to_agent="system",
        correlation_id=correlation_id
    )
    
    await asyncio.sleep(1)
    
    # Step 3: Scaling decision
    await log_scaling_event(
        service="frontend",
        old_replicas=2,
        new_replicas=4,
        reason="Proactive scaling for predicted traffic surge",
        correlation_id=correlation_id
    )
    
    await asyncio.sleep(1)
    
    # Step 4: Coordination with other agents
    await log_coordination_event(
        "Notifying other agents of scaling operation",
        correlation_id=correlation_id,
        agents=["financial-guardian", "explainer-agent"]
    )

async def demo_explainer_agent_integration():
    """Example of how Explainer Agent would integrate with dashboard"""
    
    # Set agent name
    dashboard_client.set_agent_name("explainer-agent")
    
    # Simulate explanation generation
    correlation_id = str(uuid.uuid4())
    
    # Step 1: Event correlation
    await log_conversation(
        "🔗 Correlating events from multiple agents for comprehensive explanation",
        to_agent="system",
        correlation_id=correlation_id
    )
    
    await asyncio.sleep(1)
    
    # Step 2: Context enrichment
    await log_conversation(
        "🌟 Enriching explanation with Bank of Anthos transaction context",
        to_agent="system",
        correlation_id=correlation_id
    )
    
    await asyncio.sleep(1)
    
    # Step 3: User explanation generated
    await log_conversation(
        "👤 Generated user-friendly explanation: 'Your transaction was blocked for security. No action needed.'",
        to_agent="user-interface",
        correlation_id=correlation_id
    )
    
    await asyncio.sleep(1)
    
    # Step 4: Operator explanation
    await log_conversation(
        "👨‍💻 Generated operator explanation: 'Multi-agent coordination successful: Fraud blocked, scaling paused, user notified'",
        to_agent="operations-team",
        correlation_id=correlation_id
    )

async def demo_multi_agent_coordination():
    """Demonstrate complex multi-agent coordination scenario"""
    
    correlation_id = str(uuid.uuid4())
    
    # Financial Guardian starts
    dashboard_client.set_agent_name("financial-guardian")
    await log_conversation(
        "🚨 CRITICAL: Coordinated fraud attack detected across multiple accounts",
        to_agent="coordination-system",
        correlation_id=correlation_id
    )
    
    await asyncio.sleep(1)
    
    # Ops Guardian responds
    dashboard_client.set_agent_name("ops-guardian")
    await log_conversation(
        "⏸️ Received fraud alert: Pausing all auto-scaling operations to preserve investigation resources",
        to_agent="financial-guardian",
        correlation_id=correlation_id
    )
    
    await asyncio.sleep(1)
    
    # Explainer Agent coordinates
    dashboard_client.set_agent_name("explainer-agent")
    await log_conversation(
        "📢 Multi-agent coordination in progress: Fraud investigation has priority over performance optimization",
        to_agent="all-systems",
        correlation_id=correlation_id
    )
    
    await asyncio.sleep(2)
    
    # Resolution
    dashboard_client.set_agent_name("financial-guardian")
    await log_conversation(
        "✅ Fraud investigation complete: 12 transactions blocked, attack neutralized",
        to_agent="coordination-system",
        correlation_id=correlation_id
    )
    
    await asyncio.sleep(1)
    
    dashboard_client.set_agent_name("ops-guardian")
    await log_conversation(
        "▶️ Resuming normal auto-scaling operations: Investigation resources released",
        to_agent="financial-guardian",
        correlation_id=correlation_id
    )
    
    await asyncio.sleep(1)
    
    dashboard_client.set_agent_name("explainer-agent")
    await log_conversation(
        "📋 Final report: Multi-agent coordination successful. System security maintained, performance optimized.",
        to_agent="management-dashboard",
        correlation_id=correlation_id
    )

async def demo_api_monitoring():
    """Demonstrate API call monitoring"""
    
    dashboard_client.set_agent_name("financial-guardian")
    
    # Simulate API calls with realistic data
    await dashboard_client.send_api_call(
        method="POST",
        endpoint="/fraud/check",
        request_data={
            "user_id": "testuser",
            "amount": 50000,
            "merchant": "Suspicious Store",
            "location": "Unknown"
        },
        response_data={
            "fraud_score": 0.95,
            "risk_level": "CRITICAL",
            "recommendation": "BLOCK",
            "explanation": "Large amount + suspicious merchant name"
        },
        duration_ms=245,
        status_code=200,
        correlation_id=str(uuid.uuid4())
    )
    
    await asyncio.sleep(1)
    
    dashboard_client.set_agent_name("ops-guardian")
    
    await dashboard_client.send_api_call(
        method="GET",
        endpoint="/metrics",
        request_data={},
        response_data={
            "frontend": {"cpu": 85, "memory": 70, "replicas": 2},
            "transaction-history": {"cpu": 45, "memory": 60, "replicas": 1}
        },
        duration_ms=120,
        status_code=200,
        correlation_id=str(uuid.uuid4())
    )
    
    await asyncio.sleep(1)
    
    dashboard_client.set_agent_name("explainer-agent")
    
    await dashboard_client.send_api_call(
        method="POST",
        endpoint="/explain/multi-agent-scenario",
        request_data={
            "scenario_type": "fraud_coordination",
            "agents": ["financial-guardian", "ops-guardian"],
            "correlation_id": "corr_123"
        },
        response_data={
            "explanation": "Financial Guardian detected fraud and coordinated with Ops Guardian to maintain system security",
            "audience": "user",
            "confidence": 0.95
        },
        duration_ms=890,
        status_code=200,
        correlation_id=str(uuid.uuid4())
    )

async def run_all_demos():
    """Run all demo scenarios"""
    print("🎬 Starting Guardian Dashboard Demo...")
    
    # Run individual agent demos
    await demo_financial_guardian_integration()
    await asyncio.sleep(2)
    
    await demo_ops_guardian_integration()
    await asyncio.sleep(2)
    
    await demo_explainer_agent_integration()
    await asyncio.sleep(2)
    
    # Run complex coordination demo
    await demo_multi_agent_coordination()
    await asyncio.sleep(2)
    
    # Run API monitoring demo
    await demo_api_monitoring()
    
    print("✅ All demos completed!")

if __name__ == "__main__":
    # Run the demos
    asyncio.run(run_all_demos())
