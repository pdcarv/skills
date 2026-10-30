#!/usr/bin/env python3
"""
zones.py — training zones anchored on measured LT1/LT2.

Anchoring matters: prescribing from a percentage of FTP and prescribing from
measured thresholds produce different average training responses. This script
therefore treats LT1/LT2 as the primary anchor and FTP as a flagged fallback.

Power zone scheme (fractions of the measured anchors):
    Z1 recovery       0            -> 0.75 * LT1
    Z2 endurance      0.75 * LT1   -> LT1
    Z3 tempo          LT1          -> LT1 + 0.5*(LT2 - LT1)
    Z4 sub-threshold  midpoint     -> LT2
    Z5 threshold      LT2          -> 1.05 * LT2
    Z6 VO2max         1.05 * LT2   -> 1.20 * LT2
    Z7 anaerobic      > 1.20 * LT2

Heart-rate zones use separate multipliers (0.88 / 1.03) because HR does not
scale with the power fractions.

The LT1/LT2 ratio is reported because it governs how wide the tempo band is. A
high ratio compresses Z3 and makes accidental grey-zone riding easy.

Usage
-----
  zones.py --lt1 200 --lt2 260 --mass 75 --lt1-hr 135 --lt2-hr 160
  zones.py --ftp 250 --mass 75              # fallback, emits a warning
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from corelib import base_parser, emit, in_range, r, require  # noqa: E402

POWER_SCHEME = [
    ("Z1_recovery",      None,            ("lt1", 0.75)),
    ("Z2_endurance",     ("lt1", 0.75),   ("lt1", 1.00)),
    ("Z3_tempo",         ("lt1", 1.00),   ("mid", 1.00)),
    ("Z4_subthreshold",  ("mid", 1.00),   ("lt2", 1.00)),
    ("Z5_threshold",     ("lt2", 1.00),   ("lt2", 1.05)),
    ("Z6_vo2max",        ("lt2", 1.05),   ("lt2", 1.20)),
    ("Z7_anaerobic",     ("lt2", 1.20),   None),
]

HR_LOW_MULT, HR_HIGH_MULT = 0.88, 1.03

# session targets expressed as fractions of LT2
SESSION_TARGETS = {
    "torque_T1":            (0.82, 0.88),
    "subthreshold_low":     (0.90, 0.94),
    "subthreshold_high":    (0.95, 0.98),
    "over_under_over":      (1.05, 1.07),
    "over_under_under":     (0.88, 0.88),
    "vo2_30_15":            (1.10, 1.18),
    "vo2_long":             (1.08, 1.12),
    "tempo":                (0.99, 1.03),
}


def resolve(anchor, lt1, lt2, mid):
    if anchor is None:
        return None
    base, mult = anchor
    return {"lt1": lt1, "lt2": lt2, "mid": mid}[base] * mult


def build_power_zones(lt1: float, lt2: float, mass: float | None) -> list[dict]:
    mid = lt1 + 0.5 * (lt2 - lt1)
    out = []
    for name, lo, hi in POWER_SCHEME:
        lo_w = resolve(lo, lt1, lt2, mid)
        hi_w = resolve(hi, lt1, lt2, mid)
        row = {"zone": name,
               "lo_w": r(lo_w, 0) if lo_w is not None else None,
               "hi_w": r(hi_w, 0) if hi_w is not None else None}
        if mass:
            row["lo_w_per_kg"] = r(lo_w / mass, 2) if lo_w is not None else None
            row["hi_w_per_kg"] = r(hi_w / mass, 2) if hi_w is not None else None
        out.append(row)
    return out


def build_hr_zones(lt1_hr: float, lt2_hr: float) -> list[dict]:
    mid = lt1_hr + 0.5 * (lt2_hr - lt1_hr)
    pts = [None, lt1_hr * HR_LOW_MULT, lt1_hr, mid, lt2_hr, lt2_hr * HR_HIGH_MULT, None, None]
    names = [n for n, _, _ in POWER_SCHEME]
    out = []
    for i, name in enumerate(names):
        lo, hi = pts[i], pts[i + 1]
        out.append({"zone": name,
                    "lo_bpm": int(lo) if lo else None,
                    "hi_bpm": int(hi) if hi else None,
                    "note": "HR unreliable at this intensity" if i >= 5 else None})
    return out


def main() -> int:
    ap = base_parser(__doc__)
    ap.add_argument("--lt1", type=float, help="measured LT1 power, W")
    ap.add_argument("--lt2", type=float, help="measured LT2 power, W")
    ap.add_argument("--ftp", type=float, help="FALLBACK only; emits a warning")
    ap.add_argument("--lt1-hr", type=float)
    ap.add_argument("--lt2-hr", type=float)
    ap.add_argument("--mass", type=float)
    ap.add_argument("--label", default="", help="e.g. indoor / outdoor")
    args = ap.parse_args()

    notes: list[str] = []
    anchor_kind = "measured_thresholds"

    if args.lt1 and args.lt2:
        lt1, lt2 = args.lt1, args.lt2
    elif args.ftp:
        # Population-average fallback. LT1 as a fraction of FTP varies 60-78%
        # across trained cyclists, so this band is wide and must stay flagged.
        anchor_kind = "ftp_fallback"
        lt2 = args.ftp
        lt1 = args.ftp * 0.72
        notes.append("FTP FALLBACK: LT1 imputed at 0.72*FTP. Across trained "
                     "cyclists LT1/FTP spans roughly 0.60-0.78, so the endurance "
                     "ceiling carries ~18 percentage points of uncertainty. "
                     "Zones derived this way are estimates, not prescriptions.")
        notes.append("PROVENANCE: outputs inherit STATED provenance from the FTP "
                     "input; confidence capped at Level 3.")
    else:
        require(False, "supply --lt1 and --lt2, or --ftp for flagged fallback")
        return 2

    in_range("lt1", lt1, 60, 500, notes)
    in_range("lt2", lt2, 80, 600, notes)
    require(lt2 > lt1, f"LT2 ({lt2}) must exceed LT1 ({lt1})")

    ratio = lt1 / lt2
    if ratio > 0.82:
        notes.append(f"LT1/LT2 = {ratio:.2f} is high (typical 0.72-0.80). The "
                     "tempo band is compressed, so the grey zone between "
                     "endurance and sub-threshold is easy to enter by accident. "
                     "Headroom is likelier at LT1 than at LT2.")
    elif ratio < 0.68:
        notes.append(f"LT1/LT2 = {ratio:.2f} is low; a wide aerobic band "
                     "suggests threshold work has more headroom than volume.")

    outputs = {
        "anchor": anchor_kind,
        "label": args.label or None,
        "lt1_w": r(lt1, 0),
        "lt2_w": r(lt2, 0),
        "lt1_lt2_ratio": r(ratio, 3),
        "tempo_band_width_w": r(0.5 * (lt2 - lt1), 0),
        "power_zones": build_power_zones(lt1, lt2, args.mass),
        "session_targets_w": {
            k: [r(lt2 * lo, 0), r(lt2 * hi, 0)] for k, (lo, hi) in SESSION_TARGETS.items()
        },
    }
    if args.mass:
        in_range("mass_kg", args.mass, 30, 200, notes)
        outputs["lt2_w_per_kg"] = r(lt2 / args.mass, 2)

    if args.lt1_hr and args.lt2_hr:
        require(args.lt2_hr > args.lt1_hr, "LT2 HR must exceed LT1 HR")
        in_range("lt2_hr", args.lt2_hr, 90, 220, notes)
        outputs["hr_zones"] = build_hr_zones(args.lt1_hr, args.lt2_hr)

    emit("zones.py", vars(args), outputs, args.manifest, notes, args.quiet)
    return 0


if __name__ == "__main__":
    sys.exit(main())
