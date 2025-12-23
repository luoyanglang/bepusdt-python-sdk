# BEpusdt SDK 重要注意事项

## ⚠️ 关键修复说明

本 SDK 已针对 BEpusdt API 的实际行为进行了修复，以下是关键注意事项：

### 1. redirect_url 参数

**问题**: BEpusdt API 要求 `redirect_url` 为必需参数，但文档中标注为可选。

**解决方案**: 
- 当 `redirect_url` 为 `None` 时，自动使用 `notify_url` 作为默认值
- 确保每次请求都包含 `redirect_url` 参数

```python
# ✅ 正确用法
order = client.create_order(
    order_id="ORDER_001",
    amount=29,
    notify_url="https://your-domain.com/callback"
    # redirect_url 会自动使用 notify_url
)

# ✅ 也可以显式指定
order = client.create_order(
    order_id="ORDER_001",
    amount=29,
    notify_url="https://your-domain.com/callback",
    redirect_url="https://your-domain.com/success"
)
```

### 2. amount 参数类型

**问题**: BEpusdt 的签名算法会跳过空值，浮点数和整数的字符串表示不同导致签名不匹配。

**解决方案**:
- SDK 会自动将整数值的浮点数转换为整数（29.0 → 29）
- 保留真正的小数（29.5 保持为 29.5）

```python
# ✅ 这些都可以正常工作
order = client.create_order(amount=29)      # 整数
order = client.create_order(amount=29.0)    # 会转换为 29
order = client.create_order(amount=29.5)    # 保持 29.5
```

**签名计算示例**:
```python
# 整数: amount=29
# 签名字符串: amount=29&notify_url=...&order_id=...&redirect_url=...&trade_type=...{token}

# 浮点数: amount=29.0
# 签名字符串: amount=29.0&notify_url=...&order_id=...&redirect_url=...&trade_type=...{token}
# ❌ 签名不同！
```

### 3. 回调处理

**问题**: BEpusdt 会发送多种状态的回调，不只是支付成功。

**状态码**:
- `1` - 订单已创建，等待支付
- `2` - 支付成功
- `3` - 订单超时

**正确处理方式**:
```python
@app.route('/api/payment/callback', methods=['POST'])
def payment_callback():
    data = request.get_json()
    
    # 验证签名
    if not client.verify_callback(data):
        return "fail", 400
    
    status = data['status']
    
    if status == 2:
        # 支付成功，处理业务逻辑
        activate_subscription(data['order_id'])
    elif status == 1:
        # 等待支付，正常状态
        pass
    elif status == 3:
        # 订单超时
        cancel_order(data['order_id'])
    
    # ⚠️ 重要：所有状态都应该返回 "ok"
    # 否则 BEpusdt 会认为回调失败并重复发送
    return "ok", 200
```

### 4. 钱包地址配置

**问题**: BEpusdt 需要预先配置钱包地址才能创建订单。

**BEpusdt 配置文件** (`conf.toml`):
```toml
[pay]
wallet_address = [
    "tron.trx:TQhAwH4zSsgP78CdqMNqpEDik988888888",
    "usdt.trc20:TQhAwH4zSsgP78CdqMNqpEDik988888888",
    "usdc.trc20:TQhAwH4zSsgP78CdqMNqpEDik988888888",
]
```

**注意**:
- 如果创建 TRX 订单但未配置 TRX 地址，会返回 400 错误
- 每种支付类型都需要单独配置钱包地址

### 5. 签名算法细节

BEpusdt 的签名算法会**跳过空值和空字符串**：

```python
# Go 代码逻辑
for k, v := range params {
    if v == nil || v == "" {
        continue  // 跳过空值
    }
    // 拼接到签名字符串
}
```

**影响**:
- 不要传递空字符串参数
- 可选参数如果为空，不要添加到 params 中
- 否则会导致签名不匹配

### 6. HTTPS 要求

**问题**: BEpusdt 要求回调地址必须是 HTTPS。

**解决方案**:
- 使用 Nginx 反向代理配置 HTTPS
- 或使用域名配置 SSL 证书
- 不能使用 HTTP，否则会被 301 重定向导致回调失败

```nginx
# Nginx 配置示例
server {
    listen 443 ssl;
    server_name kf.riyu.cc;
    
    location /api/payment/callback {
        proxy_pass http://localhost:5001;
    }
}
```

## 🎯 最佳实践

### 1. 测试流程

```python
# 1. 先用小金额测试（1 TRX ≈ 0.1 元）
order = client.create_order(
    order_id=f"TEST_{int(time.time())}",
    amount=1,  # 1 元
    notify_url="https://your-domain.com/callback",
    trade_type="tron.trx"
)

# 2. 验证回调是否正常接收
# 3. 确认订阅是否自动激活
# 4. 再使用真实金额
```

### 2. 错误处理

```python
try:
    order = client.create_order(...)
except APIError as e:
    if e.status_code == 400:
        # 参数错误或签名错误
        logger.error(f"参数错误: {e.response}")
    elif e.status_code == 401:
        # Token 错误
        logger.error("API Token 无效")
    else:
        # 其他错误
        logger.error(f"创建订单失败: {e}")
```

### 3. 日志记录

建议记录以下信息用于排查问题：
- 订单创建请求参数（脱敏）
- BEpusdt API 响应
- 回调接收时间和数据
- 订阅激活结果

## 📞 故障排查

### 问题：400 Bad Request

**可能原因**:
1. API Token 错误
2. 签名计算错误
3. 参数缺失或格式错误
4. 钱包地址未配置

**排查步骤**:
1. 检查 API Token 是否正确
2. 检查 BEpusdt 配置文件中的钱包地址
3. 查看 BEpusdt 日志：`docker logs bepusdt`
4. 使用 curl 直接测试 API

### 问题：回调未收到

**可能原因**:
1. 回调地址不是 HTTPS
2. 防火墙阻止
3. Nginx 配置错误

**排查步骤**:
1. 检查回调服务日志：`docker logs payment-webhook`
2. 测试回调地址是否可访问：`curl https://kf.riyu.cc/api/payment/callback`
3. 检查 Nginx 配置和日志

### 问题：订阅未激活

**可能原因**:
1. 回调返回了 "fail"
2. 数据库更新失败
3. 订单状态不正确

**排查步骤**:
1. 查看回调日志中的错误信息
2. 检查数据库中的订单状态
3. 手动查询订单：`SELECT * FROM payment_orders WHERE order_id='...'`

## 🔗 相关链接

- BEpusdt 官方文档: https://github.com/v03413/bepusdt
- BEpusdt 示例配置: `BEpusdt-main/conf.simple.toml`
- 支付服务代码: `shared/services/payment_service.py`
- 回调服务代码: `payment_webhook.py`
