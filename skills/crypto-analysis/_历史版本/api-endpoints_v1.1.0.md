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

| 费率范围 | 含义 | 操作提示 |
|---------|------|---------|
| > 0.05% | 极端过热 | ⚠️ 考虑反向，不追多 |
| 0.03% - 0.05% | 严重过热 | 警惕回调 |
| 0.01% - 0.03% | 偏多 | 正常偏多情绪 |
| 0.005% - 0.01% | 轻微偏多 | 相对健康 |
| -0.005% - 0.005% | 中性 | 多空平衡 |
| 0% - 0.005% | 恐惧区间 | 🔥 可能超卖，关注反弹 |
| < 0% (负费率) | 深度恐慌 | ⚠️ 空头拥挤，考虑反向 |

> **实战经验**: 当费率从正常水平（0.01%）快速降至 < 0.005% 时，往往是恐慌出清的信号，结合 RSI 超卖可博反弹。

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

### 多空比解读

| 比值范围 | 含义 | 操作提示 |
|---------|------|---------|
| > 4.0 | 极端多头拥挤 | ⚠️ 高危，随时可能反转 |
| 3.5 - 4.0 | 严重偏多 | 🔥 警惕清洗，不追多 |
| 2.5 - 3.5 | 明显偏多 | 注意风险 |
| 1.5 - 2.5 | 轻度偏多 | 正常范围 |
| 0.67 - 1.5 | 相对均衡 | 健康状态 |
| 0.4 - 0.67 | 轻度偏空 | 正常范围 |
| < 0.4 | 极端空头拥挤 | ⚠️ 可能逼空反弹 |

> **实战经验**: 多空比 > 3.5 且持续上升时，说明多头过度拥挤，一旦价格下跌会引发多头踩踏。今日 ETH 多空比达到 3.67 后出现强势反转验证了这一规律。

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

## 24 小时行情统计

```bash
curl -s "https://fapi.binance.com/fapi/v1/ticker/24hr?symbol={SYMBOL}USDT"
```

### 返回示例
```json
{
  "symbol": "BTCUSDT",
  "priceChange": "1234.50",
  "priceChangePercent": "1.38",
  "lastPrice": "90148.60",
  "highPrice": "90599.50",
  "lowPrice": "87205.50",
  "volume": "123456.789",
  "quoteVolume": "11234567890.12"
}
```

### 关键字段
| 字段 | 含义 | 用途 |
|------|------|------|
| `lastPrice` | 最新价 | 当前价格 |
| `highPrice` | 24h 最高 | 日内阻力参考 |
| `lowPrice` | 24h 最低 | 日内支撑参考 |
| `priceChangePercent` | 24h 涨跌幅 | 趋势强度 |
| `quoteVolume` | 24h 成交额 (USDT) | 流动性判断 |

### 振幅计算
```
振幅% = (highPrice - lowPrice) / lowPrice × 100
```

> 振幅 > 5% 为高波动日，> 8% 为极端波动日

## 注意事项

1. 所有 API 为公开接口，无需认证
2. 建议使用 `curl -s` 静默模式
3. 合约数据比现货更适合分析（包含杠杆信息）
4. 资金费率每 8 小时结算一次
5. 多空比和费率结合使用效果更佳
6. 24h Ticker 适合快速获取日内高低点
