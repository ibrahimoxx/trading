"""
Translate XAUUSD Trend Pull v1 rules into vectorised boolean arrays.
All conditions deterministic — no LLM, no discretion.
News filter skipped in backtest (historical calendar data not wired yet).
"""
import pandas as pd


def _ffill_4h_onto_1h(df_4h: pd.DataFrame, idx_1h: pd.Index) -> pd.DataFrame:
    """
    Forward-fill completed 4H bar values onto 1H index.
    At each 1H bar we see the LAST COMPLETED 4H bar — no lookahead.
    """
    return df_4h.reindex(idx_1h, method="ffill")


def build(df_1h: pd.DataFrame, df_4h: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """
    Returns DataFrame indexed like df_1h with columns:
      long_entry, short_entry, sl_pct, tp_pct
    sl_pct / tp_pct are fractions of price (for vectorbt sl_stop / tp_stop).
    """
    ctx = _ffill_4h_onto_1h(df_4h[["ema50", "ema200", "close"]], df_1h.index)

    close   = df_1h["close"]
    rsi     = df_1h["rsi14"]
    mh      = df_1h["macd_hist"]
    atr     = df_1h["atr14"]
    ema21   = df_1h["ema21"]

    lb      = cfg["pullback_lookback"]
    rsi_pb  = cfg["rsi_pullback_threshold"]       # 45
    rsi_mo  = cfg["rsi_momentum_threshold"]        # 50

    # ── 4H trend ──────────────────────────────────────────────────────────
    bull_4h = (ctx["close"] > ctx["ema50"]) & (ctx["ema50"] > ctx["ema200"])
    bear_4h = (ctx["close"] < ctx["ema50"]) & (ctx["ema50"] < ctx["ema200"])

    # ── RSI pullback (dipped in last N closed bars) ───────────────────────
    rsi_dip_long  = rsi.rolling(lb).min() < rsi_pb
    rsi_dip_short = rsi.rolling(lb).max() > (100 - rsi_pb)

    # ── MACD histogram zero-cross ─────────────────────────────────────────
    macd_up = (mh.shift(1) <= 0) & (mh > 0)
    macd_dn = (mh.shift(1) >= 0) & (mh < 0)

    # ── Session filter (UTC 07–17) ────────────────────────────────────────
    hour       = pd.Series(df_1h.index.hour, index=df_1h.index)
    in_session = (hour >= 7) & (hour < 17)

    # ── Volatility guard ──────────────────────────────────────────────────
    active = atr > cfg["min_atr"]

    # ── Entry signals ─────────────────────────────────────────────────────
    long_entry = (
        bull_4h & rsi_dip_long & (rsi > rsi_mo)
        & macd_up & (close > ema21) & active & in_session
    )
    short_entry = (
        bear_4h & rsi_dip_short & (rsi < (100 - rsi_mo))
        & macd_dn & (close < ema21) & active & in_session
    )

    # ── SL / TP as fraction of price ─────────────────────────────────────
    sl_pct = (atr * cfg["atr_sl_multiplier"]) / close
    tp_pct = sl_pct * cfg["rr_target"]

    return pd.DataFrame({
        "long_entry":  long_entry.fillna(False),
        "short_entry": short_entry.fillna(False),
        "sl_pct":      sl_pct,
        "tp_pct":      tp_pct,
    }, index=df_1h.index)
