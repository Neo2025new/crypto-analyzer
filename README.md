# Crypto Analyzer

Claude Code 加密货币技术分析插件，基于币安 API 自动获取数据，以做市商视角进行行情分析。

## 功能特点

- 🔄 自动调用币安公开 API 获取实时数据
- 📊 自动计算技术指标（RSI、MACD、ATR、布林带、EMA）
- 💹 获取衍生品数据（OI、资金费率、多空比）
- 🎯 做市商视角的多路径分析
- 🔮 支持连续对话（追问、复盘）

## 安装

```bash
claude plugins:add git@github.com:YOUR_USERNAME/crypto-analyzer.git
```

## 使用方式

### 基本命令

```bash
/analyze btc          # 分析 BTC，默认 1H 周期
/analyze eth 4h       # 分析 ETH，4H 周期
/analyze sol 15m      # 分析 SOL，15 分钟周期
/analyze btc full     # BTC 全周期分析（日线+4H+1H+15m）
```

### 支持的币种

支持所有币安合约交易对，常用：
- BTC、ETH、SOL、BNB、XRP
- DOGE、ADA、AVAX、LINK、DOT

### 支持的周期

- `1m`, `5m`, `15m` - 短线
- `1h`, `4h` - 中线
- `1d`, `1w` - 长线
- `full` - 全周期分析

## 交互功能

分析完成后，可以继续对话：

| 输入 | 功能 |
|------|------|
| `再看 4H` | 切换到 4H 周期分析 |
| `为什么看空？` | 解释分析逻辑 |
| `再分析` | 获取最新数据更新分析 |
| `复盘` | 总结本轮分析的验证情况 |

## 分析框架

### 核心原则

1. **做市商视角** — 站在流动性提供者/庄家角度思考
2. **结构推演** — 禁止直接给"看涨/看跌"结论
3. **多路径思维** — 必须输出 3 条以上可能路径
4. **可证伪性** — 所有判断必须附带否定条件
5. **概率量化** — 路径概率必须给具体数值

### 输出内容

- 数据面板（价格、OI、费率、技术指标）
- 执行摘要（核心区间、做市阶段、庄家意图）
- 流动性分析
- 技术结构分析
- 做市阶段判断
- 多路径推演（3 条以上）
- 操作建议
- 关键监控点

## 文件结构

```
crypto-analyzer/
├── .claude-plugin/
│   └── plugin.json              # 插件元数据
├── commands/
│   └── analyze.md               # /analyze 命令定义
├── skills/
│   └── crypto-analysis/
│       ├── SKILL.md             # 主 Skill 文件
│       └── references/
│           ├── api-endpoints.md # API 端点参考
│           ├── indicators.md    # 指标计算公式
│           └── analysis-template.md # 输出模板
└── README.md
```

## 数据来源

所有数据来自币安公开 API，无需认证：
- K 线数据：`fapi.binance.com/fapi/v1/klines`
- 资金费率：`fapi.binance.com/fapi/v1/fundingRate`
- 持仓量：`fapi.binance.com/fapi/v1/openInterest`
- 多空比：`fapi.binance.com/futures/data/topLongShortAccountRatio`

## License

MIT
