#!/usr/bin/env python3
"""search_sim — deterministic arithmetic for comparing plan candidates.

`cyclingcalc.py` answers "what is true of this athlete now". This answers
"which candidate plan survives". Nothing here models adaptation: there is no
individually fitted impulse-response model in this file and there will not be
one until the athlete has the longitudinal data to fit it. Fitting Banister
time constants from nothing is fabrication wearing a formula, and it produces
exactly the confident-looking numbers `references/method.md` exists to stop.

What is here instead: arithmetic that is either exact (ramp, Pareto), or
explicitly swept across a declared parameter range and reported as a band
(wbal, decay), or a stated-assumption simulation whose assumptions are printed
with the result (robust).

Every function returns a dict including `notes`. Never report a value and drop
its note. Every function that consumes an ASSUMED parameter returns a `sweep`
and a `decisive` flag; when `decisive` is false the number may not be used to
rank candidates and the comparison degrades to ordinal.

CLI:  python3 search_sim.py <command> [k=v ...]
      simgate params=cp:DERIVED:2,wprime:DERIVED:2,decay:ASSUMED:1
      rank weeks=30 items=durability:0.8:0.6:10:1.4,lt2:0.5:0.7:8:1.2
      pareto sense=max,max,max items=A:0.8:0.6:0.4,B:0.7:0.7:0.5
      ramp hours=12,13,14,10,15,16,17,12 window=4
      robust key_per_week=4 weeks=12 p_miss=0.15 cascade=0.35 threshold=0.8
      wbal cp=250 wprime=36000 work=340:180 rec=180:180 reps=6 sweep=0.25
      decay fresh=290 work_kj=2200 pct_per_1000kj=5 lo=3 hi=8
      selftest
"""
import json
import math
import random
import sys

# ----------------------------------------------------------------- helpers


def _r(x, n=3):
    return None if x is None else round(float(x), n)


def _items(spec):
    """name:v1:v2:... , name:v1:v2:...  ->  [(name, [floats])]"""
    out = []
    for chunk in spec.split(","):
        parts = chunk.split(":")
        out.append((parts[0], [float(p) for p in parts[1:]]))
    return out


# ----------------------------------------------------------------- simgate
PROV_RANK = {"MEASURED": 4, "DERIVED": 3, "STATED": 2, "ASSUMED": 1, "RECALLED": 0}


def simgate(params=None):
    """Decide whether a quantitative model may run at all.

    params: name:PROVENANCE:confidence,...  (confidence 1-5, per method.md)

    Rule (SIM-GATE). A model may emit numbers iff every parameter is MEASURED,
    or is ASSUMED/DERIVED from a declared published range AND a sensitivity
    sweep across that full range is run and reported as a band. Any RECALLED
    parameter bars the model outright. Otherwise the comparison is ordinal.
    """
    rows, notes = [], []
    if not params:
        raise ValueError("need params=name:PROVENANCE:confidence,...")
    verdict = "QUANTITATIVE"
    for chunk in params.split(","):
        name, prov, conf = (chunk.split(":") + ["3"])[:3]
        prov = prov.upper()
        if prov not in PROV_RANK:
            raise ValueError(f"unknown provenance {prov}")
        conf = int(conf)
        req = None
        if prov == "RECALLED":
            verdict = "BARRED"
            req = "RECALLED parameter: model may not run, at any confidence"
        elif prov == "MEASURED" and conf >= 4:
            req = "point estimate admissible"
        else:
            req = "sweep mandatory; report a band, never a point"
            if verdict != "BARRED":
                verdict = "QUANTITATIVE_WITH_SWEEP"
        rows.append({"param": name, "provenance": prov, "confidence": conf,
                     "requirement": req})
    if verdict == "BARRED":
        notes.append("BARRED: at least one parameter is RECALLED. Degrade to ordinal "
                     "ranking. Do not emit a number, a percentage or a confidence "
                     "figure derived from this model.")
    if verdict == "QUANTITATIVE_WITH_SWEEP":
        notes.append("Sweep is not optional. If the sign of the candidate ordering "
                     "flips anywhere inside the swept range, the model is "
                     "NON-DECISIVE and the comparison degrades to ordinal.")
    return {"verdict": verdict, "params": rows, "notes": notes}


