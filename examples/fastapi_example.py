"""FastAPI 集成示例"""

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel

from bepusdt import BEpusdtClient

app = FastAPI()
logger = logging.getLogger(__name__)

# 初始化客户端
client = BEpusdtClient(api_url="https://your-bepusdt-server.com", api_token="your-api-token")

# 示例内存状态仅用于演示。生产环境请替换为数据库事务和唯一约束。
created_orders = {}
processed_trade_ids = set()


class CreatePaymentRequest(BaseModel):
    order_id: str
    amount: float
    trade_type: str = "usdt.trc20"


@app.post("/create_payment")
async def create_payment(req: CreatePaymentRequest):
    """创建支付订单"""
    try:
        order = client.create_order(
            order_id=req.order_id,
            amount=req.amount,
            notify_url="https://your-domain.com/api/payment/notify",
            redirect_url="https://your-domain.com/payment/success",
            trade_type=req.trade_type,
        )
    except Exception:
        logger.exception("create payment failed")
        return JSONResponse({"success": False, "error": "payment creation failed"}, status_code=502)

    created_orders[req.order_id] = req.amount
    return {
        "success": True,
        "payment_url": order.payment_url,
        "amount": order.actual_amount,
        "address": order.token,
    }


@app.post("/api/payment/notify")
async def payment_notify(request: Request):
    """支付回调"""
    try:
        callback_data = await request.json()
    except ValueError:
        return PlainTextResponse(content="fail", status_code=400)

    if not client.verify_callback(callback_data):
        return PlainTextResponse(content="fail", status_code=400)

    order_id = callback_data.get("order_id")
    trade_id = callback_data.get("trade_id")
    status = callback_data.get("status")
    expected_amount = created_orders.get(order_id)

    if expected_amount is None or float(callback_data.get("amount", -1)) != expected_amount:
        return PlainTextResponse(content="fail", status_code=400)

    if status == 2 and trade_id not in processed_trade_ids:
        # 生产环境请使用数据库原子更新，确保重复回调不会重复发货。
        processed_trade_ids.add(trade_id)
        logger.info("payment succeeded for order %s", order_id)

    return PlainTextResponse(content="ok", status_code=200)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
