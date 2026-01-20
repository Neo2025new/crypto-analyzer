#!/usr/bin/env python3
"""
BTC 全周期分析工具
做市商视角 | 多路径推演 | 技术指标计算

使用方法:
    python btc_full_cycle_analysis.py
"""

import json
import urllib.request
import urllib.error
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import math

# ============================================================================
# API 数据获取
# ============================================================================

BASE_URL = "https://fapi.binance.com"

def fetch_json(url: str) -> Optional[dict]:
    """从 URL 获取 JSON 数据"""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"⚠️  获取数据失败: {e}")
        return None

def get_klines(symbol: str, interval: str, limit: int = 200) -> Optional[List]:
    """获取 K 线数据"""
    url = f"{BASE_URL}/fapi/v1/klines?symbol={symbol}USDT&interval={interval}&limit={limit}"
    return fetch_json(url)

def get_funding_rate(symbol: str) -> Optional[List]:
    """获取资金费率"""
    url = f"{BASE_URL}/fapi/v1/fundingRate?symbol={symbol}USDT&limit=1"
    return fetch_json(url)

def get_open_interest(symbol: str) -> Optional[dict]:
    """获取持仓量"""
    url = f"{BASE_URL}/fapi/v1/openInterest?symbol={symbol}USDT"
    return fetch_json(url)

def get_long_short_ratio(symbol: str, period: str = "1h") -> Optional[List]:
    """获取大户多空比"""
    url = f"{BASE_URL}/futures/data/topLongShortAccountRatio?symbol={symbol}USDT&period={period}&limit=1"
    return fetch_json(url)

def get_global_long_short_ratio(symbol: str, period: str = "1h") -> Optional[List]:
    """获取散户多空比"""
    url = f"{BASE_URL}/futures/data/globalLongShortAccountRatio?symbol={symbol}USDT&period={period}&limit=1"
    return fetch_json(url)

def get_taker_buy_sell_ratio(symbol: str, period: str = "1h") -> Optional[List]:
    """获取主动买卖比"""
    url = f"{BASE_URL}/futures/data/takerlongshortRatio?symbol={symbol}USDT&period={period}&limit=24"
    return fetch_json(url)

# ============================================================================
# 技术指标计算
# ============================================================================

def sma(data: List[float], period: int) -> List[float]:
    """简单移动平均"""
    result = []
    for i in range(len(data)):
        if i < period - 1:
            result.append(None)
        else:
            result.append(sum(data[i - period + 1:i + 1]) / period)
    return result

def ema(data: List[float], period: int) -> List[float]:
    """指数移动平均"""
    result = []
    k = 2 / (period + 1)
    for i, val in enumerate(data):
        if i == 0:
            result.append(val)
        else:
            result.append(val * k + result[-1] * (1 - k))
    return result

def calculate_rsi(closes: List[float], period: int = 14) -> List[float]:
    """计算 RSI"""
    gains = []
    losses = []
    for i in range(1, len(closes)):
        change = closes[i] - closes[i - 1]
        gains.append(max(change, 0))
        losses.append(max(-change, 0))

    # 使用 RMA (Wilder's smoothing)
    avg_gain = [None] * period
    avg_loss = [None] * period

    if len(gains) >= period:
        avg_gain.append(sum(gains[:period]) / period)
        avg_loss.append(sum(losses[:period]) / period)

        for i in range(period, len(gains)):
            avg_gain.append((avg_gain[-1] * (period - 1) + gains[i]) / period)
            avg_loss.append((avg_loss[-1] * (period - 1) + losses[i]) / period)

    rsi = [None]
    for i in range(len(avg_gain)):
        if avg_gain[i] is None or avg_loss[i] is None:
            rsi.append(None)
        elif avg_loss[i] == 0:
            rsi.append(100)
        else:
            rs = avg_gain[i] / avg_loss[i]
            rsi.append(100 - (100 / (1 + rs)))

    return rsi

def calculate_macd(closes: List[float]) -> Tuple[List[float], List[float], List[float]]:
    """计算 MACD"""
    ema12 = ema(closes, 12)
    ema26 = ema(closes, 26)
    dif = [e12 - e26 if e12 and e26 else None for e12, e26 in zip(ema12, ema26)]

    # 过滤 None 值计算 DEA
    dif_clean = [d for d in dif if d is not None]
    dea_clean = ema(dif_clean, 9) if dif_clean else []

    # 对齐 DEA
    dea = [None] * (len(dif) - len(dea_clean)) + dea_clean

    # 计算 MACD 柱状图
    macd_hist = []
    for d, e in zip(dif, dea):
        if d is not None and e is not None:
            macd_hist.append((d - e) * 2)
        else:
            macd_hist.append(None)

    return dif, dea, macd_hist

