"""Synthetic accounting and failure cases; no merchant data or account access."""
import copy
from decimal import Decimal
import json
from pathlib import Path
import subprocess
import sys
import unittest

import wholesale_contribution as calculator

SCRIPT = Path(__file__).with_name("wholesale_contribution.py")
EXAMPLE = SCRIPT.parent.parent / "references/example-scenario.json"


class ContributionTests(unittest.TestCase):
    def setUp(self):
        self.data = calculator.parse_json(EXAMPLE.read_text())

    def run_cli(self, source):
        return subprocess.run([sys.executable, str(SCRIPT), "-"], input=source,
                              text=True, capture_output=True)

    def test_supplier_revenue_to_contribution_bridge(self):
        result = calculator.calculate(self.data)
        self.assertEqual(result["unit"]["adjusted_supplier_revenue"], "175.00")
        self.assertEqual(result["unit"]["variable_cost_after_inventory_recovery"], "118.00")
        for key, value in {"gross_wholesale_revenue": "4000.00",
                           "adjusted_supplier_revenue": "3500.00",
                           "variable_costs": "2360.00", "fixed_costs": "80.00",
                           "contribution_before_ads": "1060.00",
                           "contribution_after_ads": "860.00",
                           "target_contribution": "600.00", "target_gap": "260.00"}.items():
            self.assertEqual(result["totals"][key], value)
        self.assertEqual(result["unit"]["contribution_after_ads"], "43.00")
        self.assertEqual(result["ad_budget_at_target"]["max_total_spend"], "460.00")
        self.assertEqual(result["theoretical_break_even_roas_on_adjusted_supplier_revenue"], "3.3019")

    def test_ad_ceiling_meets_target_when_fed_back(self):
        result = calculator.calculate(self.data)
        self.data["ad_spend"] = result["ad_budget_at_target"]["max_total_spend"]
        at_ceiling = calculator.calculate(self.data)
        self.assertEqual(at_ceiling["totals"]["contribution_after_ads"], "600.00")
        self.assertEqual(at_ceiling["totals"]["decision"], "TARGET_MET")
        self.data["ad_spend"] = "460.01"
        self.assertEqual(calculator.calculate(self.data)["totals"]["decision"], "BELOW_TARGET")

    def test_zero_sales_retains_fixed_and_ad_costs(self):
        self.data["units"] = 0
        result = calculator.calculate(self.data)
        self.assertEqual(result["totals"]["contribution_after_ads"], "-280.00")
        self.assertEqual(result["totals"]["decision"], "NO_SALES")
        self.assertIsNone(result["unit"]["contribution_after_ads"])
        self.assertIsNone(result["unit"]["fixed_cost_allocation"])
        self.assertIsNone(result["ad_budget_at_target"]["max_total_spend"])
        self.assertIsNone(result["theoretical_break_even_roas_on_adjusted_supplier_revenue"])

    def test_unreachable_target_has_no_positive_ceiling(self):
        self.data["target_unit_contribution"] = "60"
        result = calculator.calculate(self.data)
        self.assertFalse(result["ad_budget_at_target"]["feasible"])
        self.assertIsNone(result["ad_budget_at_target"]["max_total_spend"])
        self.assertEqual(result["ad_budget_at_target"]["shortfall_before_ads"], "140.00")

    def test_exact_zero_ceiling_is_distinct_from_infeasible(self):
        self.data["target_unit_contribution"] = "53"
        result = calculator.calculate(self.data)
        self.assertTrue(result["ad_budget_at_target"]["feasible"])
        self.assertEqual(result["ad_budget_at_target"]["max_total_spend"], "0.00")

    def test_ceiling_rounds_down_instead_of_overspending(self):
        self.data["unit_wholesale_price"] = "200.001"
        self.data["target_unit_contribution"] = "30.0003"
        result = calculator.calculate(self.data)
        self.assertEqual(result["ad_budget_at_target"]["max_total_spend"], "460.01")
        self.assertEqual(result["ad_budget_at_target"]["max_per_sellable_unit"], "23.00")

    def test_currency_precision_is_explicit(self):
        self.data["currency"] = "JPY"
        self.data["currency_minor_units"] = 0
        self.assertEqual(calculator.calculate(self.data)["totals"]["contribution_after_ads"], "860")

    def test_deductions_may_exceed_revenue_without_clamping_loss(self):
        self.data["unit_adjustments"]["refunds_and_claims"] = "300"
        result = calculator.calculate(self.data)
        self.assertEqual(result["unit"]["adjusted_supplier_revenue"], "-122.00")
        self.assertEqual(result["totals"]["decision"], "LOSS")
        self.assertFalse(result["ad_budget_at_target"]["feasible"])
        self.assertIsNone(result["theoretical_break_even_roas_on_adjusted_supplier_revenue"])

    def test_zero_before_ad_contribution_has_no_infinite_roas(self):
        self.data["unit_costs"]["other"] = "54"
        result = calculator.calculate(self.data)
        self.assertEqual(result["totals"]["contribution_before_ads"], "0.00")
        self.assertIsNone(result["theoretical_break_even_roas_on_adjusted_supplier_revenue"])

    def test_credit_and_recovery_are_separate_accounting_effects(self):
        base = calculator.calculate(self.data)
        self.data["unit_adjustments"]["credits"] = "2"
        self.data["unit_inventory_recovery_credit"] = "3"
        result = calculator.calculate(self.data)
        self.assertEqual(result["totals"]["adjusted_supplier_revenue"], "3520.00")
        self.assertEqual(result["totals"]["variable_costs"], "2340.00")
        self.assertEqual(Decimal(result["totals"]["contribution_after_ads"]) -
                         Decimal(base["totals"]["contribution_after_ads"]), Decimal("40"))

    def test_fixed_cost_does_not_scale_with_units(self):
        self.data["units"] = 1
        self.data["ad_spend"] = "0"
        result = calculator.calculate(self.data)
        self.assertEqual(result["totals"]["fixed_costs"], "80.00")
        self.assertEqual(result["totals"]["contribution_after_ads"], "-23.00")

    def test_revenue_and_incident_bases_must_be_reconciled(self):
        for field, value in [("revenue_basis", "retail_gmv"),
                             ("revenue_basis", "net_bank_payout"),
                             ("incident_basis", "unknown")]:
            with self.subTest(field=field, value=value):
                data = copy.deepcopy(self.data)
                data[field] = value
                with self.assertRaises(ValueError):
                    calculator.calculate(data)

    def test_missing_unknown_and_mixed_currency_costs_are_not_zero(self):
        cases = [None, {"USD": "90", "CAD": "10"}, True, "NaN", "Infinity", "-1"]
        for value in cases:
            with self.subTest(value=value):
                data = copy.deepcopy(self.data)
                data["unit_costs"]["product"] = value
                with self.assertRaises(ValueError):
                    calculator.calculate(data)
        del self.data["unit_costs"]["storage"]
        with self.assertRaises(ValueError):
            calculator.calculate(self.data)

    def test_unsupported_schema_and_nonwhole_units_are_rejected(self):
        for field, value in [("unexpected", 0), ("units", "1.5"), ("units", True),
                             ("units", -1), ("schema_version", True),
                             ("currency_minor_units", True), ("unit_wholesale_price", 0)]:
            with self.subTest(field=field, value=value):
                data = copy.deepcopy(self.data)
                data[field] = value
                with self.assertRaises(ValueError):
                    calculator.calculate(data)

    def test_inventory_recovery_cannot_exceed_modeled_inventory_cost(self):
        self.data["unit_inventory_recovery_credit"] = "102.01"
        with self.assertRaises(ValueError):
            calculator.calculate(self.data)

    def test_declared_actual_does_not_claim_verified_profit(self):
        self.data["input_kind"] = "actual"
        result = calculator.calculate(self.data)
        self.assertEqual(result["input_kind"], "actual")
        self.assertEqual(result["evidence_label"], "ESTIMATE")

    def test_json_duplicate_and_nonfinite_numbers_hold(self):
        for source in ['{"units":1,"units":2}', '{"units":NaN}', '{"units":Infinity}']:
            with self.subTest(source=source):
                result = self.run_cli(source)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(json.loads(result.stdout)["status"], "HOLD")

    def test_cli_file_and_stdin_have_same_result(self):
        from_file = subprocess.run([sys.executable, str(SCRIPT), str(EXAMPLE)],
                                   text=True, capture_output=True)
        from_stdin = self.run_cli(EXAMPLE.read_text())
        self.assertEqual(from_file.returncode, 0)
        self.assertEqual(from_stdin.returncode, 0)
        self.assertEqual(json.loads(from_file.stdout), json.loads(from_stdin.stdout))

    def test_cli_unreadable_input_holds_without_echoing_path(self):
        result = subprocess.run([sys.executable, str(SCRIPT), str(SCRIPT / "missing.json")],
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertNotIn(str(SCRIPT), result.stdout)
        self.assertEqual(json.loads(result.stdout)["status"], "HOLD")


if __name__ == "__main__":
    unittest.main()
