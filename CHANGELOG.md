# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

[0.2.0]: https://github.com/luoyanglang/bepusdt-python-sdk/releases/tag/v0.2.0
[0.1.0]: https://github.com/luoyanglang/bepusdt-python-sdk/releases/tag/v0.1.0
