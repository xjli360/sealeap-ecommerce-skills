"""Synthetic contract and safe transport regressions; no live credentials or network."""
import copy
from datetime import date
import io
import hashlib
import json
import os
from pathlib import Path
import stat
import tempfile
import unittest
from mpstats_read import build_request, fetch_raw, NoRedirect, parse_json, validate_response, write_private, MAX_BYTES
from validate_data import check

FIXTURE = Path(__file__).resolve().parents[1]/"references/synthetic-data.json"
AS_OF = date(2026, 9, 27)


class FakeResponse(io.BytesIO):
    def __init__(self, body, status=200):
        super().__init__(body)
        self.status = status


class FakeOpener:
    def __init__(self, body=b"[]", status=200):
        self.body, self.status = body, status

    def open(self, request, timeout):
        return FakeResponse(self.body, self.status)


class DataTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(FIXTURE.read_text())

    def blocked(self, code):
        result = check(self.data, AS_OF)
        self.assertFalse(result["ok"])
        self.assertIn(code, result["errors"])
        self.assertNotIn("estimated_orders", result)

    def test_synthetic_totals_are_never_real_sales(self):
        result = check(self.data, AS_OF)
        self.assertEqual(result["status"], "VALID_SYNTHETIC")
        self.assertEqual(result["metric_kind"], "ESTIMATE")
        self.assertEqual(result["estimated_orders"], 9)
        self.assertEqual(result["estimated_order_value"], 900)
        self.assertEqual(result["population"], "sample")

    def test_real_declared_source_still_requires_review(self):
        self.data["evidence_kind"] = "mpstats_export"
        self.data["raw_sha256"] = hashlib.sha256(b"synthetic raw test bytes").hexdigest()
        self.assertEqual(check(self.data, AS_OF)["status"], "READY_FOR_REVIEW")

    def test_synthetic_hash_cannot_pass_as_real_export(self):
        self.data["evidence_kind"] = "mpstats_export"
        self.blocked("synthetic_hash_in_real_data")

    def test_wb_cannot_enter_ozon_analysis(self):
        self.data["marketplace"] = "wb"
        self.blocked("invalid_marketplace")

    def test_internal_actuals_cannot_mix_with_external(self):
        self.data["module"] = "internal"
        self.data["metric_kind"] = "actual_sales"
        self.blocked("invalid_module")

    def test_duplicate_sku_day_is_not_summed(self):
        self.data["rows"].append(copy.deepcopy(self.data["rows"][0]))
        self.data["coverage"]["row_count"] += 1
        self.blocked("duplicate_sku_day")

    def test_missing_day_is_not_zero(self):
        self.data["rows"].pop()
        self.data["coverage"]["row_count"] -= 1
        self.blocked("missing_sku_days")

    def test_mixed_currency_rejected(self):
        self.data["rows"][0]["currency"] = "CNY"
        self.blocked("mixed_currency")

    def test_unknown_unit_blocks_money_calculations(self):
        self.data["money_unit"] = "UNCONFIRMED"
        self.blocked("invalid_money_unit")

    def test_future_or_unfinished_window_rejected(self):
        self.data["period"]["end"] = "2026-09-27"
        self.blocked("invalid_or_unfinished_period")

    def test_stale_snapshot_is_not_current(self):
        self.data["collected_at"] = "2026-09-10T10:00:00+03:00"
        self.blocked("stale_capture")

    def test_collection_error_is_not_a_zero_sale(self):
        self.data["rows"][0]["no_data"] = True
        self.blocked("no_data_or_unknown_coverage")

    def test_unknown_boolean_and_negative_numbers_rejected(self):
        for value in (None, True, -1, float("inf"), 10**1000):
            with self.subTest(value_type=type(value).__name__):
                self.data["rows"][0]["sales"] = value
                self.blocked("invalid_sales")

    def test_page_coverage_must_be_explicit(self):
        self.data["coverage"]["pagination_complete"] = False
        self.blocked("incomplete_pagination")

    def test_row_outside_window(self):
        self.data["rows"][0]["date"] = "2026-09-20"
        self.blocked("row_outside_period")

    def test_invalid_timezone(self):
        self.data["timezone"] = "UNKNOWN"
        self.blocked("unknown_timezone")

    def test_duplicate_json_keys_and_nonfinite_numbers(self):
        for source in ('{"sales":1,"sales":2}', '{"sales":NaN}', '{"sales":Infinity}'):
            with self.subTest(source=source):
                with self.assertRaises(ValueError): parse_json(source)


class TransportTests(unittest.TestCase):
    def request(self, endpoint="period", token="synthetic-token"):
        return build_request(endpoint, "123456", "2026-09-01", "2026-09-03", False, token)

    def test_ozon_current_period_path_and_token_header_only(self):
        request = self.request()
        self.assertIn("/oz/items/123456/by_period?", request.full_url)
        self.assertNotIn("by/period", request.full_url)
        self.assertNotIn("synthetic-token", request.full_url)
        self.assertEqual(request.get_method(), "GET")
        self.assertIn("synthetic-token", dict(request.header_items()).values())

    def test_no_redirect_of_authenticated_request(self):
        self.assertIsNone(NoRedirect().redirect_request(self.request(), None, 302, "", {}, "https://global-help.ozon.com/"))

    def test_missing_credential_and_path_injection_rejected(self):
        with self.assertRaises(ValueError): self.request(token="")
        with self.assertRaises(ValueError):
            build_request("period", "../wb", "2026-09-01", "2026-09-03", False, "test")

    def test_pending_is_not_complete(self):
        result, data = fetch_raw(self.request(), "period", "123456", FakeOpener(b"{}", 202))
        self.assertEqual(result["status"], "HOLD")
        self.assertIsNone(data)

    def test_business_error_even_with_http_success(self):
        with self.assertRaises(ValueError):
            fetch_raw(self.request(), "period", "123456", FakeOpener(b'{"error":"denied"}'))

    def test_wrong_sku_rejected(self):
        with self.assertRaises(ValueError):
            validate_response({"id": "987654", "period_stats": {}}, "full", "123456")

    def test_oversize_response_does_not_write(self):
        result, data = fetch_raw(self.request(), "period", "123456", FakeOpener(b"x"*(MAX_BYTES+1)))
        self.assertEqual(result["reason"], "response_too_large")
        self.assertIsNone(data)

    def test_success_is_only_raw_capture(self):
        result, data = fetch_raw(self.request(), "period", "123456", FakeOpener(b'[{"data":"2026-09-01","sales":1}]'))
        self.assertEqual(result["status"], "RAW_CAPTURED")
        self.assertEqual(len(data), 1)

    def test_private_output_cannot_overwrite_existing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)/"data.json"
            write_private(target, {"synthetic": True})
            self.assertEqual(stat.S_IMODE(target.stat().st_mode), 0o600)
            with self.assertRaises(FileExistsError): write_private(target, {})
            self.assertEqual(json.loads(target.read_text()), {"synthetic": True})


if __name__ == "__main__":
    unittest.main()
