"""
hyderabad_diet.py -- diet diversity and nutrient sources for Telangana (rural/urban) and the Hyderabad district,
from official survey indicators (data/external/india_hyderabad_indicators.csv; sources in docs/evidence/india_hyderabad_sources.md).
HCES/NSS are state-level rural/urban, so Telangana-URBAN stands in for Hyderabad city; NFHS-5 has a Hyderabad
DISTRICT fact sheet. Called from 21_india_hyderabad.py; returns LaTeX macro values and writes result tables.
"""
import os

import numpy as np
import pandas as pd

from config import CROPS, FE_REQ, PROC, ROOT_DIR, ZN_REQ

DIET_CSV = os.path.join(ROOT_DIR, "data", "external", "india_hyderabad_indicators.csv")
P = lambda f: os.path.join(PROC, f)

# HCES item pattern -> (IFCT 2017 food code, grouping). IFCT codes are the exact foods in the indicators table.
COMPOSITION = {
    "rice": (r"^rice - ", "A015", "rice"),
    "wheat": (r"^wheat( - |/atta - )", "A019", "wheat"),
    "jowar": (r"^jowar", "A005", "other cereal"),
    "bajra": (r"^bajra", "A003", "other cereal"),
    "ragi": (r"^ragi", "A010", "other cereal"),
    "maize": (r"^maize", "A006", "maize"),
    "tur": (r"^arhar", "B021", "tur"),
    "moong": (r"^moong", "B010", "moong"),
    "masur": (r"^masur", "B013", "lentil"),
    "gram_split": (r"^gram \(split", "B001", "chickpea"),
    "gram_whole": (r"^gram \(whole", "B002", "chickpea"),
    "besan": (r"^besan", "B001", "chickpea"),
    "groundnut": (r"^groundnut$", "H012", "groundnut"),
}
STUDY = ["rice", "wheat", "chickpea", "lentil", "maize", "groundnut"]


