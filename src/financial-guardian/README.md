# Financial Guardian Agent

An intelligent fraud detection microservice that integrates with Bank of Anthos to provide real-time transaction monitoring and anomaly detection using Google's Gemini AI.

## Overview

Financial Guardian is a containerized microservice designed to enhance banking security by analyzing transactions in real-time and identifying potentially fraudulent activities. It leverages Google's Gemini AI to provide sophisticated pattern recognition and risk assessment capabilities.

## Architecture

### System Design

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Bank Client   │    │  Financial       │    │   Gemini AI     │
│   Application   │───▶│  Guardian API    │───▶│   Service       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │  Bank of Anthos  │
                       │   Services       │
                       │ • Transaction    │
                       │ • User Service   │
                       │ • Contacts       │
                       └──────────────────┘
```

### Core Components

- **FraudDetector**: AI-powered transaction analysis engine
- **FinancialGuardian**: Main service orchestrator and API handler
- **User Profiling**: Behavioral pattern analysis and caching
- **Risk Assessment**: Multi-factor scoring and recommendation system

## Features

### Real-time Fraud Detection
- Analyzes transactions as they occur
- Sub-second response times for critical decisions
- Continuous monitoring capabilities

### AI-Powered Analysis
- Google Gemini AI integration for sophisticated pattern recognition
- Natural language explanations for fraud decisions
- Adaptive learning from transaction patterns

### Risk Scoring System
- Comprehensive risk assessment (0.0 - 1.0 scale)
- Detailed explanations and red flag identification
- Actionable recommendations (ALLOW/REVIEW/BLOCK)

### User Behavior Profiling
- Historical transaction pattern analysis
- Anomaly detection based on user behavior
- Dynamic profile updates

### RESTful API
- Easy integration with existing banking systems
- Comprehensive endpoint coverage
- Standardized JSON responses

### High Performance
- Kubernetes-native architecture
- Horizontal scaling capabilities
- Optimized for high-volume processing

## Prerequisites

- **Kubernetes Cluster**: Local (minikube) or cloud (GKE)
- **Docker**: For containerization and image management
- **Google Cloud Project**: With Gemini AI API enabled
- **Bank of Anthos**: Base banking system deployed
- **Python 3.12+**: For local development

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `GEMINI_API_KEY` | Google Gemini AI API key | - | Yes |
| `GEMINI_MODEL` | Gemini model to use | `gemini-1.5-flash` | No |
| `PORT` | Service port | `8081` | No |
| `VERSION` | Service version | `v1.0.0` | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |

### Kubernetes Secrets

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: guardian-secrets
type: Opaque
data:
  GEMINI_API_KEY: <base64-encoded-api-key>
```

## API Reference

### Health Endpoints

#### `GET /ready`
Kubernetes readiness probe endpoint.

**Response:**
```json
{
  "service": "financial-guardian",
  "status": "ready"
}
```

#### `GET /healthy`
Health check endpoint for monitoring.

**Response:**
```json
{
  "service": "financial-guardian",
  "status": "healthy"
}
```

### Fraud Detection

#### `POST /fraud/check`
Analyze a transaction for potential fraud.

**Request Body:**
```json
{
  "user_id": "string",
  "amount": number,
  "merchant": "string",
  "location": "string",
  "fromAccountNum": "string",
  "toAccountNum": "string",
  "timestamp": "ISO8601 datetime"
}
```

**Response:**
```json
{
  "analysis": {
    "fraud_score": 0.95,
    "risk_level": "CRITICAL",
    "explanation": "Detailed AI analysis...",
    "red_flags": ["flag1", "flag2"],
    "recommendation": "BLOCK"
  },
  "timestamp": "2024-01-15T10:30:00Z",
  "transaction_id": "uuid"
}
```

#### `GET /fraud/alerts`
Retrieve fraud alerts for a specific account.

**Query Parameters:**
- `account_id` (required): Account identifier

**Response:**
```json
{
  "account_id": "1011226111",
  "alerts": [
    {
      "timestamp": "2024-01-15T10:30:00Z",
      "fraud_score": 0.85,
      "transaction_amount": 50000,
      "risk_level": "HIGH"
    }
  ]
}
```

### Monitoring

#### `POST /monitor/start`
Start monitoring an account for suspicious activity.

**Request Body:**
```json
{
  "account_id": "1011226111"
}
```

#### `POST /monitor/stop`
Stop monitoring an account.

**Request Body:**
```json
{
  "account_id": "1011226111"
}
```

## Development

### Local Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/futureaiitofficial/anthos-guardian-agent.git
   cd anthos-guardian-agent/src/financial-guardian
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables**
   ```bash
   export GEMINI_API_KEY="your_gemini_api_key"
   export GEMINI_MODEL="gemini-1.5-flash"
   export PORT=8081
   ```

4. **Run the service**
   ```bash
   python financial_guardian.py
   ```

