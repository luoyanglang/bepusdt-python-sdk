**❗️声明：本 SDK 为 BEpusdt 支付网关的非官方 Python 客户端库，仅供学习研究使用。使用本项目请遵守当地法律法规，任何违法违规使用产生的后果由使用者自行承担。**

---

# BEpusdt Python SDK

<p align="center">
<a href="https://pypi.org/project/bepusdt/"><img src="https://img.shields.io/pypi/v/bepusdt.svg" alt="PyPI version"></a>
<a href="https://pypi.org/project/bepusdt/"><img src="https://img.shields.io/pypi/pyversions/bepusdt.svg" alt="Python Support"></a>
<a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
<a href="https://github.com/v03413/bepusdt"><img src="https://img.shields.io/badge/BEpusdt-v1.22+-blue" alt="BEpusdt"></a>
</p>

## 🪧 介绍

BEpusdt 支付网关的 Python SDK，让 Python 开发者能够快速集成 USDT/TRX/USDC 加密货币支付功能。

## ✨ 特性

- 🎯 **简单易用** - 几行代码即可集成
- 🔐 **自动签名** - 内置签名生成和验证
- 🌐 **多链支持** - 支持 10+ 区块链网络
- 💰 **多币种** - USDT、USDC、TRX
- 🔄 **自动重试** - 网络错误自动重试，提升成功率
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
💎 TRX (Tron)

## 📦 安装

```bash
pip install bepusdt
```

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

### 验证回调

```python
@app.route('/notify', methods=['POST'])
def notify():
    data = request.get_json()
    if client.verify_callback(data):
        # 处理支付成功
        return "ok", 200
    return "fail", 400
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
