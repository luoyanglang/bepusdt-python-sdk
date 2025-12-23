# BEpusdt Python SDK

BEpusdt 支付网关的 Python SDK，支持 USDT/TRX/USDC 多种加密货币支付，覆盖 Tron、Ethereum、Polygon、BSC、Solana 等多个区块链网络。

## 特性

- ✅ 简单易用的 API
- ✅ 完整的类型提示
- ✅ 支持 10+ 区块链网络
- ✅ 支持 USDT、USDC、TRX 等多种代币
- ✅ 自动签名验证
- ✅ 完善的异常处理
- ✅ 支持自定义汇率
- ✅ 订单重建机制

## 支持的支付类型

### USDT
- `usdt.trc20` - Tron 网络（推荐，手续费低）
- `usdt.erc20` - Ethereum 网络
- `usdt.polygon` - Polygon 网络
- `usdt.bep20` - BSC 网络
- `usdt.aptos` - Aptos 网络
- `usdt.solana` - Solana 网络
- `usdt.xlayer` - X-Layer 网络
- `usdt.arbitrum` - Arbitrum-One 网络
- `usdt.plasma` - Plasma 网络

### USDC
- `usdc.trc20` - Tron 网络
- `usdc.erc20` - Ethereum 网络
- `usdc.polygon` - Polygon 网络
- `usdc.bep20` - BSC 网络
- `usdc.aptos` - Aptos 网络
- `usdc.solana` - Solana 网络
- `usdc.xlayer` - X-Layer 网络
- `usdc.arbitrum` - Arbitrum-One 网络
- `usdc.base` - Base 网络

### 其他
- `tron.trx` - TRX（波场币）

## 安装

```bash
pip install bepusdt
```

或从源码安装：

```bash
git clone https://github.com/yourusername/bepusdt-python-sdk.git
cd bepusdt-python-sdk
pip install -e .
```

## 快速开始

### 1. 初始化客户端

```python
from bepusdt import BEpusdtClient, TradeType

client = BEpusdtClient(
    api_url="https://pay.kuaijieyi.com",
    api_token="your-api-token"
)
```

### 2. 创建支付订单

#### USDT TRC20 支付（推荐）

```python
order = client.create_order(
    order_id="ORDER_20231222_001",
    amount=10.0,  # CNY
    notify_url="https://your-domain.com/api/payment/notify",
    redirect_url="https://your-domain.com/payment/success",
    trade_type=TradeType.USDT_TRC20
)

print(f"支付链接: {order.payment_url}")
print(f"支付金额: {order.actual_amount} USDT")
print(f"收款地址: {order.token}")
```

#### TRX 支付

```python
order = client.create_order(
    order_id="ORDER_20231222_002",
    amount=1.0,  # CNY
    notify_url="https://your-domain.com/api/payment/notify",
    trade_type=TradeType.TRON_TRX
)

print(f"支付金额: {order.actual_amount} TRX")
```

#### USDC 支付

```python
order = client.create_order(
    order_id="ORDER_20231222_003",
    amount=10.0,  # CNY
    notify_url="https://your-domain.com/api/payment/notify",
    trade_type=TradeType.USDC_TRC20
)

print(f"支付金额: {order.actual_amount} USDC")
```

#### 自定义汇率

```python
# 固定汇率 7.4
order = client.create_order(
    order_id="ORDER_001",
    amount=10.0,
    notify_url="https://your-domain.com/notify",
    rate=7.4
)

# 最新汇率上浮 2%
order = client.create_order(
    order_id="ORDER_002",
    amount=10.0,
    notify_url="https://your-domain.com/notify",
    rate="~1.02"
)

# 最新汇率下浮 3%
order = client.create_order(
    order_id="ORDER_003",
    amount=10.0,
    notify_url="https://your-domain.com/notify",
    rate="~0.97"
)

# 最新汇率加 0.3
order = client.create_order(
    order_id="ORDER_004",
    amount=10.0,
    notify_url="https://your-domain.com/notify",
    rate="+0.3"
)
```

#### 指定收款地址

```python
order = client.create_order(
    order_id="ORDER_005",
    amount=10.0,
    notify_url="https://your-domain.com/notify",
    address="TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"  # 指定收款地址
)
```

### 3. 验证支付回调

```python
from flask import Flask, request

app = Flask(__name__)

@app.route('/api/payment/notify', methods=['POST'])
def payment_notify():
    # 获取回调数据
    callback_data = request.get_json()
    
    # 验证签名
    if not client.verify_callback(callback_data):
        return "fail", 400
    
    # 处理支付成功
    order_id = callback_data['order_id']
    status = callback_data['status']
    
    if status == 2:  # 支付成功
        # 更新订单状态
        print(f"订单 {order_id} 支付成功")
        # 开通会员/发货等业务逻辑
        
    return "ok", 200
```

### 4. 查询订单状态

