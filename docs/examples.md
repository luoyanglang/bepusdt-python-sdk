# 📚 使用示例

本批支持基础商户创建、查询、取消和回调验签；完整支持边界见 [README](../README.md)。
演示没有真实付款、钱包或履约工作者；零金额模式不在演示支持范围。

## 基础商户调用

```python
from bepusdt import BEpusdtClient, TradeType

client = BEpusdtClient(
    api_url="https://your-bepusdt-server.com", api_token="your-api-token",
    query_mode="current"  # aa3bd50；旧 f4bdee1 网关使用 legacy（默认）
)
order = client.create_order(
    order_id="ORDER_001", amount=10.0,
    notify_url="https://your-domain.com/payment/notify", trade_type=TradeType.USDT_TRC20,
    rate=7.4  # 数值汇率转为固定小数文本；字符串 ~1.02 / +0.3 等保持原样
)
# 先持久登记返回的 trade_id、商户订单、金额和法币，再把链接提供给付款人。
print(order.payment_url)
snapshot = client.query_order(order.trade_id)
print(snapshot.status, snapshot.expired_at, snapshot.actual_amount_text)
```

当前 Info 受付款端指纹约束。访问拒绝不会降级或重试；查询不是签名支付凭据。
同一 order_id 可能有多个已知 trade_id，响应丢失后的创建/取消结果可能不确定。
不能把签名有效、查询成功或传输重试当作“支付成功且只执行一次”。

## Flask 与 FastAPI 集成

从仓库取得 [callback_store.py](../examples/callback_store.py) 与对应框架脚本，
它们是演示源码，不随 pip 包安装。安装自己的框架依赖，并配置仓库外的可写
SQLite 文件路径到环境变量 `BEPUSDT_EXAMPLE_DB` 后，运行：
路径必须为绝对路径且位于仓库外，示例会拒绝相对路径和仓库内状态。

```bash
python examples/flask_example.py
# 或
python examples/fastapi_example.py
```

[Flask](../examples/flask_example.py) 和 [FastAPI](../examples/fastapi_example.py)
都按如下顺序处理固定正金额 CNY 订单：

创建入口中的订单号和金额是模拟可信业务输入。真实商户须先鉴权，从服务端
订单/商品记录确定金额与货币，再调用 reserve；不能直接信任付款人提交的价格。
这些脚本仅用于本地演示，不能作为公开商户应用直接部署。

1. 在创建前原子登记商户业务金额/法币，拒绝改变同一业务订单的付款意图。
2. 调用 SDK 创建，登记返回的 trade_id、实际数额和地址；保留历史已知尝试。
3. 回调先验签，再核对已登记尝试、商户订单、法币对应金额、实际数额和地址。
   回调本身没有 fiat，从已登记交易取得货币，不能猜测。
4. 在一个事务中保存 inbox；成功时插入按 order_id 唯一的 outbox，再应答 HTTP
   200/plain ok。未知交易/不一致字段返回 400，存储失败返回 503。
5. 商户自己的工作者处理 outbox，保证实际发货幂等、失败恢复、监控与备份。
   示例没有实现这个工作者，也不把写入 outbox 声称为完成发货。

过期回调不删除尝试、不标记业务订单已履约；已知旧尝试可能之后收到成功。
第二个已知尝试成功可持久接收，但不能生成第二条业务履约任务。未登记交易须
拒绝并由商户受控对账；创建响应丢失不能靠无签名 Info 自动补造授权关系。
同 trade_id 重建可改变分配数额/地址，需登记最新返回结果；演示并不保证上游
并发重建的原子性。生产商户须控制创建并发、保持状态历史并制定对账策略。

## Django 回调接入片段

`store` 使用仓库中的演示 CallbackStore，或替换为商户自己的持久事务存储。
创建路径同样必须先 reserve、调用 SDK、register 返回的交易。下面只展示接收端：

```python
import json
import os
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from bepusdt import BEpusdtClient
from examples.callback_store import CallbackStore

client = BEpusdtClient("https://your-bepusdt-server.com", "your-api-token")
store = CallbackStore(os.environ.get("BEPUSDT_EXAMPLE_DB"))

@csrf_exempt
def payment_notify(request):
    try:
        data = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        return HttpResponse("fail", status=400)
    if not client.verify_callback(data):
        return HttpResponse("fail", status=400)
    try:
        if not store.accept(data):
            return HttpResponse("fail", status=400)
    except Exception:
        return HttpResponse("fail", status=503)
    return HttpResponse("ok", status=200)
```

## 通知规则与验收边界

当前 aa3bd50 的 Epusdt 只检查 HTTP 200，忽略正文；拒绝时返回字典并保持 200
会错误终止成功通知重试。plain ok 是兼容建议，持久接收是商户的应答前提。
等待通知每 30 秒调度、60 秒缓存抑制；成功重试上限由配置控制（默认 10），
下一次基于确认时间 + 2^notify_num 分钟。3/6 是 best-effort；4/5 没有对应
通知触发。枚举有效不保证推送，状态可能缺失、重复、延迟或乱序。

固定/待选零金额可能和正金额订单共享钱包；同 ID 跨零重建不更新持久化锁定标志。
这些是上游源码限制，运行碰撞未验证，示例不支持零金额且 SDK 本批没有修复网关。
