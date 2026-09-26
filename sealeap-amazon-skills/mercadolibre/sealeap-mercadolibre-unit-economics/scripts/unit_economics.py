#!/usr/bin/env python3
"""Offline same-currency unit-economics scenarios; no platform fees or tax rates are embedded."""
import argparse
import json
import sys
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

COST_KEYS = ("product", "inbound", "platform_fee", "shipping", "nonrecoverable_tax", "storage", "expected_returns", "other")


def number(value, label, positive=False):
    if value is None or isinstance(value, bool):
        raise ValueError(f"{label}: provide an explicit amount; unknown is not zero")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError(f"{label}: invalid number") from None
    if not result.is_finite() or result < 0 or (positive and result <= 0):
        raise ValueError(f"{label}: amount must be finite and {'positive' if positive else 'nonnegative'}")
    return result


def money(value):
    return str(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def calculate(data):
    if not isinstance(data, dict):
        raise ValueError("Input must be an object")
    for key in ("site", "currency", "sku", "basis_note"):
        if not isinstance(data.get(key), str) or not data[key].strip():
            raise ValueError(f"{key}: required")
    currency = data["currency"]
    if len(currency) != 3 or not currency.isascii() or not currency.isalpha() or currency != currency.upper():
        raise ValueError("currency: use one uppercase ISO currency code for every amount")
    if data.get("revenue_basis") != "seller_sales_before_platform_deductions":
        raise ValueError("Use seller sales revenue after discounts and excluded pass-through taxes, before platform deductions; do not supply already-net proceeds")
    units = number(data.get("units"), "units")
    if units != units.to_integral_value():
        raise ValueError("units: must be a whole number of the stated selling unit")
    price = number(data.get("unit_revenue"), "unit_revenue", positive=True)
    costs = data.get("unit_costs")
    if not isinstance(costs, dict) or set(costs) != set(COST_KEYS):
        raise ValueError("unit_costs: all eight named cost items are required; explicit zero is allowed")
    amounts = {k: number(costs[k], "unit_costs." + k) for k in COST_KEYS}
    ads = number(data.get("ad_spend"), "ad_spend")
    withholding = number(data.get("recoverable_withholding_cash"), "recoverable_withholding_cash")
    held = number(data.get("held_cash"), "held_cash")
    unit_cost = sum(amounts.values(), Decimal(0))
    unit_contribution = price - unit_cost
    revenue = price * units
    before_ads = unit_contribution * units
    after_ads = before_ads - ads
    margin = unit_contribution / price
    return {
        "status": "CALCULATED_SCENARIO",
        "evidence_label": "ESTIMATE",
        "site": data["site"], "currency": currency, "sku": data["sku"],
        "units": int(units), "basis_note": data["basis_note"],
        "unit_variable_cost": money(unit_cost),
        "unit_contribution_before_ads": money(unit_contribution),
        "revenue": money(revenue),
        "contribution_before_ads": money(before_ads),
        "contribution_after_ads": money(after_ads),
        "pre_ad_contribution_margin_pct": money(margin * 100),
        "theoretical_break_even_roas": money(Decimal(1) / margin) if margin > 0 else None,
        "recoverable_withholding_cash": money(withholding),
        "held_cash": money(held),
        "cash_after_modeled_costs_and_restrictions": money(after_ads - withholding - held),
        "limits": [
            "Scenario only, not a bank balance or complete accounting profit.",
            "Fixed overhead, payment dates and financing costs need separate modeling.",
            "Withholding is excluded from expense only when recoverability has been verified.",
            "Theoretical break-even ROAS requires comparable revenue and cost scope; it is not a promised platform result.",
        ],
    }


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key: " + key)
        result[key] = value
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="Local JSON scenario; no credentials required")
    args = parser.parse_args()
    try:
        with open(args.input, encoding="utf-8") as handle:
            data = json.load(handle, object_pairs_hook=unique_object)
        result = calculate(data)
    except (OSError, ValueError, InvalidOperation) as error:
        print(json.dumps({"status": "HOLD", "reason": str(error)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
