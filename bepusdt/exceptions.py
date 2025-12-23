"""异常定义"""


class BEpusdtError(Exception):
    """BEpusdt SDK 基础异常"""
    pass


class SignatureError(BEpusdtError):
    """签名错误"""
    pass


class APIError(BEpusdtError):
    """API 请求错误
    
    Attributes:
        message: 错误消息
        status_code: HTTP 状态码（可选）
        response: 完整响应数据（可选）
    """
    
    def __init__(self, message: str, status_code: int = None, response: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response
