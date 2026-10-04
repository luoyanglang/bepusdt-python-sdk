# ❓ 常见问题

## 安装问题

### Q: 如何安装 SDK？

```bash
pip install bepusdt
```

二维码功能是可选依赖：

```bash
pip install bepusdt[qrcode]
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

- `amount` - 订单金额（所选 **fiat 法币**，默认 CNY，亦支持 USD/EUR/GBP/JPY）
- `actual_amount` - 实际支付金额（**加密货币 USDT/USDC/TRX/ETH/BNB/GRAM**）

**示例：**
```python
order = client.create_order(
    order_id="ORDER_001",
    amount=10.0,  # 10 元人民币
    notify_url="https://your-domain.com/notify"
)

print(order.amount)         # 10.0 (CNY)
print(order.actual_amount)  # 返回的 USDT 实际付款数额，随汇率和分配情况变化
```

**为什么这样设计？**

商户用所选法币定价，系统按汇率计算基础加密货币数额，再应用币种精度、最小原子数额和地址/数额占用规则。默认法币为 CNY；传 `fiat="USD"` 时 `amount=10` 表示 10 美元。

**如果想直接指定 USDT 金额怎么办？**

本阶段商户方法不直接指定最终加密货币数额。固定汇率可给出基础估算，但不能保证最终分配恰好等于目标：

```python
# 假设基础估算为 5 USDT，固定汇率为 7.2
# 计算：5 * 7.2 = 36 CNY
order = client.create_order(
    order_id="ORDER_001",
    amount=36.0,      # 36 CNY
    rate=7.2,         # 固定汇率
    notify_url="https://your-domain.com/notify"
)
# 显示并校验返回的 actual_amount_text，不假定结果恰好为 5
print(order.actual_amount_text)
```

上游会按币种精度舍入并应用最小原子数额；若候选地址/数额组合已占用，会递增原子数额重新分配。付款页面与本地回调关联须使用创建响应的最终 `actual_amount` / `actual_amount_text`。

### Q: 如何获取 API Token？

API Token 在 BEpusdt 的配置文件 `conf.toml` 中：

```toml
auth_token = "your-api-token"
```

### Q: 回调地址必须是 HTTPS 吗？

是的，BEpusdt 要求回调地址必须使用 HTTPS，否则会被 301 重定向导致回调失败。

### Q: 回调接口应该返回什么？

持久接收后推荐 HTTP 200/plain `"ok"` 兼容旧部署。当前 Epusdt 只检查
HTTP 200；`200 fail` 也会被视为成功，拒绝或存储失败必须非 200：

```python
@app.route('/notify', methods=['POST'])
def notify():
    # 处理回调
    return "ok", 200  # 必须先完成持久接收
```

### Q: 如何验证回调签名？

```python
callback_data = request.get_json()
if client.verify_callback(callback_data):
    # store 是已登记创建返回交易的商户持久事务接收器，见集成示例。
    accepted = store.accept(callback_data)
```

`verify_callback()` 只验证回调签名是否来自可信 BEpusdt 服务，不会替代商户
系统自己的订单校验。支付成功回调可能因为网络失败被重试，业务处理必须保证
同一个商户 `order_id` 只安排一次履约，并保留创建返回的全部已知交易尝试。
按 trade_id 去重不足以避免两次尝试造成两次发货；不能只接受最新 trade_id。

### Q: 订单状态有哪些？

- `1` - 等待支付
- `2` - 支付成功
- `3` - 订单超时
- `4` - 取消；`5` - 确认中；`6` - 失败。枚举有效不保证通知触发。

当前等待通知每 30 秒调度、60 秒缓存抑制；成功重试由配置控制，默认上限 10，
下一次基于确认时间 + 2^notify_num 分钟；3/6 是 best-effort，4/5 没有对应
通知路径。过期订单还可能在历史扫描中确认截止前的转账，出现 3→5→2。

### Q: 查询订单接口需要签名吗？

两种模式均不验商户签名：默认 legacy 用旧 GET，显式 current 用 POST Info。
新版受付款端指纹约束，绑定后商户服务器可能读不到；不是任意订单均可读的
商户鉴权接口。不会自动降级/绕过。缺失交易哈希或付款链接不从 URL 猜测。

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
# - 请求超时 (RequestTimeoutError / TimeoutError)
# - 服务器错误 5xx (ServerError)
#
# 不会自动重试：
# - 客户端错误 4xx (ClientError)
# - 业务错误或响应解析失败 (APIError)
# - 参数验证错误 (ValidationError)
```

