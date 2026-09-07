# R20 Quantum Trader - Complete Deployment Script (Windows)
# Deploys to: GitHub  Render  Kubernetes

Write-Host "=================================="
Write-Host "R20 QUANTUM TRADER - DEPLOY ALL" -ForegroundColor Green
Write-Host "=================================="
Write-Host ""

# ============================================================================
# STEP 1: GITHUB DEPLOYMENT
# ============================================================================
Write-Host " STEP 1: GitHub Deployment" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Navigate to repo
cd C:\Users\Rene\AppData\Local\Docker\quantum-trading

Write-Host " Current git status:" -ForegroundColor Green
git status

Write-Host ""
Write-Host " GitHub Repo Setup Instructions:" -ForegroundColor Yellow
Write-Host "  1. Go to: https://github.com/new"
Write-Host "  2. Create new repository:"
Write-Host "     - Name: quantum-trader"
Write-Host "     - Description: R20 LLM-Native Quantum Trading Bot"
Write-Host "     - Visibility: Public"
Write-Host "     - DO NOT initialize (repo is empty)"
Write-Host "  3. Click 'Create repository'"
Write-Host ""
Write-Host "  PAUSE HERE - Create the repo, then press Enter..." -ForegroundColor Yellow
Read-Host "Press Enter to continue"

Write-Host ""
Write-Host " Pushing code to GitHub..." -ForegroundColor Cyan
git remote set-url origin https://github.com/Raindog2023/quantum-trader.git
git branch -M main
git push -u origin main --force

Write-Host " GitHub deployment complete!" -ForegroundColor Green
Write-Host "   Repository: https://github.com/Raindog2023/quantum-trader"
Write-Host ""

# ============================================================================
# STEP 2: RENDER DEPLOYMENT
# ============================================================================
Write-Host ""
Write-Host " STEP 2: Render Deployment" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""
Write-Host " Render Setup Instructions:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Go to: https://render.com"
Write-Host "2. Sign up with GitHub (authorize)"
Write-Host "3. Dashboard -> New -> Web Service"
Write-Host "4. Connect GitHub:"
Write-Host "   - Select: Raindog2023/quantum-trader"
Write-Host "   - Click Connect"
Write-Host ""
Write-Host "5. Configure Web Service:"
Write-Host "   - Name: quantum-trader"
Write-Host "   - Environment: Docker"
Write-Host "   - Dockerfile: ./Dockerfile.safe"
Write-Host "   - Docker Compose File: ./docker-compose.safe.yml"
Write-Host "   - Port: 8080"
Write-Host ""
Write-Host "6. Environment Variables (copy-paste):" -ForegroundColor Yellow
Write-Host "   TRADING_MODE=backtest"
Write-Host "   DRY_RUN=1"
Write-Host "   STRATEGY_VALIDATION=1"
Write-Host "   RISK_LIMIT_PERCENT=1.0"
Write-Host "   STOP_LOSS_PERCENT=5.0"
Write-Host "   DAILY_LOSS_LIMIT_PERCENT=3.0"
Write-Host "   R20_SETUP_TOKEN=ZDIzMjc1MTgtN2ViZi00MTRkLTgwZTMt"
Write-Host "   OKX_IS_SIMULATED=1"
Write-Host ""
Write-Host "7. Click 'Create Web Service'"
Write-Host "8. Wait for deployment (5-10 minutes)"
Write-Host ""
Write-Host "Service URL: https://quantum-trader-xxx.onrender.com" -ForegroundColor Green
Write-Host ""
Write-Host "PAUSE HERE - Wait for Render deployment to complete..." -ForegroundColor Yellow
Read-Host "Press Enter once Render is deployed"

# ============================================================================
# STEP 3: KUBERNETES DEPLOYMENT
# ============================================================================
Write-Host ""
Write-Host " STEP 3: Kubernetes Deployment" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Check kubectl
Write-Host " Checking kubectl..." -ForegroundColor Yellow
$kubectlExists = $null -ne (Get-Command kubectl -ErrorAction SilentlyContinue)

if (-not $kubectlExists) {
    Write-Host " kubectl not found!" -ForegroundColor Red
    Write-Host "   Install from: https://kubernetes.io/docs/tasks/tools/"
    Write-Host "   Then re-run this script"
    exit 1
}

$kubeVersion = kubectl version --client --short
Write-Host " kubectl found: $kubeVersion" -ForegroundColor Green
Write-Host ""

Write-Host "1  Creating namespace..." -ForegroundColor Yellow
kubectl create namespace quantum-trading 2>$null
Write-Host "    Namespace ready"

Write-Host "2  Creating secrets..." -ForegroundColor Yellow
kubectl create secret generic r20-secrets `
  --from-literal=R20_SETUP_TOKEN=ZDIzMjc1MTgtN2ViZi00MTRkLTgwZTMt `
  --from-literal=OKX_DEMO_API_KEY="" `
  --from-literal=OKX_DEMO_SECRET_KEY="" `
  -n quantum-trading `
  2>$null
Write-Host "    Secrets ready"

Write-Host "3  Deploying to Kubernetes..." -ForegroundColor Yellow
kubectl apply -f k8s/deployment.yaml -n quantum-trading
kubectl apply -f k8s/service.yaml -n quantum-trading

Write-Host ""
Write-Host " Waiting for deployment..." -ForegroundColor Yellow
$maxRetries = 30
$retry = 0
while ($retry -lt $maxRetries) {
    $status = kubectl get deployment quantum-trader -n quantum-trading -o jsonpath='{.status.readyReplicas}' 2>$null
    if ($status -eq "1") {
        Write-Host " Deployment ready!" -ForegroundColor Green
        break
    }
    $retry++
    Start-Sleep -Seconds 2
    Write-Host "   Waiting... ($retry/$maxRetries)" -NoNewline
    Write-Host "`r" -NoNewline
}

Write-Host ""
Write-Host " Kubernetes deployment complete!" -ForegroundColor Green
Write-Host ""

Write-Host " Deployment Status:" -ForegroundColor Cyan
kubectl get all -n quantum-trading

Write-Host ""
Write-Host " Useful commands:" -ForegroundColor Yellow
Write-Host "   View logs:"
Write-Host "   kubectl logs -f deployment/quantum-trader -n quantum-trading"
Write-Host ""
Write-Host "   Access service (port-forward):"
Write-Host "   kubectl port-forward svc/quantum-trader 8080:80 -n quantum-trading"
Write-Host "   Then visit: http://localhost:8080"
Write-Host ""

# ============================================================================
# SUMMARY
# ============================================================================
Write-Host ""
Write-Host "==================================" -ForegroundColor Green
Write-Host " DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green
Write-Host ""
Write-Host " DEPLOYMENT SUMMARY:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. GitHub:" -ForegroundColor Yellow
Write-Host "    Code pushed to: https://github.com/Raindog2023/quantum-trader"
Write-Host ""
Write-Host "2. Render (Cloud):" -ForegroundColor Yellow
Write-Host "    Go to: https://render.com/dashboard"
Write-Host "    Status: Check dashboard for deployment status"
Write-Host "    URL: https://quantum-trader-xxx.onrender.com"
Write-Host ""
Write-Host "3. Kubernetes:" -ForegroundColor Yellow
Write-Host "    Deployed to namespace: quantum-trading"
Write-Host "    View pods: kubectl get pods -n quantum-trading"
Write-Host "    Access: kubectl port-forward svc/quantum-trader 8080:80 -n quantum-trading"
Write-Host ""
Write-Host "==================================" -ForegroundColor Green
Write-Host " ALL SYSTEMS DEPLOYED!" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green
