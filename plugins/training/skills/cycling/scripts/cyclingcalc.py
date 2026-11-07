#!/usr/bin/env python3
"""cyclingcalc — the whole deterministic layer in one file.

Consolidates zones, power-duration, ride physics, load, energy, durability and
the numeric trace gate in one importable file. The individual scripts carry the
richer CLIs and the reasoning in their docstrings.

Every function returns a dict including `notes`. The notes are not decoration:
they carry the caveat that makes the number honest. Never report a value and
drop its note.

CLI:  python3 cyclingcalc.py <command> [k=v ...]
      zones lt1=200 lt2=260 mass=75
      cp efforts=300:350,600:315,1200:290 mass=75
      physics power=240 mass=83 grade=0.07 cda=0.35 alt=300 temp=30
      energy mass=75 bf=15 power=200 dur_s=14400 intake=4200
      durability fresh=20min:290 fatigued=20min:262 work_kj=1000 mass=75
      selftest
"""
import json, math, sys, itertools

R_DRY, G = 287.058, 9.80665


def _r(x, n=2):
    return None if x is None else round(float(x), n)


# ---------------------------------------------------------------- zones
def zones(lt1=None, lt2=None, ftp=None, mass=None, lt1_hr=None, lt2_hr=None):
    notes, anchor = [], "measured_thresholds"
    if not (lt1 and lt2):
        if not ftp:
            raise ValueError("need lt1+lt2, or ftp for flagged fallback")
        anchor, lt2, lt1 = "ftp_fallback", ftp, ftp * 0.72
        notes.append("FTP FALLBACK: LT1 imputed at 0.72*FTP. Across trained cyclists "
                     "LT1/FTP spans ~0.60-0.78, so the endurance ceiling carries ~18 "
                     "percentage points of uncertainty. Estimates, not prescriptions.")
    if lt2 <= lt1:
        raise ValueError(f"LT2 ({lt2}) must exceed LT1 ({lt1})")
    mid = lt1 + 0.5 * (lt2 - lt1)
    bands = [("Z1_recovery", None, 0.75 * lt1), ("Z2_endurance", 0.75 * lt1, lt1),
             ("Z3_tempo", lt1, mid), ("Z4_subthreshold", mid, lt2),
             ("Z5_threshold", lt2, 1.05 * lt2), ("Z6_vo2max", 1.05 * lt2, 1.20 * lt2),
             ("Z7_anaerobic", 1.20 * lt2, None)]
    pz = [{"zone": n, "lo_w": _r(lo, 0), "hi_w": _r(hi, 0),
           "lo_w_kg": _r(lo / mass, 2) if (mass and lo) else None,
           "hi_w_kg": _r(hi / mass, 2) if (mass and hi) else None} for n, lo, hi in bands]
    ratio = lt1 / lt2
    if ratio > 0.82:
        notes.append(f"LT1/LT2 {ratio:.3f} is high (typical 0.72-0.80): the tempo band is "
                     "compressed and the grey zone is easy to enter by accident. Headroom "
                     "is likelier at LT1 than LT2.")
    elif ratio < 0.68:
        notes.append(f"LT1/LT2 {ratio:.3f} is low: a wide aerobic band suggests threshold "
                     "work has more headroom than volume.")
    tg = {"torque_T1": (.82, .88), "subthreshold_low": (.90, .94),
          "subthreshold_high": (.95, .98), "over_under_over": (1.05, 1.07),
          "over_under_under": (.88, .88), "vo2_30_15": (1.10, 1.18),
          "vo2_long": (1.08, 1.12), "tempo": (.99, 1.03)}
    out = {"anchor": anchor, "lt1_w": _r(lt1, 0), "lt2_w": _r(lt2, 0),
           "lt1_lt2_ratio": _r(ratio, 3), "tempo_band_w": _r(0.5 * (lt2 - lt1), 0),
           "power_zones": pz,
           "session_targets_w": {k: [_r(lt2 * a, 0), _r(lt2 * b, 0)] for k, (a, b) in tg.items()},
           "notes": notes}
    if mass:
        out["lt2_w_kg"] = _r(lt2 / mass, 2)
    if lt1_hr and lt2_hr:
        hmid = lt1_hr + 0.5 * (lt2_hr - lt1_hr)
        pts = [None, 0.88 * lt1_hr, lt1_hr, hmid, lt2_hr, 1.03 * lt2_hr, None, None]
        out["hr_zones"] = [{"zone": bands[i][0],
                            "lo_bpm": int(pts[i]) if pts[i] else None,
                            "hi_bpm": int(pts[i + 1]) if pts[i + 1] else None}
                           for i in range(7)]
    return out


