# Bank Guardian AI: Intelligent Risk & Operations Management for Bank of Anthos

> **Repository Migration Notice**: This repository includes migration tools to copy all content to a new location with a clean commit history. See [MIGRATION_QUICK_START.md](./MIGRATION_QUICK_START.md) or run `./migrate-to-bank-guardian-ai.sh` for automated migration.

## Overview

Bank Guardian AI is an intelligent multi-agent system that enhances Bank of Anthos with autonomous fraud detection, infrastructure management, and intelligent explanation capabilities. The system deploys alongside Bank of Anthos on Google Kubernetes Engine, providing real-time monitoring and automated responses to both financial and operational threats.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Bank of Anthos                           │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│  │  Frontend   │ │ User Service│ │ Transaction │ │ Balance     │ │
│  │             │ │             │ │ History     │ │ Reader      │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│  │ Ledger      │ │ Contacts    │ │ Accounts DB │ │ Ledger DB   │ │
│  │ Writer      │ │             │ │             │ │             │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Bank Guardian AI System                      │
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐  │
│  │ Financial       │    │ Ops Guardian    │    │ Explainer   │  │
│  │ Guardian        │    │                 │    │ Agent       │  │
│  │ • Fraud         │    │ • Monitoring    │    │ • Multi-    │  │
│  │   Detection     │◄──►│ • Auto-scaling  │◄──►│   Agent     │  │
│  │ • Risk Analysis │    │ • Prediction    │    │   Context   │  │
│  │ • User Profiles │    │ • Coordination  │    │ • Natural   │  │
│  └─────────────────┘    └─────────────────┘    │   Language  │  │
│            │                       │           └─────────────┘  │
│            │                       │                   ▲        │
│            ▼                       ▼                   │        │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              Guardian Dashboard                         │    │
│  │ • Real-time Monitoring  • Agent Coordination           │    │
│  │ • Demo Scenarios        • WebSocket Updates            │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │     Google Gemini AI    │
                    │ • Pattern Recognition   │
                    │ • Natural Language      │
                    │ • Predictive Analytics  │
                    └─────────────────────────┘
```

## Core Components

### Financial Guardian Agent
Monitors banking transactions in real-time, uses Google Gemini AI for fraud detection, and automatically blocks or flags suspicious activities.

**Key Features:**
- Real-time transaction monitoring
- AI-powered fraud detection using Gemini
- User behavioral profiling
- Automatic transaction blocking/flagging
- User-friendly explanations

### Ops Guardian Agent
Monitors infrastructure health, predicts traffic patterns, and automatically scales Kubernetes resources using AI-driven decisions.

**Key Features:**
- Kubernetes metrics monitoring
- AI-powered traffic prediction
- Automatic pod scaling
- Multi-agent coordination
- Business-aware scaling logic

### Explainer Agent
Provides natural language explanations for all Guardian agent actions, correlates multi-agent events, and generates human-readable reports.

**Key Features:**
- Multi-agent event correlation
- Natural language generation
- Context-aware explanations
- Cross-agent communication
- Operator and user-facing reports

### Guardian Dashboard
Real-time monitoring interface that visualizes agent activity, provides demo scenarios, and enables manual control of the Guardian system.

**Key Features:**
- Real-time WebSocket updates
- Interactive demo scenarios
- Agent status monitoring
- API call visualization
- Professional UI matching Bank of Anthos design

## Deployment

### Prerequisites
- Google Kubernetes Engine cluster
- Google Gemini AI API key
- Bank of Anthos deployed

### Quick Start
```bash
# Deploy Guardian secrets
kubectl apply -f kubernetes-manifests/guardian-secrets.yaml

# Deploy all Guardian agents
kubectl apply -f src/financial-guardian/k8s/deployment.yaml
kubectl apply -f src/explainer-agent/k8s/deployment.yaml
kubectl apply -f src/ops-guardian/k8s/deployment.yaml
kubectl apply -f src/guardian-dashboard/k8s/deployment.yaml

# Verify deployment
kubectl get pods | grep -E "(financial|explainer|ops|guardian)"
```

### Access Dashboard
```bash
# Get dashboard URL
kubectl get service guardian-dashboard

# Or use port forwarding
kubectl port-forward service/guardian-dashboard 8080:8080
```
Open http://localhost:8080 in your browser.

## API Overview

### Service Ports
- **Financial Guardian**: 8081
- **Explainer Agent**: 8082  
- **Ops Guardian**: 8083
- **Guardian Dashboard**: 8080

### Key Endpoints

**Financial Guardian**
```bash
# Check fraud for a transaction
POST /fraud/check

# Start monitoring account
POST /monitor/start

# Get fraud alerts
GET /fraud/alerts?account_id={id}
```

**Ops Guardian**
```bash
# Get infrastructure metrics
GET /metrics

# Start monitoring
POST /monitoring/start

# Make scaling decision
POST /scaling/decision

# Manually scale service
POST /scaling/manual

# Pause coordination
POST /coordination/pause
```

**Explainer Agent**
```bash
# Explain agent event
POST /explain/event

# Handle coordination events
POST /explain/coordination-event

# Register agent state
POST /explain/register-agent-state

# Get agent states
GET /explain/agent-states
```

**Guardian Dashboard**
```bash
# Access web interface
GET /

# WebSocket for real-time updates
WS /ws

# Get dashboard data
GET /api/dashboard-data

# Proxy to agents
POST /api/financial-guardian/fraud/check
GET /api/ops-guardian/metrics
POST /api/explainer-agent/explain/event
```

For complete API documentation with request/response examples, see [API_DOCUMENTATION.md](API_DOCUMENTATION.md).

## Demo Scenarios

The Guardian Dashboard includes three interactive demo scenarios:

1. **Fraud Detection Coordination** - Shows how Financial Guardian detects fraud and coordinates with Ops Guardian
2. **Proactive Infrastructure Scaling** - Demonstrates AI-powered scaling decisions based on traffic predictions  
3. **Multi-Agent Priority Resolution** - Shows how agents resolve conflicts when priorities clash

Each scenario makes real API calls to the Guardian agents and displays the results in real-time.

## Key Benefits

**For Banks:**
- Autonomous fraud detection reduces financial losses
- Proactive infrastructure scaling prevents outages
- Natural language explanations improve customer trust

**For Operations:**
- Reduced manual intervention through automation
- Predictive scaling prevents performance issues
- Clear explanations for all automated actions

**For Developers:**
- RESTful APIs for easy integration
- Kubernetes-native deployment
- Comprehensive monitoring and logging

## Technology Stack

- **Languages:** Python, JavaScript, HTML/CSS
- **Frameworks:** Flask, FastAPI, Bootstrap Material Design
- **AI/ML:** Google Gemini AI
- **Infrastructure:** Kubernetes, Docker
- **Databases:** PostgreSQL (Bank of Anthos)
- **Communication:** REST APIs, WebSockets
- **Monitoring:** Kubernetes metrics, custom dashboards

Bank Guardian AI transforms traditional banking infrastructure into an intelligent, self-managing system that proactively protects against both financial and operational threats while maintaining full transparency through natural language explanations.

