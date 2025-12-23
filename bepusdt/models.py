"""数据模型"""

from enum import IntEnum
from typing import Optional
from dataclasses import dataclass


class OrderStatus(IntEnum):
    """订单状态枚举"""
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
