import MetaTrader5 as mt5

mt5.initialize()
print("TF_H1:", mt5.TIMEFRAME_H1)
print("symbol_select:", mt5.symbol_select("XAUUSDm", True))
r = mt5.copy_rates_from_pos("XAUUSDm", mt5.TIMEFRAME_H1, 0, 5)
print("rates:", r)
print("error:", mt5.last_error())
mt5.shutdown()
