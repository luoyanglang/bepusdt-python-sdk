"""Flask 集成示例"""

from flask import Flask, jsonify, request
import os

from bepusdt import BEpusdtClient

if __package__:
    from .callback_store import CallbackStore
else:
    from callback_store import CallbackStore

app = Flask(__name__)

# 初始化客户端
client = BEpusdtClient(api_url="https://your-bepusdt-server.com", api_token="your-api-token")

store = CallbackStore(os.environ.get("BEPUSDT_EXAMPLE_DB"))


@app.route("/create_payment", methods=["POST"])
def create_payment():
    """创建支付订单"""
    data = request.get_json(silent=True) or {}
    order_id = data.get("order_id")
    amount = data.get("amount")

    if not order_id or amount is None:
        return jsonify({"success": False, "error": "invalid request"}), 400

    try:
        store.reserve(order_id, amount)
        order = client.create_order(
            order_id=order_id,
            amount=amount,
            notify_url="https://your-domain.com/api/payment/notify",
            redirect_url="https://your-domain.com/payment/success",
            trade_type=data.get("trade_type", "usdt.trc20"),
        )
        store.register(order)
    except Exception:
        app.logger.exception("create payment failed")
        return jsonify({"success": False, "error": "payment creation failed"}), 502

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

    try:
        accepted = store.accept(callback_data)
    except Exception:
        app.logger.exception("callback acceptance failed")
        return "fail", 503
    if not accepted:
        return "fail", 400
    # Durable acceptance precedes acknowledgement; a separate worker fulfills the outbox.
    return "ok", 200


if __name__ == "__main__":
    app.run(debug=False)
