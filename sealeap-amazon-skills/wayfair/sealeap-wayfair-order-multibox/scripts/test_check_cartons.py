"""Synthetic shipment-plan errors; no shipping request is sent."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest

import check_cartons as checker

SCRIPT = Path(__file__).with_name("check_cartons.py")
EXAMPLE = SCRIPT.parent.parent / "references/example-cartons.json"


class CartonTests(unittest.TestCase):
    def setUp(self):
        self.data = checker.parse_json(EXAMPLE.read_text())

    def codes(self, data=None):
        result = checker.check(self.data if data is None else data)
        self.assertEqual(result["status"], "HOLD")
        self.assertFalse(result["ok"])
        return {error["code"] for error in result["errors"]}

    def run_cli(self, source):
        return subprocess.run([sys.executable, str(SCRIPT), "-"], input=source,
                              text=True, capture_output=True)

    def test_two_sellable_units_have_four_boxes_and_one_bol(self):
        result = checker.check(self.data)
        self.assertTrue(result["ok"])
        self.assertEqual(result["status"], "READY_FOR_REVIEW")
        self.assertEqual(result["expected_cartons"], 4)
        self.assertEqual(result["provided_cartons"], 4)

    def test_small_parcel_needs_individual_tracking(self):
        self.data["mode"] = "small_parcel"
        self.assertIn("duplicate_parcel_tracking", self.codes())
        for index, carton in enumerate(self.data["cartons"]):
            carton["tracking_ref"] = f"synthetic-parcel-{index}"
        self.assertTrue(checker.check(self.data)["ok"])

    def test_shared_large_parcel_tracking_does_not_allow_duplicate_box_ids(self):
        self.data["cartons"][1]["package_id"] = "box-a"
        self.assertIn("duplicate_package_id", self.codes())

    def test_equal_box_count_cannot_hide_missing_component_slot(self):
        self.data["cartons"][1]["slot_id"] = "A"
        self.data["cartons"][1]["component_part_number"] = "headboard-a"
        self.assertEqual(self.codes(), {"duplicate_unit_slot", "missing_unit_slot"})

    def test_wrong_component_is_rejected(self):
        self.data["cartons"][0]["component_part_number"] = "rail-kit-a"
        self.assertIn("wrong_component", self.codes())

    def test_wrong_warehouse_is_rejected(self):
        self.data["cartons"][0]["warehouse_id"] = "synthetic-warehouse-b"
        self.assertIn("wrong_warehouse", self.codes())

    def test_wrong_destination_is_rejected(self):
        self.data["cartons"][0]["destination_ref"] = "synthetic-destination-b"
        self.assertIn("wrong_destination", self.codes())

    def test_unknown_line_or_extra_unit_does_not_replace_expected_slot(self):
        for field, value in [("line_id", "line-b"), ("unit_index", 3), ("slot_id", "C")]:
            with self.subTest(field=field):
                data = copy.deepcopy(self.data)
                data["cartons"][0][field] = value
                codes = self.codes(data)
                self.assertIn("unexpected_unit_slot", codes)
                self.assertIn("missing_unit_slot", codes)

    def test_missing_box_remains_detectable_when_declared_count_is_lowered(self):
        self.data["cartons"].pop()
        self.data["declared_package_count"] = 3
        self.assertEqual(self.codes(), {"expected_package_count_mismatch", "missing_unit_slot"})

    def test_declared_count_must_match_physical_package_rows(self):
        self.data["declared_package_count"] = 2
        self.assertEqual(self.codes(), {"declared_package_count_mismatch"})

    def test_empty_or_whitespace_identifiers_are_rejected(self):
        for value in ["", " ", " synthetic-bol-a", None]:
            with self.subTest(value=value):
                data = copy.deepcopy(self.data)
                data["cartons"][0]["tracking_ref"] = value
                with self.assertRaises(ValueError):
                    checker.check(data)

    def test_boolean_or_fractional_counts_are_rejected(self):
        for value in [True, 1.5, "2", 0, -1]:
            with self.subTest(value=value):
                data = copy.deepcopy(self.data)
                data["lines"][0]["ordered_units"] = value
                with self.assertRaises(ValueError):
                    checker.check(data)

    def test_duplicate_order_lines_and_slots_are_rejected(self):
        self.data["lines"].append(copy.deepcopy(self.data["lines"][0]))
        with self.assertRaises(ValueError):
            checker.check(self.data)
        self.data["lines"].pop()
        self.data["lines"][0]["carton_slots"].append(copy.deepcopy(self.data["lines"][0]["carton_slots"][0]))
        with self.assertRaises(ValueError):
            checker.check(self.data)

    def test_same_component_can_fill_distinct_approved_bom_slots(self):
        for slot in self.data["lines"][0]["carton_slots"]:
            slot["component_part_number"] = "identical-chair-carton"
        for carton in self.data["cartons"]:
            carton["component_part_number"] = "identical-chair-carton"
        self.assertTrue(checker.check(self.data)["ok"])

    def test_two_lines_share_same_slot_names_without_collision(self):
        line = copy.deepcopy(self.data["lines"][0])
        line["line_id"] = "line-b"
        line["ordered_units"] = 1
        self.data["lines"].append(line)
        for original in self.data["cartons"][:2]:
            carton = copy.deepcopy(original)
            carton["line_id"] = "line-b"
            carton["package_id"] += "-extra"
            self.data["cartons"].append(carton)
        self.data["declared_package_count"] = 6
        result = checker.check(self.data)
        self.assertTrue(result["ok"])
        self.assertEqual(result["expected_cartons"], 6)

    def test_partial_and_unsupported_schema_are_rejected(self):
        for field, value in [("scope", "partial_order"), ("schema_version", True),
                             ("mode", "mixed"), ("extra", 0)]:
            with self.subTest(field=field):
                data = copy.deepcopy(self.data)
                data[field] = value
                with self.assertRaises(ValueError):
                    checker.check(data)

    def test_local_size_guard_rejects_excessive_expansion(self):
        self.data["lines"][0]["ordered_units"] = 10000
        with self.assertRaises(ValueError):
            checker.check(self.data)

    def test_json_duplicate_and_nonfinite_numbers_hold(self):
        for source in ['{"lines":[],"lines":[]}', '{"units":NaN}', '{"units":Infinity}']:
            with self.subTest(source=source):
                result = self.run_cli(source)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(json.loads(result.stdout)["status"], "HOLD")

    def test_cli_file_and_stdin_match_and_failed_plan_exits_two(self):
        from_file = subprocess.run([sys.executable, str(SCRIPT), str(EXAMPLE)],
                                   text=True, capture_output=True)
        from_stdin = self.run_cli(EXAMPLE.read_text())
        self.assertEqual(from_file.returncode, 0)
        self.assertEqual(from_stdin.returncode, 0)
        self.assertEqual(json.loads(from_file.stdout), json.loads(from_stdin.stdout))
        self.data["cartons"].pop()
        bad = self.run_cli(json.dumps(self.data))
        self.assertEqual(bad.returncode, 2)
        self.assertEqual(json.loads(bad.stdout)["status"], "HOLD")


if __name__ == "__main__":
    unittest.main()
