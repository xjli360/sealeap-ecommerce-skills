#!/usr/bin/env python3
import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("economics", ROOT / "scripts/unit_economics.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
BASE = json.loads((ROOT / "references/scenario.example.json").read_text())


class ScenarioTests(unittest.TestCase):
    def test_synthetic_contribution_and_cash(self):
        result = module.calculate(BASE)
        self.assertEqual(result["contribution_after_ads"], "300.00")
        self.assertEqual(result["cash_after_modeled_costs_and_restrictions"], "210.00")
        self.assertEqual(result["theoretical_break_even_roas"], "2.50")

    def test_cash_restrictions_do_not_change_contribution(self):
        data = copy.deepcopy(BASE)
        data["held_cash"] = "900"
        result = module.calculate(data)
        self.assertEqual(result["contribution_after_ads"], "300.00")
        self.assertEqual(result["cash_after_modeled_costs_and_restrictions"], "-640.00")

    def test_nonpositive_margin_has_no_positive_break_even_roas(self):
        for cost in ["70", "90"]:
            data = copy.deepcopy(BASE)
            data["unit_costs"]["product"] = cost
            self.assertIsNone(module.calculate(data)["theoretical_break_even_roas"])

    def test_missing_cost_is_not_zero(self):
        data = copy.deepcopy(BASE)
        del data["unit_costs"]["shipping"]
        with self.assertRaises(ValueError):
            module.calculate(data)

    def test_unknown_or_nonfinite_amounts_fail(self):
        for value in [None, True, "NaN", "Infinity", "-1"]:
            data = copy.deepcopy(BASE)
            data["unit_costs"]["shipping"] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                module.calculate(data)

    def test_already_net_revenue_is_rejected(self):
        data = copy.deepcopy(BASE)
        data["revenue_basis"] = "net_proceeds"
        with self.assertRaises(ValueError):
            module.calculate(data)

    def test_zero_sales_and_nonzero_ads(self):
        data = copy.deepcopy(BASE)
        data.update(units=0, ad_spend="30", recoverable_withholding_cash=0, held_cash=0)
        self.assertEqual(module.calculate(data)["contribution_after_ads"], "-30.00")

    def test_fractional_units_rejected(self):
        data = copy.deepcopy(BASE)
        data["units"] = "1.5"
        with self.assertRaises(ValueError):
            module.calculate(data)

    def test_duplicate_json_keys_rejected(self):
        with self.assertRaises(ValueError):
            json.loads('{"units":1,"units":2}', object_pairs_hook=module.unique_object)

    def test_currency_must_be_explicit(self):
        data = copy.deepcopy(BASE)
        data["currency"] = "mxn"
        with self.assertRaises(ValueError):
            module.calculate(data)


if __name__ == "__main__":
    unittest.main()
