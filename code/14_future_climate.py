"""
14_future_climate.py -- future (2041-2060) heat and water stress with the SAME processing as the
historical index (end evaluation, commitment C5).

Future climate: WorldClim 2.1 CMIP6, MRI-ESM2-0, SSP2-4.5, 2041-2060, 10 arc-min. These files are
20-year MONTHLY CLIMATOLOGIES (12 bands), not year-by-year series, while our exposure is the mean over
years of a non-linear quantity (max(0, T_eff - T_crit); clip(1 - P/ETc)). Applying a threshold to an
average is not the same as averaging yearly exceedances, so two treatments are computed:

MAIN  (change-factor / "delta" method, yearly):
    change factors per cell and calendar month, relative to WorldClim 2.1 1970-2000 normals (the
    baseline the CMIP6 layers are downscaled and calibrated against):
        dTmax_m = Tmax_fut,m - Tmax_norm,m          dTmin_m = Tmin_fut,m - Tmin_norm,m       (additive)
        r_m     = P_fut,m / P_norm,m  (capped to [0, PREC_RATIO_CAP]; = 1 where P_norm,m < 1 mm) (multiplicative)
    FUTURE     = each 1971-2000 season-year with the change factors applied to every month
    HISTORICAL = the same 1971-2000 season-years unchanged
    -> both periods go through identical yearly processing, keep the same year-to-year variability,
       and differ only by the model's climate-change signal. The historical run must reproduce the
       1971-2000 values of country_series.pkl (checked at the end).
CHECK (climatology method):
    the hazards computed once on the 12-month climatologies: WorldClim 1970-2000 normals vs the CMIP6
    2041-2060 layers (threshold applied to the average). Reported only as a consistency check on the
    direction and size of change.

Held fixed: crop area and irrigation (SPAM 2010), calendars, flowering window, K_c, T_crit (and the
sensitivity and importance used later). Output: future_country_series.pkl, future_country_clim.csv,
future_check_hist_vs_main.csv.
"""
import importlib
import os
import sys
import zipfile

import numpy as np
import pandas as pd
import rasterio

from config import BASE, CLIMATE_CROPS, NX, NY, PROC, RAW, WORK, season_kc

hazards = importlib.import_module("04_hazards")
climate = importlib.import_module("04_climate_exposure")

MODEL, SCENARIO, FUT_PERIOD = "MRI-ESM2-0", "ssp245", "2041-2060"
PREC_RATIO_CAP = 3.0
YEARS = np.arange(BASE[0], BASE[1] + 1)          # 1971-2000 season-years (1970 read for New Year crossing)
MONTH_DAYS = hazards.MONTH_DAYS
TCRIT_OFFSETS = ()   # threshold offsets are tested on the present index only (memory: 12 grids x 2 scenarios)


def read_bands(path):
    with rasterio.open(path) as src:
        a = src.read().astype("float64").reshape(src.count, -1)
    return np.where(~np.isfinite(a) | (a < -1000) | (a > 1e5), np.nan, a)


def read_normals(var):
    zip_path = (os.path.join(RAW, "worldclim", "wc2.1_10m_prec.zip") if var == "prec"
                else os.path.join(RAW, "normals", f"wc2.1_10m_{var}.zip"))
    out_dir = os.path.join(WORK, "wc_normals")
    os.makedirs(out_dir, exist_ok=True)
    months = []
    with zipfile.ZipFile(zip_path) as z:
        for m in range(1, 13):
            name = [n for n in z.namelist() if n.endswith(f"_{var}_{m:02d}.tif")][0]
            if not os.path.exists(os.path.join(out_dir, os.path.basename(name))):
                z.extract(name, out_dir)
                if os.path.dirname(name):
                    os.replace(os.path.join(out_dir, name), os.path.join(out_dir, os.path.basename(name)))
            months.append(read_bands(os.path.join(out_dir, os.path.basename(name)))[0])
    return np.stack(months)


def change_factors():
    norm = {v: read_normals(v) for v in ("tmax", "tmin", "prec")}
    fut = {v: read_bands(os.path.join(RAW, "cmip6", f"wc2.1_10m_{v}_{MODEL}_{SCENARIO}_{FUT_PERIOD}.tif"))
           for v in ("tmax", "tmin", "prec")}
    for v in fut:
        assert fut[v].shape == (12, NX * NY) and norm[v].shape == (12, NX * NY), (v, fut[v].shape, norm[v].shape)
    with np.errstate(invalid="ignore", divide="ignore"):
        ratio = np.where(norm["prec"] >= 1.0, fut["prec"] / norm["prec"], 1.0)
    ratio = np.clip(np.nan_to_num(ratio, nan=1.0), 0.0, PREC_RATIO_CAP)
    d = {"tmax": np.nan_to_num(fut["tmax"] - norm["tmax"]), "tmin": np.nan_to_num(fut["tmin"] - norm["tmin"]),
         "prec": ratio}
    return d, norm, fut


