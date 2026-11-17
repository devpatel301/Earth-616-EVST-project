"""
21_india_hyderabad.py -- what the index says for India, Telangana and Hyderabad (end evaluation, insight layer).
All numbers come from the project's data (FAOSTAT FBS/SUA, WorldClim, SPAM, CMIP6) or from the official
survey indicators collected in data/external/india_hyderabad_indicators.csv (MoSPI HCES, NFHS-5, CNNS),
each with its source and table/page. Outputs -> data/processed/nine_crop/india_*.csv, telangana_*.csv,
hyderabad_*.csv

A. India nine-crop profile: index components, rank, nutrient shares, future change, -10 % shock, future yield.
B. Food-supply diversity (FAO FBS 2021-23, Remans et al. 2014 style): Shannon diversity H of each nutrient's
   supply across food items and its effective number of sources exp(H); top source and its share; cereal
   share of energy; share supplied by the nine study crops. India vs the other panel countries and World.
C. Telangana (Hyderabad's home state; Natural Earth 1:10m admin-1 boundary): crop areas (SPAM 2010, all 42
   SPAM crops), and heat / water exposure of each study crop's Telangana area for 2001-24 (observed), 1971-2000
   and 2041-60 (change factors), on the SAME normalisation reference as the national index.
D. Hyderabad grid cell (17.385 N, 78.487 E; WorldClim 10'): observed 1971-2024 temperature and rainfall,
   trends, and the MRI-ESM2-0 SSP2-4.5 2041-60 change.
"""
import os
import zipfile

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio import features
from rasterio.transform import from_origin

from config import CROP_ORDER, CROPS, NX, NY, PROC, RAW, RES, ROOT_DIR, WORK

HYD_LAT, HYD_LON = 17.385, 78.4867
HYD_ROW, HYD_COL = int((90 - HYD_LAT) / RES), int((HYD_LON + 180) / RES)
INDIA = 356
NUTRIENTS = ["kcal", "protein", "fat", "zinc", "iron"]
CR = [c for c in CROP_ORDER if c in CROPS]
CEREAL_ITEMS = ["Wheat and products", "Rice and products", "Barley and products", "Maize and products", "Rye and products",
                "Oats", "Millet and products", "Sorghum and products", "Cereals, Other"]
F4 = "F4_hazard_paired"
P = lambda f: os.path.join(PROC, f)


def india_profile():
    comp = pd.read_csv(P("index_components.csv"))
    ind = comp[comp.m49 == INDIA].copy()
    ind["rank_in_India"] = ind[F4].rank(ascending=False).astype(int)
    ind["heat_part"] = 0.5 * ind.E_heat * ind.S_heat * ind.In
    ind["water_part"] = 0.5 * ind.E_water * ind.S_water * ind.In
    fut = pd.read_csv(P("future_components.csv"))
    fut = fut[fut.m49 == INDIA][["crop", "F4_hazard_paired_historical_1971_2000", "F4_hazard_paired_future_2041_2060", "dF4_abs", "pct_change", "dTeff_C",
                                 "E_heat_historical_1971_2000", "E_heat_future_2041_2060", "E_water_historical_1971_2000", "E_water_future_2041_2060"]]
    sc = pd.read_csv(P("yield_diet_scenarios.csv"))
    s3 = sc[(sc.country == "India") & sc.scenario.str.startswith("S3")][["crop", "ssr", "dkcal_pct_upper", "dprotein_pct_upper", "dfat_pct_upper",
                                                                        "dzinc_pct_upper", "diron_pct_upper", "dMAR_pts_upper", "dMAR_pts_lower"]]
    fy = pd.read_csv(P("future_yield.csv"))
    fy = fy[fy.m49 == INDIA][["crop", "dY_lit_pct", "dY_emp_pct", "heat_loss_hist", "heat_loss_fut", "water_loss_hist", "water_loss_fut"]]
    out = ind.merge(fut, on="crop", how="left").merge(s3, on="crop", how="left").merge(fy, on="crop", how="left")
    out["group"] = out.crop.map(lambda c: CROPS[c]["group"])
    out.sort_values(F4, ascending=False).to_csv(P("india_profile.csv"), index=False)
    return out


