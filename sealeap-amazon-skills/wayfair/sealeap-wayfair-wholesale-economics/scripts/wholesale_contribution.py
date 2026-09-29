#!/usr/bin/env python3
"""Offline supplier-wholesale contribution scenarios; no embedded Wayfair fees."""
import argparse
from decimal import Decimal, DecimalException, ROUND_HALF_UP, ROUND_DOWN, localcontext
import json
import re
import sys

ZERO=Decimal(0)
LIMIT=Decimal('1000000000000')
COSTS={'product','inbound','packaging','warehouse_handling','storage','supplier_paid_shipping','uncovered_after_sales','nonrecoverable_tax','other'}
ADJUSTMENTS={'promotion_discount','allowances','refunds_and_claims','other_debits','credits'}
FIXED={'platform_programs','content_and_samples','other'}
ROOT={'schema_version','site','currency','currency_minor_units','sku','input_kind','basis_note','revenue_basis','incident_basis','units','unit_wholesale_price','unit_adjustments','unit_costs','unit_inventory_recovery_credit','fixed_costs','ad_spend','target_unit_contribution'}


def require(ok,message):
    if not ok:raise ValueError(message)


def keys(value,expected,label):
    require(isinstance(value,dict) and set(value)==expected,label+': missing or unsupported fields')


def number(value,label,maximum=LIMIT):
    require(value is not None and type(value) in (str,int,float,Decimal),label+': unknown is not zero; use one currency')
    try:d=Decimal(str(value))
    except DecimalException:raise ValueError(label+': invalid number') from None
    require(d.is_finite() and ZERO<=d<=maximum,label+': require a finite nonnegative amount in range')
    return d


def amounts(value,expected,label):
    keys(value,expected,label)
    return {key:number(value[key],label+'.'+key) for key in sorted(expected)}


def money(value,minor,rounding=ROUND_HALF_UP):
    return format(value.quantize(Decimal(1).scaleb(-minor),rounding=rounding),'f')


def calculate(data):
    with localcontext() as context:
        context.prec=40
        return _calculate(data)


