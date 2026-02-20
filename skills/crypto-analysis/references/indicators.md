# 技术指标计算公式

## RSI (Relative Strength Index)

相对强弱指数，衡量价格变动的速度和幅度。

### 公式

```
Change = Close - PrevClose
Gain = max(Change, 0)
Loss = max(-Change, 0)

AvgGain = SMA(Gain, 14) 或 RMA(Gain, 14)
AvgLoss = SMA(Loss, 14) 或 RMA(Loss, 14)

# ⚠️ 必须防除零：AvgLoss == 0 时 RSI = 100
RS = AvgGain / AvgLoss if AvgLoss > 0 else float('inf')
RSI = 100 - (100 / (1 + RS)) if AvgLoss > 0 else 100
```

### 解读

| RSI 值 | 状态 |
|--------|------|
| > 70 | 超买 |
| 50-70 | 偏多 |
| 30-50 | 偏空 |
| < 30 | 超卖 |

### 背离信号
- **看涨背离**：价格创新低，RSI 不创新低
- **看跌背离**：价格创新高，RSI 不创新高

---

## MACD (Moving Average Convergence Divergence)

指数平滑异同移动平均线，判断趋势方向和动量。

### 公式

```
EMA12 = EMA(Close, 12)
EMA26 = EMA(Close, 26)
DIF = EMA12 - EMA26
DEA = EMA(DIF, 9)
MACD柱 = (DIF - DEA) * 2
```

### EMA 计算

```
k = 2 / (N + 1)
EMA = Price * k + EMA_prev * (1 - k)

# 初始值：第一个 EMA = 第一个收盘价
```

### 解读

| 信号 | 含义 |
|------|------|
| DIF 上穿 DEA | 金叉，看多信号 |
| DIF 下穿 DEA | 死叉，看空信号 |
| MACD 柱由负转正 | 动能转多 |
| MACD 柱由正转负 | 动能转空 |
| 柱状图放大 | 趋势加强 |
| 柱状图收缩 | 趋势减弱 |

---

## ATR (Average True Range)

平均真实波动幅度，衡量市场波动性。

### 公式

```
TR = max(
  High - Low,
  |High - PrevClose|,
  |Low - PrevClose|
)

ATR = SMA(TR, 14) 或 RMA(TR, 14)
```

### 用途

1. **波动率判断**：ATR 高 = 高波动，ATR 低 = 低波动
2. **止损设置**：止损 = 入场价 ± 1.5~2 倍 ATR
3. **仓位计算**：风险金额 / ATR = 仓位大小

### 相对波动率

将当前 ATR 与过去 N 周期的 ATR 比较：
- ATR > 1.5 倍平均值 = 高波动
- ATR < 0.5 倍平均值 = 低波动（可能蓄力）

---

## 布林带 (Bollinger Bands)

基于标准差的波动通道。

### 公式

```
中轨 = SMA(Close, 20)
标准差 = StdDev(Close, 20)
上轨 = 中轨 + 2 * 标准差
下轨 = 中轨 - 2 * 标准差

带宽% = (上轨 - 下轨) / 中轨 * 100
%B = (Close - 下轨) / (上轨 - 下轨)
```

### 标准差计算

```
StdDev = sqrt(sum((Close - SMA)^2) / N)
```

### 解读

| 指标 | 含义 |
|------|------|
| 价格触及上轨 | 短期超买 |
| 价格触及下轨 | 短期超卖 |
| 带宽收窄 (< 4%) | 波动率低，可能突破 |
| 带宽扩张 (> 8%) | 波动率高，趋势进行中 |
| %B > 1 | 价格在上轨之上 |
| %B < 0 | 价格在下轨之下 |

---

## EMA (Exponential Moving Average)

指数移动平均线，对近期价格赋予更高权重。

### 公式

```
k = 2 / (N + 1)
EMA = Close * k + EMA_prev * (1 - k)
```

### 常用周期

| 周期 | 用途 |
|------|------|
| EMA 20 | 短期趋势 |
| EMA 50 | 中期趋势 |
| EMA 200 | 长期趋势 |

### 趋势判断

| 关系 | 含义 |
|------|------|
| 价格 > EMA20 > EMA50 > EMA200 | 强多头 |
| 价格 < EMA20 < EMA50 < EMA200 | 强空头 |
| EMA 交织 | 震荡市 |
| EMA20 上穿 EMA50 | 中期金叉 |
| EMA20 下穿 EMA50 | 中期死叉 |

---

## SMA (Simple Moving Average)

简单移动平均线，用于计算其他指标。

### 公式

```
SMA = sum(Close, N) / N
```

---

## 斐波那契回撤 (Fibonacci Retracement)

基于黄金分割比例的支撑阻力位工具。

### 原理

斐波那契数列：1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89...
关键比例来源：
- 23.6% = 前一项 / 后三项
- 38.2% = 前一项 / 后两项
- 50.0% = 中点（非严格斐波那契，但广泛使用）
- 61.8% = 前一项 / 后一项（黄金比例）
- 78.6% = 61.8% 的平方根

### 计算公式

```
# 上涨后回调（从低点画到高点）
波段幅度 = High - Low

23.6% 回撤位 = High - 波段幅度 × 0.236
38.2% 回撤位 = High - 波段幅度 × 0.382
50.0% 回撤位 = High - 波段幅度 × 0.500
61.8% 回撤位 = High - 波段幅度 × 0.618
78.6% 回撤位 = High - 波段幅度 × 0.786

# 下跌后反弹（从高点画到低点）
38.2% 反弹位 = Low + 波段幅度 × 0.382
50.0% 反弹位 = Low + 波段幅度 × 0.500
61.8% 反弹位 = Low + 波段幅度 × 0.618
```

