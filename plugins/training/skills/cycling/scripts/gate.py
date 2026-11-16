#!/usr/bin/env python3
"""
gate.py — progression gate for one interval type in one session.

Why this exists
---------------
The gate in references/review.md is arithmetic on rep powers. Left to the
model, it gets skipped for some interval types or computed ad hoc, so the
decision to push or hold has no trace. One run per interval type.

Rule (bands and step are conventions; see review.md)
----------------------------------------------------
  progress     mean >= target -2% and no rep below -5%
  hold         mean within -2% to -5%, or a rep below -5%
  recalibrate  mean below -5%, or a miss today after a miss in an earlier
               session at the same target (--prior-misses >= 1)

  next, progress:    add a rep up to --ceiling; at the ceiling, raise the
                     target 2.5% and return to --start-reps
  next, hold:        same target, same reps
  next, recalibrate: target = today's rep mean

Usage
-----
  gate.py --type "2min VO2" --target 310 --reps 314 307 308 297 \
          --reps-planned 12 --ceiling 15 [--prior-misses 0]
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from corelib import base_parser, emit, in_range, r, require  # noqa: E402

PROGRESS_BAND = -2.0   # % of target, convention
REP_FLOOR = -5.0       # % of target, convention
STEP = 0.025           # target raise at the rep ceiling, convention (2-3%)


def pct(x: float, target: float) -> float:
    return (x - target) / target * 100


def gate(target: float, reps: list[float], reps_planned: int, ceiling: int,
         start_reps: int, prior_misses: int) -> dict:
    mean = sum(reps) / len(reps)
    mean_pct, min_pct = pct(mean, target), pct(min(reps), target)
    if mean_pct >= PROGRESS_BAND and min_pct >= REP_FLOOR:
        verdict = "progress"
    elif mean_pct < REP_FLOOR or prior_misses >= 1:
        verdict = "recalibrate"
    else:
        verdict = "hold"

    if verdict == "progress" and reps_planned < ceiling:
        nxt = {"target_w": r(target, 0), "reps": reps_planned + 1}
    elif verdict == "progress":
        nxt = {"target_w": r(target * (1 + STEP), 0), "reps": start_reps}
    elif verdict == "hold":
        nxt = {"target_w": r(target, 0), "reps": reps_planned}
    else:
        nxt = {"target_w": r(mean, 0), "reps": reps_planned}
    return {"n_reps": len(reps), "mean_w": r(mean), "mean_pct": r(mean_pct),
            "min_w": r(min(reps)), "min_pct": r(min_pct), "verdict": verdict,
            "next": nxt}


def main() -> None:
    ap = base_parser(__doc__)
    ap.add_argument("--type", required=True, help="interval type label, e.g. '3min surge'")
    ap.add_argument("--target", type=float, required=True, help="planned rep power, W")
    ap.add_argument("--reps", type=float, nargs="+", required=True,
                    help="executed power of each work rep, W")
    ap.add_argument("--reps-planned", type=int, required=True)
    ap.add_argument("--ceiling", type=int, help="most reps the block allows (default: reps planned)")
    ap.add_argument("--start-reps", type=int, help="rep count after a target raise (default: reps planned)")
    ap.add_argument("--prior-misses", type=int, default=0,
                    help="earlier sessions in this block that missed this same target")
    a = ap.parse_args()

    require(a.target > 0, "--target must be positive")
    require(a.reps_planned > 0, "--reps-planned must be positive")
    ceiling = a.ceiling or a.reps_planned
    require(ceiling >= a.reps_planned, "--ceiling below --reps-planned")
    notes: list[str] = []
    in_range("target_w", a.target, 50, 1500, notes)
    if len(a.reps) != a.reps_planned:
        notes.append(f"{len(a.reps)} reps executed vs {a.reps_planned} planned")

    out = gate(a.target, a.reps, a.reps_planned, ceiling,
               a.start_reps or a.reps_planned, a.prior_misses)
    out = {"type": a.type, "target_w": r(a.target, 0), **out}
    emit("gate.py", vars(a), out, a.manifest, notes, a.quiet)


if __name__ == "__main__":
    main()
