# Ops Guardian Agent

**Intelligent Infrastructure Monitoring & Auto-Scaling for Bank of Anthos**

The Ops Guardian Agent provides AI-powered infrastructure management for Bank of Anthos, continuously monitoring service health, predicting traffic patterns, and making intelligent scaling decisions while coordinating with other Guardian agents.

## What This Service Does

### Intelligent Monitoring
- Real-time metrics tracking for CPU, memory, response times, and error rates
- Pattern recognition that learns application behavior over time  
- Predictive analytics using Google Gemini AI to forecast scaling needs
- Business context awareness of banking traffic patterns (lunch rush, paydays, etc.)

### Smart Auto-Scaling
- AI-powered decisions where Gemini analyzes metrics and predicts optimal scaling
- Banking-aware logic that considers financial service availability requirements
- Proactive scaling that scales up before performance degrades
- Cost optimization through intelligent scale-down during low-traffic periods

### Multi-Agent Coordination
- Fraud investigation priority that pauses scaling during active fraud cases
- Resource coordination that works with Financial Guardian on priority decisions
- Transparent explanations through partnership with Explainer Agent

## Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Kubernetes     │    │   Ops Guardian   │    │  Gemini AI      │
│  Cluster        │◄───┤   Agent          │───►│  Prediction     │
│  (Monitoring)   │    │                  │    │  Engine         │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │  Multi-Agent     │
                       │  Coordination    │
                       │  Hub             │
                       └──────────────────┘
                                │
                ┌───────────────┼───────────────┐
                ▼               ▼               ▼
    ┌─────────────────┐ ┌─────────────┐ ┌─────────────────┐
    │ Financial       │ │ Explainer   │ │ Bank of Anthos  │
    │ Guardian        │ │ Agent       │ │ Services        │
    └─────────────────┘ └─────────────┘ └─────────────────┘
```

## Key Features

### Kubernetes Integration
- Native integration with Kubernetes metrics API
- Automatic discovery of Bank of Anthos services
- Real-time pod and deployment monitoring
- RBAC-compliant service account configuration

### AI-Powered Predictions
- Google Gemini integration for intelligent decision making
- Historical pattern analysis for traffic prediction
- Business-aware scaling logic for banking applications
- Confidence scoring for scaling recommendations

### Multi-Agent Awareness
- Coordination with Financial Guardian during fraud investigations
- Priority-based decision making when agents have conflicting needs
- Event correlation for system-wide visibility
- Explainer Agent integration for transparent operations

## API Reference

### Health Endpoints

**GET /ready**
Kubernetes readiness probe endpoint.
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
Detailed health check with system status.
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

### Monitoring Control

**POST /monitoring/start**
Start infrastructure monitoring.
```bash
curl -X POST http://ops-guardian:8083/monitoring/start
```

**POST /monitoring/stop**
Stop infrastructure monitoring.
```bash
curl -X POST http://ops-guardian:8083/monitoring/stop
```

**GET /monitoring/status**
Get current monitoring status.
```bash
curl http://ops-guardian:8083/monitoring/status
```

### Metrics and Scaling

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

**POST /scaling/decision**
Get AI scaling recommendation for a service.
```bash
curl -X POST http://ops-guardian:8083/scaling/decision \
  -H "Content-Type: application/json" \
  -d '{"service_name": "frontend"}'
```

**POST /scaling/manual**
Manually scale a service.
```bash
curl -X POST http://ops-guardian:8083/scaling/manual \
  -H "Content-Type: application/json" \
  -d '{"service_name": "frontend", "target_replicas": 3}'
```

### Coordination

**POST /coordination/pause**
Pause scaling operations for coordination with other agents.
```bash
curl -X POST http://ops-guardian:8083/coordination/pause \
  -H "Content-Type: application/json" \
  -d '{"reason": "Active fraud investigation"}'
```

**POST /coordination/resume**
Resume normal scaling operations.
```bash
curl -X POST http://ops-guardian:8083/coordination/resume
```

## Deployment

### Prerequisites
- Kubernetes cluster with metrics API enabled
- Google Gemini AI API key
- Bank of Anthos services deployed
- Appropriate RBAC permissions for service account

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GEMINI_API_KEY="your_api_key"
export PORT=8083

# Run the service
python ops_guardian.py
```

