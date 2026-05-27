"""
Per-symbol configuration for all 6 tracked instruments.
Strategy logic is identical; only instrument-specific params differ.
"""

# Each symbol's config overrides/extends the base STRATEGY_CFG in run_phase1.py.
# min_atr: 1H ATR(14) floor — reject dead/illiquid sessions (instrument-specific units).
# fees:    round-trip cost fraction (spread approximation for Exness).
# mt5:     MT5 symbol string on Exness (check Market Watch — suffix may vary).
# yf:      yfinance ticker used as proxy until MT5 data is exported.

SYMBOLS = {
    "XAUUSD": {
        "mt5":     "XAUUSD",      # may be XAUUSDm on some Exness accounts
        "yf":      "GC=F",        # gold futures — best 1H history on yfinance
        "min_atr": 3.0,           # USD per oz; typical 1H ATR ~8-20
        "fees":    0.0002,        # ~$0.60 spread on $3000 gold
    },
    "EURUSD": {
        "mt5":     "EURUSD",
        "yf":      "EURUSD=X",
        "min_atr": 0.0005,        # 5 pip floor; typical 1H ATR ~8-20 pips
        "fees":    0.0001,        # ~1 pip spread
    },
    "GBPJPY": {
        "mt5":     "GBPJPY",
        "yf":      "GBPJPY=X",
        "min_atr": 0.20,          # 20 pip floor in JPY units; typical 1H ATR ~40-120 pips
        "fees":    0.00015,       # ~3 pip spread on GBPJPY
    },
    "USDCAD": {
        "mt5":     "USDCAD",
        "yf":      "USDCAD=X",
        "min_atr": 0.0004,        # 4 pip floor; typical 1H ATR ~8-18 pips
        "fees":    0.0001,
    },
    "BTCUSD": {
        "mt5":     "BTCUSD",      # may be BTCUSDm
        "yf":      "BTC-USD",
        "min_atr": 100.0,         # $100 floor; typical 1H ATR ~$200-2000
        "fees":    0.0005,        # higher spread on crypto CFD
    },
    "ETHUSD": {
        "mt5":     "ETHUSD",      # may be ETHUSDm
        "yf":      "ETH-USD",
        "min_atr": 5.0,           # $5 floor; typical 1H ATR ~$10-100
        "fees":    0.0008,
    },
}