# ------------------------------------------------------- power-duration
def cp_wprime(efforts, mass=None):
    """efforts: [(seconds, watts)]. Canonical fitting window 2-15 min."""
    notes = []
    keep = [(t, p) for t, p in sorted(efforts) if 120 <= t <= 1200]
    dropped = [int(t) for t, _ in sorted(efforts) if not 120 <= t <= 1200]
    if dropped:
        notes.append(f"excluded durations outside the 2-20 min window: {dropped}")
    if len(keep) < 2:
        raise ValueError("need >=2 efforts inside the fitting window")
    for t, _ in keep:
        if t > 900:
            notes.append(f"{int(t)}s is beyond the canonical 15-min ceiling; retained but "
                         "biases CP low")

    def fit(pairs):
        n = len(pairs)
        sx = sum(t for t, _ in pairs); sy = sum(p * t for t, p in pairs)
        sxx = sum(t * t for t, _ in pairs); sxy = sum(t * p * t for t, p in pairs)
        d = n * sxx - sx * sx
        cp = (n * sxy - sx * sy) / d
        wp = (sy - cp * sx) / n
        return cp, wp

    cp, wp = fit(keep)
    if len(keep) == 2:
        notes.append("FRAGILE: 2-point fit. CP is determined exactly by these two efforts "
                     "and carries no residual information. Estimate, not a measurement.")
    if wp > 30000:
        notes.append(f"W' {wp:.0f} J is high vs the 15-25 kJ trained range: anaerobically "
                     "rich relative to CP.")
    out = {"cp_w": _r(cp, 1), "w_prime_j": _r(wp, 0), "n_efforts": len(keep),
           "durations_s": [int(t) for t, _ in keep],
           "predicted_w": {f"p{t}s": _r(cp + wp / t, 1) for t in (300, 600, 1200, 3600)},
           "notes": notes}
    if len(keep) >= 3:
        cps = [fit(c)[0] for k in range(2, len(keep) + 1)
               for c in itertools.combinations(keep, k)]
        spread = max(cps) - min(cps)
        out["subset_cp_spread_w"] = _r(spread, 1)
        out["subset_cp_min_w"], out["subset_cp_max_w"] = _r(min(cps), 1), _r(max(cps), 1)
        if spread > 15:
            notes.append(f"CP varies by {spread:.1f} W across duration subsets: the fit is "
                         "not robust. Add efforts or re-test before using it as an anchor.")
    if mass:
        out["cp_w_kg"] = _r(cp / mass, 2)
    return out


# -------------------------------------------------------- ride physics
def air_density(alt=0.0, temp=15.0):
    p = 101325.0 * (1.0 - 2.25577e-5 * alt) ** 5.25588
    return p / (R_DRY * (temp + 273.15))


def power_from_speed(v, mass, grade=0.0, cda=0.32, crr=0.004, rho=1.225,
                     eta=0.976, headwind=0.0):
    th = math.atan(grade)
    pg = mass * G * math.sin(th) * v
    pr = mass * G * crr * math.cos(th) * v
    pa = 0.5 * rho * cda * (v + headwind) ** 2 * v
    tot = (pg + pr + pa) / eta
    return {"total_w": tot, "gravity_w": pg / eta, "rolling_w": pr / eta,
            "aero_w": pa / eta, "aero_fraction": (pa / eta) / tot if tot > 0 else 0.0}


def speed_from_power(power, mass, grade=0.0, cda=0.32, crr=0.004, rho=1.225,
                     eta=0.976, headwind=0.0):
    lo, hi = 0.05, 35.0
    for _ in range(200):
        m = 0.5 * (lo + hi)
        if power_from_speed(m, mass, grade, cda, crr, rho, eta, headwind)["total_w"] < power:
            lo = m
        else:
            hi = m
    return 0.5 * (lo + hi)


