"""Compute all indicators required by XAUUSD Trend Pull v1."""
import pandas as pd
import pandas_ta as ta


def compute_1h(df: pd.DataFrame) -> pd.DataFrame:
    """Add EMA21, RSI14, MACD histogram, ATR14 to 1H frame."""
    d = df.copy()
    d["ema21"] = ta.ema(d["close"], length=21)
    d["rsi14"] = ta.rsi(d["close"], length=14)
    macd = ta.macd(d["close"], fast=12, slow=26, signal=9)
    d["macd_hist"] = macd[f"MACDh_12_26_9"]
    d["atr14"] = ta.atr(d["high"], d["low"], d["close"], length=14)
    return d.dropna()


def compute_4h(df: pd.DataFrame) -> pd.DataFrame:
    """Add EMA50, EMA200 to 4H context frame."""
    d = df.copy()
    d["ema50"] = ta.ema(d["close"], length=50)
    d["ema200"] = ta.ema(d["close"], length=200)
    return d.dropna()
