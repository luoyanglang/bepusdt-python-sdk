# BEpusdt Python SDK 修复计划

> 基于全面代码审查（代码质量 + 安全 + 测试覆盖 + API 对接）制定
> 策略：每天修复 1~2 个问题，保持仓库持续活跃，版本号按 SemVer patch 递增

---

## 问题优先级总览

| 级别 | 数量 | 说明 |
|------|------|------|
| CRITICAL | 3 | 安全漏洞，立刻修复 |
| HIGH | 9 | 逻辑 bug / 严重设计缺陷 |
| MEDIUM | 8 | 最佳实践 / 代码质量 |
| LOW | 5 | 小改进 |

---

## Day 1（今日）— CRITICAL 安全修复 → v0.3.2

### 问题 1：时序攻击漏洞
- **文件**：`bepusdt/signature.py:53`
- **问题**：`expected == received` 用普通字符串比较，短路特性暴露时序侧信道，攻击者可逐字节爆破签名
- **修复**：改用 `hmac.compare_digest()`，常数时间比较
- **测试**：新增 `test_verify_signature_uses_constant_time_comparison`

### 问题 2：OrderStatus 枚举缺失状态值
- **文件**：`bepusdt/models.py:13-26`
- **问题**：Go 网关有 6 种状态，Python SDK 只定义了 3 种（WAITING/SUCCESS/TIMEOUT）。当回调返回 `status=4/5/6` 时，`OrderStatus(data["status"])` 直接抛 `ValueError`，导致回调处理崩溃
- **Go 网关对应值**：
  - `4` = OrderStatusCanceled（订单取消）
  - `5` = OrderStatusConfirming（等待区块确认）
  - `6` = OrderStatusFailed（交易确认失败）
- **修复**：补充 `CANCELED = 4`、`CONFIRMING = 5`、`FAILED = 6`
- **测试**：补充对 3 个新状态的枚举值测试

**发版**：`git tag v0.3.2`

---

## Day 2 — HIGH：参数静默丢弃 bug

### 问题：`timeout=0` / `rate=0` 被静默丢弃
- **文件**：`bepusdt/client.py:151-157`
- **问题**：`if timeout:` 对 `0` 为假值，`timeout=0` 和 `rate=0` 会被跳过不发送给 API
- **修复**：改为 `if timeout is not None:` 和 `if rate is not None:`
- **测试**：新增 `test_create_order_with_zero_timeout`、`test_create_order_with_zero_rate`

---

## Day 3 — HIGH：移除 `print()`，改用 logging → v0.3.3

### 问题：库代码使用 print()
- **文件**：`bepusdt/client.py:61-62`
- **问题**：库代码不能写 stdout。影响 CLI、测试捕获、WSGI 服务器
- **修复**：移除 `print()`，改为 `logger.debug()`；同时移除 `_SDK_INFO_SHOWN` 全局可变状态（线程不安全）
- **测试**：验证初始化不产生 stdout 输出

**发版**：`git tag v0.3.3`

---

## Day 4 — HIGH：`TimeoutError` 命名冲突

### 问题：遮盖 Python 内置 `TimeoutError`
- **文件**：`bepusdt/exceptions.py:34`
- **问题**：自定义 `TimeoutError` 遮盖 `builtins.TimeoutError`，导致 `except TimeoutError` 语义模糊
- **修复**：重命名为 `RequestTimeoutError`，同步更新 `client.py`、`retry.py`、`__init__.py`
- **兼容**：在 `__init__.py` 保留 `TimeoutError = RequestTimeoutError` 别名，避免 breaking change（下个 major 版本移除）
- **测试**：更新相关测试中的异常类名

---

## Day 5 — HIGH：exceptions.py 类型注解错误

### 问题：`Optional` 缺失
- **文件**：`bepusdt/exceptions.py:23,42,50`
- **问题**：`status_code: int = None` 类型矛盾，mypy 报错
- **修复**：改为 `status_code: Optional[int] = None`、`response: Optional[dict] = None`
- **测试**：确保 `mypy bepusdt/` 零错误

---

## Day 6 — 测试覆盖：retry.py 零测试 → v0.3.4

