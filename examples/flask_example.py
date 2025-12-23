"""Flask 集成示例"""

from flask import Flask, request, jsonify
from bepusdt import BEpusdtClient

app = Flask(__name__)

# 初始化客户端
client = BEpusdtClient(
    api_url="https://pay.kuaijieyi.com",
    api_token="your-api-token"
)


@app.route('/create_payment', methods=['POST'])
def create_payment():
    """创建支付订单"""
    data = request.get_json()
    
    try:
        order = client.create_order(
            order_id=data['order_id'],
            amount=data['amount'],
            notify_url="https://your-domain.com/api/payment/notify",
            redirect_url="https://your-domain.com/payment/success",
            trade_type=data.get('trade_type', 'usdt.trc20')
        )
        
        return jsonify({
            "success": True,
            "payment_url": order.payment_url,
            "amount": order.actual_amount,
            "address": order.token
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400


@app.route('/api/payment/notify', methods=['POST'])
def payment_notify():
    """支付回调"""
    callback_data = request.get_json()
    
    # 验证签名
    if not client.verify_callback(callback_data):
        return "fail", 400
    
    # 处理支付
    order_id = callback_data['order_id']
    status = callback_data['status']
    
    if status == 2:  # 支付成功
        print(f"订单 {order_id} 支付成功")
        # 更新订单状态、开通会员等业务逻辑
    
    return "ok", 200


if __name__ == '__main__':
    app.run(debug=True)
