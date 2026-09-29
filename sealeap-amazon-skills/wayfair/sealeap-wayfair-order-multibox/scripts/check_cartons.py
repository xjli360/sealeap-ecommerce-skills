#!/usr/bin/env python3
"""Check a normalized full-order carton plan; not a Wayfair API payload or label."""
import argparse
import json
import sys

ROOT={'schema_version','scope','order_id','warehouse_id','destination_ref','mode','declared_package_count','lines','cartons'}
LINE={'line_id','supplier_part_number','ordered_units','carton_slots'}
SLOT={'slot_id','component_part_number'}
CARTON={'package_id','line_id','unit_index','slot_id','component_part_number','warehouse_id','destination_ref','tracking_ref'}


def require(ok,message):
    if not ok:raise ValueError(message)


def keys(value,expected,label):
    require(isinstance(value,dict) and set(value)==expected,label+': missing or unsupported fields')


def text(value,label):
    require(isinstance(value,str) and bool(value.strip()),label+': nonempty identifier required')
    require(value==value.strip(),label+': remove surrounding whitespace explicitly')
    return value


def integer(value,label,minimum=1,maximum=10000):
    require(type(value) is int and minimum<=value<=maximum,label+': integer outside supported range')
    return value


def check(data):
    keys(data,ROOT,'plan')
    require(type(data['schema_version']) is int and data['schema_version']==1,'schema_version: expected 1')
    require(data['scope']=='full_order_single_warehouse','scope: only full-order, single-warehouse plans are supported')
    for field in ('order_id','warehouse_id','destination_ref'):text(data[field],field)
    require(data['mode'] in ('small_parcel','large_parcel'),'mode: unsupported')
    declared=integer(data['declared_package_count'],'declared_package_count',0)
    require(isinstance(data['lines'],list) and 1<=len(data['lines'])<=100,'lines: expected 1 to 100 order lines')
    require(isinstance(data['cartons'],list) and len(data['cartons'])<=10000,'cartons: expected array within local size limit')
    expected={};line_ids=set()
    for line in data['lines']:
        keys(line,LINE,'line')
        lid=text(line['line_id'],'line_id');text(line['supplier_part_number'],'supplier_part_number')
        require(lid not in line_ids,'line_id: duplicate');line_ids.add(lid)
        units=integer(line['ordered_units'],'ordered_units')
        slots=line['carton_slots'];require(isinstance(slots,list) and 1<=len(slots)<=100,'carton_slots: expected 1 to 100 slots')
        require(len(expected)+units*len(slots)<=10000,'expected carton count exceeds local limit')
        slot_map={}
        for slot in slots:
            keys(slot,SLOT,'slot');sid=text(slot['slot_id'],'slot_id');part=text(slot['component_part_number'],'component_part_number')
            require(sid not in slot_map,'slot_id: duplicate within line');slot_map[sid]=part
        for unit in range(1,units+1):
            for sid,part in slot_map.items():expected[(lid,unit,sid)]=part
    errors=[];seen_slots=set();package_ids=set();tracking=set()
    if declared!=len(data['cartons']):errors.append({'code':'declared_package_count_mismatch'})
    if len(data['cartons'])!=len(expected):errors.append({'code':'expected_package_count_mismatch'})
    for carton in data['cartons']:
        keys(carton,CARTON,'carton')
        for field in CARTON-{'unit_index'}:text(carton[field],'carton.'+field)
        integer(carton['unit_index'],'unit_index')
        pid=carton['package_id'];key=(carton['line_id'],carton['unit_index'],carton['slot_id'])
        if pid in package_ids:errors.append({'code':'duplicate_package_id','package_id':pid})
        package_ids.add(pid)
        if key in seen_slots:errors.append({'code':'duplicate_unit_slot','package_id':pid})
        seen_slots.add(key)
        if key not in expected:errors.append({'code':'unexpected_unit_slot','package_id':pid})
        elif expected[key]!=carton['component_part_number']:errors.append({'code':'wrong_component','package_id':pid})
        if carton['warehouse_id']!=data['warehouse_id']:errors.append({'code':'wrong_warehouse','package_id':pid})
        if carton['destination_ref']!=data['destination_ref']:errors.append({'code':'wrong_destination','package_id':pid})
        if data['mode']=='small_parcel' and carton['tracking_ref'] in tracking:errors.append({'code':'duplicate_parcel_tracking','package_id':pid})
        tracking.add(carton['tracking_ref'])
    for lid,unit,sid in sorted(set(expected)-seen_slots):errors.append({'code':'missing_unit_slot','line_id':lid,'unit_index':unit,'slot_id':sid})
    return {'ok':not errors,'status':'HOLD' if errors else 'READY_FOR_REVIEW','order_id':data['order_id'],
            'expected_cartons':len(expected),'provided_cartons':len(data['cartons']),'errors':errors,
            'boundary':'Internal plan consistency only. Does not prove physical contents, label validity, program eligibility, carrier acceptance, API processing or delivery.'}


def unique_object(pairs):
    result={}
    for key,value in pairs:
        require(key not in result,'Duplicate JSON key');result[key]=value
    return result


def parse_json(source):
    def reject(_):raise ValueError('Non-finite JSON number')
    return json.loads(source,object_pairs_hook=unique_object,parse_constant=reject)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('input',help='Normalized local JSON, or - for stdin');args=parser.parse_args()
    try:
        if args.input=='-':source=sys.stdin.read()
        else:
            with open(args.input,encoding='utf-8') as handle:source=handle.read()
        result=check(parse_json(source))
    except (ValueError,TypeError) as error:
        result={'ok':False,'status':'HOLD','errors':[{'code':'invalid_input','reason':str(error)}]}
    except OSError:result={'ok':False,'status':'HOLD','errors':[{'code':'file_unreadable'}]}
    print(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False));return 0 if result['ok'] else 2


if __name__=='__main__':raise SystemExit(main())
