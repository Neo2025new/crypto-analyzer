# 币安 API 端点参考

## 合约 K 线数据

```bash
curl -s "https://fapi.binance.com/fapi/v1/klines?symbol={SYMBOL}USDT&interval={INTERVAL}&limit=100"
```

### 参数
- `symbol`: 交易对（如 BTCUSDT, ETHUSDT）
- `interval`: 时间周期
  - `1m`, `3m`, `5m`, `15m`, `30m`
  - `1h`, `2h`, `4h`, `6h`, `8h`, `12h`
  - `1d`, `3d`, `1w`, `1M`
- `limit`: 返回数量（默认 500，最大 1500）

### 返回数据结构
```
[
  [
    1499040000000,      // 开盘时间 (timestamp)
    "0.01634000",       // 开盘价
    "0.80000000",       // 最高价
    "0.01575800",       // 最低价
    "0.01577100",       // 收盘价
    "148976.11427815",  // 成交量
    1499644799999,      // 收盘时间
    "2434.19055334",    // 成交额
    308,                // 成交笔数
    "1756.87402397",    // 主动买入量
    "28.46694368",      // 主动买入额
    "0"                 // 忽略
  ]
]
```

## 资金费率

```bash
curl -s "https://fapi.binance.com/fapi/v1/fundingRate?symbol={SYMBOL}USDT&limit=1"
```

### 返回示例
```json
[{
  "symbol": "BTCUSDT",
  "fundingTime": 1768809600007,
  "fundingRate": "0.00010000",
  "markPrice": "92788.73004348"
}]
```

### 费率解读
| 费率范围 | 含义 |
|---------|------|
| > 0.03% | 极端多头（过热） |
| 0.01% - 0.03% | 偏多 |
| -0.01% - 0.01% | 中性 |
| -0.03% - -0.01% | 偏空 |
| < -0.03% | 极端空头 |

## 持仓量（Open Interest）

```bash
curl -s "https://fapi.binance.com/fapi/v1/openInterest?symbol={SYMBOL}USDT"
```

### 返回示例
```json
{
  "symbol": "BTCUSDT",
  "openInterest": "95307.855",
  "time": 1768809645566
}
```

## 大户多空比

```bash
curl -s "https://fapi.binance.com/futures/data/topLongShortAccountRatio?symbol={SYMBOL}USDT&period=1h&limit=1"
```

### 返回示例
```json
[{
  "symbol": "BTCUSDT",
  "longAccount": "0.7043",
  "longShortRatio": "2.3818",
  "shortAccount": "0.2957",
  "timestamp": 1768809600000
}]
```

## 散户多空比

```bash
curl -s "https://fapi.binance.com/futures/data/globalLongShortAccountRatio?symbol={SYMBOL}USDT&period=1h&limit=1"
```

## 主动买卖比

```bash
curl -s "https://fapi.binance.com/futures/data/takerlongshortRatio?symbol={SYMBOL}USDT&period=1h&limit=24"
```

### 返回示例
```json
[{
  "buySellRatio": "1.2345",
  "sellVol": "1000.00",
  "buyVol": "1234.50",
  "timestamp": 1768809600000
}]
```

## 常用交易对

| 币种 | 合约符号 |
|------|---------|
| BTC | BTCUSDT |
| ETH | ETHUSDT |
| SOL | SOLUSDT |
| BNB | BNBUSDT |
| XRP | XRPUSDT |
| DOGE | DOGEUSDT |
| ADA | ADAUSDT |
| AVAX | AVAXUSDT |
| LINK | LINKUSDT |
| DOT | DOTUSDT |

## 注意事项

1. 所有 API 为公开接口，无需认证
2. 建议使用 `curl -s` 静默模式
3. 合约数据比现货更适合分析（包含杠杆信息）
4. 资金费率每 8 小时结算一次
