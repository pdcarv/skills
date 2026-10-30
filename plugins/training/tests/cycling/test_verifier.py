#!/usr/bin/env python3
"""Golden tests for verify_output.py. Run: python3 plugins/training/tests/cycling/test_verifier.py"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "skills" / "cycling"
VERIFY = ROOT / "scripts" / "verify_output.py"
FIX = Path(__file__).resolve().parent / "fixtures"
DATE = "2026-08-28"

FAILURES: list[str] = []


def run(draft, ledger=None, manifest=None, profile=None, frameworks=True):
    cmd = [sys.executable, str(VERIFY), "--draft", str(FIX / draft),
           "--session-date", DATE, "--json"]
    if ledger:
        cmd += ["--ledger", str(FIX / ledger)]
    if manifest:
        cmd += ["--manifest", str(FIX / manifest)]
    if profile:
        cmd += ["--profile", str(FIX / profile)]
    if frameworks:
        cmd += ["--frameworks", str(ROOT / "frameworks.yaml")]
    p = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(p.stdout), p.returncode


def check(name, cond, detail=""):
    print(f"  {'PASS' if cond else 'FAIL'}  {name}{'' if cond else '  <- ' + detail}")
    if not cond:
        FAILURES.append(name)


def checks_of(report, kind, severity="ERROR"):
    return [f for f in report["findings"] if f["check"] == kind and f["severity"] == severity]


print("clean path")
rep, code = run("draft_clean.md", "ledger_clean.yaml", "manifest_clean.json", "profile_min.yaml")
check("clean draft exits 0", code == 0, f"exit={code}")
check("clean draft has no errors", rep["errors"] == 0, str(rep["errors"]))
check("numbers were actually audited", rep["stats"]["numbers_audited"] >= 10)
check("no unsourced numbers", rep["stats"]["numbers_unsourced"] == 0)

print("\ndirty path — each check must fire")
rep, code = run("draft_dirty.md", "ledger_dirty.yaml", profile="profile_min.yaml")
check("dirty draft exits 1", code == 1, f"exit={code}")
check("NUMERIC fires", len(checks_of(rep, "NUMERIC")) >= 5)
check("CITATION fires on orphan citations", any(
    "orphan" in f["message"] for f in checks_of(rep, "CITATION")))
check("CITATION fires on RECALLED carrying source", any(
    "RECALLED" in f["message"] for f in checks_of(rep, "CITATION")))
check("CONFIDENCE fires on bare level", len(checks_of(rep, "CONFIDENCE")) >= 1)
check("RECENCY fires on stale high-volatility row", len(checks_of(rep, "RECENCY")) >= 1)
check("QUOTE fires on long span", any(
    "words" in f["message"] for f in checks_of(rep, "QUOTE")))
check("QUOTE fires on duplicate anchor", any(
    "anchors from one source" in f["message"] for f in checks_of(rep, "QUOTE")))
check("UNITS fires on implausible lactate", len(checks_of(rep, "UNITS")) >= 1)
check("PROFILE fires on contradicting value", len(checks_of(rep, "PROFILE")) >= 1)

print("\nregression guards")
sys.path.insert(0, str(ROOT / "scripts"))
from verify_output import rubric_level, _norm_bool_word, strip_noise  # noqa: E402

check("YAML bool coercion recovered (yes)", _norm_bool_word(True) == "yes")
check("YAML bool coercion recovered (no)", _norm_bool_word(False) == "no")
check("meta-analysis + yes + replicated -> L5",
      rubric_level({"design": {"type": "meta-analysis"}, "transfer": {"verdict": True},
                    "replication": "replicated", "provenance": "RETRIEVED"}, False) == 5)
check("RECALLED capped at L2",
      rubric_level({"design": {"type": "meta-analysis"}, "transfer": {"verdict": True},
                    "replication": "replicated", "provenance": "RECALLED"}, False) == 2)
check("contested costs confidence",
      rubric_level({"design": {"type": "meta-analysis"}, "transfer": {"verdict": True},
                    "replication": "contested", "provenance": "RETRIEVED"}, False)
      < rubric_level({"design": {"type": "meta-analysis"}, "transfer": {"verdict": True},
                      "replication": "replicated", "provenance": "RETRIEVED"}, False))
check("stale costs confidence",
      rubric_level({"design": {"type": "RCT"}, "transfer": {"verdict": True},
                    "replication": "single", "provenance": "RETRIEVED"}, True)
      < rubric_level({"design": {"type": "RCT"}, "transfer": {"verdict": True},
                      "replication": "single", "provenance": "RETRIEVED"}, False))
_, _, allowed = strip_noise("text <!-- allow: 24 reason=structural --> more")
check("allow-comment parsed", "24" in allowed, str(allowed))

print("\nunsourced deliverable baseline (synthetic zone report)")
rep, code = run("unsourced_zones.md", profile="profile_min.yaml")
check("unsourced report fails the gate", code == 1)
check("unsourced-number count recorded", rep["stats"]["numbers_unsourced"] > 30,
      str(rep["stats"]["numbers_unsourced"]))
print(f"    baseline: {rep['stats']['numbers_unsourced']}/{rep['stats']['numbers_audited']} "
      f"numbers unsourced, {rep['errors']} errors")

print("\n" + ("ALL TESTS PASSED" if not FAILURES else f"{len(FAILURES)} FAILED: {FAILURES}"))
sys.exit(1 if FAILURES else 0)
