"""
15_future_index.py -- historical vs future vulnerability with fixed assumptions (end evaluation, C5).

Recorded decisions (docs/DECISION_REGISTER_END_EVAL.md, E5-E9):
  * Comparator: the 1971-2000 season-years processed by 14_future_climate.py WITHOUT change factors;
    future = the same years WITH the MRI-ESM2-0 SSP2-4.5 2041-2060 change factors. Identical processing.
    The present (2001-2024) score of the main index is shown alongside for context.
  * Exposure = stress LEVEL (as in the final method). The change is reported as future - historical
    score; no change term is added back into exposure.
  * ONE declared normalisation reference for every period: the main run's nine-crop maxima of the
    2001-2024 heat and water levels and of importance (index_reference.csv). Future values above the
    reference maximum are allowed to exceed 1 (not clipped). Periods are never normalised separately.
  * Held fixed: sensitivity (literature), importance (FBS 2021-23), crop area / irrigation (SPAM 2010),
    calendars, panels.
  * Percentage change is reported only where the historical F4 >= PCT_FLOOR (1 % of the largest
    historical pair score); otherwise only the absolute change is meaningful (column pct_change = NaN).
Outputs: future_components.csv, future_crop.csv, future_group.csv, future_clim_check.csv
"""
import importlib
import os

import numpy as np
import pandas as pd

from config import CROP_GROUPS, CROPS, PROC, RECENT

index = importlib.import_module("08_index")
FUT = "future_MRI-ESM2-0_ssp245_2041-2060"
HIST = "historical_1971_2000"
PCT_FLOOR_SHARE = 0.01


