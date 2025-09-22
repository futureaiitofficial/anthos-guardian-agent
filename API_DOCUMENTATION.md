# Bank Guardian AI - API Documentation

## Financial Guardian Agent (Port: 8081)

### Health Endpoints

**GET /ready**
```bash
curl http://financial-guardian:8081/ready
```
Response:
```json
{
  "status": "ready",
  "service": "financial-guardian"
}
```

**GET /healthy**
```bash
curl http://financial-guardian:8081/healthy
```
Response:
```json
{
  "status": "healthy",
  "service": "financial-guardian"
}
```

### Monitoring Endpoints

**POST /monitor/start**
Start monitoring a specific account for fraudulent activity.
```bash
curl -X POST http://financial-guardian:8081/monitor/start \
  -H "Content-Type: application/json" \
  -d '{"account_id": "1011226111"}'
```
Response:
```json
{
  "message": "Started monitoring account 1011226111"
}
```

**POST /monitor/stop**
Stop monitoring a specific account.
```bash
curl -X POST http://financial-guardian:8081/monitor/stop \
  -H "Content-Type: application/json" \
  -d '{"account_id": "1011226111"}'
```
Response:
```json
{
  "message": "Stopped monitoring account 1011226111"
}
```

### Fraud Detection Endpoints

**POST /fraud/check**
Analyze a transaction for potential fraud using AI.
```bash
curl -X POST http://financial-guardian:8081/fraud/check \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user",
    "amount": 50000,
    "merchant": "Electronics Store",
    "location": "New York",
    "fromAccountNum": "1011226111",
    "toAccountNum": "1033623433",
    "timestamp": "2025-01-15T10:30:00Z"
  }'
```
Response:
```json
{
  "transaction_id": null,
  "analysis": {
    "fraud_score": 0.85,
    "risk_level": "HIGH",
    "explanation": "Transaction amount is significantly larger than user's typical spending pattern",
    "red_flags": [
      "Amount 25x larger than average transaction",
      "Unusual merchant category for user"
    ],
    "recommendation": "FLAG"
  },
  "user_explanation": {
    "title": "Transaction Flagged",
    "summary": "Your $500 transaction to Electronics Store was flagged for review",
    "explanation": "We flagged this transaction because it's 25× larger than your usual $20 purchases.",
    "next_steps": [
      "Your transaction is being reviewed for security",
      "You'll receive an update within 24 hours"
    ]
  },
  "timestamp": "2025-01-15T10:30:15.123456"
}
```

**GET /fraud/alerts**
Get fraud alerts for a specific account.
```bash
curl "http://financial-guardian:8081/fraud/alerts?account_id=1011226111"
```
Response:
```json
{
  "account_id": "1011226111",
  "alerts": [
    {
      "timestamp": "2025-01-15T10:30:00Z",
      "analysis": {
        "risk_level": "HIGH",
        "fraud_score": 0.85
      },
      "action_taken": "FLAG"
    }
  ]
}
```

## Ops Guardian Agent (Port: 8083)

### Health Endpoints

**GET /ready**
```bash
curl http://ops-guardian:8083/ready
```
Response:
```json
{
  "service": "ops-guardian",
  "status": "ready"
}
```

**GET /healthy**
```bash
curl http://ops-guardian:8083/healthy
```
Response:
```json
{
  "service": "ops-guardian",
  "status": "healthy",
  "monitoring_active": true,
  "coordination_paused": false,
  "kubernetes_connected": true,
  "ai_enabled": true,
  "monitored_services": 6
}
```

### Monitoring Endpoints

**POST /monitoring/start**
Start infrastructure monitoring.
```bash
curl -X POST http://ops-guardian:8083/monitoring/start
```
Response:
```json
{
  "status": "monitoring_started",
  "message": "Ops Guardian is now watching your infrastructure"
}
```

**POST /monitoring/stop**
Stop infrastructure monitoring.
```bash
curl -X POST http://ops-guardian:8083/monitoring/stop
```
Response:
```json
{
  "status": "monitoring_stopped"
}
```

