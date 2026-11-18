"""
32_extension_checks.py -- checks for the research extensions (28-31). Synthetic examples test the accounting
edge cases; real-output checks compare the extension tables with the established result tables.
Exits 1 on any failure. Output: data/processed/nine_crop/extension_checks.csv
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
import ext_common as E  # noqa: E402
from config import CROPS, ROOT_DIR  # noqa: E402

rows = []


def check(cid, name, ok, detail=""):
    rows.append({"id": cid, "check": name, "passed": bool(ok), "detail": str(detail)})


def toy():
    items = pd.DataFrame({
        "Item": ["Wheat and products", "Soyabeans", "Soyabean Oil", E.PARENT_PULSES, "Milk - Excluding Butter", "Apples and products"],
        "crop": ["wheat", "soybean", "soybean", None, None, None],
        "kcal": [1000.0, 50.0, 100.0, 80.0, 200.0, 0.0], "protein": [30.0, 5.0, 0.0, 5.0, 10.0, 0.0],
        "fat": [3.0, 2.0, 11.0, 0.5, 10.0, 0.0], "zinc": [6.0, 0.5, 0.0, 0.8, 1.0, 0.0], "iron": [8.0, 0.8, 0.0, 1.6, 0.1, 0.0]})
    sua = pd.DataFrame({"kcal": [40.0, 30.0], "protein": [2.5, 2.0], "fat": [0.3, 0.1], "zinc": [0.4, 0.3], "iron": [0.6, 0.9]},
                       index=pd.Index(["chickpea", "lentil"], name="crop"))
    return items, sua


def synthetic():
    items, sua = toy()
    # S1 no response reproduces baseline exactly
    s, _ = E.apply_scenario(items, sua, {}, {})
    check("S1", "synthetic: no-response scenario reproduces baseline", s[E.NUTRIENTS].equals(items[E.NUTRIENTS]))
    s, _ = E.apply_scenario(items, sua, {"wheat": 0.0, "chickpea": 0.0}, {("wheat", "zinc"): 1.0})
    check("S1b", "synthetic: zero loss and factor 1 reproduce baseline", np.allclose(s[E.NUTRIENTS], items[E.NUTRIENTS]))
    # S2 quantity loss hits all items of the crop (primary and oil), nothing else
    s, _ = E.apply_scenario(items, sua, {"soybean": 0.2}, None)
    ok = np.isclose(s.loc[1, "kcal"], 40.0) and np.isclose(s.loc[2, "kcal"], 80.0) and np.isclose(s.loc[0, "kcal"], 1000.0)
    check("S2", "synthetic: quantity fraction applied to primary and oil items of the crop only", ok)
    # S3 concentration applies to eligible (non-oil) items only
    s, _ = E.apply_scenario(items, sua, {}, {("soybean", "zinc"): 0.9, ("soybean", "fat"): 0.5})
    check("S3", "synthetic: concentration factor applied to primary product, never to oil",
          np.isclose(s.loc[1, "zinc"], 0.45) and np.isclose(s.loc[2, "fat"], 11.0) and np.isclose(s.loc[1, "fat"], 1.0))
    # S4 multiplicative quantity x quality, not additive
    s, _ = E.apply_scenario(items, sua, {"wheat": 0.1}, {("wheat", "zinc"): 0.9})
    check("S4", "synthetic: remaining = (1 - f)(1 + q), not 1 - f + q", np.isclose(s.loc[0, "zinc"], 6.0 * 0.9 * 0.9)
          and not np.isclose(s.loc[0, "zinc"], 6.0 * (1 - 0.1 - 0.1)))
    # S5 SUA crops removed from the parent, never added; joint removal sums
    s, _ = E.apply_scenario(items, sua, {"chickpea": 0.5, "lentil": 0.5}, None)
    check("S5", "synthetic: chickpea + lentil losses removed jointly from 'Pulses, Other' (no extra category)",
          np.isclose(s.loc[3, "kcal"], 80.0 - 20.0 - 15.0) and len(s) == len(items) and np.isclose(s.kcal.sum(), items.kcal.sum() - 35.0))
    # S6 simultaneous = sequential for separate crops
    a, _ = E.apply_scenario(items, sua, {"wheat": 0.1, "soybean": 0.3, "lentil": 0.2}, None)
    b1, _ = E.apply_scenario(items, sua, {"wheat": 0.1}, None)
    b2, _ = E.apply_scenario(b1, sua, {"soybean": 0.3}, None)
    b3, _ = E.apply_scenario(b2, sua, {"lentil": 0.2}, None)
    check("S6", "synthetic: simultaneous crop effects equal sequential application", np.allclose(a[E.NUTRIENTS], b3[E.NUTRIENTS]))
    # S7 joint removal larger than the parent is detected (negative supply), not clipped
    big = sua * 2.0
    s, audit = E.apply_scenario(items, big, {"chickpea": 1.0, "lentil": 1.0}, None)
    check("S7", "synthetic: removal exceeding the parent item shows up as negative supply (detected, not clipped)",
          audit["parent_min"] < 0 and (s.loc[3, E.NUTRIENTS] < 0).any())
    # S8 Shannon handles zeros: zero item adds nothing; equal shares give ln(k)
    m = E.diversity_metrics(pd.DataFrame({"Item": list("abcd"), **{n: [1.0, 1.0, 1.0, 0.0] for n in E.NUTRIENTS}}))
    check("S8", "synthetic: zero contributions ignored; equal shares give H = ln k", np.isclose(m["H_kcal"], np.log(3)) and np.isclose(m["eff_kcal"], 3.0))
    # S9 dominant-staple loss can RAISE diversity while lowering the total
    d = pd.DataFrame({"Item": ["staple", "x", "y"], "crop": ["wheat", None, None], **{n: [8.0, 1.0, 1.0] for n in E.NUTRIENTS}})
    base, after = E.diversity_metrics(d), E.diversity_metrics(E.apply_scenario(d, sua.iloc[0:0], {"wheat": 0.5}, None)[0])
    check("S9", "synthetic: losing part of a dominant staple lowers total supply but raises effective sources",
          after["total_kcal"] < base["total_kcal"] and after["eff_kcal"] > base["eff_kcal"])
    # S10 quantity fraction bounds and SSR* rule
    row = pd.Series({"ssr_star": 0.6, "prod": 60.0, "dom": 100.0, "exp": 5.0})
    check("S10", "synthetic: upper = loss x SSR*, lower <= upper, no gain from a loss",
          np.isclose(E.quantity_fraction(0.1, row), 0.06) and E.quantity_fraction(0.1, row, "lower") <= 0.06 and E.quantity_fraction(-0.2, row) == 0.0)


def real():
    P = E.P
    adq = pd.read_csv(P("adequacy.csv"))
    years = E.latest_years(adq)
    check("R1", "reference periods: food supply 2021-2023; future hybrid 1971-2000 -> 2041-2060; present-relative 2001-2024",
          years == [2021, 2022, 2023] and E.HIST == "historical_1971_2000" and "2041-2060" in E.FUT, years)
    panels = pd.read_csv(P("panels.csv"))
    items, sua = E.baseline_items(years, sorted(set(panels.m49)) + [E.WORLD])
    tot = items.groupby("m49")[E.NUTRIENTS].sum()
    a = adq[adq.Year.isin(years)].groupby("m49")[E.NUTRIENTS].mean()
    idx = tot.index.intersection(a.index)
    err = float((tot.loc[idx] / a.loc[idx] - 1).abs().max().max())
    check("R2", "baseline item sums reproduce adequacy.csv national totals (2021-23)", err < 1e-9, f"max rel. error {err:.2e}")
    check("R3", "no FBS/SUA double counting: SUA items are not Shannon categories",
          not set(E.SUA_ITEMS) & set(items.Item) and E.PARENT_PULSES in set(items.Item))
    sp = sua.groupby("m49")[E.NUTRIENTS].sum()
    par = items[items.Item == E.PARENT_PULSES].set_index("m49")[E.NUTRIENTS].reindex(sp.index)
    ratio = (sp / par).max()
    check("R4", "SUA chickpea + lentil vs parent 'Pulses, Other' (kcal, protein <= parent; Zn/Fe composition mismatch reported)",
          (ratio[["kcal", "protein"]] <= 1 + 1e-9).all(), "max ratio " + ", ".join(f"{k} {v:.3f}" for k, v in ratio.items()))
    d = pd.read_csv(P("diversity_after_losses.csv"))
    cats = pd.read_csv(P("food_categories_fbs.csv"))
    check("R5", "food-category list valid: unique items, every study-crop FBS item mapped, SUA items absent",
          cats.Item.is_unique and set(E.FBS_ITEM_CROP) >= set(cats.Item[cats.study_crop.notna()]) and not set(E.SUA_ITEMS) & set(cats.Item))
    tcols = [f"total_{n}" for n in E.NUTRIENTS]
    check("R6", "remaining supply non-negative in every scenario", (d[tcols] >= 0).all().all() and d.parent_pulses_min_after.fillna(0).ge(-1e-12).all())
    s3 = pd.read_csv(P("yield_diet_scenarios.csv"))
    s3 = s3[s3.scenario.str.startswith("S3")]
    errs = []
    for bound in ("upper", "lower"):
        m = d[d.scenario.str.startswith("A ") & (d.bound == bound)].merge(s3, left_on=["crop", "Area"], right_on=["crop", "country"])
        errs.append(max((m[f"pct_total_{n}"] - m[f"d{n}_pct_{bound}"]).abs().max() for n in E.NUTRIENTS))
        errs.append(float((100 * m.d_MAR - m[f"dMAR_pts_{bound}"]).abs().max()))
    check("R7", "scenario A reproduces the existing -10 % shock table (nutrient % and MAR, both bounds)", max(errs) < 1e-9, f"max diff {max(errs):.1e}")
    fy = pd.read_csv(P("future_yield_reference_periods.csv"))
    f16 = pd.read_csv(P("future_yield.csv"))
    mm = fy.merge(f16, on=["crop", "m49"])
    check("R8", "hybrid future yield change equals future_yield.csv; observed-series 1971-2000 loss equals the historical run",
          len(mm) == 59 and (mm.dY_hybrid_pct - mm.dY_lit_pct).abs().max() < 1e-9 and (mm.loss_1971_2000 - mm.loss_1971_2000_observed_series).abs().max() < 1e-6)
    used = pd.read_csv(P("diversity_future_pairs_used.csv"))
    pairs = set(zip(panels.crop, panels.m49))
    check("R9", "future scenarios use only modelled crop-country pairs, losses only",
          set(zip(used.crop, used.m49)) <= pairs and (used[~used.applied].qty_frac == 0).all() and (used[used.applied].dY_pct < 0).all())
    # C equals sequential single-pair application? -> totals equal the sum of single-crop removals (items separate)
    fac = pd.read_csv(P("co2_concentration_factors.csv"))
    check("R10", "CO2 factors: only study crops and counted nutrients; one primary row per crop-nutrient",
          fac.crop.isin(CROPS).all() and fac.nutrient.isin(E.NUTRIENTS).all() and not fac.duplicated(["crop", "nutrient"]).any())
    check("R11", "CO2 envelopes ordered: factor_low <= factor_primary <= factor_high",
          ((fac.factor_low <= fac.factor_primary + 1e-12) & (fac.factor_primary <= fac.factor_high + 1e-12)).all())
    sel = pd.read_csv(os.path.join(ROOT_DIR, "docs", "evidence", "co2_effects_used.csv"))
    allf = pd.read_csv(P("co2_effects_selected.csv"))
    applied = allf[allf["set"].isin(["primary", "extended", "extended_wet", "extended_dry"])]
    sel_applied = sel[sel["set"].isin(["primary", "extended", "extended_wet", "extended_dry"])]
    check("R12", "missing CO2 parameters stay missing: factors exist only for reviewed, selected rows with a published value; "
          "bean, groundnut and all kcal/fat have none",
          set(zip(applied["set"], applied.crop, applied.nutrient)) == set(zip(sel_applied["set"], sel_applied.crop, sel_applied.nutrient))
          and applied["pct_change"].notna().all() and not applied.crop.isin(["bean", "groundnut"]).any()
          and not applied.nutrient.isin(["kcal", "fat"]).any())
    res = pd.read_csv(P("co2_nutrient_results.csv"))
    b = res[res.scenario.str.startswith("B CO2 concentration only (primary)")].set_index("m49")
    covd = pd.read_csv(P("co2_coverage.csv")).set_index("m49")
    errs = []
    for n in E.NUTRIENTS:
        covered = fac[fac.nutrient == n]
        if covered.empty:
            errs.append(float(b[f"pct_{n}"].abs().max()))   # nutrient without evidence: unchanged by convention
    check("R13", "nutrients without CO2 evidence are unchanged in the quality-only scenario (convention, reported as not estimated)",
          max(errs) < 1e-9 if errs else True, f"nutrients without evidence: {[n for n in E.NUTRIENTS if fac[fac.nutrient == n].empty]}")
    # coverage share equals the treated share: quality-only % change = sum(covered share x effect) when one factor per crop
    ok = True
    for m49 in b.index:
        for n in fac.nutrient.unique():
            bi = items[items.m49 == m49]
            sc = sua[sua.m49 == m49].set_index("crop")
            exp_change = 0.0
            for _, r in fac[fac.nutrient == n].iterrows():
                if r.crop in E.SUA_CROPS:
                    v = float(sc.loc[r.crop, n]) if r.crop in sc.index else 0.0
                else:
                    v = bi.loc[bi.Item.isin(E.eligible_items(r.crop)), n].sum()
                exp_change += v * (r.factor_primary - 1.0)
            pct = 100.0 * exp_change / bi[n].sum()
            ok &= abs(pct - b.loc[m49, f"pct_{n}"]) < 1e-9
    check("R14", "quality-only change equals covered supply x published effect (coverage matches treated foods)", ok)
    comb = res[res.scenario.str.contains("C combined") & res.scenario.str.contains("hybrid") & res.scenario.str.endswith("primary)")].set_index("m49")
    qty = res[res.scenario.str.startswith("A future yield loss only (hybrid")].set_index("m49")
    qual = res[res.scenario.str.startswith("B CO2 concentration only (primary)")].set_index("m49")
    # independent re-implementation of quantity x concentration for every country and nutrient
    used = used[used.reference == "dY_hybrid_pct"]
    bal = E.crop_balance(years)
    worst, n_diff_from_additive = 0.0, 0
    for m49 in comb.index:
        bi = items[items.m49 == m49]
        sc = sua[sua.m49 == m49].set_index("crop")
        f = {r.crop: r.qty_frac for _, r in used[used.m49 == m49].iterrows()}
        for n in E.NUTRIENTS:
            qf = {r.crop: r.factor_primary for _, r in fac[fac.nutrient == n].iterrows()}
            new = 0.0
            for _, it in bi.iterrows():
                v = it[n]
                c = it.crop if isinstance(it.crop, str) else None
                if c:
                    v *= (1.0 - f.get(c, 0.0))
                    if it.Item in E.eligible_items(c):
                        v *= qf.get(c, 1.0)
                if it.Item == E.PARENT_PULSES:
                    for c2 in E.SUA_CROPS:
                        if c2 in sc.index:
                            base = float(sc.loc[c2, n])
                            v -= base - base * (1.0 - f.get(c2, 0.0)) * qf.get(c2, 1.0)
                new += v
            pct = 100.0 * (new - bi[n].sum()) / bi[n].sum()
            worst = max(worst, abs(pct - comb.loc[m49, f"pct_{n}"]))
            if abs(comb.loc[m49, f"pct_{n}"] - (qty.loc[m49, f"pct_{n}"] + qual.loc[m49, f"pct_{n}"])) > 1e-9:
                n_diff_from_additive += 1
    check("R15", "combined = remaining quantity x remaining concentration (independent item-level recomputation); differs from additive sum",
          worst < 1e-9, f"max diff {worst:.1e}; country-nutrient cases where multiplicative != additive: {n_diff_from_additive}")
    envs = res[res.scenario.str.startswith("B CO2 concentration only (")]
    lo = envs[envs.scenario.str.contains("(low)", regex=False)].set_index("m49")
    hi = envs[envs.scenario.str.contains("(high)", regex=False)].set_index("m49")
    pr = envs[envs.scenario.str.contains("(primary)", regex=False)].set_index("m49")
    ok = all(((lo[f"pct_{n}"] <= pr[f"pct_{n}"] + 1e-9) & (pr[f"pct_{n}"] <= hi[f"pct_{n}"] + 1e-9)).all() for n in E.NUTRIENTS)
    check("R16", "national envelopes ordered low <= primary <= high for every nutrient", ok)


def share_rule():
    """dH/ds_i = -(ln p_i + H)/S, so a small loss from item i raises H iff p_i > exp(-H) = 1/N_eff. Tested on the
    single-crop scenarios of crops supplied through exactly one FBS item in the country."""
    d = pd.read_csv(E.P("diversity_after_losses.csv"))
    adq = pd.read_csv(E.P("adequacy.csv"))
    items, _ = E.baseline_items(E.latest_years(adq))
    base = d[d.scenario.str.startswith("baseline")].set_index("m49")
    a = d[d.scenario.str.startswith("A ") & (d.bound == "upper")]
    ok = tot = 0
    for _, r in a.iterrows():
        if r.crop in E.SUA_CROPS:
            continue
        bi = items[items.m49 == r.m49]
        present = [i for i in CROPS[r.crop].get("fbs_items", []) if ((bi.Item == i) & (bi.kcal > 0)).any()]
        if len(present) != 1:
            continue
        for n in E.NUTRIENTS:
            v = bi[n].clip(lower=0)
            p = float(v[bi.Item == present[0]].iloc[0] / v.sum())
            if p == 0 or abs(r[f"d_eff_{n}"]) < 1e-12:
                continue
            tot += 1
            ok += (p > 1.0 / base.loc[r.m49, f"eff_{n}"]) == (r[f"d_eff_{n}"] > 0)
    check("R17", "diversity rises after a loss exactly when the item's share exceeds 1/N_eff (analytic rule, single-item crops)",
          tot > 0 and ok == tot, f"{ok} of {tot} cases")


def evidence_checks():
    import re
    P = E.P
    bib = open(os.path.join(ROOT_DIR, "docs", "refs.bib"), encoding="utf-8").read()
    keys = set(re.findall(r"^@\w+\{([^,]+),", bib, flags=re.M))
    dois = {d.lower() for d in re.findall(r"doi\s*=\s*\{([^}]+)\}", bib)}
    # parameter screening
    comp = pd.read_csv(P("index_components.csv"))
    pairs = pd.read_csv(P("evidence_screened_pairs.csv"))
    check("R18", "screening view V0 reproduces the published F4 of every pair exactly",
          np.allclose(pairs.F4_V0.values, comp.F4_hazard_paired.values, rtol=1e-12, atol=1e-15))
    unsup = {c for c in ("rice", "rapeseed")}
    nan_ok = pairs[pairs.crop.isin(unsup)][["F4_V1", "F4_V2"]].isna().all().all() and pairs[~pairs.crop.isin(unsup)].F4_V1.notna().all()
    check("R19", "unsupported components stay unavailable: rice and rapeseed have no F4 in V1/V2 (NaN, not 0, no re-weighting); other crops keep theirs",
          nan_ok, "unavailable: " + ", ".join(sorted(unsup)))
    scr = pd.read_csv(P("evidence_screened_crops.csv"))
    ranks_ok = True
    for w in ("eq", "pw"):
        r0 = scr[(scr.view == "V0")].set_index("crop")[f"F4_{w}"].drop(index=list(unsup)).rank(ascending=False)
        r1 = scr[(scr.view == "V1")].set_index("crop")[f"F4_{w}"].dropna().rank(ascending=False)
        ranks_ok &= bool((r0.sort_index() == r1.sort_index()).all())
    refs = pd.read_csv(P("evidence_screened_references.csv")).set_index("view")
    check("R20", "V1 is a common rescaling of V0 (importance reference only): order of the seven remaining crops unchanged, factor = I_ref(V0)/I_ref(V1)",
          ranks_ok and np.isclose(refs.loc["V1", "F4_rescale_vs_V0"], refs.loc["V0", "I"] / refs.loc["V1", "I"]), f"factor {refs.loc['V1', 'F4_rescale_vs_V0']:.4f}")
    reg = pd.read_csv(os.path.join(ROOT_DIR, "docs", "evidence", "parameter_evidence_register.csv"))
    miss = {c for c in CROPS} - set(reg.crop)
    check("R21", "parameter register covers all nine crops and every PARAM_RANGES perturbation is labelled as such",
          not miss and reg[reg.parameter.str.startswith("robustness")].range_status.astype(str).str.contains("exploratory|literature range|treatment range").all(),
          f"{len(reg)} rows")
    # literature coverage
    src = pd.read_csv(os.path.join(ROOT_DIR, "docs", "evidence", "future_literature_sources.csv"))
    cov = pd.read_csv(P("future_literature_coverage.csv"))
    ass = pd.read_csv(os.path.join(ROOT_DIR, "docs", "evidence", "future_literature_assessment.csv"))
    check("R22", "future literature: all nine crops accounted for (coverage assessment present), every source row has a verdict from the allowed set",
          set(cov.crop) == set(CROPS) and (cov.coverage_note.astype(str).str.len() > 20).all()
          and set(ass[~ass.id.astype(str).str.startswith("COVERAGE-")].consistency) <= {"consistent", "partly consistent", "different", "not directly comparable"})
    lit = pd.read_csv(P("future_literature_comparison.csv"))
    check("R23", "future literature rows match the computed comparison table (row count, ids)", len(lit) == len(src) and set(lit.id) == set(src.id))
    miss_doi = sorted({str(d).lower().replace("https://doi.org/", "") for d in src.doi} - dois)
    check("R24", "every DOI of the future-literature rows is in refs.bib", not miss_doi, miss_doi[:5])
    sel = pd.read_csv(P("co2_effects_selected.csv"))
    miss_doi2 = sorted({str(d).lower() for d in sel[sel["set"].isin(["primary", "extended", "extended_wet", "extended_dry"])].doi.dropna()} - dois)
    check("R25", "every DOI of the applied CO2 effects is in refs.bib", not miss_doi2, miss_doi2[:5])
    # CO2 reference levels file against the raw NOAA file
    lv = pd.read_csv(os.path.join(ROOT_DIR, "docs", "evidence", "co2_reference_levels.csv"))
    noaa = pd.read_csv(os.path.join(ROOT_DIR, "data", "raw", "noaa_gml", "co2_annmean_gl.txt"), comment="#", sep=r"\s+", names=["year", "mean", "unc"]).set_index("year")["mean"]
    ok = all(np.isclose(float(lv.loc[lv.quantity.str.contains(f"2021|2022|2023") & lv.quantity.str.contains(str(y)), "value_ppm"].iloc[0]), noaa.loc[y]) for y in (2021, 2022, 2023))
    check("R26", "CO2 reference levels: NOAA 2021-2023 values in docs/evidence/co2_reference_levels.csv equal the raw file; SSP2-4.5 2050 level (507 ppm) is below the 546 ppm lower end of the FACE experiments",
          ok and float(lv.loc[lv.quantity.str.contains("SSP2-4.5 CO2, 2050"), "value_ppm"].iloc[0]) < 546)


def main():
    synthetic()
    real()
    share_rule()
    evidence_checks()
    df = pd.DataFrame(rows)
    df.to_csv(E.P("extension_checks.csv"), index=False)
    pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 110)
    print(df.to_string(index=False))
    failed = df[~df.passed]
    print(f"{len(df) - len(failed)} of {len(df)} extension checks passed")
    if len(failed):
        sys.exit(1)


if __name__ == "__main__":
    main()
