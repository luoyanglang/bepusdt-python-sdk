"""重试机制使用示例"""

from bepusdt import BEpusdtClient, NetworkError, TimeoutError, ServerError

# 创建客户端，配置重试参数
client = BEpusdtClient(
    api_url="https://your-bepusdt-server.com",
    api_token="your-api-token",
    max_retries=3,      # 最大重试 3 次
    retry_delay=1.0     # 初始延迟 1 秒，后续指数退避（1s, 2s, 4s）
)

try:
    # 创建订单 - 网络错误会自动重试
    order = client.create_order(
        order_id="ORDER_001",
        amount=10.0,
        notify_url="https://your-domain.com/notify"
    )
    print(f"✅ 订单创建成功: {order.trade_id}")
    
except NetworkError as e:
    # 网络连接失败（重试后仍失败）
    print(f"❌ 网络连接失败: {e}")
    
except TimeoutError as e:
    # 请求超时（重试后仍失败）
    print(f"❌ 请求超时: {e}")
    
except ServerError as e:
    # 服务器错误 5xx（重试后仍失败）
    print(f"❌ 服务器错误: {e}")
    
except Exception as e:
    # 其他错误（不会重试）
    print(f"❌ 错误: {e}")
