"""
Data loader for Phase 1 backtest.
Priority: local cache (data/) -> yfinance download.
To use MT5 data: export from MT5 as CSV, run convert_mt5_csv.py, cache auto-loads next run.
"""
from pathlib import Path

import pandas as pd
import yfinance as yf

DATA_DIR = Path("data")


def load_1h(symbol: str, yf_ticker: str) -> pd.DataFrame:
    """
    Load 1H OHLCV for a symbol.
    Priority: data/<SYMBOL>_1h.parquet (MT5 export) -> yfinance download.
    symbol:    instrument name used for cache filename (e.g. "XAUUSD")
    yf_ticker: yfinance ticker used as fallback (e.g. "GC=F")
    """
    # MT5 export takes priority (better data, longer history)
    mt5_cache = DATA_DIR / f"{symbol}_1h.parquet"
    yf_cache  = DATA_DIR / f"{yf_ticker.replace('=','_').replace('-','_')}_1h.parquet"

    for cache in [mt5_cache, yf_cache]:
        if cache.exists():
            df = pd.read_parquet(cache)
            src = "MT5" if cache == mt5_cache else "yfinance"
            print(f"[{symbol}] loaded {src} cache: {len(df):,} bars  "
                  f"({df.index[0].date()} -> {df.index[-1].date()})")
            return df

    return _download_and_cache(symbol, yf_ticker, "1h", yf_cache)


def resample_4h(df_1h: pd.DataFrame) -> pd.DataFrame:
    """Resample 1H bars to 4H. label=left means bar timestamp = period open."""
    return (
        df_1h.resample("4h", label="left", closed="left")
        .agg({"open": "first", "high": "max", "low": "min",
              "close": "last", "volume": "sum"})
        .dropna()
    )


def _download_and_cache(symbol: str, ticker: str, interval: str, cache: Path) -> pd.DataFrame:
    print(f"[{symbol}] downloading {ticker} {interval} from yfinance ...")
    raw = yf.download(ticker, period="max", interval=interval,
                      auto_adjust=True, progress=False)
    if raw.empty:
        raise RuntimeError(f"yfinance returned no data for {ticker} {interval}")

    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = [c[0].lower() for c in raw.columns]
    else:
        raw.columns = [c.lower() for c in raw.columns]

    raw.index = pd.to_datetime(raw.index, utc=True)
    df = raw[["open", "high", "low", "close", "volume"]].dropna()

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    df.to_parquet(cache)
    print(f"[{symbol}] saved {cache}  ({len(df):,} bars, "
          f"{df.index[0].date()} -> {df.index[-1].date()})")
    return df
