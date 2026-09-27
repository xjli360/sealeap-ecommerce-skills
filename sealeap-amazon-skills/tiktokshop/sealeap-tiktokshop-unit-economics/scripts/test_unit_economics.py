"""Financial identities, conservative ceilings and invalid-input regressions."""
import copy
from decimal import Decimal
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unit_economics import ad_cap, calculate, parse_json

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT/"references/example-scenario.json"
SCRIPT = ROOT/"scripts/unit_economics.py"


class EconomicsTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(EXAMPLE.read_text())

    def test_hand_calculated_income_cost_and_contribution_bridge(self):
        result = calculate(self.data)
        self.assertEqual(result["unit"]["seller_revenue_after_refunds"], "38.00")
        self.assertEqual(result["unit"]["noncommission_variable_costs"], "18.00")
        self.assertEqual(result["summary"]["seller_revenue_after_refunds"], "3800.00")
        self.assertEqual(result["summary"]["contribution"], "1092.00")
        self.assertEqual(result["summary"]["contribution_per_order"], "10.92")
        self.assertEqual(result["summary"]["decision"], "TARGET_MET")

    def test_standard_and_ads_commissions_are_not_stacked(self):
        result = calculate(self.data)
        self.assertEqual(result["cohorts"][0]["commission"], "324.00")
        self.assertEqual(result["cohorts"][1]["commission"], "144.00")
        self.assertEqual(result["summary"]["commission"], "468.00")

    def test_independent_post_refund_commission_base_is_used(self):
        self.data["cohorts"][0]["unit_commission_base"] = "20"
        self.assertEqual(calculate(self.data)["cohorts"][0]["commission"], "180.00")

    def test_effective_standard_fallback_can_be_supplied_for_ads(self):
        self.data["cohorts"][1]["commission_rate"] = "0.15"
        result = calculate(self.data)
        self.assertEqual(result["cohorts"][1]["commission"], "216.00")
        self.assertEqual(result["summary"]["contribution"], "1020.00")

    def test_samples_and_production_are_allocated_by_orders(self):
        result = calculate(self.data)
        self.assertEqual(result["cohorts"][0]["allocated_campaign_costs"], "120.00")
        self.assertEqual(result["cohorts"][1]["allocated_campaign_costs"], "80.00")
        changed = copy.deepcopy(self.data)
        changed["campaign_costs"]["samples"] = "160"
        self.assertEqual(calculate(changed)["summary"]["contribution"], "992.00")

    def test_lower_volume_increases_fixed_cost_per_order(self):
        self.data["cohorts"][0]["orders"] = 30
        self.data["cohorts"][1]["orders"] = 20
        self.assertEqual(calculate(self.data)["unit"]["allocated_campaign_costs"], "4.00")

    def test_target_and_break_even_commission_caps(self):
        result = calculate(self.data)
        self.assertEqual(result["cohorts"][0]["target_commission_cap"]["rate_pct"], "38.88")
        self.assertEqual(result["cohorts"][1]["target_commission_cap"]["rate_pct"], "22.22")
        self.assertEqual(result["cohorts"][1]["break_even_commission_cap"]["rate_pct"], "33.33")

    def test_uniform_ceiling_is_conservative_when_fed_back(self):
        cap = calculate(self.data)["summary"]["uniform_target_commission_cap"]["rate"]
        for row in self.data["cohorts"]: row["commission_rate"] = cap
        self.assertGreaterEqual(Decimal(calculate(self.data)["summary"]["contribution"]), Decimal("400"))
        for row in self.data["cohorts"]: row["commission_rate"] = str(Decimal(cap)+Decimal("0.0001"))
        self.assertLess(Decimal(calculate(self.data)["summary"]["contribution"]), Decimal("400"))

    def test_group_ceiling_meets_its_own_profit_target(self):
        row = self.data["cohorts"][1]
        row["commission_rate"] = calculate(self.data)["cohorts"][1]["target_commission_cap"]["rate"]
        result = calculate(self.data)["cohorts"][1]
        self.assertGreaterEqual(Decimal(result["contribution"]), Decimal("160"))

    def test_ad_limit_holds_current_commission_fixed(self):
        result = calculate(self.data)
        self.assertEqual(result["summary"]["ad_budget_at_current_commissions_and_target"]["max_spend"], "932.00")
        self.assertEqual(result["cohorts"][1]["ad_budget_at_current_commission_and_target"]["max_spend"], "416.00")
        self.data["cohorts"][1]["ad_spend"] = "416"
        self.assertEqual(calculate(self.data)["cohorts"][1]["contribution"], "160.00")

    def test_joint_budget_exposes_commission_ad_tradeoff(self):
        summary = calculate(self.data)["summary"]
        self.assertEqual(summary["joint_commission_and_ad_budget_at_target"], "1400.00")
        available = Decimal(summary["joint_commission_and_ad_budget_at_target"])
        self.assertEqual(available-Decimal(summary["commission"])-Decimal(summary["ad_spend"]), Decimal("692.00"))

    def test_ad_limit_never_rounds_up_to_spend_more(self):
        result = ad_cap(Decimal("0.005"), Decimal(1), 2)
        self.assertEqual(result["max_spend"], "0.00")
        self.assertEqual(result["max_per_order"], "0.00")

    def test_zero_commission_cannot_rescue_negative_headroom(self):
        self.data["cohorts"][1]["ad_spend"] = "1000"
        result = calculate(self.data)["cohorts"][1]
        self.assertEqual(result["decision"], "LOSS")
        self.assertFalse(result["target_commission_cap"]["feasible"])
        self.assertIsNone(result["target_commission_cap"]["rate"])

    def test_zero_rate_can_be_a_valid_exact_boundary(self):
        self.data["cohorts"][1]["ad_spend"] = "560"
        cap = calculate(self.data)["cohorts"][1]["target_commission_cap"]
        self.assertTrue(cap["feasible"])
        self.assertEqual(cap["rate"], "0.0000")

    def test_no_commissionable_sales_has_no_infinite_rate(self):
        for row in self.data["cohorts"]:
            row.update(channel="non_affiliate", unit_commission_base="0", commission_rate="0")
        result = calculate(self.data)
        self.assertIsNone(result["summary"]["uniform_target_commission_cap"]["rate"])
        self.assertEqual(result["summary"]["commission"], "0.00")

    def test_full_refunds_keep_fulfillment_and_campaign_losses(self):
        self.data["unit_revenue"]["refunds"] = "40"
        for row in self.data["cohorts"]: row["unit_commission_base"] = "0"
        result = calculate(self.data)
        self.assertEqual(result["summary"]["contribution"], "-2240.00")
        self.assertIsNone(result["summary"]["contribution_margin_pct"])

    def test_zero_orders_keeps_sunk_spend_without_dividing(self):
        for row in self.data["cohorts"]: row["orders"] = 0
        result = calculate(self.data)
        self.assertEqual(result["summary"]["contribution"], "-440.00")
        self.assertEqual(result["summary"]["unallocated_campaign_costs"], "200.00")
        self.assertEqual(result["summary"]["decision"], "NO_ORDERS")
        self.assertIsNone(result["summary"]["contribution_per_order"])
        self.assertIsNone(result["summary"]["uniform_break_even_commission_cap"]["rate"])

    def test_commission_ceiling_cannot_exceed_one_hundred_percent(self):
        for row in self.data["cohorts"]: row["unit_commission_base"] = "0.01"
        self.assertEqual(calculate(self.data)["summary"]["uniform_target_commission_cap"]["rate"], "1.0000")

    def test_zero_decimal_currency_display(self):
        self.data.update(currency="JPY", currency_minor_units=0)
        self.assertEqual(calculate(self.data)["summary"]["contribution"], "1092")

    def test_unknown_cost_is_not_filled_with_zero(self):
        self.data["unit_costs"]["fulfillment"] = None
        with self.assertRaises(ValueError): calculate(self.data)

    def test_missing_cost_and_unsupported_extra_field_rejected(self):
        del self.data["unit_costs"]["refund_admin"]
        with self.assertRaises(ValueError): calculate(self.data)
        self.setUp(); self.data["unit_costs"]["unknown_currency_fee"] = "10"
        with self.assertRaises(ValueError): calculate(self.data)

    def test_mixed_currency_amount_is_rejected(self):
        self.data["unit_costs"]["product"] = {"amount": "10", "currency": "CNY"}
        with self.assertRaises(ValueError): calculate(self.data)

    def test_already_net_settlement_cannot_be_deducted_twice(self):
        self.data["revenue_basis"] = "net_payout_after_fees"
        with self.assertRaises(ValueError): calculate(self.data)

    def test_percent_as_fifteen_instead_of_fraction_is_rejected(self):
        self.data["cohorts"][0]["commission_rate"] = "15"
        with self.assertRaises(ValueError): calculate(self.data)

    def test_nonfinite_negative_boolean_and_huge_amounts_rejected(self):
        for value in ("NaN", "Infinity", -1, True, "1e1000"):
            with self.subTest(value_type=type(value).__name__):
                self.data["unit_costs"]["product"] = value
                with self.assertRaises(ValueError): calculate(self.data)

    def test_fractional_orders_and_duplicate_groups_rejected(self):
        self.data["cohorts"][0]["orders"] = "1.5"
        with self.assertRaises(ValueError): calculate(self.data)
        self.setUp(); self.data["cohorts"].append(copy.deepcopy(self.data["cohorts"][0]))
        with self.assertRaises(ValueError): calculate(self.data)

    def test_refunds_and_inventory_recovery_cannot_exceed_basis(self):
        self.data["unit_revenue"]["refunds"] = "41"
        with self.assertRaises(ValueError): calculate(self.data)
        self.setUp(); self.data["unit_inventory_recovery_credit"] = "12"
        with self.assertRaises(ValueError): calculate(self.data)

    def test_nonaffiliate_commission_is_rejected(self):
        self.data["cohorts"][0]["channel"] = "non_affiliate"
        with self.assertRaises(ValueError): calculate(self.data)

    def test_wrong_grain_and_date_order_rejected(self):
        self.data["unit_basis"] = "mixed_sku_cart"
        with self.assertRaises(ValueError): calculate(self.data)
        self.setUp(); self.data["period"]["start"] = "2026-10-01"
        with self.assertRaises(ValueError): calculate(self.data)

    def test_strict_json_rejects_duplicate_keys_and_nan(self):
        for source in ('{"orders":1,"orders":2}', '{"rate":NaN}', '{"rate":Infinity}'):
            with self.subTest(source=source):
                with self.assertRaises(ValueError): parse_json(source)

    def test_decimal_input_is_not_changed_by_binary_floats(self):
        self.assertEqual(parse_json('{"amount":0.1234567890123456789}')["amount"], Decimal("0.1234567890123456789"))

    def test_cli_example_and_stdin_are_equivalent(self):
        file_result = subprocess.run([sys.executable, "-B", str(SCRIPT), str(EXAMPLE)], capture_output=True, text=True)
        stdin_result = subprocess.run([sys.executable, "-B", str(SCRIPT), "-"], input=EXAMPLE.read_text(), capture_output=True, text=True)
        self.assertEqual(file_result.returncode, 0)
        self.assertEqual(stdin_result.returncode, 0)
        self.assertEqual(json.loads(file_result.stdout), json.loads(stdin_result.stdout))

    def test_cli_unknown_input_is_hold_and_nonzero_exit(self):
        self.data["unit_costs"]["fulfillment"] = None
        result = subprocess.run([sys.executable, "-B", str(SCRIPT), "-"], input=json.dumps(self.data), capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["status"], "HOLD")
        self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
