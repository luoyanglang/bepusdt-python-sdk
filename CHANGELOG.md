# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.1] - 2026-01-11

### Added
- 同步支持 BEpusdt v1.23.0
- 新增 ETH 原生代币支持 (`TradeType.ETH_ERC20`)
- 新增 BNB 原生代币支持 (`TradeType.BNB_BEP20`)
- `create_order()` 新增 `fiat` 参数，支持多法币类型 (CNY/USD/EUR/GBP/JPY)
- `create_order()` 新增 `name` 参数，支持设置商品名称
- `Order` 模型新增 `fiat` 字段

## [0.2.3] - 2026-01-01

### Added
- 新增二维码生成功能，支持生成收款地址二维码
- `Order.generate_qrcode()` - 生成二维码 PIL Image 对象
- `Order.get_qrcode_base64()` - 生成 Base64 编码的二维码
- `Order.get_qrcode_data_uri()` - 生成可直接用于 HTML img src 的 Data URI
- 新增可选依赖 `qrcode`：`pip install bepusdt[qrcode]`

## [0.2.2] - 2025-12-27

### Added
- 新增自动重试机制，支持网络错误、超时、服务器错误自动重试
- 新增 5 种异常类型：`NetworkError`、`TimeoutError`、`ServerError`、`ClientError`、`ValidationError`
- 新增 `max_retries` 和 `retry_delay` 配置参数
- 新增重试机制示例代码 `examples/retry_example.py`

### Changed
- 优化错误处理，根据 HTTP 状态码抛出不同异常
- 改进 `_post()` 和 `_get()` 方法，集成重试机制
- 更新 API 文档，添加重试机制和异常处理说明

### Fixed
- 提升网络不稳定环境下的请求成功率


## [0.2.1] - 2025-12-23

### Changed
- 优化 SDK 初始化信息显示，改为进程级别只显示一次，添加 emoji 标识
- 改用标准 User-Agent header，移除自定义 header，提升兼容性
- 调试日志改为 DEBUG 级别，并对签名进行脱敏处理，提升安全性

### Added
- 完善 OrderStatus 枚举文档，详细说明 3 种回调状态的行为差异
- 完善 verify_callback 方法文档，添加回调处理示例和注意事项

## [0.2.0] - 2025-12-23

### Added
- 新增 `query_order()` 方法，支持查询订单状态
- 新增查询订单示例代码 `examples/query_order_example.py`
- 新增 `_get()` 内部方法支持 GET 请求

### Changed
- 更新 README 文档，添加查询订单使用说明

## [0.1.0] - 2025-12-23

### Added
- 初始版本发布
- 支持创建支付订单（USDT/TRX/USDC）
- 支持 10+ 区块链网络
- 自动签名验证
- 完整的类型提示
- 订单取消功能
- 回调签名验证
- 自定义汇率支持
- Flask 和 FastAPI 集成示例

### Fixed
- 修复 redirect_url 必需参数问题
- 修复 amount 参数类型导致的签名错误
- 优化签名算法，正确处理空值

[0.2.2]: https://github.com/luoyanglang/bepusdt-python-sdk/releases/tag/v0.2.2
[0.2.1]: https://github.com/luoyanglang/bepusdt-python-sdk/releases/tag/v0.2.1
[0.2.0]: https://github.com/luoyanglang/bepusdt-python-sdk/releases/tag/v0.2.0
[0.1.0]: https://github.com/luoyanglang/bepusdt-python-sdk/releases/tag/v0.1.0
