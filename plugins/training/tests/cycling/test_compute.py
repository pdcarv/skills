#!/usr/bin/env python3
"""
Golden tests for the cycling-core compute layer.

Every expected value below is either an analytic result derivable by hand, a
published standard (ISA density, LeMond/Hamley coefficients, Cunningham BMR), or
a reproduction of a real prior deliverable. Nothing is asserted against the
scripts' own output.

Run: python3 plugins/training/tests/cycling/test_compute.py
"""
from __future__ import annotations

import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "skills" / "cycling"
S = ROOT / "scripts"
sys.path.insert(0, str(S))

FAILURES: list[str] = []


def run(script: str, *args: str) -> dict:
    p = subprocess.run([sys.executable, str(S / script), *args],
                       capture_output=True, text=True)
    if p.returncode != 0:
        raise AssertionError(f"{script} exited {p.returncode}: {p.stderr[-400:]}")
    return json.loads(p.stdout)


def close(name: str, got, want, tol=1e-6, note=""):
    ok = got is not None and abs(float(got) - float(want)) <= tol
    print(f"  {'PASS' if ok else 'FAIL'}  {name}: got {got}, want {want}"
          f"{'  ' + note if note else ''}")
    if not ok:
        FAILURES.append(name)


def truth(name: str, cond: bool, detail=""):
    print(f"  {'PASS' if cond else 'FAIL'}  {name}{'' if cond else '  <- ' + detail}")
    if not cond:
        FAILURES.append(name)


# --------------------------------------------------------------------------- #
print("power_duration.py — analytic 2-point CP")
# W' = (P1-P2)/(1/t1 - 1/t2) = 20/(1/720 - 1/1200) = 36000 J ; CP = 300 - 36000/720
o = run("power_duration.py", "--efforts", "720:300", "1200:280")["outputs"]
close("CP from 12+20 min", o["cp_w"], 250.0, 0.05)
close("W' from 12+20 min", o["w_prime_j"], 36000, 1)
truth("2-point fit flagged fragile",
      any("FRAGILE" in n for n in run("power_duration.py", "--efforts",
                                      "720:300", "1200:280")["notes"]))
o = run("power_duration.py", "--efforts", "300:350", "600:315", "1200:290")["outputs"]
truth("subset sensitivity reported", "subset_sensitivity" in o)
truth("fragile 3-point fit shows non-zero CP spread",
      o["subset_sensitivity"]["cp_spread_w"] > 0)
truth("durations outside 2-15 min window are excluded",
      run("power_duration.py", "--efforts", "60:600", "300:350", "600:315",
          "3600:255")["outputs"]["durations_used_s"] == [300, 600])

print("\nzones.py — reference zone table")
o = run("zones.py", "--lt1", "232", "--lt2", "280",
        "--lt1-hr", "130", "--lt2-hr", "150")["outputs"]
z = {row["zone"]: row for row in o["power_zones"]}
close("Z1 ceiling (0.75*LT1)", z["Z1_recovery"]["hi_w"], 174, 0.6)
close("Z2 ceiling = LT1", z["Z2_endurance"]["hi_w"], 232, 0.01)
close("Z4 ceiling = LT2", z["Z4_subthreshold"]["hi_w"], 280, 0.01)
close("Z5 ceiling (1.05*LT2)", z["Z5_threshold"]["hi_w"], 294, 0.2)
close("Z6 ceiling (1.20*LT2)", z["Z6_vo2max"]["hi_w"], 336, 0.3)
close("LT1/LT2 ratio", o["lt1_lt2_ratio"], 232 / 280, 0.001)
hz = {row["zone"]: row for row in o["hr_zones"]}
close("HR Z2 floor (0.88*LT1hr)", hz["Z2_endurance"]["lo_bpm"], 114.4, 0.6)
close("HR Z5 ceiling (1.03*LT2hr)", hz["Z5_threshold"]["hi_bpm"], 154.5, 0.6)
truth("high LT1/LT2 ratio triggers compressed-tempo warning",
      any("compressed" in n for n in
          run("zones.py", "--lt1", "232", "--lt2", "280")["notes"]))