### Kubernetes Deployment
```bash
# Deploy to Kubernetes
kubectl apply -f k8s/deployment.yaml

# Verify deployment
kubectl get pods -l app=ops-guardian
kubectl logs deployment/ops-guardian
```

### Environment Variables
- `GEMINI_API_KEY`: Google Gemini AI API key (required)
- `GEMINI_MODEL`: Gemini model to use (default: gemini-1.5-flash)
- `PORT`: Service port (default: 8083)
- `LOG_LEVEL`: Logging level (default: INFO)

## Monitored Services

The Ops Guardian automatically monitors these Bank of Anthos services:
- **frontend**: Customer-facing web interface
- **balancereader**: Account balance service
- **ledgerwriter**: Transaction processing service
- **transactionhistory**: Transaction history service
- **userservice**: User management service
- **contacts**: Contact management service

## AI Decision Making

### Scaling Logic
The AI considers multiple factors when making scaling decisions:
- Current resource utilization (CPU, memory)
- Historical usage patterns
- Time-based patterns (business hours, lunch rush, etc.)
- Error rates and response times
- Business context (banking-specific patterns)

### Example AI Decision
```json
{
  "service": "frontend",
  "scaling_decision": {
    "target_replicas": 4,
    "reason": "Lunch rush traffic pattern detected, CPU usage trending upward",
    "confidence": 0.87,
    "coordination_needed": false
  }
}
```

## Multi-Agent Scenarios

### Fraud Investigation Priority
When Financial Guardian detects fraud, Ops Guardian:
1. Pauses automatic scaling to preserve system resources
2. Maintains current capacity for investigation stability
3. Coordinates with Explainer Agent to communicate the decision

### Resource Conflict Resolution
When multiple agents need resources:
1. Financial Guardian fraud investigations take priority
2. Critical infrastructure scaling is prioritized over optimization
3. All decisions are logged and explained through Explainer Agent

## Performance

- **Monitoring Interval**: 30 seconds for metrics collection
- **Decision Latency**: < 5 seconds for scaling decisions
- **Kubernetes API Calls**: Rate-limited to prevent cluster overload
- **Memory Usage**: < 256MB typical operation
- **CPU Usage**: < 100m typical operation

## Security

- **RBAC Integration**: Uses Kubernetes service accounts with minimal required permissions
- **API Key Security**: Gemini API key stored in Kubernetes secrets
- **Network Policies**: Supports Kubernetes network policies for traffic isolation
- **Audit Logging**: All scaling decisions and coordination events are logged

## Troubleshooting

### Common Issues

**Ops Guardian not starting**
```bash
# Check pod status
kubectl get pods -l app=ops-guardian

# Check logs
kubectl logs deployment/ops-guardian

# Verify API key
kubectl get secret guardian-secrets -o yaml
```

**Metrics not available**
```bash
# Check Kubernetes metrics API
kubectl top nodes
kubectl top pods

# Verify RBAC permissions
kubectl auth can-i get pods --as=system:serviceaccount:default:ops-guardian
```

**AI decisions not working**
```bash
# Test Gemini API connectivity
curl -H "Authorization: Bearer $GEMINI_API_KEY" \
  "https://generativelanguage.googleapis.com/v1/models"

# Check environment variables
kubectl describe pod -l app=ops-guardian | grep -A 10 Environment
```

## Integration Points

- **Monitors**: Kubernetes metrics API for pod and node metrics
- **Controls**: Kubernetes deployments for scaling operations
- **Coordinates**: Financial Guardian for fraud investigation priorities
- **Explains**: Explainer Agent for transparent decision communication
- **AI Analysis**: Google Gemini API for intelligent scaling decisions

## Documentation

- **[Infrastructure Guide](docs/INFRASTRUCTURE_GUIDE.md)** - Detailed technical documentation
- **[API Documentation](../API_DOCUMENTATION.md)** - Complete API reference
- **[Deployment Guide](../../GUARDIAN_AI_DEPLOYMENT_GUIDE.md)** - Deployment instructions

The Ops Guardian Agent ensures your Bank of Anthos infrastructure remains performant, cost-effective, and responsive to business needs while maintaining coordination with other Guardian agents for optimal system-wide operation.