def food_supply_diversity():
    sup = pd.read_pickle(P("nutrient_supply.pkl"))
    sup = sup[sup.method == "new"]
    last = int(sup.Year.max())
    s = sup[sup.Year.between(last - 2, last)].groupby(["m49", "Area", "Item"])[NUTRIENTS].mean().reset_index()
    nine_items = {it: c for c in CROPS for it in CROPS[c].get("fbs_items", [])}
    countries = set(pd.read_csv(P("panels.csv")).m49) | {1}   # 1 = World (FAOSTAT M49 001)
    rows = []
    for (m49, area), g in s[s.m49.isin(countries)].groupby(["m49", "Area"]):
        r = {"m49": m49, "Area": area, "years": f"{last - 2}-{last}", "n_items_supplying_kcal": int((g.kcal > 0).sum())}
        for n in NUTRIENTS:
            v = g[n].clip(lower=0)
            p = v / v.sum()
            p = p[p > 0]
            H = float(-(p * np.log(p)).sum())
            top = g.loc[v.idxmax()]
            r.update({f"H_{n}": H, f"eff_sources_{n}": float(np.exp(H)), f"top_source_{n}": top.Item, f"top_share_{n}": float(v.max() / v.sum()),
                      f"total_{n}": float(v.sum()),
                      f"share_nine_crops_{n}": float(v[g.Item.isin(nine_items)].sum() / v.sum())})
        r["cereal_share_kcal"] = float(g[g.Item.isin(CEREAL_ITEMS)].kcal.sum() / g.kcal.sum())
        rows.append(r)
    d = pd.DataFrame(rows).sort_values("eff_sources_kcal")
    d.to_csv(P("food_supply_diversity.csv"), index=False)
    # India: top sources of each nutrient
    ind = s[s.m49 == INDIA].copy()
    top_rows = []
    for n in NUTRIENTS:
        t = ind[["Item", n]].sort_values(n, ascending=False)
        t["share"] = t[n] / t[n].sum()
        for _, r in t.head(8).iterrows():
            top_rows.append({"nutrient": n, "item": r.Item, "per_capita_day": r[n], "share": r.share, "study_crop": nine_items.get(r.Item, "")})
    pd.DataFrame(top_rows).to_csv(P("india_nutrient_sources.csv"), index=False)
    return d


def telangana_mask():
    gdf = gpd.read_file("zip://" + os.path.join(RAW, "naturalearth_admin1", "ne_10m_admin_1_states_provinces.zip"))
    tg = gdf[gdf.iso_3166_2 == "IN-TG"]
    assert len(tg) == 1
    mask = features.rasterize([(tg.geometry.iloc[0], 1)], out_shape=(NY, NX), transform=from_origin(-180, 90, RES, RES), fill=0, dtype="uint8")
    return mask.astype(bool)


def telangana_crop_areas(mask):
    spam_zip = os.path.join(RAW, "spam", "spam2010v2r0_global_harv_area.geotiff.zip")
    names = [n for n in zipfile.ZipFile(spam_zip).namelist() if n.endswith("_A.tif")]
    rows = []
    mask5 = np.repeat(np.repeat(mask, 2, 0), 2, 1)
    for n in names:
        with rasterio.open(f"/vsizip/{spam_zip}/{n}") as src:
            a = src.read(1).astype("float64")
        a = np.where(a < 0, 0, a)
        code = n.split("_")[-2]
        rows.append({"spam_code": code, "telangana_area_ha": a[mask5].sum(), "india_area_ha": np.nan})
    d = pd.DataFrame(rows)
    d["share_of_telangana_cropland_pct"] = 100 * d.telangana_area_ha / d.telangana_area_ha.sum()
    code_to_crop = {CROPS[c]["spam"]: c for c in CROPS}
    d["study_crop"] = d.spam_code.map(code_to_crop).fillna("")
    d = d.sort_values("telangana_area_ha", ascending=False)
    d.to_csv(P("telangana_crop_areas_spam2010.csv"), index=False)
    return d


