# Multi-Agent Explainer Agent

The **Multi-Agent Explainer Agent** serves as the universal translator for the Bank Guardian AI system, converting technical events from multiple Guardian agents into human-readable explanations with full multi-agent context.

## What This Service Does

### Multi-Agent Event Processing
- Correlates events from Financial Guardian, Ops Guardian, and Coordinator Agent
- Generates comprehensive explanations that show the full multi-agent picture
- Handles coordination scenarios where agents work together or resolve conflicts

### Example Multi-Agent Scenario

**Input Events:**
1. **Financial Guardian**: Detects coordinated fraud attack
2. **Coordinator Agent**: Decides to pause scaling during investigation  
3. **Ops Guardian**: Receives pause instruction and maintains current capacity

**Generated Explanation:**
```
Multi-Agent Coordination

Action: Coordinated fraud response with infrastructure freeze
Involved Agents: financial-guardian, coordinator-agent, ops-guardian

What happened:
• Financial Guardian detected coordinated fraud (confidence: 96%)
• Coordinator prioritized fraud investigation over performance
• Operations Guardian paused auto-scaling to preserve evidence

Impact: 15 suspicious transactions blocked, scaling paused for 20 minutes
Next Steps: Monitor fraud investigation progress, resume scaling when cleared
```

## Architecture

### Multi-Agent Event Flow
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Financial       │    │   Explainer      │    │ Ops Guardian    │
│ Guardian        │───▶│   Agent          │◀───│ Agent           │
│                 │    │                  │    │                 │
│ • Fraud Events  │    │ • Event          │    │ • Scale Events  │
│ • Risk Analysis │    │   Correlation    │    │ • Health Events │
└─────────────────┘    │ • Cross-Agent    │    └─────────────────┘
                       │   Context        │
                       │ • Multi-Audience │
                       └──────────────────┘
                              ▲
                              │
                       ┌──────────────────┐
                       │ Coordinator      │
                       │ Agent (A2A)      │
                       │                  │
                       │ • Orchestration  │
                       │ • Priority Mgmt  │
                       └──────────────────┘
```

## Key Features

### 1. Event Correlation
- **correlation_id**: Links related events from multiple agents
- **Time-based correlation**: Groups events within 5-minute windows
- **Cross-agent context**: Enriches explanations with data from all agents

### 2. Multi-Agent Scenarios
- **Coordination**: When Coordinator Agent orchestrates multiple agents
- **Priority Conflicts**: When agents have competing priorities  
- **Cascading Actions**: When one agent's action triggers others

### 3. Audience-Specific Explanations
- **Users**: Simple, reassuring explanations about their account security
- **Operators**: Technical details about system coordination and conflicts

## API Endpoints

### Core Multi-Agent Processing

#### `POST /explain/event`
Process single agent event (with potential correlation to other agents).

**Request:**
```json
{
  "event_type": "fraud_detection",
  "source_service": "financial-guardian", 
  "severity": "high",
  "context": {
    "transaction_id": "tx_123",
    "fraud_score": 0.95,
    "action_taken": "BLOCK"
  },
  "audience": "user",
  "correlation_id": "corr_456"
}
```

#### `POST /explain/multi-agent-event`
Process multiple related events from different agents.

#### `POST /explain/coordination-event`
Handle coordination events from Coordinator Agent.

### **Multi-Agent Context**

#### `GET /explain/correlations/{correlation_id}`
Get all events for a specific correlation ID to see the full multi-agent story.

#### `GET /explain/agent-states`
Get current state of all Guardian agents and active coordinations.

#### `POST /explain/register-agent-state`
Register current state of a Guardian agent for context enrichment.

### **Dashboard & Monitoring**

#### `GET /dashboard`
Visual dashboard showing multi-agent system status and active correlations.

#### `POST /test/fraud-coordination`
Test endpoint demonstrating multi-agent fraud coordination scenario.

## 🔄 **Integration Patterns**

### **1. Event Correlation (All Agents)**
```python
# All agents include correlation_id for related events
correlation_id = str(uuid4())

# Financial Guardian sends fraud event
await explainer_client.post("/explain/event", json={
    "event_type": "fraud_detection",
    "source_service": "financial-guardian",
    "correlation_id": correlation_id,
    "context": fraud_analysis
})

