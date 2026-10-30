#!/usr/bin/env python3
"""
load.py — training load and internal-response metrics.

Implements
----------
  normalised power   30 s rolling mean, raised to the 4th power, averaged, 4th root
  IF / TSS           anchored on LT2 by preference, FTP as flagged fallback
  sRPE               session RPE (0-10) x duration in minutes
  monotony           mean daily load / SD of daily load  (Foster)
  strain             weekly load x monotony
  ACWR               7-day acute load / 28-day chronic load
  decoupling         (P:HR first half - P:HR second half) / first half, %
  compliance         completed / planned on one metric, TrainingPeaks-style bands
  rpe vs planned     perceived minus planned session RPE

Interpretive caution
--------------------
Monotony, strain and ACWR are widely used and their validity as injury
predictors is contested in the methodological literature. They are reported here
as descriptive load statistics, not as risk predictions, and the thresholds
below are conventions rather than validated cut-points.

Usage
-----
  load.py --power-file watts.txt --anchor-lt2 260 --duration-s 3600
  load.py --daily-loads 65 0 120 80 0 190 240 --acwr-window 7,28
  load.py --decoupling --power-file w.txt --hr-file hr.txt
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from corelib import base_parser, emit, in_range, r, require  # noqa: E402


def rolling_mean(x: np.ndarray, window: int) -> np.ndarray:
    if len(x) < window:
        return np.array([x.mean()]) if len(x) else np.array([])
    c = np.cumsum(np.insert(x.astype(float), 0, 0.0))
    return (c[window:] - c[:-window]) / float(window)


def normalised_power(watts: np.ndarray, sample_hz: float = 1.0) -> float:
    window = max(1, int(round(30 * sample_hz)))
    roll = rolling_mean(watts, window)
    if roll.size == 0:
        return 0.0
    return float((np.mean(roll ** 4)) ** 0.25)


def tss(np_w: float, anchor_w: float, duration_s: float) -> tuple[float, float]:
    intensity = np_w / anchor_w
    return (duration_s * np_w * intensity) / (anchor_w * 3600.0) * 100.0, intensity


def monotony_strain(daily: list[float]) -> dict:
    a = np.asarray(daily, dtype=float)
    sd = float(a.std(ddof=1)) if a.size > 1 else 0.0
    mono = float(a.mean() / sd) if sd > 0 else None
    weekly = float(a.sum())
    return {"weekly_load": r(weekly, 1),
            "mean_daily_load": r(float(a.mean()), 1),
            "sd_daily_load": r(sd, 2),
            "monotony": r(mono, 2) if mono is not None else None,
            "strain": r(weekly * mono, 1) if mono is not None else None}


def acwr(daily: list[float], acute: int = 7, chronic: int = 28) -> dict:
    a = np.asarray(daily, dtype=float)
    require(len(a) >= chronic, f"need at least {chronic} days for a {chronic}-day chronic load")
    acute_load = float(a[-acute:].mean())
    chronic_load = float(a[-chronic:].mean())
    ratio = acute_load / chronic_load if chronic_load > 0 else None
    return {"acute_mean": r(acute_load, 1), "chronic_mean": r(chronic_load, 1),
            "acwr": r(ratio, 3) if ratio else None}


def decoupling(watts: np.ndarray, hr: np.ndarray) -> dict:
    n = min(len(watts), len(hr))
    require(n >= 120, "need at least 120 samples for a meaningful decoupling estimate")
    half = n // 2
    def ratio(w, h):
        h = h[h > 0]
        w = w[:len(h)] if len(h) < len(w) else w
        return float(np.mean(w) / np.mean(h))
    r1 = ratio(watts[:half], hr[:half])
    r2 = ratio(watts[half:n], hr[half:n])
    pw = (r1 - r2) / r1 * 100.0
    return {"first_half_p_hr": r(r1, 4), "second_half_p_hr": r(r2, 4),
            "decoupling_pct": r(pw, 2)}


def compliance(planned: float, completed: float | None) -> dict:
    """Planned vs completed on one metric, in TrainingPeaks-style bands.

    green 80-120 %, yellow 50-79 % or 121-150 %, orange beyond 50 % either way,
    red not completed. A display convention, not a validated threshold.
    """
    if not completed:
        return {"compliance_pct": 0.0, "compliance_band": "red"}
    pct = completed / planned * 100.0
    if 80 <= pct <= 120:
        b = "green"
    elif 50 <= pct < 80 or 120 < pct <= 150:
        b = "yellow"
    else:
        b = "orange"
    return {"compliance_pct": r(pct, 1), "compliance_band": b}


def read_series(path: str) -> np.ndarray:
    txt = Path(path).read_text().replace(",", "\n")
    return np.array([float(v) for v in txt.split() if v.strip()], dtype=float)


def main() -> int:
    ap = base_parser(__doc__)
    ap.add_argument("--power-file")
    ap.add_argument("--hr-file")
    ap.add_argument("--sample-hz", type=float, default=1.0)
    ap.add_argument("--anchor-lt2", type=float, help="preferred TSS anchor, W")
    ap.add_argument("--anchor-ftp", type=float, help="fallback TSS anchor, W")
    ap.add_argument("--duration-s", type=float)
    ap.add_argument("--rpe", type=float, help="session RPE 0-10")
    ap.add_argument("--minutes", type=float)
    ap.add_argument("--daily-loads", nargs="+", type=float)
    ap.add_argument("--acwr", action="store_true")
    ap.add_argument("--decoupling", action="store_true")
    ap.add_argument("--planned", type=float, help="planned value of the compliance metric")
    ap.add_argument("--completed", type=float, help="completed value of the same metric")
    ap.add_argument("--metric", default="duration_min",
                    help="which metric planned/completed refer to (duration_min, kj, tss)")
    ap.add_argument("--planned-rpe", type=float, help="RPE the session was planned at, 0-10")
    args = ap.parse_args()

    notes: list[str] = []
    outputs: dict = {}

    if args.power_file and not args.decoupling:
        watts = read_series(args.power_file)
        npw = normalised_power(watts, args.sample_hz)
        dur = args.duration_s or len(watts) / args.sample_hz
        outputs["samples"] = int(len(watts))
        outputs["duration_s"] = r(dur, 0)
        outputs["average_power_w"] = r(float(watts.mean()), 1)
        outputs["normalised_power_w"] = r(npw, 1)
        outputs["variability_index"] = r(npw / float(watts.mean()), 3) if watts.mean() else None
        outputs["work_kj"] = r(float(watts.sum()) / args.sample_hz / 1000.0, 1)
        anchor = args.anchor_lt2 or args.anchor_ftp
        if anchor:
            in_range("anchor_w", anchor, 80, 600, notes)
            t, intensity = tss(npw, anchor, dur)
            outputs["anchor_w"] = anchor
            outputs["anchor_kind"] = "lt2" if args.anchor_lt2 else "ftp_fallback"
            outputs["intensity_factor"] = r(intensity, 3)
            outputs["tss"] = r(t, 1)
            if not args.anchor_lt2:
                notes.append("TSS anchored on FTP rather than measured LT2; the "
                             "resulting IF and TSS inherit the FTP value's provenance")
        if len(watts) < 30 * args.sample_hz:
            notes.append("series shorter than the 30 s smoothing window; NP degenerates "
                         "to the mean and should not be reported as NP")

    if args.rpe is not None and args.minutes:
        in_range("rpe", args.rpe, 0, 10, notes)
        outputs["srpe_au"] = r(args.rpe * args.minutes, 1)

    if args.rpe is not None and args.planned_rpe is not None:
        delta = args.rpe - args.planned_rpe
        outputs["rpe_vs_planned"] = r(delta, 1)
        if abs(delta) >= 2:
            notes.append(f"perceived effort differs from plan by {delta:+.1f} RPE; planned and "
                         "perceived intensity often disagree, so read it with HR, power and "
                         "wellness before acting. The 2-point flag is a convention.")

    if args.planned is not None:
        require(args.planned > 0, "--planned must be positive")
        outputs["compliance_metric"] = args.metric
        outputs.update(compliance(args.planned, args.completed))
        notes.append("compliance bands follow the TrainingPeaks display convention (green "
                     "80-120 %); one metric only, not a check of interval execution")

    if args.daily_loads:
        outputs.update(monotony_strain(args.daily_loads))
        m = outputs.get("monotony")
        if m is not None and m > 2.0:
            notes.append(f"monotony {m} exceeds the conventional 2.0 flag; daily loads "
                         "are too similar. Convention, not a validated cut-point.")
        if args.acwr:
            outputs.update(acwr(args.daily_loads))
            ratio = outputs.get("acwr")
            if ratio is not None and (ratio > 1.5 or ratio < 0.8):
                notes.append(f"ACWR {ratio} sits outside the conventional 0.8-1.5 band. "
                             "ACWR's validity as an injury predictor is contested; treat "
                             "as descriptive.")

    if args.decoupling:
        require(args.power_file and args.hr_file, "--decoupling needs --power-file and --hr-file")
        outputs.update(decoupling(read_series(args.power_file), read_series(args.hr_file)))
        d = outputs["decoupling_pct"]
        if d is not None and d > 5:
            notes.append(f"decoupling {d}% exceeds the conventional 5% well-adapted "
                         "benchmark; heat, hydration and underfuelling all inflate this "
                         "and must be excluded before reading it as durability")

    require(bool(outputs), "nothing to compute; supply a power file, RPE, or daily loads")
    emit("load.py", vars(args), outputs, args.manifest, notes, args.quiet)
    return 0


if __name__ == "__main__":
    sys.exit(main())
