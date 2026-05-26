# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.13] - 2026-05-26

### Fixed
- 修正 `requests.exceptions.JSONDecodeError` 的错误分类；响应 JSON 解析失败现在稳定抛出 `APIError("响应解析失败: ...")`，不再被误归类为底层请求失败。
- `BEpusdtClient` 初始化现在会校验 `timeout`、`max_retries` 和 `retry_delay`，避免无效重试或超时配置进入请求层。
- `retry_on_error()` 现在会拒绝无效的 `max_retries`、`delay` 和 `backoff` 参数，避免负重试次数导致目标函数不执行。

### Tests
- 补充客户端重试语义回归测试，覆盖网络错误、请求超时、HTTP 5xx、HTTP 4xx 和 JSON 解析失败。
- 补充初始化参数和重试装饰器参数校验测试。

### Docs
- 明确自动重试只覆盖 `NetworkError`、`RequestTimeoutError` / `TimeoutError` 和 `ServerError`。
- 明确 `ClientError`、`APIError`、`ValidationError` 和响应解析失败不会自动重试。

## [0.3.12] - 2026-05-25

### Fixed
- `create_order()` 现在会在签名和发送前将数字 `rate` 规范化为字符串，保持与 BEpusdt Go 网关 `rate` 字段契约一致。
- `create_order()` 对 `amount` 和 `timeout` 增加本地类型校验，避免字符串金额或非整数超时生成无效下单请求。

### Tests
- 补充下单参数签名测试，覆盖数字 `rate`、浮动汇率字符串、`timeout`、`redirect_url` 等字段的请求与签名行为。
- 补充支付类型契约测试，确认 SDK `TradeType` 与当前 BEpusdt 网关支持的 21 个交易类型一致。
- 补充非法 `amount` / `timeout` 参数回归测试。

### Docs
- 更新 `create_order()` 参数说明，明确 `rate` 的字符串化规则。
- 将订单超时时间说明对齐到当前 Go 网关行为：`180-3600` 秒由网关采用，越界或 `0` 使用网关配置默认值。
- 明确字符串金额会被 SDK 本地拒绝。

## [0.3.11] - 2026-05-24

### Fixed
- `query_order()` 现在兼容查询响应中的 `block_transaction_id` 字段别名；当前上游网关仍返回 `trade_hash`，两种字段都会映射到 `Order.block_transaction_id`。
- `query_order()` 收到上游业务错误包装时会保留 `message`、`status_code` 和原始响应，便于调用方区分订单不存在等业务失败。

### Tests
- 补充 `/pay/check-status/{trade_id}` 真实响应结构回归测试，覆盖 `trade_id`、`trade_hash`、`status` 和 `return_url`。
- 补充查询状态 `1-6` 的解析测试，覆盖等待支付、成功、超时、取消、确认中和失败。
- 补充 Go 网关真实回调字段签名测试，覆盖空 `block_transaction_id` 和扩展状态值。
- 补充 `Order.from_dict()` 兼容测试，确保可选字段缺失和网关新增字段不会影响已知字段解析。

### Docs
- 明确 `query_order()` 的交易哈希映射规则和业务错误处理。
- 补齐回调状态 `4/5/6` 的说明，保持文档与当前网关枚举一致。

## [0.3.10] - 2026-05-22

### Docs
- 补充 `0.3.1` 及更早版本升级到 `0.3.9+` 的注意事项，覆盖签名、回调安全和发布链路恢复。
- 明确当前已验证的 BEpusdt 网关基线为官方上游 `v1.23.6-4-g1e52ee2`。
- 在 README、API 和 FAQ 中同步安装 extras、Python 版本验证范围和回调安全说明。
- 新增发布维护说明，记录 tag 发布流程、sdist/wheel 内容边界、Telegram 通知策略和 PyPI Trusted Publisher 迁移前置条件。

### CI
- 将 GitHub Actions 更新到 Node 24 runtime 兼容版本：`actions/checkout@v6`、`actions/setup-python@v6`、`softprops/action-gh-release@v3`。
- 修复发布 workflow 提取 CHANGELOG 版本正文时只匹配精确标题的问题；现在支持 `## [版本] - 日期` 格式，避免 tag 发布时误判缺少版本条目。
- 发布校验新增 sdist 内容检查，防止 `.github/`、`tests/`、`examples/` 和开发治理文件重新进入源码包。

