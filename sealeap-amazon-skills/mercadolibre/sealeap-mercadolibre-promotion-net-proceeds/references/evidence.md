# 证据与规则

## E：传播证据与实际阅读范围

| 编号 | 渠道 | 内容级传播证据 | 可支持的有限判断 |
| --- | --- | --- | --- |
| ML11 | 抖音 | likes 100–999；comments 0–49；saves 100–999；shares 100–999；2026-09-27 登录浏览器可见值 | 按墨西哥季节/事件拆分需求峰值与备货倒排；把活动后一月回落和一次性节庆品积压纳入情景。 |
| ML01 | YouTube | views 100,000以上；likes 1,000–9,999；comments 50–99；2026-09-26 登录浏览器可见值 | ROAS、ACOS、TACOS分母区分；广告收入倍数不等于净利润；统一窗口后对照全店收入及贡献。 |

- ML11 实际读取：visible_caption_platform_ai_chapter_summary_and_author_sample_note。边界：AI章节摘要并非人工逐字稿；未取得底层月度Top50数据，商品榜与峰值月份仅作待复核假设；不沿用统一提前2–4个月备货或推断巴西同季节。
- ML01 实际读取：complete_auto_transcript。边界：不采纳固定15%/20%贡献门槛、广告必然创造自然收入的因果推断、所有店铺都必须投放的结论；不公开原始账户、金额、营销服务或身份。

个人作者、原帖URL、视频ID、精确计数及原文映射留在仓库外受限审计中。互动只支持传播观察，不证明商业效果；同一作者的多个视频不是独立作者验证。

## R：执行前重新核验

- R68：[促销类型与定价模型](https://global-selling.mercadolibre.com/devsite/api-docs/manage-promotions-gs)。2026-09-22资料将部分Net Proceeds能力标为Coming soon；执行前核子卖家、pricing_model、活动类型、报价和实际开放能力。
- R69：[CBT 自动促销的能力限制](https://global-selling.mercadolibre.com/devsite/manage-questions-answers-global-selling/automatic-promotions-and-limitations-of-promotions-apis-for-cbt)。部分自动价格匹配活动不能由CBT排除API完整管理，需要在当前网页促销面板处理；不能把API缺失当活动不存在。
- R51：[Global Selling 费用结构](https://global-selling.mercadolibre.com/landing/pricing)。费用按站点、类目、刊登类型及物流条件区分；固定单件费、日常仓储、仓龄和移出成本不能遗漏，也不能把未知TBD当零。

规则核查日期：2026-09-27。官方规则另计，不冒充具有互动量的教程；查看方法记录于本批规则索引。国家、经营模式、权限及灰度开放情况可能不同，旧教程不能覆盖当前账户事实。

## M 与许可

本包的输入、流程、判读分支、模板与合成案例为模型综合，并经上述规则校正；未导入本地业务Skill。原创整理采用[MIT许可](../LICENSE)，不转移第三方原始文章、音视频和商标权利。
