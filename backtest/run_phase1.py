"""
Phase 1 Backtest — XAUUSD Trend Pull v1
Run from D:\\trading root:
    python backtest/run_phase1.py

Data: yfinance GC=F (gold futures 1H, max history ~730 days)
      yfinance 1H limit: no data before ~2 years ago.
      For full history: export MT5 data to data/GC_F_1h.parquet and re-run.

Split: 70% in-sample (IS) -> 30% out-of-sample (OOS)
Gate:  strategy must pass BOTH splits to advance to Phase 2.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backtest.data_loader import load_1h, resample_4h
from backtest.indicators  import compute_1h, compute_4h
from backtest.signals     import build
from backtest.runner      import run
from backtest.report      import print_section

STRATEGY_CFG = {
    "rsi_pullback_threshold": 45.0,
    "rsi_momentum_threshold": 50.0,
    "pullback_lookback":      3,
    "min_atr":                3.0,
    "atr_sl_multiplier":      1.5,
    "rr_target":              2.5,
}

IS_SPLIT = 0.70   # first 70% = in-sample, last 30% = OOS


def main():
    print("=" * 56)
    print("  PHASE 1 BACKTEST — XAUUSD Trend Pull v1")
    print("=" * 56)

    # ── 1. Load & resample ──────────────────────────────────────────────
    df_1h_raw = load_1h("XAUUSD", "GC=F")
    df_4h_raw = resample_4h(df_1h_raw)
    print(f"[data] 1H bars: {len(df_1h_raw):,}  |  "
          f"range: {df_1h_raw.index[0].date()} -> {df_1h_raw.index[-1].date()}")

    # ── 2. Indicators ───────────────────────────────────────────────────
    df_1h = compute_1h(df_1h_raw)
    df_4h = compute_4h(df_4h_raw)
    print(f"[indicators] after warmup: {len(df_1h):,} 1H bars  |  "
          f"{len(df_4h):,} 4H bars")

    # ── 3. Signals ──────────────────────────────────────────────────────
    sigs = build(df_1h, df_4h, STRATEGY_CFG)
    long_n  = sigs["long_entry"].sum()
    short_n = sigs["short_entry"].sum()
    print(f"[signals] long entries: {long_n}  |  short entries: {short_n}")

    if long_n + short_n == 0:
        print("\n[WARN] Zero signals generated.")
        print("  Possible causes:")
        print("  - Not enough data for indicator warmup")
        print("  - Strategy too selective for this data window")
        print("  - ATR threshold too high (try reducing min_atr in config)")
        return

    # ── 4. Train/test split ─────────────────────────────────────────────
    n         = len(df_1h)
    split_at  = int(n * IS_SPLIT)
    is_idx    = df_1h.index[:split_at]
    oos_idx   = df_1h.index[split_at:]

    print(f"[split] IS:  {is_idx[0].date()} -> {is_idx[-1].date()}  "
          f"({len(is_idx):,} bars)")
    print(f"[split] OOS: {oos_idx[0].date()} -> {oos_idx[-1].date()}  "
          f"({len(oos_idx):,} bars)")

    # ── 5. Backtest ─────────────────────────────────────────────────────
    close = df_1h["close"]

    is_long,  is_short  = run(close.loc[is_idx],  sigs.loc[is_idx])
    oos_long, oos_short = run(close.loc[oos_idx], sigs.loc[oos_idx])

    # ── 6. Report ────────────────────────────────────────────────────────
    print_section(f"IN-SAMPLE  ({is_idx[0].date()} -> {is_idx[-1].date()})",
                  is_long, is_short)
    print_section(f"OUT-OF-SAMPLE  ({oos_idx[0].date()} -> {oos_idx[-1].date()})",
                  oos_long, oos_short)

    print("\n[NOTE] This backtest uses yfinance data (gold futures GC=F).")
    print("       Spread/slippage estimates are approximate.")
    print("       Re-run with real MT5 XAUUSD data for final Phase 1 validation.")
    print("       News filter not applied — historical calendar data not wired yet.")


if __name__ == "__main__":
    main()
