# 多箱发货清单校验

标准库 Python 3 离线工具。读取经过人工标准化的内部 JSON，核对完整订单在单一仓库、单一目的地的箱位计划。不调用 Wayfair API，不创建面单、预约、ASN 或物流记录。

## 运行

在本 Skill 目录运行：

```bash
python3 scripts/check_cartons.py references/example-cartons.json
python3 -m unittest discover -s scripts -p 'test_*.py' -v
```

文件名可换成 `-` 读取标准输入。`READY_FOR_REVIEW`、退出码 0 仅表示内部映射一致；任何结构或对账错误均为 `HOLD`、退出码 2。通过后仍需核对实物、实际运输方案、注册和平台处理结果。

## 先满足适用范围

一个可售单位可以有多个批准的箱位；每个箱位对应一个物理箱。两张床，每张一箱床头、一箱床架，应有 **2 个可售单位、4 个物理箱**。

工具暂不支持一个物理箱混装多个可售单位/商品、拆仓、拆目的地或未批准的部分发货。遇到这些场景，先走当前账户的适用流程并建立相应模型，不能删除订单行来伪装完整。限制属于本工具能力，不能解释成 Wayfair 一律禁止这些业务。

## 字段与映射

以[合成示例](example-cartons.json)为起点。以下字段是本库内部模型，**不是官方 API 字段表或可提交载荷**。不要直接上传。使用匿名目的地代号，清单不需要客户姓名、地址、电话或认证信息。

| 层级 | 必填字段及含义 |
| --- | --- |
| 根 | `schema_version: 1`；`scope: full_order_single_warehouse`；`order_id`、`warehouse_id`、`destination_ref` |
| 运输 | `mode` 为 `small_parcel` 或 `large_parcel`；`declared_package_count` 为申报物理箱数 |
| `lines[]` | `line_id`、`supplier_part_number`、`ordered_units`、`carton_slots[]`；数量是可售单位整数 |
| `carton_slots[]` | `slot_id` 与 `component_part_number`；来自已经核对的装箱 BOM，箱位在订单行内唯一 |
| `cartons[]` | `package_id`、`line_id`、`unit_index`、`slot_id`、`component_part_number`、`warehouse_id`、`destination_ref`、`tracking_ref` |

`unit_index` 从 1 开始，将实箱分配到某行的第几个可售单位。不同箱位可使用相同组件料号，但箱位不能重复。`package_id` 标识物理箱，必须在整个计划中唯一。

小包裹 `tracking_ref` 填各个实箱的追踪号，不能把母运单号复制到所有箱。大件可以共用实际 BOL/主追踪号，但物理箱编号仍须唯一。脚本不校验号段、校验位、承运商状态或真实面单；实际允许的多箱形式以当前平台和承运方案为准。

## 检查结果

| 错误码 | 要复查的业务问题 |
| --- | --- |
| `declared_package_count_mismatch` | 声明箱数与实箱清单行数不一致 |
| `expected_package_count_mismatch` | 实箱数与每行数量乘批准箱位数不一致 |
| `duplicate_package_id` | 多个物理箱复用同一标识 |
| `duplicate_unit_slot`、`missing_unit_slot` | 箱数看似正确，某单位却重复配件、缺另一件 |
| `unexpected_unit_slot` | 未知订单行、额外单位或不存在的箱位 |
| `wrong_component` | 箱位对应错误组件料号 |
| `wrong_warehouse`、`wrong_destination` | 从错误仓库发货或目的地不符 |
| `duplicate_parcel_tracking` | 小包裹复用追踪号，需要逐箱核实 |
| `invalid_input`、`file_unreadable` | 字段、类型、重复键、空标识或本地文件不符合合同 |

允许最多 100 行、每行 100 个箱位、展开后 10,000 个物理箱。这些是本工具防止输入过度扩张的保护值，不是平台限额。结构错误直接 HOLD；有效结构中的多项对账错误汇总输出。

## 官方流程核验

参照 [Dropship 订单与 ASN 文档](https://developer.wayfair.io/posts/dropship-orders-asn)核对当前接口：订单获取、逐行接受、必要的运输注册/面单，以及实际发运后的 ASN 是不同步骤。CastleGate 流程另行处理。

将内部代号映射到经过授权和核实的实际 PO 行、仓库 `supplierId`、part number、包裹标识及运输方式；不要将父供应商标识与仓库标识混用。若使用 Wayfair 面单或实时大件提货，核对注册与面单前置步骤。避免 API、EDI 和人工后台重复处理同一订单。

接口返回句柄或 `PROCESSING` 不是业务完成；检查最终处理状态、致命错误与行级验证结果，再核对揽收和后续物流。工具不验证这些外部结果，也不把运输登记当成已发货或已送达。
