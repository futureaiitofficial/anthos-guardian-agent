# Bank Guardian AI - Complete Deployment Guide

## 🎯 Overview

This guide provides step-by-step instructions for deploying Bank Guardian AI in two environments:
1. **Local Development** - Using local Kubernetes (minikube/kind) or local GKE cluster
2. **Google Cloud GKE** - Production-ready deployment on Google Kubernetes Engine

---

## 🖥️ **Option 1: Local Development Deployment**

### **Prerequisites**
```bash
# Check if you have required tools
python3 --version    # Should be 3.12+
docker --version
kubectl version --client
skaffold version     # Should be 2.9+

# Install missing tools if needed
# Docker Desktop: https://www.docker.com/products/docker-desktop/
# kubectl: https://kubernetes.io/docs/tasks/tools/install-kubectl/
# skaffold: https://skaffold.dev/docs/install/
```

### **Step 1: Set up Local Kubernetes Cluster**

#### **Option A: Use minikube (Recommended for local dev)**
```bash
# Install minikube if not installed
# macOS: brew install minikube
# Windows: choco install minikube
# Linux: curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64

# Start minikube cluster
minikube start --memory=8192 --cpus=4
minikube addons enable ingress

# Verify cluster is running
kubectl get nodes
```

#### **Option B: Use Docker Desktop Kubernetes**
```bash
# Enable Kubernetes in Docker Desktop settings
# Docker Desktop > Settings > Kubernetes > Enable Kubernetes

# Verify cluster is running
kubectl config current-context  # Should show "docker-desktop"
kubectl get nodes
```

### **Step 2: Deploy Base Bank of Anthos**
```bash
# Navigate to project directory
cd /Users/raja/Development/Hackathon/bank-of-anthos

# Deploy JWT secrets (required for authentication)
kubectl apply -f ./extras/jwt/jwt-secret.yaml

# Deploy base Bank of Anthos services
kubectl apply -f ./kubernetes-manifests

# Wait for all pods to be ready (this may take 5-10 minutes)
kubectl get pods -w

# You should see all pods in "Running" status:
# accounts-db, balancereader, contacts, frontend, ledger-db, 
# ledgerwriter, loadgenerator, transactionhistory, userservice
```

### **Step 3: Get Gemini API Key**
```bash
# 1. Go to https://makersuite.google.com/app/apikey
# 2. Create a new API key
# 3. Copy the key (keep it secret!)

# Encode the API key for Kubernetes secret
echo -n "YOUR_ACTUAL_GEMINI_API_KEY" | base64
# Copy the base64 encoded result
```

### **Step 4: Update Guardian Secrets**
```bash
# Edit the guardian secrets file
nano kubernetes-manifests/guardian-secrets.yaml

# Replace the placeholder with your encoded API key:
# Change: GEMINI_API_KEY: "eW91ci1hY3R1YWwtZ2VtaW5pLWFwaS1rZXk="
# To:     GEMINI_API_KEY: "YOUR_BASE64_ENCODED_KEY"

# Save and exit (Ctrl+X, Y, Enter in nano)
```

### **Step 5: Deploy Financial Guardian**
```bash
# Deploy the guardian secrets
kubectl apply -f kubernetes-manifests/guardian-secrets.yaml

# Build and deploy Financial Guardian using skaffold
skaffold dev --profile development --module financial-guardian

# This will:
# 1. Build the Docker image
# 2. Deploy to your local cluster
# 3. Show real-time logs
# 4. Auto-rebuild on code changes
```

### **Step 6: Test Local Deployment**
```bash
# In a new terminal, port forward the service
kubectl port-forward service/financial-guardian 8081:8081

# Test health endpoint
curl http://localhost:8081/ready
# Should return: {"status": "ready", "service": "financial-guardian"}

# Run the interactive demo
python3 src/financial-guardian/demo_script.py
```

### **Step 7: Access Bank of Anthos Frontend**
```bash
# Port forward the frontend service
kubectl port-forward service/frontend 8080:80

# Open in browser: http://localhost:8080
# Login with: testuser / bankofanthos
```

---

## ☁️ **Option 2: Google Cloud GKE Deployment**

### **Prerequisites**
```bash
# Install Google Cloud SDK if not installed
# macOS: brew install google-cloud-sdk
# Windows: Download from https://cloud.google.com/sdk/docs/install
# Linux: curl https://sdk.cloud.google.com | bash

# Authenticate with Google Cloud
gcloud auth login
gcloud auth configure-docker
```

