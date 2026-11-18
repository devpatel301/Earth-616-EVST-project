"""
28_co2_quality.py -- elevated-CO2 nutrient-CONCENTRATION stress test on the national food supply
(research extension 3).

Evidence: docs/co2_nutrient_effects.csv (verified rows; docs/co2_nutrient_effects.md). Only rows marked
"primary for our stress test" for the nine study crops and the nutrients we count are used. Nothing is
transferred between species (no field pea -> chickpea/lentil/bean, no soybean -> groundnut/rapeseed), no
effect is applied to extracted oils, and no effect is applied to energy or fat unless a primary row exists.
Uncovered crop-nutrient combinations stay MISSING: in the partial scenario their supply is held unchanged
as a scenario convention (not as evidence of no response), and coverage is reported.

The experimental effect (FACE, ~546-586 ppm vs ~363-386 ppm ambient) is applied ONCE as a step change; it is
not scaled to SSP2-4.5 (no dose-response relation is supported by the sources). The result is therefore an
"elevated-CO2 experimental stress test applied to the 2021-23 food supply", not a 2050 forecast.

Scopes (kept separate):
  quantity  : domestic production loss passed to supply (upper bound f = loss x SSR*), future climate
              loss-only, HYBRID reference (1971-2000 -> 2041-60 applied to 2021-23 supply); present-relative
              variant (observed 2001-24 -> 2041-60)
  quality   : concentration change applied to ALL national supply of the crop's eligible (non-oil) items,
              domestic and imported
  combined  : remaining nutrient = remaining quantity x remaining concentration (multiplicative)
Envelopes: all covered effects at their published lower (or upper) confidence limit at once -- a sensitivity
envelope, not a joint confidence interval. Variant: significant effects only (nonsignificant ones held
unchanged by convention).
Outputs: co2_concentration_factors.csv, co2_coverage.csv, co2_nutrient_results.csv
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
import ext_common as E  # noqa: E402
from config import CROPS, ROOT_DIR  # noqa: E402

EVIDENCE = os.path.join(ROOT_DIR, "docs", "co2_nutrient_effects.csv")      # verified evidence rows (all candidates)
SELECTION = os.path.join(ROOT_DIR, "docs", "co2_effects_used.csv")        # our reviewed selection, with reasons
APPLIED_SETS = ("primary", "extended", "extended_wet", "extended_dry")


def load_factors():
    """All selected effects (long table, one row per set x crop x nutrient). The evidence row is looked up by its
    row number and must match the crop, nutrient and value recorded in the selection file."""
    ev = pd.read_csv(EVIDENCE)
    sel = pd.read_csv(SELECTION)
    rows = []
    for _, s in sel.iterrows():
        e = ev.loc[int(s.evidence_row)]
        if (e["crop"], e["nutrient"]) != (s["crop"], s["nutrient"]):
            raise ValueError(f"selection row {s.to_dict()} does not match evidence row {int(s.evidence_row)}")
        val = pd.to_numeric(e["pct_change"], errors="coerce")
        if pd.notna(s["pct_change_check"]) and not np.isclose(val, s["pct_change_check"]):
            raise ValueError(f"evidence value changed for {s.crop} {s.nutrient}: {val} vs {s.pct_change_check}")
        if s["set"] in APPLIED_SETS and (s["crop"] not in CROPS or s["nutrient"] not in E.NUTRIENTS or pd.isna(val)):
            raise ValueError(f"applied effect without a value or outside the counted crops/nutrients: {s.to_dict()}")
        lo, hi = pd.to_numeric(e["ci_low"], errors="coerce"), pd.to_numeric(e["ci_high"], errors="coerce")
        rows.append({"set": s["set"], "crop": s["crop"], "nutrient": s["nutrient"], "pct_change": val, "ci_low": lo, "ci_high": hi,
                     "ci_available": bool(pd.notna(lo) and pd.notna(hi)), "significant": e["significant"],
                     "significant_bool": str(e["significant"]).strip().lower().startswith("yes"),
                     "co2_elevated_ppm": e["co2_elevated_ppm"], "co2_ambient_ppm": e["co2_ambient_ppm"],
                     "exposure_system": e["exposure_system"], "n_info": e["n_info"], "evidence_set": e["evidence_set"],
                     "source": e["source_citation_short"], "doi": e["doi"], "locator": e["locator"], "read_level": e["read_level"],
                     "reason": s["reason"]})
    fac = pd.DataFrame(rows)
    app = fac["set"].isin(APPLIED_SETS)
    fac.loc[app, "factor_primary"] = 1.0 + fac.loc[app, "pct_change"] / 100.0
    lo = np.where(fac.ci_low.notna(), 1.0 + fac.ci_low / 100.0, fac.factor_primary)
    hi = np.where(fac.ci_high.notna(), 1.0 + fac.ci_high / 100.0, fac.factor_primary)
    fac["factor_low"], fac["factor_high"] = np.fmin(lo, hi), np.fmax(lo, hi)
    fac.loc[~app, ["factor_primary", "factor_low", "factor_high"]] = np.nan
    if fac[app].duplicated(["set", "crop", "nutrient"]).any():
        raise ValueError("duplicate effect within one set")
    return fac


def factor_sets(fac):
    """Concentration-factor dictionaries for every scenario variant."""
    p = fac[fac["set"] == "primary"]
    out = {"primary": {(r.crop, r.nutrient): r.factor_primary for _, r in p.iterrows()},
           "low": {(r.crop, r.nutrient): r.factor_low for _, r in p.iterrows()},
           "high": {(r.crop, r.nutrient): r.factor_high for _, r in p.iterrows()},
           "significant only": {(r.crop, r.nutrient): r.factor_primary for _, r in p.iterrows() if r.significant_bool}}
    for season in ("wet", "dry"):
        x = fac[fac["set"].isin(["primary", "extended", f"extended_{season}"])]
        out[f"extended, {season}-season lentil"] = {(r.crop, r.nutrient): r.factor_primary for _, r in x.iterrows()}
    return out


def coverage_matrix(fac):
    """Crop x nutrient status. Every combination is accounted for: applied (primary), applied only in the extended
    variant, evidence reviewed but not used (with the reason class), or not estimated (no evidence found)."""
    ev = pd.read_csv(EVIDENCE)
    rows = []
    for c in CROPS:
        r = {"crop": c}
        for n in E.NUTRIENTS:
            f = fac[(fac.crop == c) & (fac.nutrient == n)]
            e = ev[(ev.crop == c) & (ev.nutrient == n)]
            if (f["set"] == "primary").any():
                x = f[f["set"] == "primary"].iloc[0]
                r[n] = "primary: " + ("significant" if x.significant_bool else "nonsignificant estimate")
            elif f["set"].str.startswith("extended").any():
                r[n] = "extended variant only"
            elif len(f) and f["pct_change"].isna().all():
                r[n] = "not used: tested, no detectable change, size not reported"
            elif len(f) or len(e):
                r[n] = "not used: evidence unsuitable (pooled species, rescaled, conflicting or non-field design)"
            else:
                r[n] = "not estimated: no crop-specific evidence found"
        rows.append(r)
    return pd.DataFrame(rows)


def coverage(items_c, sua_c, fac):
    """Share of each national nutrient total whose concentration is changed in the stress test, and the share
    supplied by study-crop items that have NO evidence for that nutrient."""
    r = {}
    covered = {(c, n) for c, n in zip(fac.crop, fac.nutrient)}
    for n in E.NUTRIENTS:
        tot = items_c[n].sum()
        cov = sum(items_c.loc[items_c.Item.isin(E.eligible_items(c)), n].sum() for c in CROPS if (c, n) in covered and c not in E.SUA_CROPS)
        cov += sum(float(sua_c.loc[c, n]) for c in E.SUA_CROPS if (c, n) in covered and c in sua_c.index)
        unc = sum(items_c.loc[items_c.Item.isin(E.eligible_items(c)), n].sum() for c in CROPS if (c, n) not in covered and c not in E.SUA_CROPS)
        unc += sum(float(sua_c.loc[c, n]) for c in E.SUA_CROPS if (c, n) not in covered and c in sua_c.index)
        r[f"covered_share_{n}"] = cov / tot if tot else np.nan
        r[f"uncovered_study_crop_share_{n}"] = unc / tot if tot else np.nan
    return r


def summarise(label, m49, area, base_m, items_s, req, extra):
    m = E.diversity_metrics(items_s)
    m.update(E.adequacy_metrics(m, req))
    r = {"scenario": label, "m49": m49, "Area": area, **extra}
    for n in E.NUTRIENTS:
        b = base_m[f"total_{n}"]
        r[f"total_{n}"] = m[f"total_{n}"]
        r[f"pct_{n}"] = 100.0 * (m[f"total_{n}"] - b) / b
        r[f"nar_{n}"] = m[f"nar_{n}"]
    r["MAR"] = m["MAR"]
    r["dMAR_pts"] = 100.0 * (m["MAR"] - base_m["MAR"])
    r["composite_pct_5nutrients"] = float(np.mean([r[f"pct_{n}"] for n in E.NUTRIENTS]))
    r["composite_pct_protein_zinc_iron"] = float(np.mean([r[f"pct_{n}"] for n in ("protein", "zinc", "iron")]))
    return r


def main():
    fac_all = load_factors()
    fac_all.to_csv(E.P("co2_effects_selected.csv"), index=False)
    coverage_matrix(fac_all).to_csv(E.P("co2_coverage_matrix.csv"), index=False)
    fac = fac_all[fac_all["set"] == "primary"].reset_index(drop=True)
    fac.to_csv(E.P("co2_concentration_factors.csv"), index=False)     # primary set (used by 29, scenario D)
    adq = pd.read_csv(E.P("adequacy.csv"))
    years = E.latest_years(adq)
    panels = pd.read_csv(E.P("panels.csv"))
    countries = sorted(set(panels.m49))
    items, sua = E.baseline_items(years, countries + [E.WORLD])
    bal = E.crop_balance(years)
    req = adq[adq.Year.isin(years)].groupby("m49").mean(numeric_only=True)
    fy = E.future_yield_reference_periods()
    fy.to_csv(E.P("future_yield_reference_periods.csv"), index=False)

    conc = factor_sets(fac_all)

    cov_rows, res = [], []
    for m49 in countries + [E.WORLD]:
        bi = items[items.m49 == m49].reset_index(drop=True)
        if bi.empty or m49 not in req.index:
            continue
        area = bi.Area.iloc[0]
        sc = sua[sua.m49 == m49].set_index("crop")
        base = E.diversity_metrics(bi)
        base.update(E.adequacy_metrics(base, req.loc[m49]))
        cov_rows.append({"m49": m49, "Area": area, **coverage(bi, sc, fac)})
        res.append(summarise("baseline 2021-23", m49, area, base, bi, req.loc[m49], {"component": "baseline"}))
        # B: quality only (all supply of eligible items, incl. imports)
        for env, cf in conc.items():
            s, _ = E.apply_scenario(bi, sc, {}, cf)
            res.append(summarise(f"B CO2 concentration only ({env})", m49, area, base, s, req.loc[m49], {"component": "quality", "envelope": env}))
        if m49 == E.WORLD:
            continue
        crops_here = [c for c in panels[panels.m49 == m49].crop if (c, m49) in bal.index]
        f_c = fy[fy.m49 == m49].set_index("crop")
        for ref in ("dY_hybrid_pct", "dY_present_relative_pct"):
            q = {c: E.quantity_fraction(-f_c.loc[c, ref] / 100.0, bal.loc[(c, m49)]) for c in crops_here if f_c.loc[c, ref] < 0}
            tag = "hybrid 1971-2000 -> 2041-60" if ref == "dY_hybrid_pct" else "present-relative 2001-24 -> 2041-60"
            s, _ = E.apply_scenario(bi, sc, q, None)
            res.append(summarise(f"A future yield loss only ({tag})", m49, area, base, s, req.loc[m49],
                                 {"component": "quantity", "reference": tag, "crops_with_loss": ";".join(sorted(q))}))
            for env, cf in conc.items():
                s, _ = E.apply_scenario(bi, sc, q, cf)
                res.append(summarise(f"C combined quantity x concentration ({tag}; {env})", m49, area, base, s, req.loc[m49],
                                     {"component": "combined", "reference": tag, "envelope": env, "crops_with_loss": ";".join(sorted(q))}))
    pd.DataFrame(cov_rows).to_csv(E.P("co2_coverage.csv"), index=False)
    out = pd.DataFrame(res)
    for c in out.columns:
        if out[c].dtype == object:
            out[c] = out[c].fillna("")
    out.to_csv(E.P("co2_nutrient_results.csv"), index=False)
    pd.set_option("display.width", 250)
    print(fac[["crop", "nutrient", "pct_change", "ci_low", "ci_high", "significant"]].to_string(index=False))
    print(out[out.Area == "India"][["scenario", "pct_kcal", "pct_protein", "pct_zinc", "pct_iron", "dMAR_pts"]].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
