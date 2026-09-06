# R20 Quantum Trader - SAFE MODE SETUP GUIDE

## 🛡️ Overview

This is a **production-ready, safety-hardened Docker setup** for the R20 quantum trading engine. All trading is disabled by default and requires explicit opt-in.

## ✅ Safety Features

### 1. **Backtest-First Mode**
- Default: `TRADING_MODE=backtest` (historical data only, no live connections)
- Requires 30+ days of validated backtests before paper trading
- Requires Sharpe ratio ≥ 0.5 minimum

### 2. **Risk Management Hard Limits**
- Max risk per trade: 1% of account (configurable, capped at 5%)
- Stop-loss: 5% (automatic enforcement)
- Daily loss limit: 3% (trading halts if exceeded)
- Position size limits: 100 contracts max

### 3. **Dry-Run Execution**
- All trades simulated by default (`DRY_RUN=1`)
- No real money execution until explicitly enabled
- Demo API by default (`OKX_IS_SIMULATED=1`)

### 4. **Strategy Validation**
- Pre-execution validation enabled by default
- Audit logging of all operations
- Circuit breaker stops trading on errors
- Manual close disabled by default (prevents accidental sells)

### 5. **Admin Security**
- Setup token required (must be changed immediately)
- 2FA available for sensitive operations
- IP whitelist for admin access
- Session timeout: 30 minutes

### 6. **Comprehensive Audit Trail**
- All trades logged to `/app/audit/trades.jsonl`
- All API calls logged to `/app/audit/api.jsonl`
- Safety checks logged to `/app/audit/safety_check_*.json`

---

## 🚀 Quick Start

### Step 1: Copy Safe Environment
```bash
cd quantum-trading
cp .env.safe .env
```

### Step 2: IMPORTANT - Change Admin Token
Edit `.env` and change:
```bash
R20_SETUP_TOKEN=your_long_random_string_here
# Make it at least 32 characters, e.g.:
R20_SETUP_TOKEN=sk_test_abc123def456ghi789jkl012mno345pqr
```

### Step 3: Build & Start in Safe Mode
```bash
# Build the image
docker-compose -f docker-compose.safe.yml build

# Start backtest mode (safest - historical data only)
docker-compose -f docker-compose.safe.yml up

# Dashboard: http://localhost:8080
```

### Step 4: Verify Safety Checks
The startup will run safety validation. Look for:
```
✓ Backtest mode (safest)
✓ Dry-run mode enabled (no execution)
✓ Strategy validation enabled
✓ Stop-loss configured: 5%
✓ Admin token configured
✓ Circuit breaker enabled
```

If you see ✗ errors, the startup will abort. Fix those first.

---

## 📊 Available Operating Modes

### Mode 1: BACKTEST (Default - Safest)
```bash
# Historical data only, no live connections
TRADING_MODE=backtest
DRY_RUN=1

# Start
docker-compose -f docker-compose.safe.yml up
```
✅ Best for testing strategies on historical data
✅ No real API calls
✅ Can backtest years of data quickly

### Mode 2: PAPER TRADING (Demo API)
```bash
# Simulate trading with demo credentials
TRADING_MODE=paper
R20_OKX_ENV=demo
OKX_IS_SIMULATED=1

# Start with paper profile
docker-compose -f docker-compose.safe.yml --profile paper up paper-trading
```
✅ Real-time API calls but no real money
✅ Good for testing live trading logic
✅ Requires demo API credentials

### Mode 3: LIVE TRADING (Not Recommended - Expert Only)
⚠️ **Requires multiple explicit overrides:**
```bash
TRADING_MODE=live
R20_OKX_ENV=live
OKX_LIVE_API_KEY=your_actual_key
OKX_LIVE_SECRET_KEY=your_actual_secret

# AND change manual close to enabled
R20_MANUAL_CLOSE_ENABLED=1

# CRITICAL: Ensure risk limits are conservative
RISK_LIMIT_PERCENT=0.5
STOP_LOSS_PERCENT=3.0
```

⚠️ **DO NOT enable without:**
1. ✅ 30+ days of solid backtest results
2. ✅ 1+ week of successful paper trading
3. ✅ Strong risk management configured
4. ✅ Real 2FA setup
5. ✅ IP whitelist configured

---

## 🔧 Configuration Reference

### Risk Management
```bash
RISK_LIMIT_PERCENT=1.0          # Risk per trade
STOP_LOSS_PERCENT=5.0           # Auto-stop if loss > 5%
TAKE_PROFIT_PERCENT=10.0        # Close if profit > 10%
DAILY_LOSS_LIMIT_PERCENT=3.0    # Stop trading if daily loss > 3%
MAX_POSITION_SIZE=100           # Max contracts per trade
```

### Safety Gates
```bash
DRY_RUN=1                        # Simulate (don't execute)
STRATEGY_VALIDATION=1           # Validate before execution
AUDIT_LOGGING_ENABLED=1         # Log all operations
CIRCUIT_BREAKER_ENABLED=1       # Stop on errors
R20_MANUAL_CLOSE_ENABLED=0      # Disable accidental closes
```

### Security
```bash
R20_SETUP_TOKEN=...             # CHANGE ME IMMEDIATELY
R20_REQUIRE_2FA=1               # Require 2FA for admin
R20_ADMIN_IP_WHITELIST=127.0.0.1,192.168.1.0/24
SESSION_TIMEOUT_MINUTES=30
```

---

## 📈 Backtesting Workflow

