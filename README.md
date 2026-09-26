<div align="center">
  <p><a href="https://sealeap.cn"><img src="assets/sealeap-logo.png" width="116" alt="SeaLeap Logo" /></a></p>
  <h1>SeaLeap eCommerce Skills</h1>
  <p><strong>把六大电商平台的公开经验，整理成可以交给 AI Agent 执行的工作流。</strong></p>
  <p>Shopify · Etsy · eBay · TikTok Shop · Walmart · Mercado Libre<br/>从选品与利润，到商品、内容、履约、广告与归因。</p>
  <p>
    <a href="https://sealeap.cn/"><img src="https://img.shields.io/badge/Website-sealeap.cn-0ea5e9?style=for-the-badge" alt="SeaLeap 官网" /></a>
    <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge" alt="MIT License" /></a>
    <img src="https://img.shields.io/badge/Skills-144-00a8e1?style=for-the-badge" alt="144 Skills" />
    <img src="https://img.shields.io/badge/Platforms-6-8b5cf6?style=for-the-badge" alt="6 Platforms" />
    <img src="https://img.shields.io/badge/Free-100%25-22c55e?style=for-the-badge" alt="完全免费" />
    <a href="https://github.com/xjli360/sealeap-ecommerce-skills/stargazers"><img src="https://img.shields.io/github/stars/xjli360/sealeap-ecommerce-skills?style=for-the-badge&logo=github" alt="GitHub stars" /></a>
  </p>
  <p><a href="#项目目标">项目目标</a> · <a href="#技能目录">技能目录</a> · <a href="#开始使用">开始使用</a> · <a href="#来源与质量">来源与质量</a> · <a href="#免费开源">免费开源</a></p>
</div>

## 项目目标

让电商知识成为可复用的判断与操作能力。每个 Skill 明确适用任务、必要输入、处理步骤、决策条件、交付物和容易误判的场景，帮助卖家和 Agent 从“知道概念”走到“能完成一项具体工作”。

同主题的多条来源合并提炼，不按作者或视频重复建目录。各平台规则与经营方式不同，保留平台差异。内容使用公开网络资料和模型综合，不导入本地业务 Skill 或私人经营数据。

## 技能目录

截至 **2026-09-27**，共有 **144 个 Skills**：15 个综合评审入口 + 129 个专项任务，六个平台均超过20个。全部使用独立的 `SKILL.md` 架构，并附带参考文件、调用元数据和 MIT 许可。

| 平台 | 数量 | 主要方向 | 目录 |
| --- | ---: | --- | --- |
| Shopify | 27 | 定位与单位经济、供应验证、Feed、SEO、转化、弃单、邮件、多仓、本地化、Meta、Shopping、增量 | [Shopify](sealeap-amazon-skills/shopify/) |
| Etsy | 23 | 关键词与季节、原创/POD、数字品、工时定价、标签、摄影、定制、交期、客服、站内与站外广告 | [Etsy](sealeap-amazon-skills/etsy/) |
| eBay | 23 | 已售比价、成色、类目、价格底线、属性、实拍、多渠道库存、绩效、VeRO、General/Priority、对账 | [eBay](sealeap-amazon-skills/ebay/) |
| TikTok Shop | 22 | 趋势与演示、全成本、达人、佣金、寄样、素材权利、短视频、直播、爆量库存、履约、GMV Max | [TikTok Shop](sealeap-amazon-skills/tiktokshop/) |
| Walmart | 24 | 搜索需求、商品组合、WFS、价格底线、目录身份、质量、查询份额、Buy Box、库存、绩效、广告位 | [Walmart](sealeap-amazon-skills/walmart/) |
| Mercado Libre / 美客多 | 25 | 国家与模式、需求与季节、目录、Full、信誉、回款、Clips、目标ROAS与曝光损失 | [Mercado Libre](sealeap-amazon-skills/mercadolibre/) |
| **合计** | **144** | **选品、运营与广告的具体任务** | [完整索引](sealeap-amazon-skills/README.md) |

本轮新增25个美客多专项Skill，覆盖6个选品、13个运营和6个广告任务；附同币种贡献与现金情景的离线测算工具。见[美客多增量与来源边界](sealeap-amazon-skills/RESEARCH-MERCADOLIBRE-20260927.md)。此前补充见[五平台增量](sealeap-amazon-skills/RESEARCH-EXTRA-20260924.md)。

### 从常见问题开始

| 你的问题 | 对应 Skill |
| --- | --- |
| 首单最多能承受多少获客成本？ | [Shopify 单位经济](sealeap-amazon-skills/shopify/sealeap-shopify-unit-economics/SKILL.md) |
| 商品上传成功但广告里不对？ | [Shopify 商品 Feed](sealeap-amazon-skills/shopify/sealeap-shopify-product-feed/SKILL.md) |
| 定制订单很多，为什么赚不到钱？ | [Etsy 工时定价](sealeap-amazon-skills/etsy/sealeap-etsy-pricing-capacity/SKILL.md) |
| 历史达过门槛，现在能退出站外广告吗？ | [Etsy Offsite Ads](sealeap-amazon-skills/etsy/sealeap-etsy-offsite-ads-profit/SKILL.md) |
| 二手商品的真实成交价怎么比较？ | [eBay 已售样本](sealeap-amazon-skills/ebay/sealeap-ebay-sold-comps/SKILL.md) |
| 广告费为什么和预期不一致？ | [eBay 归因对账](sealeap-amazon-skills/ebay/sealeap-ebay-ad-attribution/SKILL.md) |
| 寄样、出片和投放权怎么管理？ | [TikTok 素材许可](sealeap-amazon-skills/tiktokshop/sealeap-tiktokshop-creator-brief-rights/SKILL.md) |
| GMV Max ROI 高就代表广告增量高吗？ | [TikTok 全域归因](sealeap-amazon-skills/tiktokshop/sealeap-tiktokshop-analytics-attribution/SKILL.md) |
| WFS 仓龄会怎样影响利润？ | [Walmart WFS经济性](sealeap-amazon-skills/walmart/sealeap-walmart-wfs-economics/SKILL.md) |
| 美客多目标ROAS提高，为什么曝光反而下降？ | [美客多目标ROAS与预算](sealeap-amazon-skills/mercadolibre/sealeap-mercadolibre-roas-budget-experiment/SKILL.md) |
| Full签收了，为什么可售数量还是不对？ | [美客多Full实收](sealeap-amazon-skills/mercadolibre/sealeap-mercadolibre-full-receiving-reconciliation/SKILL.md) |
| 搜索排名、份额和转化率怎样区分？ | [Walmart 搜索洞察](sealeap-amazon-skills/walmart/sealeap-walmart-search-query-insights/SKILL.md) |

