# Guardian Command Center Dashboard

**Real-time AI Agent Conversation & Monitoring Dashboard**

The Guardian Command Center is a professional mission-control dashboard that visualizes real-time communication between AI Guardian agents. It provides comprehensive monitoring of Financial Guardian, Ops Guardian, and Explainer Agent coordination and activities.

---

## What Makes This Special

### Live Agent Conversations
- Real-time chat feed showing agents communicating with each other
- Correlation tracking that links related events across agents
- Human-readable messages that make AI coordination transparent
- Multi-agent scenarios that show complex coordination patterns

### API Monitoring
- Live API call visualization with request/response data
- Performance metrics including response time and status codes
- Real-time debugging of agent interactions
- JSON payload inspection for deep troubleshooting

### Interactive Demo Scenarios
- One-click demos that showcase multi-agent coordination
- Scripted scenarios perfect for presentations
- Realistic timing with authentic agent interactions
- Expected outcomes validation

### System Overview
- Agent health monitoring with live status indicators
- Correlation statistics showing system coordination
- Uptime tracking and performance metrics
- WebSocket real-time updates for instant feedback

---

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Financial      │    │   Guardian       │    │  Ops Guardian   │
│  Guardian       │───▶│   Dashboard      │◀───│  Agent          │
│                 │    │                  │    │                 │
│ • Fraud Events  │    │ • WebSocket Hub  │    │ • Scale Events  │
│ • Conversations │    │ • Event Storage  │    │ • Metrics       │
└─────────────────┘    │ • Demo Scenarios │    └─────────────────┘
                       └──────────────────┘
                              ▲
                              │
                       ┌──────────────────┐
                       │  Explainer       │
                       │  Agent           │
                       │                  │
                       │ • Explanations   │
                       │ • Correlations   │
                       └──────────────────┘
```

---

## Quick Start

### 1. Deploy Dashboard
```bash
# Deploy to Kubernetes
kubectl apply -f k8s/deployment.yaml

# Or use Skaffold for development
skaffold dev -f skaffold.yaml
```

### 2. Access Dashboard
```bash
# Port forward for local access
kubectl port-forward service/guardian-dashboard 8080:8080

# Open in browser
open http://localhost:8080
```

### 3. Run Demo Scenarios
Click the demo buttons in the dashboard:
- **Fraud Coordination**: Financial Guardian detects fraud, coordinates with Ops
- **Proactive Scaling**: Ops Guardian predicts and prevents performance issues  
- **Priority Resolution**: Agents resolve conflicting priorities intelligently

---

## Demo Scenarios

### Fraud Detection Coordination
**What happens:**
1. Financial Guardian detects suspicious $50,000 transaction
2. Requests coordination with Ops Guardian
3. Ops Guardian pauses auto-scaling during investigation
4. Explainer Agent generates user-friendly explanation
5. Transaction blocked, user notified, system secured

**Expected outcome:** Transaction blocked, scaling paused, user informed

### Proactive Traffic Scaling
**What happens:**
1. Ops Guardian detects approaching lunch rush pattern
2. AI recommends proactive scaling before performance degrades
3. Frontend and transaction services scaled up
4. Explainer Agent explains scaling decision to operators
5. Performance maintained, costs optimized

**Expected outcome:** Services scaled, performance maintained, users happy

### Multi-Agent Priority Resolution
**What happens:**
1. Financial Guardian needs resources for fraud investigation
2. Ops Guardian detects high traffic requiring scaling
3. Explainer Agent mediates priority conflict
4. Fraud investigation prioritized over performance
5. Resources allocated, decision explained

**Expected outcome:** Fraud prioritized, scaling delayed, decision transparent

---

## 🔧 **Integration with Existing Agents**

### **Method 1: Dashboard Client (Recommended)**
```python
from dashboard_client import dashboard_client, log_conversation

# Set your agent name
dashboard_client.set_agent_name("financial-guardian")

# Log conversations
await log_conversation(
    "Fraud detected on transaction tx_123",
    to_agent="ops-guardian", 
    correlation_id="corr_abc123"
)

