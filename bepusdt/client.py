"""BEpusdt 客户端"""

import requests
from typing import Optional, Dict, Any, List
from .signature import generate_signature, verify_signature
from .models import Order, TradeType
from .exceptions import APIError


class BEpusdtClient:
    """BEpusdt 支付网关客户端
    
    Args:
        api_url: BEpusdt API 地址
        api_token: API Token
        timeout: 请求超时时间（秒），默认 30
    
    Example:
        >>> client = BEpusdtClient(
        ...     api_url="https://your-bepusdt-server.com",
        ...     api_token="your-api-token"
        ... )
        >>> order = client.create_order(
        ...     order_id="ORDER_001",
        ...     amount=10.0,
        ...     notify_url="https://your-domain.com/notify"
        ... )
    """
    
    def __init__(self, api_url: str, api_token: str, timeout: int = 30):
        self.api_url = api_url.rstrip("/")
        self.api_token = api_token
        self.timeout = timeout
        self.session = requests.Session()
    
    def create_order(
        self,
        order_id: str,
        amount: float,
        notify_url: str,
        redirect_url: Optional[str] = None,
        address: Optional[str] = None,
        trade_type: str = TradeType.USDT_TRC20,
        timeout: Optional[int] = None,
        rate: Optional[float] = None
    ) -> Order:
        """创建支付订单
        
        使用相同订单号创建订单时，不会产生两个交易；会根据实际参数重建订单。
        
        Args:
            order_id: 商户订单号，必须唯一
            amount: 支付金额（CNY）
            notify_url: 支付回调地址（必须 HTTPS）
            redirect_url: 支付成功跳转地址（可选）
            address: 指定收款地址（可选）
            trade_type: 支付类型，默认 "usdt.trc20"
                支持的类型：
                - USDT: usdt.trc20, usdt.erc20, usdt.polygon, usdt.bep20, 
                        usdt.aptos, usdt.solana, usdt.xlayer, usdt.arbitrum, usdt.plasma
                - USDC: usdc.trc20, usdc.erc20, usdc.polygon, usdc.bep20,
                        usdc.aptos, usdc.solana, usdc.xlayer, usdc.arbitrum, usdc.base
                - 其他: tron.trx
            timeout: 订单超时时间（秒，最低60，可选）
            rate: 自定义汇率（可选）
                - 固定汇率：7.4 表示固定 7.4
                - 浮动汇率：~1.02 表示最新汇率上浮 2%，~0.97 表示下浮 3%
                - 增减汇率：+0.3 表示最新加 0.3，-0.2 表示最新减 0.2
        
        Returns:
            Order: 订单对象
        
        Raises:
            APIError: API 请求失败
        
        Example:
            >>> # USDT TRC20 支付
            >>> order = client.create_order(
            ...     order_id="ORDER_001",
            ...     amount=10.0,
            ...     notify_url="https://your-domain.com/notify",
            ...     trade_type=TradeType.USDT_TRC20
            ... )
            
            >>> # TRX 支付
            >>> order = client.create_order(
            ...     order_id="ORDER_002",
            ...     amount=1.0,
            ...     notify_url="https://your-domain.com/notify",
            ...     trade_type=TradeType.TRON_TRX
            ... )
            
            >>> # 自定义汇率（上浮2%）
            >>> order = client.create_order(
            ...     order_id="ORDER_003",
            ...     amount=10.0,
            ...     notify_url="https://your-domain.com/notify",
            ...     rate="~1.02"
            ... )
        """
        params = {
            "order_id": order_id,
            "amount": int(amount) if amount == int(amount) else amount,
            "notify_url": notify_url,
            "trade_type": trade_type
        }
        
        # redirect_url 是必需的，但不能为空字符串（BEpusdt会跳过空值导致签名不匹配）
        if redirect_url:
            params["redirect_url"] = redirect_url
        else:
            # 使用 notify_url 作为默认值
            params["redirect_url"] = notify_url
        if address:
            params["address"] = address
        if timeout:
            params["timeout"] = timeout
        if rate:
            params["rate"] = rate
        
        params["signature"] = generate_signature(params, self.api_token)
        
        # 调试日志
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"创建订单请求参数: {params}")
        
        url = f"{self.api_url}/api/v1/order/create-transaction"
        response = self._post(url, params)
        
        if response["status_code"] != 200:
            raise APIError(
                response.get("message", "创建订单失败"),
                status_code=response["status_code"],
                response=response
            )
        
        return Order.from_dict(response["data"])
    
    def cancel_order(self, trade_id: str) -> Dict[str, Any]:
        """取消订单
        
        取消后，系统将不再监控此订单，同时释放对应金额占用。
        
        Args:
            trade_id: BEpusdt 交易ID
        
        Returns:
            dict: 取消结果
        
        Raises:
            APIError: API 请求失败
        
        Example:
            >>> result = client.cancel_order(trade_id="xxx")
        """
        params = {"trade_id": trade_id}
        params["signature"] = generate_signature(params, self.api_token)
        
        url = f"{self.api_url}/api/v1/order/cancel-transaction"
        response = self._post(url, params)
        
        if response["status_code"] != 200:
            raise APIError(
                response.get("message", "取消订单失败"),
                status_code=response["status_code"],
                response=response
            )
        
        return response["data"]
    
    def query_order(self, trade_id: str) -> Order:
        """查询订单状态
        
        查询指定订单的当前状态和详细信息。
        注意：此接口不需要签名验证。
        
        Args:
            trade_id: BEpusdt 交易ID
        
        Returns:
            Order: 订单对象，包含当前状态
        
        Raises:
            APIError: API 请求失败或订单不存在
        
        Example:
            >>> order = client.query_order(trade_id="xxx")
            >>> if order.status == OrderStatus.SUCCESS:
            ...     print("订单已支付")
        """
        url = f"{self.api_url}/pay/check-status/{trade_id}"
        response = self._get(url)
        
        # check-status 接口返回格式不同，需要特殊处理
        if "trade_id" not in response:
            raise APIError("订单不存在或查询失败", response=response)
        
        # 构造 Order 对象需要的数据
        # 注意：查询接口返回的字段较少，某些字段会是默认值
        order_data = {
            "trade_id": response["trade_id"],
            "order_id": "",  # 查询接口不返回此字段
            "amount": 0,  # 查询接口不返回此字段
            "actual_amount": 0,  # 查询接口不返回此字段
            "token": "",  # 查询接口不返回此字段
            "expiration_time": 0,  # 查询接口不返回此字段
            "payment_url": "",  # 查询接口不返回此字段
            "status": response["status"],
            "block_transaction_id": response.get("trade_hash", "")
        }
        
        return Order.from_dict(order_data)
    
    def verify_callback(self, callback_data: Dict[str, Any]) -> bool:
        """验证支付回调签名
        
        Args:
            callback_data: 回调数据字典
        
        Returns:
            bool: 签名是否有效
        
        Example:
            >>> callback_data = request.get_json()
            >>> if client.verify_callback(callback_data):
            ...     # 处理支付成功
            ...     pass
        """
        received_signature = callback_data.get("signature")
        if not received_signature:
            return False
        
        params = {k: v for k, v in callback_data.items() if k != "signature"}
        return verify_signature(params, self.api_token, received_signature)
    
    def _post(self, url: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """发送 POST 请求
        
        Args:
            url: 请求 URL
            data: 请求数据
        
        Returns:
            dict: 响应数据
        
        Raises:
            APIError: 请求失败或响应解析失败
        """
        try:
            resp = self.session.post(url, json=data, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            raise APIError(f"请求失败: {str(e)}")
        except ValueError as e:
            raise APIError(f"响应解析失败: {str(e)}")
    
    def _get(self, url: str) -> Dict[str, Any]:
        """发送 GET 请求
        
        Args:
            url: 请求 URL
        
        Returns:
            dict: 响应数据
        
        Raises:
            APIError: 请求失败或响应解析失败
        """
        try:
            resp = self.session.get(url, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            raise APIError(f"请求失败: {str(e)}")
        except ValueError as e:
            raise APIError(f"响应解析失败: {str(e)}")
