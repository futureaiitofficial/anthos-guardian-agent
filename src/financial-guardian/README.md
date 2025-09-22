# Financial Guardian Service

The Financial Guardian service provides real-time transaction monitoring and fraud detection capabilities using Google AI (Gemini) to analyze transaction patterns and automatically block or flag suspicious activities.

Implemented in Python with Flask and Google AI integration.

## Features

- Real-time transaction monitoring via transaction-history API
- AI-powered anomaly detection using Gemini
- Automatic transaction blocking/flagging
- User behavior profiling and baseline establishment
- Integration with ledger-writer for transaction control

## Endpoints

| Endpoint                    | Type | Auth? | Description                                                |
| --------------------------- | ---- | ----- | ---------------------------------------------------------- |
| `/monitor/start`           | POST | 🔒    | Start monitoring transactions for a specific account       |
| `/monitor/stop`            | POST | 🔒    | Stop monitoring transactions for a specific account        |
| `/fraud/check`             | POST | 🔒    | Check if a transaction is potentially fraudulent           |
| `/fraud/block`             | POST | 🔒    | Block a specific transaction                               |
| `/fraud/alerts`            | GET  | 🔒    | Get list of fraud alerts for an account                   |
| `/ready`                   | GET  |       | Readiness probe endpoint                                   |
| `/healthy`                 | GET  |       | Health check endpoint                                      |
| `/version`                 | GET  |       | Returns the service version                                |

## Environment Variables

- `VERSION`: Service version string
- `PORT`: Port for the webserver (default: 8081)
- `LOG_LEVEL`: Service log level (default: INFO)
- `GEMINI_API_KEY`: Google AI API key for Gemini integration
- `GEMINI_MODEL`: Gemini model to use (default: gemini-pro)

ConfigMap `guardian-config`:
- `TRANSACTION_HISTORY_ADDR`: Address of transaction-history service
- `LEDGER_WRITER_ADDR`: Address of ledger-writer service  
- `BALANCE_READER_ADDR`: Address of balance-reader service
- `PUB_KEY_PATH`: Path to JWT public key for authentication

## Integration Points

- **Monitors**: `transaction-history:8080/transactions/<accountid>`
- **Controls**: `ledger-writer:8080/transactions` (intercepts POST requests)
- **Checks**: `balance-reader:8080/balances/<accountid>`
- **AI Analysis**: Google Gemini API for fraud detection

## Kubernetes Resources

- [deployments/financial-guardian](k8s/deployment.yaml)
- [service/financial-guardian](k8s/service.yaml)

## Documentation

- 📖 **[Complete Documentation](DOCUMENTATION.md)** - Detailed explanation of how Financial Guardian works
- 🚀 **[Quick Start Guide](QUICK_START.md)** - Get up and running in 5 minutes  
- 🎮 **[Demo Script](demo_script.py)** - Interactive demo showing fraud detection capabilities

## Quick Demo

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