### **Step 1: Set up Google Cloud Project**
```bash
# Set your project ID (replace with your actual project)
export PROJECT_ID="your-hackathon-project-id"
export REGION="us-central1"
export CLUSTER_NAME="bank-guardian-cluster"

# Set the project
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable container.googleapis.com
gcloud services enable aiplatform.googleapis.com
gcloud services enable artifactregistry.googleapis.com

# Verify billing is enabled
gcloud billing projects describe $PROJECT_ID
```

### **Step 2: Create Artifact Registry**
```bash
# Create repository for container images
gcloud artifacts repositories create bank-guardian-ai \
    --repository-format=docker \
    --location=$REGION \
    --description="Bank Guardian AI container images"

# Configure Docker authentication
gcloud auth configure-docker ${REGION}-docker.pkg.dev
```

### **Step 3: Create GKE Cluster**
```bash
# Create GKE Autopilot cluster (recommended - fully managed)
gcloud container clusters create-auto $CLUSTER_NAME \
    --project=$PROJECT_ID \
    --region=$REGION \
    --release-channel=regular

# Alternative: Create standard GKE cluster
# gcloud container clusters create $CLUSTER_NAME \
#     --project=$PROJECT_ID \
#     --zone=${REGION}-a \
#     --machine-type=e2-standard-4 \
#     --num-nodes=3 \
#     --enable-autoscaling \
#     --min-nodes=1 \
#     --max-nodes=10

# Get cluster credentials
gcloud container clusters get-credentials $CLUSTER_NAME \
    --region=$REGION \
    --project=$PROJECT_ID

# Verify cluster access
kubectl get nodes
```

### **Step 4: Deploy Base Bank of Anthos to GKE**
```bash
# Navigate to project directory
cd /Users/raja/Development/Hackathon/bank-of-anthos

# Deploy JWT secrets
kubectl apply -f ./extras/jwt/jwt-secret.yaml

# Deploy base Bank of Anthos
kubectl apply -f ./kubernetes-manifests

# Wait for all pods to be ready (may take 10-15 minutes on first deployment)
kubectl get pods -w

# Check services (frontend should get external IP)
kubectl get services
```

### **Step 5: Get Gemini API Key and Update Secrets**
```bash
# 1. Get API key from https://makersuite.google.com/app/apikey
# 2. Encode it
echo -n "YOUR_ACTUAL_GEMINI_API_KEY" | base64

# 3. Update guardian secrets
nano kubernetes-manifests/guardian-secrets.yaml
# Replace placeholder with your encoded key

# 4. Deploy secrets
kubectl apply -f kubernetes-manifests/guardian-secrets.yaml
```

### **Step 6: Deploy Financial Guardian to GKE**
```bash
# Set the container registry
export CONTAINER_REGISTRY="${REGION}-docker.pkg.dev/${PROJECT_ID}/bank-guardian-ai"

# Deploy using skaffold
skaffold run --profile development \
    --default-repo=$CONTAINER_REGISTRY \
    --module financial-guardian

# Alternative: Use skaffold dev for development with auto-rebuild
# skaffold dev --profile development \
#     --default-repo=$CONTAINER_REGISTRY \
#     --module financial-guardian
```

### **Step 7: Test GKE Deployment**
```bash
# Check if Financial Guardian is running
kubectl get pods | grep financial-guardian
kubectl get service financial-guardian

# Port forward for testing (in new terminal)
kubectl port-forward service/financial-guardian 8081:8081

# Test health endpoint
curl http://localhost:8081/ready

# Run demo script
python3 src/financial-guardian/demo_script.py
```

### **Step 8: Access Bank of Anthos Frontend on GKE**
```bash
# Get frontend external IP
kubectl get service frontend

# Access via external IP (may take a few minutes to provision)
# Open browser to: http://EXTERNAL_IP
# Login: testuser / bankofanthos
```

### **Step 9: Set up Ingress (Optional - for production)**
```bash
# Create ingress for HTTPS access
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: bank-guardian-ingress
  annotations:
    kubernetes.io/ingress.global-static-ip-name: "bank-guardian-ip"
    networking.gke.io/managed-certificates: "bank-guardian-ssl-cert"
    kubernetes.io/ingress.class: "gce"
spec:
  rules:
  - host: your-domain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend
            port:
              number: 80
      - path: /api/guardian
        pathType: Prefix
        backend:
          service:
            name: financial-guardian
            port:
              number: 8081
EOF
```

---

## 🔧 **Troubleshooting**

### **Common Issues and Solutions**

#### **1. Pods Not Starting**
```bash
# Check pod status
kubectl get pods
kubectl describe pod <pod-name>
kubectl logs <pod-name>

# Common fixes:
# - Insufficient memory: Increase cluster resources
# - Image pull errors: Check registry permissions
# - Missing secrets: Ensure jwt-secret and guardian-secrets are deployed
```