## 开始使用

克隆仓库：

```bash
git clone https://github.com/xjli360/sealeap-ecommerce-skills.git
cd sealeap-ecommerce-skills
```

从目录选择一个任务，将**整个 Skill 文件夹**复制到你的 Agent 支持的 Skills 目录；保留其中的 `references/`、`agents/` 和 `LICENSE`。也可以直接让支持读取技能文件的 Agent 使用对应 `SKILL.md`。

例如：

```text
使用 sealeap-shopify-unit-economics。
市场：美国；币种：USD；范围：最近30天。
我会提供订单净收入、采购、履约、支付、退款和广告费用。
请给出SKU贡献、可承受CAC、数据缺口和有限测试建议。
```

只有一个具体问题时使用专项入口；需要完整选品评审、多环节巡检或广告联合诊断时，选择对应的综合入口。单个 Skill 可独立复制，不要求加载全部 144 个，也不依赖私人审计目录或特定付费服务。

## 来源与质量

本版包含 **62 个证据单元：59 条可访问内容与 3 个开源仓库**，另有 **76 项官方规则核查入口**。来源覆盖小红书、知乎、B站、抖音、YouTube、GitHub及行业公开文章。

此前已研究了 [eCommerce-Skills](https://github.com/nexscope-ai/eCommerce-Skills)（MIT），建立 **98 个上游文件到85个专项任务**的映射。仓库Stars/Forks是仓库级社区指标，不能拆成每个Skill的点赞，也不证明商业效果。部分上游文件只有主题简介，仅用作选题线索，执行流程由本项目重新编写。

质量检查包括：

- **有证据再提炼**：记录互动口径、观察时间、实际阅读范围；视频片段不冒称全文转录。
- **校正过时内容**：费用、资格、广告控制与履约时限按官方规则核验；移除固定收益、无证据算法和操纵交易建议。
- **分开三类知识**：E为网络证据，R为官方规则，M为模型综合流程与合成案例。
- **可用而不空泛**：专项任务均有独立输入、步骤、边界、交付与误判案例；没有只改平台名的模板。
- **保护个人来源**：社媒姓名、账号、原帖映射与私人资料不进入公开仓库；开源组织的MIT版权声明保留。
- **说明验证范围**：格式、引用、数量、许可、脱敏与场景审阅通过，不等于真实店铺收益验证。

详细信息见 [研究记录](sealeap-amazon-skills/RESEARCH.md)、[上游校正](UPSTREAM_REVIEW.md) 和 [验证记录](sealeap-amazon-skills/VALIDATION.md)。公众号原文因本次访问限制未计入，不以转载冒充原文。

## 免费开源

本项目的原创 Skills、代码与文档采用 **[MIT License](LICENSE)**，可免费使用、修改、分享和用于商业项目。上游版权与许可见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

开源许可不转移第三方原始文章、课程、音视频、商标或客户数据的权利。可选外部工具的费用由服务方决定；使用本仓库本身不收费。

本项目由 SeaLeap 独立维护，不代表 Shopify、Etsy、eBay、TikTok、Walmart 或 Mercado Libre 官方认证或背书。

## 仓库结构

```text
sealeap-ecommerce-skills/
├── assets/sealeap-logo.png
├── sealeap-amazon-skills/
│   ├── assets/             # 匿名证据索引、目录与交付模板
│   ├── shopify/            # 27 Skills
│   ├── etsy/               # 23 Skills
│   ├── ebay/               # 23 Skills
│   ├── tiktokshop/         # 22 Skills
│   ├── walmart/            # 24 Skills
│   ├── mercadolibre/       # 25 Skills
│   └── validate_collection.py
├── README.md
├── LICENSE
├── NOTICE
├── THIRD_PARTY_NOTICES.md
└── validate_repo.py
```

## 维护与贡献

欢迎补充公开、可核读、有传播或互动依据的资料，以及规则修正和具体业务场景。提交内容应说明解决什么问题、证据支持到哪里、需要什么输入和怎样验收；不要提交凭证、客户资料、原始课程或个人来源映射。

本地检查：

```bash
python3 validate_repo.py
```

如果这些工作流对你有帮助，欢迎 [Star](https://github.com/xjli360/sealeap-ecommerce-skills/stargazers)，帮助更多卖家和 Agent 开发者找到它。

<div align="center">
  <p><strong>知识持续汇聚，成果免费开源。</strong></p>
  <p>由 <a href="https://sealeap.cn">SeaLeap</a> 维护</p>
</div>
