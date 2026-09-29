# 供货贡献计算器

标准库 Python 3 离线工具。读取本地 JSON 或标准输入，只向终端输出 JSON；不连接账户、不修改文件、不内置平台费率。先按当前协议和订单批次整理账本，再计算情景。

## 运行与复核

在本 Skill 目录运行：

```bash
python3 scripts/wholesale_contribution.py references/example-scenario.json
python3 -m unittest discover -s scripts -p 'test_*.py' -v
```

文件名换成 `-` 可读标准输入。有效情景退出码为 0，输入缺失、未知、口径错误或文件不可读时输出 `HOLD`、退出码为 2。结果为 `CALCULATED_SCENARIO / ESTIMATE`；即使输入声明为实际账本，脚本也没有核验其真实性。

## 输入合同

以[完整合成示例](example-scenario.json)为模板。金额推荐十进制字符串；所有金额必须同币种、同 SKU、同一可售单位及同一订单批次。不能混入前台 GMV、汇总到款额、其他 SKU 或其他周期费用。缺项不能填零；只有已核实不发生或由其他方承担的费用才明确填写 0。

| 字段 | 口径 |
| --- | --- |
| `schema_version` | 整数 1 |
| `site`、`currency`、`currency_minor_units` | 市场、一个大写三字母币种及其输出小数位 0–3；脚本不校验市场资格或自动换汇 |
| `sku`、`basis_note` | 内部商品代号；输入来源、日期、假设和覆盖范围，不放个人或客户信息 |
| `input_kind` | `synthetic`、`estimate` 或 `actual`；声明不等于验证 |
| `revenue_basis` | 必须为 `supplier_wholesale_before_adjustments`：未扣下表调整项的供货单价 |
| `incident_basis` | 必须为 `residual_costs_after_allowance_and_claim_reconciliation`：已经人工排除重复扣款/成本 |
| `units`、`unit_wholesale_price` | 整数可售单位数量及正数供货单价；不是箱数、组件数或前台零售价 |
| `unit_adjustments` | 每件 `promotion_discount`、`allowances`、`refunds_and_claims`、`other_debits`、`credits`，全部显式填写 |
| `unit_costs` | 每件 `product`、`inbound`、`packaging`、`warehouse_handling`、`storage`、`supplier_paid_shipping`、`uncovered_after_sales`、`nonrecoverable_tax`、`other` |
| `unit_inventory_recovery_credit` | 每件可回收库存的合理账面价值，最多为本模型商品成本加头程；不是现金返款 |
| `fixed_costs` | 本情景固定总额：`platform_programs`、`content_and_samples`、`other`；不随件数自动扩张 |
| `ad_spend` | 同批次情景广告总额 |
| `target_unit_contribution` | 每件最低目标贡献，非负 |

`refunds_and_claims` 放收入冲减；售后人工、补件等未覆盖服务成本放 `uncovered_after_sales`。若 Allowance 已覆盖同一损失，不再完整扣第二次；若协议未覆盖，保留对应费用与凭证。`incident_basis` 只是使用者确认，脚本无法读取合同或识别同一事件。

拒绝额外字段、重复 JSON 键、布尔金额、空值、负输入、非有限数和币种对象。单项金额上限为 10¹²，件数上限为 10⁹，这是本地计算保护，不是 Wayfair 业务限制。收入调整后可以为负，损失不会被截为零。

## 公式与独立验算

设供货价为 W，促销、Allowance、返款索赔及其他扣款总和为 D，信用调整为 C，完整单位成本为 K，可回收库存价值为 I，件数为 Q，固定成本为 F，广告为 A，目标单位贡献为 T：

```text
调整后单位供货收入 R = W - D + C
单位变动成本 V = K - I
广告前总贡献 B = (R - V) × Q - F
广告后总贡献 P = B - A
达到目标贡献的广告总预算上限 = B - T × Q
理论保本 ROAS（调整后供货收入分子） = (R × Q) ÷ B
```

示例纯属虚构：20 件，供货价 200，扣款 26、信用 1，完整成本 120、可回收价值 2，固定成本 80，广告 200，目标单位贡献 30。单位收入 175、单位变动成本 118；广告前贡献 1,060，广告后贡献 **860**，每件 **43**；广告上限 **460**，供货收入口径理论保本 ROAS 为 **3.3019**。

将广告改为 460，贡献恰好为 600，达到每件 30 的目标；改为 460.01 则低于目标。广告上限是**总广告费**，不是可在当前广告费上再增加的金额。它固定销量、供货价、扣款和成本，不能预测加预算会带来多少订单。

预算向下舍入到币种最小单位，其他展示金额四舍五入。精确值用于决策；极小亏损可能显示为 `0.00` 而仍返回 `LOSS`，应提高输入精度并复核。每件上限单独向下舍入，所以每件数乘数量可能略小于总上限。

## 解释与边界

- 无销量仍保留固定费用及广告损失；无每件贡献和可用投流上限。
- 目标即使不投广告也达不到时，上限为 `null`，给出缺口；恰好可达时上限为 0，二者不同。
- 广告前贡献或收入不为正时，保本 ROAS 为 `null`，不生成无穷值或负的“可投目标”。
- 此 ROAS 分子是调整后供货收入。只有广告报表分子和成本范围完全对齐才可比较，不能直接拿零售 GMV 的面板 ROAS 作结论。
- 库存回收价值、应收和银行到账不同；固定成本范围也未必包含全部公司费用。本模型不替代现金流预测、完整会计利润或因果增量测试。
- 零费用、物流由谁承担、Allowance 覆盖、付款天数和广告资格均须逐账户验证，示例不构成平台费率或收益承诺。