def telangana_exposure(mask):
    ref = pd.read_csv(P("index_reference.csv")).set_index("quantity").max_value
    comp = pd.read_csv(P("index_components.csv"))
    ind = comp[comp.m49 == INDIA].set_index("crop")
    flat = np.flatnonzero(mask.ravel())
    rows = []
    for c in CR:
        cm = np.load(os.path.join(WORK, f"cellmaps_{c}.npz"))
        sel = np.isin(cm["cells"], flat)
        A, R = cm["A"][sel], cm["R"][sel]
        if A.sum() <= 0:
            rows.append({"crop": c, "telangana_area_ha": 0.0})
            continue
        w = lambda v, wt: np.nansum(v * wt) / np.nansum(wt[np.isfinite(v)])
        r = {"crop": c, "telangana_area_ha": A.sum(), "rainfed_share": R.sum() / A.sum(),
             "L_heat_2001_2024": w(cm["heat_R"][sel], A), "L_water_2001_2024": np.nansum(np.nan_to_num(cm["def_R"][sel]) * R) / A.sum(),
             "teff_2001_2024": w(cm["teff_R"][sel], A), "teff_1971_2000_obs": w(cm["teff_B"][sel], A)}
        for scen, lab in (("hist", "1971_2000"), ("fut", "2041_2060")):
            f = np.load(os.path.join(WORK, f"future_cellmeans_{c}_{scen}.npz"))
            fs = np.isin(f["cells"], flat)
            assert np.array_equal(f["cells"][fs], cm["cells"][sel])
            r[f"L_heat_{lab}"] = w(f["heat"][fs], A)
            r[f"L_water_{lab}"] = np.nansum(np.nan_to_num(f["deficit"][fs]) * R) / A.sum()
            r[f"teff_{lab}"] = w(f["teff"][fs], A)
        for lab in ("2001_2024", "1971_2000", "2041_2060"):
            r[f"E_heat_{lab}"] = r[f"L_heat_{lab}"] / ref["H_heat"]
            r[f"E_water_{lab}"] = r[f"L_water_{lab}"] / ref["H_water"]
            if c in ind.index:
                r[f"F4_{lab}_India_importance"] = 0.5 * (r[f"E_heat_{lab}"] * ind.loc[c, "S_heat"] + r[f"E_water_{lab}"] * ind.loc[c, "S_water"]) * ind.loc[c, "In"]
        r["dTeff_future_C"] = r["teff_2041_2060"] - r["teff_1971_2000"]
        r["dTeff_observed_C"] = r["teff_2001_2024"] - r["teff_1971_2000_obs"]
        r["India_L_heat_2001_2024"] = ind.loc[c, "H_heat"] if c in ind.index else np.nan
        r["India_L_water_2001_2024"] = ind.loc[c, "H_water"] if c in ind.index else np.nan
        rows.append(r)
    d = pd.DataFrame(rows)
    d.to_csv(P("telangana_exposure.csv"), index=False)
    return d


