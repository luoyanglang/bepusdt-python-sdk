# ❓ 常见问题

## 安装问题

### Q: 如何安装 SDK？

```bash
pip install bepusdt
```

### Q: 如何从源码安装？

```bash
git clone https://github.com/luoyanglang/bepusdt-python-sdk.git
cd bepusdt-python-sdk
pip install -e .
```

## 使用问题

### Q: 如何获取 API Token？

API Token 在 BEpusdt 的配置文件 `conf.toml` 中：

```toml
auth_token = "your-api-token"
```

### Q: 回调地址必须是 HTTPS 吗？

是的，BEpusdt 要求回调地址必须使用 HTTPS，否则会被 301 重定向导致回调失败。

### Q: 回调接口应该返回什么？

必须返回字符串 `"ok"`，表示回调成功：

```python
@app.route('/notify', methods=['POST'])
def notify():
    # 处理回调
    return "ok", 200  # 必须返回 "ok"
```

### Q: 如何验证回调签名？

```python
callback_data = request.get_json()
if client.verify_callback(callback_data):
    # 签名验证通过
    pass
```

### Q: 订单状态有哪些？

- `1` - 等待支付
- `2` - 支付成功
- `3` - 订单超时

### Q: 查询订单接口需要签名吗？

不需要，查询订单是公开的 GET 接口，不需要签名。

### Q: 如何指定收款地址？

```python
order = client.create_order(
    order_id="ORDER_001",
    amount=10.0,
    notify_url="https://your-domain.com/notify",
    address="TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
)
```

### Q: 如何自定义汇率？

```python
# 固定汇率
rate=7.4

# 最新汇率上浮 2%
rate="~1.02"

# 最新汇率加 0.3
rate="+0.3"
```

## 错误处理

### Q: 创建订单失败，返回 400

可能原因：
1. API Token 错误
2. 参数格式错误
3. 签名错误
4. 钱包地址未配置

检查 BEpusdt 日志：
```bash
docker logs bepusdt
```

### Q: 未收到回调通知

可能原因：
1. 回调地址不是 HTTPS
2. 回调地址无法访问
3. 防火墙阻止
4. 回调返回不是 "ok"

### Q: 签名验证失败

确保：
1. API Token 正确
2. 回调数据完整
3. 没有修改回调数据

## 开发问题

### Q: 如何在本地测试回调？

使用 webhook.site 或 ngrok：

```bash
# 使用 ngrok
ngrok http 5000

# 使用生成的 https 地址作为 notify_url
```

### Q: 如何查看 SDK 版本？

```python
import bepusdt
print(bepusdt.__version__)
```

### Q: 支持哪些 Python 版本？

Python 3.7+

## 更多帮助

- 📝 [提交 Issue](https://github.com/luoyanglang/bepusdt-python-sdk/issues)
- 📖 [查看文档](./README.md)
- 🔗 [BEpusdt 官方](https://github.com/v03413/bepusdt)