# ----------------------------------------------------------------- rank
def rank(items=None, weeks=None):
    """Weakness ranking.

    items: name:gap:trainability:time_to_adapt_weeks:interference_cost,...
      gap             0-1, distance from the event's demand profile
      trainability    0-1, expected responsiveness of this quality
      time_to_adapt   weeks to a detectable change
      interference    >=1.0 multiplier, cost imposed on other qualities

    Two scores are reported deliberately.

      agreed   = gap * trainability * (1 / weeks_to_adapt) * (1 / interference)
      horizon  = gap * trainability * min(1, weeks_avail / weeks_to_adapt)
                                    * (1 / interference)

    `agreed` is the function as specified. It penalises slow adaptations
    continuously, which is wrong whenever the horizon is long enough to pay
    for them: with 30 weeks available a 12-week adaptation is not 1.5x worse
    than an 8-week one, it is simply affordable. `horizon` saturates instead.
    Where the two disagree on the top rank, that disagreement is the finding
    and must be surfaced, not averaged away.
    """
    if not items:
        raise ValueError("need items=name:gap:train:weeks_to_adapt:interference,...")
    rows, notes = [], []
    for name, v in _items(items):
        if len(v) != 4:
            raise ValueError(f"{name}: need 4 values gap:train:weeks:interference")
        gap, tr, tta, inter = v
        if tta <= 0 or inter <= 0:
            raise ValueError(f"{name}: time_to_adapt and interference must be > 0")
        agreed = gap * tr * (1.0 / tta) * (1.0 / inter)
        if weeks:
            horizon = gap * tr * min(1.0, float(weeks) / tta) * (1.0 / inter)
        else:
            horizon = None
        rows.append({"weakness": name, "gap": gap, "trainability": tr,
                     "weeks_to_adapt": tta, "interference": inter,
                     "score_agreed": _r(agreed, 4),
                     "score_horizon": _r(horizon, 4),
                     "feasible_in_horizon": None if not weeks else tta <= float(weeks)})
    by_agreed = sorted(rows, key=lambda r: -r["score_agreed"])
    out = {"ranked_agreed": [r["weakness"] for r in by_agreed], "rows": rows}
    if weeks:
        by_h = sorted(rows, key=lambda r: -(r["score_horizon"] or 0))
        out["ranked_horizon"] = [r["weakness"] for r in by_h]
        out["weeks_available"] = float(weeks)
        if by_h[0]["weakness"] != by_agreed[0]["weakness"]:
            notes.append(
                f"RANK DISAGREEMENT: agreed function selects '{by_agreed[0]['weakness']}', "
                f"horizon-corrected selects '{by_h[0]['weakness']}'. The agreed function "
                "discounts slow adaptations that the remaining {} weeks can actually "
                "pay for. Put both to the athlete; do not pick silently.".format(weeks))
        infeasible = [r["weakness"] for r in rows if not r["feasible_in_horizon"]]
        if infeasible:
            notes.append("Cannot adapt inside the horizon: " + ", ".join(infeasible) +
                         ". These belong to the next macrocycle, not this one.")
    notes.append("Inputs are ordinal judgements dressed as decimals. This ranks; it "
                 "does not measure. Two weaknesses within 15% of each other are tied.")
    out["notes"] = notes
    return out


# ----------------------------------------------------------------- pareto
def pareto(items=None, sense=None):
    """Non-dominated sort over candidate plans.

    items: name:o1:o2:o3,...   sense: max,max,min  (default all max)
    Returns the front, the dominated set with what dominated each, and whether
    the front is degenerate (one candidate dominating all) — in which case
    Pareto was the wrong frame and a single objective would have sufficed.
    """
    if not items:
        raise ValueError("need items=name:o1:o2:...")
    rows = _items(items)
    k = len(rows[0][1])
    for n, v in rows:
        if len(v) != k:
            raise ValueError(f"{n}: expected {k} objectives, got {len(v)}")
    s = (sense.split(",") if sense else ["max"] * k)
    if len(s) != k:
        raise ValueError("sense length must match objective count")
    sign = [1.0 if x.strip() == "max" else -1.0 for x in s]

    def dominates(a, b):
        va = [sign[i] * a[i] for i in range(k)]
        vb = [sign[i] * b[i] for i in range(k)]
        return all(x >= y for x, y in zip(va, vb)) and any(x > y for x, y in zip(va, vb))

    front, dominated, notes = [], [], []
    for name, v in rows:
        doms = [n2 for n2, v2 in rows if n2 != name and dominates(v2, v)]
        if doms:
            dominated.append({"candidate": name, "dominated_by": doms})
        else:
            front.append(name)
    if len(front) == 1:
        notes.append(f"DEGENERATE FRONT: '{front[0]}' dominates on every objective. "
                     "Pareto added nothing here — the decision was single-objective "
                     "all along. Say so rather than presenting a trade-off that "
                     "does not exist.")
    if len(front) == len(rows):
        notes.append("NO CANDIDATE DOMINATED: every plan is on the front. Either the "
                     "objectives are too weakly discriminating, or the candidates are "
                     "not actually different. Check the diversity constraint before "
                     "spending retrieval budget on this generation.")
    notes.append("Front membership is not a ranking. Choosing inside the front "
                 "requires the athlete's exchange rate, which is a preference, "
                 "not a finding.")
    return {"front": front, "dominated": dominated, "sense": s, "notes": notes}


