"""
Export 1H OHLCV for all 6 symbols directly from running MT5 terminal.

Requirements:
  - MT5 terminal must be open and logged into Exness
  - "Allow automated trading" must be ON in MT5 Tools -> Options -> Expert Advisors
  - pip install MetaTrader5

Run from D:\\trading root:
    python backtest/export_mt5_data.py

Output: data/<SYMBOL>_1h.parquet  (overwrites yfinance cache)
These files are auto-loaded by run_all_symbols.py on next run.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import MetaTrader5 as mt5

from config.symbols import SYMBOLS

DATA_DIR = Path("data")
BARS_REQUESTED = 100_000   # request max bars; MT5 returns what's available

MT5_TF = mt5.TIMEFRAME_H1


def export_symbol(name: str, cfg: dict) -> bool:
    mt5_sym = cfg["mt5"]

    # Try base name first, then with 'm' suffix (common on Exness)
    for sym in [mt5_sym, mt5_sym + "m"]:
        info = mt5.symbol_info(sym)
        if info is not None:
            mt5_sym = sym
            break
    else:
        print(f"  [{name}] SKIP — symbol '{cfg['mt5']}' not found in MT5 Market Watch")
        print(f"         Check: is {name} visible in Market Watch? Right-click -> Show All.")
        return False

    rates = mt5.copy_rates_from_pos(mt5_sym, MT5_TF, 0, BARS_REQUESTED)
    if rates is None or len(rates) == 0:
        print(f"  [{name}] ERROR — mt5.copy_rates_from_pos returned nothing")
        return False

    df = pd.DataFrame(rates)
    df["time"] = pd.to_datetime(df["time"], unit="s", utc=True)
    df = df.set_index("time").rename(columns={"tick_volume": "volume"})
    df = df[["open", "high", "low", "close", "volume"]].sort_index()

    out = DATA_DIR / f"{name}_1h.parquet"
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out)
    print(f"  [{name}] exported {len(df):,} bars  "
          f"({df.index[0].date()} -> {df.index[-1].date()})  -> {out}")
    return True


def main():
    print("MT5 Data Export — all 6 symbols")
    print("-" * 50)

    if not mt5.initialize():
        print("ERROR: mt5.initialize() failed.")
        print("  Is MT5 terminal open and connected to Exness?")
        print("  Error:", mt5.last_error())
        sys.exit(1)

    info = mt5.terminal_info()
    print(f"Connected: {info.name}  build={info.build}")
    acc = mt5.account_info()
    print(f"Account:   #{acc.login}  server={acc.server}  "
          f"{'DEMO' if acc.trade_mode == 0 else 'LIVE'}")
    print()

    success = 0
    for name, cfg in SYMBOLS.items():
        if export_symbol(name, cfg):
            success += 1

    mt5.shutdown()
    print(f"\nDone: {success}/{len(SYMBOLS)} symbols exported.")
    if success < len(SYMBOLS):
        print("Re-run backtest — missing symbols fall back to yfinance cache.")


if __name__ == "__main__":
    main()
