"""Flask 集成示例"""

from flask import Flask, jsonify, request

from bepusdt import BEpusdtClient

app = Flask(__name__)

# 初始化客户端
client = BEpusdtClient(api_url="https://your-bepusdt-server.com", api_token="your-api-token")

# 示例内存状态仅用于演示。生产环境请替换为数据库事务和唯一约束。
created_orders = {}
processed_trade_ids = set()


@app.route("/create_payment", methods=["POST"])
def create_payment():
    """创建支付订单"""
    data = request.get_json(silent=True) or {}
    order_id = data.get("order_id")
    amount = data.get("amount")

    if not order_id or amount is None:
        return jsonify({"success": False, "error": "invalid request"}), 400

    try:
        order = client.create_order(
            order_id=order_id,
            amount=amount,
            notify_url="https://your-domain.com/api/payment/notify",
            redirect_url="https://your-domain.com/payment/success",
            trade_type=data.get("trade_type", "usdt.trc20"),
        )
    except Exception:
        app.logger.exception("create payment failed")
        return jsonify({"success": False, "error": "payment creation failed"}), 502

    created_orders[order_id] = float(amount)
    return jsonify(
        {
            "success": True,
            "payment_url": order.payment_url,
            "amount": order.actual_amount,
            "address": order.token,
        }
    )


@app.route("/api/payment/notify", methods=["POST"])
def payment_notify():
    """支付回调"""
    callback_data = request.get_json(silent=True)

    if not client.verify_callback(callback_data):
        return "fail", 400

    order_id = callback_data.get("order_id")
    trade_id = callback_data.get("trade_id")
    status = callback_data.get("status")
    expected_amount = created_orders.get(order_id)

    if expected_amount is None or float(callback_data.get("amount", -1)) != expected_amount:
        return "fail", 400

    if status == 2 and trade_id not in processed_trade_ids:
        # 生产环境请使用数据库原子更新，确保重复回调不会重复发货。
        processed_trade_ids.add(trade_id)
        app.logger.info("payment succeeded for order %s", order_id)

    return "ok", 200


if __name__ == "__main__":
    app.run(debug=False)
