"""
Multi-Agent Explainer Agent - Universal Translator for Bank Guardian AI

This service generates human-readable explanations for actions taken by 
multiple Guardian AI agents, correlating events and providing comprehensive
multi-agent context for both end users and operations teams.
"""

import os
import json
import logging
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Set
from uuid import uuid4
from collections import defaultdict

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
import httpx
import google.generativeai as genai

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Multi-Agent Explainer Agent",
    description="Universal translator for Bank Guardian AI multi-agent system",
    version="2.0.0"
)

# Configuration
class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "dummy")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    PORT = int(os.getenv("PORT", "8082"))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Guardian Agent URLs
    FINANCIAL_GUARDIAN_URL = os.getenv("FINANCIAL_GUARDIAN_URL", "http://financial-guardian:8081")
    OPS_GUARDIAN_URL = os.getenv("OPS_GUARDIAN_URL", "http://ops-guardian:8083")
    COORDINATOR_AGENT_URL = os.getenv("COORDINATOR_AGENT_URL", "http://coordinator-agent:8084")

# Data Models
class AgentEvent(BaseModel):
    """Multi-agent event model"""
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    event_type: str = Field(..., description="fraud_detection, system_scaling, agent_coordination, etc.")
    source_service: str = Field(..., description="financial-guardian, ops-guardian, coordinator-agent")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    severity: str = Field(..., description="low, medium, high, critical")
    context: Dict[str, Any] = Field(..., description="Event context and details")
    audience: str = Field(..., description="user, operator, both")
    correlation_id: Optional[str] = Field(None, description="ID for correlating related events")
    
class MultiAgentExplanation(BaseModel):
    """Multi-agent explanation response"""
    explanation_id: str = Field(default_factory=lambda: str(uuid4()))
    event_ids: List[str] = Field(description="IDs of correlated events")
    correlation_id: Optional[str] = Field(None)
    audience: str
    explanation: Dict[str, Any]
    involved_agents: List[str] = Field(description="Agents involved in this scenario")
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    explanation_type: str = Field(description="single_agent, multi_agent, coordination")

class AgentState(BaseModel):
    """Current state of a Guardian agent"""
    agent_name: str
    state: Dict[str, Any]
    last_update: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Multi-Agent Event Processor
