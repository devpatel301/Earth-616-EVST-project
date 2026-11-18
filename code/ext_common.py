"""
ext_common.py -- shared accounting for the research extensions (CO2 nutrient quality, food-supply diversity
after crop losses). Imported by 28_co2_quality.py, 29_diversity_losses.py and 32_extension_checks.py.

Accounting basis (unchanged from the main pipeline, 07/09/16):
  * national supply per FBS leaf item, method "new" (FAOSTAT FBS 2010- methodology), mean of the yearly
    values over the latest three years (2021-2023), missing item-years counted as 0 so that item sums
    reproduce the national totals of adequacy.csv exactly;
  * kcal, protein and fat are the FAOSTAT FBS values; zinc and iron = food quantity x USDA SR Legacy
    composition (07_nutrition.py);
  * chickpea and lentil supply comes from FAOSTAT SUA and is ALREADY INSIDE the FBS item
    "Pulses, Other and products": it is never added as supply or as a Shannon category; a loss of chickpea
    or lentil is removed from that parent item;
  * a crop's FBS items (primary product and its oil) are reduced by the same quantity fraction;
  * domestic production shock -> supply: f = loss x SSR*, SSR* = min(1, max(0, SSR)) (1 if domestic supply
    <= 0 with positive production) -- the upper bound of 09/16 (decision E19). The exports-first lower
    bound is also provided.
"""
import os

import numpy as np
import pandas as pd

from config import BASE, CROPS, PROC, RECENT

NUTRIENTS = ["kcal", "protein", "fat", "zinc", "iron"]
PARENT_PULSES = "Pulses, Other and products"
SUA_ITEMS = {it: c for c, info in CROPS.items() for it in info.get("sua_items", [])}
FBS_ITEM_CROP = {it: c for c, info in CROPS.items() for it in info.get("fbs_items", [])}
SUA_CROPS = sorted(set(SUA_ITEMS.values()))
WORLD = 1
FUT = "future_MRI-ESM2-0_ssp245_2041-2060"
HIST = "historical_1971_2000"
P = lambda f: os.path.join(PROC, f)


def fix_area(name):
    """FAOSTAT files are read as latin-1 in 07_nutrition.py and 03_panels.py, which turns 'Türkiye' into 'TÃ¼rkiye' in
    every saved table (consistently, so name joins work). Repair the DISPLAY name only; never change the stored keys."""
    try:
        return str(name).encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return name


def latest_years(adequacy=None):
    adequacy = adequacy if adequacy is not None else pd.read_csv(P("adequacy.csv"))
    last = int(adequacy.Year.max())
    return list(range(last - 2, last + 1))


def baseline_items(years, countries=None):
    """Item-level supply per country: sum over `years` / len(years) (missing item-years = 0)."""
    sup = pd.read_pickle(P("nutrient_supply.pkl"))
    new = sup[(sup.method == "new") & sup.Year.isin(years)]
    if countries is not None:
        new = new[new.m49.isin(countries)]
    items = new.groupby(["m49", "Area", "Item"])[NUTRIENTS].sum() / len(years)
    items = items.reset_index()      # Area kept exactly as in the established tables (join key); fix_area() is for display only
    items["crop"] = items.Item.map(FBS_ITEM_CROP)
    sua = sup[(sup.method == "sua") & sup.Year.isin(years)]
    if countries is not None:
        sua = sua[sua.m49.isin(countries)]
    sua_items = (sua.groupby(["m49", "Item"])[NUTRIENTS].sum() / len(years)).reset_index()
    sua_items["crop"] = sua_items.Item.map(SUA_ITEMS)
    return items, sua_items


def crop_balance(years):
    """Mean 2021-23 balance per crop and country (as 09/16: means of crop_contrib rows) with SSR* and bounds."""
    cc = pd.read_csv(P("crop_contrib.csv"))
    b = cc[cc.Year.isin(years)].groupby(["crop", "m49"]).mean(numeric_only=True)
    ssr_star = np.where((b["dom"] <= 0) & (b["prod"] > 0), 1.0,
                        np.where(np.isfinite(b["ssr"]), np.clip(b["ssr"], 0.0, 1.0), 0.0))
    b["ssr_star"] = ssr_star
    return b


def quantity_fraction(loss, bal_row, bound="upper"):
    """Share of a crop's national supply removed by a domestic production loss `loss` (0..1)."""
    loss = max(0.0, float(loss))
    upper = loss * bal_row["ssr_star"]
    if bound == "upper":
        return upper
    lower = max(0.0, loss * bal_row["prod"] - bal_row["exp"]) / bal_row["dom"] if bal_row["dom"] > 0 else 0.0
    return min(upper, lower)


