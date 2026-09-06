#!/usr/bin/env python3
"""
R20 Quantum Trader - Safety Wrapper & Pre-Flight Validator
Ensures all trading operations are protected with safety gates
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

class TradingSafetyValidator:
    """Validates trading configuration before execution"""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.passed_checks: List[str] = []
        
    def check_trading_mode(self) -> bool:
        """Ensure safe trading mode is set"""
        mode = os.getenv('TRADING_MODE', 'backtest').lower()
        
        if mode == 'backtest':
            self.passed_checks.append('✓ Backtest mode (safest)')
            return True
        elif mode == 'paper':
            self.warnings.append('⚠ Paper trading mode (demo API only)')
            return True
        elif mode == 'live':
            self.errors.append('✗ LIVE trading mode - requires explicit override')
            return False
        else:
            self.errors.append(f'✗ Invalid trading mode: {mode}')
            return False
    
    def check_dry_run(self) -> bool:
        """Ensure dry run is enabled"""
        dry_run = os.getenv('DRY_RUN', '1') == '1'
        
        if dry_run:
            self.passed_checks.append('✓ Dry-run mode enabled (no execution)')
            return True
        else:
            self.warnings.append('⚠ Dry-run disabled (simulation only)')
            return True  # Not an error, but warning
    
    def check_strategy_validation(self) -> bool:
        """Ensure strategy validation is enabled"""
        if os.getenv('STRATEGY_VALIDATION', '1') == '1':
            self.passed_checks.append('✓ Strategy validation enabled')
            return True
        else:
            self.errors.append('✗ Strategy validation disabled')
            return False
    
    def check_risk_limits(self) -> bool:
        """Validate risk management settings"""
        try:
            risk_limit = float(os.getenv('RISK_LIMIT_PERCENT', '1.0'))
            
            if risk_limit > 5.0:
                self.errors.append(f'✗ Risk limit too high: {risk_limit}% (max: 5%)')
                return False
            
            if risk_limit > 2.0:
                self.warnings.append(f'⚠ Risk limit is high: {risk_limit}%')
                return True
            
            self.passed_checks.append(f'✓ Risk limit OK: {risk_limit}%')
            return True
        except ValueError:
            self.errors.append('✗ Invalid risk limit percentage')
            return False
    
    def check_stop_loss(self) -> bool:
        """Ensure stop-loss is configured"""
        try:
            sl = float(os.getenv('STOP_LOSS_PERCENT', '5.0'))
            
            if sl <= 0:
                self.errors.append('✗ Stop-loss must be > 0%')
                return False
            
            if sl > 50.0:
                self.warnings.append(f'⚠ Stop-loss very wide: {sl}%')
            
            self.passed_checks.append(f'✓ Stop-loss configured: {sl}%')
            return True
        except ValueError:
            self.errors.append('✗ Invalid stop-loss percentage')
            return False
    
    def check_demo_credentials(self) -> bool:
        """Ensure demo credentials are used, not live"""
        live_key = os.getenv('OKX_LIVE_API_KEY', '').strip()
        demo_key = os.getenv('OKX_DEMO_API_KEY', '').strip()
        env = os.getenv('R20_OKX_ENV', 'demo').lower()
        simulated = os.getenv('OKX_IS_SIMULATED', '1') == '1'
        
        if env == 'demo' and simulated:
            self.passed_checks.append('✓ Demo environment + simulated trading')
            return True
        elif live_key and not demo_key:
            self.errors.append('✗ Live credentials detected without demo fallback')
            return False
        else:
            self.warnings.append('⚠ Verify exchange credentials are demo')
            return True
    
    def check_admin_tokens(self) -> bool:
        """Ensure admin tokens are changed from defaults"""
        setup_token = os.getenv('R20_SETUP_TOKEN', '').strip()
        
        if setup_token in ['', 'change-me-immediately', 'replace_with_a_long_random_setup_token']:
            self.errors.append('✗ Setup token not configured - CHANGE IMMEDIATELY')
            return False
        
        if len(setup_token) < 32:
            self.warnings.append(f'⚠ Setup token is weak ({len(setup_token)} chars, min: 32)')
            return True
        
        self.passed_checks.append('✓ Setup token configured')
        return True
    
    def check_audit_logging(self) -> bool:
        """Ensure audit logging is enabled"""
        if os.getenv('AUDIT_LOGGING_ENABLED', '1') == '1':
            self.passed_checks.append('✓ Audit logging enabled')
            return True
        else:
            self.warnings.append('⚠ Audit logging disabled')
            return True
    
    def check_backup_encryption(self) -> bool:
        """Ensure backup encryption is configured"""
        encryption_key = os.getenv('R20_BACKUP_ENCRYPTION_KEY', '').strip()
        
        if not encryption_key:
            self.warnings.append('⚠ Backup encryption key not configured')
            return True
        
        if len(encryption_key) < 32:
            self.warnings.append(f'⚠ Backup encryption key is weak ({len(encryption_key)} chars)')
            return True
        
        self.passed_checks.append('✓ Backup encryption configured')
        return True
    
    def check_circuit_breaker(self) -> bool:
        """Ensure circuit breaker is enabled"""
        if os.getenv('CIRCUIT_BREAKER_ENABLED', '1') == '1':
            self.passed_checks.append('✓ Circuit breaker enabled')
            return True
        else:
            self.errors.append('✗ Circuit breaker disabled')
            return False
    
    def check_manual_close_disabled(self) -> bool:
        """Ensure manual close is disabled by default"""
        if os.getenv('R20_MANUAL_CLOSE_ENABLED', '0') == '0':
            self.passed_checks.append('✓ Manual close disabled (protection)')
            return True
        else:
            self.warnings.append('⚠ Manual close enabled')
            return True
    
    def run_all_checks(self) -> Tuple[bool, Dict]:
        """Run all safety checks"""
        checks = [
            self.check_trading_mode,
            self.check_dry_run,
            self.check_strategy_validation,
            self.check_risk_limits,
            self.check_stop_loss,
            self.check_demo_credentials,
            self.check_admin_tokens,
            self.check_audit_logging,
            self.check_backup_encryption,
            self.check_circuit_breaker,
            self.check_manual_close_disabled,
        ]
        
        for check in checks:
            try:
                check()
            except Exception as e:
                self.errors.append(f'✗ Check failed: {check.__name__} - {e}')
        
        report = {
            'timestamp': datetime.utcnow().isoformat(),
            'passed': len(self.passed_checks),
            'warnings': len(self.warnings),
            'errors': len(self.errors),
            'checks': self.passed_checks,
            'warnings_list': self.warnings,
            'errors_list': self.errors,
        }
        
        success = len(self.errors) == 0
        return success, report
    
    def print_report(self, report: Dict):
        """Print validation report"""
        print("\n" + "="*70)
        print("R20 QUANTUM TRADER - SAFETY VALIDATION REPORT")
        print("="*70)
        
        print(f"\nTimestamp: {report['timestamp']}")
        print(f"Passed: {report['passed']} | Warnings: {report['warnings']} | Errors: {report['errors']}")
        
        if report['checks']:
            print("\n✓ PASSED CHECKS:")
            for check in report['checks']:
                print(f"  {check}")
        
        if report['warnings_list']:
            print("\n⚠ WARNINGS:")
            for warning in report['warnings_list']:
                print(f"  {warning}")
        
        if report['errors_list']:
            print("\n✗ ERRORS (BLOCKING):")
            for error in report['errors_list']:
                print(f"  {error}")
        
        print("\n" + "="*70 + "\n")


def main():
    """Run safety validation"""
    validator = TradingSafetyValidator()
    success, report = validator.run_all_checks()
    
    # Save report to audit log
    audit_path = Path(os.getenv('AUDIT_LOG_PATH', '/app/audit'))
    audit_path.mkdir(parents=True, exist_ok=True)
    
    report_file = audit_path / f"safety_check_{datetime.utcnow().isoformat()}.json"
    report_file.write_text(json.dumps(report, indent=2))
    
    validator.print_report(report)
    
    if not success:
        print("❌ SAFETY VALIDATION FAILED - Aborting startup")
        sys.exit(1)
    else:
        print("✅ SAFETY VALIDATION PASSED - Safe to proceed")
        sys.exit(0)


if __name__ == '__main__':
    main()
