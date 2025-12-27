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


class NetworkError(BEpusdtError):
    """网络连接错误（可重试）"""
    pass


class TimeoutError(BEpusdtError):
    """请求超时错误（可重试）"""
    pass


class ServerError(BEpusdtError):
    """服务器错误 5xx（可重试）"""
    
    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code


class ClientError(BEpusdtError):
    """客户端错误 4xx（不可重试）"""
    
    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code


class ValidationError(BEpusdtError):
    """参数验证错误"""
    pass