**GET /monitoring/status**
Get current monitoring status.
```bash
curl http://ops-guardian:8083/monitoring/status
```
Response:
```json
{
  "monitoring_active": true,
  "coordination_paused": false,
  "pause_reason": "",
  "monitored_services": ["frontend", "balancereader", "ledgerwriter"],
  "recent_decisions": []
}
```

### Metrics Endpoints

**GET /metrics**
Get current infrastructure metrics for all monitored services.
```bash
curl http://ops-guardian:8083/metrics
```
Response:
```json
{
  "timestamp": "2025-01-15T10:30:00Z",
  "metrics": {
    "frontend": {
      "service_name": "frontend",
      "cpu_usage": 45.2,
      "memory_usage": 32.1,
      "current_replicas": 2,
      "desired_replicas": 2,
      "response_time_avg": 150.5,
      "request_rate": 25.3,
      "error_rate": 0.1
    }
  },
  "coordination_paused": false
}
```

### Scaling Endpoints

**POST /scaling/decision**
Get AI scaling recommendation for a service.
```bash
curl -X POST http://ops-guardian:8083/scaling/decision \
  -H "Content-Type: application/json" \
  -d '{"service_name": "frontend"}'
```
Response:
```json
{
  "service": "frontend",
  "current_metrics": {
    "cpu_usage": 75.5,
    "memory_usage": 68.2,
    "current_replicas": 2
  },
  "scaling_decision": {
    "target_replicas": 3,
    "reason": "High CPU usage detected (75.5%)",
    "confidence": 0.9,
    "coordination_needed": false
  },
  "will_execute": true
}
```

**POST /scaling/manual**
Manually scale a service.
```bash
curl -X POST http://ops-guardian:8083/scaling/manual \
  -H "Content-Type: application/json" \
  -d '{"service_name": "frontend", "target_replicas": 3}'
```
Response:
```json
{
  "status": "success",
  "service": "frontend",
  "target_replicas": 3
}
```

### Coordination Endpoints

**POST /coordination/pause**
Pause scaling operations for coordination with other agents.
```bash
curl -X POST http://ops-guardian:8083/coordination/pause \
  -H "Content-Type: application/json" \
  -d '{"reason": "Active fraud investigation"}'
```
Response:
```json
{
  "status": "paused",
  "reason": "Active fraud investigation"
}
```

**POST /coordination/resume**
Resume normal scaling operations.
```bash
curl -X POST http://ops-guardian:8083/coordination/resume
```
Response:
```json
{
  "status": "resumed"
}
```

## Explainer Agent (Port: 8082)

### Health Endpoints

**GET /ready**
```bash
curl http://explainer-agent:8082/ready
```
Response:
```json
{
  "service": "explainer-agent",
  "status": "ready",
  "version": "2.0.0"
}
```

**GET /healthy**
```bash
curl http://explainer-agent:8082/healthy
```
Response:
```json
{
  "service": "explainer-agent",
  "status": "healthy",
  "multi_agent": true
}
```

### Explanation Endpoints

**POST /explain/event**
Generate explanation for a single agent event.
```bash
curl -X POST http://explainer-agent:8082/explain/event \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "fraud_detection",
    "source_service": "financial-guardian",
    "severity": "high",
    "context": {
      "transaction_id": "tx_123",
      "fraud_score": 0.95,
      "action_taken": "BLOCK"
    },
    "audience": "user"
  }'
```
Response:
```json
{
  "explanation_id": "exp_456",
  "event_ids": ["evt_123"],
  "explanation": {
    "title": "Security Alert",
    "summary": "Transaction security check completed",
    "details": "We reviewed your transaction for security and took appropriate action",
    "confidence": 0.95
  },
  "involved_agents": ["financial-guardian"],
  "explanation_type": "single_agent"
}
```

**POST /explain/coordination-event**
Handle coordination events between multiple agents.
```bash
curl -X POST http://explainer-agent:8082/explain/coordination-event \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "agent_coordination",
    "source_service": "coordinator-agent",
    "severity": "medium",
    "context": {
      "coordination_type": "priority_conflict",
      "involved_agents": ["financial-guardian", "ops-guardian"],
      "decision": "prioritize_fraud_investigation"
    },
    "audience": "operator"
  }'
```