def physics(power=None, speed_kmh=None, mass=None, grade=0.0, cda=0.32,
            crr=0.004, alt=0.0, temp=15.0, draft=0.30):
    notes = []
    rho = air_density(alt, temp)
    if speed_kmh:
        v = speed_kmh / 3.6
    else:
        v = speed_from_power(power, mass, grade, cda, crr, rho)
    d = power_from_speed(v, mass, grade, cda, crr, rho)
    if d["aero_fraction"] < 0.15:
        notes.append(f"aero is only {d['aero_fraction']*100:.0f}% of total power here; "
                     "drafting and aero equipment are worth little at this gradient/speed.")
    if grade > 0.06:
        notes.append("gradient above 6%: gravity dominates, CdA changes are second-order.")
    return {"rho": _r(rho, 4), "speed_kmh": _r(v * 3.6, 2),
            **{k: _r(x, 1) if k.endswith("_w") else _r(x, 4) for k, x in d.items()},
            "draft_saving_w": _r(d["aero_w"] * draft, 1), "notes": notes}


# ---------------------------------------------------------------- load
def normalised_power(watts, hz=1.0):
    w = int(round(30 * hz))
    if len(watts) < w:
        return sum(watts) / len(watts)
    c = [0.0]
    for x in watts:
        c.append(c[-1] + x)
    roll = [(c[i + w] - c[i]) / w for i in range(len(watts) - w + 1)]
    return (sum(r ** 4 for r in roll) / len(roll)) ** 0.25


def load(watts=None, hz=1.0, anchor=None, anchor_is_lt2=True, hr=None,
         daily=None, rpe=None, minutes=None):
    out, notes = {}, []
    if watts:
        npw = normalised_power(watts, hz); dur = len(watts) / hz
        out.update({"avg_w": _r(sum(watts) / len(watts), 1), "np_w": _r(npw, 1),
                    "work_kj": _r(sum(watts) / hz / 1000, 1), "duration_s": _r(dur, 0)})
        if anchor:
            i = npw / anchor
            out.update({"intensity_factor": _r(i, 3),
                        "tss": _r(dur * npw * i / (anchor * 3600) * 100, 1),
                        "anchor_kind": "lt2" if anchor_is_lt2 else "ftp_fallback"})
            if not anchor_is_lt2:
                notes.append("TSS anchored on FTP rather than measured LT2; IF and TSS "
                             "inherit the FTP value's provenance.")
    if hr and watts:
        n = min(len(watts), len(hr)); h = n // 2
        r1 = (sum(watts[:h]) / h) / (sum(hr[:h]) / h)
        r2 = (sum(watts[h:n]) / (n - h)) / (sum(hr[h:n]) / (n - h))
        dec = (r1 - r2) / r1 * 100
        out["decoupling_pct"] = _r(dec, 2)
        if dec > 5:
            notes.append(f"decoupling {dec:.1f}% exceeds the conventional 5% benchmark; "
                         "heat, hydration and underfuelling all inflate this and must be "
                         "excluded before reading it as durability.")
    if daily:
        m = sum(daily) / len(daily)
        sd = (sum((x - m) ** 2 for x in daily) / (len(daily) - 1)) ** 0.5 if len(daily) > 1 else 0
        mono = m / sd if sd else None
        out.update({"weekly_load": _r(sum(daily), 1), "monotony": _r(mono, 2),
                    "strain": _r(sum(daily) * mono, 1) if mono else None})
        if len(daily) >= 28:
            a = sum(daily[-7:]) / 7; c = sum(daily[-28:]) / 28
            out["acwr"] = _r(a / c, 3) if c else None
        notes.append("monotony, strain and ACWR are descriptive load statistics. Their "
                     "validity as injury predictors is contested; the thresholds are "
                     "conventions, not validated cut-points.")
    if rpe is not None and minutes:
        out["srpe_au"] = _r(rpe * minutes, 1)
    out["notes"] = notes
    return out