2. **手动重试**

```python
import time
from bepusdt.exceptions import ServerError, NetworkError, RequestTimeoutError

max_attempts = 3
for attempt in range(max_attempts):
    try:
        order = client.create_order(...)
        break  # 成功则退出
    except (ServerError, NetworkError, RequestTimeoutError) as e:
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
    amount="42",  # 字符串金额会被 SDK 本地拒绝
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

使用 SDK 的协议签名函数核对；不要把 Python 通用 `str()` / f-string 数字格式当作网关协议：

```python
from bepusdt.signature import generate_signature, verify_signature

# 1. 准备参数（不包含 signature）
params = {
    "order_id": "ORDER_001",
    "amount": 42,
    "notify_url": "https://example.com/notify",
    "redirect_url": "https://example.com/redirect"
}

# helper 按网关 JSON float64 格式处理数字，使用枚举值，跳过 None/空字符串
# 空/非空数组、对象和非有限数字会被拒绝
api_token = "your-api-token"
signature = generate_signature(params, api_token)
assert verify_signature(params, api_token, signature)
```

例如 `1000000.0` 在网关签名文本中是 `1e+06`，不是 Python 的 `1000000.0`。回调验签请使用 `client.verify_callback()`；勿输出真实 Token、Token 拼接文本或原始签名。

### Q: 未收到回调通知

可能原因：
1. 回调地址不是 HTTPS
2. 回调地址无法访问
3. 防火墙阻止
4. 没有成功持久接收或返回非 HTTP 200（当前 Epusdt 不检查正文）

### Q: 回调签名验证失败

确保：
1. API Token 正确
2. 回调数据完整
3. 没有修改回调数据

```python
@app.route('/notify', methods=['POST'])
def notify():
    data = request.get_json(silent=True)
    
    # 验证签名
    if not client.verify_callback(data):
        return "fail", 400
    
    # store 先校验已登记尝试，再原子保存 inbox 和唯一商户订单 outbox。
    try:
        if not store.accept(data):
            return "fail", 400
    except Exception:
        return "fail", 503
    
    return "ok", 200  # 持久接收后应答；实际履约由幂等工作者完成
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

SDK 包 metadata 仍允许 Python 3.7+。当前 CI 持续验证 Python 3.8、3.9、
3.10、3.11 和 3.12；Python 3.7 已进入生命周期末期，最低版本调整会作为
兼容性边界单独规划。

### Q: 从 PyPI 0.3.1 升级到 0.3.9+ 需要注意什么？

建议直接升级到最新版本：

```bash
pip install --upgrade bepusdt
```

升级后重点确认：

1. `TradeType` 枚举签名使用实际请求值，默认下单签名已与服务端一致。
2. 回调处理不能只依赖签名验证，还需要校验本地订单号、金额、状态流转和幂等发货。
3. Flask/FastAPI 示例已移除 debug 和原始异常回显，生产集成应按新示例处理错误。
4. 发布链路从 `0.3.8` 起恢复正常，PyPI 最新版本不再停留在 `0.3.1`。

## 更多帮助

- 📝 [提交 Issue](https://github.com/luoyanglang/bepusdt-python-sdk/issues)
- 📖 [查看文档](./README.md)
- 🔗 [BEpusdt 官方](https://github.com/v03413/bepusdt)
