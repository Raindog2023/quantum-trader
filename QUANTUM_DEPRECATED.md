# QUANTUM BOT — DEPRECATED for Texas live use

R20 Quantum Trader is OKX-only. OKX is not legal in Texas/US, and the full
exchange swap (651 refs, ~70 files) is not worth it against Freqtrade.

Status:
- Live OKX trading: BLOCKED (Texas guard returns 403, `r20_backend/texas_guard.py`).
- Paper/backtest: still boots (`TRADING_MODE=backtest`, `DRY_RUN=1`).
- Active development: MOVED to Texas Freqtrade bot (Kraken spot, paper-first).

Do not point this at OKX live keys. Do not deploy except paper.
Kept for research (kraken_observer / kraken_market_scanner read-only scripts).
