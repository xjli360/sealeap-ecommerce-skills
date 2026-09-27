# 接入和验收工具

本包不要求某个私有本地 Skill，也不自动安装软件。Python 3.10+ 即可运行；官方 MCP / API 需当前账户权限，手工导出同样可用。MPstats 服务订阅或 API 权限不包含在本仓库 MIT 许可中。

## API 小样本读取

[mpstats_read.py](../scripts/mpstats_read.py) 固定调用官方 OZON Analytics 的 GET 接口，支持 `full`、`period`、`keywords`。不支持写入、任意域名、跟随重定向或自动重试；单次只取一个 SKU，返回体限制为5 MiB，这是本工具的保护设置，不是供应商限额。

运行前在私有环境配置 `MPSTATS_TOKEN`。不要把令牌放进聊天、命令参数或公开文件。从 Skill 根目录运行，日期须是已结束的实际分析窗口，SKU须替换为任务目标：

```bash
python3 scripts/mpstats_read.py --endpoint period --sku 123456 --start 2026-09-01 --end 2026-09-03 --fbs exclude --out raw-capture.json
```

这只是请求格式示例，示例SKU不是研究推荐或成功实测。`include` 表示FBO+FBS，`exclude`表示FBO。输出应存放在私有研究目录，文件以0600创建且拒绝覆盖已有文件。

`RAW_CAPTURED` 不表示可分析：输出中的日期是**请求日期**，货币与单位初始为 `UNCONFIRMED`。还需核对返回时间、SKU粒度、no_data、缺日、价格类型和单位。HTTP 200 中的业务错误也失败；401/403不继续试探，202等待完成，429按平台限制稍后恢复。其他方法先读[当前官方API](https://mpstats.io/integrations/analytics-oz/)，不能把WB或旧路径替换进命令。

## 离线日序列校验

[validate_data.py](../scripts/validate_data.py) 校验**已明确映射的外部 SKU/日数据**，不是通用原始响应解析器，也不用于内部利润或广告报表。按[合成样例](synthetic-data.json)的结构映射数据：

- 把原始文件的SHA-256、源列路径、货币单位证明、报表筛选和分页完成情况填入清单。合成样例全零哈希只表示虚构输入，实际文件必须替换成真实哈希。
- `revenue`必须是已确认以货币主单位表达的**估算订单金额**；接口没有此字段时，不能把最新价格乘整个周期销量冒充历史金额，应补导出。
- 每个SKU每天一行；`no_data=false`须有覆盖证据；留空、未知或失败响应不能填0。缺日可以保留为缺口，由工具返回HOLD。
- `population=sample`必须列明选样；`full_declared_scope`也仅指清单声明范围，不自动代表全平台。所有金额只能一个币种；真实价格/订单数据不得公开提交。

```bash
python3 scripts/validate_data.py references/synthetic-data.json --as-of 2026-09-27
python3 -m unittest discover -s scripts -p 'test_*.py'
```

合成数据通过为 `VALID_SYNTHETIC`；真实声明数据通过为 `READY_FOR_REVIEW`。两者都不验证来源真实性，不证明API授权成功或业务结果。默认7天新鲜度是本地可调整策略，使用者应按任务设定 `--max-age-days`；`--as-of`用于可重复历史检查，不能用旧日期掩盖实时数据过期。

## 其他报表

对于细分、卖家、仓库、评论及内部财务，使用实际 MCP 工具或平台导出，按[共同数据约定](mpstats.md)验收。每个任务已给出报表和所需字段。不要为了调用上述窄校验器，把这些报表强行转成SKU日销量。
