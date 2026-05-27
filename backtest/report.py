"""Phase 1 backtest report — prints stats and evaluates gate criteria."""
import pandas as pd


# Minimum thresholds to pass Phase 1 gate
GATE = {
    "min_trades":      30,
    "min_win_rate":    0.40,
    "min_pf":          1.20,   # profit factor
    "min_expectancy":  0.0,    # avg R per trade > 0
    "max_drawdown":   30.0,    # %
}


def _trade_stats(pf) -> dict:
    trades = pf.trades.records_readable
    n = len(trades)
    if n == 0:
        return {"n": 0}

    wins   = trades[trades["PnL"] > 0]["PnL"]
    losses = trades[trades["PnL"] <= 0]["PnL"].abs()

    win_rate  = len(wins) / n
    avg_win   = wins.mean()   if len(wins)   > 0 else 0.0
    avg_loss  = losses.mean() if len(losses) > 0 else 1e-9
    pf_val    = (win_rate * avg_win) / ((1 - win_rate) * avg_loss)
    expect    = (win_rate * avg_win) - ((1 - win_rate) * avg_loss)

    vbt_stats = pf.stats()
    return {
        "n":          n,
        "win_rate":   win_rate,
        "avg_win":    avg_win,
        "avg_loss":   avg_loss,
        "pf":         pf_val,
        "expectancy": expect,
        "total_ret":  vbt_stats.get("Total Return [%]", float("nan")),
        "max_dd":     abs(vbt_stats.get("Max Drawdown [%]", float("nan"))),
        "sharpe":     vbt_stats.get("Sharpe Ratio", float("nan")),
    }


def _gate_check(s: dict) -> tuple[bool, list]:
    if s["n"] == 0:
        return False, ["zero trades"]
    fails = []
    if s["n"]        < GATE["min_trades"]:    fails.append(f"trades {s['n']} < {GATE['min_trades']}")
    if s["win_rate"] < GATE["min_win_rate"]:  fails.append(f"win rate {s['win_rate']:.1%} < {GATE['min_win_rate']:.0%}")
    if s["pf"]       < GATE["min_pf"]:        fails.append(f"profit factor {s['pf']:.2f} < {GATE['min_pf']}")
    if s["expectancy"] <= GATE["min_expectancy"]: fails.append(f"expectancy {s['expectancy']:.2f} ≤ 0")
    if s["max_dd"]   > GATE["max_drawdown"]:  fails.append(f"max DD {s['max_dd']:.1f}% > {GATE['max_drawdown']}%")
    return len(fails) == 0, fails


def print_section(label: str, long_pf, short_pf):
    ls = _trade_stats(long_pf)
    ss = _trade_stats(short_pf)
    combined_n = ls["n"] + ss["n"]

    print(f"\n{'-'*56}")
    print(f"  {label}")
    print(f"{'-'*56}")

    for direction, s in [("LONG", ls), ("SHORT", ss)]:
        if s["n"] == 0:
            print(f"  {direction:6s}  ->  0 trades")
            continue
        print(f"  {direction:6s}  trades={s['n']:3d}  "
              f"WR={s['win_rate']:.1%}  PF={s['pf']:.2f}  "
              f"E={s['expectancy']:+.2f}  "
              f"ret={s['total_ret']:+.1f}%  DD={s['max_dd']:.1f}%  "
              f"Sharpe={s['sharpe']:.2f}")

    print(f"  Total trades: {combined_n}")

    # Gate check on combined direction with more trades (usually tells the story)
    primary = ls if ls["n"] >= ss["n"] else ss
    passed, fails = _gate_check(primary)
    if combined_n == 0:
        print(f"\n  FAIL GATE FAIL  ->  zero trades generated")
        print("     Strategy too selective for this data window.")
        print("     Check: session filter, ATR threshold, indicator warmup.")
    elif passed:
        print(f"\n  PASS GATE PASS  ->  proceed to next split / Phase 2")
    else:
        print(f"\n  FAIL GATE FAIL  ->  {' | '.join(fails)}")
        print("     Do NOT proceed to live. Define a new strategy — do not re-tune this one.")