# -------------------------------------------------------------- energy
def energy(mass=None, bf=None, ffm=None, power=None, dur_s=None, work_kj=None,
           ge=0.235, intake=None, cho_hours=None):
    notes, out = [], {}
    if work_kj is None and power and dur_s:
        work_kj = power * dur_s / 1000.0
    if work_kj is not None:
        kcal = work_kj / (4.184 * ge)
        out.update({"work_kj": _r(work_kj, 1), "exercise_kcal": _r(kcal, 0),
                    "kcal_per_kj": _r(kcal / work_kj, 3)})
    if ffm is None and mass and bf is not None:
        ffm = mass * (1 - bf / 100.0)
    if ffm:
        out.update({"ffm_kg": _r(ffm, 1), "bmr_kcal": _r(500 + 22 * ffm, 0)})
        if intake is not None and "exercise_kcal" in out:
            ea = (intake - out["exercise_kcal"]) / ffm
            out["ea_kcal_kg_ffm"] = _r(ea, 1)
            out["ea_band"] = ("clinical_LEA_risk" if ea < 30 else
                              "reduced" if ea < 45 else "optimal")
            if ea < 30:
                notes.append(f"EA {ea:.1f} kcal/kg FFM is below the 30 clinical threshold. "
                             "This is a health flag, not a training variable, and it "
                             "outranks any performance objective.")
            elif ea < 45:
                notes.append(f"EA {ea:.1f} sits in the 30-45 reduced band: sustainable "
                             "briefly, not across a build block.")
    if cho_hours:
        h = cho_hours
        band = ((0, 30) if h < 1 else (30, 60) if h < 2 else (60, 90))
        out["cho"] = {"g_per_h_band": list(band),
                      "g_total_band": [_r(band[0] * h, 0), _r(band[1] * h, 0)],
                      "needs_glucose_fructose": h >= 2, "contested_ref": "frameworks.md contested register: carbohydrate above 90 g/h"}
        notes.append("CHO is a BAND, not a point, capped at the 90 g/h default ceiling. Above "
                     "90 g/h is contested for performance; the energy-balance argument on long "
                     "days is separate and needs gut training first.")
    out["notes"] = notes
    return out


# ---------------------------------------------------------- durability
def durability(fresh, fatigued, work_kj, mass=None):
    """fresh/fatigued: {label: watts}. Decay is only comparable at matched kJ."""
    notes, per = [], {}
    REF1000 = {"5min": (10.8, 7.8), "20min": (10.1, 6.5)}
    REF2500 = {"5min": 10.39, "20min": 12.54}
    for k in [x for x in fresh if x in fatigued]:
        f, g = fresh[k], fatigued[k]
        dec = (f - g) / f * 100
        per[k] = {"fresh_w": _r(f, 1), "fatigued_w": _r(g, 1), "decay_pct": _r(dec, 2),
                  "durability_index": _r(g / f, 4)}
        if dec < 0:
            notes.append(f"{k}: fatigued power EXCEEDS fresh by {-dec:.1f}%. The fresh "
                         "effort was submaximal or paced; not interpretable as durability.")
    out = {"work_kj": _r(work_kj, 0), "per_duration": per,
           "dose_axis_warning": "decay is only comparable at matched kJ"}
    if mass:
        out["kj_per_kg"] = _r(work_kj / mass, 2)
    if abs(work_kj - 1000) <= 150:
        out["placement"] = {k: {"reference": "~1000 kJ, well-trained amateur n=20",
                                "cohort_mean_pct": REF1000[k][0],
                                "z": _r((per[k]["decay_pct"] - REF1000[k][0]) / REF1000[k][1], 2)}
                            for k in per if k in REF1000}
    elif abs(work_kj - 2500) <= 250:
        out["placement"] = {k: {"reference": "~2500 kJ, junior international ~65 kg",
                                "p75_decay_pct": REF2500[k],
                                "at_or_above_p75": per[k]["decay_pct"] <= REF2500[k]}
                            for k in per if k in REF2500}
    else:
        notes.append(f"no reference distribution at {work_kj:.0f} kJ; decay reported "
                     "without percentile placement. References are ~1000 and ~2500 kJ.")
    if "placement" in out:
        notes.append("TRANSFER CAVEAT: reference cohorts are lighter and, at 2500 kJ, "
                     "younger than a typical amateur. Orientation, not a grade.")
    notes.append("Durability appears INDEPENDENT of VO2max and relative FTP in well-trained "
                 "amateurs. Do not infer it from threshold data, or threshold from it.")
    out["notes"] = notes
    return out