def monthly_terms(tmax, tmin, ra_rows, month_idx, tcrit):
    tmean = (tmax + tmin) / 2.0
    et0 = np.maximum(0.0023 * (tmean + 17.8) * np.sqrt(np.maximum(tmax - tmin, 0)) * 0.408 * ra_rows
                     * MONTH_DAYS[month_idx], 0)
    teff = (tmean + tmax) / 2.0
    return et0, teff, np.maximum(teff - tcrit, 0)


def setup():
    ra = hazards.compute_extraterrestrial_radiation_grid()
    rows_all = np.repeat(np.arange(NY), NX)
    crops = {}
    for crop, info in CLIMATE_CROPS.items():
        g = np.load(os.path.join(WORK, f"grids_{crop}.npz"))
        cells = np.load(os.path.join(WORK, f"series_prec_{crop}.npz"))["cells"]
        crops[crop] = {
            "cells": cells, "rows": rows_all[cells], "tcrit": info["tcrit"],
            "gs": (g["w_cur"].reshape(-1, 12)[cells], g["w_prev"].reshape(-1, 12)[cells]),
            "fl": (g["wf_cur"].reshape(-1, 12)[cells], g["wf_prev"].reshape(-1, 12)[cells]),
            "A": g["area_A"].ravel()[cells], "R": np.minimum(g["area_R"].ravel()[cells], g["area_A"].ravel()[cells]),
            "acc": {s: {k: np.zeros((len(YEARS), len(cells)), "float32")
                        for k in ["prec", "et0", "teff", "heat"] + [f"heat_off{o:+d}" for o in TCRIT_OFFSETS]}
                    for s in ("hist", "fut")},
        }
    return ra, crops


def accumulate(acc, key, weights, value, year, m):
    w_cur, w_prev = weights[0][:, m], weights[1][:, m]
    if YEARS[0] <= year <= YEARS[-1]:
        acc[key][year - YEARS[0]] += np.where(w_cur > 0, w_cur * value, 0.0).astype("float32")
    if YEARS[0] <= year + 1 <= YEARS[-1]:
        acc[key][year + 1 - YEARS[0]] += np.where(w_prev > 0, w_prev * value, 0.0).astype("float32")


def yearly_pass(ra, crops, delta):
    files = {v: climate.extract_and_index_monthly_files(folder, v)
             for v, folder in (("tmax", "tmax"), ("tmin", "tmin"), ("prec", "worldclim"))}
    for year in range(YEARS[0] - 1, YEARS[-1] + 1):
        for m in range(12):
            raw = {v: climate.read_raster_layer(files[v][(year, m + 1)]) for v in files}
            for scen in ("hist", "fut"):
                if scen == "hist":
                    tx, tn, pr = raw["tmax"], raw["tmin"], raw["prec"]
                else:
                    tx, tn, pr = raw["tmax"] + delta["tmax"][m], raw["tmin"] + delta["tmin"][m], raw["prec"] * delta["prec"][m]
                for c in crops.values():
                    et0, teff, heat = monthly_terms(tx[c["cells"]], tn[c["cells"]], ra[m, c["rows"]], m, c["tcrit"])
                    acc = c["acc"][scen]
                    accumulate(acc, "et0", c["gs"], et0, year, m)
                    accumulate(acc, "prec", c["gs"], pr[c["cells"]], year, m)
                    accumulate(acc, "teff", c["fl"], teff, year, m)
                    accumulate(acc, "heat", c["fl"], heat, year, m)
                    for o in TCRIT_OFFSETS:
                        accumulate(acc, f"heat_off{o:+d}", c["fl"], np.maximum(teff - c["tcrit"] - o, 0), year, m)
        print("future pass", year, flush=True)


def country_aggregate(crop, c, per_cell, country_grid):
    """per_cell: dict of arrays (n_years, n_cells) -> national values, exactly as 05_country_series.py."""
    kc = season_kc(crop)
    etc = kc * per_cell["et0"].astype("float64")
    prec = per_cell["prec"].astype("float64")
    mr = np.where(etc > 0, prec / np.where(etc > 0, etc, 1.0), np.nan)
    deficit = np.clip(1.0 - mr, 0.0, 1.0)
    codes = country_grid[c["cells"]]
    out = []
    wmean = importlib.import_module("05_country_series").compute_weighted_mean_1d
    for code in np.unique(codes):
        if code < 0:
            continue
        msk = codes == code
        A, R = c["A"][msk], c["R"][msk]
        if A.sum() <= 0:
            continue
        rec = {"H_heat": wmean(per_cell["heat"][:, msk].astype("float64"), A),
               "H_water": np.where(np.isfinite(deficit[:, msk]), deficit[:, msk], 0.0) @ R / A.sum(),
               "teff_flow": wmean(per_cell["teff"][:, msk].astype("float64"), A),
               "mr_rainfed": wmean(mr[:, msk], R) if R.sum() > 0 else np.full(deficit.shape[0], np.nan)}
        for o in TCRIT_OFFSETS:
            rec[f"H_heat_off{o:+d}"] = wmean(per_cell[f"heat_off{o:+d}"][:, msk].astype("float64"), A)
        out.append((int(code), rec))
    return out


