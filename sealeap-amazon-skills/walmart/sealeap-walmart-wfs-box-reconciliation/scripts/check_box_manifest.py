#!/usr/bin/env python3
"""Offline plan/box consistency check. Never contacts Walmart or changes shipments."""
import json
import sys
from collections import Counter
from pathlib import Path

def validate(data):
    errors, planned, packed, destinations = [], {}, Counter(), {}
    seen_boxes, seen_labels = set(), set()
    def err(code, **context):
        errors.append(dict(code=code, **context))
    def text(value):
        return isinstance(value, str) and bool(value.strip())
    def units(value):
        return isinstance(value, int) and not isinstance(value, bool) and value > 0
    if not isinstance(data, dict):
        return {"ok": False, "errors": [{"code": "INVALID_DOCUMENT"}]}
    plan, boxes = data.get("plan"), data.get("boxes")
    if not isinstance(plan, list) or not plan:
        err("PLAN_REQUIRED")
        plan = []
    if not isinstance(boxes, list) or not boxes:
        err("BOXES_REQUIRED")
        boxes = []
    for index, row in enumerate(plan):
        if not isinstance(row, dict) or not all(text(row.get(k)) for k in ("shipment_id", "destination", "sku")) or not units(row.get("units")):
            err("INVALID_PLAN_ROW", row=index)
            continue
        shipment, sku, dest = row["shipment_id"], row["sku"], row["destination"]
        key = (shipment, sku)
        if key in planned:
            err("DUPLICATE_PLAN_KEY", shipment_id=shipment, sku=sku)
            continue
        if shipment in destinations and destinations[shipment] != dest:
            err("PLAN_DESTINATION_CONFLICT", shipment_id=shipment)
        destinations[shipment] = dest
        planned[key] = row["units"]
    for index, box in enumerate(boxes):
        if not isinstance(box, dict) or not all(text(box.get(k)) for k in ("shipment_id", "destination", "box_id", "receiving_label_id")):
            err("INVALID_BOX_IDENTITY", box_row=index)
            continue
        shipment, box_id, label = box["shipment_id"], box["box_id"], box["receiving_label_id"]
        key = (shipment, box_id)
        if key in seen_boxes:
            err("DUPLICATE_BOX", shipment_id=shipment, box_id=box_id)
        seen_boxes.add(key)
        if label in seen_labels:
            err("REUSED_RECEIVING_LABEL", box_row=index)
        seen_labels.add(label)
        if shipment not in destinations:
            err("UNKNOWN_SHIPMENT", shipment_id=shipment, box_id=box_id)
        elif box["destination"] != destinations[shipment]:
            err("WRONG_DESTINATION", shipment_id=shipment, box_id=box_id)
        items = box.get("items")
        if not isinstance(items, list) or not items:
            err("BOX_ITEMS_REQUIRED", shipment_id=shipment, box_id=box_id)
            continue
        for item_index, item in enumerate(items):
            if not isinstance(item, dict) or not text(item.get("sku")) or not units(item.get("units")):
                err("INVALID_BOX_ITEM", box_row=index, item_row=item_index)
                continue
            item_key = (shipment, item["sku"])
            if item_key not in planned:
                err("UNPLANNED_ITEM", shipment_id=shipment, sku=item["sku"])
            packed[item_key] += item["units"]
    totals = []
    for shipment, sku in sorted(set(planned) | set(packed)):
        expected, actual = planned.get((shipment, sku), 0), packed[(shipment, sku)]
        totals.append({"shipment_id": shipment, "sku": sku, "planned": expected, "packed": actual, "difference": actual-expected})
        if actual != expected:
            err("QUANTITY_MISMATCH", shipment_id=shipment, sku=sku, planned=expected, packed=actual)
    return {"ok": not errors, "checked_boxes": len(boxes), "totals": totals, "errors": errors,
            "boundary": "Input consistency only; physical contents, barcode scanning, platform eligibility and shipment status are unverified."}

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/check_box_manifest.py manifest.json", file=sys.stderr)
        return 2
    try:
        data = json.loads(Path(sys.argv[1]).read_text())
    except (OSError, ValueError) as exc:
        print(json.dumps({"ok": False, "errors": [{"code": "INPUT_READ_ERROR", "type": type(exc).__name__}]}))
        return 2
    result = validate(data)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 2

if __name__ == "__main__":
    sys.exit(main())

