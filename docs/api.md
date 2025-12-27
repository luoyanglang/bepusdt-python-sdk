# 📖 API 参考文档

完整的 BEpusdt Python SDK API 文档。

## 安装

```bash
pip install bepusdt
```

## 初始化客户端

### BEpusdtClient

```python
from bepusdt import BEpusdtClient

client = BEpusdtClient(
    api_url="https://your-bepusdt-server.com",
    api_token="your-api-token",
    timeout=30,         # 可选，默认 30 秒
    max_retries=3,      # 可选，默认 3 次
    retry_delay=1.0     # 可选，默认 1.0 秒
)
```

**参数：**
- `api_url` (str): BEpusdt 服务器地址
- `api_token` (str): API 认证 Token
- `timeout` (int, 可选): 请求超时时间，默认 30 秒
- `max_retries` (int, 可选): 最大重试次数，默认 3 次
- `retry_delay` (float, 可选): 初始重试延迟（秒），默认 1.0 秒（指数退避：1s, 2s, 4s）

**重试机制：**
- 网络连接失败 (`NetworkError`) - 自动重试
- 请求超时 (`TimeoutError`) - 自动重试
- 服务器错误 5xx (`ServerError`) - 自动重试
- 客户端错误 4xx (`ClientError`) - 不重试
- 其他错误 - 不重试

---

## 创建订单

### create_order()

创建支付订单。

```python
order = client.create_order(
    order_id="ORDER_001",
    amount=10.0,
    notify_url="https://your-domain.com/notify",
    redirect_url="https://your-domain.com/success",  # 可选
    trade_type=TradeType.USDT_TRC20,  # 可选
    address="TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t",  # 可选
    timeout=1200,  # 可选
    rate=7.4  # 可选
)
```

**参数：**
- `order_id` (str): 商户订单号，必须唯一
- `amount` (float): 支付金额（CNY）
- `notify_url` (str): 支付回调地址（必须 HTTPS）
- `redirect_url` (str, 可选): 支付成功跳转地址
- `trade_type` (str, 可选): 支付类型，默认 `TradeType.USDT_TRC20`
- `address` (str, 可选): 指定收款地址
- `timeout` (int, 可选): 订单超时时间（秒），最低 60
- `rate` (float | str, 可选): 自定义汇率

**返回：** `Order` 对象

**异常：** `APIError`

### 支付类型 (TradeType)

```python
from bepusdt import TradeType

# USDT
TradeType.USDT_TRC20      # Tron (推荐)
TradeType.USDT_ERC20      # Ethereum
TradeType.USDT_BEP20      # BSC
TradeType.USDT_POLYGON    # Polygon
TradeType.USDT_ARBITRUM   # Arbitrum
TradeType.USDT_SOLANA     # Solana
TradeType.USDT_APTOS      # Aptos
TradeType.USDT_XLAYER     # X-Layer
TradeType.USDT_PLASMA     # Plasma

# USDC
TradeType.USDC_TRC20      # Tron
TradeType.USDC_ERC20      # Ethereum
TradeType.USDC_BEP20      # BSC
TradeType.USDC_POLYGON    # Polygon
TradeType.USDC_ARBITRUM   # Arbitrum
TradeType.USDC_SOLANA     # Solana
TradeType.USDC_APTOS      # Aptos
TradeType.USDC_XLAYER     # X-Layer
TradeType.USDC_BASE       # Base

# 其他
TradeType.TRON_TRX        # TRX
```

### 自定义汇率格式

```python
# 固定汇率
rate=7.4

# 最新汇率上浮 2%
rate="~1.02"

# 最新汇率下浮 3%
rate="~0.97"

# 最新汇率加 0.3
rate="+0.3"

# 最新汇率减 0.2
rate="-0.2"
```

---

## 查询订单

### query_order()

查询订单状态。

```python
order = client.query_order(trade_id="xxx")
```

**参数：**
- `trade_id` (str): BEpusdt 交易ID

**返回：** `Order` 对象

**异常：** `APIError`

**注意：**
- 此接口不需要签名验证
- 返回的 Order 对象中，只有 `trade_id`、`status`、`block_transaction_id` 字段有效
- 其他字段为默认值

---

