# 📚 使用示例

完整的使用示例和集成指南。

## 基础示例

### 创建 USDT 订单

```python
from bepusdt import BEpusdtClient, TradeType

client = BEpusdtClient(
    api_url="https://your-bepusdt-server.com",
    api_token="your-api-token"
)

order = client.create_order(
    order_id="ORDER_001",
    amount=10.0,
    notify_url="https://your-domain.com/notify",
    trade_type=TradeType.USDT_TRC20
)

print(f"支付金额: {order.actual_amount} USDT")
print(f"收款地址: {order.token}")
```

### 创建 TRX 订单

```python
order = client.create_order(
    order_id="ORDER_002",
    amount=1.0,
    notify_url="https://your-domain.com/notify",
    trade_type=TradeType.TRON_TRX
)
```

### 自定义汇率

```python
# 固定汇率
order = client.create_order(
    order_id="ORDER_003",
    amount=10.0,
    notify_url="https://your-domain.com/notify",
    rate=7.4  # SDK 会按 Go 网关契约发送为 "7.4"
)

# 最新汇率上浮 2%
order = client.create_order(
    order_id="ORDER_004",
    amount=10.0,
    notify_url="https://your-domain.com/notify",
    rate="~1.02"
)
```

### 指定收款地址

```python
order = client.create_order(
    order_id="ORDER_005",
    amount=10.0,
    notify_url="https://your-domain.com/notify",
    address="TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
)
```

## Flask 集成

```python
from flask import Flask, request, jsonify
from bepusdt import BEpusdtClient, OrderStatus

app = Flask(__name__)

client = BEpusdtClient(
    api_url="https://your-bepusdt-server.com",
    api_token="your-api-token"
)

@app.route('/create-payment', methods=['POST'])
def create_payment():
    data = request.get_json()
    
    order = client.create_order(
        order_id=data['order_id'],
        amount=data['amount'],
        notify_url="https://your-domain.com/payment/notify"
    )
    
    return jsonify({
        'payment_url': order.payment_url,
        'amount': order.actual_amount,
        'address': order.token
    })

@app.route('/payment/notify', methods=['POST'])
def payment_notify():
    callback_data = request.get_json(silent=True)
    
    if not client.verify_callback(callback_data):
        return "fail", 400
    
    if callback_data['status'] == 2 and mark_order_paid_once(callback_data):
        # 校验本地订单号、金额、状态流转后，再开通会员或发货
        deliver_order(callback_data['order_id'])
        
    return "ok", 200

if __name__ == '__main__':
    app.run()
```

## FastAPI 集成

```python
from fastapi import FastAPI, Request
from bepusdt import BEpusdtClient, OrderStatus

app = FastAPI()

client = BEpusdtClient(
    api_url="https://your-bepusdt-server.com",
    api_token="your-api-token"
)

@app.post("/create-payment")
async def create_payment(data: dict):
    order = client.create_order(
        order_id=data['order_id'],
        amount=data['amount'],
        notify_url="https://your-domain.com/payment/notify"
    )
    
    return {
        'payment_url': order.payment_url,
        'amount': order.actual_amount,
        'address': order.token
    }

@app.post("/payment/notify")
async def payment_notify(request: Request):
    callback_data = await request.json()
    
    if not client.verify_callback(callback_data):
        return {"status": "fail"}
    
    if callback_data['status'] == 2 and mark_order_paid_once(callback_data):
        # 校验本地订单号、金额、状态流转后，再开通会员或发货
        await deliver_order(callback_data['order_id'])
        
    return {"status": "ok"}
```

## Django 集成

```python
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from bepusdt import BEpusdtClient, OrderStatus
import json

client = BEpusdtClient(
    api_url="https://your-bepusdt-server.com",
    api_token="your-api-token"
)

@csrf_exempt
def create_payment(request):
    data = json.loads(request.body)
    
    order = client.create_order(
        order_id=data['order_id'],
        amount=data['amount'],
        notify_url="https://your-domain.com/payment/notify"
    )
    
    return JsonResponse({
        'payment_url': order.payment_url,
        'amount': order.actual_amount,
        'address': order.token
    })

@csrf_exempt
def payment_notify(request):
    callback_data = json.loads(request.body)
    
    if not client.verify_callback(callback_data):
        return HttpResponse("fail", status=400)
    
    if callback_data['status'] == 2 and mark_order_paid_once(callback_data):
        # 校验本地订单号、金额、状态流转后，再开通会员或发货
        deliver_order(callback_data['order_id'])
        
    return HttpResponse("ok")
```

## 轮询查询订单

```python
import time
from bepusdt import OrderStatus

def wait_for_payment(trade_id, max_wait=300):
    """轮询等待支付完成"""
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        order = client.query_order(trade_id=trade_id)
        
        if order.status == OrderStatus.SUCCESS:
            print("✅ 支付成功")
            return True
        elif order.status == OrderStatus.TIMEOUT:
            print("❌ 订单超时")
            return False
            
        time.sleep(5)  # 每 5 秒查询一次
    
    print("⏰ 等待超时")
    return False

# 使用
success = wait_for_payment("trade_id_xxx")
```

## 批量查询订单

```python
def batch_query_orders(trade_ids):
    """批量查询订单状态"""
    results = {}
    
    for trade_id in trade_ids:
        try:
            order = client.query_order(trade_id=trade_id)
            results[trade_id] = {
                'status': order.status,
                'success': order.status == OrderStatus.SUCCESS
            }
        except Exception as e:
            results[trade_id] = {'error': str(e)}
    
    return results

# 使用
trade_ids = ["trade_1", "trade_2", "trade_3"]
results = batch_query_orders(trade_ids)
```

## 异常处理

```python
from bepusdt import APIError

try:
    order = client.create_order(
        order_id="ORDER_001",
        amount=10.0,
        notify_url="https://your-domain.com/notify"
    )
except APIError as e:
    if e.status_code == 400:
        print(f"参数错误: {e}")
    elif e.status_code == 401:
        print("API Token 无效")
    else:
        print(f"创建订单失败: {e}")
```

## 更多示例

查看 [examples](../examples/) 目录获取完整的示例代码。
