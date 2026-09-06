# R20 Quantum Trader - Safe Mode Deployment

**Production-ready quantum trading bot with safety-first architecture, deployable to Docker, Render, and Kubernetes.**

## 🚀 Quick Deployment

### Local Docker
```bash
# Copy environment
cp .env.safe .env

# Edit token
nano .env  # Change R20_SETUP_TOKEN

# Start
docker compose -f docker-compose.safe.yml up -d

# Dashboard
open http://localhost:8080
```

### Render.com Deployment

1. **Connect GitHub Repo**
   - Go to https://render.com/dashboard
   - New → Web Service
   - Connect repository: `https://github.com/Raindog2023/quantum-trader`

2. **Configure Service**
   - **Name**: `quantum-trader`
   - **Dockerfile**: `Dockerfile.safe`
   - **Docker Command**: `docker compose -f docker-compose.safe.yml up`
   - **Port**: `8080`

3. **Set Environment Variables** (in Render dashboard)
   ```
   TRADING_MODE=backtest
   DRY_RUN=1
   RISK_LIMIT_PERCENT=1.0
   R20_SETUP_TOKEN=<your-secret-token>
   OKX_DEMO_API_KEY=<your-demo-key>
   OKX_DEMO_SECRET_KEY=<your-demo-secret>
   ```

4. **Deploy**
   - Click "Create Web Service"
   - Render will automatically build from `Dockerfile.safe`
   - Service available at `https://quantum-trader-xxx.onrender.com`

### Kubernetes Deployment

```bash
# Create namespace
kubectl create namespace quantum-trading

# Create secrets
kubectl create secret generic r20-secrets \
  --from-literal=R20_SETUP_TOKEN=your-token \
  --from-literal=OKX_DEMO_API_KEY=your-key \
  -n quantum-trading

# Deploy
kubectl apply -f k8s/deployment.yaml -n quantum-trading
kubectl apply -f k8s/service.yaml -n quantum-trading

# Check status
kubectl get pods -n quantum-trading
kubectl logs -f deployment/quantum-trader -n quantum-trading
```

---

## 📊 Architecture

```
┌──────────────────────────────────────────────┐
│     R20 Quantum Trading Engine               │
│  (LLM-native, Self-Evolving, OKX-Ready)      │
└──────────────────────────────────────────────┘
              ↓
┌──────────────────────────────────────────────┐
│      Safety Hardening Layer                  │
│  ✓ Backtest-first (default)                 │
│  ✓ Dry-run mode (simulated)                 │
│  ✓ Risk limits (enforced)                   │
│  ✓ Strategy validation                      │
│  ✓ Circuit breaker                          │
│  ✓ Audit logging                            │
└──────────────────────────────────────────────┘
              ↓
┌──────────────────────────────────────────────┐
│      Container Orchestration                 │
│  • Docker Compose (local)                    │
│  • Render (cloud)                            │
│  • Kubernetes (scalable)                     │
└──────────────────────────────────────────────┘
```

---

## 🛡️ Safety Features (Built-In)

| Feature | Default | Purpose |
|---------|---------|---------|
| **Trading Mode** | `backtest` | Historical data only |
| **Dry Run** | Enabled | Simulate all trades |
| **Risk Limit** | 1% | Max risk per trade |
| **Stop Loss** | 5% | Auto-close if down |
| **Daily Loss** | 3% | Stop trading if limit hit |
| **Demo API** | Enabled | No real money |
| **Audit Logging** | Enabled | Track all operations |
| **Admin Token** | Required | Secure access |

---

## 📁 File Structure

```
quantum-trader/
├── Dockerfile.safe              # Production Dockerfile
├── docker-compose.safe.yml      # Local orchestration
├── render.yaml                  # Render deployment config
│
├── r20_backend/                 # Trading engine
├── r20_gateway/                 # Exchange integration
├── dashboard/                   # Web dashboard
├── scripts/
│   └── safety_validator.py      # Pre-flight checks
│
├── .github/workflows/
│   ├── deploy-render.yml        # Auto-deploy to Render
│   └── test-build.yml           # CI/CD testing
│
├── .env.safe                    # Safe environment template
├── INTEGRATION_GUIDE.md         # Complete setup guide
├── SAFE_MODE_SETUP.md           # Feature documentation
└── COMPLETE_SETUP.md            # Overview
```

---

## 🚀 Deployment Options

