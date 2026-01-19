---
name: analyze
description: 分析加密货币行情。使用方式：/analyze btc, /analyze eth 4h, /analyze sol 15m, /analyze btc full
arguments:
  - name: symbol
    description: 币种符号（如 btc, eth, sol）
    required: true
  - name: interval
    description: 时间周期（1m, 5m, 15m, 1h, 4h, 1d）或 full（全周期），默认 1h
    required: false
    default: "1h"
---

# Crypto Analyzer 命令

分析指定加密货币的技术面和衍生品数据。

## 使用方式

```
/analyze <symbol> [interval]
```

### 参数说明

- `symbol`（必需）：币种符号，如 `btc`、`eth`、`sol`
- `interval`（可选）：时间周期，默认 `1h`
  - 支持：`1m`、`5m`、`15m`、`1h`、`4h`、`1d`、`1w`
  - 特殊值 `full`：执行全周期分析（日线 + 4H + 1H + 15m）

### 示例

```
/analyze btc          # 分析 BTC，默认 1H 周期
/analyze eth 4h       # 分析 ETH，4H 周期
/analyze sol 15m      # 分析 SOL，15 分钟周期
/analyze btc full     # BTC 全周期分析
```

## 执行流程

1. 解析用户输入的币种和周期
2. 调用币安 API 获取 K 线数据和衍生品数据
3. 计算技术指标（RSI、MACD、ATR、布林带、EMA）
4. 按 crypto-analysis skill 框架输出分析结果

## 后续交互

分析完成后，用户可以继续对话：
- 询问细节：「为什么看空？」「解释一下路径 A」
- 切换周期：「再看 4H」「看一下 15m」
- 更新分析：「再分析」（获取最新数据）
- 复盘总结：「复盘」（总结本轮分析）
