# R20 Quantum Trading - INTEGRATED SAFE DOCKER SETUP
## Complete Integration Guide with Safety Controls

---

## 📦 What Was Built

A **production-ready, safety-hardened Docker setup** for quantum trading with:
- ✅ **Backtest-first architecture** (default safest mode)
- ✅ **Risk management hard limits** (cannot be exceeded)
- ✅ **Dry-run execution** (simulated trading by default)
- ✅ **Comprehensive audit logging** (every trade tracked)
- ✅ **Strategy validation** (pre-execution checks)
- ✅ **Circuit breaker** (automatic stop on errors)
- ✅ **Multiple operating modes** (backtest → paper → live with guardrails)
- ✅ **Resource limits** (CPU/memory constraints)
- ✅ **Admin security** (tokens, 2FA ready, IP whitelist)

---

## 🎯 Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│         R20 Quantum Trading - Safe Container            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Trading Engine (FastAPI + Uvicorn)                    │
│  ├─ Backtest Engine                                    │
│  ├─ Paper Trading Simulator                            │
│  └─ Live Trading (locked by default)                   │
│                                                         │
│  Safety Layer                                          │
│  ├─ Risk Management (hard limits)                      │
│  ├─ Strategy Validator                                │
│  ├─ Circuit Breaker                                   │
│  ├─ Audit Logger                                      │
│  └─ Health Monitor                                    │
│                                                         │
│  Data Persistence                                      │
│  ├─ /app/data (strategy state)                         │
│  ├─ /app/logs (application logs)                       │
│  ├─ /app/backups (encrypted backups)                   │
│  ├─ /app/audit (trade/API audit logs)                  │
│  └─ /app/strategies (strategy definitions)             │
│                                                         │
└─────────────────────────────────────────────────────────┘

Resource Limits:
  CPU: 2 cores (reserved: 1 core)
  Memory: 2GB (reserved: 1GB)
  Disk: Unlimited (but audit/backups managed)
```

---

## 🚀 Quick Start (5 Minutes)

### 1. Copy Safe Environment
```bash
cd C:\Users\Rene\AppData\Local\Docker\quantum-trading
cp .env.safe .env
```

### 2. CRITICAL: Change Admin Token
```bash
# Edit .env
# Find: R20_SETUP_TOKEN=
# Change to: R20_SETUP_TOKEN=abc123def456ghi789jkl012mno345pqr

# Make it at least 32 random characters
# Generate: python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Start in Safe Mode
```bash
# Build image (one time, already done!)
docker compose -f docker-compose.safe.yml build

# Start backtest mode (safest - historical data only)
docker compose -f docker-compose.safe.yml up

# Dashboard: http://localhost:8080
# Admin Token: (from your .env)
```

### 4. Verify Safety Checks
Watch for startup messages:
```
✅ SAFETY VALIDATION PASSED - Safe to proceed
✓ Backtest mode (safest)
✓ Dry-run mode enabled (no execution)
✓ Strategy validation enabled
✓ Stop-loss configured: 5%
✓ Risk limit OK: 1.0%
✓ Circuit breaker enabled
```

---

## 📊 Operating Modes

### Mode 1: BACKTEST (Default - Recommended for Learning)
```bash
TRADING_MODE=backtest
DRY_RUN=1
```
✅ **Best for**: Testing strategies on historical data
✅ **Speed**: Very fast (process years of data in minutes)
✅ **Cost**: Free
✅ **Risk**: None (no API calls)

**Use case**:
1. Develop trading strategy
2. Run backtest on 1-2 years of data
3. Verify Sharpe ratio > 0.5
4. Check max drawdown < 20%

### Mode 2: PAPER TRADING (Recommended After Successful Backtests)
```bash
TRADING_MODE=paper
R20_OKX_ENV=demo
OKX_IS_SIMULATED=1
```
✅ **Best for**: Testing live trading logic with simulated money
✅ **Cost**: Free
✅ **Risk**: None (demo API, no real money)
✅ **Duration**: 1-4 weeks

**Use case**:
1. Run strategy on paper trading for 1+ week
2. Verify it performs similarly to backtest
3. Check that slippage/spreads are acceptable
4. Gain confidence in the system

