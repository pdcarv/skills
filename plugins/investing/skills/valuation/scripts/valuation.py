#!/usr/bin/env python3
"""
valuation.py — FCFF DCF by scenario, reverse DCF and sensitivity grids.

Implements
----------
  case DCF       revenue -> EBIT margin -> NOPAT; reinvestment = NOPAT * g / ROIC,
                 so growth is always funded (g = reinvestment rate x ROIC holds by
                 construction); mid-year discounting by default
  terminal value perpetuity on NOPAT(n+1) * (1 - g_inf / ROIC_terminal), with
                 ROIC_terminal defaulting to WACC (excess returns fade); terminal
                 value share of EV reported and flagged above 75%
  exit multiple  optional EV/EBIT cross-check on year-n EBIT
  scenarios      bear / base / bull cases, probability-weighted, with the range
  reverse DCF    constant revenue growth that makes the base case equal the price
  sensitivity    5x5 grids centred on the base case: WACC x g_inf, growth x margin,
                 and beta x risk-free rate when CAPM inputs are given

Interpretive caution
--------------------
The model is only as good as its inputs. Every input must come from a dated,
verified source or be labelled an assumption. A reverse DCF has many solutions;
this one holds margin and ROIC fixed and solves for growth only, and says so.

Input (JSON, file or stdin)
---------------------------
  {"price": 50, "shares": 100, "net_debt": 200, "rev0": 1000, "years": 5,
   "tax": 0.25, "wacc": 0.09, "g_inf": 0.025, "rf": 0.03, "exit_ev_ebit": 12,
   "cases": {"bear": {"growth": 0.02, "margin": 0.12, "roic": 0.12},
             "base": {"growth": 0.05, "margin": 0.15, "roic": 0.15},
             "bull": {"growth": 0.08, "margin": 0.17, "roic": 0.18}},
   "probabilities": {"bear": 0.25, "base": 0.55, "bull": 0.20}}
  `growth` and `margin` may be single numbers or one value per year. Any key can
  be set per case or at the top level. Instead of `wacc`, give
  "capm": {"rf": 0.03, "beta": 1.1, "erp": 0.055, "kd_after_tax": 0.035, "wd": 0.2}.

Usage
-----
  valuation.py --input model.json [--manifest manifest.json]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import emit, fail, load_input, r  # noqa: E402


def wacc_of(c: dict) -> float:
    if "capm" in c:
        k = c["capm"]
        ke = k["rf"] + k["beta"] * k["erp"]
        wd = k.get("wd", 0.0)
        return (1 - wd) * ke + wd * k.get("kd_after_tax", 0.0)
    if "wacc" not in c:
        fail("give either wacc or capm inputs")
    return c["wacc"]


def per_year(v, n: int, name: str) -> list[float]:
    if isinstance(v, (int, float)):
        return [float(v)] * n
    if isinstance(v, list) and len(v) == n:
        return [float(x) for x in v]
    fail(f"{name} must be a number or a list of {n} values")


def dcf(c: dict) -> dict:
    n = int(c["years"])
    wacc, g_inf, tax, roic = wacc_of(c), c["g_inf"], c["tax"], c["roic"]
    roic_t = c.get("roic_terminal", wacc)
    if roic <= 0 or roic_t <= 0:
        fail("ROIC must be positive")
    if g_inf >= wacc:
        fail(f"terminal growth {g_inf} must be below WACC {wacc:.4f}")
    growth, margin = per_year(c["growth"], n, "growth"), per_year(c["margin"], n, "margin")
    mid = c.get("mid_year", True)
    rev, pv_sum, ebit, nopat = c["rev0"], 0.0, 0.0, 0.0
    for t in range(1, n + 1):
        g = growth[t - 1]
        rev *= 1 + g
        ebit = rev * margin[t - 1]
        nopat = ebit * (1 - tax)
        fcff = nopat * (1 - g / roic)
        pv_sum += fcff / (1 + wacc) ** (t - 0.5 if mid else t)
    fcff_tv = nopat * (1 + g_inf) * (1 - g_inf / roic_t)
    tv = fcff_tv / (wacc - g_inf)
    pv_tv = tv / (1 + wacc) ** n
    ev = pv_sum + pv_tv
    equity = ev - c.get("net_debt", 0.0)
    out = {"wacc": r(wacc, 4), "ev": r(ev), "pv_explicit": r(pv_sum), "pv_terminal": r(pv_tv),
           "tv_share_of_ev": r(pv_tv / ev, 3) if ev > 0 else None,
           "equity": r(equity), "per_share": r(equity / c["shares"], 2),
           "year_n_ebit": r(ebit), "implied_tv_ev_ebit": r(tv / ebit, 1) if ebit else None}
    if c.get("exit_ev_ebit"):
        pv_exit = ebit * c["exit_ev_ebit"] / (1 + wacc) ** n
        out["per_share_exit_multiple"] = r((pv_sum + pv_exit - c.get("net_debt", 0.0)) / c["shares"], 2)
    return out


def case_inputs(model: dict, name: str) -> dict:
    base = {k: v for k, v in model.items() if k not in ("cases", "probabilities")}
    return {**base, **model["cases"][name]}


def reverse_growth(c: dict, price: float) -> dict:
    def gap(g):
        return dcf({**c, "growth": g})["per_share"] - price
    lo, hi = -0.5, min(1.0, wacc_of(c) * 5)
    try:
        flo, fhi = gap(lo), gap(hi)
    except SystemExit:
        return {"solved": False, "reason": "model invalid in the search range"}
    if flo * fhi > 0:
        return {"solved": False, "reason": f"no constant growth in [{lo}, {hi:.2f}] matches the price"}
    for _ in range(80):
        mid = (lo + hi) / 2
        if gap(lo) * gap(mid) <= 0:
            hi = mid
        else:
            lo = mid
    return {"solved": True, "implied_growth": r((lo + hi) / 2, 4), "held_fixed": ["margin", "roic", "wacc", "g_inf"]}


def grid(c: dict, xkey: str, xs: list, ykey: str, ys: list) -> dict:
    rows = []
    for y in ys:
        row = []
        for x in xs:
            cc = {**c}
            for key, val in ((xkey, x), (ykey, y)):
                if key in ("beta", "rf"):
                    cc["capm"] = {**cc["capm"], key: val}
                else:
                    cc[key] = val
            try:
                row.append(dcf(cc)["per_share"])
            except SystemExit:
                row.append(None)
        rows.append(row)
    return {"x": xkey, "x_values": [r(v, 4) for v in xs], "y": ykey, "y_values": [r(v, 4) for v in ys], "per_share": rows}


def steps(centre: float, step: float) -> list[float]:
    return [centre + k * step for k in (-2, -1, 0, 1, 2)]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", default="-")
    ap.add_argument("--manifest")
    args = ap.parse_args()
    model = load_input(args.input)
    for k in ("cases", "shares", "rev0", "years", "tax", "g_inf"):
        if k not in model:
            fail(f"missing '{k}'")
    if "base" not in model["cases"]:
        fail("cases must include 'base'")
    notes: list[str] = []
    outputs: dict = {"cases": {}}
    for name in model["cases"]:
        outputs["cases"][name] = dcf(case_inputs(model, name))
    probs = model.get("probabilities")
    if probs:
        total = sum(probs.values())
        if abs(total - 1) > 1e-6:
            fail(f"probabilities sum to {total}, not 1")
        ev = sum(probs[n] * outputs["cases"][n]["per_share"] for n in probs)
        vals = [outputs["cases"][n]["per_share"] for n in probs]
        outputs["weighted_per_share"] = r(ev, 2)
        outputs["range_per_share"] = [min(vals), max(vals)]
    base = case_inputs(model, "base")
    b = outputs["cases"]["base"]
    if b["tv_share_of_ev"] is not None:
        if b["tv_share_of_ev"] > 0.75:
            notes.append(f"terminal value is {b['tv_share_of_ev']:.0%} of EV in the base case: the valuation is "
                         "mostly a terminal assumption; say so and defend it")
        elif not 0.5 <= b["tv_share_of_ev"] <= 0.7:
            notes.append(f"terminal value is {b['tv_share_of_ev']:.0%} of EV, outside the usual 50-70% band; check why")
    if model.get("rf") is not None and model["g_inf"] > model["rf"]:
        notes.append("terminal growth exceeds the risk-free rate of the valuation currency; justify or lower it")
    if "per_share_exit_multiple" in b and b["per_share"]:
        gap = b["per_share_exit_multiple"] / b["per_share"] - 1
        outputs["exit_vs_perpetuity_gap"] = r(gap, 3)
        if abs(gap) > 0.3:
            notes.append(f"exit-multiple value differs from perpetuity value by {gap:+.0%}; reconcile the terminal assumption")
    if model.get("price"):
        outputs["price"] = model["price"]
        outputs["reverse_dcf"] = reverse_growth(base, model["price"])
        outputs["upside_to_weighted"] = r(outputs["weighted_per_share"] / model["price"] - 1, 3) if probs else None
        notes.append("reverse DCF solves for constant growth with margin and ROIC held fixed; other assumption sets "
                     "also fit the price")
    w = wacc_of(base)
    g0 = base["growth"] if isinstance(base["growth"], (int, float)) else None
    m0 = base["margin"] if isinstance(base["margin"], (int, float)) else None
    outputs["sensitivity"] = [grid(base, "wacc", steps(w, 0.01), "g_inf", steps(model["g_inf"], 0.005))] \
        if "capm" not in base else []
    if g0 is not None and m0 is not None:
        outputs["sensitivity"].append(grid(base, "growth", steps(g0, 0.02), "margin", steps(m0, 0.02)))
    if "capm" in base:
        k = base["capm"]
        outputs["sensitivity"].append(grid(base, "beta", steps(k["beta"], 0.1), "rf", steps(k["rf"], 0.005)))
    notes.append("every input must carry a dated source or be labelled an assumption before this output is used")
    emit("valuation.py", model, outputs, notes, args.manifest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
