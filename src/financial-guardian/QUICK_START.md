# Financial Guardian - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Get Your Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key (keep it secret!)

### Step 2: Update the Secret
```bash
# Encode your API key
echo -n "YOUR_ACTUAL_API_KEY" | base64

# Edit the secret file
nano kubernetes-manifests/guardian-secrets.yaml

# Replace the placeholder with your encoded key
```

### Step 3: Deploy Everything
```bash
# Navigate to bank-of-anthos directory
cd bank-of-anthos

# Deploy base Bank of Anthos
kubectl apply -f extras/jwt/jwt-secret.yaml
kubectl apply -f kubernetes-manifests/

# Deploy Financial Guardian
kubectl apply -f kubernetes-manifests/guardian-secrets.yaml

# Build and run with Skaffold
export PROJECT_ID="your-gcp-project-id"
skaffold dev --profile development \
  --default-repo=us-central1-docker.pkg.dev/${PROJECT_ID}/bank-of-anthos \
  --module financial-guardian
```

### Step 4: Test It Works
```bash
# Check if it's running
kubectl get pods | grep financial-guardian

# Port forward to test locally
kubectl port-forward service/financial-guardian 8081:8081

# Test the health endpoint
curl http://localhost:8081/ready
# Should return: {"status": "ready", "service": "financial-guardian"}
```

## 🎮 Try It Out

### Start Monitoring an Account
```bash
curl -X POST http://localhost:8081/monitor/start \
  -H "Content-Type: application/json" \
  -d '{"account_id": "testuser"}'
```

### Check a Transaction for Fraud
```bash
curl -X POST http://localhost:8081/fraud/check \
  -H "Content-Type: application/json" \
  -d '{
    "fromAccountNum": "testuser",
    "toAccountNum": "suspicious_account", 
    "amount": 100000,
    "timestamp": "2025-09-21T02:30:00Z",
    "uuid": "test-transaction-123"
  }'
```

### View Fraud Alerts
```bash
curl "http://localhost:8081/fraud/alerts?account_id=testuser"
```

## 🎯 What You'll See

### Normal Transaction Response
```json
{
  "fraud_score": 0.2,
  "risk_level": "LOW", 
  "recommendation": "ALLOW",
  "explanation": "Transaction appears normal based on user patterns"
}
```

### Suspicious Transaction Response
```json
{
  "fraud_score": 0.85,
  "risk_level": "HIGH",
  "recommendation": "BLOCK", 
  "explanation": "Amount $1,000 is 20x larger than user's average of $50",
  "red_flags": [
    "Amount significantly larger than normal",
    "Transaction at unusual time (2:30 AM)"
  ]
}
```

## 🔧 Common Issues

### Pod Won't Start
```bash
# Check logs
kubectl logs -f deployment/financial-guardian

# Common issue: Missing API key
# Solution: Make sure guardian-secrets.yaml has correct encoded API key
```

### API Key Issues
```bash
# Test if your API key works
curl -H "Authorization: Bearer YOUR_API_KEY" \
  "https://generativelanguage.googleapis.com/v1/models"

# Should list available models including gemini-pro
```

### Can't Connect to Services
```bash
# Check if Bank of Anthos services are running
kubectl get services

# Should see: transactionhistory, balancereader, ledgerwriter
```

## 📊 Monitor Performance

### View Logs
```bash
# Real-time logs
kubectl logs -f deployment/financial-guardian

# Look for:
# - "Fraud detector initialized with Gemini AI"
# - "Transaction monitoring started"
# - "AI fraud analysis completed"
```

### Check Resource Usage
```bash
# CPU and memory usage
kubectl top pods | grep financial-guardian

# Should be well within limits:
# - CPU: < 500m (0.5 cores)
# - Memory: < 512Mi
```

## 🎉 You're Ready!

Your Financial Guardian is now:
- ✅ **Monitoring** transactions in real-time
- 🧠 **Analyzing** with Google AI
- 🛡️ **Protecting** against fraud
- 📱 **Alerting** on suspicious activity

Next steps:
1. Integrate with your banking frontend
2. Set up monitoring dashboards  
3. Configure alert notifications
4. Deploy other Guardian services (Ops, Explainer, Coordinator)

Happy fraud hunting! 🕵️‍♂️🤖