def main():
    base = index.load_index_components()                      # present components (2001-24 levels)
    ref_df = pd.read_csv(os.path.join(PROC, "index_reference.csv")).set_index("quantity")
    reference = {k: ref_df.loc[k, "max_value"] for k in ("H_heat", "H_water", "I")}
    fs = pd.read_pickle(os.path.join(PROC, "future_country_series.pkl"))
    # compatibility check: the unperturbed 1971-2000 run must equal the main pipeline's country series
    main_cs = pd.read_pickle(os.path.join(PROC, "country_series.pkl"))
    hh = fs[fs.scenario == HIST].merge(main_cs, on=["crop", "m49", "year"], suffixes=("_f", "_m"))
    pd.DataFrame([{"variable": v, "n": len(hh), "max_abs_diff": float(np.nanmax(np.abs(hh[f"{v}_f"] - hh[f"{v}_m"]))),
                   "max_value": float(np.nanmax(np.abs(hh[f"{v}_m"])))} for v in ("H_heat", "H_water", "teff_flow")]
                 ).to_csv(os.path.join(PROC, "future_check_hist_vs_main.csv"), index=False)
    fs = fs[fs.crop.isin(CROPS)]
    period_means = fs.groupby(["scenario", "crop", "m49"])[["H_heat", "H_water", "teff_flow", "mr_rainfed"]].mean().reset_index()

    frames = {}
    for label, scen in (("present_2001_2024", None), ("historical_1971_2000", HIST), ("future_2041_2060", FUT)):
        comp = base.copy()
        if scen is not None:
            pm = period_means[period_means.scenario == scen].drop(columns="scenario")
            comp = comp.drop(columns=["H_heat", "H_water"]).merge(pm, on=["crop", "m49"], how="left")
            assert comp.H_heat.notna().all(), comp[comp.H_heat.isna()][["crop", "country"]]
        frames[label] = index.calculate_indices(comp, reference=reference)

    keep = ["H_heat", "H_water", "E_heat", "E_water", "S_heat", "S_water", "In", "ES_paired", "F4_hazard_paired"]
    out = frames["historical_1971_2000"][["crop", "country", "m49", "production_t"]].copy()
    for label, fr in frames.items():
        for c in keep:
            out[f"{c}_{label}"] = fr[c].values
    out["teff_hist"] = frames["historical_1971_2000"]["teff_flow"].values
    out["teff_fut"] = frames["future_2041_2060"]["teff_flow"].values
    out["dTeff_C"] = out.teff_fut - out.teff_hist
    h, f = out["F4_hazard_paired_historical_1971_2000"], out["F4_hazard_paired_future_2041_2060"]
    out["dF4_abs"] = f - h
    floor = PCT_FLOOR_SHARE * h.max()
    out["pct_change"] = np.where(h >= floor, 100 * (f - h) / h, np.nan)
    out["dF4_from_heat"] = 0.5 * out.S_heat_future_2041_2060 * (out.E_heat_future_2041_2060 - out.E_heat_historical_1971_2000) * out.In_future_2041_2060
    out["dF4_from_water"] = 0.5 * out.S_water_future_2041_2060 * (out.E_water_future_2041_2060 - out.E_water_historical_1971_2000) * out.In_future_2041_2060
    out["exceeds_reference"] = (out.E_heat_future_2041_2060 > 1) | (out.E_water_future_2041_2060 > 1)
    for lbl in ("historical_1971_2000", "future_2041_2060"):
        out[f"rank_within_crop_{lbl}"] = out.groupby("crop")[f"F4_hazard_paired_{lbl}"].rank(ascending=False).astype(int)
        out[f"rank_all_pairs_{lbl}"] = out[f"F4_hazard_paired_{lbl}"].rank(ascending=False).astype(int)
    out["rank_change_all_pairs"] = out.rank_all_pairs_historical_1971_2000 - out.rank_all_pairs_future_2041_2060
    out.attrs["note"] = "MRI-ESM2-0 SSP2-4.5 2041-2060 change factors on 1971-2000 years; fixed reference"
    out.to_csv(os.path.join(PROC, "future_components.csv"), index=False)

    rows = []
    for crop, g in out.groupby("crop", sort=False):
        w = g.production_t / g.production_t.sum()
        r = {"crop": crop, "group": CROPS[crop]["group"], "n_pairs": len(g)}
        for lbl in ("present_2001_2024", "historical_1971_2000", "future_2041_2060"):
            r[f"F4_eq_{lbl}"] = g[f"F4_hazard_paired_{lbl}"].mean()
            r[f"F4_pw_{lbl}"] = (g[f"F4_hazard_paired_{lbl}"] * w).sum()
            r[f"E_heat_eq_{lbl}"] = g[f"E_heat_{lbl}"].mean()
            r[f"E_water_eq_{lbl}"] = g[f"E_water_{lbl}"].mean()
        r["dTeff_C_eq"] = g.dTeff_C.mean()
        r["pairs_with_higher_F4"] = int((g.dF4_abs > 0).sum())
        rows.append(r)
    crop_df = pd.DataFrame(rows)
    for wt in ("eq", "pw"):
        for lbl in ("historical_1971_2000", "future_2041_2060"):
            crop_df[f"rank_{wt}_{lbl}"] = crop_df[f"F4_{wt}_{lbl}"].rank(ascending=False).astype(int)
        crop_df[f"dF4_{wt}"] = crop_df[f"F4_{wt}_future_2041_2060"] - crop_df[f"F4_{wt}_historical_1971_2000"]
        hh = crop_df[f"F4_{wt}_historical_1971_2000"]
        crop_df[f"pct_{wt}"] = np.where(hh >= PCT_FLOOR_SHARE * hh.max(), 100 * crop_df[f"dF4_{wt}"] / hh, np.nan)
    crop_df.to_csv(os.path.join(PROC, "future_crop.csv"), index=False)

    grp = []
    for group, members in CROP_GROUPS.items():
        sub = crop_df[crop_df.crop.isin(members)]
        if len(sub) == 0:
            continue
        r = {"group": group, "crops": ", ".join(sub.crop)}
        for col in [c for c in crop_df.columns if c.startswith("F4_") or c.startswith("dF4_")]:
            r[col] = sub[col].mean()
        grp.append(r)
    pd.DataFrame(grp).to_csv(os.path.join(PROC, "future_group.csv"), index=False)

    # climatology-method check (threshold applied to the 20-year mean climate)
    clim = pd.read_csv(os.path.join(PROC, "future_country_clim.csv"))
    clim = clim[clim.crop.isin(CROPS)]
    cc = []
    for scen in ("hist_clim_1970_2000", "fut_clim_2041_2060"):
        comp = base.drop(columns=["H_heat", "H_water"]).merge(clim[clim.scenario == scen][["crop", "m49", "H_heat", "H_water"]], on=["crop", "m49"], how="left")
        comp = comp.fillna({"H_heat": 0.0, "H_water": 0.0})
        cc.append(index.calculate_indices(comp, reference=reference)[["crop", "country", "F4_hazard_paired", "H_heat", "H_water"]].add_suffix("_" + scen))
    cc = pd.concat(cc, axis=1)
    cc = cc.rename(columns={"crop_hist_clim_1970_2000": "crop", "country_hist_clim_1970_2000": "country"})
    cc = cc.merge(out[["crop", "country", "dF4_abs"]], on=["crop", "country"])
    cc["dF4_clim"] = cc.F4_hazard_paired_fut_clim_2041_2060 - cc.F4_hazard_paired_hist_clim_1970_2000
    cc["same_sign"] = np.sign(cc.dF4_clim.round(6)) == np.sign(cc.dF4_abs.round(6))
    cc.to_csv(os.path.join(PROC, "future_clim_check.csv"), index=False)

    pd.set_option("display.width", 250)
    print(crop_df[["crop", "F4_eq_historical_1971_2000", "F4_eq_future_2041_2060", "dF4_eq", "pct_eq",
                   "rank_eq_historical_1971_2000", "rank_eq_future_2041_2060", "dTeff_C_eq", "pairs_with_higher_F4"]].round(4).to_string(index=False))
    print(pd.DataFrame(grp).round(4).to_string(index=False))
    print("pairs exceeding reference:", int(out.exceeds_reference.sum()), "| climatology check same sign:",
          f"{cc.same_sign.mean():.2f}", "| Spearman(dF4 delta, dF4 clim) =", round(cc[["dF4_abs", "dF4_clim"]].corr("spearman").iloc[0, 1], 3))


if __name__ == "__main__":
    main()
