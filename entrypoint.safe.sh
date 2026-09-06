#!/bin/bash
# R20 Quantum Trader - Safe Docker Startup Script
# Performs pre-flight checks before running trading engine

set -e

echo "=================================="
echo "R20 QUANTUM TRADER - SAFE STARTUP"
echo "=================================="

# Load environment
export $(cat .env.safe | grep -v '^#' | xargs)

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check 1: Ensure .env.safe exists
if [ ! -f ".env.safe" ]; then
    echo -e "${RED}✗ .env.safe not found${NC}"
    echo "Copy from env.example: cp .env.example .env.safe"
    exit 1
fi

echo -e "${GREEN}✓ .env.safe found${NC}"

# Check 2: Verify trading mode
TRADING_MODE=${TRADING_MODE:-backtest}
echo -e "Trading Mode: ${YELLOW}${TRADING_MODE}${NC}"

if [ "$TRADING_MODE" = "live" ]; then
    echo -e "${RED}✗ LIVE trading mode detected${NC}"
    echo "This requires explicit override. Edit .env.safe to enable."
    exit 1
fi

# Check 3: Verify demo environment
if [ "$R20_OKX_ENV" = "live" ] && [ -z "$OKX_LIVE_API_KEY" ]; then
    echo -e "${YELLOW}⚠ Live environment but no credentials${NC}"
fi

# Check 4: Create required directories
mkdir -p data logs backups audit strategies config backtest-results

# Check 5: Run Python safety validator
echo "Running safety validator..."
python3 scripts/safety_validator.py

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Safety validation failed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ All pre-flight checks passed${NC}"
echo ""

# Check 6: Display configuration summary
echo "=================================="
echo "CONFIGURATION SUMMARY"
echo "=================================="
echo "Trading Mode:        $TRADING_MODE"
echo "Risk Limit:          ${RISK_LIMIT_PERCENT}%"
echo "Stop Loss:           ${STOP_LOSS_PERCENT}%"
echo "Dry Run:             $DRY_RUN"
echo "Strategy Validation: $STRATEGY_VALIDATION"
echo "Audit Logging:       $AUDIT_LOGGING_ENABLED"
echo "=================================="
echo ""

# Check 7: Display usage instructions
echo -e "${GREEN}Starting R20 Quantum Trader...${NC}"
echo ""
echo "Dashboard:    http://localhost:8080"
echo "Admin token:  $R20_SETUP_TOKEN"
echo ""
echo "IMPORTANT:"
echo "1. Change R20_SETUP_TOKEN immediately after first login"
echo "2. Do NOT enable live trading without thorough backtesting"
echo "3. Monitor audit logs at: ./audit/"
echo "4. Check logs at: ./logs/"
echo ""

# Start the application
exec python3 -m uvicorn r20_backend.app:app --host 0.0.0.0 --port 8080