# Coordinator Agent sends coordination decision
await explainer_client.post("/explain/coordination-event", json={
    "event_type": "agent_coordination",
    "source_service": "coordinator-agent", 
    "correlation_id": correlation_id,
    "context": coordination_decision
})
```

### **2. Agent State Registration**
```python
# Each agent registers its current state for context
await explainer_client.post("/explain/register-agent-state", json={
    "agent_name": "financial-guardian",
    "state": {
        "active_investigations": 3,
        "blocked_transactions": 15,
        "risk_level": "HIGH"
    }
})
```

### **3. Cross-Agent Explanations**
```python
# Financial Guardian can request explanations that include ops context
explanation = await explainer_client.post("/explain/event", json={
    "event_type": "fraud_detection",
    "context": {
        "fraud_score": 0.95,
        "requires_ops_context": True  # Include ops status in explanation
    },
    "audience": "operator"
})
```

## 🎮 **Example Multi-Agent Scenarios**

### **Scenario 1: Priority Conflict Resolution**
```json
{
  "title": "⚖️ Agent Priority Resolution",
  "summary": "Resolved conflict between fraud investigation and scaling",
  "details": "Conflict: Peak traffic scaling vs. Active fraud investigation\nDecision: Prioritized fraud investigation over performance\nReasoning: Security takes precedence over performance optimization",
  "impact": "Response times may increase by ~200ms during 15-minute investigation",
  "next_steps": ["Monitor fraud investigation progress", "Resume scaling after resolution"]
}
```

### **Scenario 2: Coordinated Security Response**  
```json
{
  "title": "🎯 Multi-Agent Coordination", 
  "summary": "Coordinated response from 3 agents to security threat",
  "details": "1. Financial Guardian detected coordinated fraud\n2. Coordinator paused all scaling operations\n3. Ops Guardian maintained defensive posture",
  "impact": "15 transactions blocked, infrastructure frozen for evidence preservation",
  "next_steps": ["Continue fraud investigation", "Resume normal operations when cleared"]
}
```

## 🚀 **Deployment**

### **Local Development**
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GEMINI_API_KEY="your_api_key"
export PORT=8082

# Run the service
python explainer_agent.py
```

### **Kubernetes Deployment**
```bash
# Deploy to Kubernetes
kubectl apply -f k8s/deployment.yaml

# Test the service
kubectl port-forward service/explainer-agent 8082:8082
curl http://localhost:8082/ready
```

### **Test Multi-Agent Coordination**
```bash
# Test fraud coordination scenario
curl -X POST http://localhost:8082/test/fraud-coordination | python3 -m json.tool
```

## 🔍 **Monitoring Multi-Agent System**

### **Dashboard**
Access the multi-agent dashboard at: `http://localhost:8082/dashboard`

Shows:
- ✅ Active Guardian agents
- 🔄 Current event correlations  
- 🤖 Multi-agent coordination status

### **Health Checks**
```bash
# Service health
curl http://localhost:8082/healthy
# Returns: {"service": "explainer-agent", "status": "healthy", "multi_agent": true}

# Agent states
curl http://localhost:8082/explain/agent-states
# Returns current state of all registered agents
```

## 🎯 **Benefits Over Single-Agent Approach**

### **1. Complete Picture**
- Users understand **why multiple systems** acted together
- Operators see **cross-agent dependencies** and conflicts
- **Coordinated explanations** rather than fragmented messages

### **2. Conflict Transparency**
- When agents disagree, users understand **the trade-offs**
- **Priority decisions** are explained clearly
- **Resolution reasoning** builds trust in the system

### **3. System-Wide Context**
- **Single source of truth** for all Guardian AI explanations
- **Consistent messaging** across all agents
- **Coordinated communication** strategy

## 🔮 **Future Integration Points**

### **Ops Guardian Integration**
```python
# When Ops Guardian is built, it will send scaling events
await explainer_client.post("/explain/event", json={
    "event_type": "system_scaling",
    "source_service": "ops-guardian",
    "context": {
        "service_name": "ledgerwriter", 
        "from_replicas": 3,
        "to_replicas": 6,
        "trigger": "cpu_threshold"
    },
    "audience": "operator"
})
```

### **Coordinator Agent Integration**
```python
# When Coordinator Agent is built, it will send coordination events  
await explainer_client.post("/explain/coordination-event", json={
    "event_type": "agent_coordination",
    "source_service": "coordinator-agent",
    "context": {
        "coordination_type": "priority_conflict",
        "decision": "prioritize_fraud_over_scaling",
        "involved_agents": ["financial-guardian", "ops-guardian"]
    },
    "audience": "operator"
})
```

## 📚 **Documentation**

- 🏗️ **[Multi-Agent Architecture](docs/MULTI_AGENT_ARCHITECTURE.md)** - Detailed multi-agent system design and coordination patterns

## 🏆 **Why This Architecture Wins**

### **Enterprise-Grade Design**
- **Microservices pattern**: Each agent focuses on its domain
- **Event-driven architecture**: Loose coupling between agents
- **Scalable**: Easy to add new Guardian agents

### **Production-Ready Features**  
- **Event correlation**: Handles complex multi-agent scenarios
- **Conflict resolution**: Explains priority decisions transparently
- **Cross-agent context**: Enriches explanations with full system state

### **Hackathon Impact**
- **Sophisticated system design** that impresses judges
- **Real-world applicability** for enterprise banking systems  
- **Complete solution** that handles the full Guardian AI ecosystem

The Multi-Agent Explainer Agent transforms your Guardian AI system from individual services into a **coordinated, intelligent banking platform** with transparent decision-making! 🚀
