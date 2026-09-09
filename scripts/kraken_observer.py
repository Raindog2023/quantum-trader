"""Observe Kraken health only. This module cannot submit or trigger trades."""
import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

MAX_BYTES = 262144
BOOL_FIELDS = ("autonomous_enabled", "live_trading", "paused", "kraken_configured")
SCAN_STATUSES = {"hold", "skipped", "error", "submitted", "order_ready", "dry_run",
                 "low_confidence", "paused", "insufficient_funds", "insufficient_position"}

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

def health_url(base):
    parts = urlsplit(base)
    if (parts.scheme not in {"http", "https"} or not parts.hostname
            or parts.username is not None or parts.password is not None
            or parts.query or parts.fragment or parts.path not in {"", "/"}):
        raise ValueError("invalid_endpoint")
    return base.rstrip("/") + "/health"

def summarize(data):
    if not isinstance(data, dict) or data.get("status") != "ok":
        raise ValueError("unhealthy_response")
    if any(type(data.get(key)) is not bool for key in BOOL_FIELDS):
        raise ValueError("invalid_health_schema")
    auto = data.get("autonomous")
    if not isinstance(auto, dict) or type(auto.get("scan_in_progress")) is not bool:
        raise ValueError("invalid_autonomous_schema")
    scan = auto.get("last_scan")
    if not isinstance(scan, dict):
        raise ValueError("missing_scan")
    status = scan.get("status")
    if status not in SCAN_STATUSES:
        raise ValueError("unknown_scan_status")
    result = {"mode": "observation_only", "health": "ok",
              **{key: data[key] for key in BOOL_FIELDS},
              "scan_in_progress": auto["scan_in_progress"],
              "last_scan_status": status}
    if type(scan.get("submitted")) is bool:
        result["last_scan_submitted"] = scan["submitted"]
    # Never emit rationale, exception detail, URL, headers or exchange responses.
    return result, 1 if status == "error" or not data["kraken_configured"] else 0

def observe(base, opener=None):
    request = Request(health_url(base), method="GET", headers={"Accept": "application/json"})
    client = opener or build_opener(ProxyHandler({}), NoRedirect())
    with client.open(request, timeout=10) as response:
        if response.status != 200:
            raise ValueError("unexpected_http_status")
        raw = response.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError("response_too_large")
    return summarize(json.loads(raw))

def main():
    try:
        result, code = observe(os.environ.get("KRAKEN_BOT_URL", ""))
    except (ValueError, TypeError, HTTPError, URLError, OSError):
        result, code = {"mode": "observation_only", "health": "unavailable"}, 1
    print(json.dumps(result, sort_keys=True))
    return code

if __name__ == "__main__":
    sys.exit(main())
