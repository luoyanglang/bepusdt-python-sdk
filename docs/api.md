# 📖 API 参考文档

完整的 BEpusdt Python SDK API 文档。

## 安装

```bash
pip install bepusdt

# 如需二维码功能
pip install bepusdt[qrcode]
```

## 兼容性

- 历史旧模式基线 f4bdee1 / v1.23.6；显式 current 模式对照官方 aa3bd50。
- 本阶段覆盖商户创建/查询/取消与验签，收银台新增接口留待后续；完整支持表见 [README](../README.md#-兼容性)。本批验证为离线契约测试，不是链上付款或浏览器验收。
- 请求金额仍使用 int/float，上游 JSON 解码为 float64；超过其精度的整数或小数不能保持原始请求精度。金额文本属性保留的是响应值，不是上游不存在的任意精度请求协议。
- SDK 包 metadata 仍允许 Python 3.7+；当前 CI 持续验证 Python 3.8 至
  3.12。

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
- `timeout` (int | float, 可选): 请求超时时间，必须为正数，默认 30 秒
- `max_retries` (int, 可选): 最大重试次数，必须为非负整数，默认 3 次
- `retry_delay` (int | float, 可选): 初始重试延迟（秒），必须为非负数字，默认 1.0 秒（指数退避：1s, 2s, 4s）
- `query_mode` (str, 仅关键字): `legacy`（默认旧 GET）或 `current`（新版 POST Info）；无自动探测/回退。

**重试机制：**
- 网络连接失败 (`NetworkError`) - 自动重试
- 请求超时 (`RequestTimeoutError` / `TimeoutError`) - 自动重试
- 服务器错误 5xx (`ServerError`) - 自动重试
- 客户端错误 4xx (`ClientError`) - 不重试
- 业务错误、响应解析失败、参数验证失败 (`APIError` / `ValidationError`) - 不重试

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
    rate=7.4,  # 可选
    fiat="CNY",  # 可选，法币类型
    name="商品名称"  # 可选
)
```

**参数：**
- `order_id` (str): 商户订单号，必须唯一
- `amount` (int | float): 支付金额（法币）⭐，字符串金额会被本地拒绝
- `notify_url` (str): 支付回调地址（必须 HTTPS）
- `redirect_url` (str, 可选): 支付成功跳转地址
- `trade_type` (str, 可选): 支付类型，默认 `TradeType.USDT_TRC20`
- `address` (str, 可选): 指定收款地址
- `timeout` (int, 可选): 订单超时时间（秒）；当前 Go 网关采用 `180-3600`，传 `0` 或越界值时使用网关配置默认值
- `rate` (int | float | str, 可选): 自定义汇率；数字会转换为字符串后参与签名和发送
- `fiat` (str, 可选): 法币类型，支持 CNY/USD/EUR/GBP/JPY，默认 CNY
- `name` (str, 可选): 商品名称

**返回：** `Order` 对象

**重要说明：**
- `amount` 参数是**人民币金额**，系统会根据汇率自动计算加密货币数量
- 返回的 `order.actual_amount` 是**实际需要支付的加密货币数量**（USDT/USDC/TRX/ETH/BNB/GRAM）
- 例如：`amount=10.0` (10元人民币) → `actual_amount=1.35` (1.35 USDT)

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
TradeType.USDT_TON        # TON

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
TradeType.ETH_ERC20       # ETH (Ethereum)
TradeType.BNB_BEP20       # BNB (BSC)
TradeType.TON_GRAM        # GRAM (TON)
```

### 自定义汇率格式

