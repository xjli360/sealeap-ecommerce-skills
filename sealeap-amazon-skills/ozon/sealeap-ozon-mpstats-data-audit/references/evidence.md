# 来源与证据边界

观察日期：2026-09-27。E为网上内容有限支持；R为官方定义/执行前复核入口；M为本包新编的流程、计算条件、交付与合成案例。互动只证明传播，不证明方法有效或作者结论正确。

## E：匿名内容

| 编号 | 渠道与传播区间 | 采用的有限方法 | 核读范围与排除项 |
| --- | --- | --- | --- |
| O06 | Xiaohongshu；likes: 100–999、saves: 100–999、comments: 0–49 | 需求/价带/竞争/物流/风险/评论形成选品卡和每周复核 | 笔记正文完整核读，评论只看使用限制，不作效果验证；未检验作者软件；不引入其私有Skill、安装包或效果声称 |
| O08 | trade_press；views: 1,000–9,999 | 将MPstats报表对应到不同经营问题 | 检索索引页面；核读类目、卖家、SKU日序列、属性、关键词和相似商品章节；服务营销保证、估算收入或毛利不能视为实收利润；旧覆盖范围须更新 |

## R：官方核对

| 编号 | 官方入口 | 约束 |
| --- | --- | --- |
| R77 | [MPstats OZON Analytics API](https://mpstats.io/integrations/analytics-oz/) | API字段需逐端点映射；不能套用WB路径。文档核对不等于成功取数。 |
| R78 | [MPstats API 鉴权与状态](https://mpstats.io/integrations/docs/description/) | 用X-Mpstats-TOKEN请求头；202不是完成；凭证只放私有环境。 |
| R79 | [MPstats 官方 MCP 能力](https://mpstats.io/instruments/ai/mcp) | 发现工具后选择OZON只读能力；MCP还包含其他平台/写入能力，不能假定全部可用或授权。 |
| R80 | [MPstats OZON 细分市场](https://wiki.mpstats.io/ru/OZON/Выбор_ниши_Ozon) | 细分按商品类型组织；估算订单、真实利润与缺货潜力分开。 |
| R81 | [MPstats OZON SKU 报告](https://wiki.mpstats.io/OZON/Поиск_по_артикулу_Ozon) | 尺寸可有独立SKU；首次发现不是上架证明；缺失名次不等于固定名次。 |
| R82 | [MPstats OZON 搜索报告](https://wiki.mpstats.io/ru/OZON/Товары_в_поиске) | OZON频次为7天独立用户，不能与WB30天查询次数混算；记录FBS开关。 |
| R83 | [MPstats OZON 内部商品报表](https://wiki.mpstats.io/ru/Кабинет_Ozon/Товары) | 内部模块需授权店铺；记录成本完整性，按字段定义区分订单、销售、退款、贡献与到账。 |
| R90 | [MPstats 旧比较模块停用提示](https://wiki.mpstats.io/ru/Сравнение_маркетплейсов/По_дням) | 旧WB+Ozon比较模块不作为必需入口，使用当前各平台报表并明确匹配口径。 |

官方文档可能变化，按当前地区/账户复核。公开正文为重新组织的工作方法，未复制原文、字幕或图片；原始内容权利未转移。精确计数、个人来源链接和原始审计材料不进入公开包。
