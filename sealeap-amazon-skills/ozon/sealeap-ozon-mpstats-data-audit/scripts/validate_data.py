#!/usr/bin/env python3
"""Validate a mapped external MPstats OZON SKU/day dataset, not its authenticity."""
import argparse
from datetime import date, datetime, timedelta
import json
import math
from pathlib import Path
import re
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from mpstats_read import parse_json


def check(document, as_of, max_age_days=7):
    errors = []
    def require(ok, code):
        if not ok:
            errors.append(code)
    if not isinstance(document, dict):
        return {"ok": False, "status": "HOLD", "errors": ["not_an_object"]}
    require(type(max_age_days) is int and max_age_days >= 0, "invalid_freshness_limit")
    for field, expected in {"schema_version": 1, "provider": "mpstats", "marketplace": "ozon",
                            "module": "external", "report": "sku_daily",
                            "metric_kind": "estimated_orders", "money_unit": "major"}.items():
        require(document.get(field) == expected, "invalid_" + field)
    require(document.get("fulfillment") in ("FBO", "FBO+FBS"), "unknown_fulfillment")
    require(bool(re.fullmatch(r"[A-Z]{3}", str(document.get("currency", "")))), "invalid_currency")
    try:
        report_zone = ZoneInfo(document.get("timezone", ""))
    except (ZoneInfoNotFoundError, ValueError, TypeError):
        return {"ok": False, "status": "HOLD", "errors": errors+["unknown_timezone"]}
    require(document.get("evidence_kind") in ("synthetic", "mpstats_export", "mpstats_api", "mpstats_mcp"), "unknown_evidence_kind")
    require(bool(re.fullmatch(r"[a-f0-9]{64}", str(document.get("raw_sha256", "")))), "missing_raw_hash")
    if document.get("evidence_kind") != "synthetic":
        require(document.get("raw_sha256") != "0"*64, "synthetic_hash_in_real_data")
    require(bool(document.get("unit_evidence")), "missing_unit_evidence")
    mapping = document.get("field_mapping", {})
    require(isinstance(mapping, dict) and all(mapping.get(k) for k in ("sku", "date", "sales", "revenue", "stock")), "missing_field_mapping")
    try:
        first = date.fromisoformat(document["period"]["start"])
        last = date.fromisoformat(document["period"]["end"])
        capture = datetime.fromisoformat(document["collected_at"].replace("Z", "+00:00"))
        require(capture.tzinfo is not None, "capture_timezone_required")
        local_capture_day = capture.astimezone(report_zone).date() if capture.tzinfo else capture.date()
        require(first <= last < local_capture_day <= as_of, "invalid_or_unfinished_period")
        require((last-first).days <= 365, "period_too_large")
        require((as_of-capture.date()).days <= max_age_days, "stale_capture")
        dates = {first+timedelta(days=i) for i in range(max(0, min(366, (last-first).days+1)))}
    except (KeyError, TypeError, ValueError, AttributeError):
        return {"ok": False, "status": "HOLD", "errors": errors+["invalid_dates"]}
    rows = document.get("rows")
    if not isinstance(rows, list) or not rows:
        return {"ok": False, "status": "HOLD", "errors": errors+["missing_rows"]}
    coverage = document.get("coverage", {})
    if not isinstance(coverage, dict):
        coverage = {}
    require(coverage.get("pagination_complete") is True, "incomplete_pagination")
    require(coverage.get("row_count") == len(rows), "row_count_mismatch")
    require(coverage.get("population") in ("sample", "full_declared_scope"), "unknown_population")
    require(bool(coverage.get("selection")), "missing_selection")
    seen, by_sku = set(), {}
    sales_total, revenue_total = 0, 0.0
    for row in rows:
        if not isinstance(row, dict):
            errors.append("invalid_row"); continue
        sku = row.get("sku")
        require(isinstance(sku, str) and bool(sku.strip()), "invalid_sku")
        if not isinstance(sku, str):
            continue
        try:
            day = date.fromisoformat(row["date"])
        except (KeyError, ValueError, TypeError):
            errors.append("invalid_row_date"); continue
        require(day in dates, "row_outside_period")
        key = (sku, day)
        require(key not in seen, "duplicate_sku_day")
        seen.add(key); by_sku.setdefault(sku, set()).add(day)
        require(row.get("no_data") is False, "no_data_or_unknown_coverage")
        require(row.get("currency", document.get("currency")) == document.get("currency"), "mixed_currency")
        for field in ("sales", "revenue", "stock"):
            value = row.get(field)
            try:
                good = type(value) in (int, float) and math.isfinite(value) and value >= 0
            except OverflowError:
                good = False
            if field in ("sales", "stock") and good:
                good = float(value).is_integer()
            require(good, "invalid_"+field)
            if good and field == "sales": sales_total += value
            if good and field == "revenue": revenue_total += value
    require(all(value == dates for value in by_sku.values()) and bool(by_sku), "missing_sku_days")
    result = {"ok": not errors, "status": "HOLD" if errors else "VALID_SYNTHETIC" if document.get("evidence_kind") == "synthetic" else "READY_FOR_REVIEW",
              "errors": sorted(set(errors)), "metric_kind": "ESTIMATE", "population": coverage.get("population"),
              "boundary": "Checks structure and declared scope only; no authentication, source authenticity, or business outcome proof."}
    if not errors:
        result.update(estimated_orders=sales_total, estimated_order_value=revenue_total, currency=document["currency"], skus=len(by_sku))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path)
    parser.add_argument("--as-of", type=date.fromisoformat, default=date.today())
    parser.add_argument("--max-age-days", type=int, default=7)
    args = parser.parse_args()
    try:
        result = check(parse_json(args.file.read_text()), args.as_of, args.max_age_days)
    except (OSError, ValueError, TypeError):
        result = {"ok": False, "status": "HOLD", "errors": ["invalid_json_or_file"]}
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
