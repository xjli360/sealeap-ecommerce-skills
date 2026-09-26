# 美客多新增：119 → 144

研究开始于2026-09-26，完成资料核读和规则整理于2026-09-27。本批新增 `mercadolibre` 平台目录，共25个专项Skill：选品6、运营13、广告6。源码与方法来自在线公开资料和模型综合，没有导入本地业务Skill。

## 任务索引

| Skill | 方向 | 网络证据 |
| --- | --- | --- |
| [美客多站点与经营模式评审](mercadolibre/sealeap-mercadolibre-market-entry-route/SKILL.md) | 选品 | ML09、ML04 |
| [美客多类目需求与新品验证](mercadolibre/sealeap-mercadolibre-category-demand-validation/SKILL.md) | 选品 | ML02、ML07、ML11 |
| [美客多同款报价与目录竞争分析](mercadolibre/sealeap-mercadolibre-competitor-offer-benchmark/SKILL.md) | 选品 | ML02 |
| [美客多单位经济与现金测算](mercadolibre/sealeap-mercadolibre-unit-economics/SKILL.md) | 选品 | ML01、ML02、ML09 |
| [美客多季节需求与备货倒排](mercadolibre/sealeap-mercadolibre-seasonal-stock-planning/SKILL.md) | 选品 | ML11、ML04 |
| [美客多供应报价与样品验证](mercadolibre/sealeap-mercadolibre-supplier-sample-validation/SKILL.md) | 选品 | ML07、ML02 |
| [美客多刊登事实与本地化文案](mercadolibre/sealeap-mercadolibre-listing-localization/SKILL.md) | 运营 | ML09、ML07 |
| [美客多目录匹配与资料更正](mercadolibre/sealeap-mercadolibre-catalog-identity-corrections/SKILL.md) | 运营 | ML02、ML09 |
| [美客多变体与尺码表验收](mercadolibre/sealeap-mercadolibre-variations-sizecharts/SKILL.md) | 运营 | ML09 |
| [美客多商品图片与 Clips 验收](mercadolibre/sealeap-mercadolibre-product-visuals-clips/SKILL.md) | 运营 | ML12、ML09 |
| [美客多 Full 入仓包装与计划预检](mercadolibre/sealeap-mercadolibre-full-inbound-precheck/SKILL.md) | 运营 | ML04、ML05 |
| [美客多 Full 实收与可售对账](mercadolibre/sealeap-mercadolibre-full-receiving-reconciliation/SKILL.md) | 运营 | ML04、ML05 |
| [美客多 Full 库存、仓龄与移出决策](mercadolibre/sealeap-mercadolibre-full-inventory-aging/SKILL.md) | 运营 | ML04、ML05 |
| [美客多订单履约与交接控制](mercadolibre/sealeap-mercadolibre-fulfillment-dispatch-controls/SKILL.md) | 运营 | ML09、ML05 |
| [美客多信誉指标与异常处理](mercadolibre/sealeap-mercadolibre-reputation-incident-triage/SKILL.md) | 运营 | ML09、ML05 |
| [美客多售前问答与事实回复](mercadolibre/sealeap-mercadolibre-customer-questions-responses/SKILL.md) | 运营 | ML09、ML07 |
| [美客多退货案件与证据处理](mercadolibre/sealeap-mercadolibre-returns-case-evidence/SKILL.md) | 运营 | ML09、ML04 |
| [美客多回款、费用与退货对账](mercadolibre/sealeap-mercadolibre-payment-fee-reconciliation/SKILL.md) | 运营 | ML09、ML02、ML01 |
| [美客多知识产权与刊登限制初筛](mercadolibre/sealeap-mercadolibre-ip-policy-response/SKILL.md) | 运营 | ML10、ML09 |
| [美客多促销资格与净回款评审](mercadolibre/sealeap-mercadolibre-promotion-net-proceeds/SKILL.md) | 广告 | ML11、ML01 |
| [美客多 Product Ads 投放准备](mercadolibre/sealeap-mercadolibre-product-ads-readiness/SKILL.md) | 广告 | ML06、ML09 |
| [美客多广告组与商品映射](mercadolibre/sealeap-mercadolibre-product-ads-grouping/SKILL.md) | 广告 | ML06、ML01 |
| [美客多目标 ROAS 与预算试验](mercadolibre/sealeap-mercadolibre-roas-budget-experiment/SKILL.md) | 广告 | ML01、ML06 |
| [美客多广告归因与贡献对账](mercadolibre/sealeap-mercadolibre-ads-attribution-profit/SKILL.md) | 广告 | ML01、ML06 |
| [美客多广告曝光损失诊断](mercadolibre/sealeap-mercadolibre-ads-impression-loss-diagnosis/SKILL.md) | 广告 | ML06、ML01 |

