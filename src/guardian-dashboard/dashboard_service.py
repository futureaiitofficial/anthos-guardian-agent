#!/usr/bin/env python3

"""
Guardian Command Center - Real-time AI Agent Conversation Dashboard
Aggregates and visualizes communication between Financial, Ops, and Explainer agents
"""

import os
import json
import asyncio
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict, deque

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
import structlog
from pydantic import BaseModel

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

# Pydantic Models
class AgentMessage(BaseModel):
    id: str
    timestamp: datetime
    from_agent: str
    to_agent: Optional[str]
    message_type: str  # conversation, api_call, alert, coordination
    content: str
    correlation_id: Optional[str] = None
    metadata: Dict[str, Any] = {}

class APICall(BaseModel):
    id: str
    timestamp: datetime
    service: str
    method: str
    endpoint: str
    request_data: Dict[str, Any]
    response_data: Dict[str, Any]
    duration_ms: int
    status_code: int
    correlation_id: Optional[str] = None

class AgentState(BaseModel):
    agent_name: str
    status: str  # active, paused, error
    last_update: datetime
    metrics: Dict[str, Any] = {}
    active_operations: List[str] = []

class DemoScenario(BaseModel):
    id: str
    name: str
    description: str
    steps: List[Dict[str, Any]]
    expected_outcomes: List[str]