def hyderabad_climate():
    import importlib
    clim = importlib.import_module("04_climate_exposure")
    files = {v: clim.extract_and_index_monthly_files(folder, v) for v, folder in (("tmax", "tmax"), ("tmin", "tmin"), ("prec", "worldclim"))}
    idx = HYD_ROW * NX + HYD_COL
    rows = []
    for (y, m), path in sorted(files["tmax"].items()):
        if y < 1971:
            continue
        rec = {"year": y, "month": m}
        for v in files:
            with rasterio.open(files[v][(y, m)]) as src:
                rec[v] = float(src.read(1, window=((HYD_ROW, HYD_ROW + 1), (HYD_COL, HYD_COL + 1)))[0, 0])
        rows.append(rec)
    mon = pd.DataFrame(rows)
    mon.to_csv(P("hyderabad_cell_monthly.csv"), index=False)
    ann = mon.groupby("year").agg(tmax_mean=("tmax", "mean"), tmin_mean=("tmin", "mean"), prec_total=("prec", "sum")).reset_index()
    ann["tmax_AprMay"] = mon[mon.month.isin([4, 5])].groupby("year").tmax.mean().values
    ann["prec_JJAS"] = mon[mon.month.isin([6, 7, 8, 9])].groupby("year").prec.sum().values
    ann["months_tmax_ge_40"] = mon.assign(h=mon.tmax >= 40).groupby("year").h.sum().values
    ann.to_csv(P("hyderabad_cell_annual.csv"), index=False)
    summ = []
    for col in ("tmax_mean", "tmin_mean", "tmax_AprMay", "prec_total", "prec_JJAS", "months_tmax_ge_40"):
        b = ann[ann.year.between(1971, 2000)][col]; r = ann[ann.year.between(2001, 2024)][col]
        slope = np.polyfit(ann.year, ann[col], 1)[0] * 10
        summ.append({"variable": col, "mean_1971_2000": b.mean(), "mean_2001_2024": r.mean(), "change": r.mean() - b.mean(), "trend_per_decade_1971_2024": slope})
    # CMIP6 change at the cell (relative to WorldClim 1970-2000 normals)
    fut_idx = importlib.import_module("14_future_climate")
    norm = {v: fut_idx.read_normals(v)[:, idx] for v in ("tmax", "tmin", "prec")}
    fut = {v: fut_idx.read_bands(os.path.join(RAW, "cmip6", f"wc2.1_10m_{v}_MRI-ESM2-0_ssp245_2041-2060.tif"))[:, idx] for v in ("tmax", "tmin", "prec")}
    cm = pd.DataFrame({"month": range(1, 13), **{f"{v}_normal_1970_2000": norm[v] for v in norm}, **{f"{v}_2041_2060": fut[v] for v in fut}})
    cm.to_csv(P("hyderabad_cell_cmip6.csv"), index=False)
    summ += [{"variable": "tmax_mean (CMIP6 2041-60 minus normal)", "change": float(np.mean(fut["tmax"] - norm["tmax"]))},
             {"variable": "tmax_AprMay (CMIP6 2041-60 minus normal)", "change": float(np.mean(fut["tmax"][3:5] - norm["tmax"][3:5]))},
             {"variable": "tmax_AprMay 2041-60 level", "mean_2001_2024": np.nan, "change": float(np.mean(fut["tmax"][3:5]))},
             {"variable": "tmin_mean (CMIP6 2041-60 minus normal)", "change": float(np.mean(fut["tmin"] - norm["tmin"]))},
             {"variable": "prec_total ratio (CMIP6 2041-60 / normal)", "change": float(fut["prec"].sum() / norm["prec"].sum())},
             {"variable": "prec_JJAS ratio (CMIP6 2041-60 / normal)", "change": float(fut["prec"][5:9].sum() / norm["prec"][5:9].sum())}]
    pd.DataFrame(summ).to_csv(P("hyderabad_climate_summary.csv"), index=False)
    return pd.DataFrame(summ)


DIET_CSV = os.path.join(ROOT_DIR, "data", "external", "india_hyderabad_indicators.csv")


def hyderabad_diet(prof, tg):
    import hyderabad_diet as hd
    return hd.run(prof, tg)


