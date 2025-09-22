# Financial Guardian - Deployment Guide

This guide provides comprehensive instructions for deploying the Financial Guardian service in both local and cloud environments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Local Deployment (Minikube)](#local-deployment-minikube)
- [Google Kubernetes Engine (GKE) Deployment](#google-kubernetes-engine-gke-deployment)
- [Configuration](#configuration)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)
- [Monitoring](#monitoring)

## Prerequisites

### Required Tools

- **Docker**: For building container images
- **kubectl**: Kubernetes command-line tool
- **Google Cloud SDK**: For GKE deployment
- **Git**: For cloning the repository

### Required Services

- **Bank of Anthos**: Must be deployed and running
- **Google Cloud Project**: With Gemini AI API enabled
- **Gemini API Key**: Valid Google AI API key

### Install Tools

```bash
# Install Docker (Ubuntu/Debian)
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Install Google Cloud SDK
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init
```

## Local Deployment (Minikube)

### Step 1: Setup Minikube

```bash
# Install minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Start minikube with sufficient resources
minikube start --memory=7000 --cpus=4
```

### Step 2: Deploy Bank of Anthos

```bash
# Clone Bank of Anthos
git clone https://github.com/GoogleCloudPlatform/bank-of-anthos.git
cd bank-of-anthos

# Deploy base services
kubectl apply -f ./extras/jwt/jwt-secret.yaml
kubectl apply -f ./kubernetes-manifests

# Wait for services to be ready
kubectl wait --for=condition=available --timeout=300s deployment --all
```

### Step 3: Configure Secrets

```bash
# Create Gemini API key secret
kubectl create secret generic guardian-secrets \
  --from-literal=GEMINI_API_KEY="your_gemini_api_key_here"
```

### Step 4: Build and Deploy Financial Guardian

```bash
# Clone Guardian Agent repository
git clone https://github.com/futureaiitofficial/anthos-guardian-agent.git
cd anthos-guardian-agent/src/financial-guardian

# Build Docker image for minikube
eval $(minikube docker-env)
docker build -t financial-guardian .

# Deploy to Kubernetes
kubectl apply -f k8s/

# Update deployment to use local image
kubectl patch deployment financial-guardian -p '{"spec":{"template":{"spec":{"containers":[{"name":"financial-guardian","imagePullPolicy":"Never"}]}}}}'
```

### Step 5: Verify Deployment

```bash
# Check pod status
kubectl get pods -l app=financial-guardian

# Check service
kubectl get service financial-guardian

# Test the service
kubectl port-forward service/financial-guardian 8081:8081 &
curl http://localhost:8081/ready
```

## Google Kubernetes Engine (GKE) Deployment

### Step 1: Setup Google Cloud Environment

```bash
# Set project variables
export PROJECT_ID="your-project-id"
export REGION="us-central1"

# Configure gcloud
gcloud config set project $PROJECT_ID
gcloud config set compute/region $REGION

# Enable required APIs
gcloud services enable container.googleapis.com
gcloud services enable cloudbuild.googleapis.com  
gcloud services enable artifactregistry.googleapis.com
```

### Step 2: Create GKE Cluster (if needed)

```bash
# Create GKE Autopilot cluster
gcloud container clusters create-auto bank-of-anthos \
  --project=${PROJECT_ID} --region=${REGION}

# Get cluster credentials
gcloud container clusters get-credentials bank-of-anthos \
    --project=$PROJECT_ID --region=$REGION
```

### Step 3: Deploy Bank of Anthos to GKE

```bash
# Clone Bank of Anthos (if not already done)
git clone https://github.com/GoogleCloudPlatform/bank-of-anthos.git
cd bank-of-anthos

# Deploy JWT secret and services
kubectl apply -f ./extras/jwt/jwt-secret.yaml
kubectl apply -f ./kubernetes-manifests

# Wait for deployment
kubectl wait --for=condition=available --timeout=600s deployment --all
```

### Step 4: Setup Artifact Registry

```bash
# Create Artifact Registry repository
gcloud artifacts repositories create bank-guardian-repo \
    --repository-format=docker \
    --location=$REGION \
    --description="Bank Guardian AI Docker Repository"

# Configure Docker authentication
gcloud auth configure-docker ${REGION}-docker.pkg.dev
```

### Step 5: Build and Push Financial Guardian Image

```bash
# Clone Guardian Agent repository
git clone https://github.com/futureaiitofficial/anthos-guardian-agent.git
cd anthos-guardian-agent/src/financial-guardian

# Build Docker image
docker build -t us-central1-docker.pkg.dev/$PROJECT_ID/bank-guardian-repo/financial-guardian .

# Push to Artifact Registry
docker push us-central1-docker.pkg.dev/$PROJECT_ID/bank-guardian-repo/financial-guardian
```

### Step 6: Configure Secrets

```bash
# Create Gemini API key secret
kubectl create secret generic guardian-secrets \
  --from-literal=GEMINI_API_KEY="your_gemini_api_key_here"
```

### Step 7: Deploy Financial Guardian

```bash
# Update deployment manifest with correct image
kubectl apply -f k8s/

# Update deployment to use Artifact Registry image
kubectl patch deployment financial-guardian -p '{"spec":{"template":{"spec":{"containers":[{"name":"financial-guardian","image":"us-central1-docker.pkg.dev/'$PROJECT_ID'/bank-guardian-repo/financial-guardian:latest","imagePullPolicy":"IfNotPresent"}]}}}}'

# Set Gemini model to working version
kubectl patch deployment financial-guardian -p '{"spec":{"template":{"spec":{"containers":[{"name":"financial-guardian","env":[{"name":"GEMINI_MODEL","value":"gemini-1.5-flash"}]}]}}}}'

# Restart deployment
kubectl rollout restart deployment financial-guardian
kubectl rollout status deployment financial-guardian
```

## Configuration

### Environment Variables

The Financial Guardian service can be configured using the following environment variables:

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `GEMINI_API_KEY` | Google Gemini AI API key | - | Yes |
| `GEMINI_MODEL` | Gemini model to use | `gemini-1.5-flash` | No |
| `PORT` | Service port | `8081` | No |
| `VERSION` | Service version | `v1.0.0` | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |

### Kubernetes Configuration

```yaml
# Example ConfigMap
apiVersion: v1
kind: ConfigMap
metadata:
  name: financial-guardian-config
data:
  GEMINI_MODEL: "gemini-1.5-flash"
  PORT: "8081"
  LOG_LEVEL: "INFO"
```

### Secrets Configuration

```yaml
# Guardian secrets
apiVersion: v1
kind: Secret
metadata:
  name: guardian-secrets
type: Opaque
data:
  GEMINI_API_KEY: <base64-encoded-api-key>
```

To encode your API key:
```bash
echo -n "your_api_key_here" | base64
```

## Verification

### Step 1: Check Pod Status

```bash
# Verify all pods are running
kubectl get pods

# Check Financial Guardian specifically
kubectl get pods -l app=financial-guardian

# View logs
kubectl logs deployment/financial-guardian --tail=20
```

### Step 2: Test Service Endpoints

```bash
# Port forward the service
kubectl port-forward service/financial-guardian 8081:8081 &

# Test health endpoints
curl http://localhost:8081/ready
curl http://localhost:8081/healthy

# Test fraud detection with suspicious transaction
curl -X POST http://localhost:8081/fraud/check \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "testuser", 
    "amount": 50000,
    "merchant": "Suspicious Store",
    "location": "Unknown Location",
    "fromAccountNum": "1011226111",
    "toAccountNum": "1033623433",
    "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%S.%fZ)'"
  }' | python3 -m json.tool
```

### Step 3: Verify AI Integration

A successful AI-powered response should look like:

```json
{
    "analysis": {
        "explanation": "This transaction exhibits numerous red flags strongly indicative of fraudulent activity...",
        "fraud_score": 0.95,
        "recommendation": "BLOCK",
        "red_flags": [
            "Extremely large transaction amount ($50,000)",
            "Suspicious merchant name: 'Suspicious Store'",
            "Unknown transaction location"
        ],
        "risk_level": "CRITICAL"
    },
    "timestamp": "2025-09-22T04:42:15.375656",
    "transaction_id": null
}
```

If you see `"Rule-based analysis (AI unavailable)"`, check:
- Gemini API key is correct
- Gemini model is set to `gemini-1.5-flash`
- Network connectivity to Google AI services

## Troubleshooting

### Common Issues

#### 1. "ErrImageNeverPull" Error

**Problem**: Pod cannot pull the Docker image.

**Solution**:
```bash
# For GKE deployment
kubectl patch deployment financial-guardian -p '{"spec":{"template":{"spec":{"containers":[{"name":"financial-guardian","imagePullPolicy":"IfNotPresent"}]}}}}'
```

#### 2. "AI response not valid JSON" Warning

**Problem**: Gemini AI response parsing issues.

**Solution**: This has been fixed in the latest version. Ensure you're using the latest image:
```bash
# Pull latest changes
git pull origin main

# Rebuild and redeploy
docker build -t us-central1-docker.pkg.dev/$PROJECT_ID/bank-guardian-repo/financial-guardian .
docker push us-central1-docker.pkg.dev/$PROJECT_ID/bank-guardian-repo/financial-guardian
kubectl rollout restart deployment financial-guardian
```

#### 3. "404 models/gemini-pro is not found" Error

**Problem**: Using deprecated Gemini model.

**Solution**:
```bash
kubectl patch deployment financial-guardian -p '{"spec":{"template":{"spec":{"containers":[{"name":"financial-guardian","env":[{"name":"GEMINI_MODEL","value":"gemini-1.5-flash"}]}]}}}}'
kubectl rollout restart deployment financial-guardian
```

#### 4. Bank of Anthos Services Not Running

**Problem**: Core banking services are in CrashLoopBackOff.

**Solution**:
```bash
# Check service status
kubectl get pods

# For local development, disable Google Cloud tracing
kubectl patch configmap environment-config -p '{"data":{"ENABLE_TRACING":"false","ENABLE_METRICS":"false","ENV":"local"}}'

# Restart affected services
kubectl rollout restart deployment/frontend
kubectl rollout restart deployment/contacts
kubectl rollout restart deployment/userservice
```

#### 5. Port Forward Connection Issues

**Problem**: Cannot connect to port-forwarded service.

**Solution**:
```bash
# Kill existing port forwards
pkill -f "kubectl port-forward"

# Wait and restart
sleep 2
kubectl port-forward service/financial-guardian 8081:8081 &
```

### Debug Commands

```bash
# Check pod details
kubectl describe pod -l app=financial-guardian

# View detailed logs
kubectl logs deployment/financial-guardian --tail=50

# Check service configuration
kubectl describe service financial-guardian

# Test internal connectivity
kubectl run debug --image=busybox --rm -it -- sh
# Inside the pod:
wget -qO- http://financial-guardian:8081/ready
```

## Monitoring

### Health Checks

The Financial Guardian includes built-in health check endpoints:

- **Readiness**: `GET /ready` - Kubernetes readiness probe
- **Liveness**: `GET /healthy` - Health check for monitoring

### Logging

The service provides structured JSON logging:

```bash
# View logs in real-time
kubectl logs -f deployment/financial-guardian

# Search for specific events
kubectl logs deployment/financial-guardian | grep "fraud_score"
kubectl logs deployment/financial-guardian | grep "ERROR"
```

### Metrics

Monitor key metrics:
- Response times for fraud analysis
- Fraud detection rates
- API error rates
- Gemini AI availability

### Alerting

Set up alerts for:
- Pod restarts or failures
- High error rates
- Gemini AI service unavailability
- Unusual fraud detection patterns

## Performance Tuning

### Resource Allocation

```yaml
# Recommended resource limits
resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 250m
    memory: 256Mi
```

### Scaling

```bash
# Scale horizontally
kubectl scale deployment financial-guardian --replicas=3

# Enable autoscaling
kubectl autoscale deployment financial-guardian --cpu-percent=70 --min=1 --max=10
```

## Security Best Practices

1. **API Key Management**: Store Gemini API keys in Kubernetes secrets
2. **Network Policies**: Implement network policies to restrict traffic
3. **RBAC**: Use Role-Based Access Control for service accounts
4. **Image Security**: Regularly update base images and scan for vulnerabilities
5. **Data Privacy**: Ensure no sensitive data is logged or persisted

## Backup and Disaster Recovery

1. **Configuration Backup**: Store Kubernetes manifests in version control
2. **Secret Management**: Use external secret management systems
3. **Image Registry**: Maintain multiple image tags for rollback capability
4. **Monitoring**: Implement comprehensive monitoring and alerting

## Next Steps

After successful deployment:

1. **Integration Testing**: Test with real Bank of Anthos transactions
2. **Performance Testing**: Load test the fraud detection API
3. **Security Review**: Conduct security assessment
4. **Monitoring Setup**: Implement comprehensive observability
5. **Documentation**: Update operational runbooks

For additional support, refer to the [main README](README.md) and [technical documentation](DOCUMENTATION.md).
