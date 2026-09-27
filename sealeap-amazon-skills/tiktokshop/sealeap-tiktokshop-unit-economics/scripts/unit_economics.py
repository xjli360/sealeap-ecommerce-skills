#!/usr/bin/env python3
"""Offline TikTok Shop contribution, affiliate commission ceilings and ad budgets.

No platform rates, credentials, network calls or account changes are embedded.
All money inputs use one declared currency and the same one-unit order cohort.
"""
import argparse
from datetime import date
from decimal import Decimal, DecimalException, ROUND_DOWN, ROUND_HALF_UP, localcontext
import json
import re
import sys

ZERO = Decimal(0)
ONE = Decimal(1)
MAX_AMOUNT = Decimal("1000000000000")
MAX_ORDERS = 1000000000
REVENUE_BASIS = "seller_revenue_before_fees_excluding_pass_through_tax"
UNIT_BASIS = "one_paid_shipped_order_one_sellable_unit"
REVENUE_KEYS = {"item_after_seller_discount", "seller_shipping_income", "additional_seller_incentives", "refunds"}
COST_KEYS = {"product", "inbound", "packaging", "fulfillment", "platform_fee", "refund_admin",
             "return_logistics", "return_handling", "storage", "nonrecoverable_tax", "other"}
CAMPAIGN_KEYS = {"samples", "creator_fixed_fees", "content_production", "other_fixed"}
CHANNELS = {"standard_affiliate", "shop_ads_affiliate", "non_affiliate"}
ROOT_KEYS = {"schema_version", "site", "currency", "currency_minor_units", "sku", "period",
             "input_kind", "basis_note", "revenue_basis", "unit_basis", "unit_revenue",
             "unit_costs", "unit_inventory_recovery_credit", "campaign_costs",
             "target_unit_contribution", "cohorts"}
