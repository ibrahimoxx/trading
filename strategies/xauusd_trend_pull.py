"""
Strategy: XAUUSD Trend Pull v1
Phase: 0 — defined, awaiting Phase 1 backtest gate

Logic: 4H sets trend direction; 1H detects pullback-then-resume entry.
All conditions are deterministic booleans — no discretion, no LLM in this path.
Do not modify entry rules without re-running the backtest.
"""

from dataclasses import dataclass

import pandas as pd


@dataclass
class Signal:
    direction: str    # "BUY" | "SELL" | "NONE"
    entry: float
    stop_loss: float
    take_profit: float
    rr: float
    reason: str

    def is_trade(self) -> bool:
        return self.direction != "NONE"

    def __str__(self) -> str:
        if not self.is_trade():
            return f"No trade — {self.reason}"
        return (
            f"XAUUSD {self.direction}\n"
            f"Entry:  {self.entry:.2f}\n"
            f"SL:     {self.stop_loss:.2f}\n"
            f"TP:     {self.take_profit:.2f}\n"
            f"RR:     1:{self.rr:.1f}"
        )


# ── 4H trend context ──────────────────────────────────────────────────────

def _bullish_trend_4h(df: pd.DataFrame) -> bool:
    """Close > EMA50 > EMA200 on 4H — confirmed uptrend."""
    c = df.iloc[-1]
    return bool(c["close"] > c["ema50"] > c["ema200"])


def _bearish_trend_4h(df: pd.DataFrame) -> bool:
    """Close < EMA50 < EMA200 on 4H — confirmed downtrend."""
    c = df.iloc[-1]
    return bool(c["close"] < c["ema50"] < c["ema200"])


# ── 1H entry conditions ───────────────────────────────────────────────────

def _pullback_occurred_long(df: pd.DataFrame, lookback: int, threshold: float) -> bool:
    """RSI dipped below threshold in last N closed bars (pullback into trend)."""
    window = df.iloc[-(lookback + 1):-1]
    return bool((window["rsi14"] < threshold).any())


def _momentum_resumed_long(df: pd.DataFrame, threshold: float) -> bool:
    """RSI now above threshold — bulls regained momentum."""
    return bool(df.iloc[-1]["rsi14"] > threshold)


def _macd_turned_bullish(df: pd.DataFrame) -> bool:
    """MACD histogram crossed from negative to positive on current bar."""
    return bool(df.iloc[-2]["macd_hist"] <= 0 < df.iloc[-1]["macd_hist"])


def _price_above_ema21(df: pd.DataFrame) -> bool:
    return bool(df.iloc[-1]["close"] > df.iloc[-1]["ema21"])


def _pullback_occurred_short(df: pd.DataFrame, lookback: int, threshold: float) -> bool:
    """RSI rose above threshold in last N bars (pullback in downtrend)."""
    window = df.iloc[-(lookback + 1):-1]
    return bool((window["rsi14"] > threshold).any())


def _momentum_resumed_short(df: pd.DataFrame, threshold: float) -> bool:
    return bool(df.iloc[-1]["rsi14"] < threshold)


def _macd_turned_bearish(df: pd.DataFrame) -> bool:
    """MACD histogram crossed from positive to negative on current bar."""
    return bool(df.iloc[-2]["macd_hist"] >= 0 > df.iloc[-1]["macd_hist"])


def _price_below_ema21(df: pd.DataFrame) -> bool:
    return bool(df.iloc[-1]["close"] < df.iloc[-1]["ema21"])


# ── Market quality guard ──────────────────────────────────────────────────

def _market_active(df: pd.DataFrame, min_atr: float) -> bool:
    """ATR(14) above minimum — reject dead/choppy markets."""
    return bool(df.iloc[-1]["atr14"] > min_atr)


# ── SL / TP calculation ───────────────────────────────────────────────────

def _sl_tp(
    entry: float,
    direction: str,
    atr: float,
    sl_mult: float,
    rr: float,
) -> tuple[float, float]:
    dist = atr * sl_mult
    if direction == "BUY":
        return round(entry - dist, 2), round(entry + dist * rr, 2)
    return round(entry + dist, 2), round(entry - dist * rr, 2)


# ── Main entry point ──────────────────────────────────────────────────────

def compute_signal(
    df_4h: pd.DataFrame,
    df_1h: pd.DataFrame,
    current_price: float,
    news_blocked: bool,
    session_active: bool,
    *,
    rsi_pullback_threshold: float = 45.0,
    rsi_momentum_threshold: float = 50.0,
    pullback_lookback: int = 3,
    min_atr: float = 3.0,
    atr_sl_multiplier: float = 1.5,
    rr_target: float = 2.5,
) -> Signal:
    """
    Compute a trade signal for XAUUSD using XAUUSD Trend Pull v1 rules.

    Required columns:
      df_4h : close, ema50, ema200
      df_1h : close, ema21, rsi14, macd_hist, atr14

    All indicators must be pre-computed by the caller.
    This function is pure logic — no I/O, no API calls.

    Parameters (match config/config.yaml strategy.XAUUSD section):
      rsi_pullback_threshold  : RSI level that defines a pullback (default 45)
      rsi_momentum_threshold  : RSI level that confirms resumed momentum (default 50)
      pullback_lookback       : bars to look back for the RSI dip (default 3)
      min_atr                 : minimum ATR(14) to trade (default 3.0 USD)
      atr_sl_multiplier       : SL = atr * multiplier (default 1.5)
      rr_target               : TP = SL_distance * rr_target (default 2.5)
    """
    def no_trade(reason: str) -> Signal:
        return Signal("NONE", current_price, 0.0, 0.0, 0.0, reason)

    if news_blocked:
        return no_trade("news_block")

    if not session_active:
        return no_trade("outside_session")

    if not _market_active(df_1h, min_atr):
        return no_trade("low_volatility")

    atr = float(df_1h.iloc[-1]["atr14"])

    # ── BUY conditions (all five must be True) ────────────────────────────
    long_ok = (
        _bullish_trend_4h(df_4h)
        and _pullback_occurred_long(df_1h, pullback_lookback, rsi_pullback_threshold)
        and _momentum_resumed_long(df_1h, rsi_momentum_threshold)
        and _macd_turned_bullish(df_1h)
        and _price_above_ema21(df_1h)
    )
    if long_ok:
        sl, tp = _sl_tp(current_price, "BUY", atr, atr_sl_multiplier, rr_target)
        return Signal("BUY", current_price, sl, tp, rr_target, "trend_pull_long")

    # ── SELL conditions (all five must be True) ───────────────────────────
    short_ok = (
        _bearish_trend_4h(df_4h)
        and _pullback_occurred_short(df_1h, pullback_lookback, 100 - rsi_pullback_threshold)
        and _momentum_resumed_short(df_1h, 100 - rsi_momentum_threshold)
        and _macd_turned_bearish(df_1h)
        and _price_below_ema21(df_1h)
    )
    if short_ok:
        sl, tp = _sl_tp(current_price, "SELL", atr, atr_sl_multiplier, rr_target)
        return Signal("SELL", current_price, sl, tp, rr_target, "trend_pull_short")

    return no_trade("no_setup")