# ----------------------------------------------------------------- ramp
def ramp(hours=None, window=4, step_cap=0.10):
    """Week-over-week load ramp feasibility on a declared weekly series.

    Exact arithmetic on stated hours. Reports week-over-week deltas, the
    acute:chronic ratio, and whether any recovery week exists in each window.
    ACWR is reported because it is asked for, and flagged because its
    predictive validity is contested — see frameworks.yaml, monitoring_validity.
    """
    if not hours:
        raise ValueError("need hours=12,13,14,...")
    h = [float(x) for x in hours.split(",")]
    if len(h) < 2:
        raise ValueError("need at least 2 weeks")
    w = int(window)
    rows, notes, flags = [], [], []
    for i, v in enumerate(h):
        prev = h[i - 1] if i else None
        dpct = None if prev in (None, 0) else (v - prev) / prev
        chronic = sum(h[max(0, i - w + 1):i + 1]) / len(h[max(0, i - w + 1):i + 1])
        acwr = v / chronic if chronic else None
        row = {"week": i + 1, "hours": v,
               "delta_pct": _r(None if dpct is None else dpct * 100, 1),
               "chronic_mean": _r(chronic, 2), "acwr": _r(acwr, 2)}
        if dpct is not None and dpct > step_cap:
            row["flag"] = f"step +{dpct*100:.1f}% exceeds the {step_cap*100:.0f}% cap"
            flags.append(i + 1)
        rows.append(row)
    for start in range(0, len(h) - w + 1):
        blk = h[start:start + w]
        if min(blk) >= 0.85 * max(blk):
            notes.append(f"weeks {start+1}-{start+w}: no week below 85% of the block "
                         "peak — this window has no recovery week in it.")
    notes.append("ACWR is reported for continuity with common practice. Its "
                 "predictive validity is methodologically contested (spurious "
                 "correlation from shared terms); it is weak evidence for "
                 "restricting training and equally weak for permitting it.")
    notes.append(f"The {step_cap*100:.0f}% step cap is a convention, not a measured "
                 "threshold for this athlete. It is a prompt to justify, not a law.")
    return {"weeks": rows, "stepped_weeks": flags, "window": w, "notes": notes}


# ----------------------------------------------------------------- robust
def robust(key_per_week=4, weeks=12, p_miss=0.15, cascade=0.35,
           threshold=0.8, trials=20000, seed=17):
    """Monte Carlo over missed key sessions.

    Model, stated in full because it is an assumption and not a finding:
      - each key session is missed independently with probability p_miss
      - a missed session raises the miss probability of the NEXT key session
        by `cascade` (rescheduling debt), decaying back after one hit
      - everything else about the plan is assumed executed

    Answers: what fraction of key sessions survives, and P(completion >=
    threshold). It ranks candidate plans by fragility. It does not predict
    adaptation and no output here may be converted into a performance claim.
    """
    kpw, wk = int(key_per_week), int(weeks)
    pm, cs, th = float(p_miss), float(cascade), float(threshold)
    n = kpw * wk
    if n <= 0:
        raise ValueError("key_per_week and weeks must be positive")
    rng = random.Random(int(seed))
    done, hits = [], 0
    for _ in range(int(trials)):
        p, c = pm, 0
        for _s in range(n):
            if rng.random() < min(0.95, p):
                c += 1
                p = min(0.95, pm + cs)
            else:
                p = pm
        frac = (n - c) / n
        done.append(frac)
        if frac >= th:
            hits += 1
    done.sort()

    def q(x):
        return done[min(len(done) - 1, int(x * len(done)))]

    return {"key_sessions_total": n, "p_miss": pm, "cascade": cs,
            "completion_p10": _r(q(0.10)), "completion_p50": _r(q(0.50)),
            "completion_p90": _r(q(0.90)),
            "p_completion_ge_threshold": _r(hits / float(trials)),
            "threshold": th, "trials": int(trials), "seed": int(seed),
            "notes": [
                "p_miss and cascade are STATED assumptions, not measured adherence. "
                "Sweep both across the plausible range before ranking candidates on "
                "this output; if the ordering flips, the model is non-decisive.",
                "A plan with fewer key sessions scores better here by construction. "
                "That is the point — fragility, not quality — and it must be read "
                "against the adaptation objective, never alone.",
                "Deterministic seed: same inputs give the same answer, so two "
                "candidates are comparable only when run at identical seed."]}


