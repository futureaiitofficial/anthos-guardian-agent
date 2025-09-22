# 🚀 Guardian AI Deployment Guide

**Complete guide for deploying and updating Guardian AI microservices on Google Kubernetes Engine (GKE)**

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Deploying New Microservices](#deploying-new-microservices)
4. [Updating Existing Microservices](#updating-existing-microservices)
5. [Testing Deployments](#testing-deployments)
6. [Troubleshooting](#troubleshooting)
7. [Production Considerations](#production-considerations)

---

## 🔧 Prerequisites

### Required Tools
- **Google Cloud SDK** (`gcloud`)
- **Docker** (for building images)
- **kubectl** (for Kubernetes operations)
- **Git** (for code management)

### Required Access
- **GKE Cluster** with admin access
- **Artifact Registry** repository
- **Google Cloud Project** with appropriate permissions

### Environment Variables
```bash
export PROJECT_ID="your-project-id"
export REGION="us-central1"
export CLUSTER_NAME="bank-of-anthos"
export ARTIFACT_REGISTRY_REPO="bank-guardian-repo"
```

---

## 🏗️ Initial Setup

### 1. Authenticate and Configure Google Cloud

```bash
# Authenticate with Google Cloud
gcloud auth login

# Set your project
gcloud config set project $PROJECT_ID

# Get GKE cluster credentials
gcloud container clusters get-credentials $CLUSTER_NAME \
    --project=$PROJECT_ID --region=$REGION

# Verify cluster access
kubectl cluster-info
kubectl get nodes
```

### 2. Clone and Setup Repository

```bash
# Clone the repository
git clone https://github.com/futureaiitofficial/anthos-guardian-agent.git
cd anthos-guardian-agent

# Verify Guardian AI services
ls -la src/
```

### 3. Configure Artifact Registry (One-time setup)

```bash
# Create Artifact Registry repository (if not exists)
gcloud artifacts repositories create $ARTIFACT_REGISTRY_REPO \
    --repository-format=docker \
    --location=$REGION \
    --description="Guardian AI Docker images"

# Configure Docker authentication
gcloud auth configure-docker $REGION-docker.pkg.dev
```

---

## 🆕 Deploying New Microservices

Use this process when deploying a **completely new Guardian AI service** (like Explainer Agent, Ops Guardian, etc.)

### Step 1: Pull Latest Code

```bash
# Navigate to project directory
cd ~/cloudshell_open/anthos-guardian-agent

# Pull latest changes
git pull origin main

# Verify new service directory exists
ls -la src/your-new-service/
```

### Step 2: Configure Deployment Manifests

```bash
# Replace PROJECT_ID placeholder in Kubernetes manifests
sed -i "s/PROJECT_ID/$PROJECT_ID/g" src/your-new-service/k8s/deployment.yaml

# Verify image reference is correct
grep "image:" src/your-new-service/k8s/deployment.yaml
```

**Expected output:**
```yaml
image: us-central1-docker.pkg.dev/your-project-id/bank-guardian-repo/your-new-service
```

### Step 3: Build and Push Docker Image

```bash
# Navigate to service directory
cd src/your-new-service

# Build Docker image
docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/$ARTIFACT_REGISTRY_REPO/your-new-service .

# Push to Artifact Registry
docker push $REGION-docker.pkg.dev/$PROJECT_ID/$ARTIFACT_REGISTRY_REPO/your-new-service
```

### Step 4: Deploy to GKE

```bash
# Go back to root directory
cd ~/cloudshell_open/anthos-guardian-agent

# Deploy the new service
kubectl apply -f src/your-new-service/k8s/deployment.yaml

# Wait for deployment to be ready
kubectl wait --for=condition=ready pod -l app=your-new-service --timeout=300s

# Verify deployment
kubectl get pods | grep your-new-service
kubectl get services | grep your-new-service
```

### Step 5: Test New Service

```bash
# Port forward to test locally
kubectl port-forward service/your-new-service LOCAL_PORT:SERVICE_PORT &

# Test health endpoint
curl http://localhost:LOCAL_PORT/ready

# Test main functionality (service-specific)
curl -X POST http://localhost:LOCAL_PORT/your-endpoint \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}' | python3 -m json.tool
```

---

## 🔄 Updating Existing Microservices

Use this process when updating an **existing Guardian AI service** with new features or bug fixes.

### Step 1: Pull Latest Code

```bash
# Navigate to project directory
cd ~/cloudshell_open/anthos-guardian-agent

# Pull latest changes
git pull origin main

# Check what changed
git log --oneline -5
```

### Step 2: Verify Configuration

```bash
# Ensure PROJECT_ID is still correct in manifests
grep "image:" src/existing-service/k8s/deployment.yaml

# If PROJECT_ID placeholder exists, replace it
sed -i "s/PROJECT_ID/$PROJECT_ID/g" src/existing-service/k8s/deployment.yaml
```

### Step 3: Build and Push Updated Image

```bash
# Navigate to service directory
cd src/existing-service

# Build updated Docker image
docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/$ARTIFACT_REGISTRY_REPO/existing-service .

# Push to Artifact Registry
docker push $REGION-docker.pkg.dev/$PROJECT_ID/$ARTIFACT_REGISTRY_REPO/existing-service
```

### Step 4: Update Deployment

```bash
# Go back to root directory
cd ~/cloudshell_open/anthos-guardian-agent

# Apply updated configuration
kubectl apply -f src/existing-service/k8s/deployment.yaml

# Force rolling update (if needed)
kubectl rollout restart deployment existing-service

# Wait for rollout to complete
kubectl rollout status deployment existing-service

# Verify update
kubectl get pods | grep existing-service
```

### Step 5: Test Updated Service

```bash
# Check logs for any errors
kubectl logs deployment/existing-service --tail=20

# Port forward and test
kubectl port-forward service/existing-service LOCAL_PORT:SERVICE_PORT &

# Test updated functionality
curl http://localhost:LOCAL_PORT/ready
```

---

## 🧪 Testing Deployments

### Health Checks

```bash
# Check all Guardian AI services
kubectl get pods | grep -E "(financial-guardian|explainer-agent|ops-guardian|coordinator-agent)"

# Check service endpoints
kubectl get services | grep -E "(financial-guardian|explainer-agent|ops-guardian|coordinator-agent)"

# Check deployment status
kubectl get deployments | grep -E "(financial-guardian|explainer-agent|ops-guardian|coordinator-agent)"
```

### Service-Specific Tests

#### Financial Guardian
```bash
kubectl port-forward service/financial-guardian 8081:8081 &

curl -X POST http://localhost:8081/fraud/check \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "testuser", 
    "amount": 50000,
    "merchant": "Suspicious Store",
    "location": "Unknown Location",
    "fromAccountNum": "1011226111",
    "toAccountNum": "1033623433"
  }' | python3 -m json.tool
```

#### Explainer Agent
```bash
kubectl port-forward service/explainer-agent 8082:8082 &

curl -X POST http://localhost:8082/explain/event \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "fraud_analysis",
    "source_service": "financial-guardian",
    "context": {
      "fraud_score": 0.95,
      "recommendation": "BLOCK",
      "amount": 50000
    },
    "audience": "customer"
  }' | python3 -m json.tool
```

### Multi-Agent Integration Test

```bash
# Test agent registration
curl -X POST http://localhost:8082/register-agent \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "financial-guardian",
    "agent_type": "security",
    "version": "1.0.0",
    "capabilities": ["fraud_detection", "transaction_analysis"],
    "endpoints": {
      "health": "http://financial-guardian:8081/ready",
      "api": "http://financial-guardian:8081"
    }
  }'

# Check registered agents
curl http://localhost:8082/agents | python3 -m json.tool

# Test multi-agent dashboard
curl http://localhost:8082/dashboard
```

---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. Image Pull Errors
```bash
# Check if image exists in registry
gcloud artifacts docker images list $REGION-docker.pkg.dev/$PROJECT_ID/$ARTIFACT_REGISTRY_REPO

# Verify image reference in deployment
kubectl describe deployment your-service

# Check pod events
kubectl describe pod your-service-pod-name
```

#### 2. Container Startup Issues
```bash
# Check container logs
kubectl logs deployment/your-service

# Check resource limits
kubectl describe deployment your-service

# Check secrets and config maps
kubectl get secrets
kubectl get configmaps
```

#### 3. Service Communication Issues
```bash
# Check service endpoints
kubectl get endpoints

# Test service connectivity from another pod
kubectl run debug --image=busybox -it --rm -- /bin/sh
# Inside the pod:
# wget -qO- http://your-service:port/ready
```

#### 4. Gemini AI Issues
```bash
# Check API key is set
kubectl exec deployment/your-service -- env | grep GEMINI

# Verify API key is valid (from local machine)
curl -H "Authorization: Bearer YOUR_API_KEY" \
  "https://generativelanguage.googleapis.com/v1/models?key=YOUR_API_KEY"

# Check Gemini model name
kubectl logs deployment/your-service | grep -i gemini
```

### Rollback Procedures

#### Quick Rollback
```bash
# Rollback to previous version
kubectl rollout undo deployment/your-service

# Check rollback status
kubectl rollout status deployment/your-service

# Verify rollback
kubectl get pods | grep your-service
```

#### Specific Version Rollback
```bash
# See rollout history
kubectl rollout history deployment/your-service

# Rollback to specific revision
kubectl rollout undo deployment/your-service --to-revision=2
```

---

## 🏭 Production Considerations

### Resource Management

```yaml
# Example resource configuration
resources:
  limits:
    cpu: 500m
    memory: 512Mi
    ephemeral-storage: 0.25Gi
  requests:
    cpu: 250m
    memory: 256Mi
    ephemeral-storage: 0.25Gi
```

### Monitoring and Logging

```bash
# Enable monitoring (if using Google Cloud Monitoring)
kubectl apply -f - <<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: environment-config
data:
  ENABLE_METRICS: "true"
  ENABLE_TRACING: "true"
  LOG_LEVEL: "info"
EOF
```

### Security Best Practices

1. **Use non-root containers** (already configured)
2. **Read-only root filesystem** (already configured)
3. **Drop all capabilities** (already configured)
4. **Use secrets for sensitive data**

```bash
# Update Gemini API key
kubectl create secret generic guardian-secrets \
  --from-literal=GEMINI_API_KEY="your-new-api-key" \
  --dry-run=client -o yaml | kubectl apply -f -
```

### High Availability

```yaml
# Example HA configuration
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
```

---

## 📚 Quick Reference Commands

### Deployment Commands
```bash
# Deploy all Guardian services
kubectl apply -f src/financial-guardian/k8s/deployment.yaml
kubectl apply -f src/explainer-agent/k8s/deployment.yaml

# Update all services
kubectl rollout restart deployment financial-guardian
kubectl rollout restart deployment explainer-agent

# Check all Guardian services
kubectl get pods,services,deployments | grep -E "(financial|explainer|ops|coordinator)"
```

### Debugging Commands
```bash
# Get all logs
kubectl logs -f deployment/financial-guardian
kubectl logs -f deployment/explainer-agent

# Describe resources
kubectl describe deployment financial-guardian
kubectl describe service financial-guardian

# Port forward all services
kubectl port-forward service/financial-guardian 8081:8081 &
kubectl port-forward service/explainer-agent 8082:8082 &
```

### Cleanup Commands
```bash
# Stop port forwards
pkill -f "kubectl port-forward"

# Delete Guardian services (if needed)
kubectl delete -f src/financial-guardian/k8s/deployment.yaml
kubectl delete -f src/explainer-agent/k8s/deployment.yaml
```

---

## 🎯 Summary

This guide covers:

✅ **New Service Deployment** - Complete process from code to production  
✅ **Service Updates** - Rolling updates with zero downtime  
✅ **Testing Procedures** - Comprehensive validation steps  
✅ **Troubleshooting** - Common issues and solutions  
✅ **Production Readiness** - Security, monitoring, and HA considerations  

For questions or issues, refer to the individual service documentation in their respective `src/service-name/README.md` files.

---

**Happy Deploying! 🚀**