### Release Notes
- PyPI Trusted Publisher 暂未启用；当前发布仍使用 `PYPI_API_TOKEN`，等待 PyPI 项目侧 trusted publisher 配置确认后再迁移。

## [0.3.9] - 2026-05-19

### Security
- 加固 `verify_callback()`：非字典回调数据、缺失签名或非字符串签名现在返回 `False`，避免商户回调接口因畸形请求抛出 500。
- 补充回调安全说明：签名验证只证明回调来源可信，商户仍必须校验本地订单号、金额、状态流转，并保证 `trade_id` / `block_transaction_id` 幂等处理。

### Docs
- 更新 README、API、FAQ 和示例文档中的回调代码，避免用户误以为“签名有效即可直接发货”。
- 更新 Flask/FastAPI 示例：移除 `debug=True`，避免向客户端返回原始异常信息，并加入订单金额校验和幂等处理示例。

### CI
- 将 `examples/` 纳入 black 和 flake8 门禁，避免示例代码继续漂移。
- 发布流程仅保留 Telegram 频道通知，避免同一发布消息重复投递。
- 新增 gitleaks baseline，压掉测试/文档里钱包地址样例导致的历史误报，同时保留默认密钥检测规则。
- 从 sdist 中排除 `.github/` 工作流文件和开发治理/工具配置文件，减少发布包中的非运行时内容。

### Tests
- 新增回调畸形输入回归测试，覆盖非 dict payload 和非字符串签名。

## [0.3.8] - 2026-05-19

### Fixed
- 修复 `TradeType` 枚举参与签名时使用枚举成员名的问题；现在签名会使用实际请求值，例如 `usdt.trc20`，避免默认下单参数与服务端验签值不一致。
- 修复发布包版本被 `setup.py` 写死为 `0.3.1` 的问题；包版本现在统一由 Git tag 通过 `setuptools_scm` 推导。
- 限制打包时的包发现范围，防止本地残留 `build/` 目录污染 wheel 内容。

### CI
- 新增 main / PR CI，覆盖 Python 3.8、3.9、3.10、3.11、3.12，并运行格式检查、lint 和测试。
- 加强 tag 发布流程：发布前必须通过测试、构建、`twine check`、tag 与包版本一致性校验，以及 wheel 污染检查。
- Telegram 通知改为 PyPI 发布和 GitHub Release 成功后再发送，避免发布失败时误报成功。
- 固定 Telegram GitHub Action 版本，避免使用浮动 `master` 分支处理通知 token。

### Tests
- 新增 `TradeType` 枚举签名回归测试，确保枚举值和等价字符串生成相同签名。
- 新增打包元数据回归测试，确保构建版本可由 `setuptools_scm` 控制，且 wheel 不包含 `build/` 产物。

### Release Notes
- 这是发版链路修复版本。此前 `v0.3.3` 至 `v0.3.7` 的 Git tag 已存在，但 PyPI 发布因版本号错误失败，PyPI 最新版本仍停留在 `0.3.1`。

## [0.3.7] - 2026-04-14

### Tests
- 新建 `tests/test_exceptions.py`：覆盖所有异常继承链、属性存储、向后兼容别名
- 测试场景：8 种异常的 `issubclass` 继承关系验证；`APIError`/`ServerError`/`ClientError` 属性存储（`status_code`/`response`）；`TimeoutError` 别名等同于 `RequestTimeoutError`；所有 SDK 异常均可用 `BEpusdtError` 捕获

## [0.3.6] - 2026-04-12

### Tests
- `tests/test_models.py` 新增 `TestOrderQRCode`：覆盖二维码三个方法的完整测试
- 测试场景：未安装 `qrcode` 时抛出含 `pip install` 提示的 `ImportError`；`get_qrcode_base64` 返回合法 base64 字符串；`get_qrcode_data_uri` 返回 `data:image/png;base64,` 前缀；`generate_qrcode` 使用 `order.token` 作为二维码数据

## [0.3.5] - 2026-04-09