# ------------------------------------------------- numeric trace gate
def trace_gate(draft_text, allowed_values):
    """Every number in the draft must appear in allowed_values (computed outputs
    or profile). Returns the unsourced ones. This is the minimum viable form of
    the full verifier: no citation, recency or confidence checks."""
    import re
    def flat(o, acc=None):
        acc = set() if acc is None else acc
        if isinstance(o, dict):
            [flat(v, acc) for v in o.values()]
        elif isinstance(o, (list, tuple)):
            [flat(v, acc) for v in o]
        elif isinstance(o, bool):
            pass
        elif isinstance(o, (int, float)):
            acc.add(f"{float(o):.6g}")
        return acc
    uni = flat(allowed_values)
    for v in list(uni):
        for s in (0.001, 1000, 0.01, 100):
            uni.add(f"{float(v)*s:.6g}")
    txt = re.sub(r"```.*?```|<!--.*?-->", " ", draft_text, flags=re.S)
    bad = []
    for m in re.finditer(r"(?<![\w/.-])-?\d+(?:\.\d+)?(?![\w.-])", txt):
        val = f"{float(m.group(0)):.6g}"
        f = float(val)
        if f.is_integer() and 1900 <= f <= 2100:
            continue
        if val in uni:
            continue
        if any(abs(f - float(u)) / max(abs(float(u)), 1e-9) <= 0.005 for u in uni):
            continue
        bad.append(m.group(0))
    return {"unsourced": sorted(set(bad)), "count": len(set(bad))}


# ------------------------------------------------------------- selftest
def selftest():
    f, checks = [], 0
    def chk(name, got, want, tol=0.05):
        nonlocal checks
        checks += 1
        if got is None or abs(float(got) - float(want)) > tol:
            f.append(f"{name}: got {got}, want {want}")
    r = cp_wprime([(720, 300), (1200, 280)])
    chk("CP 2-point", r["cp_w"], 250.0); chk("W' 2-point", r["w_prime_j"], 36000, 1)
    z = zones(lt1=232, lt2=280, lt1_hr=130, lt2_hr=150)
    chk("Z1 ceiling", z["power_zones"][0]["hi_w"], 174, 0.6)
    chk("Z6 ceiling", z["power_zones"][5]["hi_w"], 336, 0.5)
    chk("HR Z5 top", z["hr_zones"][4]["hi_bpm"], 154.5, 0.6)
    chk("ISA density", air_density(0, 15), 1.2250, 0.0005)
    e = energy(mass=75, bf=15, power=200, dur_s=14400, intake=3600)
    chk("FFM", e["ffm_kg"], 63.75, 0.05); chk("BMR", e["bmr_kcal"], 1902.5, 0.6)
    chk("EA band", 0 if e["ea_band"] == "clinical_LEA_risk" else 1, 0)
    d = durability({"20min": 290}, {"20min": 262}, 1000, 75)
    chk("decay", d["per_duration"]["20min"]["decay_pct"], 9.655, 0.01)
    l = load(watts=[200] * 600, anchor=260)
    chk("NP const", l["np_w"], 200, 0.01); chk("TSS", l["tss"], 9.862, 0.05)
    p = physics(power=240, mass=83, grade=0.07, cda=0.35, alt=300, temp=30)
    chk("physics roundtrip", p["total_w"], 240, 0.5)
    t = trace_gate("value is 42 and 250.5", {"a": 250.5})
    chk("gate catches 42", len(t["unsourced"]), 1)
    print(f"SELFTEST {'PASS' if not f else 'FAIL'} ({checks} checks)" + "".join(f"\n  {x}" for x in f))
    return 1 if f else 0


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] == "selftest":
        sys.exit(selftest())
    cmd = sys.argv[1]
    kw = {}
    for a in sys.argv[2:]:
        k, v = a.split("=", 1)
        if k == "efforts":
            kw[k] = [tuple(float(x) for x in e.split(":")) for e in v.split(",")]
        elif k in ("fresh", "fatigued"):
            kw[k] = {e.split(":")[0]: float(e.split(":")[1]) for e in v.split(",")}
        elif k == "daily":
            kw[k] = [float(x) for x in v.split(",")]
        else:
            try:
                kw[k] = float(v)
            except ValueError:
                kw[k] = v
    fn = {"zones": zones, "cp": cp_wprime, "physics": physics, "load": load,
          "energy": energy, "durability": durability}[cmd]
    if cmd == "cp":
        print(json.dumps(fn(kw.pop("efforts"), **kw), indent=2))
    elif cmd == "durability":
        print(json.dumps(fn(kw.pop("fresh"), kw.pop("fatigued"), kw.pop("work_kj"),
                            kw.get("mass")), indent=2))
    else:
        print(json.dumps(fn(**kw), indent=2))
