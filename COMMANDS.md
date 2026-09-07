# 🚀 DEPLOYMENT COMMANDS - COMPLETE REFERENCE

## QUICK START (Copy & Paste These Commands)

### Windows (PowerShell)
```powershell
cd C:\Users\Rene\AppData\Local\Docker\quantum-trading
.\DEPLOY_ALL.ps1
```

### Mac/Linux (Bash)
```bash
cd /path/to/quantum-trading
bash DEPLOY_ALL.sh
```

---

## MANUAL DEPLOYMENT STEPS

### Step 1: Create GitHub Repository

Go to: **https://github.com/new**

```
Name:        quantum-trader
Description: R20 LLM-Native Quantum Trading Bot
Visibility:  Public
Initialize:  NO (leave empty)
```

Click **Create repository**

---

### Step 2: Push to GitHub

```bash
cd C:\Users\Rene\AppData\Local\Docker\quantum-trading

# Set remote to your new repo
git remote set-url origin https://github.com/Raindog2023/quantum-trader.git

# Ensure main branch
git branch -M main

# Push code
git push -u origin main --force
```

**Result**: Your code is now on GitHub!

---

### Step 3: Deploy to Render (Cloud)

#### Step 3a: Go to Render
- Visit: **https://render.com**
- Sign up (use GitHub to authorize)
- Click **Dashboard**

#### Step 3b: Create Web Service
- Dashboard → **New** → **Web Service**
- Select: **Raindog2023/quantum-trader**
- Click **Connect**

#### Step 3c: Configure Service
Fill in these settings:

```
Name:                    quantum-trader
Environment:             Docker
Dockerfile:              ./Dockerfile.safe
Docker Compose File:     ./docker-compose.safe.yml
Port:                    8080
Instance Type:           Free (or Starter paid)
Auto-deploy:             Yes
```

#### Step 3d: Set Environment Variables
Copy-paste all of these:

```
TRADING_MODE=backtest
DRY_RUN=1
STRATEGY_VALIDATION=1
RISK_LIMIT_PERCENT=1.0
STOP_LOSS_PERCENT=5.0
DAILY_LOSS_LIMIT_PERCENT=3.0
R20_SETUP_TOKEN=ZDIzMjc1MTgtN2ViZi00MTRkLTgwZTMt
OKX_IS_SIMULATED=1
```

#### Step 3e: Deploy
Click **Create Web Service**

⏳ Wait 5-10 minutes for deployment

**Result**: Service deployed! URL: `https://quantum-trader-xxx.onrender.com`

---

### Step 4: Deploy to Kubernetes

#### Prerequisites
```bash
# Install kubectl (one-time)
# Windows: https://kubernetes.io/docs/tasks/tools/install-kubectl-windows/
# Mac: brew install kubectl
# Linux: curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"

# Verify kubectl installed
kubectl version --client
```

#### Deployment Commands

```bash
cd C:\Users\Rene\AppData\Local\Docker\quantum-trading

# 1. Create namespace
kubectl create namespace quantum-trading

# 2. Create secrets
kubectl create secret generic r20-secrets \
  --from-literal=R20_SETUP_TOKEN=ZDIzMjc1MTgtN2ViZi00MTRkLTgwZTMt \
  --from-literal=OKX_DEMO_API_KEY= \
  --from-literal=OKX_DEMO_SECRET_KEY= \
  -n quantum-trading

# 3. Deploy application
kubectl apply -f k8s/deployment.yaml -n quantum-trading
kubectl apply -f k8s/service.yaml -n quantum-trading

# 4. Check status
kubectl get pods -n quantum-trading

# 5. Wait for ready
kubectl rollout status deployment/quantum-trader -n quantum-trading
```

**Result**: Deployed to Kubernetes!

---

## VERIFY DEPLOYMENTS

### GitHub
```bash
# Check code is pushed
git log --oneline -5

# View on GitHub
open https://github.com/Raindog2023/quantum-trader
```

### Render
```
1. Go to https://render.com/dashboard
2. Find "quantum-trader" service
3. Check "Logs" tab for deployment status
4. Note the service URL (quantum-trader-xxx.onrender.com)
5. Test: curl https://quantum-trader-xxx.onrender.com/api/v1/health
```

### Kubernetes
```bash
# Check deployment
kubectl get deployment -n quantum-trading

# Check pods
kubectl get pods -n quantum-trading

# Check service
kubectl get svc -n quantum-trading

# View logs
kubectl logs -f deployment/quantum-trader -n quantum-trading

# Describe deployment
kubectl describe deployment/quantum-trader -n quantum-trading
```

---

## ACCESS SERVICES

### Local (Docker)
```
URL: http://localhost:8080
Token: ZDIzMjc1MTgtN2ViZi00MTRkLTgwZTMt
```

### Render (Cloud)
```
URL: https://quantum-trader-xxx.onrender.com
Token: ZDIzMjc1MTgtN2ViZi00MTRkLTgwZTMt
```

