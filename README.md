**❗️声明：本 SDK 为 BEpusdt 支付网关的非官方 Python 客户端库，仅供学习研究使用。使用本项目请遵守当地法律法规，任何违法违规使用产生的后果由使用者自行承担。**

---

# BEpusdt Python SDK

<p align="center">
<a href="https://pypi.org/project/bepusdt/"><img src="https://img.shields.io/pypi/v/bepusdt.svg" alt="PyPI version"></a>
<a href="https://pypi.org/project/bepusdt/"><img src="https://img.shields.io/pypi/pyversions/bepusdt.svg" alt="Python Support"></a>
<a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
<a href="https://github.com/v03413/bepusdt"><img src="https://img.shields.io/badge/BEpusdt-v1.23+-blue" alt="BEpusdt"></a>
</p>

## 🪧 介绍

BEpusdt 支付网关的 Python SDK，让 Python 开发者能够快速集成 USDT/TRX/USDC 加密货币支付功能。

## ✨ 特性

- 🎯 **简单易用** - 几行代码即可集成
- 🔐 **自动签名** - 内置签名生成和验证
- 🌐 **多链支持** - 支持 10+ 区块链网络
- 💰 **多币种** - USDT、USDC、TRX、ETH、BNB
- 🔄 **自动重试** - 网络错误自动重试，提升成功率
- 📱 **二维码生成** - 一键生成收款地址二维码
- 📝 **类型提示** - 完整的 IDE 智能提示
- ✅ **生产就绪** - 经过真实环境测试
- 🔄 **完全兼容** - 完整支持 BEpusdt API

## 🌟 支持的网络

### USDT
🔥 主流网络：Tron (TRC20) · Ethereum (ERC20) · BSC (BEP20) · Polygon  
⚡ 其他网络：Arbitrum · Solana · Aptos · X-Layer · Plasma

### USDC  
🔥 主流网络：Tron (TRC20) · Ethereum (ERC20) · BSC (BEP20) · Polygon  
⚡ 其他网络：Arbitrum · Solana · Aptos · X-Layer · Base

### 其他
💎 TRX (Tron) · ETH (Ethereum) · BNB (BSC)

## 📦 安装

```bash
pip install bepusdt

# 如需二维码功能
pip install bepusdt[qrcode]
```

## 🔖 兼容性

- 当前已验证的 BEpusdt 网关基线：官方上游 `v1.23.6-7-gc659103`。
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

`query_order()` 会把网关返回的 `trade_hash` 映射为
`order.block_transaction_id`；兼容网关如果直接返回 `block_transaction_id`，
SDK 也会映射到同一属性。

### 验证回调

```python
@app.route('/notify', methods=['POST'])
def notify():
    data = request.get_json(silent=True)
    if not client.verify_callback(data):
        return "fail", 400

    # 签名只证明回调来自 BEpusdt。
    # 发货前仍需查询本地订单并校验 order_id、amount、status 状态流转，
    # 再用数据库唯一约束或事务确保 trade_id/block_transaction_id 只处理一次。
    if data["status"] == 2 and mark_order_paid_once(data):
        deliver_order(data["order_id"])

    return "ok", 200
```

当前网关状态值为：`1` 等待支付、`2` 支付成功、`3` 支付超时、
`4` 订单取消、`5` 等待区块确认、`6` 交易确认失败。

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
