"""
19_endeval_tex.py -- LaTeX macros and tables for the end-evaluation report, slides and appendix,
generated from the saved result tables (no hand-typed result values) -> docs/nine_crop/generated/
"""
import os

import numpy as np
import pandas as pd

from config import CROP_GROUPS, CROP_ORDER, CROPS, PROC, ROOT_DIR, TEX

GEN = os.path.join(TEX, "generated")
os.makedirs(GEN, exist_ok=True)
F4 = "F4_hazard_paired"
CR = [c for c in CROP_ORDER if c in CROPS]
LAB = {c: CROPS[c]["label"] for c in CROPS}
SHORT = {"United States of America": "USA", "China, mainland": "China", "Russian Federation": "Russia",
         "United Republic of Tanzania": "Tanzania", "Türkiye": "Turkey", "Iran (Islamic Republic of)": "Iran"}
def sh(s):
    """FAOSTAT area names are UTF-8 but were read as latin-1 upstream: repair, then shorten to ASCII."""
    if isinstance(s, str) and "Ã" in s:
        s = s.encode("latin-1").decode("utf-8")
    return SHORT.get(s, s)
GROUP_NAME = {"cereal": "Cereals", "pulse": "Pulses", "oilseed": "Oilseeds"}
P = lambda f: os.path.join(PROC, f)
macros = []


