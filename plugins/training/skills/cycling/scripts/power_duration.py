#!/usr/bin/env python3
"""
power_duration.py — critical power and W' from mean-maximal power data.

Models
------
2-parameter (linear work form):   W(t) = CP*t + W'
2-parameter (hyperbolic power):   P(t) = CP + W'/t
3-parameter (Morton):             P(t) = W'/(t - W'/(Pmax - CP)) + CP

Why the subset sensitivity block exists
---------------------------------------
A 2-point CP fit is fragile and its answer depends heavily on which durations
are chosen. A common numeric error is a 20-minute power carried forward as
FTP. This script therefore never returns a
bare CP: it returns CP together with the spread across every valid duration
subset, so a fragile fit is visibly fragile.

Valid fitting durations are 2-15 min (Jones/Vanhatalo convention). Efforts
shorter than 2 min are W'-dominated; longer than ~20 min drift below CP through
fatigue that the 2-parameter model does not represent.

Usage
-----
  power_duration.py --efforts 300:350 600:315 1200:290 [--all-durations]
  power_duration.py --efforts 60:600 300:350 600:315 1200:290 3600:255 \
                    --model both --manifest m.json
"""

from __future__ import annotations

import itertools
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from corelib import base_parser, emit, in_range, r, require  # noqa: E402

VALID_LO, VALID_HI = 120.0, 900.0          # seconds; canonical CP fitting window
TOLERATED_HI = 1200.0                       # 20 min accepted with a warning


def fit_2p(ts: list[float], ps: list[float]) -> tuple[float, float, float]:
    """Linear work-form fit. Returns (CP, W', r2)."""
    t = np.asarray(ts, dtype=float)
    w = np.asarray(ps, dtype=float) * t
    A = np.vstack([t, np.ones_like(t)]).T
    (cp, wp), *_ = np.linalg.lstsq(A, w, rcond=None)
    pred = cp * t + wp
    ss_res = float(((w - pred) ** 2).sum())
    ss_tot = float(((w - w.mean()) ** 2).sum())
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0
    return float(cp), float(wp), r2


def fit_3p(ts: list[float], ps: list[float]) -> dict | None:
    """Morton 3-parameter fit by coarse-to-fine search on Pmax."""
    if len(ts) < 3:
        return None
    t = np.asarray(ts, dtype=float)
    p = np.asarray(ps, dtype=float)
    cp0, wp0, _ = fit_2p(ts, ps)
    best = None
    for pmax in np.linspace(cp0 * 1.5, cp0 * 8.0, 400):
        for cp in np.linspace(cp0 * 0.75, cp0 * 1.15, 120):
            denom = pmax - cp
            if denom <= 1:
                continue
            # solve W' by least squares given cp, pmax
            # P = W'/(t - W'/denom) + CP  -> nonlinear in W'; grid it
            for wp in np.linspace(max(1000.0, wp0 * 0.4), wp0 * 2.5, 60):
                d = t - wp / denom
                if np.any(d <= 0):
                    continue
                pred = wp / d + cp
                sse = float(((p - pred) ** 2).sum())
                if best is None or sse < best[0]:
                    best = (sse, cp, wp, pmax)
    if best is None:
        return None
    sse, cp, wp, pmax = best
    return {"cp_w": r(cp, 1), "w_prime_j": r(wp, 0), "pmax_w": r(pmax, 0),
            "sse": r(sse, 2)}


def predict(cp: float, wp: float, t: float) -> float:
    return cp + wp / t


def subset_sensitivity(pairs: list[tuple[float, float]]) -> dict:
    """CP/W' across every 2+ point subset of valid durations."""
    cps, wps, rows = [], [], []
    for k in range(2, len(pairs) + 1):
        for combo in itertools.combinations(pairs, k):
            ts = [c[0] for c in combo]
            ps = [c[1] for c in combo]
            cp, wp, r2 = fit_2p(ts, ps)
            cps.append(cp)
            wps.append(wp)
            rows.append({"durations_s": ts, "cp_w": r(cp, 1),
                         "w_prime_j": r(wp, 0), "r2": r(r2, 4)})
    return {
        "n_subsets": len(rows),
        "cp_median_w": r(float(np.median(cps)), 1),
        "cp_min_w": r(min(cps), 1),
        "cp_max_w": r(max(cps), 1),
        "cp_spread_w": r(max(cps) - min(cps), 1),
        "cp_sd_w": r(float(np.std(cps, ddof=1)) if len(cps) > 1 else 0.0, 2),
        "w_prime_median_j": r(float(np.median(wps)), 0),
        "w_prime_spread_j": r(max(wps) - min(wps), 0),
        "subsets": rows,
    }


