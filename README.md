**❗️声明：本 SDK 为 BEpusdt 支付网关的非官方 Python 客户端库，仅供学习研究使用。使用本项目请遵守当地法律法规，任何违法违规使用产生的后果由使用者自行承担。**

---

# BEpusdt Python SDK

<p align="center">
<a href="https://pypi.org/project/bepusdt/"><img src="https://img.shields.io/pypi/v/bepusdt.svg" alt="PyPI version"></a>
<a href="https://pypi.org/project/bepusdt/"><img src="https://img.shields.io/pypi/pyversions/bepusdt.svg" alt="Python Support"></a>
<a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
<a href="https://github.com/v03413/bepusdt"><img src="https://img.shields.io/badge/BEpusdt-API-blue" alt="BEpusdt"></a>
</p>

## 🪧 介绍

BEpusdt 支付网关的 Python SDK，让 Python 开发者能够快速集成 USDT/USDC/TRX/ETH/BNB/GRAM 加密货币支付功能。

## ✨ 特性

- 🎯 **简单易用** - 几行代码即可集成
- 🔐 **自动签名** - 内置签名生成和验证
- 🌐 **多链支持** - 支持 10+ 区块链网络
- 💰 **多币种** - USDT、USDC、TRX、ETH、BNB、GRAM
- 🔄 **自动重试** - 网络错误自动重试，提升成功率
- 📱 **二维码生成** - 一键生成收款地址二维码
- 📝 **类型提示** - 完整的 IDE 智能提示
- 🔎 **明确兼容模式** - 保留旧版查询，显式选择当前网关查询
- 🧪 **契约验证** - Go 签名黄金样本与商户流程回归测试

## 🌟 支持的网络

### USDT
🔥 主流网络：Tron (TRC20) · Ethereum (ERC20) · BSC (BEP20) · Polygon  
⚡ 其他网络：Arbitrum · Solana · Aptos · X-Layer · Plasma · TON

### USDC  
🔥 主流网络：Tron (TRC20) · Ethereum (ERC20) · BSC (BEP20) · Polygon  
⚡ 其他网络：Arbitrum · Solana · Aptos · X-Layer · Base

### 其他
💎 TRX (Tron) · ETH (Ethereum) · BNB (BSC) · GRAM (TON)

## 📦 安装

```bash
pip install bepusdt

# 如需二维码功能
pip install bepusdt[qrcode]
```

## 🔖 兼容性

- 旧模式 `query_mode="legacy"`（默认）：历史基线 f4bdee1 / v1.23.6，GET `/pay/check-status/{trade_id}`。
- 新模式 `query_mode="current"`：按官方 aa3bd5097f258cccd5a53baed7211c74733b8332 的 POST `/api/v1/pay/info` 适配；本批是源码和离线契约验证，不是实际数据库、浏览器或链上付款验收。
- 创建、取消的现有方法含义不变；待选收银台创建、方式发现/选择、后台、Epay、MQTT 不在本阶段支持范围。
- Info 不验商户签名，绑定付款端指纹后可能拒绝服务器读取；不自动探测、降级或绕过访问限制，不能把查询结果作为签名支付凭据。
- 上游固定/待选零金额、正/零共享钱包及同 ID 跨零重建存在源码限制，尚未验证为安全支付模式。SDK 仍接受已有零金额参数，但本批不承诺这些模式的地址独占、正确归属或完整兼容。
- SDK 包 metadata 仍允许 Python 3.7+；当前 CI 持续验证 Python 3.8 至
  3.12。Python 3.7 已进入生命周期末期，最低版本调整会作为兼容性边界单独规划。

## ⬆️ 从旧版升级

如果你从 PyPI `0.3.1` 或更早版本升级，建议直接升级到 `0.3.9+`：

```bash
pip install --upgrade bepusdt
```

升级后请重点确认：

- `TradeType` 枚举参与签名时使用实际请求值，默认下单签名已与服务端一致。
- 版本号由 Git tag 推导，PyPI 包版本已恢复正常发布。
- 回调示例已强化安全边界；签名验证通过后仍需校验本地订单、金额、状态流转和幂等发货。
- Flask/FastAPI 示例不再返回原始异常，也不再启用 Flask debug 模式。

## 🚀 快速开始

```python
from bepusdt import BEpusdtClient, TradeType

# 初始化客户端（支持自动重试）
client = BEpusdtClient(
    api_url="https://your-bepusdt-server.com",
    api_token="your-api-token",
    max_retries=3  # 可选：网络错误自动重试3次
)

# 创建订单
order = client.create_order(
    order_id="ORDER_001",
    amount=10.0,
    notify_url="https://your-domain.com/notify",
    trade_type=TradeType.USDT_TRC20
)

print(f"💰 支付金额: {order.actual_amount} USDT")
print(f"📍 收款地址: {order.token}")
print(f"🔗 支付链接: {order.payment_url}")
```

## 📖 文档

- 📚 [完整文档](./docs/README.md)
- 📖 [API 参考](./docs/api.md)
- 💡 [使用示例](./docs/examples.md)
- ❓ [常见问题](./docs/faq.md)

## 🔧 核心功能

### 错误处理

SDK 会自动处理网络错误和服务器临时故障：

