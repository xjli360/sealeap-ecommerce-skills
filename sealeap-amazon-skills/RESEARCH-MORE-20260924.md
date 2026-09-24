# 本轮新增：公开库100 → 114

研究日期：2026-09-24。本批在独立工作区完成，未导入主目录中另一批未提交草稿；它们保留原样。本版新增14个专项Skill，补强3个现有入口。

## 新增任务

| Skill | 新增判断边界 | 网络证据 |
| --- | --- | --- |
| [Shopify 订阅上线与购买路径验收](shopify/sealeap-shopify-subscription-launch-audit/SKILL.md) | 订阅计划、一次性购买选项、顾客自助管理和上线前验收；不处理通用邮件营销 | A01 |
| [Shopify 续费失败与合同状态诊断](shopify/sealeap-shopify-subscription-renewal-recovery/SKILL.md) | 续费失败、库存不足、重试耗尽、暂停/取消与重复通知；不代替支付争议处理 | A01 |
| [Shopify 组合商品库存与履约验收](shopify/sealeap-shopify-bundle-fulfillment-audit/SKILL.md) | 固定组合、多件装的组件库存、渠道兼容、拆单与退货；不做组合优惠创意 | A02、A03 |
| [Shopify 主题许可与恢复准备](shopify/sealeap-shopify-theme-license-recovery/SKILL.md) | 主题授权告警、跨店主题迁移、草稿副本与恢复验收；不编写主题代码或自动关闭商店 | A09 |
| [Shopify 营销组合建模数据准备](shopify/sealeap-shopify-mmm-data-readiness/SKILL.md) | 多渠道MMM建模前的数据适用性、口径和可识别性审计；不输出尚未拟合的渠道ROI | A10 |
| [Shopify 边际收益与预算方案评审](shopify/sealeap-shopify-marginal-budget-review/SKILL.md) | 已有营销模型的响应曲线、预算约束和可执行性复核；不替代模型训练或直接投放 | A10 |
| [Etsy 储备金与可用现金诊断](etsy/sealeap-etsy-reserve-cashflow/SKILL.md) | Payment Reserve、在途确认、可用余额和生产资金缺口；不处理银行转账或一般利润定价 | A08 |
| [Etsy 休店与恢复接单验收](etsy/sealeap-etsy-vacation-restart/SKILL.md) | 主动休店、恢复接单、旧单责任与费用检查；不预测恢复排名或保证出单时间 | A13 |
| [eBay 国际配送范围与政策变更](ebay/sealeap-ebay-international-shipping-controls/SKILL.md) | eIS参与、国家排除、账户/政策/刊登作用范围及批量变更验收；不替代一般运费定价 | A06 |
| [eBay 合并运费与购物篮验收](ebay/sealeap-ebay-combined-shipping-audit/SKILL.md) | 追加件运费、跨刊登合并规则、付款前发票和付款后差额；不自动退款 | A12 |
| [Walmart WFS 包装与标签预检](walmart/sealeap-walmart-wfs-packaging-labels/SKILL.md) | 入仓可售单元包装、单品/收货/承运标签及交接准备；不创建或购买物流服务 | A04 |
| [Walmart WFS 箱内明细与数量核对](walmart/sealeap-walmart-wfs-box-reconciliation/SKILL.md) | 装箱表、目的仓、唯一收货标签及计划数量对账；附离线JSON核对脚本 | A04 |
| [Walmart WFS 收货差异与处理准备](walmart/sealeap-walmart-wfs-receiving-resolution/SKILL.md) | Delivered后未可售、收货未完成、缺少数量和争议材料；不保证赔付 | A04 |
| [TikTok Shop 商用音乐与跨平台素材验收](tiktokshop/sealeap-tiktokshop-commercial-audio-clearance/SKILL.md) | 带货视频、品牌合作、广告音轨及跨平台再利用的许可核对；不提供侵权规避技巧 | A14 |

WFS箱内核对另附离线脚本和合成输入合同，检查数量、目的仓、未知商品、重复箱号/收货标签；不生成平台标签、不创建发货、不验证实际箱内实物。

## 补强的既有入口

- Shopify复购与组合：增加收益之外的组件库存、渠道兼容和部分退货检查。
- eBay配送政策：增加国际项目、目的地作用范围与付款前后合并运费的区别。
- TikTok达人brief与权利：把画面与音轨许可分开，增加跨平台版本核验。

## 证据质量

新增11个证据单元：YouTube 7、Shopify社区2、B站及关联作者原文1、MIT开源仓库1。7个视频均核读了与视频ID对应的文字稿；自动字幕可能有错误，规则另用12项当前官方资料校正。

社区和B站计数为搜索索引快照，YouTube为本次浏览器展示值，开源仓库指标为公开API快照。一个YouTube案例页面标为未列出，经公开检索链接可访问；只提炼运营段落，原文与身份不公开。GitHub指标只属于整个仓库，不拆成文档或Skill的互动。

没有采用只见标题/目录的高播放材料，也没有因为互动过关就采纳全部说法。剔除的内容包括无证据“内部黑名单”、特殊申诉服务保证、强制替换工具及绕过访问限制的要求、固定催款重试、固定解冻承诺和单个恢复出单案例的因果推断。

视频连播可能更换内容。本轮出现过一次导出ID与预期不一致，该文字稿未用于原视频；纳入的7份文字稿逐一核对ID。没有用“导出成功”代替来源身份核验。

## 许可和隐私

继续采用MIT；新增Robyn开源方法的Meta组织版权完整保留。个人社媒姓名、账号、原帖URL、精确计数、原文和字幕位于仓库外受限审计包，不进入GitHub。未读取私人消息或商户后台；未处理CAPTCHA或绕过公众号访问限制。

## 验证

见 [验证记录](VALIDATION.md)。格式、映射、源码与离线脚本验证不等于真实店铺收益、发货接收或模型因果效果验证。