### Mode 3: LIVE TRADING (Expert Only - Use at Your Own Risk)
⚠️ **Requires explicit overrides + multiple checks**

```bash
TRADING_MODE=live
R20_OKX_ENV=live
OKX_LIVE_API_KEY=your_real_key
OKX_LIVE_SECRET_KEY=your_real_secret
RISK_LIMIT_PERCENT=0.5          # Extra conservative
STOP_LOSS_PERCENT=3.0           # Tighter
```

⚠️ **Prerequisites**:
- [ ] 30+ days successful backtest (Sharpe > 1.0)
- [ ] 2+ weeks successful paper trading (profit > 10%)
- [ ] Real 2FA setup
- [ ] IP whitelist configured
- [ ] Admin token set to strong random value
- [ ] Backup encryption key set
- [ ] Circuit breaker understood and tested
- [ ] Risk limits reviewed multiple times

---

## 🔐 Safety Features Explained

### 1. Risk Management Hard Limits
These **cannot be exceeded** - built into the engine:

```bash
RISK_LIMIT_PERCENT=1.0          # Max 1% risk per trade
MAX_POSITION_SIZE=100            # Max 100 contracts
STOP_LOSS_PERCENT=5.0            # Auto-close if down 5%
DAILY_LOSS_LIMIT_PERCENT=3.0     # Stop trading if daily loss > 3%
```

**How it works**: If any trade exceeds these limits, it's auto-rejected.

### 2. Dry-Run Mode
All trades simulated, **never executed**:
```bash
DRY_RUN=1  # Enabled by default
```

**How it works**: Trades are logged and processed but not sent to exchange.

### 3. Strategy Validation
Pre-execution checks before any trade:
```bash
STRATEGY_VALIDATION=1  # Enabled by default
```

**Checks**:
- Strategy file syntax OK?
- Risk parameters within limits?
- Previous backtest successful?
- Are we in safe trading hours?

### 4. Circuit Breaker
Automatic stop if errors occur:
```bash
CIRCUIT_BREAKER_ENABLED=1
CIRCUIT_BREAKER_THRESHOLD=5  # Stop after 5 errors
```

**How it works**: If 5 errors occur in 1 hour, stop trading and alert admin.

### 5. Admin Security
Protect sensitive operations:
```bash
R20_SETUP_TOKEN=...            # Change immediately
R20_REQUIRE_2FA=1              # 2FA for admin
R20_ADMIN_IP_WHITELIST=127.0.0.1,192.168.1.0/24
SESSION_TIMEOUT_MINUTES=30
```

### 6. Audit Logging
Every operation tracked:
```bash
AUDIT_LOGGING_ENABLED=1
```

**Logs**:
- `/app/audit/trades.jsonl` - Every trade
- `/app/audit/api.jsonl` - Every API call
- `/app/audit/safety_check_*.json` - Safety checks

---

## 🔧 Configuration Deep Dive

### Essential Settings (MUST configure)
```bash
# 1. Change this immediately!
R20_SETUP_TOKEN=your_long_random_token_32_chars_minimum

# 2. Set demo credentials (if using paper trading)
OKX_DEMO_API_KEY=your_demo_key
OKX_DEMO_SECRET_KEY=your_demo_secret
OKX_DEMO_PASSPHRASE=your_demo_passphrase

# 3. Backup encryption (protect your data)
R20_BACKUP_ENCRYPTION_KEY=your_backup_encryption_key
```

### Risk Management (Set to Your Comfort Level)
```bash
# Most conservative (start here):
RISK_LIMIT_PERCENT=0.5
STOP_LOSS_PERCENT=3.0
DAILY_LOSS_LIMIT_PERCENT=2.0

# Moderate:
RISK_LIMIT_PERCENT=1.0
STOP_LOSS_PERCENT=5.0
DAILY_LOSS_LIMIT_PERCENT=3.0

# Aggressive (not recommended):
RISK_LIMIT_PERCENT=2.0
STOP_LOSS_PERCENT=10.0
DAILY_LOSS_LIMIT_PERCENT=5.0
```