truth("FTP fallback is flagged, not silent",
      any("FTP FALLBACK" in n for n in run("zones.py", "--ftp", "250")["notes"]))
truth("FTP fallback labels its anchor",
      run("zones.py", "--ftp", "250")["outputs"]["anchor"] == "ftp_fallback")

print("\nride_physics.py — ISA and round-trip")
close("ISA sea-level density", run("ride_physics.py", "--density")["outputs"]["rho_kg_m3"],
      1.2250, 0.0005, "(International Standard Atmosphere)")
# ISA at 2000 m is 2 C, not 15 C — the script uses the temperature it is given,
# so the standard-atmosphere value must be requested explicitly.
close("ISA density at 2000 m / 2 C",
      run("ride_physics.py", "--density", "--altitude", "2000",
          "--temp", "2")["outputs"]["rho_kg_m3"], 1.0065, 0.005)
close("isothermal density falls with altitude",
      run("ride_physics.py", "--density", "--altitude", "2000")["outputs"]["rho_kg_m3"],
      0.9611, 0.005)
o = run("ride_physics.py", "--speed-from-power", "--power", "240", "--mass", "83",
        "--grade", "0.07", "--cda", "0.35", "--altitude", "300", "--temp", "30")["outputs"]
close("solver round-trips to input power", o["roundtrip_power_w"], 240, 0.5)
truth("steep gradient flagged as aero-irrelevant",
      any("gravity dominates" in n for n in
          run("ride_physics.py", "--speed-from-power", "--power", "240", "--mass", "83",
              "--grade", "0.07", "--cda", "0.35")["notes"]))
flat = run("ride_physics.py", "--power-from-speed", "--speed-kmh", "40",
           "--mass", "83", "--cda", "0.32")["outputs"]
truth("aero dominates on the flat at 40 km/h", flat["aero_fraction"] > 0.7,
      str(flat["aero_fraction"]))
climb = run("ride_physics.py", "--power-from-speed", "--speed-kmh", "11.0",
            "--mass", "83", "--grade", "0.07", "--cda", "0.35")["outputs"]
truth("aero negligible on a 7% climb", climb["aero_fraction"] < 0.10,
      str(climb["aero_fraction"]))

print("\nenergy.py — Cunningham and energy availability")
o = run("energy.py", "--mass", "75", "--body-fat", "15", "--power", "200",
        "--duration-s", "14400", "--intake", "4200")["outputs"]
ffm = 75 * (1 - 0.15)
close("FFM from mass and body fat", o["ffm_kg"], ffm, 0.05)
close("Cunningham BMR (500 + 22*FFM)", o["bmr_kcal"], 500 + 22 * ffm, 0.6)
close("work kJ = P*t/1000", o["work_kj"], 200 * 14400 / 1000, 0.1)
close("kcal per kJ near unity at 23.5% GE", o["kcal_per_kj"], 1.0, 0.03)
close("energy availability", o["energy_availability_kcal_kg_ffm"],
      (4200 - o["exercise_kcal"]) / o["ffm_kg"], 0.05)
truth("clinical LEA band detected", o["ea_band"] == "clinical_LEA_risk")
cho = run("energy.py", "--cho-plan", "--duration-h", "4.5", "--mass", "75")["outputs"]["cho_plan"]
truth("CHO returned as a band capped at 90 g/h", cho["cho_g_per_h_band"] == [60, 90])
truth("CHO plan points to the contested register", "contested" in cho["contested_ref"])
truth("short ride needs no glucose-fructose mix",
      run("energy.py", "--cho-plan", "--duration-h", "1.5")["outputs"]
      ["cho_plan"]["requires_glucose_fructose"] is False)