def climatology_hazards(ra, crops, norm, fut, country_grid):
    rows = []
    for scen, src in (("hist_clim_1970_2000", norm), ("fut_clim_2041_2060", fut)):
        for crop, c in crops.items():
            per = {k: np.zeros((1, len(c["cells"]))) for k in ["prec", "et0", "teff", "heat"] + [f"heat_off{o:+d}" for o in TCRIT_OFFSETS]}
            for m in range(12):
                tx, tn, pr = src["tmax"][m][c["cells"]], src["tmin"][m][c["cells"]], src["prec"][m][c["cells"]]
                et0, teff, heat = monthly_terms(tx, tn, ra[m, c["rows"]], m, c["tcrit"])
                wg = c["gs"][0][:, m] + c["gs"][1][:, m]
                wf = c["fl"][0][:, m] + c["fl"][1][:, m]
                per["et0"][0] += np.where(wg > 0, wg * et0, 0.0)
                per["prec"][0] += np.where(wg > 0, wg * pr, 0.0)
                per["teff"][0] += np.where(wf > 0, wf * teff, 0.0)
                per["heat"][0] += np.where(wf > 0, wf * heat, 0.0)
                for o in TCRIT_OFFSETS:
                    per[f"heat_off{o:+d}"][0] += np.where(wf > 0, wf * np.maximum(teff - c["tcrit"] - o, 0), 0.0)
            wsum = c["fl"][0].sum(1) + c["fl"][1].sum(1)
            wsum = np.where(wsum > 0, wsum, np.nan)
            for k in ["teff", "heat"] + [f"heat_off{o:+d}" for o in TCRIT_OFFSETS]:
                per[k] = per[k] / wsum
            for code, rec in country_aggregate(crop, c, per, country_grid):
                rows.append({"crop": crop, "m49": code, "scenario": scen, **{k: v[0] for k, v in rec.items()}})
    return pd.DataFrame(rows)


def main():
    country_grid = np.load(os.path.join(WORK, "country_grid.npy")).ravel()
    delta, norm, fut = change_factors()
    ra, crops = setup()
    clim = climatology_hazards(ra, crops, norm, fut, country_grid)
    clim.to_csv(os.path.join(PROC, "future_country_clim.csv"), index=False)
    print("climatology check written", len(clim), flush=True)

    yearly_pass(ra, crops, delta)
    records = []
    for crop, c in crops.items():
        wsum = c["fl"][0].sum(1) + c["fl"][1].sum(1)
        wsum = np.where(wsum > 0, wsum, np.nan)
        for scen in ("hist", "fut"):
            per = dict(c["acc"][scen])
            for k in ["teff", "heat"] + [f"heat_off{o:+d}" for o in TCRIT_OFFSETS]:
                per[k] = per[k].astype("float64") / wsum
            # per-cell period means (used for sub-national analysis, e.g. Telangana, in 21_india_hyderabad.py)
            kc = season_kc(crop)
            etc = kc * per["et0"].astype("float64")
            mr = np.where(etc > 0, per["prec"].astype("float64") / np.where(etc > 0, etc, 1.0), np.nan)
            np.savez_compressed(os.path.join(WORK, f"future_cellmeans_{crop}_{scen}.npz"), cells=c["cells"],
                                heat=np.nanmean(per["heat"], axis=0), deficit=np.nanmean(np.clip(1.0 - mr, 0.0, 1.0), axis=0),
                                teff=np.nanmean(per["teff"], axis=0), prec=np.nanmean(per["prec"].astype("float64"), axis=0),
                                etc=np.nanmean(etc, axis=0))
            for code, rec in country_aggregate(crop, c, per, country_grid):
                for i, y in enumerate(YEARS):
                    records.append({"crop": crop, "m49": code, "year": int(y),
                                    "scenario": "historical_1971_2000" if scen == "hist" else f"future_{MODEL}_{SCENARIO}_{FUT_PERIOD}",
                                    **{k: v[i] for k, v in rec.items()}})
        print(crop, "aggregated", flush=True)
    fs = pd.DataFrame(records)
    fs.attrs.update(model=MODEL, scenario=SCENARIO, period=FUT_PERIOD, method="change factor on 1971-2000 years")
    fs.to_pickle(os.path.join(PROC, "future_country_series.pkl"))

    print("future series written; the historical-reproduction check runs in 15_future_index.py")


if __name__ == "__main__":
    main()