#### **2. API Key Issues**
```bash
# Test if your Gemini API key works
curl -H "Authorization: Bearer YOUR_API_KEY" \
  "https://generativelanguage.googleapis.com/v1/models"

# Should list available models including gemini-pro
```

#### **3. Service Connection Issues**
```bash
# Check if Bank of Anthos services are running
kubectl get services

# Should see: transactionhistory, balancereader, ledgerwriter
# If missing, redeploy base services:
kubectl apply -f ./kubernetes-manifests
```

#### **4. Skaffold Build Issues**
```bash
# Clear skaffold cache
skaffold delete
skaffold cache purge

# Rebuild from scratch
skaffold build --profile development --default-repo=$CONTAINER_REGISTRY
```

#### **5. Local Kubernetes Issues**
```bash
# Reset minikube
minikube delete
minikube start --memory=8192 --cpus=4

# Reset Docker Desktop Kubernetes
# Docker Desktop > Settings > Kubernetes > Reset Kubernetes Cluster
```

---

## 📊 **Verification Checklist**

### **✅ Successful Deployment Indicators:**

#### **Pods Running:**
```bash
kubectl get pods
# Should show all pods in "Running" status:
# - accounts-db-*: 1/1 Running
# - balancereader-*: 1/1 Running
# - contacts-*: 1/1 Running
# - frontend-*: 1/1 Running
# - financial-guardian-*: 1/1 Running
# - ledger-db-*: 1/1 Running
# - ledgerwriter-*: 1/1 Running
# - loadgenerator-*: 1/1 Running
# - transactionhistory-*: 1/1 Running
# - userservice-*: 1/1 Running
```

#### **Services Available:**
```bash
kubectl get services
# Should show services with appropriate IPs:
# - frontend: LoadBalancer with EXTERNAL-IP
# - financial-guardian: ClusterIP 8081
# - Other services: ClusterIP with their ports
```

#### **Health Checks Passing:**
```bash
# Financial Guardian health
curl http://localhost:8081/ready
# Response: {"status": "ready", "service": "financial-guardian"}

curl http://localhost:8081/healthy
# Response: {"status": "healthy", "service": "financial-guardian"}
```

#### **Demo Script Working:**
```bash
python3 src/financial-guardian/demo_script.py
# Should show:
# ✅ Financial Guardian is READY!
# ✅ Financial Guardian is HEALTHY!
# ✅ Started monitoring account
# 🤖 AI Analysis responses for different scenarios
```

---

## 🎯 **Next Steps After Deployment**

### **1. Test Fraud Detection**
- Run the demo script to see AI fraud detection in action
- Test with different transaction amounts and patterns
- Monitor logs for AI analysis results

### **2. Integrate with Frontend**
- Access Bank of Anthos at frontend URL
- Create test transactions
- Observe Financial Guardian monitoring in logs

### **3. Scale and Monitor**
- Monitor resource usage: `kubectl top pods`
- Scale if needed: `kubectl scale deployment financial-guardian --replicas=3`
- View logs: `kubectl logs -f deployment/financial-guardian`

### **4. Implement Other Guardian Services**
- Deploy Ops Guardian for infrastructure monitoring
- Deploy Explainer Agent for natural language reports
- Deploy Coordinator Agent for agent-to-agent communication

### **5. Prepare for Demo**
- Document your deployment process
- Create demo scenarios showing fraud detection
- Prepare video showing the system in action

---

## 🚀 **Quick Start Commands Summary**

### **Local Development:**
```bash
cd /Users/raja/Development/Hackathon/bank-of-anthos
minikube start --memory=8192 --cpus=4
kubectl apply -f ./extras/jwt/jwt-secret.yaml
kubectl apply -f ./kubernetes-manifests
# Update guardian-secrets.yaml with your API key
kubectl apply -f kubernetes-manifests/guardian-secrets.yaml
skaffold dev --profile development --module financial-guardian
```

### **GKE Deployment:**
```bash
export PROJECT_ID="your-project-id"
export REGION="us-central1"
gcloud container clusters create-auto bank-guardian-cluster --project=$PROJECT_ID --region=$REGION
gcloud container clusters get-credentials bank-guardian-cluster --region=$REGION --project=$PROJECT_ID
cd /Users/raja/Development/Hackathon/bank-of-anthos
kubectl apply -f ./extras/jwt/jwt-secret.yaml
kubectl apply -f ./kubernetes-manifests
# Update guardian-secrets.yaml with your API key
kubectl apply -f kubernetes-manifests/guardian-secrets.yaml
skaffold run --profile development --default-repo=${REGION}-docker.pkg.dev/${PROJECT_ID}/bank-guardian-ai --module financial-guardian
```

Your Bank Guardian AI is now ready to protect the banking system with intelligent fraud detection! 🛡️🤖
