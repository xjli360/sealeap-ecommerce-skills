# 2026-10-16 规则与能力更新

基线为公开提交 `e1a39e197193a07a044ca80191bf541eae17f4a5`。新增1个Skill、补强26个原有Skill，全库194→195；Shopify27→28，其余七个平台数量不变。新增R112–R131共20条官方核查记录，E类来源仍81个。核查记录包含对旧页面的版本复核，不声称新增20个独立信源。

## 已落实

新增[Shopify AI销售渠道可售与数据验收](shopify/sealeap-shopify-agentic-storefront-audit/SKILL.md)，检查Catalog及渠道资格、数据映射、购买路径和B2B排除。使用官方R与原创M，不新增或伪造E互动数据。

以下现有技能各自附带可独立复制的规则补充，不跨包依赖：

| 技能 | 更新内容 | 官方记录 |
| --- | --- | --- |
| [sealeap-tiktokshop-store-operations](tiktokshop/sealeap-tiktokshop-store-operations/SKILL.md) | 美国SPS版本与欧盟规则分支 | R112, R127 |
| [sealeap-tiktokshop-fulfillment-service](tiktokshop/sealeap-tiktokshop-fulfillment-service/SKILL.md) | 履约SLA、VTR与新版SPS | R112, R115, R127 |
| [sealeap-tiktokshop-returns-feedback](tiktokshop/sealeap-tiktokshop-returns-feedback/SKILL.md) | POD取消与FBT退货责任 | R114 |
| [sealeap-tiktokshop-listing-localization](tiktokshop/sealeap-tiktokshop-listing-localization/SKILL.md) | AI商品图片与欧盟资料验收 | R113, R127 |
| [sealeap-tiktokshop-content-product-fit](tiktokshop/sealeap-tiktokshop-content-product-fit/SKILL.md) | 演示真实性与AI视觉检查 | R113 |
| [sealeap-tiktokshop-unit-economics](tiktokshop/sealeap-tiktokshop-unit-economics/SKILL.md) | 欧盟账期与现金情景核验 | R127 |
| [sealeap-shopify-product-feed](shopify/sealeap-shopify-product-feed/SKILL.md) | Google商品接口退役排错 | R116 |
| [sealeap-shopify-google-shopping](shopify/sealeap-shopify-google-shopping/SKILL.md) | 商品广告的数据源迁移影响 | R116 |
| [sealeap-shopify-store-operations](shopify/sealeap-shopify-store-operations/SKILL.md) | AI销售渠道运营验收 | R117, R118 |
| [sealeap-shopify-technical-seo](shopify/sealeap-shopify-technical-seo/SKILL.md) | AI抓取与Catalog分发的边界 | R118 |
| [sealeap-etsy-etsy-ads-tests](etsy/sealeap-etsy-etsy-ads-tests/SKILL.md) | 逐Listing策略与测试 | R120 |
| [sealeap-etsy-advertising](etsy/sealeap-etsy-advertising/SKILL.md) | 广告策略控制项更新 | R120 |
| [sealeap-etsy-market-keywords](etsy/sealeap-etsy-market-keywords/SKILL.md) | Marketplace Insights取数与判读 | R121 |
| [sealeap-etsy-product-selection](etsy/sealeap-etsy-product-selection/SKILL.md) | 官方搜索证据与选品边界 | R121 |
| [sealeap-etsy-listing-seo](etsy/sealeap-etsy-listing-seo/SKILL.md) | 标题可读性与AI建议复核 | R122 |
| [sealeap-etsy-reserve-cashflow](etsy/sealeap-etsy-reserve-cashflow/SKILL.md) | 新版余额与打款状态桥 | R123 |
| [sealeap-walmart-wfs-economics](walmart/sealeap-walmart-wfs-economics/SKILL.md) | 美国WFS旺季与超龄费用情景 | R124 |
| [sealeap-walmart-inventory-planning](walmart/sealeap-walmart-inventory-planning/SKILL.md) | 旺季可售与仓龄行动 | R124, R125 |
| [sealeap-walmart-wfs-receiving-resolution](walmart/sealeap-walmart-wfs-receiving-resolution/SKILL.md) | 旺季收货缓冲与争议时钟 | R125 |
| [sealeap-walmart-returns-recovery](walmart/sealeap-walmart-returns-recovery/SKILL.md) | 美国节日退货与跨年现金 | R126 |
| [sealeap-mercadolibre-promotion-net-proceeds](mercadolibre/sealeap-mercadolibre-promotion-net-proceeds/SKILL.md) | B2B多件价迁移前核验 | R128 |
| [sealeap-ozon-unit-economics](ozon/sealeap-ozon-unit-economics/SKILL.md) | 会员与临时仓储的合同情景 | R130, R131 |
| [sealeap-ozon-fulfillment-choice](ozon/sealeap-ozon-fulfillment-choice/SKILL.md) | FBO优惠与入仓批次资格 | R131 |
| [sealeap-ozon-settlement-audit](ozon/sealeap-ozon-settlement-audit/SKILL.md) | 会员续订与仓储扣款对账 | R130, R131 |
| [sealeap-wayfair-attributes-localization](wayfair/sealeap-wayfair-attributes-localization/SKILL.md) | 批量商品修改与变更日志验收 | R129 |
| [sealeap-wayfair-catalog-identifiers](wayfair/sealeap-wayfair-catalog-identifiers/SKILL.md) | 父SKU与部件编辑范围 | R129 |

## 15项候选的处理结果

- 1–10：落实SPS、AI图片、POD/FBT售后、Merchant API、Etsy逐商品广告策略、Shopify AI渠道、Etsy官方关键词、标题、资金页以及WFS旺季。Walmart节日退货只有官方索引完整片段，因此保留类目/模式例外待核。
- 11（TikTok EU/UK）：落实制造商资料、账期、OTDR的核验入口和数据清单。只有官方索引可读，不输出完整法规结论、确定到账日或处罚结果；未将PID/EPR的未核细节写成可执行规则。
- 12（美客多B2B多件价）：加入迁移预告、资格/站点、净价例外及草稿验收；直接页面受限，端点执行保持待核。
- 13（OZON）：加入地区/合同、会员续订和优惠批次对账；保留MPstats必需输入，不填跨地区通用费率。
- 14（Wayfair）：加入批量字段变更、父SKU/部件和审计日志验收；先确认账户实际可用能力，历史Beta/预告不视作已开放。
- 15（上游）：旧上游主分支仍为已记录提交，无需重复合并；另一候选仓库README声明专有许可，未取得MIT再分发授权，不导入文件、代码或安装其程序。根目录上游审阅记录保留核验信息。

## 日期与证据强度

[规则登记](assets/rule-refresh-20261016.json)逐条记录URL、核读日期、版本、读取范围、限制和使用包。只引用公开平台/开发者资料，无商家凭证、个人原帖、课程原文或经营数据。

- 美国SPS：同一知识ID不同URL返回过不同版本；采用10月15日正文中的10月16日计划，不把计划当账户实际切换证明。
- Google：退役、渐进410、最终停机是不同阶段；第三方连接器迁移责任与自建集成分开。
- Etsy：标题词数为建议；广告策略资格不授权自动加预算；资金页面按实际版本映射。
- 费率与时效：记录观察快照和适用范围，不宣称永久固定。临时优惠不进入长期利润基线。
- 索引可读不等于完整原文已核读；受阻部分通过补证清单继续工作，不补造规则或后台结果。

本批流程、决策矩阵和合成案例是SeaLeap的M设计，不证明平台认证、卖家收益或真实后台操作。验证结果见[验证记录](VALIDATION.md)。
