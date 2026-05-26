# Trading System — Task Tracker

## Phase 0 — Define Strategy
- [x] Write CLAUDE.md blueprint
- [x] Scaffold project structure
- [x] Define XAUUSD Trend Pull v1 strategy (`strategies/xauusd_trend_pull.py`)
- [ ] Verify MT5 symbol string for XAUUSD on Exness terminal (check suffix)
- [ ] Export 2+ years of XAUUSD 1H + 4H OHLCV from MT5 → `data/`

## Phase 1 — Backtest
- [ ] Build indicator computation pipeline (EMA21/50/200, RSI14, MACD, ATR14)
- [ ] Implement backtest runner using vectorbt
- [ ] Run in-sample backtest on 2020–2022 data
- [ ] Run out-of-sample validation on 2023–2024 data
- [ ] Walk-forward test across full history
- [ ] Report: expectancy, win rate, profit factor, max drawdown, trade count
- [ ] Gate check: passes → Phase 2. Fails → define a new strategy (do NOT tune this one)

## Phase 2 — Demo + Alerts (Telegram)
- [ ] Build live MT5 data connector
- [ ] Build indicator computation on live data
- [ ] Integrate news filter (economic calendar API)
- [ ] Integrate session filter
- [ ] Build Telegram alert formatter
- [ ] Run on DEMO account for 4+ weeks / 30+ trades
- [ ] Compare live stats to backtest stats
- [ ] Gate check: divergence acceptable → Phase 3

## Phase 3 — Semi-auto (Demo)
- [ ] Build order preparation module (entry/SL/TP/lot)
- [ ] Build Telegram confirm-to-execute flow
- [ ] Risk engine: exposure cap + daily kill-switch
- [ ] Test on demo with confirm step
- [ ] Gate check: zero risk violations → Phase 4

## Phase 4 — Micro Live Auto
- [ ] Ibrahim provides explicit written go-ahead
- [ ] Start at minimum lot size on real account
- [ ] All kill-switches armed
- [ ] Monitor for 30+ trades
- [ ] Gate check: stats consistent with demo → scale

## Symbols Queue (each earns own gate)
- [ ] XAUUSD (current)
- [ ] EURUSD (next — after XAUUSD Phase 4)
- [ ] GBPJPY
- [ ] USDCAD
- [ ] BTCUSD
- [ ] ETHUSD