print("\nload.py — hand-computable cases")
with tempfile.TemporaryDirectory() as td:
    pw = Path(td) / "p.txt"
    pw.write_text("\n".join(["200"] * 600))
    o = run("load.py", "--power-file", str(pw), "--anchor-lt2", "260")["outputs"]
    close("NP of a constant series equals the mean", o["normalised_power_w"], 200, 0.01)
    close("variability index = 1 for constant power", o["variability_index"], 1.0, 0.001)
    close("work kJ", o["work_kj"], 120.0, 0.05)
    close("intensity factor NP/LT2", o["intensity_factor"], 200 / 260, 0.001)
    close("TSS", o["tss"], (600 * 200 * (200 / 260)) / (260 * 3600) * 100, 0.05)
    truth("LT2 anchor recorded as such", o["anchor_kind"] == "lt2")
    o = run("load.py", "--power-file", str(pw), "--anchor-ftp", "260")["outputs"]
    truth("FTP anchor flagged as fallback", o["anchor_kind"] == "ftp_fallback")

    daily = [65, 0, 120, 80, 0, 190, 240]
    o = run("load.py", "--daily-loads", *map(str, daily))["outputs"]
    mean = sum(daily) / 7
    sd = math.sqrt(sum((d - mean) ** 2 for d in daily) / 6)
    close("weekly load", o["weekly_load"], sum(daily), 0.05)
    close("monotony = mean/SD", o["monotony"], mean / sd, 0.01)
    close("strain = weekly x monotony", o["strain"], sum(daily) * mean / sd, 0.5)
    o = run("load.py", "--rpe", "7", "--minutes", "90")["outputs"]
    close("sRPE = RPE x minutes", o["srpe_au"], 630, 0.01)

    # decoupling: power flat, HR drifts +10% in the second half -> ~9.09%
    hr = Path(td) / "hr.txt"
    hr.write_text("\n".join(["140"] * 300 + ["154"] * 300))
    o = run("load.py", "--decoupling", "--power-file", str(pw),
            "--hr-file", str(hr))["outputs"]
    close("decoupling with +10% HR drift", o["decoupling_pct"],
          (1 / 140 - 1 / 154) / (1 / 140) * 100, 0.05)
    truth("decoupling above 5% is flagged",
          any("decoupling" in n for n in
              run("load.py", "--decoupling", "--power-file", str(pw),
                  "--hr-file", str(hr))["notes"]))

print("\nload.py — compliance bands and planned-vs-perceived RPE")
for planned, done, want in [(90, 90, "green"), (90, 72, "green"), (90, 70, "yellow"),
                            (90, 130, "yellow"), (90, 40, "orange"), (90, 0, "red")]:
    o = run("load.py", "--planned", str(planned), "--completed", str(done))["outputs"]
    truth(f"compliance {done}/{planned} is {want}", o["compliance_band"] == want,
          f"{o['compliance_pct']}% -> {o['compliance_band']}")
o = run("load.py", "--rpe", "7", "--planned-rpe", "4", "--minutes", "60")
close("RPE vs planned delta", o["outputs"]["rpe_vs_planned"], 3.0)
truth("a 3-point RPE mismatch is flagged", any("differs from plan" in n for n in o["notes"]))

print("\nhrv.py — baseline gating and band status")
o = run("hrv.py", "--values", *["60"] * 10)["outputs"]
truth("short series reports baseline_incomplete", o["status"] == "baseline_incomplete")
close("days still needed (28 + 7 - 10)", o["days_needed"], 25)
steady = [str(60 + (i % 5)) for i in range(35)]
o = run("hrv.py", "--values", *steady)["outputs"]
truth("stable series sits inside its own band", o["status"] == "inside", o["status"])
dropped = [str(60 + (i % 5)) for i in range(28)] + ["45"] * 7
o = run("hrv.py", "--values", *dropped)["outputs"]
truth("a week of suppressed RMSSD falls below the band", o["status"] == "below", o["status"])
o = run("hrv.py", "--values", *steady, "--raw")["outputs"]
truth("raw mode reports untransformed values", o["transform"] == "raw" and "band_ms" not in o)

print("\ndurability.py — decay arithmetic and dose gating")
o = run("durability.py", "--fresh", "5min:350", "20min:290",
        "--fatigued", "5min:315", "20min:262", "--work-kj", "1000",
        "--mass", "75")["outputs"]