### Notifications (Optional)
```bash
# Telegram alerts
R20_NOTIFY_TELEGRAM_ENABLED=1
R20_TELEGRAM_BOT_TOKEN=your_bot_token
R20_TELEGRAM_CHAT_ID=your_chat_id

# Webhook (custom integration)
R20_NOTIFY_WEBHOOK_ENABLED=1
R20_NOTIFICATION_WEBHOOK=https://your-service.example/webhook
```

---

## 📈 Backtesting Workflow

### Step 1: Create Strategy
```bash
# Create: strategies/my_momentum_strategy.py
import pandas as pd

def signal(bars):
    """Generate buy/sell signals"""
    if bars['close'].tail(1).values[0] > bars['close'].tail(20).mean():
        return 'BUY'
    elif bars['close'].tail(1).values[0] < bars['close'].tail(20).mean():
        return 'SELL'
    return 'HOLD'
```

### Step 2: Run Backtest
```bash
# Start backtest engine
docker compose -f docker-compose.safe.yml --profile backtest up backtest-engine

# It will process historical data and save results to:
# ./backtest-results/my_momentum_strategy_backtest.json
```

### Step 3: Analyze Results
```bash
# View backtest report
cat backtest-results/my_momentum_strategy_backtest.json | jq

# Look for:
# - sharpe_ratio > 0.5 (good) or > 1.0 (excellent)
# - max_drawdown < 20% (acceptable) or < 10% (good)
# - profit_factor > 1.5 (good) or > 2.0 (excellent)
# - win_rate > 40% (acceptable)
```

### Step 4: Paper Trade (1-4 weeks)
```bash
# Update .env
TRADING_MODE=paper
ACTIVE_STRATEGIES=my_momentum_strategy

# Start paper trading
docker compose -f docker-compose.safe.yml --profile paper up paper-trading

# Monitor: http://localhost:8081 (paper trading dashboard)
# Check daily: logs and audit files
```

### Step 5: Go Live (If Results Are Strong)
```bash
# Only if:
# ✅ Backtest Sharpe > 1.0
# ✅ Paper trading profitable for 2+ weeks
# ✅ Max drawdown < 15%

TRADING_MODE=live
# (plus all other live settings)
docker compose -f docker-compose.safe.yml up
```

---

## 🛠️ Troubleshooting

### Issue: "Safety validation failed"
```bash
# Check logs
docker compose -f docker-compose.safe.yml logs r20-quantum-trader-safe

# Verify .env settings
cat .env.safe | grep -E "^(TRADING_MODE|DRY_RUN|STRATEGY_VALIDATION)"

# Expected output:
# TRADING_MODE=backtest
# DRY_RUN=1
# STRATEGY_VALIDATION=1
```

### Issue: "Circuit breaker tripped"
```bash
# Check audit logs for errors
tail -f ./audit/api.jsonl | grep "error"

# Restart container after fixing
docker compose -f docker-compose.safe.yml restart r20-quantum-trader-safe
```

### Issue: "Backtest results poor"
```bash
# Review strategy logic
cat strategies/my_strategy.py

# Try different parameters:
# - Shorter/longer moving averages
# - Different timeframes
# - Different risk management

# Re-run backtest
docker compose -f docker-compose.safe.yml --profile backtest up backtest-engine
```

### Issue: "Paper trading results different from backtest"
**This is normal!** Paper trading includes:
- Real-time slippage
- Real bid-ask spreads
- Market microstructure

**Solution**: Adjust strategy to be more robust to these costs.

---

## 📊 Monitoring & Observability

### Real-Time Logs
```bash
# Application logs
docker compose -f docker-compose.safe.yml logs -f r20-quantum-trader-safe

# Audit logs (all trades)
tail -f ./audit/trades.jsonl

# API logs
tail -f ./audit/api.jsonl
```

### Health Check
```bash
# Is the container healthy?
docker compose -f docker-compose.safe.yml ps

# Should show "healthy"
# If "unhealthy", check logs

# Manual health check
curl http://localhost:8080/api/v1/health
```