### Agent Management Endpoints

**POST /explain/register-agent-state**
Register current state of a Guardian agent.
```bash
curl -X POST http://explainer-agent:8082/explain/register-agent-state \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "financial-guardian",
    "state": {
      "active_investigations": 3,
      "blocked_transactions": 15,
      "risk_level": "HIGH"
    }
  }'
```
Response:
```json
{
  "status": "registered",
  "agent": "financial-guardian"
}
```

**GET /explain/agent-states**
Get current state of all Guardian agents.
```bash
curl http://explainer-agent:8082/explain/agent-states
```
Response:
```json
{
  "agent_states": {
    "financial-guardian": {
      "agent_name": "financial-guardian",
      "state": {
        "active_investigations": 3,
        "blocked_transactions": 15
      }
    }
  },
  "active_coordinations": 2,
  "buffered_correlations": 5
}
```

**GET /explain/correlations/{correlation_id}**
Get all events for a specific correlation ID.
```bash
curl http://explainer-agent:8082/explain/correlations/corr_123
```
Response:
```json
{
  "correlation_id": "corr_123",
  "events": [],
  "count": 0,
  "involved_agents": []
}
```

## Guardian Dashboard (Port: 8080)

### Web Interface

**GET /**
Serves the main dashboard web interface.
```bash
curl http://guardian-dashboard:8080/
```
Returns HTML dashboard interface.

### WebSocket Connection

**WebSocket /ws**
Real-time updates for dashboard UI.
```javascript
const ws = new WebSocket('ws://guardian-dashboard:8080/ws');
ws.onmessage = function(event) {
  const message = JSON.parse(event.data);
  // Handle real-time updates
};
```

### API Endpoints

**GET /ready**
```bash
curl http://guardian-dashboard:8080/ready
```
Response:
```json
{
  "status": "healthy",
  "service": "guardian-dashboard"
}
```

**GET /api/dashboard-data**
Get current dashboard data.
```bash
curl http://guardian-dashboard:8080/api/dashboard-data
```
Response:
```json
{
  "conversations": [],
  "api_calls": [],
  "agent_states": {},
  "active_correlations": 0,
  "total_conversations": 0,
  "total_api_calls": 0
}
```

**POST /api/conversations**
Add a new agent conversation to the dashboard.
```bash
curl -X POST http://guardian-dashboard:8080/api/conversations \
  -H "Content-Type: application/json" \
  -d '{
    "id": "msg_123",
    "timestamp": "2025-01-15T10:30:00Z",
    "from_agent": "financial-guardian",
    "to_agent": "ops-guardian",
    "message_type": "fraud_alert",
    "content": "Fraud detected, requesting coordination",
    "correlation_id": "corr_123"
  }'
```

**POST /api/api-calls**
Log an API call to the dashboard.
```bash
curl -X POST http://guardian-dashboard:8080/api/api-calls \
  -H "Content-Type: application/json" \
  -d '{
    "id": "call_123",
    "timestamp": "2025-01-15T10:30:00Z",
    "service": "financial-guardian",
    "method": "POST",
    "endpoint": "/fraud/check",
    "request_data": {"amount": 50000},
    "response_data": {"fraud_score": 0.95},
    "duration_ms": 245,
    "status_code": 200
  }'
```

### Proxy Endpoints

The dashboard provides proxy endpoints to access Guardian agents from the web interface:

**POST /api/financial-guardian/fraud/check**
Proxy to Financial Guardian fraud check.

**GET /api/ops-guardian/metrics**
Proxy to Ops Guardian metrics.

**POST /api/ops-guardian/monitoring/start**
Proxy to Ops Guardian monitoring start.

**POST /api/ops-guardian/scaling/decision**
Proxy to Ops Guardian scaling decision.

**POST /api/ops-guardian/scaling/manual**
Proxy to Ops Guardian manual scaling.

**POST /api/ops-guardian/coordination/pause**
Proxy to Ops Guardian coordination pause.

**POST /api/explainer-agent/explain/event**
Proxy to Explainer Agent event explanation.
