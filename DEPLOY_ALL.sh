#!/bin/bash
# R20 Quantum Trader - Complete Deployment Script
# Deploys to: GitHub → Render → Kubernetes

set -e

echo "=================================="
echo "R20 QUANTUM TRADER - DEPLOY ALL"
echo "=================================="
echo ""

# ============================================================================
# STEP 1: GITHUB DEPLOYMENT
# ============================================================================
echo "📍 STEP 1: GitHub Deployment"
echo "=================================="
echo ""

# Check git status
echo "✓ Checking git status..."
cd C:\Users\Rene\AppData\Local\Docker\quantum-trading
git status

echo ""
echo "🔗 GitHub Repo Setup:"
echo "  1. Go to: https://github.com/new"
echo "  2. Create new repository:"
echo "     - Name: quantum-trader"
echo "     - Description: R20 LLM-Native Quantum Trading Bot"
echo "     - Visibility: Public"
echo "     - DO NOT initialize (repo is empty)"
echo "  3. Click 'Create repository'"
echo ""
echo "⏸️  PAUSE HERE - Come back once repo is created!"
echo ""
read -p "Press Enter once GitHub repo is created..."

echo ""
echo "🚀 Pushing to GitHub..."
git remote set-url origin https://github.com/Raindog2023/quantum-trader.git
git branch -M main
git push -u origin main --force

echo "✅ GitHub deployment complete!"
echo "   Repository: https://github.com/Raindog2023/quantum-trader"
echo ""

# ============================================================================
# STEP 2: RENDER DEPLOYMENT
# ============================================================================
echo ""
echo "📍 STEP 2: Render Deployment"
echo "=================================="
echo ""
echo "🔗 Render Setup Instructions:"
echo ""
echo "1. Go to: https://render.com"
echo "2. Sign up with GitHub (authorize)"
echo "3. Dashboard → New → Web Service"
echo "4. Connect GitHub:"
echo "   - Select: Raindog2023/quantum-trader"
echo "   - Click Connect"
echo ""
echo "5. Configure Web Service:"
echo "   - Name: quantum-trader"
echo "   - Environment: Docker"
echo "   - Dockerfile: ./Dockerfile.safe"
echo "   - Docker Compose File: ./docker-compose.safe.yml"
echo "   - Port: 8080"
echo "   - Instance Type: Free (or paid)"
echo ""
echo "6. Environment Variables:"
cat << 'EOF'
   TRADING_MODE=backtest
   DRY_RUN=1
   STRATEGY_VALIDATION=1
   RISK_LIMIT_PERCENT=1.0
   STOP_LOSS_PERCENT=5.0
   DAILY_LOSS_LIMIT_PERCENT=3.0
   R20_SETUP_TOKEN=ZDIzMjc1MTgtN2ViZi00MTRkLTgwZTMt
   OKX_IS_SIMULATED=1
   TRADING_MODE=backtest
EOF
echo ""
echo "7. Click 'Create Web Service'"
echo "8. Wait for deployment (5-10 minutes)"
echo ""
echo "✅ Service URL: https://quantum-trader-xxx.onrender.com"
echo "   (Replace xxx with your service ID)"
echo ""
read -p "Press Enter once Render deployment is complete..."

# ============================================================================
# STEP 3: KUBERNETES DEPLOYMENT
# ============================================================================
echo ""
echo "📍 STEP 3: Kubernetes Deployment"
echo "=================================="
echo ""

echo "🔍 Checking kubectl..."
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl not found!"
    echo "   Install from: https://kubernetes.io/docs/tasks/tools/"
    exit 1
fi

echo "✓ kubectl found: $(kubectl version --client --short)"
echo ""

echo "1️⃣  Creating namespace..."
kubectl create namespace quantum-trading 2>/dev/null || echo "   (namespace already exists)"

echo "2️⃣  Creating secrets..."
kubectl create secret generic r20-secrets \
  --from-literal=R20_SETUP_TOKEN=ZDIzMjc1MTgtN2ViZi00MTRkLTgwZTMt \
  --from-literal=OKX_DEMO_API_KEY= \
  --from-literal=OKX_DEMO_SECRET_KEY= \
  -n quantum-trading \
  2>/dev/null || echo "   (secrets already exist)"

echo "3️⃣  Deploying to Kubernetes..."
kubectl apply -f k8s/deployment.yaml -n quantum-trading
kubectl apply -f k8s/service.yaml -n quantum-trading

echo ""
echo "⏳ Waiting for deployment..."
kubectl rollout status deployment/quantum-trader -n quantum-trading --timeout=5m

echo ""
echo "✅ Kubernetes deployment complete!"
echo ""

echo "📊 Deployment Status:"
kubectl get all -n quantum-trading
echo ""

echo "🔍 View logs:"
echo "   kubectl logs -f deployment/quantum-trader -n quantum-trading"
echo ""

echo "🌐 Access service:"
echo "   kubectl port-forward svc/quantum-trader 8080:80 -n quantum-trading"
echo "   Then visit: http://localhost:8080"
echo ""

# ============================================================================
# SUMMARY
# ============================================================================
echo ""
echo "=================================="
echo "✅ DEPLOYMENT COMPLETE!"
echo "=================================="
echo ""
echo "📍 DEPLOYMENT SUMMARY:"
echo ""
echo "1. GitHub:"
echo "   ✅ Code pushed to: https://github.com/Raindog2023/quantum-trader"
echo ""
echo "2. Render (Cloud):"
echo "   🔗 Go to: https://render.com/dashboard"
echo "   📊 Status: Check dashboard for deployment status"
echo "   🌐 URL: https://quantum-trader-xxx.onrender.com"
echo ""
echo "3. Kubernetes:"
echo "   ✅ Deployed to namespace: quantum-trading"
echo "   📊 Status: Run 'kubectl get all -n quantum-trading'"
echo "   🌐 Access: kubectl port-forward svc/quantum-trader 8080:80"
echo ""
echo "=================================="
echo "🎉 ALL SYSTEMS DEPLOYED!"
echo "=================================="