```python
from bepusdt.exceptions import ServerError, NetworkError, RequestTimeoutError, APIError

try:
    order = client.create_order(...)
except ServerError as e:
    # 服务器错误 5xx（已自动重试）
    print(f"服务器错误: {e}")
except NetworkError as e:
    # 网络连接失败（已自动重试）
    print(f"网络错误: {e}")
except RequestTimeoutError as e:
    # 请求超时（已自动重试）
    print(f"超时: {e}")
except APIError as e:
    # 业务错误或响应解析失败（不会自动重试）
    print(f"API 错误: {e}")
```

**自动重试配置：**
```python
client = BEpusdtClient(
    api_url="https://your-server.com",
    api_token="your-api-token",
    max_retries=3,      # 最多重试 3 次
    retry_delay=1.0     # 初始延迟 1 秒（指数退避）
)
```

自动重试只覆盖 `NetworkError`、`RequestTimeoutError` / `TimeoutError` 和
`ServerError`；`ClientError`、`APIError`、`ValidationError` 不会自动重试。

### 创建订单

```python
order = client.create_order(
    order_id="ORDER_001",
    amount=10.0,
    notify_url="https://your-domain.com/notify",
    redirect_url="https://your-domain.com/success",
    trade_type=TradeType.USDT_TRC20
)
```

### 查询订单

```python
order = client.query_order(trade_id="xxx")
if order.status == OrderStatus.SUCCESS:
    print("✅ 支付成功")
```

旧模式 `query_order()` 会把网关返回的 `trade_hash` 映射为
`order.block_transaction_id`；兼容网关如果直接返回 `block_transaction_id`，
SDK 也会映射到同一属性。

当前网关必须显式配置：

```python
client = BEpusdtClient(
    api_url="https://your-bepusdt-server.com", api_token="your-api-token",
    query_mode="current"
)
order = client.query_order("known-trade-id")
print(order.expired_at, order.amount_text, order.actual_amount_text)
```

新版保留原有 float 属性，另提供金额原文和 Unix 时间。`expiration_time` 为
按本地时钟计算、截断并归零的剩余秒数；`expired_at` 为权威返回的绝对期限。
未选方式时地址为空、actual_amount 为兼容占位 0.0，精确文本为 None。
Info 不提供原始交易哈希或付款链接：前者为 None、后者为空，不从 trade_url 猜测。

### 验证回调

```python
@app.route('/notify', methods=['POST'])
def notify():
    data = request.get_json(silent=True)
    if not client.verify_callback(data):
        return "fail", 400

    # store 是商户的持久事务接收器，详见 examples/callback_store.py。
    # 校验已登记交易尝试、金额/法币；原子记录 inbox 和唯一 order_id outbox。
    try:
        if not store.accept(data):
            return "fail", 400
    except Exception:
        return "fail", 503
    return "ok", 200
```

当前网关状态值为：`1` 等待支付、`2` 支付成功、`3` 支付超时、
`4` 订单取消、`5` 等待区块确认、`6` 交易确认失败。

当前上游不保证发送 4/5 回调；等待通知每 30 秒调度、60 秒缓存抑制；
过期/失败为 best-effort，成功才进入配置控制的重试队列（默认上限 10）。
过期的已知尝试仍可能随后成功，不能只接受最新 trade_id。按商户 order_id
确保一次履约；实际工作者需另做履约幂等与失败恢复。当前 Epusdt 只检查 HTTP 200，
拒绝/存储失败必须非 200，持久接收后推荐 plain ok 兼容旧部署。
示例使用仓库外 SQLite 文件，配置及运行方式见[集成示例](docs/examples.md)。

### 生成二维码

```python
# 创建订单后生成收款地址二维码
order = client.create_order(...)

# 方式1：保存为图片文件
qr = order.generate_qrcode()
qr.save("payment_qr.png")

# 方式2：获取 Base64（用于 API 返回）
qr_base64 = order.get_qrcode_base64()

# 方式3：获取 Data URI（直接用于 HTML img src）
data_uri = order.get_qrcode_data_uri()
# <img src="{data_uri}">
```

## 🏝️ 交流反馈

- 💬 Telegram: [@luoyanglang](https://t.me/luoyanglang)
- 📝 [提交 Issue](https://github.com/luoyanglang/bepusdt-python-sdk/issues)
- 🔗 [BEpusdt 官方群组](https://t.me/BEpusdtChat)

## 🙏 感谢

- [BEpusdt](https://github.com/v03413/bepusdt) - 优秀的 USDT 支付网关
- [Epusdt](https://github.com/assimon/epusdt) - BEpusdt 的前身

## 🔗 相关链接

- 🏠 [BEpusdt 官方](https://github.com/v03413/bepusdt)
- 📦 [PyPI 页面](https://pypi.org/project/bepusdt/)
- 💻 [GitHub 仓库](https://github.com/luoyanglang/bepusdt-python-sdk)
- 📋 [更新日志](./CHANGELOG.md)

## 📄 许可证

[MIT License](LICENSE)

## 📢 声明

本项目仅供学习研究使用，使用过程中请遵守当地法律法规，任何违法违规使用产生的后果由使用者自行承担。

---

Made with ❤️ for BEpusdt community