def run(prof, tg):
    d = pd.read_csv(DIET_CSV)
    d["v"] = pd.to_numeric(d.value.astype(str).str.replace(r"[()*,]", "", regex=True), errors="coerce")
    out = {}
    q = d[(d.source_short == "HCES2324_A10S") & (d.indicator == "Monthly per capita quantity consumed")]

    def qty(geo, sec, pattern):
        m = q[(q.geography == geo) & (q.sector == sec) & q.item.str.contains(pattern, case=False, regex=True, na=False)]
        return m.v.sum()

    # A. staple basket, kg per person per 30 days (HCES 2023-24)
    rows = []
    for geo in ("Telangana", "All-India"):
        for sec in ("urban", "rural"):
            r = {"geography": geo, "sector": sec}
            for lab, pat in (("rice", r"^rice - "), ("wheat_atta", r"^wheat( - |/atta - )"), ("tur", r"^arhar"), ("moong", r"^moong"),
                             ("masur_lentil", r"^masur"), ("gram_chickpea", r"^(gram \(|besan)"), ("groundnut_kernel", r"^groundnut$")):
                r[lab] = qty(geo, sec, pat)
            r["pulses_listed"] = r["tur"] + r["moong"] + r["masur_lentil"] + r["gram_chickpea"]
            rows.append(r)
    basket = pd.DataFrame(rows)
    basket.to_csv(P("hyderabad_staple_basket.csv"), index=False)
    bt = basket.set_index(["geography", "sector"])
    for geo, g in (("Telangana", "Tg"), ("All-India", "In")):
        for sec in ("urban", "rural"):
            S = sec.capitalize()
            for lab, nm in (("rice", "Rice"), ("wheat_atta", "Wheat"), ("pulses_listed", "Pulses")):
                out[f"hq{g}{S}Kg{nm}"] = f"{bt.loc[(geo, sec), lab]:.2f}"
            out[f"hq{g}{S}RiceToWheat"] = f"{bt.loc[(geo, sec), 'rice'] / bt.loc[(geo, sec), 'wheat_atta']:.1f}"
            for lab, nm in (("gram_chickpea", "Chick"), ("masur_lentil", "Lentil"), ("tur", "Tur"), ("moong", "Moong")):
                out[f"hq{g}{S}Share{nm}"] = f"{100 * bt.loc[(geo, sec), lab] / bt.loc[(geo, sec), 'pulses_listed']:.0f}"

    # B. iron and zinc from the listed grains and pulses = quantity x IFCT 2017 composition
    ifct = d[d.source_short == "IFCT2017"].copy()
    ifct["code"] = ifct["item"].str.split().str[0]
    fe = ifct[ifct.indicator.str.startswith("Iron")].set_index("code").v
    zn = ifct[ifct.indicator.str.startswith("Zinc")].set_index("code").v
    irows = []
    for geo in ("Telangana", "All-India"):
        for sec in ("urban", "rural"):
            for k, (pat, code, grp) in COMPOSITION.items():
                gday = qty(geo, sec, pat) * 1000 / 30.0
                irows.append({"geography": geo, "sector": sec, "food": k, "group": grp, "g_per_day": gday, "ifct_code": code,
                              "iron_mg_per_100g": fe[code], "zinc_mg_per_100g": zn[code],
                              "iron_mg_day": gday * fe[code] / 100, "zinc_mg_day": gday * zn[code] / 100})
    ir = pd.DataFrame(irows)
    ir.to_csv(P("hyderabad_iron_zinc_from_listed_foods.csv"), index=False)
    for geo, g in (("Telangana", "Tg"), ("All-India", "In")):
        for sec in ("urban", "rural"):
            S = sec.capitalize()
            x = ir[(ir.geography == geo) & (ir.sector == sec)]
            tot_fe, tot_zn = x.iron_mg_day.sum(), x.zinc_mg_day.sum()
            out[f"hq{g}{S}FeListed"] = f"{tot_fe:.1f}"; out[f"hq{g}{S}ZnListed"] = f"{tot_zn:.1f}"
            out[f"hq{g}{S}FeReq"] = f"{100 * tot_fe / FE_REQ:.0f}"; out[f"hq{g}{S}ZnReq"] = f"{100 * tot_zn / ZN_REQ:.0f}"
            byg = x.groupby("group").iron_mg_day.sum() / tot_fe
            for grp, nm in (("rice", "Rice"), ("wheat", "Wheat"), ("chickpea", "Chickpea"), ("lentil", "Lentil"), ("maize", "Maize"),
                            ("groundnut", "Groundnut"), ("other cereal", "OtherCereal"), ("tur", "Tur"), ("moong", "Moong")):
                out[f"hq{g}{S}Fe{nm}"] = f"{100 * byg.get(grp, 0):.0f}"
            out[f"hq{g}{S}FeStudy"] = f"{100 * x[x.group.isin(STUDY)].iron_mg_day.sum() / tot_fe:.0f}"

    # C. Telangana climate-driven yield change (period-mean stress x literature response) and its iron consequence
    t = tg.set_index("crop")
    ind = prof.set_index("crop")
    dY = {}
    for c in ("rice", "maize", "chickpea", "groundnut"):
        if t.loc[c, "telangana_area_ha"] > 0:
            sT, ky = CROPS[c]["heat_slope"], CROPS[c]["ky"]

            def loss(lh, lw):
                return 1 - (1 - min(1, sT * lh)) * (1 - min(1, ky * lw))
            l0 = loss(t.loc[c, "L_heat_1971_2000"], t.loc[c, "L_water_1971_2000"])
            l1 = loss(t.loc[c, "L_heat_2041_2060"], t.loc[c, "L_water_2041_2060"])
            dY[c] = -100 * (l1 - l0) / (1 - l0)
    route = {"rice": ("Telangana", dY["rice"]), "maize": ("Telangana", dY["maize"]), "chickpea": ("Telangana", dY["chickpea"]),
             "groundnut": ("Telangana", dY["groundnut"]), "wheat": ("India", ind.loc["wheat", "dY_lit_pct"]),
             "lentil": ("India", ind.loc["lentil", "dY_lit_pct"])}
    for c, (rt, v) in route.items():
        out[f"hqdY{c.capitalize()}"] = f"{v:+.1f}"
    pd.DataFrame([{"crop": c, "route": rt, "dY_lit_pct": v} for c, (rt, v) in route.items()]).to_csv(P("hyderabad_future_yield_by_route.csv"), index=False)
    for sec in ("urban", "rural"):
        x = ir[(ir.geography == "Telangana") & (ir.sector == sec)]
        sh = x.groupby("group").iron_mg_day.sum() / x.iron_mg_day.sum()
        out[f"hqIronChange{sec.capitalize()}"] = f"{sum(sh.get(c, 0) * v for c, (_, v) in route.items()):+.2f}"
        for c in ("wheat", "rice", "chickpea"):
            out[f"hqIronTen{c.capitalize()}{sec.capitalize()}"] = f"{10 * sh.get(c, 0):.1f}"

    # D. intake, protein-source diversity (Shannon over the MoSPI food groups), cereal share of energy, food-group frequency
    pg = d[(d.source_short == "NSS594") & (d.indicator == "% share of protein intake by food group") & d.period.str.contains("2023-24")]
    kc = d[(d.source_short == "NSS594") & (d.indicator == "% of calorie intake from cereals") & d.period.str.contains("2023-24")]
    nr = d[(d.source_short == "NSS594") & d.period.str.contains("2023-24") & d.geography.isin(["Telangana", "All-India"])]
    for geo, g in (("Telangana", "Tg"), ("All-India", "In")):
        for sec in ("urban", "rural"):
            S = sec.capitalize()
            x = pg[(pg.geography == geo) & (pg.sector == sec)]
            p = x.v.values / x.v.sum()
            out[f"hqProtEff{g}{S}"] = f"{np.exp(-(p * np.log(p)).sum()):.2f}"
            for grp, nm in (("cereals", "Cereal"), ("egg, fish & meat", "Animal"), ("milk & milk products", "Milk"), ("pulses", "Pulse")):
                out[f"hqProt{nm}{g}{S}"] = f"{x[x['item'] == grp].v.iloc[0]:.1f}"
            out[f"hqKcalCereal{g}{S}"] = f"{kc[(kc.geography == geo) & (kc.sector == sec)].v.iloc[0]:.1f}"
            for ind_, nm in (("Average daily calorie intake per capita", "Kcal"), ("Average daily protein intake per capita", "Prot"),
                             ("Average daily fat intake per capita", "Fat")):
                out[f"hqIntake{nm}{g}{S}"] = f"{nr[(nr.indicator == ind_) & (nr.geography == geo) & (nr.sector == sec)].v.iloc[0]:g}"
    fr = d[(d.source_short == "NFHS5_TG_REP") & d.indicator.str.startswith("Frequency") & (d.sex_age_group == "women 15-49") & (d.geography == "Telangana")]
    wk = fr[fr.indicator.str.contains("daily|weekly")].groupby("item").v.sum()
    dl = fr[fr.indicator.str.contains("daily")].set_index("item").v
    names = {"Milk or curd": "Milk", "Pulses or beans": "Pulses", "Dark green leafy vegetables": "Leafy", "Fruits": "Fruit", "Eggs": "Egg",
             "Fish": "Fish", "Chicken or meat": "Meat"}
    for it, nm in names.items():
        out[f"hqWeekly{nm}"] = f"{wk[it]:.0f}"; out[f"hqDaily{nm}"] = f"{dl[it]:.0f}"
    pd.DataFrame({"food": list(names), "daily_or_weekly_pct": [wk[i] for i in names], "daily_pct": [dl[i] for i in names]}
                 ).to_csv(P("hyderabad_nfhs_food_frequency_women.csv"), index=False)

    # E. nutrition status: Hyderabad district vs Telangana vs India (NFHS-5)
    h = d[d.source_short == "NFHS5_HYD_DFS"]
    hv = lambda pat: h[h.indicator.str.contains(pat, regex=True)].v
    out["hydAnaemChild"] = f"{hv(r'<11.0 g/dl').iloc[0]:g}"
    out["hydAnaemNPW"] = f"{hv(r'<12.0 g/dl').iloc[0]:g}"
    out["hydStunted"] = f"{hv('Stunted').iloc[0]:g}"; out["hydBmiLow"] = f"{hv('BMI below').iloc[0]:g}"
    out["hydOverweight"] = f"{hv('Overweight or obese').iloc[0]:g}"
    s5 = d[(d.source_short == "NFHS5_TG_FS") & d.indicator.str.startswith("NFHS-5") & (d.sector == "total")]
    gv = lambda pat, sex: s5[s5.indicator.str.contains(pat, regex=True) & (s5.sex_age_group == sex)].v.iloc[0]
    out["tgAnaemChild"] = f"{gv('Anaemic .<11.0', 'children 6-59 months'):g}"
    out["tgAnaemNPW"] = f"{gv('Anaemic .<12.0', 'non-pregnant women 15-49'):g}"
    out["tgBmiLow"] = f"{gv('BMI below', 'women 15-49'):g}"; out["tgOverweight"] = f"{gv('Overweight or obese', 'women 15-49'):g}"
    out["tgStunted"] = f"{gv('Stunted', 'children under 5 years'):g}"
    i5 = d[(d.source_short == "NFHS5_IN_FS") & d.indicator.str.startswith("NFHS-5") & (d.sector == "total")]
    ig = lambda pat, sex: i5[i5.indicator.str.contains(pat, regex=True) & (i5.sex_age_group == sex)].v.iloc[0]
    out["inAnaemNPW"] = f"{ig('Anaemic .<12.0', 'non-pregnant women 15-49'):g}"; out["inOverweight"] = f"{ig('Overweight or obese', 'women 15-49'):g}"
    c = d[(d.source_short == "CNNS_TG_FS")]
    for pat, nm in (("ferritin", "Iron"), ("zinc deficiency", "Zinc")):
        for age, a in (("children 1-4 years", "CFour"), ("children 5-9 years", "CNine"), ("adolescents 10-19 years", "Adol")):
            out[f"cnns{nm}{a}"] = f"{c[c.indicator.str.contains(pat) & (c.sex_age_group == age)].v.iloc[0]:g}"

    # F. Telangana paddy area: state statistics 2023-24 vs the 2010 SPAM map
    paddy = d[(d.source_short == "TG_DES_AAG2024") & (d.indicator == "Crop area") & (d["item"] == "Paddy")].v
    des_mha = paddy.iloc[2] * 1000 * 0.404686 / 1e6
    out["tgPaddyAreaMha"] = f"{des_mha:.2f}"
    out["tgPaddySpamMha"] = f"{t.loc['rice', 'telangana_area_ha'] / 1e6:.2f}"
    out["tgPaddyGrowth"] = f"{des_mha * 1e6 / t.loc['rice', 'telangana_area_ha']:.1f}"
    return out
