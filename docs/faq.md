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

### Q: amount 和 actual_amount 有什么区别？⭐

**重要概念：**

- `amount` - 订单金额（**人民币 CNY**）
- `actual_amount` - 实际支付金额（**加密货币 USDT/TRX/USDC**）

**示例：**
```python
order = client.create_order(
    order_id="ORDER_001",
    amount=10.0,  # 10 元人民币
    notify_url="https://your-domain.com/notify"
)

print(order.amount)         # 10.0 (CNY)
print(order.actual_amount)  # 1.35 (USDT，根据汇率计算)
```

**为什么这样设计？**

BEpusdt 是为中国用户设计的支付网关，商户通常以人民币定价商品。系统会根据实时汇率自动计算需要支付的加密货币数量。

**如果想直接指定 USDT 金额怎么办？**

目前 BEpusdt 不支持直接指定加密货币金额，但可以通过自定义汇率实现：

```python
# 假设想收 5 USDT，当前汇率是 7.2
# 计算：5 * 7.2 = 36 CNY
order = client.create_order(
    order_id="ORDER_001",
    amount=36.0,      # 36 CNY
    rate=7.2,         # 固定汇率
    notify_url="https://your-domain.com/notify"
)
# 结果：actual_amount = 5.0 USDT
```

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

### Q: 遇到 503 Service Unavailable 错误怎么办？

**问题现象：**
```
rpc error: code = Unavailable desc = unexpected HTTP status code received from server: 503 (Service Unavailable)
```

**原因分析：**
- BEpusdt 服务器暂时不可用（维护、重启、负载过高）
- 网络临时故障
- 区块链节点连接问题

**解决方案：**

1. **使用自动重试（推荐）** - SDK v0.2.2+ 已内置

```python
# 初始化时配置重试参数
client = BEpusdtClient(
    api_url="https://your-server.com",
    api_token="your-api-token",
    max_retries=3,      # 最多重试 3 次
    retry_delay=1.0     # 初始延迟 1 秒（指数退避）
)

# SDK 会自动重试以下错误：
# - 网络连接失败 (NetworkError)
# - 请求超时 (TimeoutError)
# - 服务器错误 5xx (ServerError)
```

2. **手动重试**

```python
import time
from bepusdt.exceptions import ServerError, NetworkError, TimeoutError

max_attempts = 3
for attempt in range(max_attempts):
    try:
        order = client.create_order(...)
        break  # 成功则退出
    except (ServerError, NetworkError, TimeoutError) as e:
        if attempt < max_attempts - 1:
            wait_time = 2 ** attempt  # 指数退避：1s, 2s, 4s
            print(f"请求失败，{wait_time}秒后重试...")
            time.sleep(wait_time)
        else:
            raise  # 最后一次失败则抛出异常
```

3. **检查服务器状态**

```bash
# 查看 BEpusdt 日志
docker logs bepusdt

# 检查服务是否运行
curl https://your-server.com/pay/check-status/test
```

4. **联系管理员**

如果问题持续，可能是服务器配置问题，建议联系 BEpusdt 管理员。

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

### Q: 签名错误（签名验证失败）⚠️

这是最常见的问题！签名错误通常有以下几种原因：

#### 1. API Token 不匹配

**问题：** 客户端使用的 `api_token` 和服务端配置的 `auth_token` 不一致

**解决：**
```python
# 检查客户端配置
client = BEpusdtClient(
    api_url="https://your-server.com",
    api_token="your-api-token"  # 必须和服务端一致！
)
```

服务端配置（`conf.toml`）：
```toml
auth_token = "your-api-token"  # 必须和客户端一致！
```

#### 2. 参数类型或格式错误

**问题：** 参数值的类型不对，比如：
- amount 应该是数字，传了字符串
- 参数值有多余的空格
- 参数值为空字符串

**解决：**
```python
# ✅ 正确
order = client.create_order(
    order_id="ORDER_001",
    amount=42,  # 数字类型
    notify_url="https://example.com/notify"
)

# ❌ 错误
order = client.create_order(
    order_id="ORDER_001",
    amount="42",  # 字符串类型会导致签名错误
    notify_url="https://example.com/notify "  # 末尾有空格
)
```

#### 3. 参数缺失或多余

**问题：** 必需参数没传，或者传了不该传的参数

**解决：**
```python
# 必需参数
order = client.create_order(
    order_id="ORDER_001",      # 必需
    amount=10.0,               # 必需
    notify_url="https://..."   # 必需
)
```

#### 4. 如何调试签名问题

开启 DEBUG 日志查看签名详情：

```python
import logging

# 开启 DEBUG 日志
logging.basicConfig(level=logging.DEBUG)

# 创建订单时会输出签名前的参数
client = BEpusdtClient(...)
order = client.create_order(...)
```

输出示例：
```
DEBUG:bepusdt.client:创建订单请求参数: {'order_id': 'ORDER_001', 'amount': 42, 'notify_url': '...', 'signature': '***'}
```

#### 5. 手动验证签名

如果还是有问题，可以手动计算签名对比：

```python
import hashlib

# 1. 准备参数（不包含 signature）
params = {
    "order_id": "ORDER_001",
    "amount": 42,
    "notify_url": "https://example.com/notify",
    "redirect_url": "https://example.com/redirect"
}

# 2. 按键排序
sorted_params = sorted(params.items())

# 3. 拼接参数
param_str = "&".join([f"{k}={v}" for k, v in sorted_params])
print(f"参数字符串: {param_str}")

# 4. 加上 token 计算 MD5
api_token = "your-api-token"
sign_str = param_str + api_token
signature = hashlib.md5(sign_str.encode("utf-8")).hexdigest().lower()
print(f"签名: {signature}")
```

对比输出的签名和服务端日志中的签名是否一致。

### Q: 未收到回调通知

可能原因：
1. 回调地址不是 HTTPS
2. 回调地址无法访问
3. 防火墙阻止
4. 回调返回不是 "ok"

### Q: 回调签名验证失败

确保：
1. API Token 正确
2. 回调数据完整
3. 没有修改回调数据

```python
@app.route('/notify', methods=['POST'])
def notify():
    data = request.get_json()
    
    # 验证签名
    if not client.verify_callback(data):
        return "fail", 400
    
    # 处理业务逻辑
    # ...
    
    return "ok", 200  # 必须返回 "ok"
```

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