def apply_scenario(items_c, sua_c, qty_frac, conc_factor=None):
    """Remaining item-level supply for ONE country.
    items_c : FBS leaf items of the country (columns Item, crop, NUTRIENTS)
    sua_c   : SUA rows of the country (chickpea, lentil), indexed by crop
    qty_frac: {crop: fraction of the crop's national supply removed} (0..1)
    conc_factor: {(crop, nutrient): multiplicative concentration factor, e.g. 0.95 for -5 %}; applied to the
                 crop's ELIGIBLE items only (see eligible_items); absent keys = unchanged (scenario convention)
    Remaining = quantity remaining x concentration remaining (multiplicative). Returns (items, audit)."""
    conc_factor = conc_factor or {}
    out = items_c.copy()
    audit = {}
    for crop, f in qty_frac.items():
        if crop in SUA_CROPS:
            continue
        m = out.crop == crop
        for n in NUTRIENTS:
            out.loc[m, n] = out.loc[m, n] * (1.0 - f)
    for (crop, n), q in conc_factor.items():
        if crop in SUA_CROPS:
            continue
        m = out.Item.isin(eligible_items(crop))
        out.loc[m, n] = out.loc[m, n] * q
    # chickpea / lentil: remove from the parent FBS item; quantity and quality multiplicative on the SUA share
    pm = out.Item == PARENT_PULSES
    for crop in SUA_CROPS:
        f = qty_frac.get(crop, 0.0)
        if crop not in sua_c.index:
            if f > 0 or any(k[0] == crop for k in conc_factor):
                audit[f"{crop}_missing_sua"] = True
            continue
        for n in NUTRIENTS:
            base = float(sua_c.loc[crop, n])
            remaining = base * (1.0 - f) * conc_factor.get((crop, n), 1.0)
            removal = base - remaining
            if removal != 0.0:
                if not pm.any():
                    raise ValueError(f"{crop}: no parent item {PARENT_PULSES} to remove {n} from")
                out.loc[pm, n] = out.loc[pm, n] - removal
    if pm.any():
        audit["parent_min"] = float(out.loc[pm, NUTRIENTS].min(axis=1).iloc[0])
    return out, audit


def eligible_items(crop):
    """Items whose nutrient CONCENTRATION follows the crop's grain/seed CO2 response: the primary product
    (and its products) only -- never the extracted oil (no evidence transfers seed minerals to oil)."""
    return [it for it in CROPS[crop].get("fbs_items", []) if "Oil" not in it]


def diversity_metrics(items_c):
    """Per nutrient: total (unclipped sum, = national total), Shannon H over items with positive supply,
    effective number exp(H), largest source and its share. Zero contributions are dropped (0 log 0 = 0);
    negative item values (FBS balancing) are excluded from the shares, as in 21_india_hyderabad.py."""
    r = {}
    for n in NUTRIENTS:
        v = items_c[n].astype(float)
        r[f"total_{n}"] = float(v.sum())
        pos = v.clip(lower=0)
        p = pos / pos.sum()
        p = p[p > 0]
        H = float(-(p * np.log(p)).sum())
        r[f"H_{n}"] = H
        r[f"eff_{n}"] = float(np.exp(H))
        i = pos.idxmax()
        r[f"top_{n}"] = items_c.loc[i, "Item"]
        r[f"top_share_{n}"] = float(pos.max() / pos.sum())
    return r


def adequacy_metrics(totals, req):
    """NAR (capped at 1) and MAR from totals and the requirement row of adequacy.csv."""
    nar = {n: min(1.0, totals[f"total_{n}"] / req[f"req_{n}"]) for n in NUTRIENTS}
    out = {f"nar_{n}": v for n, v in nar.items()}
    out["MAR"] = float(np.mean(list(nar.values())))
    return out


def period_loss(df, crop):
    """Literature damage accounting of 16_future_yield_nutrition.py (identical formula)."""
    s_t, k_y = CROPS[crop]["heat_slope"], CROPS[crop]["ky"]
    heat = np.minimum(1.0, s_t * df.H_heat)
    water = np.minimum(1.0, k_y * df.H_water)
    return float((1 - (1 - heat) * (1 - water)).mean())


def future_yield_reference_periods():
    """Conditional yield change per pair under two reference conventions:
    hybrid (main, as in 16): 1971-2000 -> 2041-2060 (change factors on 1971-2000), applied to 2021-23 supply;
    present-relative (sensitivity): observed 2001-2024 -> 2041-2060, i.e. the modelled future level against
    the observed recent level, removing the part of the change that had already occurred by 2001-2024."""
    panels = pd.read_csv(P("panels.csv"))
    fs = pd.read_pickle(P("future_country_series.pkl"))
    cs = pd.read_pickle(P("country_series.pkl"))
    rows = []
    for _, p in panels.iterrows():
        g = fs[(fs.crop == p.crop) & (fs.m49 == p.m49)]
        o = cs[(cs.crop == p.crop) & (cs.m49 == p.m49)]
        l_hist = period_loss(g[g.scenario == HIST], p.crop)
        l_fut = period_loss(g[g.scenario == FUT], p.crop)
        l_obs = period_loss(o[o.year.between(*RECENT)], p.crop)
        l_obs_base = period_loss(o[o.year.between(*BASE)], p.crop)
        rows.append({"crop": p.crop, "country": p.country, "m49": p.m49,
                     "loss_1971_2000": l_hist, "loss_1971_2000_observed_series": l_obs_base,
                     "loss_2001_2024_observed": l_obs, "loss_2041_2060": l_fut,
                     "dY_hybrid_pct": -100.0 * (l_fut - l_hist) / max(1e-9, 1 - l_hist),
                     "dY_present_relative_pct": -100.0 * (l_fut - l_obs) / max(1e-9, 1 - l_obs),
                     "dY_already_observed_pct": -100.0 * (l_obs - l_hist) / max(1e-9, 1 - l_hist)})
    return pd.DataFrame(rows)
