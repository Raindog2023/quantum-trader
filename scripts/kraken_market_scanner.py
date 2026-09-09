"""Public Kraken spot market research. Never authenticates or submits orders."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import tempfile
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

BASE = "https://api.kraken.com/0/public/"
ALLOWED = {"AssetPairs", "Ticker", "OHLC"}


def public_get(endpoint, **params):
    if endpoint not in ALLOWED:
        raise ValueError("Only public market-data endpoints are allowed")
    url = BASE + endpoint + ("?" + urlencode(params) if params else "")
    for attempt in range(3):
        try:
            with urlopen(url, timeout=12) as response:
                payload = json.load(response)
            errors = payload.get("error", [])
            if errors:
                message = "; ".join(errors)
                if "rate limit" in message.lower() and attempt < 2:
                    time.sleep(2 ** attempt)
                    continue
                raise ValueError(message)
            return payload["result"]
        except (HTTPError, URLError, TimeoutError) as exc:
            if isinstance(exc, HTTPError) and exc.code not in (429, 500, 502, 503, 504):
                raise
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)


def number(value, positive=False):
    value = float(value)
    if not math.isfinite(value) or value < 0 or (positive and value == 0):
        raise ValueError("Invalid market numeric value")
    return value


def ticker_metrics(ticker):
    close = number(ticker["c"][0], True)
    opening = number(ticker["o"], True)
    ask, bid = number(ticker["a"][0], True), number(ticker["b"][0], True)
    if ask < bid:
        raise ValueError("Crossed quote")
    return {
        "last_price_usd": close,
        "return_since_utc_open_pct": 100 * (close / opening - 1),
        "volume_24h_base": number(ticker["v"][1]),
        "turnover_24h_usd": number(ticker["v"][1]) * number(ticker["p"][1]),
        "spread_pct": 100 * (ask - bid) / ((ask + bid) / 2),
    }


def candle_metrics(result):
    series = [value for key, value in result.items() if key != "last"]
    if len(series) != 1:
        raise ValueError("Expected one OHLC series")
    closed = series[0][:-1]  # Kraken's final row is always unfinished.
    if len(closed) < 2:
        raise ValueError("Insufficient closed candles")
    times = [int(row[0]) for row in closed]
    if any(b <= a for a, b in zip(times, times[1:])):
        raise ValueError("Unordered candles")
    latest = number(closed[-1][4], True)
    metrics = {"last_closed_candle_utc": datetime.fromtimestamp(
        times[-1], timezone.utc).isoformat(), "closed_candle_count": len(closed)}
    for hours in (1, 4, 24):
        target = times[-1] - hours * 3600
        reference = next((row for row in reversed(closed) if int(row[0]) == target), None)
        metrics["closed_return_" + str(hours) + "h_pct"] = (
            100 * (latest / number(reference[4], True) - 1) if reference else None)
    prior = [number(row[6]) for row in closed[-25:-1]]
    average = sum(prior) / len(prior)
    metrics["last_hour_volume_vs_prior_mean"] = number(closed[-1][6]) / average if average else None
    return metrics


def scan(top_n=20, workers=3, fetch=public_get):
    if not 0 <= top_n <= 200 or not 1 <= workers <= 3:
        raise ValueError("top_n must be 0..200; workers must be 1..3")
    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "research_only": True, "source": "Kraken public spot REST",
        "scope": "Online USD-quoted pairs; no account/regional eligibility verification",
        "ranking": "Descending return since midnight UTC; turnover breaks ties",
        "coverage": {"discovered": 0, "eligible": 0, "scored": 0, "failed": 0,
                     "ohlc_requested": 0, "ohlc_scored": 0, "ohlc_failed": 0},
        "excluded": [], "errors": [], "ranked_candidates": [],
    }
    coverage = report["coverage"]
    try:
        pairs = fetch("AssetPairs")
    except Exception as exc:
        report["errors"].append({"stage": "discovery", "error": str(exc)})
        report["status"] = "failed"
        return report
    coverage["discovered"] = len(pairs)
    eligible = {}
    for key, pair in pairs.items():
        reason = None
        if pair.get("quote") not in ("ZUSD", "USD"):
            reason = "not_USD_quoted"
        elif pair.get("status") != "online":
            reason = "not_online"
        elif key.endswith(".d"):
            reason = "dark_pool"
        elif pair.get("aclass_base") not in (None, "currency"):
            reason = "non_currency_asset_class"
        if reason:
            report["excluded"].append({"pair": key, "reason": reason})
        else:
            eligible[key] = pair
    coverage["eligible"] = len(eligible)
    try:
        tickers = fetch("Ticker")
    except Exception as exc:
        report["errors"].append({"stage": "ticker", "error": str(exc)})
        coverage["failed"] = len(eligible)
        report["status"] = "failed"
        return report
    ranked = report["ranked_candidates"]
    for key, pair in eligible.items():
        try:
            ticker = tickers.get(key, tickers.get(pair.get("altname")))
            ranked.append({"pair": key, "symbol": pair.get("wsname", key),
                           **ticker_metrics(ticker)})
        except Exception as exc:
            report["errors"].append({"stage": "ticker", "pair": key, "error": str(exc)})
            coverage["failed"] += 1
    ranked.sort(key=lambda row: (row["return_since_utc_open_pct"],
                                 row["turnover_24h_usd"]), reverse=True)
    coverage["scored"] = len(ranked)
    selected = ranked[:top_n]
    coverage["ohlc_requested"] = len(selected)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        jobs = {pool.submit(fetch, "OHLC", pair=row["pair"], interval=60): row
                for row in selected}
        for future in as_completed(jobs):
            row = jobs[future]
            try:
                row["ohlc"] = candle_metrics(future.result())
                coverage["ohlc_scored"] += 1
            except Exception as exc:
                row["ohlc_error"] = str(exc)
                report["errors"].append({"stage": "ohlc", "pair": row["pair"], "error": str(exc)})
                coverage["ohlc_failed"] += 1
    report["status"] = "partial" if report["errors"] else "complete"
    return report


def atomic_write(path, report):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         delete=False, suffix=".tmp") as handle:
            temporary = handle.name
            json.dump(report, handle, indent=2, allow_nan=False)
            handle.write("\n")
        os.replace(temporary, path)
    finally:
        if temporary and os.path.exists(temporary):
            os.unlink(temporary)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--top-n", type=int, default=20)
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--output", default="data/kraken_market_scan.json")
    args = parser.parse_args()
    report = scan(args.top_n, args.workers)
    atomic_write(args.output, report)
    print(json.dumps({"status": report["status"], "coverage": report["coverage"],
                      "output": args.output}))
    return 1 if report["status"] == "failed" else 0


if __name__ == "__main__":
    raise SystemExit(main())