### Backup Verification
```bash
# Check backup status
ls -lah ./backups/

# Verify encryption
file ./backups/*.enc
```

---

## 🆘 Emergency Procedures

### Stop All Trading Immediately
```bash
docker compose -f docker-compose.safe.yml down

# Or just stop the container
docker stop r20-quantum-trader-safe
```

### Recover from Backup
```bash
# List backups
ls -la ./backups/

# Restore from backup (requires encryption key)
docker compose -f docker-compose.safe.yml up

# In admin panel, go to Settings > Restore
# Upload backup file and provide encryption key
```

### Manual Trade Closure
```bash
# Edit .env (ONLY if absolutely necessary)
R20_MANUAL_CLOSE_ENABLED=1

# Restart
docker compose -f docker-compose.safe.yml restart

# Close trade in dashboard
# Then re-disable
R20_MANUAL_CLOSE_ENABLED=0
```

---

## 📋 Deployment Checklist

Before going live, verify all of these:

```bash
☐ R20_SETUP_TOKEN changed to random 32+ character string
☐ OKX demo credentials configured (if using paper trading)
☐ R20_BACKUP_ENCRYPTION_KEY set
☐ Audit logging enabled and verified working
☐ Backtest results reviewed and documented
☐ Sharpe ratio > 0.5 (minimum acceptable)
☐ Max drawdown < 20% (acceptable) or < 10% (good)
☐ Paper trading completed for 1+ weeks
☐ Paper trading profit > 10% (or breakeven minimum)
☐ Circuit breaker tested by deliberately causing errors
☐ Manual close tested (then re-disabled)
☐ Health check working: curl http://localhost:8080/api/v1/health
☐ Backup encryption tested
☐ Monitoring/alerts configured
☐ IP whitelist set up for admin
☐ 2FA enabled
☐ Strategy code reviewed for logic errors
☐ Risk limits set conservatively (RISK_LIMIT_PERCENT=0.5%)
☐ Stop loss tested
☐ Daily loss limit set
☐ Read through this guide entirely
☐ Understand you can lose money
☐ Ready to start with minimal position size
```

---

## 🔒 Security Hardening Checklist

```bash
☐ Dockerfile runs as non-root user (trader:trader)
☐ Memory limits enforced (2GB max)
☐ CPU limits enforced (2 cores max)
☐ API keys stored in .env (never in code)
☐ Secrets not committed to git
☐ Audit logging of all operations
☐ Session timeout set to 30 minutes
☐ 2FA available and documented
☐ IP whitelist for admin access
☐ Regular backups encrypted
☐ Database encryption enabled
☐ Health checks configured
☐ Circuit breaker tested
☐ Error handling comprehensive
☐ No hardcoded credentials anywhere
```

---

## 📞 Support & Resources

### Files in This Setup
- `Dockerfile.safe` - Safety-hardened container image
- `docker-compose.safe.yml` - Complete orchestration
- `.env.safe` - Safe configuration template
- `SAFE_MODE_SETUP.md` - This guide
- `scripts/safety_validator.py` - Pre-flight safety checks
- `entrypoint.safe.sh` - Startup script with checks

### Key Directories
- `./data/` - Strategy state & database
- `./logs/` - Application logs
- `./audit/` - Trade audit logs
- `./backups/` - Encrypted backups
- `./strategies/` - Your trading strategies
- `./backtest-results/` - Backtest output

### Next Steps
1. **Read** `SAFE_MODE_SETUP.md` completely
2. **Configure** `.env` with your settings
3. **Start** in backtest mode: `docker compose -f docker-compose.safe.yml up`
4. **Test** your strategy with backtesting
5. **Paper trade** for 2-4 weeks
6. **Monitor** audit logs daily
7. **Only then** consider live trading

---

## ⚠️ Risk Disclaimer

**IMPORTANT**: Trading involves substantial risk of loss.
- Past performance does not guarantee future results
- You can lose more than your initial investment
- Leverage can amplify losses
- Always start with minimal position size
- Use proper risk management
- Never trade with money you can't afford to lose

---

**Status**: ✅ Production Ready  
**Version**: 1.0  
**Last Updated**: 2024