### Kubernetes (Port-Forward)
```bash
# In one terminal
kubectl port-forward svc/quantum-trader 8080:80 -n quantum-trading

# In another terminal
curl http://localhost:8080/api/v1/health
```

---

## HEALTH CHECKS

### All Deployments
```bash
# Should return healthy status
curl http://localhost:8080/api/v1/health

# Expected response:
# {"service":"r20-standalone-backend","version":"7.5.0","status":"ok","credentials":{"okx_configured":false,"llm_configured":false,"simulated_trading":true}}
```

---

## MONITORING & DEBUGGING

### Docker (Local)
```bash
# View running containers
docker ps

# View logs
docker logs r20-quantum-trader-safe

# View live logs
docker logs -f r20-quantum-trader-safe

# Check container health
docker inspect r20-quantum-trader-safe | grep -A 5 "Health"
```

### Render
```
Dashboard → Your Service → Logs tab
(View deployment logs in real-time)
```

### Kubernetes
```bash
# View all resources
kubectl get all -n quantum-trading

# View pod logs
kubectl logs -f deployment/quantum-trader -n quantum-trading

# Stream logs from all pods
kubectl logs -f -l app=quantum-trader -n quantum-trading

# Describe pod for errors
kubectl describe pod <pod-name> -n quantum-trading

# Get events
kubectl get events -n quantum-trading --sort-by='.lastTimestamp'
```

---

## TROUBLESHOOTING

### GitHub Push Fails
```bash
# Check remote
git remote -v

# Update remote URL
git remote set-url origin https://github.com/Raindog2023/quantum-trader.git

# Try push again
git push -u origin main --force
```

### Render Deployment Fails
1. Check repository is public
2. Verify environment variables are set
3. Check logs in Render dashboard
4. Try manual redeploy: Dashboard → Service → Manual Deploy

### Kubernetes Pod Won't Start
```bash
# Check pod events
kubectl describe pod <pod-name> -n quantum-trading

# Check pod logs
kubectl logs <pod-name> -n quantum-trading

# Check deployment status
kubectl describe deployment quantum-trader -n quantum-trading

# Check if image exists
docker images | grep quantum-trader
```

---

## USEFUL KUBECTL COMMANDS

```bash
# Switch namespace (make quantum-trading default)
kubectl config set-context --current --namespace=quantum-trading

# All future commands use quantum-trading namespace
kubectl get pods
kubectl logs -f deployment/quantum-trader

# Delete everything in namespace
kubectl delete all --all -n quantum-trading

# Delete namespace
kubectl delete namespace quantum-trading

# Restart deployment
kubectl rollout restart deployment/quantum-trader -n quantum-trading

# Scale deployment
kubectl scale deployment quantum-trader --replicas=3 -n quantum-trading

# Update deployment
kubectl set image deployment/quantum-trader quantum-trader=NEW_IMAGE -n quantum-trading

# Port-forward to service
kubectl port-forward svc/quantum-trader 8080:80 -n quantum-trading

# SSH into pod
kubectl exec -it <pod-name> /bin/bash -n quantum-trading
```

---

## COMPLETE DEPLOYMENT FLOW

```
┌─────────────────────────────────────────────────────────┐
│ 1. CREATE GITHUB REPO                                   │
│    https://github.com/new                               │
└──────────────────┬──────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────────┐
│ 2. PUSH TO GITHUB                                       │
│    git push -u origin main --force                      │
└──────────────────┬──────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────────┐
│ 3. DEPLOY TO RENDER (Optional)                          │
│    https://render.com/dashboard                         │
│    - New Web Service                                    │
│    - Connect GitHub repo                               │
│    - Set env vars                                       │
│    - Deploy (auto via GitHub Actions)                  │
└──────────────────┬──────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────────┐
│ 4. DEPLOY TO KUBERNETES (Optional)                      │
│    kubectl create namespace quantum-trading             │
│    kubectl create secret generic r20-secrets ...        │
│    kubectl apply -f k8s/deployment.yaml                 │
│    kubectl apply -f k8s/service.yaml                    │
└──────────────────┬──────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────────┐
│ 5. VERIFY DEPLOYMENTS                                   │
│    - GitHub: Code is pushed                            │
│    - Render: Service running at URL                    │
│    - Kubernetes: Pods are ready                        │
└─────────────────────────────────────────────────────────┘
```

---

## FINAL SUMMARY

| Platform | Command | Status |
|----------|---------|--------|
| **GitHub** | `git push -u origin main --force` | ✅ Push code |
| **Render** | https://render.com → New Web Service | ✅ Cloud deploy |
| **Kubernetes** | `kubectl apply -f k8s/*.yaml` | ✅ Enterprise deploy |
| **Local** | `docker-compose -f docker-compose.safe.yml up` | ✅ Already running |

---

## ⏱️ EXPECTED TIMES

- GitHub push: 1-2 seconds
- Render build & deploy: 5-10 minutes
- Kubernetes deployment: 1-2 minutes

---

**Ready to deploy? Choose your command from above and run it! 🚀**
