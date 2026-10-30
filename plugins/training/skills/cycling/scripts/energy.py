#!/usr/bin/env python3
"""
energy.py — expenditure, energy availability, and fuelling targets.

Relations
---------
  work_kJ        = mean power (W) x duration (s) / 1000
  exercise kcal  = work_kJ / (4.184 * gross_efficiency)
                   At ~23-24% gross efficiency this collapses to roughly
                   1 kcal per kJ, which is why the kJ~kcal shortcut works for
                   trained cyclists and fails for untrained ones.
  FFM            = mass * (1 - body_fat_fraction)
  BMR            = 500 + 22 * FFM            (Cunningham; athlete-appropriate)
  EA             = (intake_kcal - exercise_kcal) / FFM   [kcal/kg FFM/day]

Energy availability bands (IOC RED-S framing):
  >= 45  optimal      30-45  reduced / subclinical      < 30  clinical LEA risk

Carbohydrate
------------
Whether intake above 90 g/h improves performance over 60-90 g/h is contested
(frameworks.md, contested register); current guidelines stop at 90 g/h. This
script therefore returns a band capped at 90 g/h, never a single "optimal"
number, and notes the separate energy-balance argument for long days.

Usage
-----
  energy.py --power 200 --duration-s 14400 --mass 75 --body-fat 15 --intake 3600
  energy.py --cho-plan --duration-h 4.5 --mass 75
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from corelib import base_parser, emit, in_range, r, require  # noqa: E402

KJ_PER_KCAL = 4.184
DEFAULT_GE = 0.235          # gross efficiency, trained cyclist
EA_OPTIMAL, EA_REDUCED = 45.0, 30.0


def exercise_kcal(work_kj: float, gross_efficiency: float) -> float:
    return work_kj / (KJ_PER_KCAL * gross_efficiency)


def cunningham_bmr(ffm_kg: float) -> float:
    return 500.0 + 22.0 * ffm_kg


def cho_plan(duration_h: float, mass: float) -> dict:
    """Return a band, not a point, capped at the 90 g/h default ceiling."""
    if duration_h < 1.0:
        band, rationale = (0, 30), "under 1 h: fuelling is optional for trained athletes"
    elif duration_h < 2.0:
        band, rationale = (30, 60), "1-2 h: glucose-only transport is sufficient"
    elif duration_h < 3.0:
        band, rationale = (60, 90), "2-3 h: multiple transportable CHO indicated"
    else:
        band, rationale = (60, 90), ("3 h+: 90 g/h is the default ceiling; above it "
                                     "is contested for performance and needs gut "
                                     "training first. Energy balance on long days is "
                                     "a separate argument")
    return {
        "duration_h": duration_h,
        "cho_g_per_h_band": list(band),
        "cho_g_total_band": [r(band[0] * duration_h, 0), r(band[1] * duration_h, 0)],
        "rationale": rationale,
        "contested_ref": "frameworks.md contested register: carbohydrate above 90 g/h",
        "requires_glucose_fructose": duration_h >= 2.0,
        "gut_training_note": ("transporter density adapts to repeated exposure; a "
                              "target above habitual intake needs progressive "
                              "exposure in training, not first use on race day"),
    }


def main() -> int:
    ap = base_parser(__doc__)
    ap.add_argument("--power", type=float, help="mean session power, W")
    ap.add_argument("--work-kj", type=float, help="alternative to --power")
    ap.add_argument("--duration-s", type=float)
    ap.add_argument("--duration-h", type=float)
    ap.add_argument("--gross-efficiency", type=float, default=DEFAULT_GE)
    ap.add_argument("--mass", type=float)
    ap.add_argument("--body-fat", type=float, help="percent")
    ap.add_argument("--ffm", type=float, help="kg, overrides --body-fat")
    ap.add_argument("--intake", type=float, help="daily intake, kcal")
    ap.add_argument("--neat-factor", type=float, default=1.35,
                    help="non-exercise activity multiplier on BMR")
    ap.add_argument("--cho-plan", action="store_true")
    args = ap.parse_args()

    notes: list[str] = []
    outputs: dict = {}
    dur_s = args.duration_s or (args.duration_h * 3600 if args.duration_h else None)

    in_range("gross_efficiency", args.gross_efficiency, 0.15, 0.30, notes)
    if not (0.20 <= args.gross_efficiency <= 0.26):
        notes.append("gross efficiency outside the 20-26% trained-cyclist range; the "
                     "kJ~kcal shortcut does not hold here")

    work_kj = args.work_kj
    if work_kj is None and args.power and dur_s:
        in_range("power_w", args.power, 20, 700, notes)
        work_kj = args.power * dur_s / 1000.0

    if work_kj is not None:
        kcal = exercise_kcal(work_kj, args.gross_efficiency)
        outputs["work_kj"] = r(work_kj, 1)
        outputs["exercise_kcal"] = r(kcal, 0)
        outputs["kcal_per_kj"] = r(kcal / work_kj, 3)

    ffm = args.ffm
    if ffm is None and args.mass and args.body_fat is not None:
        in_range("mass_kg", args.mass, 30, 200, notes)
        in_range("body_fat_pct", args.body_fat, 3, 60, notes)
        ffm = args.mass * (1 - args.body_fat / 100.0)

    if ffm is not None:
        bmr = cunningham_bmr(ffm)
        outputs["ffm_kg"] = r(ffm, 1)
        outputs["bmr_kcal"] = r(bmr, 0)
        outputs["bmr_plus_neat_kcal"] = r(bmr * args.neat_factor, 0)
        outputs["ea_floor_intake_kcal"] = r(EA_OPTIMAL * ffm + outputs.get("exercise_kcal", 0), 0)

        if args.intake is not None and "exercise_kcal" in outputs:
            ea = (args.intake - outputs["exercise_kcal"]) / ffm
            outputs["energy_availability_kcal_kg_ffm"] = r(ea, 1)
            if ea < EA_REDUCED:
                outputs["ea_band"] = "clinical_LEA_risk"
                notes.append(f"EA {ea:.1f} kcal/kg FFM is below the 30 clinical "
                             "threshold. This is a health flag, not a training "
                             "variable, and outranks any performance objective.")
            elif ea < EA_OPTIMAL:
                outputs["ea_band"] = "reduced"
                notes.append(f"EA {ea:.1f} kcal/kg FFM sits in the 30-45 reduced band; "
                             "sustainable briefly, not across a build block")
            else:
                outputs["ea_band"] = "optimal"

    if args.cho_plan:
        require(args.duration_h is not None, "--cho-plan needs --duration-h")
        in_range("duration_h", args.duration_h, 0.25, 24, notes)
        outputs["cho_plan"] = cho_plan(args.duration_h, args.mass or 0)
        notes.append("CHO band is capped at the 90 g/h default ceiling; above it is "
                     "contested (frameworks.md). Do not assert a single optimal rate")

    require(bool(outputs), "nothing to compute; supply power/work, body composition, "
                           "or --cho-plan")
    emit("energy.py", vars(args), outputs, args.manifest, notes, args.quiet)
    return 0


if __name__ == "__main__":
    sys.exit(main())