### 关键回撤位解读

| 回撤比例 | 含义 | 操作提示 |
|---------|------|---------|
| 23.6% | 强势回调 | 趋势强劲，回调浅 |
| 38.2% | 健康回调 | 常见首次支撑/阻力 |
| 50.0% | 标准回调 | 多空分界线 |
| 61.8% | 深度回调 | 黄金分割位，关键支撑 |
| 78.6% | 最后防线 | 跌破则趋势反转概率大 |

### 使用条件

> **重要**: 斐波那契仅在以下条件满足时使用：
> 1. 存在明确的趋势波段（非震荡行情）
> 2. 波段幅度足够大（BTC 至少 5%，山寨至少 10%）
> 3. 波段起点和终点清晰可辨

### 共振原则

斐波那契单独使用效果有限，需与其他指标共振：

| 共振类型 | 示例 | 信号强度 |
|---------|------|---------|
| 斐波那契 + EMA | 38.2% 回撤位与 EMA50 重合 | ★★★★★ |
| 斐波那契 + 前高/前低 | 61.8% 回撤位与前期高点重合 | ★★★★☆ |
| 斐波那契 + 整数关口 | 50% 回撤位在 $90,000 附近 | ★★★★☆ |
| 斐波那契 + 布林带 | 回撤位与布林下轨重合 | ★★★☆☆ |

### 示例计算

```
场景：BTC 从 $85,000 涨到 $97,000 后回调

波段幅度 = $97,000 - $85,000 = $12,000

斐波那契回撤位：
┌──────────┬────────────────┬──────────┐
│ 比例     │ 计算           │ 价位     │
├──────────┼────────────────┼──────────┤
│ 23.6%    │ 97000-12000×0.236 │ $94,168  │
│ 38.2%    │ 97000-12000×0.382 │ $92,416  │
│ 50.0%    │ 97000-12000×0.500 │ $91,000  │
│ 61.8%    │ 97000-12000×0.618 │ $89,584  │
│ 78.6%    │ 97000-12000×0.786 │ $87,568  │
└──────────┴────────────────┴──────────┘
```

---

## 计算顺序建议

1. 首先计算 SMA/EMA（被其他指标依赖）
2. 计算 RSI
3. 计算 MACD
4. 计算 ATR
5. 计算布林带
6. 斐波那契回撤（可选，需明确波段时使用）

---

## 示例计算（伪代码）

```python
def calculate_indicators(klines):
    closes = [k[4] for k in klines]  # 收盘价数组
    highs = [k[2] for k in klines]
    lows = [k[3] for k in klines]

    # EMA — 注意：数据不足时返回 None，格式化时必须做 None 检查
    ema20 = ema(closes, 20)
    ema50 = ema(closes, 50)
    ema200 = ema(closes, 200) if len(closes) >= 200 else None

    # RSI — ⚠️ calc_rsi 必须处理 AvgLoss=0 的情况（全涨无跌时返回 100）
    # def calc_rsi(closes, period=14):
    #     changes = [closes[i]-closes[i-1] for i in range(1, len(closes))]
    #     gains = [max(c, 0) for c in changes]
    #     losses = [max(-c, 0) for c in changes]
    #     avg_gain = sum(gains[-period:]) / period
    #     avg_loss = sum(losses[-period:]) / period
    #     if avg_loss == 0: return 100.0
    #     rs = avg_gain / avg_loss
    #     return 100 - (100 / (1 + rs))
    rsi = calculate_rsi(closes, 14)

    # MACD
    ema12 = ema(closes, 12)
    ema26 = ema(closes, 26)
    dif = ema12 - ema26
    dea = ema(dif, 9)
    macd_hist = (dif - dea) * 2

    # ATR
    atr = calculate_atr(highs, lows, closes, 14)

    # 布林带
    sma20 = sma(closes, 20)
    std = stddev(closes, 20)
    upper = sma20 + 2 * std
    lower = sma20 - 2 * std
    bandwidth = (upper - lower) / sma20 * 100

    return {
        'ema20': ema20[-1],
        'ema50': ema50[-1],
        'ema200': ema200[-1] if ema200 is not None else None,
        'rsi': rsi[-1],
        'macd': {'dif': dif[-1], 'dea': dea[-1], 'hist': macd_hist[-1]},
        'atr': atr[-1],
        'boll': {'upper': upper[-1], 'mid': sma20[-1], 'lower': lower[-1], 'width': bandwidth[-1]}
    }


# ⚠️ 格式化安全规范（必须遵守）
# 所有从 API 或计算结果获取的数值，可能为 None（数据不足/API 返回空）
# 使用格式说明符（:.2f / :,.0f / :.1% 等）前必须确认值不为 None
#
# ❌ 错误写法（None 时崩溃）：
#   f"EMA200: ${ema200:.2f}"
#
# ✅ 正确写法（两种方式任选）：
#   # 方式1：三元表达式
#   f"EMA200: {'$'+f'{ema200:.2f}' if ema200 is not None else 'N/A'}"
#
#   # 方式2：赋值处给默认值（推荐，代码更简洁）
#   ema200 = result.get('ema200') or 0  # 数据不足时显示 0
#   f"EMA200: ${ema200:.2f}"
#
# 适用字段：ema200、longShortRatio、fundingRate、openInterest 等所有 API 返回字段
```
