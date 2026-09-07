#!/bin/bash
# Docker Security Audit Script
# Run this to verify all security hardening is in place

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=================================================="
echo "DOCKER SECURITY AUDIT"
echo "=================================================="
echo ""

PASSED=0
FAILED=0
WARNINGS=0

# Function to print results
pass() {
    echo -e "${GREEN}✅ PASS${NC}: $1"
    ((PASSED++))
}

fail() {
    echo -e "${RED}❌ FAIL${NC}: $1"
    ((FAILED++))
}

warn() {
    echo -e "${YELLOW}⚠️  WARN${NC}: $1"
    ((WARNINGS++))
}

# 1. Check for root user
echo ""
echo "1️⃣  Checking for root user in running containers..."
ROOT_CONTAINERS=0
while IFS= read -r line; do
    if [[ "$line" == *"root"* ]] || [[ "$line" == *"0"* && "$line" != *"appuser"* ]]; then
        echo "  Container: $line"
        ((ROOT_CONTAINERS++))
    fi
done < <(docker ps --format "table {{.Names}}\t{{.Config.User}}" | tail -n +2)

if [ $ROOT_CONTAINERS -eq 0 ]; then
    pass "All containers running as non-root"
else
    fail "Found $ROOT_CONTAINERS container(s) running as root"
fi

# 2. Check port bindings
echo ""
echo "2️⃣  Checking port bindings (should be 127.0.0.1, not 0.0.0.0)..."
EXPOSED_PORTS=0
while IFS= read -r line; do
    if [[ "$line" == *"0.0.0.0"* ]]; then
        echo "  $line"
        ((EXPOSED_PORTS++))
    fi
done < <(docker ps --format "table {{.Names}}\t{{.Ports}}" | tail -n +2)

if [ $EXPOSED_PORTS -eq 0 ]; then
    pass "All ports properly restricted"
else
    warn "Found $EXPOSED_PORTS port(s) exposed to 0.0.0.0 (can be OK with firewall rules)"
fi

# 3. Check for privileged containers
echo ""
echo "3️⃣  Checking for privileged containers..."
PRIV_CONTAINERS=$(docker ps --format "{{.HostConfig.Privileged}}" | grep -c "true" || true)
if [ $PRIV_CONTAINERS -eq 0 ]; then
    pass "No privileged containers found"
else
    fail "Found $PRIV_CONTAINERS privileged container(s)"
fi

# 4. Check security options
echo ""
echo "4️⃣  Checking security options (no-new-privileges should be set)..."
NO_SEC_OPT=0
for container in $(docker ps -q); do
    secopt=$(docker inspect "$container" --format='{{json .HostConfig.SecurityOpt}}' 2>/dev/null || echo "[]")
    if [[ "$secopt" == "null" ]] || [[ "$secopt" == "[]" ]]; then
        name=$(docker inspect "$container" --format='{{.Name}}' | cut -d/ -f2)
        echo "  Missing security options: $name"
        ((NO_SEC_OPT++))
    fi
done

if [ $NO_SEC_OPT -eq 0 ]; then
    pass "All containers have security options set"
else
    warn "Found $NO_SEC_OPT container(s) without security options"
fi

# 5. Check capabilities
echo ""
echo "5️⃣  Checking dropped capabilities..."
for container in $(docker ps -q); do
    caps=$(docker inspect "$container" --format='{{json .HostConfig.CapDrop}}' 2>/dev/null || echo "null")
    if [[ "$caps" == "null" ]] || [[ "$caps" == "[]" ]]; then
        name=$(docker inspect "$container" --format='{{.Name}}' | cut -d/ -f2)
        echo "  Not dropping capabilities: $name"
    fi
done

# 6. Check resource limits
echo ""
echo "6️⃣  Checking resource limits (CPU & Memory)..."
MISSING_LIMITS=0
for container in $(docker ps -q); do
    cpu_limit=$(docker inspect "$container" --format='{{.HostConfig.CpuQuota}}')
    mem_limit=$(docker inspect "$container" --format='{{.HostConfig.Memory}}')
    
    if [[ "$cpu_limit" == "0" ]] || [[ "$mem_limit" == "0" ]]; then
        name=$(docker inspect "$container" --format='{{.Name}}' | cut -d/ -f2)
        echo "  Missing resource limits: $name"
        ((MISSING_LIMITS++))
    fi
done

if [ $MISSING_LIMITS -eq 0 ]; then
    pass "All containers have resource limits set"
else
    warn "Found $MISSING_LIMITS container(s) without resource limits"
fi

# 7. Check read-only filesystem
echo ""
echo "7️⃣  Checking read-only root filesystem..."
for container in $(docker ps -q); do
    ro=$(docker inspect "$container" --format='{{.HostConfig.ReadonlyRootfs}}')
    if [[ "$ro" != "true" ]]; then
        name=$(docker inspect "$container" --format='{{.Name}}' | cut -d/ -f2)
        warn "Not read-only: $name (consider using tmpfs for /tmp and /run)"
    fi
done

# 8. Check logging configuration
echo ""
echo "8️⃣  Checking logging configuration..."
for container in $(docker ps -q); do
    driver=$(docker inspect "$container" --format='{{.HostConfig.LogConfig.Type}}')
    if [[ "$driver" != "json-file" ]] && [[ "$driver" != "splunk" ]]; then
        name=$(docker inspect "$container" --format='{{.Name}}' | cut -d/ -f2)
        warn "Non-standard logging driver: $name uses $driver"
    fi
done

# 9. Check restart policy
echo ""
echo "9️⃣  Checking restart policy..."
MISSING_RESTART=0
for container in $(docker ps -q); do
    policy=$(docker inspect "$container" --format='{{.HostConfig.RestartPolicy.Name}}')
    if [[ "$policy" == "" ]] || [[ "$policy" == "no" ]]; then
        name=$(docker inspect "$container" --format='{{.Name}}' | cut -d/ -f2)
        ((MISSING_RESTART++))
    fi
done

if [ $MISSING_RESTART -eq 0 ]; then
    pass "All containers have restart policies set"
else
    warn "Found $MISSING_RESTART container(s) without restart policy"
fi

# Summary
echo ""
echo "=================================================="
echo "AUDIT SUMMARY"
echo "=================================================="
echo -e "${GREEN}PASSED:${NC}   $PASSED"
echo -e "${RED}FAILED:${NC}   $FAILED"
echo -e "${YELLOW}WARNINGS:${NC} $WARNINGS"
echo ""

if [ $FAILED -gt 0 ]; then
    echo -e "${RED}❌ SECURITY AUDIT FAILED${NC}"
    exit 1
elif [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}⚠️  SECURITY AUDIT PASSED WITH WARNINGS${NC}"
    exit 0
else
    echo -e "${GREEN}✅ SECURITY AUDIT PASSED${NC}"
    exit 0
fi
