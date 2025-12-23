"""FastAPI 集成示例"""

from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from bepusdt import BEpusdtClient

app = FastAPI()

# 初始化客户端
client = BEpusdtClient(
    api_url="https://pay.kuaijieyi.com",
    api_token="your-api-token"
)


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
            trade_type=req.trade_type
        )
        
        return {
            "success": True,
            "payment_url": order.payment_url,
            "amount": order.actual_amount,
            "address": order.token
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.post("/api/payment/notify")
async def payment_notify(request: Request):
    """支付回调"""
    callback_data = await request.json()
    
    # 验证签名
    if not client.verify_callback(callback_data):
        return PlainTextResponse(content="fail", status_code=400)
    
    # 处理支付
    order_id = callback_data['order_id']
    status = callback_data['status']
    
    if status == 2:  # 支付成功
        print(f"订单 {order_id} 支付成功")
        # 更新订单状态、开通会员等业务逻辑
    
    return PlainTextResponse(content="ok", status_code=200)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