### Changed
- `models.py` 将 `TradeType` 从普通类改为 `class TradeType(str, Enum)`，提供类型安全、IDE 补全和运行时校验；继承 `str` 保持向后兼容，原有 `TradeType.USDT_TRC20` 写法及字符串比较无需修改

### Tests
- `tests/test_models.py` 新增 `TestTradeType` 完整覆盖：全部 21 个常量值验证、字符串比较、按值反查、非法值 `ValueError`、枚举迭代、`isinstance` 类型断言

## [0.3.4] - 2026-04-06

### Tests
- 新建 `tests/test_retry.py`，补全 `retry_on_error` 装饰器的完整测试覆盖
- 测试场景：首次成功不触发 sleep、网络错误后重试成功、超出最大重试次数后抛异常、指数退避延迟验证（mock `time.sleep`）、非重试异常立即透传、`max_retries=0` 只调用一次

## [0.3.3] - 2026-03-30

### Fixed
- `client.py` 移除 `print()` 调用，改用 `logger.debug()`，库代码不再写 stdout
- 移除 `_SDK_INFO_SHOWN` 全局可变状态（线程不安全），初始化逻辑简化为直接写 debug 日志

### Tests
- 新增 `test_init_produces_no_stdout_output`：验证 `BEpusdtClient` 初始化不产生任何 stdout 输出

## [0.3.2] - 2026-03-29

### Security
- `signature.py` 改用 `hmac.compare_digest()` 进行常数时间比较，修复 `verify_signature` 中普通字符串 `==` 比较导致的时序攻击侧信道

### Fixed
- `models.py` 补充 `OrderStatus.CANCELED(4)` / `CONFIRMING(5)` / `FAILED(6)`，与 Go 网关枚举完整对齐，修复回调返回这些状态时抛 `ValueError` 的崩溃 bug

### Tests
- 新增 `test_verify_signature_constant_time`：验证 `hmac.compare_digest` 被正确调用
- 新增 `test_order_status_new_values` / `test_order_status_from_int` / `test_order_status_invalid_raises`
- 修复测试中 `mock_response.status_code` 缺失导致的 5 个预存测试失败

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

[0.3.13]: https://github.com/luoyanglang/bepusdt-python-sdk/releases/tag/v0.3.13
[0.3.12]: https://github.com/luoyanglang/bepusdt-python-sdk/releases/tag/v0.3.12
[0.3.11]: https://github.com/luoyanglang/bepusdt-python-sdk/releases/tag/v0.3.11
[0.3.10]: https://github.com/luoyanglang/bepusdt-python-sdk/releases/tag/v0.3.10
[0.3.9]: https://github.com/luoyanglang/bepusdt-python-sdk/releases/tag/v0.3.9
[0.3.8]: https://github.com/luoyanglang/bepusdt-python-sdk/releases/tag/v0.3.8
[0.3.7]: https://github.com/luoyanglang/bepusdt-python-sdk/releases/tag/v0.3.7
[0.3.6]: https://github.com/luoyanglang/bepusdt-python-sdk/releases/tag/v0.3.6
[0.3.5]: https://github.com/luoyanglang/bepusdt-python-sdk/releases/tag/v0.3.5
[0.3.4]: https://github.com/luoyanglang/bepusdt-python-sdk/releases/tag/v0.3.4
[0.3.3]: https://github.com/luoyanglang/bepusdt-python-sdk/releases/tag/v0.3.3
[0.3.2]: https://github.com/luoyanglang/bepusdt-python-sdk/releases/tag/v0.3.2
[0.3.1]: https://github.com/luoyanglang/bepusdt-python-sdk/releases/tag/v0.3.1
[0.2.3]: https://github.com/luoyanglang/bepusdt-python-sdk/releases/tag/v0.2.3
[0.2.2]: https://github.com/luoyanglang/bepusdt-python-sdk/releases/tag/v0.2.2
[0.2.1]: https://github.com/luoyanglang/bepusdt-python-sdk/releases/tag/v0.2.1
[0.2.0]: https://github.com/luoyanglang/bepusdt-python-sdk/releases/tag/v0.2.0
[0.1.0]: https://github.com/luoyanglang/bepusdt-python-sdk/releases/tag/v0.1.0
