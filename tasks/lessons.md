# Lessons Learned

Format: ## [YYYY-MM-DD] — [category]
What happened / Root cause / Rule going forward

## [2026-05-26] — architecture
Corrected from ChatGPT's plan: put LLM in the live execution path and invented a "confidence %" trigger.
Root cause: ChatGPT described infrastructure without questioning whether a live LLM call is safe or deterministic.
Rule: LLM (Claude/GPT) is OFFLINE only. Live loop is deterministic Python. No LLM call ever sits between signal and order.

## [2026-05-26] — edge-first
ChatGPT put backtesting at Phase 4. That means building execution infra for a strategy with no proven edge.
Root cause: assumed popular indicators = edge.
Rule: backtest with walk-forward + OOS comes first. If the strategy fails OOS, discard it — never tune until it passes.

## [2026-05-26] — stack
ChatGPT included CCXT, Freqtrade, Hummingbot, Binance/Bybit APIs for a trader who uses Exness MT5.
Root cause: generic crypto-bot template applied without reading the broker context.
Rule: Exness MT5 = MetaTrader5 Python package only for execution. No crypto-exchange tooling.

## [2026-05-26] — 100% trade myth
User expectation: "100% guaranteed / sure trade."
Root cause: misunderstanding of probability vs certainty in markets.
Rule: No trade is guaranteed. Goal = positive expectancy over many trades. Any system claiming 100% is either lying or will blow the account. Document and repeat this at every phase gate.