def main() -> int:
    ap = base_parser(__doc__)
    ap.add_argument("--efforts", nargs="+", required=True,
                    help="seconds:watts pairs, e.g. 300:350 600:315 1200:290")
    ap.add_argument("--model", choices=["2p", "3p", "both"], default="2p")
    ap.add_argument("--all-durations", action="store_true",
                    help="fit outside the 2-15 min window (records a warning)")
    ap.add_argument("--mass", type=float, help="kg, for W/kg reporting")
    args = ap.parse_args()

    notes: list[str] = []
    pairs_all: list[tuple[float, float]] = []
    for tok in args.efforts:
        require(":" in tok, f"bad effort token '{tok}', expected seconds:watts")
        s, w = tok.split(":")
        pairs_all.append((float(s), float(w)))
    pairs_all.sort()

    for t, p in pairs_all:
        in_range(f"power@{int(t)}s", p, 50, 2500, notes)

    if args.all_durations:
        pairs = pairs_all
        notes.append("WARNING: fitting outside the 2-15 min window on request; "
                     "CP will be biased low by durations >20 min")
    else:
        pairs = [(t, p) for t, p in pairs_all if VALID_LO <= t <= TOLERATED_HI]
        dropped = [int(t) for t, _ in pairs_all if (t, _) not in pairs]
        dropped = [int(t) for t, p in pairs_all if not (VALID_LO <= t <= TOLERATED_HI)]
        if dropped:
            notes.append(f"excluded durations (s) outside fitting window: {dropped}")
        for t, _ in pairs:
            if t > VALID_HI:
                notes.append(f"{int(t)}s is beyond the canonical 15-min ceiling; "
                             "retained but biases CP low")

    require(len(pairs) >= 2, "need at least 2 efforts inside the fitting window "
                             f"[{int(VALID_LO)}s, {int(TOLERATED_HI)}s]")

    ts = [p[0] for p in pairs]
    ps = [p[1] for p in pairs]
    cp, wp, r2 = fit_2p(ts, ps)

    if len(pairs) == 2:
        notes.append("FRAGILE: 2-point fit. CP is determined exactly by these two "
                     "efforts and carries no residual information. Treat as an "
                     "estimate, not a measurement.")
    if wp > 30000:
        notes.append(f"W' of {wp:.0f} J is high vs the 15-25 kJ trained range — "
                     "anaerobically rich relative to CP")
    if wp < 8000:
        notes.append(f"W' of {wp:.0f} J is low vs the 15-25 kJ trained range")

    outputs = {
        "cp_w": r(cp, 1),
        "w_prime_j": r(wp, 0),
        "r2": r(r2, 4),
        "n_efforts_used": len(pairs),
        "durations_used_s": [int(t) for t in ts],
        "predicted_w": {f"p{int(t)}s": r(predict(cp, wp, t), 1)
                        for t in (300, 600, 1200, 1800, 3600)},
    }
    if args.mass:
        in_range("mass_kg", args.mass, 30, 200, notes)
        outputs["cp_w_per_kg"] = r(cp / args.mass, 2)

    if len(pairs) >= 3:
        outputs["subset_sensitivity"] = subset_sensitivity(pairs)
        spread = outputs["subset_sensitivity"]["cp_spread_w"]
        if spread and spread > 15:
            notes.append(f"CP varies by {spread} W across duration subsets — the "
                         "fit is not robust; add efforts or re-test")

    if args.model in ("3p", "both"):
        three = fit_3p(ts, ps)
        if three:
            outputs["three_param"] = three
            if abs(three["cp_w"] - cp) > 10:
                notes.append(f"2-param CP {r(cp,1)} W and 3-param CP "
                             f"{three['cp_w']} W disagree by "
                             f"{abs(three['cp_w']-cp):.1f} W")
        else:
            notes.append("3-parameter fit needs >=3 efforts; skipped")

    emit("power_duration.py", {"efforts": args.efforts, "model": args.model,
                               "all_durations": args.all_durations,
                               "mass": args.mass},
         outputs, args.manifest, notes, args.quiet)
    return 0


if __name__ == "__main__":
    sys.exit(main())