```python
# 查询订单当前状态
order = client.query_order(trade_id="xxx")

if order.status == OrderStatus.SUCCESS:
    print("订单已支付")
    print(f"区块链交易ID: {order.block_transaction_id}")
elif order.status == OrderStatus.WAITING:
    print("等待支付中")
elif order.status == OrderStatus.TIMEOUT:
    print("订单已超时")
```

**注意**：
- 查询接口不需要签名，是公开的 GET 请求
- 返回的 Order 对象中，只有 `trade_id`、`status`、`block_transaction_id` 字段有效
- 适用场景：支付页面轮询、补单机制、批量对账

**轮询示例**：
```python
import time

def wait_for_payment(trade_id, max_wait=300):
    """轮询等待支付完成"""
    start_time = time.time()
    while time.time() - start_time < max_wait:
        order = client.query_order(trade_id=trade_id)
        if order.status == OrderStatus.SUCCESS:
            return True
        elif order.status == OrderStatus.TIMEOUT:
            return False
        time.sleep(5)  # 每5秒查询一次
    return False
```

### 5. 取消订单

```python
result = client.cancel_order(trade_id="xxx")
print(result)
```

## API 文档

### BEpusdtClient

#### 初始化参数

- `api_url` (str): BEpusdt API 地址
- `api_token` (str): API Token
- `timeout` (int, 可选): 请求超时时间，默认 30 秒

#### create_order()

创建支付订单。

**参数**:
- `order_id` (str): 商户订单号，必须唯一
- `amount` (float): 支付金额（CNY）
- `notify_url` (str): 支付回调地址（必须 HTTPS）
- `redirect_url` (str, 可选): 支付成功跳转地址
- `address` (str, 可选): 指定收款地址
- `trade_type` (str, 可选): 支付类型，默认 "usdt.trc20"
  - `"usdt.trc20"` - USDT (TRC20)
  - `"tron.trx"` - TRX
- `timeout` (int, 可选): 订单超时时间（秒）
- `rate` (float, 可选): 自定义汇率

**返回**: `Order` 对象

**异常**: `APIError`

#### cancel_order()

取消订单。

**参数**:
- `trade_id` (str): BEpusdt 交易ID

**返回**: dict

**异常**: `APIError`

#### query_order()

查询订单状态。

**参数**:
- `trade_id` (str): BEpusdt 交易ID

**返回**: `Order` 对象

**异常**: `APIError`

**注意**: 
- 此接口不需要签名验证
- 返回的 Order 对象中，只有 `trade_id`、`status` 和 `block_transaction_id` 字段有效
- 其他字段（如 `order_id`、`amount` 等）为默认值

#### verify_callback()

验证支付回调签名。

**参数**:
- `callback_data` (dict): 回调数据

**返回**: bool

### Order 对象

订单信息对象。

**属性**:
- `trade_id` (str): BEpusdt 交易ID
- `order_id` (str): 商户订单号
- `amount` (float): 请求金额（CNY）
- `actual_amount` (float): 实际支付金额（USDT/TRX）
- `token` (str): 收款地址
- `expiration_time` (int): 过期时间（秒）
- `payment_url` (str): 支付链接
- `status` (OrderStatus, 可选): 订单状态
- `block_transaction_id` (str, 可选): 区块链交易ID

### OrderStatus 枚举

订单状态枚举。

- `OrderStatus.WAITING = 1` - 等待支付
- `OrderStatus.SUCCESS = 2` - 支付成功
- `OrderStatus.TIMEOUT = 3` - 支付超时

### 异常

- `BEpusdtError` - SDK 基础异常
- `SignatureError` - 签名错误
- `APIError` - API 请求错误

## 回调数据格式

BEpusdt 会向 `notify_url` 发送 POST 请求，数据格式：

```json
{
    "trade_id": "xxx",
    "order_id": "ORDER_20231222_001",
    "amount": 10.0,
    "actual_amount": "5.2",
    "token": "TQhAwH4zSsgP78CdqMNqpEDik988888888",
    "block_transaction_id": "xxx",
    "signature": "xxx",
    "status": 2
}
```

**重要**: 
- 回调地址必须使用 HTTPS，否则会被 301 重定向导致失败
- 验证签名后再处理业务逻辑
- 返回 "ok" 表示成功，返回 "fail" 表示失败

## 完整示例

查看 [examples](examples/) 目录获取更多示例：

- [Flask 集成示例](examples/flask_example.py)
- [FastAPI 集成示例](examples/fastapi_example.py)
- [Django 集成示例](examples/django_example.py)

## 开发

```bash
# 克隆仓库
git clone https://github.com/yourusername/bepusdt-python-sdk.git
cd bepusdt-python-sdk

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 代码格式化
black bepusdt tests
```

## 许可证

MIT License

## 链接

- [BEpusdt 官方](https://github.com/v03413/bepusdt)
- [GitHub](https://github.com/luoyanglang/bepusdt-python-sdk)
- [PyPI](https://pypi.org/project/bepusdt/)
- [问题反馈](https://github.com/luoyanglang/bepusdt-python-sdk/issues)

## 贡献

欢迎提交 Issue 和 Pull Request！
