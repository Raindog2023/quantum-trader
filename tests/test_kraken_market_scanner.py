import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

SPEC = importlib.util.spec_from_file_location(
    "scanner", Path(__file__).resolve().parents[1] / "scripts" / "kraken_market_scanner.py")
scanner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(scanner)
TICKER = {"c": ["110"], "o": "100", "a": ["111"], "b": ["109"],
          "v": ["1", "20"], "p": ["100", "105"]}
PAIR = {"quote": "ZUSD", "status": "online", "wsname": "XBT/USD"}


class ScannerTests(unittest.TestCase):
    def test_closed_candles_ignore_live(self):
        rows = [[i * 3600, 0, 0, 0, 100 + i, 0, 10, 1] for i in range(26)]
        rows[-1][4] = 999999
        result = scanner.candle_metrics({"PAIR": rows, "last": 0})
        self.assertAlmostEqual(result["closed_return_24h_pct"], 24)
        self.assertEqual(result["closed_candle_count"], 25)

    def test_scope_and_missing_ticker_coverage(self):
        def fetch(endpoint, **kwargs):
            if endpoint == "AssetPairs":
                return {"A": PAIR, "B": PAIR, "C": dict(PAIR, quote="ZEUR"),
                        "D": dict(PAIR, status="cancel_only")}
            return {"A": TICKER}
        report = scanner.scan(top_n=0, fetch=fetch)
        self.assertEqual(report["coverage"]["discovered"], 4)
        self.assertEqual(report["coverage"]["eligible"], 2)
        self.assertEqual(report["coverage"]["scored"], 1)
        self.assertEqual(report["coverage"]["failed"], 1)
        self.assertEqual(report["status"], "partial")
        self.assertEqual(len(report["excluded"]), 2)

    def test_failed_ohlc_retained(self):
        def fetch(endpoint, **kwargs):
            if endpoint == "AssetPairs":
                return {"A": PAIR}
            if endpoint == "Ticker":
                return {"A": TICKER}
            raise TimeoutError("mock timeout")
        report = scanner.scan(fetch=fetch)
        self.assertEqual(report["coverage"]["ohlc_failed"], 1)
        self.assertIn("ohlc_error", report["ranked_candidates"][0])

    def test_fatal_discovery(self):
        report = scanner.scan(fetch=lambda *a, **k: (_ for _ in ()).throw(ValueError("offline")))
        self.assertEqual(report["status"], "failed")
        self.assertEqual(report["coverage"]["scored"], 0)

    def test_ticker_units(self):
        result = scanner.ticker_metrics(TICKER)
        self.assertAlmostEqual(result["return_since_utc_open_pct"], 10)
        self.assertEqual(result["turnover_24h_usd"], 2100)
        self.assertAlmostEqual(result["spread_pct"], 100 * 2 / 110)

    def test_limits_and_no_private_endpoint(self):
        for kwargs in ({"workers": 4}, {"top_n": 201}, {"top_n": -1}):
            with self.assertRaises(ValueError):
                scanner.scan(**kwargs)
        with self.assertRaises(ValueError):
            scanner.public_get("AddOrder")

    def test_rate_limit_retry_bounded(self):
        with patch.object(scanner, "urlopen", side_effect=HTTPError(
                "mock", 429, "rate limit", {}, None)) as opening:
            with patch.object(scanner.time, "sleep"):
                with self.assertRaises(HTTPError):
                    scanner.public_get("Ticker")
        self.assertEqual(opening.call_count, 3)

    def test_atomic_report(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "scan.json"
            scanner.atomic_write(target, {"research_only": True})
            self.assertEqual(scanner.json.loads(target.read_text()), {"research_only": True})
            self.assertEqual(len(list(Path(directory).iterdir())), 1)


if __name__ == "__main__":
    unittest.main()
