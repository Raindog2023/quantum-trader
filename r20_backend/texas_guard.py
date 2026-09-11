"""Texas/US jurisdiction guard: OKX is not legal in Texas/US.

Enforces paper-only for banned venues. Allowed live spot venues:
kraken, coinbase. Everything else (okx, binance, bybit, futures)
is forced to paper/backtest.
"""
from __future__ import annotations

import os

ALLOWED_LIVE = {"kraken", "coinbase", "coinbaseexchange"}
BANNED = {"okx", "binance", "bybit", "krakenfutures", "bitget", "pionex"}


def allowlist() -> set[str]:
    raw = os.getenv("EXCHANGE_ALLOWLIST", "kraken,coinbase")
    return {x.strip().lower() for x in raw.split(",") if x.strip()}


def is_live_allowed(exchange: str) -> bool:
    ex = (exchange or "").strip().lower()
    if ex in BANNED:
        return False
    return ex in allowlist() and ex in ALLOWED_LIVE


def assert_texas_legal_live(exchange: str) -> None:
    """Raise RuntimeError if live trading is requested on a banned venue."""
    if not is_live_allowed(exchange):
        raise RuntimeError(
            f"Live trading blocked in Texas/US for venue '{exchange}'. "
            f"Allowed: {sorted(ALLOWED_LIVE)}. Use paper/backtest."
        )
