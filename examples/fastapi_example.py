"""FastAPI 集成示例"""

import logging
import os

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool

from bepusdt import BEpusdtClient

if __package__:
    from .callback_store import CallbackStore
else:
    from callback_store import CallbackStore

app = FastAPI()
logger = logging.getLogger(__name__)

# 初始化客户端
client = BEpusdtClient(api_url="https://your-bepusdt-server.com", api_token="your-api-token")

store = CallbackStore(os.environ.get("BEPUSDT_EXAMPLE_DB"))


class CreatePaymentRequest(BaseModel):
    order_id: str
    amount: float
    trade_type: str = "usdt.trc20"


@app.post("/create_payment")
def create_payment(req: CreatePaymentRequest):
    """创建支付订单"""
    try:
        store.reserve(req.order_id, req.amount)
        order = client.create_order(
            order_id=req.order_id,
            amount=req.amount,
            notify_url="https://your-domain.com/api/payment/notify",
            redirect_url="https://your-domain.com/payment/success",
            trade_type=req.trade_type,
        )
        store.register(order)
    except Exception:
        logger.exception("create payment failed")
        return JSONResponse({"success": False, "error": "payment creation failed"}, status_code=502)

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

    try:
        accepted = await run_in_threadpool(store.accept, callback_data)
    except Exception:
        logger.exception("callback acceptance failed")
        return PlainTextResponse(content="fail", status_code=503)
    if not accepted:
        return PlainTextResponse(content="fail", status_code=400)
    return PlainTextResponse(content="ok", status_code=200)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
