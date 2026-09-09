"""Offline safety tests: no exchange calls, credentials, or scheduler startup."""
import ast
import importlib.util
import json
import os
from pathlib import Path
import unittest
from unittest.mock import MagicMock, patch
from urllib.error import URLError

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("observer", ROOT / "scripts/kraken_observer.py")
observer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(observer)

def health():
    return {"status": "ok", "autonomous_enabled": True, "live_trading": True,
            "paused": False, "kraken_configured": True,
            "autonomous": {"scan_in_progress": False,
                           "last_scan": {"status": "hold", "submitted": False,
                                         "detail": "SECRET", "rationale": "SECRET"}}}

class ObserverTests(unittest.TestCase):
    def opener(self, data):
        client = MagicMock()
        response = client.open.return_value.__enter__.return_value
        response.status = 200
        response.read.return_value = data
        return client

    def test_only_get_health_and_sanitized(self):
        client = self.opener(json.dumps(health()).encode())
        result, rc = observer.observe("http://localhost:8000", client)
        request = client.open.call_args.args[0]
        self.assertEqual(request.get_method(), "GET")
        self.assertEqual(request.full_url, "http://localhost:8000/health")
        self.assertIsNone(request.data)
        self.assertEqual(client.open.call_args.kwargs["timeout"], 10)
        self.assertNotIn("SECRET", json.dumps(result))
        self.assertEqual(rc, 0)
        client.open.assert_called_once()

    def test_bad_urls(self):
        for url in ("", "file:///etc/passwd", "http://u:p@localhost",
                    "http://localhost/auto", "http://localhost?key=secret"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                observer.health_url(url)

    def test_bad_schema(self):
        for data in ([], {}, {"status": "bad"}, {**health(), "paused": "false"}):
            with self.subTest(data=data), self.assertRaises(ValueError):
                observer.summarize(data)

    def test_scan_failure_not_success(self):
        data = health()
        data["autonomous"]["last_scan"]["status"] = "error"
        self.assertEqual(observer.summarize(data)[1], 1)
        data["autonomous"]["last_scan"] = {}
        with self.assertRaises(ValueError):
            observer.summarize(data)

    def test_malformed_json(self):
        with self.assertRaises(ValueError):
            observer.observe("http://localhost", self.opener(b"{broken"))

    def test_oversize(self):
        with self.assertRaises(ValueError):
            observer.observe("http://localhost", self.opener(b"x" * (observer.MAX_BYTES + 1)))

    def test_network_failure_main_nonzero(self):
        with patch.object(observer, "observe", side_effect=URLError("SECRET")), patch("builtins.print") as out:
            self.assertEqual(observer.main(), 1)
            self.assertNotIn("SECRET", str(out.call_args))

    def test_no_redirect(self):
        self.assertIsNone(observer.NoRedirect().redirect_request(None, None, 302, "", {}, "http://other/auto"))

    def test_execution_never_falls_back(self):
        import subprocess
        import sys
        from types import SimpleNamespace
        for relative, method in (("r20_gateway/scheduler.py", "_execute"),
                                 ("r20_backend/scheduler.py", "run_script")):
            tree = ast.parse((ROOT / relative).read_text(encoding="utf-8"))
            nodes = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
                     and n.name in {"trader_script", method}]
            ns = {"os": os, "sys": sys, "subprocess": MagicMock(),
                  "ROOT": ROOT, "SCRIPTS": ROOT / "scripts",
                  "JobSpec": object, "logging": MagicMock(),
                  "JOBS": {"trader": ("ai_factor_trader.py", 900)}}
            ns["subprocess"].TimeoutExpired = subprocess.TimeoutExpired
            ns["subprocess"].run.return_value = SimpleNamespace(returncode=0, stdout="ok", stderr="")
            exec(compile(ast.Module(body=nodes, type_ignores=[]), relative, "exec"), ns)
            store = MagicMock()
            def execute():
                if method == "_execute":
                    ns[method](SimpleNamespace(store=store), SimpleNamespace(
                        name="trader", script="ai_factor_trader.py", schedule_key="", timeout_seconds=600))
                else:
                    ns[method]("trader")
            with patch.dict(os.environ, {"R20_TRADER_BACKEND": "kraken_observer"}):
                execute()
            self.assertTrue(str(ns["subprocess"].run.call_args.args[0][1]).endswith("kraken_observer.py"))
            ns["subprocess"].run.reset_mock()
            with patch.dict(os.environ, {"R20_TRADER_BACKEND": "bad"}):
                if method == "_execute":
                    execute()
                    self.assertEqual(store.finish_job.call_args.args[1], 1)
                else:
                    with self.assertRaises(ValueError):
                        execute()
            ns["subprocess"].run.assert_not_called()

    def test_scheduler_dispatch_offline(self):
        # Isolate dispatch AST, avoiding scheduler startup and database imports.
        for relative in ("r20_gateway/scheduler.py", "r20_backend/scheduler.py"):
            tree = ast.parse((ROOT / relative).read_text(encoding="utf-8"))
            function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "trader_script")
            ns = {"os": os}
            exec(compile(ast.Module(body=[function], type_ignores=[]), relative, "exec"), ns)
            with patch.dict(os.environ, {}, clear=True):
                self.assertEqual(ns["trader_script"](), "ai_factor_trader.py")
            with patch.dict(os.environ, {"R20_TRADER_BACKEND": "kraken_observer"}):
                self.assertEqual(ns["trader_script"](), "kraken_observer.py")
            with patch.dict(os.environ, {"R20_TRADER_BACKEND": "bad"}):
                with self.assertRaises(ValueError):
                    ns["trader_script"]()
            text = ast.unparse(tree)
            self.assertIn("trader_script()", text)
            self.assertIn("R20_MARKET_SCANNER_ENABLED", text)
            self.assertIn("kraken_market_scanner.py", text)

if __name__ == "__main__":
    unittest.main()
