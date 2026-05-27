"""
Vectorbt portfolio simulation for XAUUSD Trend Pull v1.
Runs long-only and short-only portfolios separately for clean attribution.
"""
import vectorbt as vbt
import pandas as pd

INIT_CASH  = 100_000.0   # USD — used for drawdown % calculation
FEES       = 0.0002      # 0.02% per side (≈ $0.60 spread on $3000 gold)
SLIPPAGE   = 0.0001      # 0.01% execution slippage
SIZE       = 1.0         # 1 contract/unit per trade (sizing irrelevant for edge test)


def run(close: pd.Series, signals: pd.DataFrame) -> tuple:
    """
    Returns (long_portfolio, short_portfolio).
    sl_stop / tp_stop are per-bar ATR-based fraction arrays.
    """
    no_exit = pd.Series(False, index=close.index)

    long_pf = vbt.Portfolio.from_signals(
        close       = close,
        entries     = signals["long_entry"],
        exits       = no_exit,
        sl_stop     = signals["sl_pct"],
        tp_stop     = signals["tp_pct"],
        init_cash   = INIT_CASH,
        size        = SIZE,
        fees        = FEES,
        slippage    = SLIPPAGE,
        freq        = "1h",
    )

    short_pf = vbt.Portfolio.from_signals(
        close       = close,
        entries     = signals["short_entry"],
        exits       = no_exit,
        sl_stop     = signals["sl_pct"],
        tp_stop     = signals["tp_pct"],
        direction   = "shortonly",
        init_cash   = INIT_CASH,
        size        = SIZE,
        fees        = FEES,
        slippage    = SLIPPAGE,
        freq        = "1h",
    )

    return long_pf, short_pf