COHORT_KEYS = {"id", "channel", "orders", "unit_commission_base", "commission_rate", "ad_spend", "basis_note"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def keys(value, expected, label):
    require(isinstance(value, dict), f"{label}: expected an object")
    require(set(value) == expected, f"{label}: missing or unsupported fields; check the documented schema")


def text(value, label):
    require(isinstance(value, str) and bool(value.strip()), f"{label}: required nonempty text")
    return value.strip()


def number(value, label, maximum=MAX_AMOUNT):
    require(value is not None and not isinstance(value, bool), f"{label}: unknown is not zero")
    require(isinstance(value, (str, int, float, Decimal)), f"{label}: use an amount in the declared currency")
    try:
        result = Decimal(str(value))
    except DecimalException:
        raise ValueError(f"{label}: invalid number") from None
    require(result.is_finite() and ZERO <= result <= maximum, f"{label}: outside the finite nonnegative supported range")
    return result


def amounts(value, expected, label):
    keys(value, expected, label)
    return {key: number(value[key], f"{label}.{key}") for key in sorted(expected)}


def money(value, minor_units):
    return format(value.quantize(ONE.scaleb(-minor_units), rounding=ROUND_HALF_UP), "f")


def budget_money(value, minor_units):
    return format(value.quantize(ONE.scaleb(-minor_units), rounding=ROUND_DOWN), "f")


def percent(value):
    return format((value*100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP), "f")


def commission_cap(available, base, minor_units):
    """Floor, never round up, a mathematical rate cap to 0.01 percentage point."""
    result = {"available_for_commission": money(available, minor_units), "rate": None,
              "rate_pct": None, "feasible": False, "economic_only": True}
    if base <= 0:
        result["reason"] = "no_commissionable_base"
    elif available < 0:
        result["reason"] = "target_unreachable_even_at_zero_commission"
    else:
        cap = min(available/base, ONE).quantize(Decimal("0.0001"), rounding=ROUND_DOWN)
        result.update(rate=format(cap, "f"), rate_pct=percent(cap), feasible=True,
                      reason="within_economic_limit_only")
    return result


def ad_cap(available, orders, minor_units):
    feasible = orders > 0 and available >= 0
    return {"feasible": feasible, "max_spend": budget_money(available, minor_units) if feasible else None,
            "max_per_order": budget_money(available/orders, minor_units) if feasible else None,
            "shortfall_before_ads": money(max(-available, ZERO), minor_units),
            "reason": "no_orders" if orders == 0 else "target_unreachable_before_ads" if available < 0 else "economic_limit_only"}


def decision(profit, target, orders):
    if orders == 0:
        return "NO_ORDERS"
    if profit < 0:
        return "LOSS"
    return "TARGET_MET" if profit >= target else "BELOW_TARGET"


def calculate(data):
    with localcontext() as context:
        context.prec = 40
        return _calculate(data)


def _calculate(data):
    keys(data, ROOT_KEYS, "scenario")
    require(type(data["schema_version"]) is int and data["schema_version"] == 1, "schema_version: expected 1")
    site, sku = text(data["site"], "site"), text(data["sku"], "sku")
    basis_note = text(data["basis_note"], "basis_note")
    currency = text(data["currency"], "currency")
    require(bool(re.fullmatch(r"[A-Z]{3}", currency)), "currency: one uppercase ISO-style code is required")
    minor = data["currency_minor_units"]
    require(type(minor) is int and 0 <= minor <= 3, "currency_minor_units: choose 0, 1, 2 or 3")
    require(data["revenue_basis"] == REVENUE_BASIS, "revenue_basis: already-net settlement or advertising GMV is not accepted")
    require(data["unit_basis"] == UNIT_BASIS, "unit_basis: normalize to one paid, shipped order containing one sellable unit")
    require(data["input_kind"] in ("synthetic", "estimate", "actual"), "input_kind: synthetic, estimate or actual required")
    keys(data["period"], {"start", "end"}, "period")
    try:
        first, last = (date.fromisoformat(data["period"][k]) for k in ("start", "end"))
    except (ValueError, TypeError):
        raise ValueError("period: use YYYY-MM-DD dates") from None
    require(first <= last, "period: start must not follow end")

    revenue = amounts(data["unit_revenue"], REVENUE_KEYS, "unit_revenue")
    costs = amounts(data["unit_costs"], COST_KEYS, "unit_costs")
    campaign = amounts(data["campaign_costs"], CAMPAIGN_KEYS, "campaign_costs")
    recovery = number(data["unit_inventory_recovery_credit"], "unit_inventory_recovery_credit")
    target_unit = number(data["target_unit_contribution"], "target_unit_contribution")
    require(recovery <= costs["product"]+costs["inbound"], "inventory recovery cannot exceed modeled product plus inbound cost")
    before_refunds = sum((value for key, value in revenue.items() if key != "refunds"), ZERO)
    require(revenue["refunds"] <= before_refunds, "refunds exceed this cohort's revenue; separate cross-period refunds")
    unit_revenue = before_refunds-revenue["refunds"]
    unit_cost = sum(costs.values(), ZERO)-recovery
    unit_before_marketing = unit_revenue-unit_cost
    fixed = sum(campaign.values(), ZERO)

    require(isinstance(data["cohorts"], list) and 1 <= len(data["cohorts"]) <= 100, "cohorts: provide 1 to 100 disjoint groups")
    cohorts, seen = [], set()
    for row in data["cohorts"]:
        keys(row, COHORT_KEYS, "cohort")
        identifier = text(row["id"], "cohort.id")
        require(identifier not in seen, "cohort.id: duplicate group would double-count orders")
        seen.add(identifier)
        require(row["channel"] in CHANNELS, "cohort.channel: unsupported channel")
        count = number(row["orders"], "cohort.orders", Decimal(MAX_ORDERS))
        require(count == count.to_integral_value(), "cohort.orders: must be a whole count")
        rate = number(row["commission_rate"], "cohort.commission_rate", ONE)
        base = number(row["unit_commission_base"], "cohort.unit_commission_base")
        ads = number(row["ad_spend"], "cohort.ad_spend")
        note = text(row["basis_note"], "cohort.basis_note")
        if row["channel"] == "non_affiliate":
            require(base == 0 and rate == 0, "non_affiliate: commission base and rate must both be zero")
        cohorts.append(dict(id=identifier, channel=row["channel"], orders=count, rate=rate, base=base, ads=ads, basis_note=note))
    count = sum((row["orders"] for row in cohorts), ZERO)
    require(count <= MAX_ORDERS, "total orders exceed the supported range")
    per_order_fixed = fixed/count if count else ZERO
    results = []
    commission_total, ads_total, base_total = ZERO, ZERO, ZERO
    for row in cohorts:
        n = row["orders"]
        group_revenue = unit_revenue*n
        group_fixed = per_order_fixed*n
        before = unit_before_marketing*n-group_fixed
        base = row["base"]*n
        commission = base*row["rate"]
        profit = before-commission-row["ads"]
        target = target_unit*n
        commission_total += commission; ads_total += row["ads"]; base_total += base
        results.append({
            "id": row["id"], "channel": row["channel"], "orders": int(n), "basis_note": row["basis_note"],
            "seller_revenue_after_refunds": money(group_revenue, minor),
            "noncommission_variable_costs": money(unit_cost*n, minor), "allocated_campaign_costs": money(group_fixed, minor),
            "commission_base": money(base, minor), "commission_rate": format(row["rate"], "f"),
            "commission": money(commission, minor), "ad_spend": money(row["ads"], minor),
            "contribution": money(profit, minor), "contribution_per_order": money(profit/n, minor) if n else None,
            "contribution_margin_pct": percent(profit/group_revenue) if group_revenue > 0 else None,
            "decision": decision(profit, target, n),
            "joint_commission_and_ad_budget_at_target": budget_money(before-target, minor) if n > 0 and before >= target else None,
            "break_even_commission_cap": commission_cap(before-row["ads"], base, minor),
            "target_commission_cap": commission_cap(before-row["ads"]-target, base, minor),
            "ad_budget_at_current_commission_and_target": ad_cap(before-commission-target, n, minor),
        })

    retained_revenue = unit_revenue*count
    before = unit_before_marketing*count-fixed
    profit = before-commission_total-ads_total
    target = target_unit*count
    summary = {
        "orders": int(count), "seller_revenue_after_refunds": money(retained_revenue, minor),
        "noncommission_variable_costs": money(unit_cost*count, minor), "campaign_costs": money(fixed, minor),
        "unallocated_campaign_costs": money(fixed if count == 0 else ZERO, minor),
        "commission_base": money(base_total, minor), "commission": money(commission_total, minor),
        "ad_spend": money(ads_total, minor), "contribution": money(profit, minor),
        "contribution_per_order": money(profit/count, minor) if count else None,
        "contribution_margin_pct": percent(profit/retained_revenue) if retained_revenue > 0 else None,
        "target_contribution": money(target, minor), "target_gap": money(profit-target, minor),
        "decision": decision(profit, target, count),
        "joint_commission_and_ad_budget_at_target": budget_money(before-target, minor) if count > 0 and before >= target else None,
        "uniform_break_even_commission_cap": commission_cap(before-ads_total, base_total, minor),
        "uniform_target_commission_cap": commission_cap(before-ads_total-target, base_total, minor),
        "ad_budget_at_current_commissions_and_target": ad_cap(before-commission_total-target, count, minor),
    }
    return {
        "status": "CALCULATED_SCENARIO", "evidence_label": "ESTIMATE", "input_kind": data["input_kind"],
        "site": site, "currency": currency, "currency_minor_units": minor, "sku": sku,
        "period": data["period"], "basis_note": basis_note,
        "unit": {"seller_revenue_after_refunds": money(unit_revenue, minor),
                 "noncommission_variable_costs_before_recovery": money(sum(costs.values(), ZERO), minor),
                 "inventory_recovery_credit": money(recovery, minor),
                 "noncommission_variable_costs": money(unit_cost, minor),
                 "contribution_before_commission_ads_campaign": money(unit_before_marketing, minor),
                 "allocated_campaign_costs": money(per_order_fixed, minor) if count else None,
                 "target_contribution": money(target_unit, minor)},
        "summary": summary, "cohorts": results,
        "limits": [
            "Economic rate ceilings only; verify active platform limits, rate linkage and commission protection before changing rates.",
            "Standard and Shop Ads groups must be disjoint. For ads orders without a special rate, supply the effective standard fallback rate once.",
            "All groups share the declared unit revenue, costs and refund assumptions; split different SKU, price or fulfillment economics into separate scenarios.",
            "Campaign costs are allocated by order count; this is an assumption, not marginal cost or verified acquisition attribution.",
            "Commission caps hold current ad spend fixed; ad caps hold current commissions fixed. Do not apply both maxima together.",
            "Commission caps are floored to 0.01 percentage point and bounded at 100%; this is not a platform input range or increment.",
            "Money rounds only for display; displayed group allocations may differ from totals by minor rounding amounts.",
            "No bank cash-flow forecast, accounting profit, live fee lookup, or incremental ad ROAS is calculated.",
        ],
    }


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "Duplicate JSON key")
        result[key] = value
    return result


def parse_json(source):
    def invalid_constant(_):
        raise ValueError("Non-finite JSON number")
    return json.loads(source, parse_float=Decimal, object_pairs_hook=unique_object, parse_constant=invalid_constant)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="Local JSON scenario, or - for stdin")
    args = parser.parse_args()
    try:
        if args.input == "-":
            source = sys.stdin.read()
        else:
            with open(args.input, encoding="utf-8") as handle:
                source = handle.read()
        result = calculate(parse_json(source))
    except (ValueError, TypeError, DecimalException) as error:
        print(json.dumps({"status": "HOLD", "reason": str(error)}, ensure_ascii=False))
        return 2
    except OSError:
        print(json.dumps({"status": "HOLD", "reason": "Unable to read input JSON"}))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