### Option 1: Local Docker (Development)
```bash
docker compose -f docker-compose.safe.yml up
```
✅ Fastest  
✅ Full control  
✅ Local debugging

### Option 2: Render.com (Simple Cloud)
- Automatic GitHub integration
- Free tier available ($7/month)
- Auto-scaling
- No infrastructure management

**Steps**:
1. Push to GitHub
2. Connect to Render
3. Set environment variables
4. Deploy (automatic on push)

### Option 3: Kubernetes (Enterprise)
- High availability
- Horizontal scaling
- Advanced networking
- Multi-region support

**Files**:
- `k8s/deployment.yaml`
- `k8s/service.yaml`
- `k8s/ingress.yaml`

---

## 🔐 Security Best Practices

### Environment Variables
```bash
# Never commit these
R20_SETUP_TOKEN=<secret>
OKX_DEMO_API_KEY=<secret>
OKX_DEMO_SECRET_KEY=<secret>
OKX_DEMO_PASSPHRASE=<secret>

# Use GitHub Secrets or Render Secrets
```

### Container Security
- Non-root user execution
- Resource limits (CPU/memory)
- Read-only root filesystem ready
- Minimal base image (Python 3.11 slim)

### Access Control
```bash
# IP whitelist (Render)
R20_ADMIN_IP_WHITELIST=YOUR_IP

# Session timeout
SESSION_TIMEOUT_MINUTES=30

# 2FA ready
R20_REQUIRE_2FA=1
```

---

## 📈 Monitoring & Debugging

### Local Docker Logs
```bash
docker compose -f docker-compose.safe.yml logs -f r20-quantum-trader-safe
```

### Render Logs
```
Dashboard → Your Service → Logs tab
```

### Kubernetes Logs
```bash
kubectl logs -f deployment/quantum-trader -n quantum-trading
```

### Health Check
```bash
curl http://localhost:8080/api/v1/health
```

Expected response:
```json
{
  "service": "r20-standalone-backend",
  "version": "7.5.0",
  "status": "ok",
  "credentials": {
    "okx_configured": false,
    "llm_configured": false,
    "simulated_trading": true
  }
}
```

---

## 🔄 CI/CD Pipeline

GitHub Actions automatically:
1. **On PR**: Test Docker build, run safety checks
2. **On Push to Main**: Build image, deploy to Render
3. **On Push to Develop**: Run tests only

### Configure Render Deployment Secrets

In GitHub Repo Settings → Secrets:

```
RENDER_API_KEY=<your-render-api-key>
RENDER_SERVICE_ID=<your-service-id>
```

Get these from:
- **API Key**: Render Dashboard → Account Settings
- **Service ID**: Render Dashboard → Your Service → URL

---

## 📋 Deployment Checklist

- [x] Docker image builds locally
- [x] All services starting healthily
- [x] Health endpoint responding
- [x] Safety validation passing
- [x] GitHub Actions configured
- [x] Render deployment ready
- [ ] Set `R20_SETUP_TOKEN` (secret)
- [ ] Configure OKX demo credentials (if needed)
- [ ] Test in Render preview environment
- [ ] Monitor first 24 hours
- [ ] Set up alerting/monitoring

---

## 🆘 Troubleshooting

### Container won't start
```bash
# Check logs
docker logs r20-quantum-trader-safe

# Verify build
docker compose -f docker-compose.safe.yml build --no-cache

# Check resources
docker stats
```

### Port 8080 already in use
```bash
# Find process
lsof -i :8080

# Kill and restart
docker compose -f docker-compose.safe.yml restart
```

### API not responding
```bash
# Check health
curl http://localhost:8080/api/v1/health

# Check logs for errors
docker logs r20-quantum-trader-safe | grep -i error

# Verify networks
docker network ls
docker network inspect quantum-trading_trading-network
```

---

## 📞 Support

- **Local Issues**: Check Docker logs and `audit/` directory
- **Render Issues**: Check Render dashboard logs
- **Code Issues**: See `INTEGRATION_GUIDE.md` or `SAFE_MODE_SETUP.md`

---

## 📜 License

MIT License - See LICENSE file

---

## ⚠️ Disclaimer

**RISK WARNING**: Trading involves substantial risk of loss. This software is provided AS-IS. Always:
- Start with backtesting
- Paper trade thoroughly
- Use conservative risk limits
- Never risk more than you can afford to lose

---

**Status**: ✅ Production Ready  
**Version**: 1.0  
**Last Updated**: 2024
