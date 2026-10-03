"""Perplexity (`pplx`) web-news supplement and English black-swan patterns."""
from __future__ import annotations
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import news_sentiment_harvester as harvester  # noqa: E402

FAKE_HITS = {
    "total": 2,
    "hits": [
        {"url": "https://example.com/a", "title": "Bitcoin news", "domain": "example.com",
         "snippet": "Bitcoin reaches for $87K as short liquidations top $120M", "date": "2026-10-02"},
        {"url": "https://example.com/b", "title": "Exchange update", "domain": "example.com",
         "snippet": "Binance halts all withdrawals amid bank run fears", "last_updated": "2026-10-02"},
        {"url": "https://example.com/a", "title": "dup", "snippet": "dup"},
    ],
}


class WebNewsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        fake = Path(self.temp.name) / "pplx"
        fake.write_text(f"#!/bin/sh\ncat <<'EOF'\n{json.dumps(FAKE_HITS)}\nEOF\n")
        fake.chmod(fake.stat().st_mode | stat.S_IEXEC)
        self.path = f"{self.temp.name}{os.pathsep}{os.environ.get('PATH', '')}"

    def tearDown(self):
        self.temp.cleanup()

    def test_fetch_web_news_parses_dedupes_and_flags(self):
        with patch.dict(os.environ, {"PATH": self.path, "R20_PPLX_NEWS": "1"}), \
                patch.object(harvester, "_HARVEST_START", harvester.time.time()):
            items = harvester.fetch_web_news(["BTC", "ETH"])
        self.assertEqual([i["url"] for i in items], ["https://example.com/a", "https://example.com/b"])
        self.assertTrue(all(i["source"] == "pplx" for i in items))
        self.assertIsNone(items[0]["alert"])
        self.assertEqual(items[1]["alert"], "主流中心化交易所崩盘挤兑")

    def test_disabled_by_env(self):
        with patch.dict(os.environ, {"PATH": self.path, "R20_PPLX_NEWS": "0"}):
            self.assertEqual(harvester.fetch_web_news(["BTC"]), [])

    def test_missing_cli_returns_empty(self):
        with patch.dict(os.environ, {"PATH": "/nonexistent", "R20_PPLX_NEWS": "1"}):
            self.assertEqual(harvester.fetch_web_news(["BTC"]), [])

    def test_english_black_swan_patterns(self):
        self.assertEqual(harvester.match_black_swan("USDT depegged sharply overnight"), "头部稳定币恶性脱锚危机")
        self.assertEqual(harvester.match_black_swan("Solana network halted for hours"), "顶级底层公链系统性故障/51%攻击")
        self.assertIsNone(harvester.match_black_swan("Bitcoin ETFs draw $6.3B in Q3"))
        self.assertIsNone(harvester.match_black_swan("Bitget pauses withdrawals after hack"))


if __name__ == "__main__":
    unittest.main()
