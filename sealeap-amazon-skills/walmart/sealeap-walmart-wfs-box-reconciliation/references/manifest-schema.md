# 离线装箱数据合同

这是本Skill自定义的核对格式，**不是Walmart上传模板或API请求格式**。从授权的实际计划与最终装箱记录映射字段，不能用此文件直接创建发货。

```json
{
  "plan": [
    {"shipment_id":"SHIP-A","destination":"FC-A","sku":"SKU-A","units":6},
    {"shipment_id":"SHIP-A","destination":"FC-A","sku":"SKU-B","units":4}
  ],
  "boxes": [
    {"shipment_id":"SHIP-A","destination":"FC-A","box_id":"BOX-1","receiving_label_id":"LABEL-1",
     "items":[{"sku":"SKU-A","units":3},{"sku":"SKU-B","units":2}]},
    {"shipment_id":"SHIP-A","destination":"FC-A","box_id":"BOX-2","receiving_label_id":"LABEL-2",
     "items":[{"sku":"SKU-A","units":3},{"sku":"SKU-B","units":2}]}
  ]
}
```

上述为合成样例。每个shipment/SKU只有一行计划；units为正整数。箱号在同一shipment内唯一，完整收货标签标识须在整个输入内唯一。相同SKU可以分装到多个箱，程序会聚合核对。

运行：

```bash
python3 scripts/check_box_manifest.py manifest.json
```

退出码0表示所输入数据一致，2表示输入或一致性失败。输出按shipment/SKU列planned、packed、difference，并给错误类型。脚本无网络调用、不生成标签、不修改文件或平台库存。

通过后还需人工核实实物、标签扫码、GTIN、箱/托盘贴标层级及当前平台要求；不同仓相同SKU不能互相抵消差异。不要将凭证或买家信息放入此输入。

运行内置合成测试：

```bash
python3 scripts/test_box_manifest.py
```

