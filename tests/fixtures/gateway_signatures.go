// Run only inside the frozen gateway source copy with go run -mod=vendor.
package main

import (
    "encoding/json"
    "math"
    "math/rand"
    "os"
    "github.com/v03413/bepusdt/app/utils"
)

func main() {
    cases := []string{
        `{"amount":10}`, `{"amount":10.0}`, `{"amount":1000000}`, `{"amount":1000000.5}`,
        `{"amount":0.00001}`, `{"amount":0.0001}`, `{"amount":-0.0}`,
        `{"amount":9007199254740993}`, `{"amount":1.2345678901234567}`,
        `{"amount":1e20}`, `{"amount":5e-324}`, `{"flag":true}`, `{"flag":false}`,
        `{"amount":0,"empty":"","absent":null,"signature":"excluded"}`,
        `{"name":"测试商品","rate":"~1.02","trade_type":"usdt.trc20"}`,
        `{"order_id":"fixture-order","amount":10,"notify_url":"https://merchant.example/notify","redirect_url":"https://merchant.example/notify","trade_type":"usdt.trc20","timeout":1000000}`,
        `{"trade_id":"fixture-trade","order_id":"fixture-order","amount":10.0,"actual_amount":"1.35","token":"fixture-wallet","status":2,"block_transaction_id":"fixture-hash"}`,
    }
    r := rand.New(rand.NewSource(20261004))
    for i := 0; i < 128; i++ {
        f := math.Float64frombits(r.Uint64())
        if math.IsNaN(f) || math.IsInf(f, 0) { continue }
        raw, err := json.Marshal(map[string]any{"amount":f})
        if err != nil { panic(err) }
        cases = append(cases, string(raw))
    }
    out := []map[string]any{}
    for _, raw := range cases {
        var p map[string]any
        if err := json.Unmarshal([]byte(raw), &p); err != nil { panic(err) }
        out = append(out, map[string]any{"json":raw,"signature":utils.EpusdtSign(p,"fixture-token")})
    }
    enc := json.NewEncoder(os.Stdout)
    enc.SetIndent("", "  ")
    if err := enc.Encode(map[string]any{"gateway_sha":"aa3bd5097f258cccd5a53baed7211c74733b8332","token":"fixture-token","cases":out}); err != nil { panic(err) }
}