# Dashboard Service
class GuardianDashboard:
    def __init__(self):
        self.conversations = deque(maxlen=1000)  # Last 1000 messages
        self.api_calls = deque(maxlen=1000)     # Last 1000 API calls
        self.agent_states = {}
        self.active_correlations = defaultdict(list)
        self.websocket_connections = set()
        
        # Agent service URLs
        self.services = {
            "financial-guardian": os.getenv("FINANCIAL_GUARDIAN_URL", "http://financial-guardian:8081"),
            "ops-guardian": os.getenv("OPS_GUARDIAN_URL", "http://ops-guardian:8083"),
            "explainer-agent": os.getenv("EXPLAINER_AGENT_URL", "http://explainer-agent:8082")
        }
        
    async def add_conversation(self, message: AgentMessage):
        """Add a new agent conversation message"""
        self.conversations.append(message)
        
        # Group by correlation_id if present
        if message.correlation_id:
            self.active_correlations[message.correlation_id].append(message)
            
        # Broadcast to all connected WebSocket clients
        message_dict = message.dict()
        message_dict['timestamp'] = message_dict['timestamp'].isoformat()
        await self._broadcast_update("conversation", message_dict)
        
        logger.info("Agent conversation logged", 
                   from_agent=message.from_agent,
                   to_agent=message.to_agent,
                   message_type=message.message_type)
    
    async def add_api_call(self, api_call: APICall):
        """Add a new API call record"""
        self.api_calls.append(api_call)
        
        # Group by correlation_id if present
        if api_call.correlation_id:
            self.active_correlations[api_call.correlation_id].append(api_call)
            
        # Broadcast to WebSocket clients
        api_call_dict = api_call.dict()
        api_call_dict['timestamp'] = api_call_dict['timestamp'].isoformat()
        await self._broadcast_update("api_call", api_call_dict)
        
        logger.info("API call logged",
                   service=api_call.service,
                   endpoint=api_call.endpoint,
                   duration=api_call.duration_ms,
                   status=api_call.status_code)
    
    async def update_agent_state(self, state: AgentState):
        """Update agent state"""
        self.agent_states[state.agent_name] = state
        state_dict = state.dict()
        state_dict['last_update'] = state_dict['last_update'].isoformat()
        await self._broadcast_update("agent_state", state_dict)
        
        logger.info("Agent state updated", 
                   agent=state.agent_name, 
                   status=state.status)
    
    async def _broadcast_update(self, update_type: str, data: Dict[str, Any]):
        """Broadcast update to all WebSocket connections"""
        if not self.websocket_connections:
            return
            
        message = {
            "type": update_type,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Send to all connected clients
        disconnected = set()
        for websocket in self.websocket_connections:
            try:
                await websocket.send_json(message)
            except Exception:
                disconnected.add(websocket)
        
        # Remove disconnected clients
        self.websocket_connections -= disconnected
    
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get current dashboard data"""
        # Serialize conversations with proper datetime handling
        conversations = []
        for msg in list(self.conversations)[-50:]:
            msg_dict = msg.dict()
            msg_dict['timestamp'] = msg_dict['timestamp'].isoformat()
            conversations.append(msg_dict)
        
        # Serialize API calls with proper datetime handling
        api_calls = []
        for call in list(self.api_calls)[-50:]:
            call_dict = call.dict()
            call_dict['timestamp'] = call_dict['timestamp'].isoformat()
            api_calls.append(call_dict)
        
        # Serialize agent states with proper datetime handling
        agent_states = {}
        for name, state in self.agent_states.items():
            state_dict = state.dict()
            state_dict['last_update'] = state_dict['last_update'].isoformat()
            agent_states[name] = state_dict
        
        return {
            "conversations": conversations,
            "api_calls": api_calls,
            "agent_states": agent_states,
            "active_correlations": len(self.active_correlations),
            "total_conversations": len(self.conversations),
            "total_api_calls": len(self.api_calls)
        }
    
    async def monitor_agents(self):
        """Background task to monitor agent health"""
        while True:
            try:
                async with httpx.AsyncClient() as client:
                    for agent_name, url in self.services.items():
                        try:
                            # Health check
                            response = await client.get(f"{url}/ready", timeout=5.0)
                            status = "active" if response.status_code == 200 else "error"
                            
                            # Update agent state
                            await self.update_agent_state(AgentState(
                                agent_name=agent_name,
                                status=status,
                                last_update=datetime.now(timezone.utc),
                                metrics={"health_check": response.status_code}
                            ))
                            
                        except Exception as e:
                            await self.update_agent_state(AgentState(
                                agent_name=agent_name,
                                status="error",
                                last_update=datetime.now(timezone.utc),
                                metrics={"error": str(e)}
                            ))
                            
            except Exception as e:
                logger.error("Error monitoring agents", error=str(e))
                
            await asyncio.sleep(10)  # Check every 10 seconds

# Global dashboard instance
dashboard = GuardianDashboard()

# FastAPI App
app = FastAPI(title="Guardian Command Center", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for the dashboard UI
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup_event():
    """Start background monitoring"""
    asyncio.create_task(dashboard.monitor_agents())
    logger.info("Guardian Dashboard started")

@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    """Serve the main dashboard UI"""
    try:
        with open("static/dashboard.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse("""
        <html><body>
        <h1>Guardian Command Center</h1>
        <p>Dashboard UI not found. Please create static/dashboard.html</p>
        </body></html>
        """)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    dashboard.websocket_connections.add(websocket)
    
    try:
        # Send initial data
        initial_data = await dashboard.get_dashboard_data()
        await websocket.send_json({
            "type": "initial_data",
            "data": initial_data
        })
        
        # Keep connection alive
        while True:
            await websocket.receive_text()
            
    except WebSocketDisconnect:
        dashboard.websocket_connections.discard(websocket)

@app.post("/api/conversations")
async def add_conversation(message: AgentMessage):
    """Add a new agent conversation"""
    await dashboard.add_conversation(message)
    return {"status": "success"}

@app.post("/api/api-calls") 
async def add_api_call(api_call: APICall):
    """Add a new API call record"""
    await dashboard.add_api_call(api_call)
    return {"status": "success"}

@app.get("/api/dashboard-data")
async def get_dashboard_data():
    """Get current dashboard data"""
    return await dashboard.get_dashboard_data()

@app.get("/api/correlations/{correlation_id}")
async def get_correlation_data(correlation_id: str):
    """Get all events for a correlation ID"""
    events = dashboard.active_correlations.get(correlation_id, [])
    serialized_events = []
    for event in events:
        if hasattr(event, 'dict'):
            event_dict = event.dict()
            if 'timestamp' in event_dict and hasattr(event_dict['timestamp'], 'isoformat'):
                event_dict['timestamp'] = event_dict['timestamp'].isoformat()
            serialized_events.append(event_dict)
        else:
            serialized_events.append(event)
    
    return {
        "correlation_id": correlation_id,
        "events": serialized_events,
        "count": len(events)
    }

# Demo Scenarios
DEMO_SCENARIOS = [
    DemoScenario(
        id="fraud_coordination",
        name="🚨 Fraud Detection Coordination",
        description="Financial Guardian detects fraud, coordinates with Ops Guardian to pause scaling",
        steps=[
            {"action": "fraud_detection", "agent": "financial-guardian", "description": "Detect suspicious $50,000 transaction"},
            {"action": "coordination_request", "agent": "financial-guardian", "description": "Request ops coordination"},
            {"action": "scaling_pause", "agent": "ops-guardian", "description": "Pause auto-scaling during investigation"},
            {"action": "user_explanation", "agent": "explainer-agent", "description": "Generate user-friendly explanation"}
        ],
        expected_outcomes=["Transaction blocked", "Scaling paused", "User notified", "Investigation started"]
    ),
    DemoScenario(
        id="traffic_prediction",
        name="📈 Proactive Scaling",
        description="Ops Guardian predicts lunch rush, scales proactively",
        steps=[
            {"action": "pattern_detection", "agent": "ops-guardian", "description": "Detect approaching lunch rush pattern"},
            {"action": "ai_recommendation", "agent": "ops-guardian", "description": "AI recommends proactive scaling"},
            {"action": "scaling_decision", "agent": "ops-guardian", "description": "Scale frontend and transaction services"},
            {"action": "explanation_generation", "agent": "explainer-agent", "description": "Explain scaling decision"}
        ],
        expected_outcomes=["Services scaled up", "Performance maintained", "Cost optimized", "Users informed"]
    ),
    DemoScenario(
        id="multi_agent_conflict",
        name="⚖️ Priority Resolution",
        description="Agents have conflicting priorities, coordination resolves conflict",
        steps=[
            {"action": "fraud_investigation", "agent": "financial-guardian", "description": "Start fraud investigation (needs resources)"},
            {"action": "scaling_needed", "agent": "ops-guardian", "description": "High traffic detected (needs scaling)"},
            {"action": "priority_decision", "agent": "explainer-agent", "description": "Prioritize fraud investigation"},
            {"action": "coordination_explanation", "agent": "explainer-agent", "description": "Explain priority decision"}
        ],
        expected_outcomes=["Fraud prioritized", "Scaling delayed", "Resources allocated", "Decision explained"]
    )
]

@app.get("/api/demo-scenarios")
async def get_demo_scenarios():
    """Get available demo scenarios"""
    return [scenario.dict() for scenario in DEMO_SCENARIOS]

@app.post("/api/demo-scenarios/{scenario_id}/run")
async def run_demo_scenario(scenario_id: str, background_tasks: BackgroundTasks):
    """Run a demo scenario"""
    scenario = next((s for s in DEMO_SCENARIOS if s.id == scenario_id), None)
    if not scenario:
        return {"error": "Scenario not found"}
    
    background_tasks.add_task(_execute_demo_scenario, scenario)
    return {"status": "started", "scenario": scenario.dict()}

async def _execute_demo_scenario(scenario: DemoScenario):
    """Execute a demo scenario with realistic timing"""
    correlation_id = str(uuid.uuid4())
    
    logger.info("Starting demo scenario", scenario=scenario.name, correlation_id=correlation_id)
    
    # Add scenario start message
    await dashboard.add_conversation(AgentMessage(
        id=str(uuid.uuid4()),
        timestamp=datetime.now(timezone.utc),
        from_agent="demo-system",
        to_agent="all-agents",
        message_type="scenario_start",
        content=f"🎬 Starting demo scenario: {scenario.name}",
        correlation_id=correlation_id,
        metadata={"scenario_id": scenario.id}
    ))
    
    # Execute each step with realistic delays
    for i, step in enumerate(scenario.steps):
        await asyncio.sleep(2)  # 2 second delay between steps
        
        # Generate realistic conversation
        message_content = f"Step {i+1}: {step['description']}"
        
        await dashboard.add_conversation(AgentMessage(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc),
            from_agent=step["agent"],
            to_agent="coordination-system",
            message_type="demo_action",
            content=message_content,
            correlation_id=correlation_id,
            metadata={"step": i+1, "action": step["action"]}
        ))
        
        # Simulate API calls for realistic steps
        if step["action"] == "fraud_detection":
            await dashboard.add_api_call(APICall(
                id=str(uuid.uuid4()),
                timestamp=datetime.now(timezone.utc),
                service="financial-guardian",
                method="POST",
                endpoint="/fraud/check",
                request_data={"amount": 50000, "merchant": "Suspicious Store"},
                response_data={"fraud_score": 0.95, "recommendation": "BLOCK"},
                duration_ms=245,
                status_code=200,
                correlation_id=correlation_id
            ))
    
    # Scenario completion
    await asyncio.sleep(1)
    await dashboard.add_conversation(AgentMessage(
        id=str(uuid.uuid4()),
        timestamp=datetime.now(timezone.utc),
        from_agent="demo-system",
        to_agent="all-agents",
        message_type="scenario_complete",
        content=f"✅ Demo scenario completed: {scenario.name}",
        correlation_id=correlation_id,
        metadata={"outcomes": scenario.expected_outcomes}
    ))

@app.get("/ready")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "guardian-dashboard"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