# Log API calls automatically
await dashboard_client.send_api_call(
    method="POST",
    endpoint="/fraud/check",
    request_data={"amount": 50000},
    response_data={"fraud_score": 0.95},
    duration_ms=245,
    status_code=200
)
```

### **Method 2: Direct HTTP Integration**
```python
import httpx

async def send_to_dashboard(message):
    async with httpx.AsyncClient() as client:
        await client.post("http://guardian-dashboard:8080/api/conversations", json={
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "from_agent": "your-agent-name",
            "to_agent": "target-agent",
            "message_type": "conversation",
            "content": message,
            "correlation_id": "optional-correlation-id"
        })
```

### **Method 3: Decorator for Automatic Logging**
```python
from dashboard_client import log_api_call, dashboard_client

dashboard_client.set_agent_name("financial-guardian")

@log_api_call(dashboard_client)
async def check_fraud(transaction):
    # Your existing fraud detection logic
    return {"fraud_score": 0.95, "action": "BLOCK"}
```

---

## 📊 **API Reference**

### **WebSocket Endpoint**
```
WS /ws
```
Real-time updates for conversations, API calls, and agent states.

### **REST Endpoints**

#### **Conversations**
```bash
POST /api/conversations
{
  "from_agent": "financial-guardian",
  "to_agent": "ops-guardian", 
  "content": "Fraud detected",
  "correlation_id": "corr_123"
}
```

#### **API Calls**
```bash
POST /api/api-calls
{
  "service": "financial-guardian",
  "method": "POST",
  "endpoint": "/fraud/check",
  "request_data": {...},
  "response_data": {...},
  "duration_ms": 245,
  "status_code": 200
}
```

#### **Demo Scenarios**
```bash
# List available demos
GET /api/demo-scenarios

# Run a demo
POST /api/demo-scenarios/fraud_coordination/run
```

#### **Dashboard Data**
```bash
# Get current dashboard state
GET /api/dashboard-data

# Get correlation events
GET /api/correlations/{correlation_id}
```

---

## 🎯 **Perfect for Hackathon Demos**

### **Why Judges Will Love This:**

1. **🎬 Visual Impact**: Stunning real-time dashboard that looks like mission control
2. **🧠 AI Innovation**: Shows actual AI agents coordinating intelligently  
3. **🔗 System Integration**: Demonstrates real integration with Bank of Anthos
4. **📈 Business Value**: Clear visualization of fraud prevention and performance optimization
5. **🎮 Interactive Demo**: One-click scenarios perfect for presentations

### **Demo Script for Judges:**

```bash
# 1. Show the dashboard
open http://localhost:8080

# 2. Run fraud coordination demo
# Click "Fraud Coordination" button

# 3. Show real-time agent conversations
# Point out correlation IDs linking related events

# 4. Show API monitoring
# Highlight request/response data and performance metrics

# 5. Run scaling demo
# Click " Proactive Scaling" button

# 6. Explain multi-agent intelligence
# Show how agents coordinate and resolve conflicts
```

---

## **Development**

### **Local Development**
```bash
# Install dependencies
pip install -r requirements.txt

# Run dashboard service
python dashboard_service.py

# Run demo integration examples
python demo_integration_examples.py
```

### **Testing**
```bash
# Test WebSocket connection
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" \
  -H "Sec-WebSocket-Key: test" -H "Sec-WebSocket-Version: 13" \
  http://localhost:8080/ws

# Test conversation endpoint
curl -X POST http://localhost:8080/api/conversations \
  -H "Content-Type: application/json" \
  -d '{
    "from_agent": "test-agent",
    "content": "Test message",
    "correlation_id": "test-123"
  }'

# Test demo scenario
curl -X POST http://localhost:8080/api/demo-scenarios/fraud_coordination/run
```

### **Building and Deployment**
```bash
# Build Docker image
docker build -t guardian-dashboard .

# Deploy to Kubernetes
kubectl apply -f k8s/deployment.yaml

# Update root Skaffold config
# (Already included in bank-of-anthos/skaffold.yaml)