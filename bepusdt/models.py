"""数据模型"""

import io
import base64
from enum import IntEnum
from typing import Optional, TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from PIL import Image


class OrderStatus(IntEnum):
    """订单状态枚举
    
    回调行为说明：
        - WAITING (1): 订单创建后每分钟推送一次，直到支付或超时，不重试
        - SUCCESS (2): 支付成功后推送，失败会重试（间隔 2,4,8,16...分钟，最多10次）
        - TIMEOUT (3): 订单超时后推送一次，不重试
    
    注意：
        商户端收到回调后，应返回状态码 200 和内容 "ok" 表示接收成功
    """
    WAITING = 1  # 等待支付
    SUCCESS = 2  # 支付成功
    TIMEOUT = 3  # 支付超时


class TradeType:
    """支付类型常量
    
    支持的区块链网络和代币类型
    """
    # USDT
    USDT_TRC20 = "usdt.trc20"      # Tron 网络
    USDT_ERC20 = "usdt.erc20"      # Ethereum 网络
    USDT_POLYGON = "usdt.polygon"  # Polygon 网络
    USDT_BEP20 = "usdt.bep20"      # BSC 网络
    USDT_APTOS = "usdt.aptos"      # Aptos 网络
    USDT_SOLANA = "usdt.solana"    # Solana 网络
    USDT_XLAYER = "usdt.xlayer"    # X-Layer 网络
    USDT_ARBITRUM = "usdt.arbitrum"  # Arbitrum-One 网络
    USDT_PLASMA = "usdt.plasma"    # Plasma 网络
    
    # USDC
    USDC_TRC20 = "usdc.trc20"      # Tron 网络
    USDC_ERC20 = "usdc.erc20"      # Ethereum 网络
    USDC_POLYGON = "usdc.polygon"  # Polygon 网络
    USDC_BEP20 = "usdc.bep20"      # BSC 网络
    USDC_APTOS = "usdc.aptos"      # Aptos 网络
    USDC_SOLANA = "usdc.solana"    # Solana 网络
    USDC_XLAYER = "usdc.xlayer"    # X-Layer 网络
    USDC_ARBITRUM = "usdc.arbitrum"  # Arbitrum-One 网络
    USDC_BASE = "usdc.base"        # Base 网络
    
    # 其他
    TRON_TRX = "tron.trx"          # TRX


@dataclass
class Order:
    """订单信息
    
    Attributes:
        trade_id: BEpusdt 交易ID
        order_id: 商户订单号
        amount: 请求金额（CNY）
        actual_amount: 实际支付金额（USDT/TRX/USDC）
        token: 收款地址
        expiration_time: 过期时间（秒）
        payment_url: 支付链接
        status: 订单状态（可选）
        block_transaction_id: 区块链交易ID（可选）
    """
    trade_id: str
    order_id: str
    amount: float
    actual_amount: float
    token: str
    expiration_time: int
    payment_url: str
    status: Optional[OrderStatus] = None
    block_transaction_id: Optional[str] = None
    
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
            status=OrderStatus(data["status"]) if "status" in data else None,
            block_transaction_id=data.get("block_transaction_id")
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
            raise ImportError(
                "生成二维码需要安装 qrcode 库: pip install qrcode[pil]"
            )
        
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