class MultiAgentEventProcessor:
    def __init__(self):
        self.event_buffer = defaultdict(list)  # correlation_id -> events
        self.correlation_window = 300  # 5 minutes
        self.agent_states = {}  # agent_name -> AgentState
        self.active_coordinations = {}  # correlation_id -> coordination info
        
    async def process_event(self, event: AgentEvent) -> MultiAgentExplanation:
        """Process event and determine if it's part of multi-agent scenario"""
        
        # Store event in buffer if it has correlation_id
        if event.correlation_id:
            self.event_buffer[event.correlation_id].append(event)
            
            # Clean old events
            await self._cleanup_old_events()
            
            # Check for correlated events
            correlated_events = self.event_buffer[event.correlation_id]
            
            if len(correlated_events) > 1:
                # Multi-agent scenario
                return await self._generate_multi_agent_explanation(event, correlated_events)
        
        # Single agent event
        return await self._generate_single_agent_explanation(event)
    
    async def _cleanup_old_events(self):
        """Remove events older than correlation window"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(seconds=self.correlation_window)
        
        for correlation_id in list(self.event_buffer.keys()):
            events = self.event_buffer[correlation_id]
            # Keep only recent events
            recent_events = [e for e in events if e.timestamp > cutoff_time]
            
            if recent_events:
                self.event_buffer[correlation_id] = recent_events
            else:
                del self.event_buffer[correlation_id]
    
    async def _generate_multi_agent_explanation(
        self, 
        current_event: AgentEvent, 
        correlated_events: List[AgentEvent]
    ) -> MultiAgentExplanation:
        """Generate explanation for multi-agent scenario"""
        
        involved_agents = list(set(e.source_service for e in correlated_events))
        
        # Determine explanation type
        if any(e.event_type == "agent_coordination" for e in correlated_events):
            explanation_type = "coordination"
        else:
            explanation_type = "multi_agent"
        
        # Generate explanation based on scenario
        if explanation_type == "coordination":
            explanation_content = await self._explain_coordination_scenario(correlated_events)
        else:
            explanation_content = await self._explain_multi_agent_scenario(correlated_events)
        
        return MultiAgentExplanation(
            event_ids=[e.event_id for e in correlated_events],
            correlation_id=current_event.correlation_id,
            audience=current_event.audience,
            explanation=explanation_content,
            involved_agents=involved_agents,
            explanation_type=explanation_type
        )
    
    async def _generate_single_agent_explanation(self, event: AgentEvent) -> MultiAgentExplanation:
        """Generate explanation for single agent event"""
        
        explanation_content = await self._explain_single_agent_event(event)
        
        return MultiAgentExplanation(
            event_ids=[event.event_id],
            audience=event.audience,
            explanation=explanation_content,
            involved_agents=[event.source_service],
            explanation_type="single_agent"
        )
    
    async def _explain_coordination_scenario(self, events: List[AgentEvent]) -> Dict[str, Any]:
        """Explain coordination between agents"""
        
        # Find the coordination event
        coord_event = next((e for e in events if e.event_type == "agent_coordination"), None)
        other_events = [e for e in events if e.event_type != "agent_coordination"]
        
        if not coord_event:
            return await self._explain_multi_agent_scenario(events)
        
        coord_context = coord_event.context
        
        # Build coordination explanation
        title = "🎯 Multi-Agent Coordination"
        
        if coord_context.get("coordination_type") == "priority_conflict":
            title = "⚖️ Agent Priority Resolution"
            
            explanation = {
                "title": title,
                "summary": f"Resolved conflict between {len(other_events)} agents",
                "details": self._build_coordination_details(coord_event, other_events),
                "reasoning": coord_context.get("reasoning", "Coordinator decision based on system priorities"),
                "impact": self._assess_coordination_impact(coord_event, other_events),
                "next_steps": self._get_coordination_next_steps(coord_event),
                "confidence": 0.95
            }
        else:
            explanation = {
                "title": title,
                "summary": f"Coordinated action involving {len(events)} agents",
                "details": self._build_multi_agent_timeline(events),
                "reasoning": "Multi-agent coordination for optimal system response",
                "impact": self._assess_multi_agent_impact(events),
                "next_steps": ["Monitor coordinated response progress"],
                "confidence": 0.9
            }
        
        return explanation
    
    async def _explain_multi_agent_scenario(self, events: List[AgentEvent]) -> Dict[str, Any]:
        """Explain multi-agent scenario without explicit coordination"""
        
        primary_event = events[0]  # Most recent or first event
        
        return {
            "title": "🔄 Multi-Agent Response",
            "summary": f"Coordinated response from {len(set(e.source_service for e in events))} agents",
            "details": self._build_multi_agent_timeline(events),
            "reasoning": "Multiple agents responded to related system conditions",
            "impact": self._assess_multi_agent_impact(events),
            "next_steps": ["Monitor multi-agent response progress"],
            "confidence": 0.85
        }
    
    async def _explain_single_agent_event(self, event: AgentEvent) -> Dict[str, Any]:
        """Explain single agent event"""
        
        if event.event_type == "fraud_detection":
            return self._explain_fraud_event(event)
        elif event.event_type == "system_scaling":
            return self._explain_scaling_event(event)
        elif event.event_type == "agent_coordination":
            return self._explain_coordination_event(event)
        else:
            return self._explain_generic_event(event)
    
    def _explain_fraud_event(self, event: AgentEvent) -> Dict[str, Any]:
        """Explain fraud detection event"""
        context = event.context
        
        if event.audience == "user":
            return {
                "title": "🛡️ Security Alert",
                "summary": f"Transaction security check completed",
                "details": f"We reviewed your transaction for security and took appropriate action based on our analysis.",
                "reasoning": "Our security systems protect your account from suspicious activity",
                "next_steps": ["Check your account activity", "Contact support if you have questions"],
                "confidence": context.get("fraud_score", 0.5)
            }
        else:  # operator
            return {
                "title": "🚨 Fraud Detection Alert",
                "summary": f"Fraud analysis completed with score {context.get('fraud_score', 'unknown')}",
                "details": self._build_fraud_details(context),
                "reasoning": "AI-powered fraud detection based on transaction patterns",
                "next_steps": ["Review fraud analysis", "Monitor user account"],
                "confidence": context.get("fraud_score", 0.5)
            }
    
    def _explain_scaling_event(self, event: AgentEvent) -> Dict[str, Any]:
        """Explain system scaling event"""
        context = event.context
        
        return {
            "title": "🚀 System Scaling",
            "summary": f"Scaled {context.get('service_name', 'service')} from {context.get('from_replicas', '?')} to {context.get('to_replicas', '?')} replicas",
            "details": self._build_scaling_details(context),
            "reasoning": f"Triggered by {context.get('trigger', 'system conditions')}",
            "next_steps": ["Monitor scaling impact", "Review performance metrics"],
            "confidence": context.get("prediction_confidence", 0.8)
        }
    
    def _explain_coordination_event(self, event: AgentEvent) -> Dict[str, Any]:
        """Explain coordination event"""
        context = event.context
        
        return {
            "title": "🤝 Agent Coordination",
            "summary": f"Coordinated {len(context.get('involved_agents', []))} agents",
            "details": context.get("decision", "Coordination decision made"),
            "reasoning": context.get("reasoning", "Multi-agent coordination required"),
            "next_steps": ["Monitor coordination outcome"],
            "confidence": 0.9
        }
    
    def _explain_generic_event(self, event: AgentEvent) -> Dict[str, Any]:
        """Fallback explanation for unknown event types"""
        return {
            "title": "📋 System Event",
            "summary": f"{event.source_service} generated {event.event_type} event",
            "details": f"Event processed with {event.severity} severity",
            "reasoning": "Automated system response",
            "next_steps": ["Review event details"],
            "confidence": 0.7
        }
    
    def _build_coordination_details(self, coord_event: AgentEvent, other_events: List[AgentEvent]) -> str:
        """Build detailed coordination explanation"""
        coord_context = coord_event.context
        
        details = []
        details.append(f"Conflict: {coord_context.get('coordination_type', 'Unknown conflict')}")
        details.append(f"Decision: {coord_context.get('decision', 'Coordination decision made')}")
        
        if coord_context.get("involved_agents"):
            details.append(f"Affected Agents: {', '.join(coord_context['involved_agents'])}")
        
        if coord_context.get("reasoning"):
            details.append(f"Reasoning: {coord_context['reasoning']}")
        
        return "\n".join(details)
    
    def _build_multi_agent_timeline(self, events: List[AgentEvent]) -> str:
        """Build timeline of multi-agent events"""
        timeline = []
        
        for i, event in enumerate(sorted(events, key=lambda e: e.timestamp)):
            timestamp = event.timestamp.strftime("%H:%M:%S")
            timeline.append(f"{i+1}. [{timestamp}] {event.source_service}: {event.event_type}")
        
        return "\n".join(timeline)
    
    def _build_fraud_details(self, context: Dict[str, Any]) -> str:
        """Build fraud detection details"""
        details = []
        
        if context.get("fraud_score"):
            details.append(f"Fraud Score: {context['fraud_score']}")
        
        if context.get("risk_level"):
            details.append(f"Risk Level: {context['risk_level']}")
        
        if context.get("action_taken"):
            details.append(f"Action: {context['action_taken']}")
        
        return "\n".join(details) if details else "Fraud analysis completed"
    
    def _build_scaling_details(self, context: Dict[str, Any]) -> str:
        """Build scaling event details"""
        details = []
        
        if context.get("trigger"):
            details.append(f"Trigger: {context['trigger']}")
        
        if context.get("prediction_confidence"):
            details.append(f"Confidence: {context['prediction_confidence']*100:.0f}%")
        
        if context.get("estimated_duration"):
            details.append(f"Duration: {context['estimated_duration']}")
        
        return "\n".join(details) if details else "System scaling completed"
    
    def _assess_coordination_impact(self, coord_event: AgentEvent, other_events: List[AgentEvent]) -> str:
        """Assess impact of coordination"""
        return f"Coordinated response involving {len(other_events)} agents"
    
    def _assess_multi_agent_impact(self, events: List[AgentEvent]) -> str:
        """Assess impact of multi-agent scenario"""
        return f"Multi-agent response with {len(events)} coordinated actions"
    
    def _get_coordination_next_steps(self, coord_event: AgentEvent) -> List[str]:
        """Get next steps for coordination"""
        coord_context = coord_event.context
        
        if coord_context.get("estimated_duration"):
            return [f"Monitor coordination for {coord_context['estimated_duration']}", "Review outcome when complete"]
        else:
            return ["Monitor coordination progress", "Review coordination outcome"]

# Global processor
processor = MultiAgentEventProcessor()

# API Endpoints
@app.on_event("startup")
async def startup():
    """Initialize services on startup"""
    logger.info("Multi-Agent Explainer Agent started", 
               extra={"port": Config.PORT, "version": "2.0.0"})

@app.get("/ready")
async def ready():
    """Readiness probe"""
    return {"service": "explainer-agent", "status": "ready", "version": "2.0.0"}

@app.get("/healthy")
async def healthy():
    """Health check"""
    return {"service": "explainer-agent", "status": "healthy", "multi_agent": True}

@app.post("/explain/event", response_model=MultiAgentExplanation)
async def explain_event(event: AgentEvent):
    """Process single agent event (with potential correlation)"""
    try:
        explanation = await processor.process_event(event)
        
        logger.info("Event explained", 
                   extra={
                       "event_id": event.event_id,
                       "explanation_id": explanation.explanation_id,
                       "explanation_type": explanation.explanation_type,
                       "involved_agents": explanation.involved_agents
                   })
        
        return explanation
        
    except Exception as e:
        logger.error("Error processing event", 
                    extra={"event_id": event.event_id, "error": str(e)})
        raise HTTPException(status_code=500, detail=f"Error processing event: {str(e)}")

@app.post("/explain/multi-agent-event", response_model=MultiAgentExplanation)
async def explain_multi_agent_event(events: List[AgentEvent]):
    """Process multiple related events from different agents"""
    try:
        # Assign same correlation_id if not present
        correlation_id = events[0].correlation_id or str(uuid4())
        
        for event in events:
            if not event.correlation_id:
                event.correlation_id = correlation_id
        
        # Process all events
        explanations = []
        for event in events:
            explanation = await processor.process_event(event)
            explanations.append(explanation)
        
        # Return the most comprehensive explanation (likely the last one)
        return explanations[-1]
        
    except Exception as e:
        logger.error("Error processing multi-agent events", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail=f"Error processing multi-agent events: {str(e)}")

@app.post("/explain/coordination-event", response_model=MultiAgentExplanation)
async def explain_coordination_event(event: AgentEvent):
    """Handle coordination events from Coordinator Agent"""
    try:
        # Ensure this is marked as coordination event
        if event.event_type != "agent_coordination":
            event.event_type = "agent_coordination"
        
        explanation = await processor.process_event(event)
        
        logger.info("Coordination event explained",
                   extra={
                       "event_id": event.event_id,
                       "correlation_id": event.correlation_id,
                       "involved_agents": event.context.get("involved_agents", [])
                   })
        
        return explanation
        
    except Exception as e:
        logger.error("Error processing coordination event", 
                    extra={"event_id": event.event_id, "error": str(e)})
        raise HTTPException(status_code=500, detail=f"Error processing coordination: {str(e)}")

@app.get("/explain/correlations/{correlation_id}")
async def get_correlation_events(correlation_id: str):
    """Get all events for a specific correlation ID"""
    events = processor.event_buffer.get(correlation_id, [])
    
    return {
        "correlation_id": correlation_id,
        "events": events,
        "count": len(events),
        "involved_agents": list(set(e.source_service for e in events))
    }

@app.get("/explain/agent-states")
async def get_agent_states():
    """Get current state of all Guardian agents"""
    return {
        "agent_states": processor.agent_states,
        "active_coordinations": len(processor.active_coordinations),
        "buffered_correlations": len(processor.event_buffer)
    }

@app.post("/explain/register-agent-state")
async def register_agent_state(agent_state: AgentState):
    """Register current state of a Guardian agent"""
    processor.agent_states[agent_state.agent_name] = agent_state
    
    logger.info("Agent state registered",
               extra={"agent": agent_state.agent_name, "state_keys": list(agent_state.state.keys())})
    
    return {"status": "registered", "agent": agent_state.agent_name}

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Multi-agent explanation dashboard"""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Multi-Agent Explainer Dashboard</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
            .status {{ margin: 20px 0; }}
            .agents {{ display: flex; gap: 20px; margin: 20px 0; }}
            .agent {{ background-color: #e8f4fd; padding: 15px; border-radius: 5px; flex: 1; }}
            .correlations {{ background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 10px 0; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🎯 Multi-Agent Explainer</h1>
            <p>Universal Translator for Bank Guardian AI System</p>
        </div>
        
        <div class="status">
            <h2>System Status</h2>
            <p>✅ Multi-Agent Processing Active</p>
            <p>🔄 Active Correlations: {len(processor.event_buffer)}</p>
            <p>🤖 Registered Agents: {len(processor.agent_states)}</p>
        </div>
        
        <div class="agents">
            <div class="agent">
                <h3>Financial Guardian</h3>
                <p>Status: {"✅ Active" if "financial-guardian" in processor.agent_states else "⏸️ Not Registered"}</p>
                <p>Events: Fraud Detection, Risk Analysis</p>
            </div>
            <div class="agent">
                <h3>Ops Guardian</h3>
                <p>Status: {"✅ Active" if "ops-guardian" in processor.agent_states else "⏸️ Not Registered"}</p>
                <p>Events: System Scaling, Health Monitoring</p>
            </div>
            <div class="agent">
                <h3>Coordinator Agent</h3>
                <p>Status: {"✅ Active" if "coordinator-agent" in processor.agent_states else "⏸️ Not Registered"}</p>
                <p>Events: Agent Coordination, Priority Resolution</p>
            </div>
        </div>
        
        <div class="correlations">
            <h3>🔗 Active Event Correlations</h3>
            <p>Multi-agent scenarios currently being tracked: {len(processor.event_buffer)}</p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# Test endpoints for development
@app.post("/test/fraud-coordination")
async def test_fraud_coordination():
    """Test multi-agent fraud coordination scenario"""
    correlation_id = str(uuid4())
    
    # Simulate Financial Guardian fraud detection
    fraud_event = AgentEvent(
        event_type="fraud_detection",
        source_service="financial-guardian",
        severity="high",
        context={
            "transaction_id": "tx_123",
            "user_id": "user_456",
            "fraud_score": 0.95,
            "action_taken": "BLOCK"
        },
        audience="operator",
        correlation_id=correlation_id
    )
    
    # Simulate Coordinator Agent coordination
    coord_event = AgentEvent(
        event_type="agent_coordination",
        source_service="coordinator-agent",
        severity="medium",
        context={
            "coordination_type": "fraud_response",
            "involved_agents": ["financial-guardian", "ops-guardian"],
            "decision": "pause_scaling_during_investigation",
            "reasoning": "Preserve system state for fraud investigation"
        },
        audience="operator",
        correlation_id=correlation_id
    )
    
    # Process events
    fraud_explanation = await explain_event(fraud_event)
    coord_explanation = await explain_event(coord_event)
    
    return {
        "scenario": "fraud_coordination",
        "correlation_id": correlation_id,
        "fraud_explanation": fraud_explanation,
        "coordination_explanation": coord_explanation
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=Config.PORT)