目录身份匹配与资料更正合为一项；图片与Clips按商品表达合并。Full入仓预检、实收对账、库存仓龄具有不同输入与交付，保留独立入口。广告则分开投放资格、控制粒度、目标/预算试验、归因贡献和曝光瓶颈。

单位经济包附离线计算器与合成样例，不预置国家费率。它区分成本、确认可回收的代扣税和暂扣现金，缺失成本返回HOLD；不是银行余额或完整会计利润。

## 本批来源与读取范围

| 类别 | 数量 | 核读边界 |
| --- | ---: | --- |
| YouTube | 8 | 7条完整自动字幕；1条官方BPP视频无可导出字幕，仅核描述和约26秒画面 |
| 小红书 | 1 | 登录后的完整可见笔记正文；赞/收藏/评论合计达到门槛，非独立人数 |
| 抖音 | 1 | 登录页面的说明、AI章节摘要与作者披露的样本范围；不是人工逐字稿 |
| 官方规则 | 27 | 独立的R50–R76，用于规则校正，不混算互动来源 |

中文、西语、葡语和英语资料均纳入检索。来源中多条视频来自同一作者，不能宣称10位独立专家验证。指标为内容级浏览器观察值，公开登记只保留区间；个人原帖、账号、视频ID、精确计数和原始材料不进入公开库。

## 采用与排除

- 小红书一篇高收藏上品内容明确支持照搬他人刊登，排除；另一篇SOP仅保留需求—成本—供应验证的顺序，去掉固定阈值和成功率。
- 目录视频的虚假改绑、保证全赢和未注册品牌可随意使用说法未采用。
- 退货视频中劝阻投诉、自动退固定比例等核心策略未采用；采用当期官方案件和沟通规则。
- 行业文章的作者累计曝光不能代替文章阅读量；未达到内容级门槛的文章不计入来源。
- 本批检索到的相关GitHub仓库未达既定100 Stars门槛，未把它们的源码或文本纳入。
- B站视频有合格传播量，但本次登录态失效、正文停在试看/登录提示，未按完整课程计入。公众号原文没有获得可核读的新证据，也不以转载代替。

检索覆盖多个渠道，不声称穷尽全网、通读所有视频或验证每位作者的经营业绩。

## 关键规则校正

- 国家、本土/跨境模式、直邮/Full与账户控制权分别识别，不能套用另一国家的成本与功能。
- 目录与普通刊登可共享库存；暂停一条不保证另一条停止销售。资料更正提交、审核和前台应用是不同状态。
- Full不全面免除质量投诉；入仓标识、承运签收、实收和可售分别验收。
- Product Ads按当前广告组粒度核验，使用目标ROAS与实际能力；旧目标ACOS配置和旧Ads资源不能直接照搬。
- 平均日预算不一定是单日硬上限；归因收入、全量收入和利润分开计算。
- 2026-09-22促销说明的部分Net Proceeds功能标为Coming soon；不能当作全量已开放。子卖家身份、定价模型和自动活动的网页管理限制都需核验。
- 某些角色（如Model 6）没有对应Questions/退货API能力，缺权限不能解释成零业务量或伪造执行成功。

## 许可与验收

继续使用MIT；只许可本项目的原创整理和代码，不转移原始视频、文章或商标的权利。每包独立携带许可、参考与调用元数据。25包共附75个合成案例，作为文本审阅材料，不是店铺实测业绩。

验证结果见[验证记录](VALIDATION.md)。本次从公开版本建立独立工作区，原主目录另一批未提交草稿未纳入此次发布。