```python
# 固定汇率
rate=7.4
# 实际请求中会按 Go 网关契约发送为 "7.4"

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
- legacy 的 `trade_hash` / `block_transaction_id` 映射为 `Order.block_transaction_id`；仅 trade_id/status/hash 有效，其他字段保持历史默认值。
- current 发送 `{"trade_id": "..."}` 至 `/api/v1/pay/info`；`money` 是法币金额，`actual_amount` 是加密币数量。
- current 提供 `expired_at/created_at` Unix 时间、`amount_text/actual_amount_text` 精确原文及 `trade_type/network/name/reselect/trade_url` 元数据。既有 float 属性不变。
- `expiration_time=max(0, int(expired_at - 本地当前时间))`，是查询时快照，不是动态倒计时；本地时钟偏差会影响它。
- current 未选方式时 token 为空、actual_amount 为兼容占位 0.0、actual_amount_text 为 None；这不表示已分配零金额付款。
- current 缺原始链上哈希/付款链接，分别用 None/空串明确表示；不从 trade_url 推导。
- Info 受付款端指纹限制，不是签名商户查询。拒绝不重试、不回退后台/旧接口，也不伪造请求身份。
- 订单不存在等业务错误会抛出 `APIError`，并保留网关返回的 `status_code`
  和原始响应
- 非对象 JSON、缺失/矛盾字段、未知状态、无效数字/期限统一抛不重试的 APIError；HTTP 4xx、5xx、网络和超时类别保持原样。

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

若第一次取消已执行但响应丢失，重试可能因当前状态不可取消而报业务错误；
异常不证明没有取消。创建同 ID 也不保证只有一个交易：等待订单可能重建，
过期/取消/失败后可有新 trade_id。请求参数相同的传输重试不等于 exactly-once。

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

**安全边界：**
- `True` 只表示签名有效，不能单独作为发货条件。
- 商户仍须登记创建返回的交易尝试和法币，校验 order_id、amount、实际数额、地址与可接受状态；回调没有 fiat，不能从载荷猜货币。
- 验签成功不代表该交易属于本订单。保留历史已知尝试，不能只接受最新 trade_id；过期后仍可能确认截止前转账。
- 原子持久接收与按商户 order_id 唯一的 outbox 避免两个尝试安排两次履约；工作者还要保证实际发货幂等和失败恢复。
- HTTP 200 在当前 Epusdt 中即为应答成功，正文不参与判断；推荐 plain ok 兼容旧部署，拒绝/存储失败应非 200。
- 等待每 30 秒调度、60 秒缓存抑制；成功重试上限配置控制（默认 10），时间基于确认时间 + 2^notify_num 分钟；3/6 是 best-effort，4/5 无对应通知触发。

**当前网关状态值：**
- `1`: 等待支付
- `2`: 支付成功
- `3`: 支付超时
- `4`: 订单取消
- `5`: 等待区块确认
- `6`: 交易确认失败

---

## 数据模型

### Order

订单对象。

**属性：**
- `trade_id` (str): BEpusdt 交易ID
- `order_id` (str): 商户订单号
- `amount` (float): 请求金额（法币）
- `actual_amount` (float): 实际支付金额（**加密货币 USDT/USDC/TRX/ETH/BNB/GRAM**）⭐
- `token` (str): 收款地址
- `expiration_time` (int): 过期时间（秒）
- `payment_url` (str): 支付链接
- `fiat` (str, 可选): 法币类型（CNY/USD/EUR/GBP/JPY）
- `status` (OrderStatus, 可选): 订单状态
- `block_transaction_id` (str, 可选): 区块链交易ID

**重要：** 用户实际需要支付的是 `actual_amount`（加密货币），而不是 `amount`（人民币）。

### OrderStatus

订单状态枚举。

```python
from bepusdt import OrderStatus

OrderStatus.WAITING = 1   # 等待支付
OrderStatus.SUCCESS = 2   # 支付成功
OrderStatus.TIMEOUT = 3   # 支付超时
OrderStatus.CANCELED = 4     # 订单取消
OrderStatus.CONFIRMING = 5   # 等待区块确认
OrderStatus.FAILED = 6       # 交易确认失败
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

### RequestTimeoutError / TimeoutError

请求超时（可重试）。

`TimeoutError` 是 `RequestTimeoutError` 的向后兼容别名。

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
    NetworkError, RequestTimeoutError, ServerError, ClientError, APIError
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
    
except RequestTimeoutError as e:
    # 请求超时（已重试 3 次）
    print(f"❌ 超时: {e}")
    
except ServerError as e:
    # 服务器错误（已重试 3 次）
    print(f"❌ 服务器错误 {e.status_code}: {e}")
    
except ClientError as e:
    # 客户端错误（不会重试）
    print(f"❌ 请求错误 {e.status_code}: {e}")

except APIError as e:
    # 业务错误或响应解析失败（不会重试）
    print(f"❌ API 错误: {e}")
    
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
- 必须验证签名，并校验本地订单号、金额和订单状态
- 支付成功处理必须幂等，避免重复回调或手动重试导致重复发货
- 返回 `"ok"` 表示成功，返回 `"fail"` 表示失败
