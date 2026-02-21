#!/usr/bin/env python3
"""
加密货币技术分析工具
用法: python3 analyze.py [--symbols BTCUSDT,ETHUSDT] [--mode 15m|4h|8h]
输出: JSON 格式的完整分析数据
"""
import json
import urllib.request
import math
from datetime import datetime, timezone, timedelta

BASE = "https://fapi.binance.com"
SGT = timezone(timedelta(hours=8))


def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "crypto-analyzer/1.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


def fetch_klines(symbol, interval, limit=300):
    url = f"{BASE}/fapi/v1/klines?symbol={symbol}&interval={interval}&limit={limit}"
    raw = fetch_json(url)
    return [
        {
            "ts": k[0],
            "open": float(k[1]),
            "high": float(k[2]),
            "low": float(k[3]),
            "close": float(k[4]),
            "volume": float(k[5]),
        }
        for k in raw
    ]


def fetch_funding(symbol):
    url = f"{BASE}/fapi/v1/fundingRate?symbol={symbol}&limit=1"
    data = fetch_json(url)
    return float(data[0]["fundingRate"]) if data else None


def fetch_oi(symbol):
    url = f"{BASE}/fapi/v1/openInterest?symbol={symbol}"
    data = fetch_json(url)
    return float(data.get("openInterest", 0))


def fetch_lsr(symbol):
    url = f"{BASE}/futures/data/topLongShortAccountRatio?symbol={symbol}&period=1h&limit=1"
    data = fetch_json(url)
    if data:
        return {
            "ratio": float(data[0]["longShortRatio"]),
            "longPct": float(data[0]["longAccount"]) * 100,
            "shortPct": float(data[0]["shortAccount"]) * 100,
        }
    return None


def fetch_ticker(symbol):
    url = f"{BASE}/fapi/v1/ticker/24hr?symbol={symbol}"
    data = fetch_json(url)
    return {
        "price": float(data["lastPrice"]),
        "high24h": float(data["highPrice"]),
        "low24h": float(data["lowPrice"]),
        "change24h": float(data["priceChangePercent"]),
        "volume24h": float(data["quoteVolume"]),
    }


# ── 指标计算 ──────────────────────────────────────


def calc_ema(values, period):
    if len(values) < period:
        return None
    k = 2 / (period + 1)
    ema = sum(values[:period]) / period
    for v in values[period:]:
        ema = v * k + ema * (1 - k)
    return ema


def calc_ema_series(values, period):
    if len(values) < period:
        return []
    k = 2 / (period + 1)
    ema = sum(values[:period]) / period
    result = [ema]
    for v in values[period:]:
        ema = v * k + ema * (1 - k)
        result.append(ema)
    return result


def calc_sma(values, period):
    if len(values) < period:
        return None
    return sum(values[-period:]) / period


def calc_rsi(closes, period=14):
    if len(closes) < period + 1:
        return None
    changes = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
    gains = [max(c, 0) for c in changes]
    losses = [max(-c, 0) for c in changes]
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def calc_macd(closes, fast=12, slow=26, signal=9):
    ema_fast = calc_ema_series(closes, fast)
    ema_slow = calc_ema_series(closes, slow)
    if not ema_fast or not ema_slow:
        return None
    # 对齐长度
    diff = len(ema_fast) - len(ema_slow)
    ema_fast_aligned = ema_fast[diff:]
    dif_line = [f - s for f, s in zip(ema_fast_aligned, ema_slow)]
    dea_series = calc_ema_series(dif_line, signal)
    if not dea_series:
        return None
    dif = dif_line[-1]
    dea = dea_series[-1]
    hist = (dif - dea) * 2
    # 判断金叉/死叉
    cross = "neutral"
    if len(dif_line) >= 2 and len(dea_series) >= 2:
        prev_dif = dif_line[-2]
        prev_dea = dea_series[-2]
        if prev_dif <= prev_dea and dif > dea:
            cross = "golden"
        elif prev_dif >= prev_dea and dif < dea:
            cross = "death"
    return {"dif": round(dif, 2), "dea": round(dea, 2), "hist": round(hist, 2), "cross": cross}


