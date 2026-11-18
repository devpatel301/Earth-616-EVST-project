"""
24_checks.py -- consistency checks on the saved nine-crop results (commitments C1-C10, section "checks" of the
results register). Recomputes quantities from the raw component columns and compares them with what the pipeline
saved, so an arithmetic slip, a stale file or a double count shows up as a FAIL.
Writes data/processed/nine_crop/consistency_checks.csv and exits non-zero if any check fails.
"""
import os
import sys

import numpy as np
import pandas as pd

from config import CROP_GROUPS, CROPS, PROC

rows = []


def check(name, ok, detail=""):
    rows.append({"check": name, "passed": bool(ok), "detail": detail})
    print(("PASS " if ok else "FAIL ") + name + (f"  [{detail}]" if detail else ""))


def rd(name):
    return pd.read_csv(os.path.join(PROC, name))


def close(a, b, tol=1e-9):
    return float(np.nanmax(np.abs(np.asarray(a, float) - np.asarray(b, float))))


def main():
    comp, ref = rd("index_components.csv"), rd("index_reference.csv").set_index("quantity").max_value
    panels = rd("panels.csv")

    # ---- C1/C2: inputs and component arithmetic -------------------------------------------------
    check("nine crops in panels", set(panels.crop) == set(CROPS) and len(CROPS) == 9, f"{panels.crop.nunique()} crops, {len(panels)} pairs")
    reg = pd.read_csv(os.path.join(PROC, "..", "..", "..", "docs", "input_register.csv")).astype(str)
    missing = [c for c in CROPS if not reg.apply(lambda col: col.str.contains(c, case=False)).any(axis=None)]
    check("every crop appears in docs/input_register.csv", not missing, str(missing))
    for h in ("heat", "water"):
        check(f"E_{h} = observed level / fixed maximum", close(comp[f"E_{h}"], comp[f"H_{h}_used"] / comp[f"H_{h}_used"].max()) < 1e-12,
              f"max {ref[f'H_{h}']:.4f}")
    check("index_reference maxima equal component maxima", close([ref["H_heat"], ref["H_water"], ref["I"]], [comp.H_heat.max(), comp.H_water.max(), comp.I.max()]) < 1e-12)
    slope = comp.crop.map(lambda c: CROPS[c]["heat_slope"]).astype(float)
    ky = comp.crop.map(lambda c: CROPS[c]["ky"]).astype(float)
    check("S_heat is literature slope / max slope (literature-only)", close(comp.S_heat, slope / slope.max()) < 1e-12 and close(comp.S_heat, comp.S_lit_heat_n) < 1e-12)
    check("S_water is FAO K_y / max K_y (literature-only)", close(comp.S_water, ky / ky.max()) < 1e-12 and close(comp.S_water, comp.S_lit_water_n) < 1e-12)
    check("I = mean of five nutrient shares", close(comp.I, comp[["sh_kcal", "sh_protein", "sh_fat", "sh_zinc", "sh_iron"]].mean(axis=1)) < 1e-12)
    check("In = I / max I", close(comp.In, comp.I / comp.I.max()) < 1e-12)
    f4 = 0.5 * (comp.E_heat * comp.S_heat + comp.E_water * comp.S_water) * comp.In
    check("F4 recomputed from components", close(f4, comp.F4_hazard_paired) < 1e-12)

    # ---- C4/C6: crop and group aggregation ------------------------------------------------------
    crop = rd("index_crop.csv").set_index("crop")
    eq = comp.groupby("crop").F4_hazard_paired.mean()
    pw = comp.groupby("crop").apply(lambda g: (g.F4_hazard_paired * g.production_t / g.production_t.sum()).sum(), include_groups=False)
    check("crop score, equal weights = mean over countries", close(crop.F4_hazard_paired_eq, eq.reindex(crop.index)) < 1e-12)
    check("crop score, production weights", close(crop.F4_hazard_paired_pw, pw.reindex(crop.index)) < 1e-12)
    grp = rd("index_group.csv").set_index("group")
    ok = all(abs(grp.loc[g, "F4_hazard_paired_eq"] - crop.loc[[c for c in m if c in crop.index], "F4_hazard_paired_eq"].mean()) < 1e-12 for g, m in CROP_GROUPS.items())
    check("group score = simple mean of its three crop scores", ok and set(grp.index) == set(CROP_GROUPS))

    # ---- C5: future processing ------------------------------------------------------------------
    fut = rd("future_components.csv")
    m = fut.merge(comp[["crop", "m49", "F4_hazard_paired", "E_heat", "E_water"]], on=["crop", "m49"])
    check("future run's 'present' column reproduces the main F4", close(m.F4_hazard_paired_present_2001_2024, m.F4_hazard_paired) < 1e-12)
    for lbl in ("historical_1971_2000", "future_2041_2060"):
        check(f"{lbl}: E uses the FIXED present-period maximum", close(fut[f"E_heat_{lbl}"], fut[f"H_heat_{lbl}"] / ref["H_heat"]) < 1e-12
              and close(fut[f"E_water_{lbl}"], fut[f"H_water_{lbl}"] / ref["H_water"]) < 1e-12)
    check("S and In identical across periods", close(fut.S_heat_historical_1971_2000, fut.S_heat_future_2041_2060) == 0 and close(fut.In_historical_1971_2000, fut.In_future_2041_2060) == 0)
    check("dF4 = heat part + water part", close(fut.dF4_abs, fut.dF4_from_heat + fut.dF4_from_water) < 1e-12)
    hc = rd("future_check_hist_vs_main.csv")
    check("1971-2000 comparator reproduces main series (relative < 1e-3)", (hc.max_abs_diff / hc.max_value).max() < 1e-3, f"max rel {(hc.max_abs_diff / hc.max_value).max():.2e}")
    fy = rd("future_yield.csv")
    check("yield change comes from loss accounting, not from index values", "dY_lit_pct" in fy and not np.allclose(fy.dY_lit_pct.values, fut.dF4_abs.values[:len(fy)], equal_nan=True))

    # ---- C8: nutrition accounting -----------------------------------------------------------------
    cc, adq = rd("crop_contrib.csv"), rd("adequacy.csv")
    t = cc.drop_duplicates(["m49", "Year"]).merge(adq[["m49", "Year", "kcal", "iron"]], on=["m49", "Year"], suffixes=("_cc", "_adq"))
    check("crop_contrib national totals equal the adequacy (FBS) totals", close(t.kcal_tot, t.kcal_adq) < 1e-6 and close(t.iron_tot, t.iron_adq) < 1e-9, f"{len(t)} country-years")
    s = cc.groupby(["m49", "Year"])[["sh_kcal", "sh_protein", "sh_fat", "sh_zinc", "sh_iron"]].sum()
    check("nine crops never exceed 100% of any national nutrient supply", (s.max().max() <= 1.0), f"max {s.max().max():.3f}")
    sup = pd.read_pickle(os.path.join(PROC, "nutrient_supply.pkl"))
    sua = sup[sup.method == "sua"]
    par = sup[(sup.method == "new") & (sup.Item == "Pulses, Other and products")]
    j = sua.groupby(["m49", "Year"])[["kcal", "protein", "iron"]].sum().join(par.groupby(["m49", "Year"])[["kcal", "protein", "iron"]].sum(), rsuffix="_parent", how="inner")
    over = (j.kcal > 1.05 * j.kcal_parent + 1e-9).mean()
    check("SUA chickpea+lentil kcal do not exceed the FBS 'Pulses, Other' aggregate (5% tolerance)", over < 0.05, f"{100 * over:.1f}% of {len(j)} country-years exceed (SUA and FBS can differ)")
    check("SUA rows are labelled and kept out of national totals", set(sua.crop.dropna()) == {"chickpea", "lentil"} and "sua" not in set(sup[sup.Item.isin(par.Item)].method))
    div = rd("food_supply_diversity.csv").set_index("Area")
    ind = cc[(cc.m49 == 356) & cc.Year.between(2021, 2023)].groupby("Year")[["sh_kcal", "sh_protein", "sh_iron"]].sum().mean()
    check("India nine-crop share (diversity table) = summed crop contributions", all(abs(div.loc["India", f"share_nine_crops_{n}"] - ind[f"sh_{n}"]) < 2e-3 for n in ("kcal", "protein", "iron")),
          f"kcal {div.loc['India', 'share_nine_crops_kcal']:.4f} vs {ind.sh_kcal:.4f}")
    check("nine-crop share >= FBS-item-only share everywhere it is defined", (div.share_nine_crops_kcal.dropna() >= div.loc[div.share_nine_crops_kcal.notna(), "share_fbs_item_crops_kcal"] - 1e-12).all())
    sc = rd("yield_diet_scenarios.csv")
    check("standard shock is -10% everywhere", (sc[sc.scenario.str.startswith("S3")].dY_pct == -10).all())
    for name, d in (("historical scenarios", sc), ("future nutrition", rd("future_nutrition.csv"))):
        c1 = [c for c in d.columns if c.startswith("dkcal_pct") or c.startswith("diron_pct")]
        check(f"{name}: supply changes are <= 0 and the lower bound is no larger than the upper bound",
              (d[c1].max().max() <= 1e-9) and (d.dkcal_pct_lower.abs() <= d.dkcal_pct_upper.abs() + 1e-9).all() and (d.diron_pct_lower.abs() <= d.diron_pct_upper.abs() + 1e-9).all())

    out = pd.DataFrame(rows)
    out.to_csv(os.path.join(PROC, "consistency_checks.csv"), index=False)
    n_fail = int((~out.passed).sum())
    print(f"\n{len(out) - n_fail}/{len(out)} checks passed")
    sys.exit(1 if n_fail else 0)


if __name__ == "__main__":
    main()