## 取消订单

### cancel_order()

取消等待中的订单。

```python
result = client.cancel_order(trade_id="xxx")
```

**参数：**
- `trade_id` (str): BEpusdt 交易ID

**返回：** dict

**异常：** `APIError`

---

## 验证回调

### verify_callback()

验证支付回调签名。

```python
callback_data = request.get_json()
is_valid = client.verify_callback(callback_data)
```

**参数：**
- `callback_data` (dict): 回调数据字典

**返回：** bool

---

## 数据模型

### Order

订单对象。

**属性：**
- `trade_id` (str): BEpusdt 交易ID
- `order_id` (str): 商户订单号
- `amount` (float): 请求金额（CNY）
- `actual_amount` (float): 实际支付金额
- `token` (str): 收款地址
- `expiration_time` (int): 过期时间（秒）
- `payment_url` (str): 支付链接
- `status` (OrderStatus, 可选): 订单状态
- `block_transaction_id` (str, 可选): 区块链交易ID

### OrderStatus

订单状态枚举。

```python
from bepusdt import OrderStatus

OrderStatus.WAITING = 1   # 等待支付
OrderStatus.SUCCESS = 2   # 支付成功
OrderStatus.TIMEOUT = 3   # 支付超时
```

---

## 异常

### BEpusdtError

SDK 基础异常类，所有其他异常的父类。

### SignatureError

签名相关错误。

### APIError

通用 API 请求错误。

**属性：**
- `message` (str): 错误消息
- `status_code` (int, 可选): HTTP 状态码
- `response` (dict, 可选): 完整响应数据

### NetworkError

网络连接失败（可重试）。

**使用场景：**
- DNS 解析失败
- 连接被拒绝
- 网络不可达

### TimeoutError

请求超时（可重试）。

**使用场景：**
- 连接超时
- 读取超时

### ServerError

服务器错误 5xx（可重试）。

**属性：**
- `message` (str): 错误消息
- `status_code` (int): HTTP 状态码（500-599）

**使用场景：**
- 500 Internal Server Error
- 502 Bad Gateway
- 503 Service Unavailable

### ClientError

客户端错误 4xx（不可重试）。

**属性：**
- `message` (str): 错误消息
- `status_code` (int): HTTP 状态码（400-499）

**使用场景：**
- 400 Bad Request
- 401 Unauthorized
- 404 Not Found

### ValidationError

参数验证错误（不可重试）。

**使用场景：**
- 参数格式错误
- 必填参数缺失

---

## 错误处理示例

```python
from bepusdt import (
    BEpusdtClient, 
    NetworkError, TimeoutError, ServerError, ClientError
)

client = BEpusdtClient(
    api_url="https://your-server.com",
    api_token="your-token",
    max_retries=3
)

try:
    order = client.create_order(
        order_id="ORDER_001",
        amount=10.0,
        notify_url="https://your-domain.com/notify"
    )
    print(f"✅ 订单创建成功: {order.trade_id}")
    
except NetworkError as e:
    # 网络连接失败（已重试 3 次）
    print(f"❌ 网络错误: {e}")
    
except TimeoutError as e:
    # 请求超时（已重试 3 次）
    print(f"❌ 超时: {e}")
    
except ServerError as e:
    # 服务器错误（已重试 3 次）
    print(f"❌ 服务器错误 {e.status_code}: {e}")
    
except ClientError as e:
    # 客户端错误（不会重试）
    print(f"❌ 请求错误 {e.status_code}: {e}")
    
except Exception as e:
    # 其他错误
    print(f"❌ 未知错误: {e}")
```

---

## 回调数据格式

BEpusdt 会向 `notify_url` 发送 POST 请求：

```json
{
    "trade_id": "xxx",
    "order_id": "ORDER_001",
    "amount": 10.0,
    "actual_amount": "1.35",
    "token": "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t",
    "block_transaction_id": "0x123abc...",
    "signature": "xxx",
    "status": 2
}
```

**状态码：**
- `1` - 等待支付
- `2` - 支付成功
- `3` - 订单超时

**重要：**
- 回调地址必须使用 HTTPS
- 必须验证签名
- 返回 `"ok"` 表示成功，返回 `"fail"` 表示失败