def calc_atr(klines, period=14):
    if len(klines) < period + 1:
        return None
    trs = []
    for i in range(1, len(klines)):
        h, l, pc = klines[i]["high"], klines[i]["low"], klines[i - 1]["close"]
        tr = max(h - l, abs(h - pc), abs(l - pc))
        trs.append(tr)
    return sum(trs[-period:]) / period


def calc_bollinger(closes, period=20, mult=2):
    if len(closes) < period:
        return None
    sma = sum(closes[-period:]) / period
    variance = sum((c - sma) ** 2 for c in closes[-period:]) / period
    std = math.sqrt(variance)
    upper = sma + mult * std
    lower = sma - mult * std
    bandwidth = (upper - lower) / sma * 100 if sma > 0 else 0
    return {
        "upper": round(upper, 2),
        "mid": round(sma, 2),
        "lower": round(lower, 2),
        "bandwidth": round(bandwidth, 2),
    }


# ── 主分析 ──────────────────────────────────────


def analyze_symbol(symbol, mode="15m"):
    result = {"symbol": symbol, "timestamp": datetime.now(SGT).isoformat(), "mode": mode}

    # 获取 ticker
    ticker = fetch_ticker(symbol)
    result["ticker"] = ticker

    # K 线周期选择
    if mode == "15m":
        intervals = {"1h": 300, "4h": 100}
    elif mode == "4h":
        intervals = {"1h": 300, "4h": 200, "1d": 100}
    else:  # 8h
        intervals = {"4h": 200, "1d": 100}

    result["indicators"] = {}
    for interval, limit in intervals.items():
        klines = fetch_klines(symbol, interval, limit)
        closes = [k["close"] for k in klines]

        indicators = {}
        rsi_val = calc_rsi(closes)
        indicators["rsi"] = round(rsi_val, 1) if rsi_val is not None else None
        indicators["macd"] = calc_macd(closes)
        atr_val = calc_atr(klines)
        indicators["atr"] = round(atr_val, 2) if atr_val is not None else None

        ema20 = calc_ema(closes, 20)
        ema50 = calc_ema(closes, 50)
        ema200 = calc_ema(closes, 200)
        indicators["ema"] = {
            "ema20": round(ema20, 2) if ema20 else None,
            "ema50": round(ema50, 2) if ema50 else None,
            "ema200": round(ema200, 2) if ema200 else None,
        }

        indicators["bollinger"] = calc_bollinger(closes)

        # 支撑阻力 (简单: 近期高低点)
        recent = closes[-20:]
        indicators["support"] = round(min(recent), 2)
        indicators["resistance"] = round(max(recent), 2)

        result["indicators"][interval] = indicators

    # 衍生品数据
    result["derivatives"] = {}
    try:
        result["derivatives"]["fundingRate"] = fetch_funding(symbol)
    except Exception:
        result["derivatives"]["fundingRate"] = None
    try:
        result["derivatives"]["openInterest"] = fetch_oi(symbol)
    except Exception:
        result["derivatives"]["openInterest"] = None
    try:
        result["derivatives"]["longShortRatio"] = fetch_lsr(symbol)
    except Exception:
        result["derivatives"]["longShortRatio"] = None

    return result


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Crypto technical analysis")
    parser.add_argument("--symbols", default="BTCUSDT,ETHUSDT", help="Comma-separated symbols")
    parser.add_argument("--mode", default="15m", choices=["15m", "4h", "8h"], help="Analysis mode")
    args = parser.parse_args()

    symbols = [s.strip().upper() for s in args.symbols.split(",")]
    results = []
    for symbol in symbols:
        try:
            result = analyze_symbol(symbol, args.mode)
            results.append(result)
        except Exception as e:
            results.append({"symbol": symbol, "error": str(e)})

    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
