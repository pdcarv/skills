#!/usr/bin/env python3
"""
screens.py — deterministic quality, distress and value screens.

Implements
----------
  piotroski   F-score, nine binary signals from two consecutive fiscal years:
              profitability (ROA > 0, CFO > 0, ROA up, CFO > net income),
              leverage and liquidity (long-term debt ratio down, current ratio up,
              no new shares), efficiency (gross margin up, asset turnover up)
  altman      Z-score; `model: "original"` (public manufacturers, 1968 weights)
              or `model: "z2"` (non-manufacturers, Z''), with zone labels
  greenblatt  earnings yield = EBIT / EV; return on capital =
              EBIT / (net working capital + net fixed assets)
  quality     ROCE = EBIT / (total assets - current liabilities); cash conversion
              = sum(FCF) / sum(net income) over the years given; gross margin;
              interest cover = EBIT / interest expense

Each screen returns its inputs' derived ratios and a verdict string. The screens
feed the lens checks; they are evidence, not the decision. Financials (banks,
insurers) distort most of these ratios; the script says so when `sector` is
"financial".

Input (JSON): {"sector": "industrial", "current": {...}, "prior": {...},
               "history": [{"fcf": .., "net_income": ..}, ...], "ev": ..}
Field names are listed in each function. Missing fields skip that screen with a
note rather than guessing.

Usage
-----
  screens.py --input company.json [--manifest manifest.json]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import emit, load_input, r  # noqa: E402


def need(d: dict, keys: list[str]) -> list[str]:
    return [k for k in keys if d.get(k) is None]


def piotroski(cur: dict, pri: dict) -> dict:
    keys = ["net_income", "total_assets", "cfo", "long_term_debt", "current_assets",
            "current_liabilities", "shares", "gross_profit", "revenue"]
    missing = need(cur, keys) + [f"prior.{k}" for k in need(pri, keys)]
    if missing:
        return {"skipped": True, "missing": missing}
    roa, roa_p = cur["net_income"] / cur["total_assets"], pri["net_income"] / pri["total_assets"]
    signals = {
        "roa_positive": roa > 0,
        "cfo_positive": cur["cfo"] > 0,
        "roa_improving": roa > roa_p,
        "cfo_exceeds_net_income": cur["cfo"] > cur["net_income"],
        "leverage_falling": cur["long_term_debt"] / cur["total_assets"] < pri["long_term_debt"] / pri["total_assets"],
        "current_ratio_rising": cur["current_assets"] / cur["current_liabilities"]
        > pri["current_assets"] / pri["current_liabilities"],
        "no_new_shares": cur["shares"] <= pri["shares"],
        "gross_margin_rising": cur["gross_profit"] / cur["revenue"] > pri["gross_profit"] / pri["revenue"],
        "asset_turnover_rising": cur["revenue"] / cur["total_assets"] > pri["revenue"] / pri["total_assets"],
    }
    score = sum(signals.values())
    verdict = "strong (8-9)" if score >= 8 else "weak (0-2)" if score <= 2 else "middling (3-7)"
    return {"score": score, "signals": signals, "verdict": verdict}


def altman(cur: dict, model: str) -> dict:
    keys = ["current_assets", "current_liabilities", "total_assets", "retained_earnings", "ebit", "total_liabilities"]
    if model == "original":
        keys += ["market_cap", "revenue"]
    else:
        keys += ["book_equity"]
    missing = need(cur, keys)
    if missing:
        return {"skipped": True, "missing": missing}
    ta = cur["total_assets"]
    a = (cur["current_assets"] - cur["current_liabilities"]) / ta
    b = cur["retained_earnings"] / ta
    c = cur["ebit"] / ta
    if model == "original":
        d = cur["market_cap"] / cur["total_liabilities"]
        e = cur["revenue"] / ta
        z = 1.2 * a + 1.4 * b + 3.3 * c + 0.6 * d + 1.0 * e
        zone = "safe" if z > 2.99 else "grey" if z >= 1.81 else "distress"
    else:
        d = cur["book_equity"] / cur["total_liabilities"]
        z = 6.56 * a + 3.26 * b + 6.72 * c + 1.05 * d
        zone = "safe" if z > 2.6 else "grey" if z >= 1.1 else "distress"
    return {"model": model, "z": r(z, 2), "zone": zone}


def greenblatt(cur: dict, ev: float | None) -> dict:
    missing = need(cur, ["ebit", "current_assets", "current_liabilities", "net_fixed_assets"])
    if ev is None:
        missing.append("ev")
    if missing:
        return {"skipped": True, "missing": missing}
    capital = cur["current_assets"] - cur["current_liabilities"] + cur["net_fixed_assets"]
    return {"earnings_yield": r(cur["ebit"] / ev, 4),
            "return_on_capital": r(cur["ebit"] / capital, 4) if capital > 0 else None}


def quality(cur: dict, history: list[dict]) -> dict:
    out: dict = {}
    if not need(cur, ["ebit", "total_assets", "current_liabilities"]):
        out["roce"] = r(cur["ebit"] / (cur["total_assets"] - cur["current_liabilities"]), 4)
    if not need(cur, ["gross_profit", "revenue"]):
        out["gross_margin"] = r(cur["gross_profit"] / cur["revenue"], 4)
    if not need(cur, ["ebit", "interest_expense"]) and cur["interest_expense"] > 0:
        out["interest_cover"] = r(cur["ebit"] / cur["interest_expense"], 2)
    rows = [h for h in history if h.get("fcf") is not None and h.get("net_income") is not None]
    if rows:
        ni = sum(h["net_income"] for h in rows)
        out["cash_conversion"] = r(sum(h["fcf"] for h in rows) / ni, 3) if ni > 0 else None
        out["cash_conversion_years"] = len(rows)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", default="-")
    ap.add_argument("--manifest")
    args = ap.parse_args()
    data = load_input(args.input)
    cur, pri = data.get("current", {}), data.get("prior", {})
    notes: list[str] = []
    outputs = {"piotroski": piotroski(cur, pri),
               "altman": altman(cur, data.get("altman_model", "z2")),
               "greenblatt": greenblatt(cur, data.get("ev")),
               "quality": quality(cur, data.get("history", []))}
    for name, res in outputs.items():
        if isinstance(res, dict) and res.get("skipped"):
            notes.append(f"{name} skipped: missing {', '.join(res['missing'])}")
    q = outputs["quality"]
    if q.get("cash_conversion") is not None and q["cash_conversion"] < 0.8:
        notes.append(f"cash conversion {q['cash_conversion']:.0%} is below 80% over {q['cash_conversion_years']} "
                     "years; the quality lens requires an explanation")
    if data.get("sector") == "financial":
        notes.append("financial company: Altman, Greenblatt and ROCE are not meaningful; use residual income and "
                     "regulatory capital measures instead")
    notes.append("screens are evidence for the lens checks, not a decision; every input needs a dated filing source")
    emit("screens.py", data, outputs, notes, args.manifest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