DIG = dict(zip("0123456789", ["Zero", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine"]))


def export_macros(prof, div, areas, tg, clim, extra=None):
    """LaTeX macros for the India/Hyderabad section (no hand-typed values)."""
    from config import TEX
    m = []
    def mac(k, v):
        k = "".join(DIG.get(ch, ch) for ch in k if ch.isalnum())
        m.append(f"\\newcommand{{\\{k}}}{{{v}}}")
    lab = {c: CROPS[c]["label"] for c in CROPS}
    p = prof.sort_values(F4, ascending=False).reset_index(drop=True)
    mac("indOrder", " $>$ ".join(lab[c] for c in p.crop))
    for i, r in p.head(4).iterrows():
        mac(f"indTop{'ABCD'[i]}", lab[r.crop]); mac(f"indTop{'ABCD'[i]}Value", f"{r[F4]:.4f}")
    pr = prof.set_index("crop")
    for c in CR:
        for n in ("kcal", "protein", "iron", "zinc", "fat"):
            mac(f"ind{c.capitalize()}Sh{n.capitalize()}", f"{100 * pr.loc[c, f'sh_{n}']:.1f}")
        mac(f"ind{c.capitalize()}FFour", f"{pr.loc[c, F4]:.4f}")
        mac(f"ind{c.capitalize()}HeatPart", f"{pr.loc[c, 'heat_part']:.4f}"); mac(f"ind{c.capitalize()}WaterPart", f"{pr.loc[c, 'water_part']:.4f}")
        mac(f"ind{c.capitalize()}dY", f"{pr.loc[c, 'dY_lit_pct']:+.1f}"); mac(f"ind{c.capitalize()}dYemp", f"{pr.loc[c, 'dY_emp_pct']:+.1f}")
        mac(f"ind{c.capitalize()}dFFour", f"{pr.loc[c, 'dF4_abs']:+.4f}"); mac(f"ind{c.capitalize()}dTeff", f"{pr.loc[c, 'dTeff_C']:+.1f}")
        mac(f"ind{c.capitalize()}ShockKcal", f"{pr.loc[c, 'dkcal_pct_upper']:+.2f}"); mac(f"ind{c.capitalize()}ShockIron", f"{pr.loc[c, 'diron_pct_upper']:+.2f}")
        mac(f"ind{c.capitalize()}ShockMar", f"{pr.loc[c, 'dMAR_pts_upper']:+.2f}")
    d = div.set_index("Area")
    for area, nm in (("India", "Ind"), ("World", "World"), ("Bangladesh", "Bgd"), ("China, mainland", "Chn"), ("United States of America", "Usa")):
        for n in ("kcal", "protein", "iron", "zinc"):
            mac(f"div{nm}{n.capitalize()}", f"{d.loc[area, f'eff_sources_{n}']:.1f}")
        mac(f"div{nm}Cereal", f"{100 * d.loc[area, 'cereal_share_kcal']:.0f}")
    mac("divIndIronTop", d.loc["India", "top_source_iron"].replace(" and products", ""))
    mac("divIndIronTopShare", f"{100 * d.loc['India', 'top_share_iron']:.1f}")
    mac("divIndRank", int((div.eff_sources_kcal < d.loc["India", "eff_sources_kcal"]).sum()) + 1); mac("divN", len(div))
    mac("divIndNineKcal", f"{100 * d.loc['India', 'share_nine_crops_kcal']:.0f}"); mac("divIndNineIron", f"{100 * d.loc['India', 'share_nine_crops_iron']:.0f}")
    a = areas.set_index("spam_code")
    for code, nm in (("RICE", "Rice"), ("COTT", "Cotton"), ("MAIZ", "Maize"), ("BEAN", "Bean"), ("PIGE", "Pigeonpea"), ("GROU", "Groundnut"),
                     ("CHIC", "Chickpea"), ("SOYB", "Soybean"), ("SORG", "Sorghum"), ("WHEA", "Wheat")):
        mac(f"tgArea{nm}", f"{a.loc[code, 'share_of_telangana_cropland_pct']:.1f}"); mac(f"tgHa{nm}", f"{a.loc[code, 'telangana_area_ha'] / 1e3:,.0f}".replace(",", "{,}"))
    mac("tgNineShare", f"{a[a.study_crop != ''].share_of_telangana_cropland_pct.sum():.0f}")
    t = tg.set_index("crop")
    for c in ("rice", "maize", "chickpea", "bean", "groundnut", "soybean", "wheat", "rapeseed"):
        if c in t.index and t.loc[c, "telangana_area_ha"] > 0:
            mac(f"tg{c.capitalize()}Rainfed", f"{100 * t.loc[c, 'rainfed_share']:.0f}")
            for k in ("E_heat_2001_2024", "E_water_2001_2024", "E_heat_2041_2060", "E_water_2041_2060", "dTeff_future_C", "dTeff_observed_C"):
                mac(f"tg{c.capitalize()}{k}", f"{t.loc[c, k]:.2f}")
    cs = clim.set_index("variable")
    mac("hydTmaxBase", f"{cs.loc['tmax_mean', 'mean_1971_2000']:.1f}"); mac("hydTmaxRecent", f"{cs.loc['tmax_mean', 'mean_2001_2024']:.1f}")
    mac("hydTmaxTrend", f"{cs.loc['tmax_mean', 'trend_per_decade_1971_2024']:.2f}"); mac("hydTminTrend", f"{cs.loc['tmin_mean', 'trend_per_decade_1971_2024']:.2f}")
    mac("hydAMBase", f"{cs.loc['tmax_AprMay', 'mean_1971_2000']:.1f}"); mac("hydAMRecent", f"{cs.loc['tmax_AprMay', 'mean_2001_2024']:.1f}")
    mac("hydRainBase", f"{cs.loc['prec_total', 'mean_1971_2000']:.0f}"); mac("hydRainRecent", f"{cs.loc['prec_total', 'mean_2001_2024']:.0f}")
    mac("hydAMFutChange", f"{cs.loc['tmax_AprMay (CMIP6 2041-60 minus normal)', 'change']:+.1f}")
    mac("hydAMFutLevel", f"{cs.loc['tmax_AprMay 2041-60 level', 'change']:.1f}")
    mac("hydTminFutChange", f"{cs.loc['tmin_mean (CMIP6 2041-60 minus normal)', 'change']:+.1f}")
    mac("hydTmaxFutChange", f"{cs.loc['tmax_mean (CMIP6 2041-60 minus normal)', 'change']:+.1f}")
    mac("hydRainFutRatio", f"{100 * (cs.loc['prec_total ratio (CMIP6 2041-60 / normal)', 'change'] - 1):+.0f}")
    for k, v in (extra or {}).items():
        mac(k, v)
    with open(os.path.join(TEX, "generated", "numbers_india.tex"), "w", encoding="utf-8") as f:
        f.write("% generated by code/21_india_hyderabad.py -- do not edit\n" + "\n".join(m) + "\n")
    print(len(m), "India/Hyderabad macros")


def main():
    pd.set_option("display.width", 250)
    prof = india_profile()
    print(prof[["crop", F4, "rank_in_India", "heat_part", "water_part", "In", "sh_kcal", "sh_protein", "sh_iron", "dF4_abs", "dkcal_pct_upper", "dMAR_pts_upper", "dY_lit_pct"]].round(4).to_string(index=False))
    div = food_supply_diversity()
    print(div[["Area", "eff_sources_kcal", "eff_sources_protein", "eff_sources_iron", "eff_sources_zinc", "cereal_share_kcal", "top_source_iron", "top_share_iron"]].round(3).to_string(index=False))
    mask = telangana_mask()
    print("Telangana cells:", int(mask.sum()), "| Hyderabad cell in Telangana:", bool(mask[HYD_ROW, HYD_COL]))
    areas = telangana_crop_areas(mask)
    print(areas.head(12).round(1).to_string(index=False))
    tg = telangana_exposure(mask)
    print(tg.round(4).T.to_string())
    clim = hyderabad_climate()
    print(clim.round(3).to_string(index=False))
    extra = hyderabad_diet(prof, tg) if os.path.exists(DIET_CSV) else {}
    export_macros(prof, div, areas, tg, clim, extra)


if __name__ == "__main__":
    main()