def calculate_atr(highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> List[float]:
    """计算 ATR"""
    tr = []
    for i in range(len(closes)):
        if i == 0:
            tr.append(highs[i] - lows[i])
        else:
            tr.append(max(
                highs[i] - lows[i],
                abs(highs[i] - closes[i - 1]),
                abs(lows[i] - closes[i - 1])
            ))

    # 使用 RMA
    atr = [None] * (period - 1)
    if len(tr) >= period:
        atr.append(sum(tr[:period]) / period)
        for i in range(period, len(tr)):
            atr.append((atr[-1] * (period - 1) + tr[i]) / period)

    return atr

def calculate_bollinger(closes: List[float], period: int = 20, std_mult: float = 2) -> Tuple[List[float], List[float], List[float], List[float]]:
    """计算布林带"""
    mid = sma(closes, period)
    upper = []
    lower = []
    bandwidth = []

    for i in range(len(closes)):
        if mid[i] is None:
            upper.append(None)
            lower.append(None)
            bandwidth.append(None)
        else:
            # 计算标准差
            window = closes[i - period + 1:i + 1]
            mean = mid[i]
            variance = sum((x - mean) ** 2 for x in window) / period
            std = math.sqrt(variance)

            upper.append(mid[i] + std_mult * std)
            lower.append(mid[i] - std_mult * std)
            bandwidth.append((upper[-1] - lower[-1]) / mid[i] * 100 if mid[i] != 0 else 0)

    return upper, mid, lower, bandwidth

def calculate_all_indicators(klines: List) -> Dict:
    """计算所有技术指标"""
    opens = [float(k[1]) for k in klines]
    highs = [float(k[2]) for k in klines]
    lows = [float(k[3]) for k in klines]
    closes = [float(k[4]) for k in klines]
    volumes = [float(k[5]) for k in klines]

    # EMA
    ema20 = ema(closes, 20)
    ema50 = ema(closes, 50)
    ema200 = ema(closes, 200)

    # RSI
    rsi = calculate_rsi(closes, 14)

    # MACD
    dif, dea, macd_hist = calculate_macd(closes)

    # ATR
    atr = calculate_atr(highs, lows, closes, 14)

    # 布林带
    boll_upper, boll_mid, boll_lower, boll_bw = calculate_bollinger(closes, 20, 2)

    # 最新值
    latest = {
        'open': opens[-1],
        'high': highs[-1],
        'low': lows[-1],
        'close': closes[-1],
        'volume': volumes[-1],
        'high_24h': max(highs[-24:]) if len(highs) >= 24 else max(highs),
        'low_24h': min(lows[-24:]) if len(lows) >= 24 else min(lows),
        'ema20': ema20[-1],
        'ema50': ema50[-1],
        'ema200': ema200[-1] if len(ema200) >= 200 else None,
        'rsi': rsi[-1],
        'macd_dif': dif[-1],
        'macd_dea': dea[-1],
        'macd_hist': macd_hist[-1],
        'atr': atr[-1],
        'boll_upper': boll_upper[-1],
        'boll_mid': boll_mid[-1],
        'boll_lower': boll_lower[-1],
        'boll_bw': boll_bw[-1],
    }

    # 计算变化
    if len(closes) >= 2:
        latest['change_pct'] = (closes[-1] - closes[-2]) / closes[-2] * 100
    if len(closes) >= 24:
        latest['change_24h'] = (closes[-1] - closes[-24]) / closes[-24] * 100

    # 判断趋势
    latest['trend'] = determine_trend(closes[-1], ema20[-1], ema50[-1], ema200[-1] if len(ema200) >= 200 else None)

    # MACD 状态
    latest['macd_signal'] = 'golden_cross' if dif[-1] > dea[-1] else 'death_cross'
    if len(dif) >= 2 and len(dea) >= 2:
        if dif[-2] <= dea[-2] and dif[-1] > dea[-1]:
            latest['macd_signal'] = 'just_golden_cross'
        elif dif[-2] >= dea[-2] and dif[-1] < dea[-1]:
            latest['macd_signal'] = 'just_death_cross'

    # RSI 状态
    if latest['rsi']:
        if latest['rsi'] > 70:
            latest['rsi_status'] = 'overbought'
        elif latest['rsi'] < 30:
            latest['rsi_status'] = 'oversold'
        elif latest['rsi'] > 50:
            latest['rsi_status'] = 'bullish'
        else:
            latest['rsi_status'] = 'bearish'

    return latest

def determine_trend(price: float, ema20: float, ema50: float, ema200: Optional[float]) -> str:
    """判断趋势"""
    if ema200:
        if price > ema20 > ema50 > ema200:
            return 'strong_bullish'
        elif price < ema20 < ema50 < ema200:
            return 'strong_bearish'

    if price > ema20 > ema50:
        return 'bullish'
    elif price < ema20 < ema50:
        return 'bearish'
    else:
        return 'ranging'

# ============================================================================
# 分析逻辑
# ============================================================================

def analyze_market_phase(indicators: Dict, funding_rate: float, oi_change: float) -> Dict:
    """判断做市阶段"""
    phases = {
        'accumulation': 0,  # 吸筹
        'markup': 0,        # 拉升
        'distribution': 0,  # 派发
        'markdown': 0,      # 下跌
        'rebalancing': 0,   # 再平衡
    }

    trend = indicators.get('trend', 'ranging')
    rsi = indicators.get('rsi', 50)
    macd_signal = indicators.get('macd_signal', '')
    boll_bw = indicators.get('boll_bw', 5)

    # 吸筹特征
    if trend in ['bearish', 'ranging'] and funding_rate < 0 and oi_change > 0:
        phases['accumulation'] += 40
    if rsi and rsi < 40 and boll_bw < 4:
        phases['accumulation'] += 30

    # 拉升特征
    if trend in ['bullish', 'strong_bullish'] and funding_rate > 0 and oi_change > 0:
        phases['markup'] += 40
    if rsi and rsi > 60 and 'golden' in macd_signal:
        phases['markup'] += 30

    # 派发特征
    if trend == 'strong_bullish' and funding_rate > 0.03:
        phases['distribution'] += 40
    if rsi and rsi > 70 and boll_bw > 8:
        phases['distribution'] += 30

    # 下跌特征
    if trend in ['bearish', 'strong_bearish'] and oi_change < 0:
        phases['markdown'] += 40
    if rsi and rsi < 40 and 'death' in macd_signal:
        phases['markdown'] += 30

    # 再平衡特征
    if trend == 'ranging' and abs(funding_rate) < 0.01:
        phases['rebalancing'] += 40
    if boll_bw < 3:
        phases['rebalancing'] += 20

    # 找出最可能的阶段
    max_phase = max(phases, key=phases.get)

    return {
        'phases': phases,
        'current_phase': max_phase,
        'confidence': phases[max_phase]
    }

def generate_paths(indicators: Dict, phase: str, price: float) -> List[Dict]:
    """生成多路径推演"""
    paths = []
    atr = indicators.get('atr', price * 0.02)

    if phase == 'accumulation':
        paths = [
            {
                'name': '路径 A：震荡吸筹后突破',
                'probability': 45,
                'direction': 'bullish',
                'path': f"${price:.0f} → ${price - atr:.0f}（假跌洗盘） → ${price + atr * 3:.0f}（突破）",
                'logic': '做市商在底部吸筹完毕，通过假跌清洗浮筹后拉升',
                'target_victims': '抄底止损盘、高杠杆多头',
                'confirmation': f'突破 ${price + atr:.0f} 并站稳',
                'invalidation': f'跌破 ${price - atr * 2:.0f} 形成新低',
            },
            {
                'name': '路径 B：继续横盘吸筹',
                'probability': 35,
                'direction': 'neutral',
                'path': f"${price:.0f} → ${price - atr * 0.5:.0f} ~ ${price + atr * 0.5:.0f}（横盘）",
                'logic': '吸筹尚未完成，继续在区间内震荡',
                'target_victims': '追涨杀跌者',
                'confirmation': '成交量持续萎缩，OI 缓慢上升',
                'invalidation': f'成交量放大并突破区间',
            },
            {
                'name': '路径 C：吸筹失败下跌',
                'probability': 20,
                'direction': 'bearish',
                'path': f"${price:.0f} → ${price - atr * 3:.0f}（破位下跌）",
                'logic': '宏观利空或抛压过大导致吸筹失败',
                'target_victims': '抄底多头',
                'confirmation': f'跌破 ${price - atr * 1.5:.0f} 且 OI 暴跌',
                'invalidation': f'回升至 ${price:.0f} 上方',
            },
        ]
    elif phase == 'markup':
        paths = [
            {
                'name': '路径 A：趋势延续',
                'probability': 50,
                'direction': 'bullish',
                'path': f"${price:.0f} → ${price + atr * 2:.0f}（继续上涨）",
                'logic': '多头动能充沛，趋势延续',
                'target_victims': '空头、观望者',
                'confirmation': '回调不破 EMA20，放量上涨',
                'invalidation': f'跌破 ${indicators.get("ema20", price - atr):.0f}',
            },
            {
                'name': '路径 B：回调整理',
                'probability': 35,
                'direction': 'neutral',
                'path': f"${price:.0f} → ${price - atr * 1.5:.0f}（回调） → ${price + atr:.0f}（反弹）",
                'logic': '短期获利盘了结，回调后继续上攻',
                'target_victims': '追高者、高杠杆多头',
                'confirmation': f'回调至 ${indicators.get("ema50", price - atr * 1.5):.0f} 获支撑',
                'invalidation': f'跌破 ${indicators.get("ema50", price - atr * 2):.0f}',
            },
            {
                'name': '路径 C：趋势反转',
                'probability': 15,
                'direction': 'bearish',
                'path': f"${price:.0f} → ${price - atr * 3:.0f}（反转下跌）",
                'logic': '主力派发完毕，趋势反转',
                'target_victims': '追高多头',
                'confirmation': '跌破关键支撑，OI 暴跌',
                'invalidation': f'回升至 ${price:.0f} 上方',
            },
        ]
    elif phase == 'distribution':
        paths = [
            {
                'name': '路径 A：诱多出货',
                'probability': 45,
                'direction': 'bearish',
                'path': f"${price:.0f} → ${price + atr:.0f}（假突破） → ${price - atr * 3:.0f}（下跌）",
                'logic': '做市商拉高诱多后出货',
                'target_victims': '追高者、FOMO 多头',
                'confirmation': f'假突破后跌破 ${price - atr:.0f}',
                'invalidation': f'站稳 ${price + atr * 1.5:.0f} 形成新高',
            },
            {
                'name': '路径 B：高位震荡',
                'probability': 35,
                'direction': 'neutral',
                'path': f"${price:.0f} → 高位区间震荡",
                'logic': '派发尚未完成，继续高位震荡消化',
                'target_victims': '追涨杀跌者',
                'confirmation': '成交量萎缩但价格维持',
                'invalidation': '成交量放大突破或破位',
            },
            {
                'name': '路径 C：继续上涨',
                'probability': 20,
                'direction': 'bullish',
                'path': f"${price:.0f} → ${price + atr * 3:.0f}（继续拉升）",
                'logic': '新资金入场，打破派发预期',
                'target_victims': '空头',
                'confirmation': '放量突破前高且 OI 上升',
                'invalidation': f'回落至 ${price - atr:.0f}',
            },
        ]
    elif phase == 'markdown':
        paths = [
            {
                'name': '路径 A：下跌延续',
                'probability': 50,
                'direction': 'bearish',
                'path': f"${price:.0f} → ${price - atr * 2:.0f}（继续下跌）",
                'logic': '空头动能充沛，下跌趋势延续',
                'target_victims': '抄底者、多头',
                'confirmation': '反弹不过 EMA20，缩量下跌',
                'invalidation': f'站稳 ${indicators.get("ema20", price + atr):.0f}',
            },
            {
                'name': '路径 B：反弹修复',
                'probability': 30,
                'direction': 'neutral',
                'path': f"${price:.0f} → ${price + atr * 1.5:.0f}（反弹） → ${price - atr:.0f}（继续下跌）",
                'logic': '超跌反弹，但不改变趋势',
                'target_victims': '抄底者、追涨者',
                'confirmation': f'反弹至 ${indicators.get("ema20", price + atr):.0f} 附近受阻',
                'invalidation': f'突破 ${indicators.get("ema50", price + atr * 2):.0f}',
            },
            {
                'name': '路径 C：触底反转',
                'probability': 20,
                'direction': 'bullish',
                'path': f"${price:.0f} → ${price + atr * 3:.0f}（V 型反转）",
                'logic': '恐慌抛售结束，多头强势入场',
                'target_victims': '空头、恐慌抛售者',
                'confirmation': '放量上涨，RSI 背离',
                'invalidation': f'跌破 ${price - atr * 1.5:.0f}',
            },
        ]
    else:  # rebalancing
        paths = [
            {
                'name': '路径 A：向上突破',
                'probability': 40,
                'direction': 'bullish',
                'path': f"${price:.0f} → ${price + atr * 2:.0f}（向上突破）",
                'logic': '震荡蓄力后选择向上',
                'target_victims': '空头、观望者',
                'confirmation': f'放量突破 ${price + atr:.0f}',
                'invalidation': f'假突破后回落',
            },
            {
                'name': '路径 B：向下突破',
                'probability': 35,
                'direction': 'bearish',
                'path': f"${price:.0f} → ${price - atr * 2:.0f}（向下突破）",
                'logic': '震荡蓄力后选择向下',
                'target_victims': '多头、抄底者',
                'confirmation': f'放量跌破 ${price - atr:.0f}',
                'invalidation': f'假跌后回升',
            },
            {
                'name': '路径 C：继续震荡',
                'probability': 25,
                'direction': 'neutral',
                'path': f"${price:.0f} 附近继续横盘",
                'logic': '多空均衡，继续在区间内博弈',
                'target_victims': '追涨杀跌者',
                'confirmation': '成交量持续萎缩',
                'invalidation': '成交量放大突破区间',
            },
        ]

    return paths

# ============================================================================
# 输出格式化
# ============================================================================

def format_number(num: float, decimals: int = 2) -> str:
    """格式化数字"""
    if num is None:
        return "N/A"
    if abs(num) >= 1e9:
        return f"{num / 1e9:.{decimals}f}B"
    elif abs(num) >= 1e6:
        return f"{num / 1e6:.{decimals}f}M"
    elif abs(num) >= 1e3:
        return f"{num / 1e3:.{decimals}f}K"
    else:
        return f"{num:.{decimals}f}"

def get_trend_arrow(trend: str) -> str:
    """获取趋势箭头"""
    arrows = {
        'strong_bullish': '↑↑',
        'bullish': '↑',
        'ranging': '—',
        'bearish': '↓',
        'strong_bearish': '↓↓',
    }
    return arrows.get(trend, '—')

def get_rsi_status_cn(status: str) -> str:
    """RSI 状态中文"""
    statuses = {
        'overbought': '超买',
        'oversold': '超卖',
        'bullish': '偏多',
        'bearish': '偏空',
    }
    return statuses.get(status, '中性')

def get_phase_cn(phase: str) -> str:
    """阶段中文"""
    phases = {
        'accumulation': '吸筹',
        'markup': '拉升',
        'distribution': '派发',
        'markdown': '下跌',
        'rebalancing': '再平衡',
    }
    return phases.get(phase, '未知')

def print_data_panel(symbol: str, interval: str, indicators: Dict, derivatives: Dict):
    """打印数据面板"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    print(f"""
┌─────────────────────────────────────────────────────────────────────┐
│ 📊 {symbol}/USDT 永续合约 │ {interval} │ {now}
├─────────────────────────────────────────────────────────────────────┤
│ 价格: ${indicators['close']:,.2f}  │ 24h: {indicators.get('change_24h', 0):+.2f}%  │ 成交量: ${format_number(indicators['volume'])}
├─────────────────────────────────────────────────────────────────────┤
│ 【持仓数据】
│ OI: {format_number(derivatives.get('oi', 0))} │ 资金费率: {derivatives.get('funding_rate', 0) * 100:.4f}% │ 多空比(大户): {derivatives.get('long_short_ratio', 'N/A')}
├─────────────────────────────────────────────────────────────────────┤
│ 【技术指标】
│ RSI(14): {indicators.get('rsi', 'N/A'):.1f} [{get_rsi_status_cn(indicators.get('rsi_status', 'neutral'))}] │ MACD: {indicators.get('macd_dif', 0):.2f}/{indicators.get('macd_dea', 0):.2f} │ ATR(14): ${indicators.get('atr', 0):,.2f}
│ 布林: ${indicators.get('boll_upper', 0):,.0f} / ${indicators.get('boll_mid', 0):,.0f} / ${indicators.get('boll_lower', 0):,.0f} │ 带宽: {indicators.get('boll_bw', 0):.2f}%
│ EMA: 20=${indicators.get('ema20', 0):,.0f} │ 50=${indicators.get('ema50', 0):,.0f} │ 200={f"${indicators['ema200']:,.0f}" if indicators.get('ema200') else 'N/A'}
│ 趋势: {get_trend_arrow(indicators.get('trend', 'ranging'))} {indicators.get('trend', 'ranging').replace('_', ' ').title()}
└─────────────────────────────────────────────────────────────────────┘
""")

def print_phase_analysis(phase_data: Dict, indicators: Dict, price: float):
    """打印做市阶段分析"""
    phase = phase_data['current_phase']
    phases = phase_data['phases']

    print(f"""
┌─────────────────────────────────────────────────────────────────────┐
│ 🎯 做市阶段判断
├─────────────────────────────────────────────────────────────────────┤
│ 吸筹: {'█' * (phases['accumulation'] // 10)}{' ' * (10 - phases['accumulation'] // 10)} {phases['accumulation']}%
│ 拉升: {'█' * (phases['markup'] // 10)}{' ' * (10 - phases['markup'] // 10)} {phases['markup']}%
│ 派发: {'█' * (phases['distribution'] // 10)}{' ' * (10 - phases['distribution'] // 10)} {phases['distribution']}%
│ 下跌: {'█' * (phases['markdown'] // 10)}{' ' * (10 - phases['markdown'] // 10)} {phases['markdown']}%
│ 再平衡: {'█' * (phases['rebalancing'] // 10)}{' ' * (10 - phases['rebalancing'] // 10)} {phases['rebalancing']}%
├─────────────────────────────────────────────────────────────────────┤
│ ➤ 当前判断: 【{get_phase_cn(phase)}】阶段 (置信度: {phase_data['confidence']}%)
└─────────────────────────────────────────────────────────────────────┘
""")

def print_paths(paths: List[Dict]):
    """打印多路径推演"""
    print("""
┌─────────────────────────────────────────────────────────────────────┐
│ 🔮 多路径推演
├─────────────────────────────────────────────────────────────────────┤""")

    for i, path in enumerate(paths):
        direction_icon = {'bullish': '📈', 'bearish': '📉', 'neutral': '📊'}.get(path['direction'], '📊')
        print(f"""
│ {path['name']} (概率: {path['probability']}%) {direction_icon}
│ ────────────────────────────────────────────────────────────────
│ 价格路径: {path['path']}
│ 庄家逻辑: {path['logic']}
│ 收割对象: {path['target_victims']}
│ 确认信号: {path['confirmation']}
│ 否定条件: {path['invalidation']}""")

    print("""
└─────────────────────────────────────────────────────────────────────┘""")

def print_multi_timeframe_matrix(results: Dict):
    """打印多周期共振矩阵"""
    print("""
┌──────────────────────────────────────────────────────────────────────────────┐
│ 📊 多周期共振矩阵
├────────┬────────┬────────┬───────────────┬───────────────────┬──────────────┤
│ 周期   │ 趋势   │ RSI    │ MACD          │ 关键位            │ 信号强度     │
├────────┼────────┼────────┼───────────────┼───────────────────┼──────────────┤""")

    for interval, data in results.items():
        ind = data['indicators']
        trend = get_trend_arrow(ind.get('trend', 'ranging'))
        rsi = f"{ind.get('rsi', 0):.1f}"
        macd = '金叉' if 'golden' in ind.get('macd_signal', '') else '死叉'
        support = f"S:${ind.get('boll_lower', 0):,.0f}"
        resistance = f"R:${ind.get('boll_upper', 0):,.0f}"

        # 计算信号强度
        strength = calculate_signal_strength(ind)
        stars = '★' * strength + '☆' * (5 - strength)

        print(f"│ {interval:6} │ {trend:6} │ {rsi:6} │ {macd:13} │ {support} {resistance:12} │ {stars:12} │")

    print("""├────────┴────────┴────────┴───────────────┴───────────────────┴──────────────┤""")

    # 共振分析
    trends = [r['indicators'].get('trend', 'ranging') for r in results.values()]
    bullish_count = sum(1 for t in trends if 'bullish' in t)
    bearish_count = sum(1 for t in trends if 'bearish' in t)

    if bullish_count >= 3:
        resonance = f"多头共振（{bullish_count}个周期一致看多）"
    elif bearish_count >= 3:
        resonance = f"空头共振（{bearish_count}个周期一致看空）"
    else:
        resonance = "无明显共振"

    print(f"│ 🔍 共振分析: {resonance:62} │")
    print("└──────────────────────────────────────────────────────────────────────────────┘")

def calculate_signal_strength(indicators: Dict) -> int:
    """计算信号强度 (1-5)"""
    strength = 3  # 基础分

    trend = indicators.get('trend', 'ranging')
    if 'strong' in trend:
        strength += 1

    rsi = indicators.get('rsi', 50)
    if rsi and (rsi > 70 or rsi < 30):
        strength += 1

    macd_signal = indicators.get('macd_signal', '')
    if 'just' in macd_signal:
        strength += 1

    return min(5, max(1, strength))

def print_trading_suggestions(indicators: Dict, phase: str, paths: List[Dict]):
    """打印操作建议"""
    price = indicators['close']
    atr = indicators.get('atr', price * 0.02)
    boll_bw = indicators.get('boll_bw', 5)

    # 根据波动率确定仓位建议
    if boll_bw > 8:
        vol_env = "高波动"
        position_pct = "≤30%"
        leverage = "≤3x"
    elif boll_bw < 4:
        vol_env = "低波动"
        position_pct = "50-70%"
        leverage = "≤10x"
    else:
        vol_env = "正常波动"
        position_pct = "40-50%"
        leverage = "≤5x"

    # 找出主路径
    main_path = paths[0]
    direction = main_path['direction']

    print(f"""
┌─────────────────────────────────────────────────────────────────────┐
│ 💡 操作建议
├─────────────────────────────────────────────────────────────────────┤
│ 波动率环境: {vol_env} │ 建议仓位: {position_pct} │ 杠杆建议: {leverage}
├─────────────────────────────────────────────────────────────────────┤
│ 【方向性建议】
│""")

    if direction == 'bullish' or (direction == 'neutral' and phase in ['accumulation', 'markup']):
        entry = price - atr * 0.5
        stop = price - atr * 1.5
        target1 = price + atr * 1.5
        target2 = price + atr * 3
        rr = (target1 - entry) / (entry - stop)
        print(f"│ 做多: 入场 ${entry:,.0f} | 止损 ${stop:,.0f} | 目标1 ${target1:,.0f} | 目标2 ${target2:,.0f} | 盈亏比 {rr:.1f}:1")

    if direction == 'bearish' or (direction == 'neutral' and phase in ['distribution', 'markdown']):
        entry = price + atr * 0.5
        stop = price + atr * 1.5
        target1 = price - atr * 1.5
        target2 = price - atr * 3
        rr = (entry - target1) / (stop - entry)
        print(f"│ 做空: 入场 ${entry:,.0f} | 止损 ${stop:,.0f} | 目标1 ${target1:,.0f} | 目标2 ${target2:,.0f} | 盈亏比 {rr:.1f}:1")

    print(f"""│
├─────────────────────────────────────────────────────────────────────┤
│ 【不建议操作】
│ ❌ 追涨杀跌，在极端位置重仓
│ ❌ 使用超过建议杠杆 ({leverage})
│ ❌ 忽略止损或移动止损逆向""")

    print(f"""│
├─────────────────────────────────────────────────────────────────────┤
│ 【关键监控】
│ 📍 多头确认位: ${indicators.get('boll_upper', price + atr):,.0f} (突破则看多)
│ 📍 空头确认位: ${indicators.get('boll_lower', price - atr):,.0f} (跌破则看空)
│ 📍 止损警戒位: ${price - atr * 1.5:,.0f} / ${price + atr * 1.5:,.0f}
└─────────────────────────────────────────────────────────────────────┘
""")

# ============================================================================
# 主程序
# ============================================================================

def analyze_single_timeframe(symbol: str, interval: str) -> Optional[Dict]:
    """分析单一时间周期"""
    print(f"\n⏳ 正在获取 {symbol} {interval} 数据...")

    klines = get_klines(symbol, interval, 200)
    if not klines:
        print(f"❌ 无法获取 {interval} K 线数据")
        return None

    indicators = calculate_all_indicators(klines)

    return {
        'interval': interval,
        'indicators': indicators,
        'klines': klines
    }

def analyze_full_cycle(symbol: str = "BTC"):
    """执行全周期分析"""
    print(f"""
╔═══════════════════════════════════════════════════════════════════════╗
║              🔍 {symbol}/USDT 全周期分析 (做市商视角)                    ║
╚═══════════════════════════════════════════════════════════════════════╝
""")

    # 获取衍生品数据
    print("⏳ 正在获取衍生品数据...")
    funding = get_funding_rate(symbol)
    oi = get_open_interest(symbol)
    ls_ratio = get_long_short_ratio(symbol)

    derivatives = {
        'funding_rate': float(funding[0]['fundingRate']) if funding else 0,
        'oi': float(oi['openInterest']) if oi else 0,
        'long_short_ratio': ls_ratio[0]['longShortRatio'] if ls_ratio else 'N/A'
    }

    # 分析多个周期
    intervals = ['1d', '4h', '1h', '15m']
    results = {}

    for interval in intervals:
        result = analyze_single_timeframe(symbol, interval)
        if result:
            results[interval] = result

    if not results:
        print("❌ 无法获取任何周期的数据，请检查网络连接")
        return

    # 打印多周期共振矩阵
    print_multi_timeframe_matrix(results)

    # 使用 1H 周期作为主要分析周期
    main_interval = '1h'
    if main_interval not in results:
        main_interval = list(results.keys())[0]

    main_data = results[main_interval]
    indicators = main_data['indicators']
    price = indicators['close']

    # 打印数据面板
    print_data_panel(symbol, main_interval, indicators, derivatives)

    # 做市阶段判断
    phase_data = analyze_market_phase(indicators, derivatives['funding_rate'], 0)
    print_phase_analysis(phase_data, indicators, price)

    # 多路径推演
    paths = generate_paths(indicators, phase_data['current_phase'], price)
    print_paths(paths)

    # 操作建议
    print_trading_suggestions(indicators, phase_data['current_phase'], paths)

    # 执行摘要
    print_executive_summary(symbol, indicators, phase_data, paths, derivatives)

def print_executive_summary(symbol: str, indicators: Dict, phase_data: Dict, paths: List[Dict], derivatives: Dict):
    """打印执行摘要"""
    price = indicators['close']
    atr = indicators.get('atr', price * 0.02)
    phase = phase_data['current_phase']
    main_path = paths[0]

    # 确定陷阱对象
    if phase in ['accumulation', 'markup']:
        trap_target = "扛空者、高杠杆空头"
    elif phase in ['distribution', 'markdown']:
        trap_target = "追多者、抄底者"
    else:
        trap_target = "追涨杀跌者、高杠杆双向"

    # 一句话总结
    if main_path['direction'] == 'bullish':
        summary = f"短期偏多，关注 ${price + atr:,.0f} 突破确认"
    elif main_path['direction'] == 'bearish':
        summary = f"短期偏空，关注 ${price - atr:,.0f} 支撑测试"
    else:
        summary = f"方向不明，等待 ${price - atr:,.0f}-${price + atr:,.0f} 区间突破"

    print(f"""
┌─────────────────────────────────────────────────────────────────────┐
│ 📋 执行摘要
├─────────────────────────────────────────────────────────────────────┤
│ 核心区间: ${price - atr:,.0f} – ${price + atr:,.0f}
│ 做市阶段: 【{get_phase_cn(phase)}】(置信度 {phase_data['confidence']}%)
│ 庄家意图: {main_path['logic'][:40]}...
│ 陷阱对象: {trap_target}
│
│ 💬 一句话: {summary}
└─────────────────────────────────────────────────────────────────────┘
""")

def generate_demo_data() -> Tuple[List, Dict]:
    """生成演示用模拟数据"""
    import random
    import time

    base_price = 104500
    current_time = int(time.time() * 1000)

    klines = []
    price = base_price - 5000  # 起始价格

    for i in range(200):
        # 模拟价格波动
        change = random.uniform(-0.015, 0.018) * price
        open_price = price
        close_price = price + change

        high = max(open_price, close_price) * (1 + random.uniform(0, 0.008))
        low = min(open_price, close_price) * (1 - random.uniform(0, 0.008))
        volume = random.uniform(5000, 15000)

        klines.append([
            current_time - (200 - i) * 3600000,  # timestamp
            str(open_price),
            str(high),
            str(low),
            str(close_price),
            str(volume),
            current_time - (199 - i) * 3600000,
            str(volume * close_price),
            random.randint(100, 500),
            str(volume * 0.5),
            str(volume * close_price * 0.5),
            "0"
        ])

        price = close_price

    derivatives = {
        'funding_rate': random.uniform(-0.0005, 0.0015),
        'oi': random.uniform(80000, 120000),
        'long_short_ratio': f"{random.uniform(0.8, 1.5):.4f}"
    }

    return klines, derivatives

def run_demo_analysis():
    """运行演示分析"""
    print("""
╔═══════════════════════════════════════════════════════════════════════╗
║         🔍 BTC/USDT 全周期分析 (做市商视角) - 演示模式                 ║
║                                                                         ║
║  ⚠️  当前使用模拟数据演示，实际使用请确保可访问币安 API                   ║
╚═══════════════════════════════════════════════════════════════════════╝
""")

    # 生成模拟数据
    print("⏳ 正在生成演示数据...")
    klines_1h, derivatives = generate_demo_data()

    # 分析多个周期 (使用相同数据模拟不同周期)
    intervals = ['1d', '4h', '1h', '15m']
    results = {}

    for interval in intervals:
        print(f"⏳ 正在分析 {interval} 周期...")
        indicators = calculate_all_indicators(klines_1h)
        results[interval] = {
            'interval': interval,
            'indicators': indicators,
            'klines': klines_1h
        }

    # 打印多周期共振矩阵
    print_multi_timeframe_matrix(results)

    # 使用 1H 周期作为主要分析周期
    main_data = results['1h']
    indicators = main_data['indicators']
    price = indicators['close']

    # 打印数据面板
    print_data_panel("BTC", "1h", indicators, derivatives)

    # 做市阶段判断
    phase_data = analyze_market_phase(indicators, derivatives['funding_rate'], 0)
    print_phase_analysis(phase_data, indicators, price)

    # 多路径推演
    paths = generate_paths(indicators, phase_data['current_phase'], price)
    print_paths(paths)

    # 操作建议
    print_trading_suggestions(indicators, phase_data['current_phase'], paths)

    # 执行摘要
    print_executive_summary("BTC", indicators, phase_data, paths, derivatives)

    print("""
╔═══════════════════════════════════════════════════════════════════════╗
║  📌 使用说明                                                            ║
║                                                                         ║
║  在可访问币安 API 的环境中运行:                                          ║
║    python btc_full_cycle_analysis.py                                    ║
║                                                                         ║
║  运行演示模式:                                                           ║
║    python btc_full_cycle_analysis.py --demo                             ║
╚═══════════════════════════════════════════════════════════════════════╝
""")

if __name__ == "__main__":
    import sys

    try:
        if "--demo" in sys.argv or len(sys.argv) > 1 and sys.argv[1] == "demo":
            run_demo_analysis()
        else:
            # 尝试真实分析，失败则自动切换到演示模式
            print("⏳ 正在尝试连接币安 API...")
            test = get_funding_rate("BTC")
            if test:
                analyze_full_cycle("BTC")
            else:
                print("⚠️  无法连接币安 API，自动切换到演示模式...\n")
                run_demo_analysis()
    except KeyboardInterrupt:
        print("\n\n⚠️ 分析已取消")
    except Exception as e:
        print(f"\n❌ 分析出错: {e}")
        print("⚠️  切换到演示模式...\n")
        run_demo_analysis()