### Testing

```bash
# Health check
curl http://localhost:8081/ready

# Test fraud detection
curl -X POST http://localhost:8081/fraud/check \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "testuser",
    "amount": 50000,
    "merchant": "Suspicious Store",
    "location": "Unknown Location"
  }'
```

## Deployment

### Quick Start

For rapid deployment, see our **[Quick Start Guide](QUICK_START.md)** - get up and running in 5 minutes!

### Local Kubernetes (Minikube)

1. **Start minikube**
   ```bash
   minikube start --memory=7000
   ```

2. **Build and deploy**
   ```bash
   # Build image
   docker build -t financial-guardian .
   
   # Deploy to Kubernetes
   kubectl apply -f k8s/
   ```

### Google Kubernetes Engine (GKE)

See **[DEPLOYMENT.md](DEPLOYMENT.md)** for comprehensive GKE deployment instructions including:
- GKE cluster setup
- Artifact Registry configuration
- Image building and pushing
- Service deployment and verification

## Integration Points

- **Monitors**: `transaction-history:8080/transactions/<accountid>`
- **Controls**: `ledger-writer:8080/transactions` (intercepts POST requests)
- **Checks**: `balance-reader:8080/balances/<accountid>`
- **AI Analysis**: Google Gemini API for fraud detection

## Documentation

- 📖 **[Technical Documentation](docs/DOCUMENTATION.md)** - Detailed system architecture and implementation
- 🚀 **[Quick Start Guide](docs/QUICK_START.md)** - Get up and running in 5 minutes  
- 🚀 **[Deployment Guide](docs/DEPLOYMENT.md)** - Complete deployment instructions for local and cloud
- 🎮 **[Demo Script](demo_script.py)** - Interactive fraud detection demonstration

## Demo

### Quick Demo

```bash
# 1. Deploy Financial Guardian (see Quick Start Guide)
# 2. Port forward the service
kubectl port-forward service/financial-guardian 8081:8081

# 3. Run the interactive demo
python3 demo_script.py
```

This will demonstrate:
- ✅ Normal transaction (allowed)
- ⚠️ Suspicious transaction (flagged)  
- 🚫 Fraud transaction (blocked)
- 📊 AI explanations for each decision

### Example AI Analysis Output

```json
{
  "analysis": {
    "fraud_score": 0.95,
    "risk_level": "CRITICAL",
    "explanation": "This transaction exhibits numerous red flags strongly indicative of fraudulent activity. The transaction involves a large sum of money ($50,000) which is significantly higher than the user's transaction history...",
    "red_flags": [
      "Extremely large transaction amount ($50,000) compared to absent recent transaction history",
      "Suspicious merchant name: 'Suspicious Store'",
      "Unknown transaction location",
      "Absence of user profile information",
      "Unusual transaction time (4:42 AM might be outside typical activity patterns)"
    ],
    "recommendation": "BLOCK"
  },
  "user_explanation": {
    "title": "Transaction Blocked",
    "summary": "Your $50,000 transaction to Suspicious Store was blocked",
    "explanation": "We blocked this transaction because it's 250× larger than your usual $200 purchases.",
    "next_steps": [
      "If this was you, please verify via the mobile app or call us",
      "If this wasn't you, your account is secure - no action needed"
    ]
  }
}
```

## Performance

- **Response Time**: < 2 seconds for fraud analysis
- **Throughput**: 1000+ transactions per minute
- **Availability**: 99.9% uptime with proper Kubernetes setup
- **Scalability**: Horizontal scaling with replica sets

## Security

- **API Key Management**: Secure handling of Gemini AI credentials via Kubernetes secrets
- **Data Privacy**: No transaction data persistence
- **Network Security**: Kubernetes network policies supported
- **Audit Logging**: Comprehensive request/response logging

## Monitoring & Observability

- **Health Checks**: Kubernetes-native readiness and liveness probes
- **Structured Logging**: JSON-formatted logs for observability
- **Error Handling**: Graceful degradation with fallback analysis
- **Metrics**: Request/response metrics and fraud detection statistics

## Troubleshooting

### Common Issues

1. **"AI response not valid JSON"** - Check Gemini API key and model configuration
2. **"ErrImageNeverPull"** - Update `imagePullPolicy` to `IfNotPresent` for GKE
3. **Service unavailable** - Verify all Bank of Anthos services are running

### Debugging

```bash
# Check pod status
kubectl get pods -l app=financial-guardian

# View logs
kubectl logs deployment/financial-guardian --tail=20

# Test connectivity
kubectl port-forward service/financial-guardian 8081:8081
curl http://localhost:8081/ready
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is part of the Bank Guardian AI system developed for hackathon purposes. See the main repository for license information.

## Support

For questions and support:
- Create an issue in the GitHub repository
- Review the technical documentation
- Check the deployment guide for common issues
