#!/usr/bin/env python3
"""
ride_physics.py — air density, the power-speed relation, drafting, aero fraction.

Model
-----
    P_total = [ m*g*(sin(theta) + Crr*cos(theta))*v  +  0.5*rho*CdA*(v+w)^2*v
                + m*a*v ] / eta

Air density from the barometric formula plus the ideal gas law:
    p  = 101325 * (1 - 2.25577e-5 * h)^5.25588
    rho = p / (R_d * T),   R_d = 287.058 J/(kg K)
Sea level at 15 C returns 1.2250 kg/m3, the ISA value, which is the calibration
check in the test suite.

Why aero fraction is reported
-----------------------------
An intervention that only helps above a given speed delivers its headline watts
only for the fraction of time spent there. Reporting the aero share of total
power at the stated gradient is what stops a wind-tunnel number being applied to
a climb where it is worth nothing.

Usage
-----
  ride_physics.py --density --altitude 400 --temp 32
  ride_physics.py --speed-from-power --power 240 --mass 83 --grade 0.07 \
                  --cda 0.36 --altitude 400 --temp 32
  ride_physics.py --power-from-speed --speed-kmh 40 --mass 83 --cda 0.32
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from corelib import base_parser, emit, in_range, r, require  # noqa: E402

G = 9.80665
R_DRY = 287.058
R_VAPOUR = 461.495


def air_density(altitude_m: float = 0.0, temp_c: float = 15.0,
                rel_humidity: float | None = None) -> float:
    """Dry-air density, optionally corrected for humidity (Tetens saturation)."""
    p = 101325.0 * (1.0 - 2.25577e-5 * altitude_m) ** 5.25588
    t_k = temp_c + 273.15
    if rel_humidity is None:
        return p / (R_DRY * t_k)
    p_sat = 610.78 * math.exp(17.27 * temp_c / (temp_c + 237.3))
    p_v = (rel_humidity / 100.0) * p_sat
    return (p - p_v) / (R_DRY * t_k) + p_v / (R_VAPOUR * t_k)


def power_from_speed(v: float, mass: float, grade: float, cda: float,
                     crr: float, rho: float, eta: float,
                     headwind: float = 0.0, accel: float = 0.0) -> dict:
    theta = math.atan(grade)
    p_gravity = mass * G * math.sin(theta) * v
    p_rolling = mass * G * crr * math.cos(theta) * v
    p_aero = 0.5 * rho * cda * (v + headwind) ** 2 * v
    p_accel = mass * accel * v
    total = (p_gravity + p_rolling + p_aero + p_accel) / eta
    return {"total_w": total, "gravity_w": p_gravity / eta,
            "rolling_w": p_rolling / eta, "aero_w": p_aero / eta,
            "accel_w": p_accel / eta,
            "aero_fraction": (p_aero / eta) / total if total > 0 else 0.0}


def speed_from_power(power: float, mass: float, grade: float, cda: float,
                     crr: float, rho: float, eta: float,
                     headwind: float = 0.0) -> float:
    """Bisection on the monotone power-speed relation. Returns m/s."""
    lo, hi = 0.05, 35.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if power_from_speed(mid, mass, grade, cda, crr, rho, eta, headwind)["total_w"] < power:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def main() -> int:
    ap = base_parser(__doc__)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--density", action="store_true")
    mode.add_argument("--power-from-speed", action="store_true")
    mode.add_argument("--speed-from-power", action="store_true")
    ap.add_argument("--altitude", type=float, default=0.0, help="m")
    ap.add_argument("--temp", type=float, default=15.0, help="deg C")
    ap.add_argument("--humidity", type=float, help="%% RH, optional")
    ap.add_argument("--mass", type=float, help="kg, rider + bike + kit")
    ap.add_argument("--grade", type=float, default=0.0, help="fraction, e.g. 0.07")
    ap.add_argument("--cda", type=float, default=0.32, help="m2")
    ap.add_argument("--crr", type=float, default=0.004)
    ap.add_argument("--eta", type=float, default=0.976, help="drivetrain efficiency")
    ap.add_argument("--headwind", type=float, default=0.0, help="m/s, + = headwind")
    ap.add_argument("--power", type=float, help="W")
    ap.add_argument("--speed-kmh", type=float)
    ap.add_argument("--draft-saving", type=float, default=0.30,
                    help="fraction of aero drag removed in the wheels")
    args = ap.parse_args()

    notes: list[str] = []
    in_range("temp_c", args.temp, -30, 55, notes)
    in_range("altitude_m", args.altitude, -500, 6000, notes)
    rho = air_density(args.altitude, args.temp, args.humidity)

    if args.density:
        outputs = {"rho_kg_m3": r(rho, 4), "altitude_m": args.altitude,
                   "temp_c": args.temp, "humidity_pct": args.humidity,
                   "vs_isa_pct": r((rho / 1.2250 - 1) * 100, 2)}
        emit("ride_physics.py", vars(args), outputs, args.manifest, notes, args.quiet)
        return 0

    require(args.mass is not None, "--mass is required for power/speed modes")
    in_range("mass_kg", args.mass, 40, 250, notes)
    in_range("cda_m2", args.cda, 0.15, 0.60, notes)
    in_range("crr", args.crr, 0.0015, 0.015, notes)

    if args.power_from_speed:
        require(args.speed_kmh is not None, "--speed-kmh required")
        v = args.speed_kmh / 3.6
        d = power_from_speed(v, args.mass, args.grade, args.cda, args.crr,
                             rho, args.eta, args.headwind)
        outputs = {"rho_kg_m3": r(rho, 4), "speed_kmh": args.speed_kmh,
                   **{k: r(val, 1) if k.endswith("_w") else r(val, 4)
                      for k, val in d.items()}}
    else:
        require(args.power is not None, "--power required")
        in_range("power_w", args.power, 20, 2000, notes)
        v = speed_from_power(args.power, args.mass, args.grade, args.cda,
                             args.crr, rho, args.eta, args.headwind)
        d = power_from_speed(v, args.mass, args.grade, args.cda, args.crr,
                             rho, args.eta, args.headwind)
        outputs = {"rho_kg_m3": r(rho, 4), "speed_ms": r(v, 3),
                   "speed_kmh": r(v * 3.6, 2),
                   "roundtrip_power_w": r(d["total_w"], 1),
                   **{k: r(val, 1) if k.endswith("_w") else r(val, 4)
                      for k, val in d.items()}}
        if abs(d["total_w"] - args.power) > 0.5:
            notes.append(f"solver round-trip error {d['total_w'] - args.power:+.2f} W")

    saving = d["aero_w"] * args.draft_saving
    outputs["draft_saving_w"] = r(saving, 1)
    outputs["draft_saving_fraction_of_total"] = r(saving / d["total_w"], 4) if d["total_w"] else 0.0

    if d["aero_fraction"] < 0.15:
        notes.append(f"aero is only {d['aero_fraction']*100:.0f}% of total power here; "
                     "aerodynamic interventions and drafting are worth little at "
                     "this gradient and speed")
    if args.grade > 0.06:
        notes.append("gradient above 6%: gravity dominates, treat CdA changes as "
                     "second-order for this segment")

    emit("ride_physics.py", vars(args), outputs, args.manifest, notes, args.quiet)
    return 0


if __name__ == "__main__":
    sys.exit(main())