def _calculate(data):
    keys(data,ROOT,'scenario')
    require(type(data['schema_version']) is int and data['schema_version']==1,'schema_version: expected 1')
    for field in ('site','sku','basis_note'):
        require(isinstance(data[field],str) and bool(data[field].strip()),field+': required')
    require(isinstance(data['currency'],str) and bool(re.fullmatch('[A-Z]{3}',data['currency'])),'currency: one uppercase currency code required')
    minor=data['currency_minor_units']
    require(type(minor) is int and 0<=minor<=3,'currency_minor_units: expected 0 to 3')
    require(data['input_kind'] in ('synthetic','estimate','actual'),'input_kind: required declaration')
    require(data['revenue_basis']=='supplier_wholesale_before_adjustments','revenue_basis: retail GMV and already-net payouts are not accepted')
    require(data['incident_basis']=='residual_costs_after_allowance_and_claim_reconciliation','incident_basis: reconcile allowance, revenue claims and residual service costs first')
    units=number(data['units'],'units',Decimal(1000000000))
    require(units==units.to_integral_value(),'units: whole sellable units required')
    price=number(data['unit_wholesale_price'],'unit_wholesale_price')
    require(price>0,'unit_wholesale_price: positive supplier quote required')
    adjustments=amounts(data['unit_adjustments'],ADJUSTMENTS,'unit_adjustments')
    costs=amounts(data['unit_costs'],COSTS,'unit_costs')
    fixed=amounts(data['fixed_costs'],FIXED,'fixed_costs')
    recovery=number(data['unit_inventory_recovery_credit'],'unit_inventory_recovery_credit')
    require(recovery<=costs['product']+costs['inbound'],'inventory recovery exceeds modeled product and inbound cost')
    ads=number(data['ad_spend'],'ad_spend')
    target=number(data['target_unit_contribution'],'target_unit_contribution')
    debits=sum((v for k,v in adjustments.items() if k!='credits'),ZERO)
    retained=price-debits+adjustments['credits']
    variable=sum(costs.values(),ZERO)-recovery
    fixed_total=sum(fixed.values(),ZERO)
    revenue=retained*units
    before_ads=(retained-variable)*units-fixed_total
    after_ads=before_ads-ads
    target_total=target*units
    available=before_ads-target_total
    feasible=units>0 and available>=0
    if not units:decision='NO_SALES'
    elif after_ads<0:decision='LOSS'
    elif after_ads<target_total:decision='BELOW_TARGET'
    else:decision='TARGET_MET'
    return {
        'status':'CALCULATED_SCENARIO','evidence_label':'ESTIMATE','input_kind':data['input_kind'],
        'site':data['site'],'currency':data['currency'],'sku':data['sku'],'units':int(units),'basis_note':data['basis_note'],
        'unit':{'wholesale_price':money(price,minor),'debits':money(debits,minor),'credits':money(adjustments['credits'],minor),
                'adjusted_supplier_revenue':money(retained,minor),'variable_cost_after_inventory_recovery':money(variable,minor),
                'inventory_recovery_credit':money(recovery,minor),
                'fixed_cost_allocation':money(fixed_total/units,minor) if units else None,
                'contribution_after_ads':money(after_ads/units,minor) if units else None},
        'totals':{'gross_wholesale_revenue':money(price*units,minor),'adjusted_supplier_revenue':money(revenue,minor),
                  'variable_costs':money(variable*units,minor),'fixed_costs':money(fixed_total,minor),'ad_spend':money(ads,minor),
                  'contribution_before_ads':money(before_ads,minor),'contribution_after_ads':money(after_ads,minor),
                  'target_contribution':money(target_total,minor),'target_gap':money(after_ads-target_total,minor),
                  'decision':decision},
        'ad_budget_at_target':{'feasible':feasible,'max_total_spend':money(available,minor,ROUND_DOWN) if feasible else None,
                               'max_per_sellable_unit':money(available/units,minor,ROUND_DOWN) if feasible else None,
                               'shortfall_before_ads':money(max(-available,ZERO),minor),
                               'reason':'no_sales' if not units else 'target_unreachable_even_without_ads' if available<0 else 'fixed_volume_scenario_only'},
        'theoretical_break_even_roas_on_adjusted_supplier_revenue':money(revenue/before_ads,4) if units>0 and revenue>0 and before_ads>0 else None,
        'limits':[
            'All adjustments and costs must refer to the same SKU, sellable unit, currency and order cohort.',
            'Allowance coverage is an input assertion, not an automatic contract or duplicate-charge audit.',
            'Only residual service costs go in uncovered_after_sales; revenue reversals belong in refunds_and_claims.',
            'Inventory recovery is an accounting value, not cash received.',
            'Ad budget holds volume, price, deductions and costs fixed; it is not a prediction of incremental demand.',
            'Theoretical ROAS uses adjusted supplier revenue, not customer retail GMV or an unverified advertising-report denominator.',
            'No live fee lookup, bank cash-flow forecast, complete accounting profit or account mutation is performed.'
        ]
    }


def unique_object(pairs):
    result={}
    for key,value in pairs:
        require(key not in result,'Duplicate JSON key')
        result[key]=value
    return result


def parse_json(source):
    def reject(_):raise ValueError('Non-finite JSON number')
    return json.loads(source,parse_float=Decimal,object_pairs_hook=unique_object,parse_constant=reject)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('input',help='Local JSON scenario, or - for stdin');args=parser.parse_args()
    try:
        if args.input=='-':source=sys.stdin.read()
        else:
            with open(args.input,encoding='utf-8') as handle:source=handle.read()
        result=calculate(parse_json(source))
    except (ValueError,TypeError,DecimalException) as error:
        print(json.dumps({'status':'HOLD','reason':str(error)},ensure_ascii=False));return 2
    except OSError:
        print(json.dumps({'status':'HOLD','reason':'Unable to read input JSON'}));return 2
    print(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False));return 0


if __name__=='__main__':raise SystemExit(main())
