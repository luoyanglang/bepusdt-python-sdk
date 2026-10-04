"""数据模型"""

import io
import base64
from enum import IntEnum, Enum
from typing import Optional, Dict, Any, TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from PIL import Image


class OrderStatus(IntEnum):
    """订单状态枚举

    回调行为说明：
        - WAITING (1): 当前上游每 30 秒调度，缓存抑制 60 秒，非精确周期保证
        - SUCCESS (2): 失败进入配置控制的重试队列，默认上限 10
        - TIMEOUT (3)、FAILED (6): best-effort 推送，不进入成功重试队列
        - CANCELED (4)、CONFIRMING (5): 当前取消/确认中路径没有相应推送

    注意：
        枚举有效不代表必然推送。状态 3 之后仍可能确认截止前的交易并变为成功。
        持久接收后返回 HTTP 200/plain ok；当前 Epusdt 只检查 HTTP 200。
    """

    WAITING = 1  # 等待支付
    SUCCESS = 2  # 支付成功
    TIMEOUT = 3  # 支付超时
    CANCELED = 4  # 订单取消
    CONFIRMING = 5  # 等待区块确认
    FAILED = 6  # 交易确认失败


class TradeType(str, Enum):
    """支付类型枚举

    支持的区块链网络和代币类型。
    继承 str 使枚举成员可直接与字符串比较，向后兼容旧代码。
    """

    # USDT
    USDT_TRC20 = "usdt.trc20"  # Tron 网络
    USDT_ERC20 = "usdt.erc20"  # Ethereum 网络
    USDT_POLYGON = "usdt.polygon"  # Polygon 网络
    USDT_BEP20 = "usdt.bep20"  # BSC 网络
    USDT_APTOS = "usdt.aptos"  # Aptos 网络
    USDT_SOLANA = "usdt.solana"  # Solana 网络
    USDT_XLAYER = "usdt.xlayer"  # X-Layer 网络
    USDT_ARBITRUM = "usdt.arbitrum"  # Arbitrum-One 网络
    USDT_PLASMA = "usdt.plasma"  # Plasma 网络
    USDT_TON = "usdt.ton"  # TON 网络

    # USDC
    USDC_TRC20 = "usdc.trc20"  # Tron 网络
    USDC_ERC20 = "usdc.erc20"  # Ethereum 网络
    USDC_POLYGON = "usdc.polygon"  # Polygon 网络
    USDC_BEP20 = "usdc.bep20"  # BSC 网络
    USDC_APTOS = "usdc.aptos"  # Aptos 网络
    USDC_SOLANA = "usdc.solana"  # Solana 网络
    USDC_XLAYER = "usdc.xlayer"  # X-Layer 网络
    USDC_ARBITRUM = "usdc.arbitrum"  # Arbitrum-One 网络
    USDC_BASE = "usdc.base"  # Base 网络

    # 原生代币
    TRON_TRX = "tron.trx"  # TRX (Tron 网络)
    ETH_ERC20 = "ethereum.eth"  # ETH (Ethereum 网络)
    BNB_BEP20 = "bsc.bnb"  # BNB (BSC 网络)
    TON_GRAM = "ton.gram"  # GRAM (TON 网络)


@dataclass
class Order:
    """订单信息

    Attributes:
        trade_id: BEpusdt 交易ID
        order_id: 商户订单号
        amount: 请求金额（法币）
        actual_amount: 实际支付金额（加密货币）
        token: 收款地址
        expiration_time: 过期时间（秒）
        payment_url: 支付链接
        fiat: 法币类型（可选，如 CNY/USD/EUR）
        status: 订单状态（可选）
        block_transaction_id: 区块链交易ID（可选）
        expired_at/created_at: 新版查询的 Unix 时间（可选）
        amount_text/actual_amount_text: 保留响应精度的金额文本（可选）
        trade_type/network/name/reselect/trade_url: 新版查询元数据（可选）
    """

    trade_id: str
    order_id: str
    amount: float
    actual_amount: float
    token: str
    expiration_time: int
    payment_url: str
    fiat: Optional[str] = None
    status: Optional[OrderStatus] = None
    block_transaction_id: Optional[str] = None
    # Additive metadata: old float attributes and constructor positions stay stable.
    expired_at: Optional[int] = None
    created_at: Optional[int] = None
    amount_text: Optional[str] = None
    actual_amount_text: Optional[str] = None
    trade_type: Optional[str] = None
    network: Optional[Dict[str, Any]] = None
    name: Optional[str] = None
    reselect: Optional[bool] = None
    trade_url: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Order":
        """从字典创建订单对象

        Args:
            data: 订单数据字典

        Returns:
            Order: 订单对象
        """
        return cls(
            trade_id=data["trade_id"],
            order_id=data["order_id"],
            amount=float(data["amount"]),
            actual_amount=float(data["actual_amount"]),
            token=data["token"],
            expiration_time=int(data["expiration_time"]),
            payment_url=data["payment_url"],
            fiat=data.get("fiat"),
            status=OrderStatus(data["status"]) if "status" in data else None,
            block_transaction_id=data.get("block_transaction_id"),
            amount_text=str(data["amount"]),
            actual_amount_text=str(data["actual_amount"]),
            trade_type=data.get("trade_type"),
            name=data.get("name"),
        )

    def generate_qrcode(self, box_size: int = 10, border: int = 4) -> "Image.Image":
        """生成收款地址二维码图片

        Args:
            box_size: 每个方块的像素大小，默认 10
            border: 边框宽度（方块数），默认 4

        Returns:
            PIL.Image.Image: 二维码图片对象

        Raises:
            ImportError: 未安装 qrcode 或 pillow 库

        Example:
            >>> order = client.create_order(...)
            >>> qr_image = order.generate_qrcode()
            >>> qr_image.save("payment_qr.png")
        """
        try:
            import qrcode
        except ImportError:
            raise ImportError("生成二维码需要安装 qrcode 库: pip install qrcode[pil]")

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=box_size,
            border=border,
        )
        qr.add_data(self.token)
        qr.make(fit=True)

        return qr.make_image(fill_color="black", back_color="white")

    def get_qrcode_base64(self, box_size: int = 10, border: int = 4, format: str = "PNG") -> str:
        """生成收款地址二维码的 Base64 编码

        Args:
            box_size: 每个方块的像素大小，默认 10
            border: 边框宽度（方块数），默认 4
            format: 图片格式，默认 PNG

        Returns:
            str: Base64 编码的图片数据（不含 data:image 前缀）

        Example:
            >>> order = client.create_order(...)
            >>> qr_base64 = order.get_qrcode_base64()
            >>> # 在 HTML 中使用: <img src="data:image/png;base64,{qr_base64}">
        """
        img = self.generate_qrcode(box_size=box_size, border=border)
        buffer = io.BytesIO()
        img.save(buffer, format=format)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    def get_qrcode_data_uri(self, box_size: int = 10, border: int = 4) -> str:
        """生成收款地址二维码的 Data URI（可直接用于 HTML img src）

        Args:
            box_size: 每个方块的像素大小，默认 10
            border: 边框宽度（方块数），默认 4

        Returns:
            str: Data URI 格式的图片数据

        Example:
            >>> order = client.create_order(...)
            >>> data_uri = order.get_qrcode_data_uri()
            >>> # 直接用于 HTML: <img src="{data_uri}">
        """
        qr_base64 = self.get_qrcode_base64(box_size=box_size, border=border)
        return f"data:image/png;base64,{qr_base64}"
