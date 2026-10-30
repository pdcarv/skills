#!/usr/bin/env python3
"""
hrv.py — morning HRV readiness against a personal baseline.

Implements
----------
  baseline      mean and SD of daily morning RMSSD over a run-in period
                (default 28 days, the run-in used by Javaloyes 2019 and
                Heikura 2015); `fixed` uses the first N days, `rolling` the
                N days before the current window
  rolling mean  7-day rolling mean of the same series (decisions are made on
                the rolling mean, never on a single morning)
  band          baseline mean +/- k * SD (default k = 0.5)
  status        inside | below | above the band, or baseline_incomplete

Interpretive caution
--------------------
This is ONE reasonable convention, not a validated standard. The best HRV
index, recording position, baseline method (fixed or rolling) and band width
are unsettled (Manresa-Rocamora 2021). The 0.5 SD band is common practice and
unverified here. HRV-guided training beats predefined training only by small,
non-significant margins on performance; treat the status as one input to a
session decision, never as the decision.

Input is one value per line (or comma-separated), oldest first, RMSSD in ms.
Pure standard library, so it runs wherever python3 does.

Usage
-----
  hrv.py --values-file rmssd.txt
  hrv.py --values 62 58 71 ... --baseline-days 28 --window 7 --band-sd 0.5
  hrv.py --values-file rmssd.txt --baseline-mode rolling --raw
"""
from __future__ import annotations

import math
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from corelib import base_parser, emit, in_range, r, require  # noqa: E402


def readiness(values: list[float], baseline_days: int = 28, window: int = 7,
              band_sd: float = 0.5, log: bool = True, mode: str = "fixed") -> dict:
    require(all(v > 0 for v in values), "RMSSD values must be positive")
    series = [math.log(v) for v in values] if log else list(values)
    out = {"days": len(series), "transform": "ln" if log else "raw",
           "baseline_mode": mode, "baseline_days": baseline_days, "window": window}
    if mode == "fixed":
        need = baseline_days + window
        base = series[:baseline_days]
    else:
        need = baseline_days + window
        base = series[-(baseline_days + window):-window] if len(series) >= need else []
    if len(series) < need or len(base) < 2:
        out["status"] = "baseline_incomplete"
        out["days_needed"] = need - len(series) if len(series) < need else 0
        return out
    mean = statistics.fmean(base)
    sd = statistics.stdev(base)
    current = statistics.fmean(series[-window:])
    lo, hi = mean - band_sd * sd, mean + band_sd * sd
    out.update({"baseline_mean": r(mean, 4), "baseline_sd": r(sd, 4),
                "band": [r(lo, 4), r(hi, 4)], "band_sd": band_sd,
                "rolling_mean": r(current, 4),
                "status": "inside" if lo <= current <= hi else ("below" if current < lo else "above")})
    if log:
        out["rolling_mean_ms"] = r(math.exp(current), 1)
        out["band_ms"] = [r(math.exp(lo), 1), r(math.exp(hi), 1)]
    return out


def main() -> int:
    ap = base_parser(__doc__)
    ap.add_argument("--values", nargs="+", type=float, help="daily RMSSD in ms, oldest first")
    ap.add_argument("--values-file")
    ap.add_argument("--baseline-days", type=int, default=28)
    ap.add_argument("--window", type=int, default=7)
    ap.add_argument("--band-sd", type=float, default=0.5)
    ap.add_argument("--baseline-mode", choices=["fixed", "rolling"], default="fixed")
    ap.add_argument("--raw", action="store_true", help="use raw RMSSD instead of ln(RMSSD)")
    args = ap.parse_args()

    values = args.values
    if args.values_file:
        txt = Path(args.values_file).read_text().replace(",", "\n")
        values = [float(v) for v in txt.split() if v.strip()]
    require(bool(values), "supply --values or --values-file")

    notes: list[str] = []
    for v in values:
        in_range("rmssd_ms", v, 5, 250, notes)
    outputs = readiness(values, args.baseline_days, args.window, args.band_sd,
                        not args.raw, args.baseline_mode)
    if outputs["status"] == "baseline_incomplete":
        notes.append(f"baseline incomplete: {outputs['days_needed']} more daily readings "
                     "needed before HRV may inform a session decision")
    else:
        notes.append("convention, not a validated standard: band width, baseline method "
                     "and index choice are unsettled; one input to the decision, not the decision")
    emit("hrv.py", vars(args), outputs, args.manifest, notes, args.quiet)
    return 0


if __name__ == "__main__":
    sys.exit(main())
