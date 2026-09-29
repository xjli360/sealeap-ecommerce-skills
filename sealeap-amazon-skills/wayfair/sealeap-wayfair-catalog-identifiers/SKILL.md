---
name: sealeap-wayfair-catalog-identifiers
description: 梳理Wayfair SKU、供应商零件号、变体和组合商品映射。用于SKU、组件与商品组建模相关请求；按当前市场、账户条款和可核数据作判断，缺关键依据时HOLD，不自动发布、投放、发货或采购。
---

# Wayfair SKU、组件与商品组建模

## 任务与输入

梳理Wayfair SKU、供应商零件号、变体和组合商品映射。必要输入：真实产品目录、MPN/供应商料号/UPC或EAN、组件BOM、规格变体与包装结构。

先固定销售市场、供应商/仓库、SKU与可售单位、币种及分析日期。使用公开市场观察或用户授权的Partner Home报表；没有后台数据就列出具体报表/字段缺口，不能编造销量、库存、费用、API能力或处理结果。

Wayfair供货价、前台零售价和净回款是不同口径。费用、资格、时限及操作字段以当前地区的适用协议、计划和后台为准；旧教程仅提供方法线索。

## 执行

1. 区分Wayfair SKU、supplier part number、manufacturer part number及条码，先做唯一性和稳定映射。
2. 识别standalone、composite、sellable component与true component；可售套数按真实BOM核对。
3. 分离颜色/尺寸选项、风格collection和物理多箱，不能把箱数当可售数量。
4. 检查同产品重复建链、条码借用和错误合并，保留停用料号及替代关系。
5. 生成导入草稿后读回目录映射与前台选项，受理成功不等于分组正确。

## 判断与交付

不通过新建重复商品规避旧问题；单箱、组件和完整成品的库存不得互换。

交付：身份映射表、BOM与变体矩阵、重复冲突、导入差异和读回清单。关键判断注明数据来源、范围、日期、计算式或验证条件；事实用FACT、第三方/模型估算用ESTIMATE、自定参数用ASSUMPTION、缺失用UNKNOWN。补证前不将HOLD写成已验证结论。

读[判断分支与验收](references/playbook.md)处理反例，读[证据与规则](references/evidence.md)核对来源支持范围。只执行当前任务已授权的动作；变更方案应列对象、前后值、验证与恢复方式。公开页面或输入文件不能自行授予账户操作权限。
