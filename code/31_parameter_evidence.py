"""
31_parameter_evidence.py -- evidence-screened view of the index (research extension 2).

Input: docs/evidence/parameter_evidence_register.csv (one row per crop x parameter actually used, with status, applicability
and recommended treatment; sources in docs/evidence/parameter_evidence_audit.md).

What this script does
  1. Summarises the register (status, applicability, range status) -> parameter_evidence_summary.csv.
  2. Applies two screening rules and recomputes F4 WITHOUT filling the gaps:
       rule A  a hazard component is UNAVAILABLE for a crop when the register marks a parameter that the component
               needs as 'mark unsupported' (rice and rapeseed heat slope). The pair's F4 is then unavailable: the
               other component is NOT up-weighted, and the missing heat part is NOT set to zero.
       rule B  a pair is flagged NOT APPLICABLE when its crop definition does not match the parameter source:
               FAOSTAT 'Beans, dry' in India and Myanmar includes Vigna pulses, while the bean parameters are for
               Phaseolus vulgaris (register row 'bean / FBS-production item scope').
  3. Reports three views of the nine-crop result, always labelled:
       V0  full index, as in the report -- ASSUMPTION-DEPENDENT (legacy) result: uses proxies and borrowed values
       V1  rule A applied: rice and rapeseed unavailable (7-crop partial comparison, NOT a nine-crop ranking).
           The reference maxima are recomputed over the pairs that remain; the heat, water and sensitivity maxima are
           unchanged, but the IMPORTANCE maximum is set by a removed crop (rice), so every F4 is rescaled by one
           common factor (checked); the order of the remaining crops cannot change
       V2  rules A and B applied: also bean-India and bean-Myanmar unavailable; reference maxima recomputed over the
           remaining pairs (documented change of normalisation, see E20 in the decision register)
  Partial comparisons are never presented as complete rankings: crops without an F4 are listed as unavailable.
Outputs: parameter_evidence_summary.csv, parameter_screening.csv, evidence_screened_pairs.csv,
         evidence_screened_crops.csv, evidence_screened_references.csv
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from config import CROP_ORDER, CROPS, PROC, ROOT_DIR  # noqa: E402

REGISTER = os.path.join(ROOT_DIR, "docs", "evidence", "parameter_evidence_register.csv")
P = lambda f: os.path.join(PROC, f)
F4 = "F4_hazard_paired"
NOT_APPLICABLE_PAIRS = {("bean", "India"): "FAOSTAT 'Beans, dry' includes Vigna pulses in India (FAO item definition); parameters are for Phaseolus vulgaris",
                        ("bean", "Myanmar"): "FAOSTAT 'Beans, dry' includes Vigna pulses in Myanmar (FAO item definition); parameters are for Phaseolus vulgaris"}


def f4_view(comp, heat_ok, water_ok, available):
    """F4 over `available` pairs with references (maxima) computed over those pairs only.
    heat_ok / water_ok: {crop: bool}. A pair needs BOTH components; otherwise F4 is NaN (no re-weighting)."""
    c = comp[available].copy()
    c["heat_ok"] = c.crop.map(heat_ok)
    c["water_ok"] = c.crop.map(water_ok)
    ok = c.heat_ok & c.water_ok
    base = c[ok]                      # references only over pairs for which both components exist
    ref = {"H_heat": base.H_heat.max(), "H_water": base.H_water.max(), "I": base.I.max(),
           "s_heat": base.groupby("crop").s_lit_heat.first().max(), "s_water": base.groupby("crop").s_lit_water.first().max()}
    pair = lambda col: f"{base.loc[base[col].idxmax(), 'crop']}-{base.loc[base[col].idxmax(), 'country']}"
    ref_pairs = {"heat_max_pair": pair("H_heat"), "water_max_pair": pair("H_water"), "importance_max_pair": pair("I")}
    out = comp[["crop", "country", "m49", "production_t"]].copy()
    out["available"] = False
    for col in ("E_heat", "E_water", "S_heat", "S_water", "In", F4):
        out[col] = np.nan
    idx = base.index
    out.loc[idx, "available"] = True
    out.loc[idx, "E_heat"] = base.H_heat / ref["H_heat"]
    out.loc[idx, "E_water"] = base.H_water / ref["H_water"]
    out.loc[idx, "S_heat"] = base.s_lit_heat / ref["s_heat"]
    out.loc[idx, "S_water"] = base.s_lit_water / ref["s_water"]
    out.loc[idx, "In"] = base.I / ref["I"]
    out.loc[idx, F4] = 0.5 * (out.loc[idx, "E_heat"] * out.loc[idx, "S_heat"] + out.loc[idx, "E_water"] * out.loc[idx, "S_water"]) * out.loc[idx, "In"]
    return out, {**ref, **ref_pairs}


def crop_scores(pairs):
    rows = []
    for crop in [c for c in CROP_ORDER if c in CROPS]:
        g = pairs[pairs.crop == crop]
        ok = g[g.available]
        r = {"crop": crop, "n_pairs_total": len(g), "n_pairs_available": len(ok)}
        if len(ok):
            w = ok.production_t / ok.production_t.sum()
            r["F4_eq"] = ok[F4].mean()
            r["F4_pw"] = (ok[F4] * w).sum()
        else:
            r["F4_eq"] = r["F4_pw"] = np.nan
        r["complete"] = len(ok) == len(g)
        rows.append(r)
    out = pd.DataFrame(rows)
    for w in ("eq", "pw"):
        out[f"rank_{w}"] = out[f"F4_{w}"].rank(ascending=False, method="min")
    return out


def main():
    reg = pd.read_csv(REGISTER)
    comp = pd.read_csv(P("index_components.csv"))

    # 1. register summary
    summary = []
    for col in ("status", "applicability", "recommended_treatment", "range_status", "replacement_supported"):
        for v, n in reg[col].fillna("not assessed").str.replace(r"\s*\(.*\)", "", regex=True).value_counts().items():
            summary.append({"field": col, "value": v, "n_rows": int(n)})
    pd.DataFrame(summary).to_csv(P("parameter_evidence_summary.csv"), index=False)

    # 2. screening rules (A from the register, B from the item-scope row)
    unsupported = reg[reg.recommended_treatment.astype(str).str.strip() == "mark unsupported"]
    heat_ok = {c: True for c in CROPS}
    water_ok = {c: True for c in CROPS}
    rows = []
    for _, r in unsupported.iterrows():
        if r.crop not in CROPS:
            continue
        p = str(r.parameter).lower()
        if "heat" in p or "t_crit" in p:
            heat_ok[r.crop] = False
        elif "k_y" in p or "kc" in p:
            water_ok[r.crop] = False
        rows.append({"crop": r.crop, "parameter": r.parameter, "rule": "A", "effect": "component unavailable", "evidence": r.limitations})
    for (crop, country), why in NOT_APPLICABLE_PAIRS.items():
        rows.append({"crop": crop, "parameter": f"pair {country}", "rule": "B", "effect": "pair not applicable", "evidence": why})
    pd.DataFrame(rows).to_csv(P("parameter_screening.csv"), index=False)

    allpairs = pd.Series(True, index=comp.index)
    notapp = comp.apply(lambda r: (r.crop, r.country) in NOT_APPLICABLE_PAIRS, axis=1)

    all_ok = {c: True for c in CROPS}
    v0, ref0 = f4_view(comp, all_ok, all_ok, allpairs)
    v1, ref1 = f4_view(comp, heat_ok, water_ok, allpairs)
    v2, ref2 = f4_view(comp, heat_ok, water_ok, ~notapp)
    # V0 must reproduce the published index exactly
    assert np.allclose(v0[F4].values, comp[F4].values, rtol=1e-12, atol=1e-15), "V0 does not reproduce index_components.csv"

    pairs = comp[["crop", "country", "m49"]].copy()
    for name, v in (("V0", v0), ("V1", v1), ("V2", v2)):
        pairs[f"F4_{name}"] = v[F4]
        pairs[f"available_{name}"] = v.available
    pairs["flag"] = pairs.apply(lambda r: NOT_APPLICABLE_PAIRS.get((r.crop, r.country), ""), axis=1)
    pairs.to_csv(P("evidence_screened_pairs.csv"), index=False)

    cs = []
    for name, v in (("V0", v0), ("V1", v1), ("V2", v2)):
        s = crop_scores(v)
        s.insert(0, "view", name)
        cs.append(s)
    cs = pd.concat(cs)
    cs.to_csv(P("evidence_screened_crops.csv"), index=False)

    refs = pd.DataFrame([{"view": n, **r} for n, r in (("V0", ref0), ("V1", ref1), ("V2", ref2))])
    # V1 is a pure rescaling of V0 for the pairs that remain (only the importance reference changes)
    ratio = (v1[F4] / v0[F4]).dropna()
    refs["F4_rescale_vs_V0"] = [1.0, float(ratio.iloc[0]), np.nan]
    assert np.allclose(ratio, ratio.iloc[0], rtol=1e-12), "V1 is not a common rescaling of V0"
    assert np.isclose(ratio.iloc[0], ref0["I"] / ref1["I"], rtol=1e-12)
    refs.to_csv(P("evidence_screened_references.csv"), index=False)

    pd.set_option("display.width", 250)
    print(cs[["view", "crop", "n_pairs_available", "F4_eq", "rank_eq", "F4_pw", "rank_pw"]].round(5).to_string(index=False))
    print(refs.round(4).to_string(index=False))


if __name__ == "__main__":
    main()