# ----------------------------------------------------------------- wbal
def wbal(cp=None, wprime=None, work=None, rec=None, reps=6, sweep=0.25, dt=1.0):
    """W'bal over an interval set, swept across a W' uncertainty band.

    work / rec: "power:seconds". Integrates the differential form: W' depletes
    at (P - CP) above CP and reconstitutes toward W' below it on a tau set by
    the deficit and the recovery power (Skiba-type). Session is deemed
    completable while W'bal stays positive throughout.

    CP and W' here are DERIVED (2-parameter fit, efforts three months apart).
    The sweep is therefore mandatory, and the reported answer is the band.
    """
    if not (cp and wprime and work and rec):
        raise ValueError("need cp=, wprime=, work=P:s, rec=P:s")
    cp, w0 = float(cp), float(wprime)
    pw, tw = [float(x) for x in work.split(":")]
    pr, tr = [float(x) for x in rec.split(":")]
    reps, sw = int(reps), float(sweep)

    def run(w_cap):
        w = w_cap
        lowest = w_cap
        for _ in range(reps):
            for _t in range(int(tw / dt)):
                w -= (pw - cp) * dt
                lowest = min(lowest, w)
                if w <= 0:
                    return lowest, False
            for _t in range(int(tr / dt)):
                if pr < cp:
                    dcp = cp - pr
                    tau = 546.0 * math.exp(-0.01 * dcp) + 316.0
                    w += (w_cap - w) * (1 - math.exp(-dt / tau))
                else:
                    w -= (pr - cp) * dt
                w = min(w, w_cap)
                lowest = min(lowest, w)
                if w <= 0:
                    return lowest, False
        return lowest, True

    lo_cap, hi_cap = w0 * (1 - sw), w0 * (1 + sw)
    res = {}
    for label, cap in (("low", lo_cap), ("point", w0), ("high", hi_cap)):
        low, ok = run(cap)
        res[label] = {"wprime_j": _r(cap, 0), "min_wbal_j": _r(low, 0),
                      "completable": ok}
    decisive = res["low"]["completable"] == res["high"]["completable"]
    notes = ["W' is DERIVED from efforts three months apart, violating the "
             "same-fitness-state assumption of the fit. The band, not the point "
             "value, is the answer.",
             "Reconstitution tau is a population model. It is not fitted to this "
             "athlete and no individual tau exists in state/."]
    if not decisive:
        notes.append("NON-DECISIVE: completability flips inside the swept W' range. "
                     "This session's feasibility cannot rank candidates. Degrade to "
                     "ordinal, or measure W' before using it.")
    return {"cp_w": cp, "reps": reps, "work": f"{pw:.0f} W x {tw:.0f} s",
            "recovery": f"{pr:.0f} W x {tr:.0f} s", "sweep_pct": sw * 100,
            "sweep": res, "decisive": decisive, "notes": notes}


# ----------------------------------------------------------------- decay
def decay(fresh=None, work_kj=None, pct_per_1000kj=5.0, lo=3.0, hi=8.0):
    """Durability projection on the declared placeholder decay rate.

    For use when the athlete has NO measured durability baseline. The 5%/1000 kJ
    figure is an ASSUMED placeholder authorised for candidate comparison only. It unblocks
    candidate comparison; it does not unblock prescription, and no output here
    may be written into a plan as a target.
    """
    if not (fresh and work_kj):
        raise ValueError("need fresh=<W> work_kj=<kJ>")
    f, kj = float(fresh), float(work_kj)
    out = {}
    for label, r in (("low", float(lo)), ("point", float(pct_per_1000kj)),
                     ("high", float(hi))):
        d = (r / 100.0) * (kj / 1000.0)
        out[label] = {"pct_per_1000kj": r, "total_decay_pct": _r(d * 100, 1),
                      "projected_w": _r(f * (1 - d), 0)}
    spread = out["low"]["projected_w"] - out["high"]["projected_w"]
    return {"fresh_w": f, "work_kj": kj, "sweep": out,
            "band_width_w": _r(spread, 0),
            "notes": [
                "PLACEHOLDER, source ASSUMED, confidence 1. Authorised for candidate "
                "comparison only. Without a measured durability baseline, no "
                "durability target may be prescribed.",
                f"The swept band spans {spread:.0f} W. Any candidate ordering that "
                "depends on a difference smaller than that band is noise.",
                "Linear decay in kJ is a modelling convenience. Real decay curves "
                "are not constrained to be linear and may have a knee.",
                "A durability test (tests.yaml) replaces this entire function with a "
                "measurement."]}