### 问题：重试机制完全没有测试
- **文件**：新建 `tests/test_retry.py`
- **缺失测试**：
  - 首次成功不触发 sleep
  - 网络错误重试后成功
  - 超出最大重试次数后抛异常
  - 指数退避延迟验证（mock `time.sleep`）
  - 非重试异常立即透传（不 sleep）
  - `max_retries=0` 只调用一次

**发版**：`git tag v0.3.4`

---

## Day 7 — 测试覆盖：HTTP 异常路径

### 问题：`_post`/`_get` 异常转换逻辑无测试
- **文件**：`tests/test_client.py`
- **缺失测试**：
  - HTTP 5xx → `ServerError`
  - HTTP 4xx → `ClientError`
  - `requests.Timeout` → SDK `RequestTimeoutError`
  - `requests.ConnectionError` → `NetworkError`
  - JSON 解析失败 → `APIError`

---

## Day 8 — 测试覆盖：create_order 参数细节

### 问题：可选参数路径无测试
- **文件**：`tests/test_client.py`
- **缺失测试**：
  - `amount=10.0` → 发送整数 `10`（整数化逻辑）
  - `redirect_url` 未传时默认用 `notify_url`
  - `redirect_url` 显式传值时使用传入值
  - `address`/`fiat`/`name` 等可选参数正确传入

---

## Day 9 — MEDIUM：TradeType 改为 Enum → v0.3.5

### 问题：TradeType 是普通类，无类型安全
- **文件**：`bepusdt/models.py:29-59`
- **问题**：任意字符串都能通过，无 IDE 补全，无运行时校验
- **修复**：改为 `class TradeType(str, Enum)`（兼容 Python 3.7+）
- **影响**：用户原有 `TradeType.USDT_TRC20` 写法保持不变（str Enum 可直接比较字符串）
- **测试**：验证所有 21 个常量值、字符串比较、迭代枚举成员

**发版**：`git tag v0.3.5`

---

## Day 10 — MEDIUM：`_post`/`_get` 重复代码重构

### 问题：两个方法 100% 代码重复
- **文件**：`bepusdt/client.py:301-410`
- **修复**：抽取私有方法 `_request(self, method: str, url: str, **kwargs)`，`_post`/`_get` 各调用一行
- **测试**：现有测试不变，覆盖率不降

---

## Day 11 — MEDIUM：`rate` 参数类型注解修正

### 问题：注解为 `float` 但实际支持字符串前缀语法
- **文件**：`bepusdt/client.py`
- **问题**：`rate` 支持 `~1.02`、`+0.3`、`-0.2` 前缀语法，应为 `Union[float, str]`
- **修复**：改为 `Optional[Union[float, str]]`，更新 docstring 示例

---

## Day 12 — 测试覆盖：二维码功能 → v0.3.6

### 问题：三个二维码方法零测试
- **文件**：`tests/test_models.py`
- **新增测试**：
  - 未安装 qrcode 时抛出含安装提示的 `ImportError`
  - `get_qrcode_base64` 返回合法 base64 字符串
  - `get_qrcode_data_uri` 返回 `data:image/png;base64,` 前缀
  - `generate_qrcode` 使用 `order.token` 作为二维码数据

**发版**：`git tag v0.3.6`

---

## Day 13 — MEDIUM：HTTPS 强制校验

### 问题：`api_url` 和 `notify_url` 未校验协议
- **文件**：`bepusdt/client.py`
- **修复**：`__init__` 中校验 `api_url` 必须 `https://` 开头；`create_order` 中校验 `notify_url`
- **兼容**：仅校验，不自动转换；提供清晰的 `ValidationError` 错误消息
- **测试**：`http://` 地址抛 `ValidationError`，`https://` 正常通过

---

## Day 14 — 测试覆盖：exceptions 和 TradeType 完整覆盖 → v0.3.7

### 补充测试
- 新建 `tests/test_exceptions.py`：验证所有异常继承链、属性存储
- 补充 `test_models.py`：覆盖全部 21 个 TradeType 常量

**发版**：`git tag v0.3.7`

---

## 备注

- 每次修复后必须运行 `pytest tests/` 确保全绿
- 有测试变更的版本在 CHANGELOG.md 记录
- 发版用 `git tag vX.Y.Z && git push origin vX.Y.Z`（GitHub Actions 自动发 PyPI）
- 示例代码（`examples/`）的问题（debug=True 等）随对应主题一起修