close("5-min decay = (350-315)/350", o["per_duration"]["5min"]["decay_pct"],
      (350 - 315) / 350 * 100, 0.02)
close("20-min decay = (290-262)/290", o["per_duration"]["20min"]["decay_pct"],
      (290 - 262) / 290 * 100, 0.02)
close("durability index = fatigued/fresh", o["per_duration"]["20min"]["durability_index"],
      262 / 290, 0.001)
close("kJ per kg", o["kj_per_kg"], 1000 / 75, 0.01)
truth("1000 kJ dose gets the amateur reference",
      "1000 kJ" in o["placement"]["20min"]["reference"])
close("z vs amateur cohort (mean 10.1, SD 6.5)", o["placement"]["20min"]["z_score"],
      ((290 - 262) / 290 * 100 - 10.1) / 6.5, 0.02)
truth("dose-axis warning always present", "matched kJ" in o["dose_axis_warning"])
truth("transfer caveat accompanies any placement",
      any("TRANSFER CAVEAT" in n for n in
          run("durability.py", "--fresh", "20min:290", "--fatigued", "20min:262",
              "--work-kj", "1000")["notes"]))
mid = run("durability.py", "--fresh", "20min:290", "--fatigued", "20min:262",
          "--work-kj", "1700")
truth("unmatched dose gets no percentile placement",
      "placement" not in mid["outputs"])
truth("unmatched dose says so", any("no reference distribution" in n for n in mid["notes"]))
truth("2500 kJ dose gets the elite reference",
      "2500 kJ" in run("durability.py", "--fresh", "20min:290", "--fatigued",
                       "20min:250", "--work-kj", "2500")["outputs"]
      ["placement"]["20min"]["reference"])
neg = run("durability.py", "--fresh", "20min:270", "--fatigued", "20min:290",
          "--work-kj", "1000")
truth("negative decay flagged as a paced fresh effort",
      any("submaximal or paced" in n for n in neg["notes"]))
truth("durability decoupled from threshold in the notes",
      any("independent of VO2max" in n for n in neg["notes"]))
truth("result routed to tests.yaml as MEASURED", any("tests.yaml" in n for n in neg["notes"]))

print("\nmanifest integration — every script appends a traceable run")
with tempfile.TemporaryDirectory() as td:
    mf = Path(td) / "m.json"
    run("zones.py", "--lt1", "200", "--lt2", "260", "--manifest", str(mf))
    run("energy.py", "--mass", "75", "--body-fat", "15", "--manifest", str(mf))
    run("ride_physics.py", "--density", "--manifest", str(mf))
    data = json.loads(mf.read_text())
    truth("three runs appended", len(data["runs"]) == 3, str(len(data["runs"])))
    truth("run ids are sequential and unique",
          [r["id"] for r in data["runs"]] == ["R-01", "R-02", "R-03"])
    truth("runs carry an inputs hash", all(r["inputs_hash"] for r in data["runs"]))
    truth("runs carry outputs", all(r["outputs"] for r in data["runs"]))

    # the point of the whole layer: a draft citing these numbers must now verify
    o = json.loads(mf.read_text())["runs"][0]["outputs"]
    draft = Path(td) / "d.md"
    draft.write_text(
        f"Indoor LT2 is {o['lt2_w']:.0f} W and LT1 is {o['lt1_w']:.0f} W, "
        f"giving a ratio of {o['lt1_lt2_ratio']}.\n")
    p = subprocess.run([sys.executable, str(S / "verify_output.py"),
                        "--draft", str(draft), "--manifest", str(mf),
                        "--frameworks", str(ROOT / "frameworks.yaml"),
                        "--session-date", "2026-08-28", "--json"],
                       capture_output=True, text=True)
    rep = json.loads(p.stdout)
    truth("computed numbers pass the NUMERIC gate", rep["stats"]["numbers_unsourced"] == 0,
          f"{rep['stats']['numbers_unsourced']} unsourced")

print("\n" + ("ALL COMPUTE TESTS PASSED" if not FAILURES
             else f"{len(FAILURES)} FAILED: {FAILURES}"))
sys.exit(1 if FAILURES else 0)
