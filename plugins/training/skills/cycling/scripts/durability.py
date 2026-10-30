#!/usr/bin/env python3
"""
durability.py — fatigue resistance from paired fresh and fatigued efforts.

Why this exists
---------------
Durability is the ability to hold power after accumulated work, and evidence in
well-trained amateurs indicates it does not correlate with VO2max or relative
FTP. A rider's threshold therefore says nothing about the quality that decides a
long event. Without a measured baseline, durability prescriptions have no KPI and
cannot be falsified, which is why the athlete profile blocks them until this
script has a result to record.

Protocol this expects
---------------------
  1. Fresh, standardised warm-up, then a 5-min and a 20-min maximal effort.
  2. On a separate day, the same warm-up, then steady riding at ~80% of the fresh
     20-min power until the target work (kJ) is complete, then repeat both efforts.
  3. Feed both pairs in here.

Reported quantities
-------------------
  decay_pct          (fresh - fatigued) / fresh * 100, per duration
  kj_per_kg          work normalised to body mass, the comparable dose axis
  percentile band    placement against published decay distributions
  durability_index   fatigued power as a fraction of fresh, per duration

Reference distributions
-----------------------
Percentile placement uses published decay values at ~2500 kJ in trained
cyclists. Those cohorts are lighter and younger than a typical amateur, so the
band is reported with an explicit transfer caveat and never as a grade. The dose
axis matters: decay measured at 1000 kJ is not comparable to decay at 2500 kJ,
and this script refuses to compare across dose without saying so.

Usage
-----
  durability.py --fresh 5min:350 20min:290 --fatigued 5min:315 20min:262 \
                --work-kj 1000 --mass 75
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from corelib import base_parser, emit, in_range, r, require  # noqa: E402

# Published decay reference at ~2500 kJ (trained/elite cohorts).
# Interpreted as: decay at or below this value sits at the stated percentile.
REFERENCE_2500KJ = {
    "5min": {"p75": 10.39, "cohort": "junior international, ~65 kg"},
    "20min": {"p75": 12.54, "cohort": "junior international, ~65 kg"},
}
# Amateur reference at 1000 kJ (mean +/- SD), well-trained amateurs.
REFERENCE_1000KJ = {
    "5min": {"mean": 10.8, "sd": 7.8, "cohort": "well-trained amateur, n=20"},
    "20min": {"mean": 10.1, "sd": 6.5, "cohort": "well-trained amateur, n=20"},
}


def parse_efforts(tokens: list[str]) -> dict[str, float]:
    out: dict[str, float] = {}
    for tok in tokens:
        require(":" in tok, f"bad effort token '{tok}', expected label:watts (e.g. 20min:290)")
        label, watts = tok.split(":")
        out[label.strip()] = float(watts)
    return out


def main() -> int:
    ap = base_parser(__doc__)
    ap.add_argument("--fresh", nargs="+", required=True, help="label:watts pairs")
    ap.add_argument("--fatigued", nargs="+", required=True, help="label:watts pairs")
    ap.add_argument("--work-kj", type=float, required=True,
                    help="accumulated work before the fatigued efforts")
    ap.add_argument("--mass", type=float, help="kg, for kJ/kg normalisation")
    args = ap.parse_args()

    notes: list[str] = []
    fresh = parse_efforts(args.fresh)
    fatigued = parse_efforts(args.fatigued)
    in_range("work_kj", args.work_kj, 200, 6000, notes)

    shared = [k for k in fresh if k in fatigued]
    require(bool(shared), "no duration label appears in both --fresh and --fatigued")
    missing = [k for k in fresh if k not in fatigued] + [k for k in fatigued if k not in fresh]
    if missing:
        notes.append(f"unpaired durations ignored: {sorted(set(missing))}")

    per_duration = {}
    for label in shared:
        f, g = fresh[label], fatigued[label]
        in_range(f"fresh_{label}_w", f, 50, 2000, notes)
        in_range(f"fatigued_{label}_w", g, 50, 2000, notes)
        decay = (f - g) / f * 100.0
        row = {"fresh_w": r(f, 1), "fatigued_w": r(g, 1),
               "decay_pct": r(decay, 2),
               "durability_index": r(g / f, 4)}
        if decay < 0:
            notes.append(f"{label}: fatigued power EXCEEDS fresh by {-decay:.1f}%. "
                         "The fresh effort was almost certainly submaximal or paced; "
                         "the pair is not interpretable as durability.")
        per_duration[label] = row

    outputs = {
        "work_kj": r(args.work_kj, 0),
        "per_duration": per_duration,
        "dose_axis_warning": ("decay is only comparable at matched kJ; do not compare "
                              "this result to one measured at a different work dose"),
    }

    if args.mass:
        in_range("mass_kg", args.mass, 30, 200, notes)
        kj_kg = args.work_kj / args.mass
        outputs["kj_per_kg"] = r(kj_kg, 2)
        if kj_kg < 11:
            notes.append(f"{kj_kg:.1f} kJ/kg is a light dose; decay at this load "
                         "discriminates poorly between riders")

    # percentile / band placement, only against a matched dose
    placement = {}
    if abs(args.work_kj - 2500) <= 250:
        for label, ref in REFERENCE_2500KJ.items():
            if label in per_duration:
                d = per_duration[label]["decay_pct"]
                placement[label] = {
                    "reference": "~2500 kJ, " + ref["cohort"],
                    "p75_decay_pct": ref["p75"],
                    "at_or_above_p75": d <= ref["p75"],
                }
    elif abs(args.work_kj - 1000) <= 150:
        for label, ref in REFERENCE_1000KJ.items():
            if label in per_duration:
                d = per_duration[label]["decay_pct"]
                z = (d - ref["mean"]) / ref["sd"]
                placement[label] = {
                    "reference": "~1000 kJ, " + ref["cohort"],
                    "cohort_mean_decay_pct": ref["mean"],
                    "cohort_sd": ref["sd"],
                    "z_score": r(z, 2),
                    "better_than_cohort_mean": d < ref["mean"],
                }
    else:
        notes.append(f"no reference distribution at {args.work_kj:.0f} kJ; decay is "
                     "reported without percentile placement. Reference doses are "
                     "~1000 kJ and ~2500 kJ.")

    if placement:
        outputs["placement"] = placement
        notes.append("TRANSFER CAVEAT: reference cohorts are lighter and, for the "
                     "2500 kJ set, younger than a typical amateur. Placement is "
                     "orientation, not a grade.")

    notes.append("Durability appears independent of VO2max and relative FTP in "
                 "well-trained amateurs; do not infer this result from threshold "
                 "data, and do not infer threshold from it.")
    notes.append("PROVENANCE: this is a measurement of the athlete, not a literature "
                 "claim. Record it in tests.yaml as MEASURED, under the fixed "
                 "protocol and dose it was run with.")

    emit("durability.py", vars(args), outputs, args.manifest, notes, args.quiet)
    return 0


if __name__ == "__main__":
    sys.exit(main())