### Step 1: Create a Strategy
```bash
# Create file: strategies/my_strategy.py
# Implement your trading logic

# Copy to container
docker cp strategies/my_strategy.py r20-quantum-trader-safe:/app/strategies/
```

### Step 2: Run Backtest
```bash
# Start backtest engine
docker-compose -f docker-compose.safe.yml --profile backtest up backtest-engine

# Results saved to: ./backtest-results/
```

### Step 3: Validate Results
```bash
# Check backtest report
cat backtest-results/my_strategy_backtest.json

# Verify Sharpe ratio >= 0.5
# Verify max drawdown is acceptable
# Verify profit factor > 1.5
```

### Step 4: If Good, Test Paper Trading
```bash
# Edit .env
TRADING_MODE=paper
ACTIVE_STRATEGIES=my_strategy

# Start paper trading
docker-compose -f docker-compose.safe.yml --profile paper up paper-trading

# Paper trade for 1+ weeks
# Monitor: ./logs/ and ./audit/
```

### Step 5: Only Then Consider Live (Expert Only)
```bash
# After successful paper trading results
# Change to live mode with extra caution
TRADING_MODE=live
RISK_LIMIT_PERCENT=0.5  # Extra conservative
```

---

## 🔍 Monitoring & Auditing

### View Trade Audit Log
```bash
tail -f ./audit/trades.jsonl
```

### View API Calls
```bash
tail -f ./audit/api.jsonl
```

### View Safety Checks
```bash
ls -la ./audit/safety_check_*.json
cat ./audit/safety_check_*.json | jq
```

### View Application Logs
```bash
docker-compose -f docker-compose.safe.yml logs -f r20-quantum-trader-safe
```

### View Metrics (if monitoring profile enabled)
```bash
# Enable monitoring
docker-compose -f docker-compose.safe.yml --profile monitoring up

# Prometheus: http://localhost:9090
# Grafana: http://localhost:3000
```

---

## 🆘 Emergency Stop

### Stop All Trading Immediately
```bash
docker-compose -f docker-compose.safe.yml down

# Or kill specific container
docker stop r20-quantum-trader-safe
```

### Check Circuit Breaker Status
```bash
docker-compose -f docker-compose.safe.yml logs r20-quantum-trader-safe | grep "circuit-breaker"
```

### Manual Trade Closure (if needed)
1. SSH into dashboard: `http://localhost:8080/admin`
2. Manual Close button is DISABLED by default (safety feature)
3. If truly needed, enable `R20_MANUAL_CLOSE_ENABLED=1`, then use

---

## 🔐 Security Best Practices

### 1. Never Commit Real Credentials
```bash
# .env is in .gitignore, but verify
git status .env .env.safe .env.local
# Should show "nothing to commit"
```

### 2. Use Secrets Manager for Production
```bash
# Instead of .env, use Docker secrets
docker secret create okx_api_key -
docker secret create okx_secret_key -
```

### 3. Rotate API Keys Regularly
```bash
# Every 30-90 days
# 1. Generate new OKX keys
# 2. Update .env
# 3. Restart container
# 4. Verify with paper trading first
```

### 4. Enable 2FA for Admin
```bash
# In dashboard admin panel
# Settings > Security > Enable 2FA
```

### 5. Monitor IP Access
```bash
# Whitelist only your IPs
R20_ADMIN_IP_WHITELIST=192.168.1.100,203.0.113.50
```

---

## 📋 Deployment Checklist

- [ ] Changed `R20_SETUP_TOKEN` to random 32+ char string
- [ ] Set up demo OKX credentials (if not using backtest only)
- [ ] Configured backup encryption key
- [ ] Enabled audit logging
- [ ] Tested backtest mode successfully
- [ ] Reviewed backtest metrics (Sharpe ratio, max drawdown, profit factor)
- [ ] Paper traded for 1+ weeks with consistent results
- [ ] Set up monitoring/alerts
- [ ] Configured IP whitelist for admin
- [ ] Enabled 2FA
- [ ] Scheduled regular backups
- [ ] Documented strategy logic and rules
- [ ] Ready for live trading (expert only)

---

## 🚨 Common Issues

### Issue: "Safety validation failed"
**Solution:** Check `.env` settings, run:
```bash
docker-compose -f docker-compose.safe.yml logs r20-quantum-trader-safe
```

### Issue: "Circuit breaker tripped"
**Solution:** Check logs for errors, fix, then restart

### Issue: "Backtest results look good but paper trades are bad"
**Solution:** Paper trading has slippage/spreads. This is normal. Adjust risk limits down.

### Issue: "I want to close a trade manually"
**Solution:** Manual close is disabled by default. To enable:
```bash
R20_MANUAL_CLOSE_ENABLED=1
# Restart container
# Then use dashboard
# Re-disable after closing
```

---

## 📞 Support

For issues or questions:
1. Check audit logs: `./audit/`
2. Check application logs: `docker logs r20-quantum-trader-safe`
3. Check safety report: `cat ./audit/safety_check_*.json | jq`
4. Review strategy code for logic errors
5. Run backtest validation again

---

## 📜 License & Disclaimer

**RISK DISCLAIMER:**
This software is provided AS-IS. Trading involves substantial risk of loss. Past performance does not guarantee future results. Always:
- Start with backtesting
- Paper trade thoroughly
- Risk only what you can afford to lose
- Use proper risk management
- Never use leverage you don't understand

---

**Version**: 1.0 Safe Mode
**Last Updated**: 2024
**Status**: Production Ready ✅
