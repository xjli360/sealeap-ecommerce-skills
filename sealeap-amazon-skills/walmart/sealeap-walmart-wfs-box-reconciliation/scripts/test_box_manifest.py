import copy
import unittest
from check_box_manifest import validate

BASE = {"plan": [
    {"shipment_id": "SHIP-A", "destination": "FC-A", "sku": "SKU-A", "units": 6},
    {"shipment_id": "SHIP-A", "destination": "FC-A", "sku": "SKU-B", "units": 4}],
    "boxes": [
    {"shipment_id": "SHIP-A", "destination": "FC-A", "box_id": "BOX-1", "receiving_label_id": "LABEL-1",
     "items": [{"sku": "SKU-A", "units": 3}, {"sku": "SKU-B", "units": 2}]},
    {"shipment_id": "SHIP-A", "destination": "FC-A", "box_id": "BOX-2", "receiving_label_id": "LABEL-2",
     "items": [{"sku": "SKU-A", "units": 3}, {"sku": "SKU-B", "units": 2}]}]}

class ManifestChecks(unittest.TestCase):
    def codes(self, data):
        return {x["code"] for x in validate(data)["errors"]}
    def test_valid_split_sku_across_boxes(self):
        result = validate(BASE)
        self.assertTrue(result["ok"])
        self.assertEqual(sum(x["packed"] for x in result["totals"]), 10)
    def test_duplicate_label_despite_correct_quantities(self):
        d=copy.deepcopy(BASE);d["boxes"][1]["receiving_label_id"]="LABEL-1"
        self.assertIn("REUSED_RECEIVING_LABEL", self.codes(d))
    def test_correct_total_wrong_warehouse(self):
        d=copy.deepcopy(BASE);d["boxes"][1]["destination"]="FC-B"
        self.assertIn("WRONG_DESTINATION", self.codes(d))
    def test_short_and_overpacked(self):
        for quantity in (2,4):
            d=copy.deepcopy(BASE);d["boxes"][0]["items"][0]["units"]=quantity
            self.assertIn("QUANTITY_MISMATCH", self.codes(d))
    def test_unplanned_item(self):
        d=copy.deepcopy(BASE);d["boxes"][0]["items"].append({"sku":"EXTRA","units":1})
        self.assertIn("UNPLANNED_ITEM", self.codes(d))
    def test_repeated_plan_not_silently_aggregated(self):
        d=copy.deepcopy(BASE);d["plan"].append(copy.deepcopy(d["plan"][0]))
        self.assertIn("DUPLICATE_PLAN_KEY", self.codes(d))
    def test_invalid_quantity_types(self):
        for quantity in (True,0,-1,1.5,"3"):
            d=copy.deepcopy(BASE);d["boxes"][0]["items"][0]["units"]=quantity
            self.assertIn("INVALID_BOX_ITEM", self.codes(d))
    def test_empty_and_malformed_documents(self):
        for data in (None,[],{},{"plan":[],"boxes":[]},{"plan":[None],"boxes":[None]}):
            self.assertFalse(validate(data)["ok"])
    def test_box_numbers_can_repeat_between_shipments(self):
        d=copy.deepcopy(BASE)
        d["plan"].append({"shipment_id":"SHIP-B","destination":"FC-B","sku":"SKU-A","units":1})
        d["boxes"].append({"shipment_id":"SHIP-B","destination":"FC-B","box_id":"BOX-1","receiving_label_id":"LABEL-3","items":[{"sku":"SKU-A","units":1}]})
        self.assertTrue(validate(d)["ok"])
    def test_actual_box_repeated_is_error(self):
        d=copy.deepcopy(BASE);d["boxes"][1]["box_id"]="BOX-1"
        self.assertIn("DUPLICATE_BOX",self.codes(d))

if __name__ == "__main__":
    unittest.main()