DIGITS = dict(zip("0123456789", ["Zero", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine"]))


def mac(name, value):
    name = "".join(DIGITS.get(ch, ch) for ch in name if ch.isalnum())
    macros.append(f"\\newcommand{{\\{name}}}{{{value}}}")


def f4(v, d=4):
    return r"$<$0.0001" if 0 < v < 1e-4 else f"{v:.{d}f}"


def write(name, body):
    with open(os.path.join(GEN, name), "w", encoding="utf-8") as fh:
        fh.write(body)


def tabular(cols, header, rows, note=None):
    out = "\\begin{tabular}{" + cols + "}\n\\toprule\n" + " & ".join(header) + " \\\\\n\\midrule\n"
    out += "\n".join(" & ".join(str(x) for x in r) + " \\\\" for r in rows)
    out += "\n\\bottomrule\n\\end{tabular}\n"
    if note:   # table scaled to the text width, note set underneath at the same width
        out = ("\\begin{minipage}{\\textwidth}\\centering\n\\adjustbox{max width=\\textwidth}{" + out + "}\n"
               "\\par\\vspace{2pt}{\\footnotesize " + note + "}\n\\end{minipage}\n")
    return out


def main():
    comp = pd.read_csv(P("index_components.csv"))
    crop = pd.read_csv(P("index_crop.csv")).set_index("crop")
    ref = pd.read_csv(P("index_reference.csv")).set_index("quantity")
    panels = pd.read_csv(P("panels.csv"))

    # ---- present ranking ----
    mac("nPairs", len(comp)); mac("nCountries", comp.country.nunique()); mac("nCrops", len(CROPS))
    for wt, nm in (("eq", "Eq"), ("pw", "Pw")):
        order = crop[f"{F4}_{wt}"].sort_values(ascending=False)
        mac(f"order{nm}", " $>$ ".join(LAB[c] for c in order.index))
        mac(f"top{nm}", LAB[order.index[0]]); mac(f"second{nm}", LAB[order.index[1]]); mac(f"last{nm}", LAB[order.index[-1]])
        mac(f"top{nm}Value", f4(order.iloc[0])); mac(f"second{nm}Value", f4(order.iloc[1]))
    rows = []
    for c in crop.sort_values(f"{F4}_eq", ascending=False).index:
        r = crop.loc[c]
        rows.append([LAB[c], GROUP_NAME[CROPS[c]["group"]], int((comp.crop == c).sum()), f"{r.E_heat_eq:.2f}", f"{r.E_water_eq:.2f}",
                     f"{r.S_heat_eq:.2f}", f"{r.S_water_eq:.2f}", f"{r.In_eq:.2f}", f4(r[f'{F4}_eq']), int(r[f'rank_{F4}_eq']),
                     f4(r[f'{F4}_pw']), int(r[f'rank_{F4}_pw'])])
    write("tab_crop_index9.tex", tabular("llrrrrrrrrrr", ["Crop", "Group", "n", r"$E_T$", r"$E_P$", r"$S_T$", r"$S_P$", r"$\tilde I$",
                                                           r"F4 eq", "rank", r"F4 pw", "rank"], rows,
                                         "Component columns are equal-weighted means over the crop's panel countries. eq = equal country weights; pw = production-weighted (FAOSTAT 2020--24)."))
    top = comp.sort_values(F4, ascending=False).head(6)
    for i, (_, r) in enumerate(top.iterrows(), 1):
        mac(f"topPair{'ABCDEF'[i-1]}", f"{LAB[r.crop].lower()}--{sh(r.country)}")
        mac(f"topPair{'ABCDEF'[i-1]}Value", f4(r[F4]))
    mac("refHeatPair", f"{LAB[ref.loc['H_heat','crop']].lower()}--{sh(ref.loc['H_heat','country'])}"); mac("refHeat", f"{ref.loc['H_heat','max_value']:.3f}")
    mac("refWaterPair", f"{LAB[ref.loc['H_water','crop']].lower()}--{sh(ref.loc['H_water','country'])}"); mac("refWater", f"{ref.loc['H_water','max_value']:.3f}")
    mac("refImpPair", f"{LAB[ref.loc['I','crop']].lower()}--{sh(ref.loc['I','country'])}"); mac("refImp", f"{ref.loc['I','max_value']:.3f}")

    # ---- country x crop matrix ----
    m = comp.pivot_table(index="country", columns="crop", values=F4).reindex(columns=CR)
    m = m.loc[m.max(axis=1).sort_values(ascending=False).index]
    rows = [[sh(k)] + [("--" if np.isnan(v) else f4(v)) for v in m.loc[k]] for k in m.index]
    write("tab_country_crop9.tex", tabular("l" + "r" * len(CR), ["Country"] + [LAB[c].replace("Rapeseed-mustard", "Rapeseed") for c in CR], rows,
                                           "-- = country not in the crop's panel. Values: F4, 2001--2024 stress level, literature-only sensitivity."))

    # ---- groups ----
    if os.path.exists(P("index_group.csv")):
        g = pd.read_csv(P("index_group.csv")).set_index("group")
        fut = pd.read_csv(P("future_group.csv")).set_index("group") if os.path.exists(P("future_group.csv")) else None
        rows = []
        for grp in CROP_GROUPS:
            r = g.loc[grp]
            row = [GROUP_NAME[grp], ", ".join(LAB[c] for c in CROP_GROUPS[grp]), f4(r.F4_hazard_paired_eq), f"{f4(r.F4_hazard_paired_eq_min)}--{f4(r.F4_hazard_paired_eq_max)}", f4(r.F4_hazard_paired_pw)]
            if fut is not None:
                row += [f4(fut.loc[grp, "F4_eq_historical_1971_2000"]), f4(fut.loc[grp, "F4_eq_future_2041_2060"])]
            rows.append(row)
        hdr = ["Group", "Crops", "mean F4 eq", "crop range", "mean F4 pw"] + (["1971--2000", "2041--2060"] if fut is not None else [])
        write("tab_groups.tex", tabular("ll" + "r" * (len(hdr) - 2), hdr, rows, "Group value = simple mean of the three selected crops; it describes these crops, not every cereal, pulse or oilseed."))
        og = g["F4_hazard_paired_eq"].sort_values(ascending=False)
        mac("groupOrder", " $>$ ".join(GROUP_NAME[x] for x in og.index))

    # ---- facts quoted in the text (so no result value is typed by hand) ----
    div = pd.read_csv(P("food_supply_diversity.csv"))
    mac("nDivUnits", len(div))
    for n in ("zinc", "iron", "protein", "kcal"):
        mac(f"wheatTop{n.capitalize()}", int((div[f"top_source_{n}"] == "Wheat and products").sum()))
    mz = comp[comp.crop == "maize"].set_index("country")
    use = pd.read_csv(P("crop_use_shares.csv"))
    mac("maizeSAkcal", f"{100 * mz.loc['South Africa', 'sh_kcal']:.0f}"); mac("maizeSArainfed", f"{100 * mz.loc['South Africa', 'rainfed_share']:.0f}")
    mac("maizeSAEwater", f"{mz.loc['South Africa', 'E_water']:.2f}"); mac("maizeUAEwater", f"{mz.loc['Ukraine', 'E_water']:.2f}")
    for area, nm in (("United States of America", "USA"), ("China, mainland", "China"), ("South Africa", "SA")):
        mac(f"maizeFood{nm}", f"{use[(use.crop == 'maize') & (use.Area == area)].food.iloc[0]:.0f}")
    if os.path.exists(P("future_components.csv")):
        fcp = pd.read_csv(P("future_components.csv"))
        tot = fcp.dF4_from_heat.sum() + fcp.dF4_from_water.sum()
        mac("futHeatShare", f"{100 * fcp.dF4_from_heat.sum() / tot:.0f}"); mac("futWaterShare", f"{100 * fcp.dF4_from_water.sum() / tot:.0f}")
        mac("nPairsDown", int((fcp.dF4_abs < 0).sum()))
        mac("nPairsDownWaterOnly", int(((fcp.dF4_abs < 0) & (fcp.dF4_from_water < 0)).sum()))

    # ---- parameters (from config.py, no hand-typed values) ----
    from config import season_kc
    smax = max(CROPS[c]["heat_slope"] for c in CROPS); kmax = max(CROPS[c]["ky"] for c in CROPS)
    short_src = {"rice": "Yoshida 1981; Jagadish 2007", "wheat": "Deryng 2014", "maize": "Deryng 2014", "soybean": "Deryng 2014",
                 "chickpea": "Bhandari 2020 (fit)", "lentil": "Bhandari 2020 (fit)", "bean": "Prasad 2002 (fit)",
                 "groundnut": "Prasad 2003 (fit)", "rapeseed": "Morrison 2002; slope proxy"}
    rows = []
    for c in CR:
        i = CROPS[c]
        tl = "--" if c == "rice" else f"{(i.get('tlim') or i['tcrit'] + 1 / i['heat_slope']):.1f}"
        rows.append([LAB[c], f"{i['tcrit']:.1f}", tl, f"{i['heat_slope']:.3f}", f"{i['heat_slope'] / smax:.2f}", f"{i['ky']:.2f}",
                     f"{i['ky'] / kmax:.2f}", f"{season_kc(c):.2f}", short_src.get(c, "")])
    write("tab_params9.tex", tabular("lrrrrrrrl", [r"Crop", r"$T_{crit}$", r"$T_{lim}$", r"$s_T$ (/\si{\celsius})", r"$S_T$", r"$K_y$", r"$S_P$", r"$\bar K_c$", "heat source"], rows,
                                     r"$T_{crit}$, $T_{lim}$ in \si{\celsius} of $T_{eff}$. Rice $K_y$ is a proxy (FAO gives none); lentil $K_y$ and the rapeseed slope are proxies; new-crop heat values are fits to chamber or field data (docs/literature\_verification\_new\_crops.md)."))

    # ---- panels ----
    rows = []
    for c in CR:
        p = panels[panels.crop == c].sort_values("rank")
        rows.append([LAB[c], ", ".join(f"{sh(k)}{'*' if s else ''}" for k, s in zip(p.country, p.small_producer)), f"{p.share_pct.sum():.0f}"])
    write("tab_panels9.tex", tabular("lp{10.5cm}r", ["Crop", "Countries (world rank order; * = <0.5\\% of world output)", "\\% world"], rows))

    # ---- future ----
    if os.path.exists(P("future_crop.csv")):
        fc = pd.read_csv(P("future_crop.csv")).set_index("crop")
        fcomp = pd.read_csv(P("future_components.csv"))
        rows = []
        for c in fc.sort_values("F4_eq_future_2041_2060", ascending=False).index:
            r = fc.loc[c]
            pct = "n/a" if np.isnan(r.pct_eq) else f"{r.pct_eq:+.0f}\\%"
            rows.append([LAB[c], f"{r.dTeff_C_eq:+.1f}", f4(r.F4_eq_present_2001_2024), f4(r.F4_eq_historical_1971_2000), f4(r.F4_eq_future_2041_2060),
                         f"{r.dF4_eq:+.4f}", pct, f"{int(r.rank_eq_historical_1971_2000)}$\\to${int(r.rank_eq_future_2041_2060)}",
                         f"{int(r.pairs_with_higher_F4)}/{int(r.n_pairs)}", f4(r.F4_pw_future_2041_2060), f"{int(r.rank_pw_historical_1971_2000)}$\\to${int(r.rank_pw_future_2041_2060)}"])
        write("tab_future_crop.tex", tabular("lrrrrrrcrrc", ["Crop", r"$\Delta T_{eff}$", "2001--24", "1971--2000", "2041--60", r"$\Delta$F4", r"\%", "rank eq", "pairs up",
                                                             "F4 pw 2041--60", "rank pw"], rows,
                                             r"MRI-ESM2-0, SSP2-4.5, change factors on 1971--2000 years; one fixed normalisation reference (2001--24 nine-crop maxima); sensitivity, importance, crop area, irrigation and calendars held fixed. $\Delta T_{eff}$ = mean change in flowering-window effective temperature (\si{\celsius}). \% only where the historical score is $\geq$1\% of the largest."))
        fo = fc["F4_eq_future_2041_2060"].sort_values(ascending=False)
        ho = fc["F4_eq_historical_1971_2000"].sort_values(ascending=False)
        mac("futOrderEq", " $>$ ".join(LAB[c] for c in fo.index)); mac("histOrderEq", " $>$ ".join(LAB[c] for c in ho.index))
        mac("futOrderPw", " $>$ ".join(LAB[c] for c in fc["F4_pw_future_2041_2060"].sort_values(ascending=False).index))
        mac("nPairsUp", int((fcomp.dF4_abs > 0).sum())); mac("nPairsExceedRef", int(fcomp.exceeds_reference.sum()))
        mac("meanDTeff", f"{fcomp.dTeff_C.mean():.1f}")
        big = fcomp.sort_values("dF4_abs", ascending=False).head(8)
        rows = [[f"{LAB[r.crop]}--{sh(r.country)}", f4(r.F4_hazard_paired_historical_1971_2000), f4(r.F4_hazard_paired_future_2041_2060), f"{r.dF4_abs:+.4f}",
                 ("n/a" if np.isnan(r["pct_change"]) else f"{r["pct_change"]:+.0f}\\%"), f"{r.dF4_from_heat:+.4f}", f"{r.dF4_from_water:+.4f}", f"{r.dTeff_C:+.1f}"]
                for _, r in big.iterrows()]
        write("tab_future_pairs.tex", tabular("lrrrrrrr", ["Pair", "1971--2000", "2041--60", r"$\Delta$F4", r"\%", "from heat", "from water", r"$\Delta T_{eff}$"], rows,
                                              "Largest increases. 'from heat/water' = the change in each hazard term (future sensitivity and importance, fixed)."))
        b1 = big.iloc[0]
        mac("futTopPair", f"{LAB[b1.crop].lower()}--{sh(b1.country)}"); mac("futTopPairChange", f"{b1.dF4_abs:+.4f}")
        cc = pd.read_csv(P("future_clim_check.csv"))
        mac("climCheckSameSign", f"{100 * cc.same_sign.mean():.0f}"); mac("climCheckRho", f"{cc[['dF4_abs', 'dF4_clim']].corr('spearman').iloc[0, 1]:.2f}")
        chk = pd.read_csv(P("future_check_hist_vs_main.csv")).set_index("variable")
        mac("histReproMaxDiff", f"{chk.max_abs_diff.max():.1e}")

    # ---- yield -> diet (standard shock, nine crops) ----
    sc = pd.read_csv(P("yield_diet_scenarios.csv"))
    s3 = sc[sc.scenario.str.startswith("S3")].sort_values("dMAR_pts_upper")
    rows = [[f"{LAB[r.crop]}--{sh(r.country)}", f"{min(1, r.ssr):.2f}", f"{r.dkcal_pct_upper:+.2f}", f"{r.dprotein_pct_upper:+.2f}", f"{r.dzinc_pct_upper:+.2f}",
             f"{r.diron_pct_upper:+.2f}", f"{100 * r.MAR_base:.1f}", f"{r.dMAR_pts_upper:+.2f}", f"{r.dMAR_pts_lower:+.2f}"] for _, r in s3.head(12).iterrows()]
    write("tab_shock9.tex", tabular("lrrrrrrrr", ["Pair", "min(1,SSR)", r"$\Delta$kcal \%", r"$\Delta$prot \%", r"$\Delta$Zn \%", r"$\Delta$Fe \%", "MAR", r"$\Delta$MAR", "w/ exports"], rows,
                                      "Standard $-10\\%$ yield shock, no market response; national supply 2021--23. MAR and $\\Delta$MAR in points out of 100. 'w/ exports' = exports absorb the loss first."))
    kc = s3.sort_values("dkcal_pct_upper").iloc[0]
    mac("shockTopMar", f"{LAB[s3.iloc[0].crop].lower()}--{sh(s3.iloc[0].country)}"); mac("shockTopMarValue", f"{s3.iloc[0].dMAR_pts_upper:+.2f}")
    mac("shockTopKcal", f"{LAB[kc.crop].lower()}--{sh(kc.country)}"); mac("shockTopKcalValue", f"{kc.dkcal_pct_upper:+.1f}")
    mac("shockZeroMar", int((s3.dMAR_pts_upper > -0.005).sum())); mac("shockN", len(s3))

    # pass-through
    hist = pd.read_csv(P("yield_diet_historical.csv"))
    for era in ("old", "new"):
        h = hist[hist.fbs == era]
        mac(f"pass{era.capitalize()}N", len(h)); mac(f"pass{era.capitalize()}Pos", int(((h.beta_kcal > 0) & (h.p_kcal < 0.05)).sum()))

    # adequacy and requirement sensitivity
    adq = pd.read_csv(P("adequacy.csv"))
    last = int(adq.Year.max())
    a = adq[adq.Year.between(last - 2, last) & adq.m49.isin(comp.m49.unique())].groupby("Area").mean(numeric_only=True)
    rows = [[sh(k), f"{r.nar_kcal:.2f}", f"{r.nar_protein:.2f}", f"{r.nar_fat:.2f}", f"{r.nar_zinc:.2f}", f"{r.nar_iron:.2f}", f"{100 * r.MAR:.1f}",
             f"{r.nar_zinc_moderate:.2f}", f"{r.nar_iron_15pct:.2f}", f"{100 * r.MAR_moderate_bioavailability:.1f}"] for k, r in a.sort_values("MAR").iterrows()]
    write("tab_adequacy9.tex", tabular("lrrrrrrrrr", ["Country", "kcal", "protein", "fat", "Zn", "Fe", "MAR", "Zn mod.", "Fe 15\\%", "MAR alt"], rows,
                                         "NAR = min(1, national supply / requirement), 2021--23. Main: zinc low bioavailability, iron 10\\% bioavailability (WHO/FAO 2004 RNIs). Alternative: moderate zinc, 15\\% iron. RNIs are individual upper-percentile requirements compared with national mean supply, so both overstate shortfall."))
    mac("nIronShort", int((a.nar_iron < 1).sum())); mac("nIronShortAlt", int((a.nar_iron_15pct < 1).sum()))
    mac("nZincShort", int((a.nar_zinc < 1).sum())); mac("nZincShortAlt", int((a.nar_zinc_moderate < 1).sum()))
    mac("nAdqCountries", len(a))

    # ---- future nutrition ----
    if os.path.exists(P("future_nutrition.csv")):
        fy = pd.read_csv(P("future_yield.csv"))
        fn = pd.read_csv(P("future_nutrition.csv"))
        main_fn = fn[fn.model.str.startswith("literature")].sort_values("dMAR_pts_upper")
        rows = [[f"{LAB[r.crop]}--{sh(r.country)}", f"{r.dY_pct:+.1f}", f"{fy[(fy.crop == r.crop) & (fy.country == r.country)].dY_emp_pct.iloc[0]:+.1f}",
                 f"{r.dkcal_pct_upper:+.2f}", f"{r.diron_pct_upper:+.2f}", f"{r.dMAR_pts_upper:+.2f}", f"{r.dMAR_pts_lower:+.2f}"] for _, r in main_fn.head(10).iterrows()]
        write("tab_future_nutrition.tex", tabular("lrrrrrr", ["Pair", r"$\Delta Y$ lit \%", r"$\Delta Y$ emp \%", r"$\Delta$kcal \%", r"$\Delta$Fe \%", r"$\Delta$MAR", "w/ exports"], rows,
                                                  "Conditional screening estimate: change in climate-attributable loss (heat: $s_T \\cdot$ \\si{\\celsius} above $T_{crit}$; water: $K_y \\cdot$ rainfed deficit), 2041--60 vs 1971--2000, MRI-ESM2-0 SSP2-4.5; no CO$_2$ fertilisation, adaptation or market response. Only losses propagated."))
        by = fy.groupby("crop").agg(lit=("dY_lit_pct", "mean"), emp=("dY_emp_pct", "mean"), lo=("dY_lit_pct", "min"), hi=("dY_lit_pct", "max"), dT=("dTeff_C", "mean"))
        rows = [[LAB[c], f"{by.loc[c, 'dT']:+.1f}", f"{by.loc[c, 'lit']:+.1f}", f"{by.loc[c, 'lo']:+.1f} to {by.loc[c, 'hi']:+.1f}", f"{by.loc[c, 'emp']:+.1f}"] for c in CR]
        write("tab_future_yield.tex", tabular("lrrrr", ["Crop", r"$\Delta T_{eff}$ \si{\celsius}", r"$\Delta Y$ lit (mean \%)", "range over countries", r"$\Delta Y$ empirical (mean \%)"], rows))
        mac("futYieldWorst", f"{LAB[by.lit.idxmin()]}"); mac("futYieldWorstValue", f"{by.lit.min():+.1f}")
        mac("futNutTopPair", f"{LAB[main_fn.iloc[0].crop].lower()}--{sh(main_fn.iloc[0].country)}"); mac("futNutTopMar", f"{main_fn.iloc[0].dMAR_pts_upper:+.2f}")
        mac("corrLitEmp", f"{fy[['dY_lit_pct', 'dY_emp_pct']].corr('spearman').iloc[0, 1]:.2f}")

    # ---- robustness ----
    rob = pd.read_csv(P("index_robustness.csv"))
    r4 = rob[rob.form == F4]
    top_crop = crop[f"{F4}_eq"].idxmax()
    mac("robN", len(rob)); mac("robTopAll", int((rob.top == top_crop).sum())); mac("robTopFfour", int((r4.top == top_crop).sum())); mac("robNFfour", len(r4))
    rows = []
    for test, g in r4.groupby("test", sort=False):
        e, p = g[g.weighting == "eq"].iloc[0], g[g.weighting == "pw"].iloc[0]
        rows.append([test.replace("_", " ").replace("%", "\\%"), " $>$ ".join(LAB[c][:5] for c in e.order.split(" > ")[:3]) + " \\ldots",
                     int(e[f"rank_{top_crop}"]), int(p[f"rank_{top_crop}"])])
    write("tab_robust9.tex", tabular("p{6.8cm}p{5.2cm}cc", ["Test (one at a time)", "Top three, F4 equal weights", f"{LAB[top_crop]} rank eq", "rank pw"], rows))
    mc = pd.read_csv(P("index_montecarlo.csv"))
    m4 = mc[mc.form == F4].set_index("crop")
    first = m4["1"] if "1" in m4.columns else m4[m4.columns[2]]
    mac("mcTop", LAB[first.idxmax()]); mac("mcTopShare", f"{100 * first.max():.1f}")
    mac("mcSecond", LAB[first.drop(first.idxmax()).idxmax()]); mac("mcSecondShare", f"{100 * first.drop(first.idxmax()).max():.1f}")

    # ---- validation ----
    vz = pd.read_csv(P("val_zhao.csv")).set_index("measure")
    mac("zhaoRhoFfour", f"{vz.loc['F4_hazard_paired (equal-weighted)', 'rho']:+.1f}")
    mac("zhaoRhoClimate", f"{vz.loc['climate part E x S (hazard-paired, no I)', 'rho']:+.1f}")
    vs = pd.read_csv(P("val_shocks_test.csv")).set_index("predictor")
    mac("shockRho", f"{vs.loc['ES_paired', 'rho']:+.2f}"); mac("shockP", f"{vs.loc['ES_paired', 'p_perm_one_sided']:.2f}"); mac("shockNpairs", int(vs.loc['ES_paired', 'n']))
    vsh = pd.read_csv(P("val_shocks.csv"))
    mac("oosMedian", f"{vsh.oos_skill_r.median():.2f}"); mac("oosPos", int((vsh.oos_skill_r > 0).sum())); mac("oosN", int(vsh.oos_skill_r.notna().sum()))

    hp = 0.5 * comp.E_heat * comp.S_heat * comp.In
    wp = 0.5 * comp.E_water * comp.S_water * comp.In
    mac("presentHeatShare", f"{100 * hp.sum() / (hp.sum() + wp.sum()):.0f}"); mac("presentWaterShare", f"{100 * wp.sum() / (hp.sum() + wp.sum()):.0f}")
    top7 = comp.assign(hp=hp, wp=wp).sort_values(F4, ascending=False).head(7)
    mac("nTopSevenWater", int((top7.wp > top7.hp).sum()))
    sens = pd.read_csv(P("sensitivity.csv"))
    mac("empHeatDetected", int((sens.b_T_used < 0).sum())); mac("empHeatCountry", int((sens.T_source == "country").sum())); mac("empN", len(sens))
    # ---- literature comparison (22_literature_comparison.py) ----
    if os.path.exists(P("literature_comparison.csv")):
        lc = pd.read_csv(P("literature_comparison.csv"))
        esc = lambda t: (str(t).replace("\\", "/").replace("%", r"\%").replace("&", r"\&").replace("_", r"\_")
                         .replace("~", "-").replace("<", "$<$").replace(">", "$>$").replace("#", r"\#"))
        rows = [[esc(r.id), esc(r.paper), esc(r.published_finding), esc(r.our_comparable_result), esc(r.agreement)] for _, r in lc.iterrows()]
        write("tab_litcompare.tex", tabular("p{0.9cm}p{3.0cm}p{4.4cm}p{4.6cm}p{2.0cm}", ["", "Study", "Published finding", "Our comparable result", "Verdict"], rows,
                                            "Signs and rank orders only; published values verified in docs/literature\\_comparison\\_sources.md; ours computed by code/22\\_literature\\_comparison.py."))
        lc_agree = lc.agreement.str.startswith("agree").sum()
        mac("litN", len(lc)); mac("litAgree", int(lc_agree)); mac("litDiffer", int(lc.agreement.str.startswith("differ").sum()))
        mac("litPartial", int(lc.agreement.str.startswith("partial").sum() + lc.agreement.str.startswith("sign").sum()))

    # ---- run comparison / worked example ----
    if os.path.exists(P("compare_crop_rank_runs.csv")):
        cr = pd.read_csv(P("compare_crop_rank_runs.csv"))
        for run, nm in (("mid-evaluation (blended S)", "Mid"), ("four-crop, literature-only S", "Four"), ("nine-crop, literature-only S", "Nine")):
            for wt in ("eq", "pw"):
                r = cr[(cr.run == run) & (cr.weighting == wt)].iloc[0]
                mac(f"order{nm}{wt.capitalize()}", r.order.replace(" > ", " $>$ ").title())
                mac(f"orderOrig{nm}{wt.capitalize()}", r.order_original_four.replace(" > ", " $>$ ").title())
        a4 = pd.read_csv(P("compare_mideval_vs_fourcrop.csv"))
        t = a4.sort_values(f"{F4}_lit", ascending=False).iloc[0]
        mac("litTopPair", f"{t.crop}--{sh(t.country)}"); mac("litTopValue", f4(t[f'{F4}_lit']))
        t2 = a4.sort_values(f"{F4}_lit", ascending=False).iloc[1]
        mac("litSecondPair", f"{t2.crop}--{sh(t2.country)}"); mac("litSecondValue", f4(t2[f'{F4}_lit']))
        mac("litRatioMedian", f"{a4.ratio_lit_to_mideval.median():.2f}")
        ex = pd.read_csv(P("worked_example.csv")).set_index("run")
        for run, nm in (("four_crop", "Four"), ("nine_crop", "Nine")):
            r = ex.loc[run]
            for k, fmt in (("L_heat_C", ".3f"), ("max_L_heat", ".3f"), ("E_heat", ".3f"), ("L_water", ".3f"), ("max_L_water", ".3f"), ("E_water", ".3f"),
                           ("s_T_per_C", ".3f"), ("max_s_T", ".3f"), ("S_heat", ".3f"), ("K_y", ".2f"), ("max_K_y", ".2f"), ("S_water", ".3f"),
                           ("I", ".3f"), ("max_I", ".3f"), ("I_norm", ".3f"), ("F4_pipeline", ".4f")):
                mac(f"ex{nm}{k.replace('_', '').replace('per', 'p').replace('C', 'c')}", format(r[k], fmt))
    write("numbers9.tex", "% generated by code/19_endeval_tex.py -- do not edit\n" + "\n".join(macros) + "\n")
    print(f"{len(macros)} macros; tables in {GEN}")


if __name__ == "__main__":
    main()
