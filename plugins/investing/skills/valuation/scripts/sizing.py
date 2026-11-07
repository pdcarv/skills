#!/usr/bin/env python3
"""
sizing.py — Kelly sizing from a scenario tree, capped by bands and survivability.

Implements
----------
  growth-optimal f   maximises sum(p_i * ln(1 + f * r_i)) over f in [0, 1] (no
                     leverage, no shorting), where r_i is the return from the
                     current price to scenario i's value
  fractional Kelly   default 0.5 x f*; 0.25 for weaker conviction evidence
  conviction band    tier -> band of equities NAV (portfolio-optimization.md 1.3):
                     core 8-15%, standard 4-8%, opportunistic 2-5%, tracking <=1%,
                     outside circle of competence 0%
  survivability cap  max size = tolerable portfolio drawdown / worst-case loss
  adopted size       min(fractional Kelly, band maximum, survivability cap), with
                     the binding constraint named

Interpretive caution
--------------------
Kelly is hypersensitive to the probabilities and returns, which are estimates.
The script reports how the size moves when the worst scenario's probability is
raised by 5 points, so a fragile size is visibly fragile.

Input (JSON)
------------
  {"scenarios": [{"name": "bear", "p": 0.25, "return": -0.40},
                 {"name": "base", "p": 0.55, "return": 0.20},
                 {"name": "bull", "p": 0.20, "return": 0.80}],
   "fraction": 0.5, "tier": "standard", "tolerable_drawdown": 0.03}
  `tolerable_drawdown` is the portfolio loss (fraction of NAV) the user can hold
  through from this position alone without forced action.

Usage
-----
  sizing.py --input sizing.json [--manifest manifest.json]
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import emit, fail, load_input, r  # noqa: E402

BANDS = {"core": (0.08, 0.15), "standard": (0.04, 0.08), "opportunistic": (0.02, 0.05),
         "tracking": (0.0, 0.01), "outside": (0.0, 0.0)}


def growth(f: float, sc: list[dict]) -> float:
    total = 0.0
    for s in sc:
        x = 1 + f * s["return"]
        if x <= 0:
            return -math.inf
        total += s["p"] * math.log(x)
    return total


def kelly(sc: list[dict]) -> float:
    lo, hi = 0.0, 1.0
    for _ in range(100):  # ternary search on a concave function
        m1, m2 = lo + (hi - lo) / 3, hi - (hi - lo) / 3
        if growth(m1, sc) < growth(m2, sc):
            lo = m1
        else:
            hi = m2
    f = (lo + hi) / 2
    return 0.0 if growth(f, sc) <= 0 else f


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", default="-")
    ap.add_argument("--manifest")
    args = ap.parse_args()
    d = load_input(args.input)
    sc: list[dict] = d.get("scenarios") or []
    if not sc or any("p" not in s or "return" not in s for s in sc):
        fail("scenarios need p and return")
    if abs(sum(s["p"] for s in sc) - 1) > 1e-6:
        fail("scenario probabilities must sum to 1")
    tier = d.get("tier", "standard")
    if tier not in BANDS:
        fail(f"tier must be one of {', '.join(BANDS)}")
    fraction = d.get("fraction", 0.5)
    notes: list[str] = []
    f_star = kelly(sc)
    exp_ret = sum(s["p"] * s["return"] for s in sc)
    worst = min(sc, key=lambda s: s["return"])
    candidates = {"fractional_kelly": f_star * fraction, "band_max": BANDS[tier][1]}
    if d.get("tolerable_drawdown") is not None and worst["return"] < 0:
        candidates["survivability_cap"] = d["tolerable_drawdown"] / -worst["return"]
    binding = min(candidates, key=lambda k: candidates[k])
    adopted = candidates[binding]
    # fragility: move 5 points of probability from the best to the worst scenario
    best = max(sc, key=lambda s: s["return"])
    shifted = [{**s, "p": s["p"] + (0.05 if s is worst else -0.05 if s is best else 0)} for s in sc]
    f_shift = kelly(shifted) if all(s["p"] >= 0 for s in shifted) else None
    outputs = {"expected_return": r(exp_ret, 4), "kelly_full": r(f_star, 4), "fraction": fraction,
               "candidates": {k: r(v, 4) for k, v in candidates.items()},
               "adopted_size": r(adopted, 4), "binding_constraint": binding,
               "tier": tier, "band": list(BANDS[tier]),
               "worst_case": {"name": worst.get("name"), "return": worst["return"],
                              "portfolio_loss_at_adopted": r(adopted * -worst["return"], 4) if worst["return"] < 0 else 0},
               "kelly_full_if_worst_plus_5pts": r(f_shift, 4) if f_shift is not None else None}
    if f_star >= 0.999:
        notes.append("growth-optimal fraction is at the 100% no-leverage cap: the tree implies more edge than "
                     "a long-only position can express; treat that as a reason to audit the tree, not to size up")
    if f_star == 0:
        notes.append("no positive expected log growth: Kelly says do not hold at this price")
    if adopted < BANDS[tier][0] and tier not in ("tracking", "outside"):
        notes.append(f"adopted size {adopted:.1%} is below the {tier} band floor {BANDS[tier][0]:.0%}: "
                     "the evidence supports a lower tier, or the position should wait for a better price")
    if f_shift is not None and f_star > 0 and f_shift < 0.6 * f_star:
        notes.append("Kelly falls by more than 40% when the worst case gains 5 points of probability: the size is "
                     "fragile to the tree; audit the worst branch")
    if binding == "survivability_cap":
        notes.append("the survivability cap binds below the Kelly fraction; the cap wins")
    notes.append("Kelly inputs are estimates; full Kelly is never used, and the tree itself must be audited "
                 "(base rates per branch, completeness of the worst case)")
    emit("sizing.py", d, outputs, notes, args.manifest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
