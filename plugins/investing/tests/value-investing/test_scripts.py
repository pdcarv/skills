#!/usr/bin/env python3
"""Tests for the value-investing compute scripts. Run: python3 plugins/investing/tests/value-investing/test_scripts.py

Standard library only. Every expected value is computed by hand in the test, so a
failure means the script, not the test, changed.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

S = Path(__file__).resolve().parents[2] / "skills" / "value-investing" / "scripts"
FAILURES: list[str] = []


def run(script: str, payload: dict | None = None, *args: str) -> tuple[dict, int, str]:
    p = subprocess.run([sys.executable, str(S / script), *args], input=json.dumps(payload) if payload else None,
                       capture_output=True, text=True)
    try:
        return json.loads(p.stdout), p.returncode, p.stderr
    except json.JSONDecodeError:
        return {}, p.returncode, p.stderr


def check(name: str, cond: bool, detail: str = "") -> None:
    print(f"  {'PASS' if cond else 'FAIL'}  {name}{'' if cond else '  <- ' + detail}")
    if not cond:
        FAILURES.append(name)


def close(name, got, want, tol):
    check(name, got is not None and abs(got - want) <= tol, f"got {got}, want {want}")


MODEL = {"price": 50, "shares": 100, "net_debt": 200, "rev0": 1000, "years": 5, "tax": 0.25,
         "wacc": 0.09, "g_inf": 0.025, "rf": 0.03, "exit_ev_ebit": 12,
         "cases": {"bear": {"growth": 0.02, "margin": 0.12, "roic": 0.12},
                   "base": {"growth": 0.05, "margin": 0.15, "roic": 0.15},
                   "bull": {"growth": 0.08, "margin": 0.17, "roic": 0.18}},
         "probabilities": {"bear": 0.25, "base": 0.55, "bull": 0.20}}

print("valuation.py — hand-computed base case")
# base: NOPAT_t = 1000*1.05^t*0.15*0.75; FCFF_t = NOPAT_t*(1-0.05/0.15); mid-year discounting
pv = sum(1000 * 1.05 ** t * 0.15 * 0.75 * (1 - 0.05 / 0.15) / 1.09 ** (t - 0.5) for t in range(1, 6))
nopat5 = 1000 * 1.05 ** 5 * 0.15 * 0.75
tv = nopat5 * 1.025 * (1 - 0.025 / 0.09) / (0.09 - 0.025)
pv_tv = tv / 1.09 ** 5
want_ps = (pv + pv_tv - 200) / 100
out, code, _ = run("valuation.py", MODEL)
base = out["outputs"]["cases"]["base"]
close("base per-share value", base["per_share"], want_ps, 0.01)
close("terminal value share of EV", base["tv_share_of_ev"], pv_tv / (pv + pv_tv), 0.001)
check("terminal share above 75% is flagged", any("terminal assumption" in n for n in out["notes"]))
w = sum(MODEL["probabilities"][k] * out["outputs"]["cases"][k]["per_share"] for k in MODEL["probabilities"])
close("probability-weighted value", out["outputs"]["weighted_per_share"], w, 0.01)
check("sensitivity grid centre equals the base case", out["outputs"]["sensitivity"][0]["per_share"][2][2] == base["per_share"])
check("two grids without CAPM inputs", len(out["outputs"]["sensitivity"]) == 2)
check("exit-multiple gap above 30% is flagged", any("exit-multiple" in n for n in out["notes"]))
check("unreachable price reports no solution", out["outputs"]["reverse_dcf"]["solved"] is False)

m2 = {**MODEL, "price": base["per_share"]}
out2, _, _ = run("valuation.py", m2)
close("reverse DCF recovers the base growth", out2["outputs"]["reverse_dcf"]["implied_growth"], 0.05, 0.001)

_, code, err = run("valuation.py", {**MODEL, "g_inf": 0.095})
check("terminal growth at or above WACC is rejected", code == 2 and "below WACC" in err, err)
_, code, err = run("valuation.py", {**MODEL, "probabilities": {"bear": 0.5, "base": 0.6}})
check("probabilities not summing to 1 are rejected", code == 2, err)
capm = {**MODEL, "capm": {"rf": 0.03, "beta": 1.1, "erp": 0.055, "kd_after_tax": 0.035, "wd": 0.2}}
del capm["wacc"]
out3, _, _ = run("valuation.py", capm)
close("CAPM WACC = 0.8*(0.03+1.1*0.055)+0.2*0.035", out3["outputs"]["cases"]["base"]["wacc"],
      0.8 * (0.03 + 1.1 * 0.055) + 0.2 * 0.035, 0.0001)
check("beta x rf grid present with CAPM inputs", any(g["x"] == "beta" for g in out3["outputs"]["sensitivity"]))

print("\nscreens.py — hand-computed ratios")
CO = {"altman_model": "original", "ev": 1400,
      "current": {"net_income": 90, "total_assets": 1000, "cfo": 120, "long_term_debt": 200, "current_assets": 400,
                  "current_liabilities": 200, "shares": 100, "gross_profit": 400, "revenue": 1050,
                  "retained_earnings": 300, "ebit": 160, "total_liabilities": 500, "market_cap": 1200,
                  "net_fixed_assets": 500, "interest_expense": 20, "book_equity": 500},
      "prior": {"net_income": 80, "total_assets": 950, "cfo": 100, "long_term_debt": 220, "current_assets": 360,
                "current_liabilities": 200, "shares": 100, "gross_profit": 370, "revenue": 1000},
      "history": [{"fcf": 70, "net_income": 80}, {"fcf": 85, "net_income": 90}]}
out, _, _ = run("screens.py", CO)
o = out["outputs"]
close("Altman Z original = 1.2*.2+1.4*.3+3.3*.16+.6*2.4+1.05", o["altman"]["z"], 0.24 + 0.42 + 0.528 + 1.44 + 1.05, 0.01)
check("Altman zone safe above 2.99", o["altman"]["zone"] == "safe")
check("Piotroski 8 of 9 (asset turnover fell 1.053 -> 1.05)", o["piotroski"]["score"] == 8, str(o["piotroski"]))
close("earnings yield = 160/1400", o["greenblatt"]["earnings_yield"], 160 / 1400, 0.0001)
close("return on capital = 160/(200+500)", o["greenblatt"]["return_on_capital"], 160 / 700, 0.0001)
close("ROCE = 160/(1000-200)", o["quality"]["roce"], 0.2, 0.0001)
close("cash conversion = 155/170", o["quality"]["cash_conversion"], 155 / 170, 0.001)
out, _, _ = run("screens.py", {"current": {"ebit": 10}, "sector": "financial"})
check("missing fields skip a screen with a note", out["outputs"]["piotroski"].get("skipped") is True)
check("financial sector warning", any("financial company" in n for n in out["notes"]))
low = {**CO, "history": [{"fcf": 40, "net_income": 80}, {"fcf": 50, "net_income": 90}]}
out, _, _ = run("screens.py", low)
check("cash conversion below 80% is flagged", any("below 80%" in n for n in out["notes"]))

print("\nsizing.py — Kelly arithmetic and caps")
# binary even-money bet, p=0.6: f* = (bp - q)/b = 0.2
out, _, _ = run("sizing.py", {"scenarios": [{"p": 0.6, "return": 1.0}, {"p": 0.4, "return": -1.0}],
                              "fraction": 1.0, "tier": "core"})
close("growth-optimal f for even-money p=0.6 is 0.2", out["outputs"]["kelly_full"], 0.2, 0.002)
TREE = {"scenarios": [{"name": "bear", "p": 0.25, "return": -0.40}, {"name": "base", "p": 0.55, "return": 0.20},
                      {"name": "bull", "p": 0.20, "return": 0.80}],
        "fraction": 0.5, "tier": "standard", "tolerable_drawdown": 0.03}
out, _, _ = run("sizing.py", TREE)
o = out["outputs"]
close("survivability cap = 0.03/0.40", o["candidates"]["survivability_cap"], 0.075, 0.0001)
check("smallest constraint is adopted and named", o["binding_constraint"] == "survivability_cap" and o["adopted_size"] == 0.075)
check("Kelly at the no-leverage cap is flagged", any("no-leverage cap" in n for n in out["notes"]))
out, _, _ = run("sizing.py", {"scenarios": [{"p": 0.5, "return": -0.5}, {"p": 0.5, "return": 0.4}], "tier": "standard"})
check("negative expected log growth sizes to zero", out["outputs"]["kelly_full"] == 0.0)
_, code, _ = run("sizing.py", {"scenarios": [{"p": 0.5, "return": 0.1}], "tier": "standard"})
check("probabilities not summing to 1 are rejected", code == 2)

print("\ntrace_check.py — attachment of numbers")
with tempfile.TemporaryDirectory() as td:
    mf = Path(td) / "m.json"
    run("valuation.py", MODEL, "--manifest", str(mf))
    vo = json.loads(mf.read_text())["runs"][0]["outputs"]
    good = Path(td) / "good.md"
    good.write_text(f"Base value {vo['cases']['base']['per_share']} per share; weighted {vo['weighted_per_share']}. "
                    f"Terminal value is {vo['cases']['base']['tv_share_of_ev'] * 100:.1f}% of EV. Price is 48.2.\n"
                    "<!-- allow: 3 reason=three scenarios -->We use 3 scenarios as of 2026-10-29.\n")
    src = Path(td) / "src.json"
    src.write_text(json.dumps([{"label": "price", "value": 48.2, "source": "https://example.org/quote", "as_of": "2026-10-29"}]))
    p = subprocess.run([sys.executable, str(S / "trace_check.py"), "--draft", str(good), "--manifest", str(mf),
                        "--sources", str(src)], capture_output=True, text=True)
    check("traced draft passes (manifest, dated source, allow, percent, date ignored)", p.returncode == 0, p.stdout)
    bad = Path(td) / "bad.md"
    bad.write_text("Fair value is 73.5 per share.\n")
    p = subprocess.run([sys.executable, str(S / "trace_check.py"), "--draft", str(bad), "--manifest", str(mf)],
                       capture_output=True, text=True)
    check("untraced number fails", p.returncode == 1 and "73.5" in p.stdout, p.stdout)
    src.write_text(json.dumps([{"label": "price", "value": 48.2, "source": "https://example.org/quote"}]))
    p = subprocess.run([sys.executable, str(S / "trace_check.py"), "--draft", str(good), "--manifest", str(mf),
                        "--sources", str(src)], capture_output=True, text=True)
    check("source without as_of date fails", p.returncode == 1 and "as_of" in p.stdout, p.stdout)

print("\n" + ("ALL TESTS PASSED" if not FAILURES else f"{len(FAILURES)} FAILED: {FAILURES}"))
sys.exit(1 if FAILURES else 0)