# ----------------------------------------------------------------- selftest
def selftest():
    checks, fails = 0, []

    def ck(cond, label):
        nonlocal checks
        checks += 1
        if not cond:
            fails.append(label)

    g = simgate(params="cp:DERIVED:2,mass:MEASURED:4")
    ck(g["verdict"] == "QUANTITATIVE_WITH_SWEEP", "simgate sweep verdict")
    ck(simgate(params="x:RECALLED:2")["verdict"] == "BARRED", "simgate bars RECALLED")
    ck(simgate(params="m:MEASURED:5")["verdict"] == "QUANTITATIVE", "simgate measured")

    r = rank(items="dur:0.8:0.6:12:1.4,lt2:0.5:0.7:8:1.2", weeks=30)
    ck(r["ranked_agreed"][0] == "lt2", "rank agreed picks fast adaptation")
    ck(r["ranked_horizon"][0] == "dur", "rank horizon picks the bigger gap")
    ck(any("DISAGREEMENT" in n for n in r["notes"]), "rank surfaces disagreement")
    ck(rank(items="a:0.5:0.5:60:1", weeks=30)["rows"][0]["feasible_in_horizon"]
       is False, "rank horizon feasibility")

    p = pareto(items="A:0.9:0.9:0.9,B:0.5:0.5:0.5,C:0.95:0.1:0.5")
    ck("A" in p["front"] and "B" not in p["front"], "pareto dominance")
    ck("C" in p["front"], "pareto keeps trade-off candidate")
    ck(any("DEGENERATE" in n for n in
           pareto(items="A:1:1,B:0:0")["notes"]), "pareto degenerate note")
    ck(any("NO CANDIDATE DOMINATED" in n for n in
           pareto(items="A:1:0,B:0:1")["notes"]), "pareto no-dominance note")
    ck(pareto(items="A:1:0,B:0:1", sense="max,min")["front"] == ["A"],
       "pareto honours sense")

    rp = ramp(hours="10,11,12,9,13,14,15,11")
    ck(rp["weeks"][1]["delta_pct"] == 10.0, "ramp delta arithmetic")
    ck(4 in rp["stepped_weeks"] or 5 in rp["stepped_weeks"], "ramp flags big step")
    ck(any("ACWR" in n for n in rp["notes"]), "ramp carries ACWR caveat")

    rb = robust(key_per_week=4, weeks=10, p_miss=0.15, cascade=0.35, trials=3000)
    ck(0.0 <= rb["completion_p50"] <= 1.0, "robust p50 in range")
    ck(rb["completion_p10"] <= rb["completion_p90"], "robust quantile order")
    ck(robust(p_miss=0.5, weeks=10, trials=2000)["completion_p50"]
       < rb["completion_p50"], "robust monotone in p_miss")

    w = wbal(cp=250, wprime=36000, work="340:180", rec="180:180", reps=6)
    ck("sweep" in w and w["sweep"]["point"]["min_wbal_j"] is not None, "wbal runs")
    ck(wbal(cp=250, wprime=36000, work="600:180", rec="180:180",
            reps=6)["sweep"]["high"]["completable"] is False, "wbal fails hard set")
    ck(w["decisive"] in (True, False), "wbal reports decisiveness")

    d = decay(fresh=290, work_kj=2200)
    ck(d["sweep"]["low"]["projected_w"] > d["sweep"]["high"]["projected_w"],
       "decay band ordering")
    ck(d["band_width_w"] > 0, "decay band non-zero")
    ck(any("durability baseline" in n for n in d["notes"]), "decay carries the block")

    print(f"SELFTEST {'PASS' if not fails else 'FAIL'} ({checks} checks)")
    for f in fails:
        print("  FAILED:", f)
    return 0 if not fails else 1


CMDS = {"simgate": simgate, "rank": rank, "pareto": pareto, "ramp": ramp,
        "robust": robust, "wbal": wbal, "decay": decay}


def main(argv):
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        print(__doc__)
        return 0
    cmd = argv[1]
    if cmd == "selftest":
        return selftest()
    if cmd not in CMDS:
        print(f"unknown command {cmd}; one of {', '.join(sorted(CMDS))}, selftest")
        return 2
    kw = {}
    for a in argv[2:]:
        if "=" not in a:
            print(f"bad arg {a}; expected k=v")
            return 2
        k, v = a.split("=", 1)
        kw[k] = v
    print(json.dumps(CMDS[cmd](**kw), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
