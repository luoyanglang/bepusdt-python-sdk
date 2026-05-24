"""BEpusdt 客户端"""

import logging
import requests
from typing import Optional, Dict, Any, Union
from .signature import generate_signature, verify_signature
from .models import Order, TradeType
from .exceptions import APIError, NetworkError, RequestTimeoutError, ServerError, ClientError, ValidationError
from .retry import retry_on_error

logger = logging.getLogger(__name__)


class BEpusdtClient:
    """BEpusdt 支付网关客户端

    Args:
        api_url: BEpusdt API 地址
        api_token: API Token
        timeout: 请求超时时间（秒），默认 30
        max_retries: 最大重试次数，默认 3
        retry_delay: 重试延迟（秒），默认 1.0

    Example:
        >>> client = BEpusdtClient(
        ...     api_url="https://your-bepusdt-server.com",
        ...     api_token="your-api-token",
        ...     max_retries=3
        ... )
        >>> order = client.create_order(
        ...     order_id="ORDER_001",
        ...     amount=10.0,
        ...     notify_url="https://your-domain.com/notify"
        ... )
    """

    def __init__(self, api_url: str, api_token: str, timeout: int = 30, max_retries: int = 3, retry_delay: float = 1.0):
        if not api_url.startswith("https://"):
            raise ValidationError(f"api_url 必须使用 HTTPS 协议（以 https:// 开头），当前值: {api_url!r}")
        self.api_url = api_url.rstrip("/")
        self.api_token = api_token
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.session = requests.Session()

        from . import __version__, __url__

        logger.debug("BEpusdt Python SDK v%s 已初始化，GitHub: %s", __version__, __url__)

    def create_order(
        self,
        order_id: str,
        amount: float,
        notify_url: str,
        redirect_url: Optional[str] = None,
        address: Optional[str] = None,
        trade_type: str = TradeType.USDT_TRC20,
        timeout: Optional[int] = None,
        rate: Optional[Union[float, str]] = None,
        fiat: Optional[str] = None,
        name: Optional[str] = None,
    ) -> Order:
        """创建支付订单

        使用相同订单号创建订单时，不会产生两个交易；会根据实际参数重建订单。

        Args:
            order_id: 商户订单号，必须唯一
            amount: 支付金额（法币）
            notify_url: 支付回调地址（必须 HTTPS）
            redirect_url: 支付成功跳转地址（可选）
            address: 指定收款地址（可选）
            trade_type: 支付类型，默认 "usdt.trc20"
                支持的类型：
                - USDT: usdt.trc20, usdt.erc20, usdt.polygon, usdt.bep20,
                        usdt.aptos, usdt.solana, usdt.xlayer, usdt.arbitrum, usdt.plasma
                - USDC: usdc.trc20, usdc.erc20, usdc.polygon, usdc.bep20,
                        usdc.aptos, usdc.solana, usdc.xlayer, usdc.arbitrum, usdc.base
                - 原生代币: tron.trx, ethereum.eth, bsc.bnb
            timeout: 订单超时时间（秒，最低60，可选）
            rate: 自定义汇率（可选），支持 float 或特殊前缀字符串
                - 固定汇率：7.4（float）或 "7.4"（str）表示固定 7.4
                - 浮动汇率："~1.02" 表示最新汇率上浮 2%，"~0.97" 表示下浮 3%
                - 增减汇率："+0.3" 表示最新加 0.3，"-0.2" 表示最新减 0.2
            fiat: 法币类型（可选），支持 CNY/USD/EUR/GBP/JPY，默认 CNY
            name: 商品名称（可选）

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

            >>> # ETH 支付
            >>> order = client.create_order(
            ...     order_id="ORDER_002",
            ...     amount=100.0,
            ...     notify_url="https://your-domain.com/notify",
            ...     trade_type=TradeType.ETH_ERC20,
            ...     fiat="USD"
            ... )

            >>> # BNB 支付（带商品名称）
            >>> order = client.create_order(
            ...     order_id="ORDER_003",
            ...     amount=50.0,
            ...     notify_url="https://your-domain.com/notify",
            ...     trade_type=TradeType.BNB_BEP20,
            ...     name="VIP会员"
            ... )
        """
        if not notify_url.startswith("https://"):
            raise ValidationError(f"notify_url 必须使用 HTTPS 协议（以 https:// 开头），当前值: {notify_url!r}")
        params = {
            "order_id": order_id,
            "amount": int(amount) if amount == int(amount) else amount,
            "notify_url": notify_url,
            "trade_type": trade_type,
        }

        # redirect_url 是必需的，但不能为空字符串（BEpusdt会跳过空值导致签名不匹配）
        if redirect_url:
            params["redirect_url"] = redirect_url
        else:
            # 使用 notify_url 作为默认值
            params["redirect_url"] = notify_url
        if address:
            params["address"] = address
        if timeout is not None:
            params["timeout"] = timeout
        if rate is not None:
            params["rate"] = rate
        if fiat:
            params["fiat"] = fiat
        if name:
            params["name"] = name

        params["signature"] = generate_signature(params, self.api_token)

        # 调试日志（DEBUG 级别，且脱敏）
        logger = logging.getLogger(__name__)
        if logger.isEnabledFor(logging.DEBUG):
            debug_params = {k: v for k, v in params.items() if k != "signature"}
            debug_params["signature"] = "***"
            logger.debug(f"创建订单请求参数: {debug_params}")

        url = f"{self.api_url}/api/v1/order/create-transaction"
        response = self._post(url, params)

        if response["status_code"] != 200:
            raise APIError(
                response.get("message", "创建订单失败"), status_code=response["status_code"], response=response
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
                response.get("message", "取消订单失败"), status_code=response["status_code"], response=response
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
        if response.get("status_code") and response["status_code"] != 200:
            raise APIError(
                response.get("message", "订单不存在或查询失败"),
                status_code=response["status_code"],
                response=response,
            )
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
            "block_transaction_id": response.get("trade_hash") or response.get("block_transaction_id", ""),
        }

        return Order.from_dict(order_data)

    def verify_callback(self, callback_data: Any) -> bool:
        """验证支付回调签名

        Args:
            callback_data: 回调数据字典，包含以下字段：
                - trade_id: BEpusdt 交易ID
                - order_id: 商户订单号
                - amount: 请求金额（CNY）
                - actual_amount: 实际支付金额（USDT/TRX/USDC）
                - token: 收款地址
                - block_transaction_id: 区块链交易ID
                - status: 订单状态（1=等待支付, 2=支付成功, 3=支付超时）
                - signature: 签名

        Returns:
            bool: 签名是否有效

        回调行为说明：
            - status=1 (等待支付): 订单创建后每分钟推送一次，直到支付或超时，不重试
            - status=2 (支付成功): 支付完成后推送，失败会重试（间隔 2,4,8,16...分钟，最多10次）
            - status=3 (支付超时): 订单超时后推送一次，不重试

        注意：
            验证成功后，应返回 HTTP 200 和内容 "ok"，否则系统会认为回调失败

        Example:
            >>> @app.route('/notify', methods=['POST'])
            >>> def notify():
            ...     data = request.get_json()
            ...     if client.verify_callback(data):
            ...         if data['status'] == OrderStatus.SUCCESS:
            ...             # 处理支付成功
            ...             return "ok", 200
            ...         elif data['status'] == OrderStatus.TIMEOUT:
            ...             # 处理订单超时
            ...             return "ok", 200
            ...     return "fail", 400
        """
        if not isinstance(callback_data, dict):
            return False

        received_signature = callback_data.get("signature")
        if not received_signature:
            return False
        if not isinstance(received_signature, str):
            return False

        params = {k: v for k, v in callback_data.items() if k != "signature"}
        return verify_signature(params, self.api_token, received_signature)

    def _request(self, method: str, url: str, **kwargs: Any) -> Dict[str, Any]:
        """发送 HTTP 请求（带重试）

        Args:
            method: HTTP 方法（"post" 或 "get"）
            url: 请求 URL
            **kwargs: 传递给 requests.Session 的额外参数

        Returns:
            dict: 响应数据

        Raises:
            NetworkError: 网络连接失败
            RequestTimeoutError: 请求超时
            ServerError: 服务器错误 5xx
            ClientError: 客户端错误 4xx
            APIError: 其他 API 错误
        """

        @retry_on_error(
            max_retries=self.max_retries,
            delay=self.retry_delay,
            exceptions=(NetworkError, RequestTimeoutError, ServerError),
        )
        def _do_request():
            try:
                from . import __version__, __url__

                headers = {"User-Agent": f"bepusdt-python-sdk/{__version__} (+{__url__})"}
                resp = getattr(self.session, method)(url, headers=headers, timeout=self.timeout, **kwargs)

                if resp.status_code >= 500:
                    raise ServerError(f"服务器错误: HTTP {resp.status_code}", status_code=resp.status_code)
                elif resp.status_code >= 400:
                    raise ClientError(f"客户端错误: HTTP {resp.status_code}", status_code=resp.status_code)

                resp.raise_for_status()
                return resp.json()

            except requests.exceptions.Timeout as e:
                raise RequestTimeoutError(f"请求超时: {str(e)}")
            except requests.exceptions.ConnectionError as e:
                raise NetworkError(f"网络连接失败: {str(e)}")
            except requests.exceptions.RequestException as e:
                raise APIError(f"请求失败: {str(e)}")
            except ValueError as e:
                raise APIError(f"响应解析失败: {str(e)}")

        return _do_request()

    def _post(self, url: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """发送 POST 请求（带重试）"""
        return self._request("post", url, json=data)

    def _get(self, url: str) -> Dict[str, Any]:
        """发送 GET 请求（带重试）"""
        return self._request("get", url)
