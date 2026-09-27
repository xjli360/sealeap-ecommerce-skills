#!/usr/bin/env python3
"""Bounded, read-only OZON API probe. A captured response is not validated data."""
import argparse
from datetime import date, datetime, timezone
import json
import os
from pathlib import Path
import re
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://mpstats.io/api/analytics/v1/oz"
ENDPOINTS = {"full": "full", "period": "by_period", "keywords": "keywords"}
MAX_BYTES = 5 * 1024 * 1024


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def parse_json(text):
    def invalid_number(_):
        raise ValueError("non-finite JSON number")
    return json.loads(text, object_pairs_hook=unique_object, parse_constant=invalid_number)


def build_request(endpoint, sku, start, end, fbs, token):
    if endpoint not in ENDPOINTS or not re.fullmatch(r"[1-9][0-9]{0,19}", str(sku)):
        raise ValueError("unsupported endpoint or SKU")
    first, last = date.fromisoformat(start), date.fromisoformat(end)
    if first > last or (last-first).days > 365 or last >= date.today():
        raise ValueError("use an ordered, completed period of at most 366 days")
    if type(fbs) is not bool or not token or any(c in token for c in "\r\n"):
        raise ValueError("invalid FBS choice or missing credential")
    query = urllib.parse.urlencode({"d1": start, "d2": end, "fbs": int(fbs)})
    url = f"{BASE}/items/{sku}/{ENDPOINTS[endpoint]}?{query}"
    return urllib.request.Request(url, headers={
        "X-Mpstats-TOKEN": token, "Accept": "application/json"
    }, method="GET")


def validate_response(data, endpoint, sku):
    if not isinstance(data, (dict, list)) or not data:
        raise ValueError("empty or unexpected response")
    if isinstance(data, dict):
        if any(data.get(k) not in (None, False, "", [], {}) for k in ("error", "errors")):
            raise ValueError("business error")
        if data.get("success") is False or data.get("status") in ("error", "failed", "pending"):
            raise ValueError("business status is not complete")
        if "code" in data and data["code"] not in (0, "0", 200, "200", "OK", "ok"):
            raise ValueError("unrecognized business code")
    if endpoint == "full":
        if not isinstance(data, dict) or str(data.get("id")) != str(sku):
            raise ValueError("SKU mismatch")
        if not isinstance(data.get("period_stats"), dict):
            raise ValueError("missing period statistics")
    elif not isinstance(data, list) or not all(isinstance(row, dict) for row in data):
        raise ValueError("expected row array")


def fetch_raw(request, endpoint, sku, opener=None):
    opener = opener or urllib.request.build_opener(NoRedirect())
    with opener.open(request, timeout=30) as response:
        status = response.status
        if status != 200:
            return {"status": "HOLD", "http_status": status}, None
        body = response.read(MAX_BYTES + 1)
        if len(body) > MAX_BYTES:
            return {"status": "HOLD", "reason": "response_too_large"}, None
        data = parse_json(body.decode("utf-8"))
        validate_response(data, endpoint, sku)
        return {"status": "RAW_CAPTURED", "http_status": 200}, data


def write_private(path, envelope):
    # Exclusive creation prevents overwriting source files or following a symlink.
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        json.dump(envelope, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--endpoint", required=True, choices=ENDPOINTS)
    parser.add_argument("--sku", required=True)
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    parser.add_argument("--fbs", required=True, choices=["include", "exclude"])
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    try:
        request = build_request(args.endpoint, args.sku, args.start, args.end,
                                args.fbs == "include", os.environ.get("MPSTATS_TOKEN", ""))
        receipt, data = fetch_raw(request, args.endpoint, args.sku)
        if data is not None:
            envelope = {
                "provider": "mpstats", "marketplace": "ozon", "module": "external",
                "endpoint": ENDPOINTS[args.endpoint], "sku": args.sku,
                "requested_period": {"start": args.start, "end": args.end},
                "fulfillment": "FBO+FBS" if args.fbs == "include" else "FBO",
                "collected_at": datetime.now(timezone.utc).isoformat(),
                "status": "RAW_CAPTURED", "currency": "UNCONFIRMED",
                "money_unit": "UNCONFIRMED", "data": data,
                "boundary": "Requested dates do not prove returned coverage or units. Validate before analysis."
            }
            write_private(args.out, envelope)
            receipt["requires_data_validation"] = True
        print(json.dumps(receipt))
        return 0 if data is not None else 2
    except urllib.error.HTTPError as exc:
        print(json.dumps({"status": "HOLD", "http_status": exc.code,
                          "reason": "no_retry_no_body_logged"}))
    except (ValueError, OSError, UnicodeError, urllib.error.URLError):
        # Never print raw exception text: it could contain credentials or response bodies.
        print(json.dumps({"status": "HOLD", "reason": "request_or_response_failed_validation"}))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
