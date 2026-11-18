"""
26_report_tables.py -- extra tables and macros for the comprehensive final report (docs/final_report.tex):
data-source inventory (from docs/DATA_MANIFEST.csv), parameter/source ledger (values from config.py, sources from
docs/literature_verification_new_crops.md and the mid-evaluation verification notes), derived-parameter fits,
consistency checks, rerun comparison, worked examples for the yield shock and the future yield accounting, and the
India nine-crop supply shares before/after the chickpea-lentil correction. Every number is read from a saved output
or from config.py; the code asserts that hand calculations equal the pipeline values.
Writes docs/nine_crop/generated/{tab_*.tex, numbers_report.tex}.
"""
import os
import re

import numpy as np
import pandas as pd

from config import ALL_CROPS, CROPS, FE_REQ, IRON_REQUIREMENT_15PCT, PROC, ROOT_DIR, ZINC_REQUIREMENT_MODERATE, ZN_REQ, season_kc

GEN = os.path.join(ROOT_DIR, "docs", "nine_crop", "generated")
P = lambda f: os.path.join(PROC, f)
macros = []
DIGITS = dict(zip("0123456789", ["Zero", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine"]))
LAB = {"rice": "Rice", "wheat": "Wheat", "maize": "Maize", "soybean": "Soybean", "chickpea": "Chickpea", "lentil": "Lentil",
       "bean": "Common bean", "groundnut": "Groundnut", "rapeseed": "Rapeseed-mustard"}


def mac(name, value):
    name = "".join(DIGITS.get(ch, ch) for ch in name if ch.isalnum())
    macros.append(f"\\newcommand{{\\{name}}}{{{value}}}")


def esc(s):
    return str(s).replace("&", "\\&").replace("%", "\\%").replace("_", "\\_").replace("#", "\\#")


def write(name, body):
    with open(os.path.join(GEN, name), "w", encoding="utf-8") as fh:
        fh.write(body)


def frac_cols(cols):
    """p{Xcm} -> L{fraction of the line width} (column type defined in final_report.tex), scaled so the p columns
    fill the width left by the r/c/l columns: generated longtables cannot run past the margin."""
    widths = [float(x) for x in re.findall(r"p\{([\d.]+)cm\}", cols)]
    n_other = len(re.sub(r"p\{[\d.]+cm\}", "", cols))
    avail = 1.0 - 0.085 * n_other
    return re.sub(r"p\{([\d.]+)cm\}", lambda m: "L{%.3f}" % (avail * float(m.group(1)) / sum(widths)), cols)


def longtable(cols, header, rows, caption, label, size="\\scriptsize"):
    cols = frac_cols(cols)
    short = caption.split(". ")[0].split(" (")[0].rstrip(".")
    h = " & ".join(header) + " \\\\"
    out = [f"{{{size}\\begin{{longtable}}{{{cols}}}", f"\\caption[{short}]{{{caption}}}\\label{{{label}}}\\\\", "\\toprule", h, "\\midrule\\endfirsthead",
           "\\toprule", h, "\\midrule\\endhead", "\\bottomrule\\endfoot"]
    out += [" & ".join(str(x) for x in r) + " \\\\" for r in rows]
    out.append("\\end{longtable}}")
    return "\n".join(out) + "\n"


def tabular(cols, header, rows):
    return ("\\begin{tabular}{" + cols + "}\n\\toprule\n" + " & ".join(header) + " \\\\\n\\midrule\n"
            + "\n".join(" & ".join(str(x) for x in r) + " \\\\" for r in rows) + "\n\\bottomrule\n\\end{tabular}\n")


# ------------------------------------------------------------------------------------------------ data sources
DATASETS = [  # folder, name, version / edition, provider + citation key, use
    ("worldclim", "WorldClim 2.1 monthly weather (CRU-TS 4.09 downscaled), 10$'$; elevation; 1970--2000 precipitation normals", "CRU-TS 4.09; WorldClim 2.1", "\\citet{fick2017,harris2020}", "monthly precipitation 1970--2024; elevation"),
    ("tmax", "WorldClim 2.1 monthly maximum temperature, 10$'$", "CRU-TS 4.09", "\\citet{fick2017,harris2020}", "$T_{\\max}$ 1970--2024"),
    ("tmin", "WorldClim 2.1 monthly minimum temperature, 10$'$", "CRU-TS 4.09", "\\citet{fick2017,harris2020}", "$T_{\\min}$ 1970--2024"),
    ("normals", "WorldClim 2.1 monthly normals $T_{\\max}$, $T_{\\min}$, 10$'$", "1970--2000", "\\citet{fick2017}", "baseline of the change factors"),
    ("cmip6", "WorldClim 2.1 CMIP6 downscaled climatology, MRI-ESM2-0, SSP2-4.5, 10$'$", "2041--2060", "\\citet{wcmip6}", "future change factors"),
    ("spam", "SPAM 2010 harvested area (all, irrigated, rainfed), 5$'$", "v2.0", "\\citet{spam2010}", "crop area weights, rainfed share"),
    ("sacks", "Crop calendar dataset (planting, harvest)", "Sacks et al.\\ 2010", "\\citet{sacks2010}", "growing season and flowering window"),
    ("faostat", "FAOSTAT bulk: crop production (QCL); Food Balances 2010-- and --2013; Food Security indicators", "bulk files of 5 Oct 2026", "\\citet{faostat}", "panels, yields, nutrient supply, energy requirement"),
    ("faostat_sua", "FAOSTAT Supply Utilization Accounts, crops", "bulk file of 17 Nov 2026", "\\citet{faosua}", "chickpea and lentil supply"),
    ("usda", "USDA FoodData Central, SR Legacy", "April 2018 release", "\\citet{usda2019}", "zinc and iron per 100 g"),
    ("naturalearth", "Natural Earth admin-0 countries, 1:50m", "--", "Natural Earth (public domain)", "country masks, continents"),
    ("naturalearth_admin1", "Natural Earth admin-1 states/provinces, 1:10m", "--", "Natural Earth (public domain)", "Telangana mask"),
    ("koppen", "K\\\"oppen--Geiger 1991--2020, 0.5\\textdegree", "Beck et al.\\ 2023", "\\citet{beck2018}", "check of our K\\\"oppen groups"),
    ("india", "Official India/Telangana/Hyderabad files: MoSPI HCES 2023--24, NSS 592 and 594, NFHS-5, CNNS, ICMR-NIN IFCT 2017, Telangana DES", "see Appendix~\\ref{app:indiasources}", "Section~\\ref{sec:india}", "Hyderabad and Telangana analysis"),
]


def data_sources():
    m = pd.read_csv(os.path.join(ROOT_DIR, "docs", "DATA_MANIFEST.csv"))
    rows = []
    for folder, name, ver, cite, use in DATASETS:
        g = m[m.folder == folder]
        rows.append([name, ver, cite, use, len(g), f"{g.bytes.sum() / 1e6:,.0f}".replace(",", "{,}"), " / ".join(sorted(g.modified.unique()))])
    assert sum(r[4] for r in rows) == len(m), "a manifest folder is missing from DATASETS"
    write("tab_data_sources.tex", longtable("p{4.6cm}p{2.2cm}p{2.3cm}p{3.2cm}rrp{1.6cm}", ["Dataset", "Version", "Source", "Used for", "Files", "MB", "File date"], rows,
                                          "Raw inputs (from \\texttt{docs/DATA\\_MANIFEST.csv}, which lists every file with its SHA-256 checksum).", "tab:datasources"))
    mac("manifestFiles", len(m))
    mac("manifestGB", f"{m.bytes.sum() / 1e9:.1f}")


# ------------------------------------------------------------------------------------------------ parameter ledger
def ledger():
    c = ALL_CROPS
    f = lambda x, d=2: f"{x:.{d}f}"
    R = []   # crop, parameter, value, source & location, conditions, metric/outcome, status, alternatives tested

    def add(*r):
        R.append(list(r))   # cells are written as LaTeX already
    add("Rice", "$T_{crit}$", f(c["rice"]["tcrit"], 1), "\\citet{yoshida1981} Table 2.4; FAO-66 p.~106", "critical high temperature at anthesis, $>$1 h", "daily mean air $T$; spikelet sterility", "published (metric differs from $T_{eff}$)", "$\\pm$1--3\\,\\si{\\celsius}")
    add("Rice", "$s_T$", f(c["rice"]["heat_slope"], 3), "\\citet{jagadish2007}", "IR64 in chambers, $\\le$1 h at anthesis", "spikelet fertility ($\\approx$7\\%/\\si{\\celsius} above 29.6\\,\\si{\\celsius})", "published, outcome borrowed (fertility $\\to$ yield)", "--")
    add("Rice", "$K_y$", f(c["rice"]["ky"]), "FAO-33 Table 2 p.~7 (rice ``high'', no number); maize value FAO-66 Table 1", "--", "seasonal yield--ET response", "PROXY (maize)", "1.0, 1.5")
    add("Wheat", "$T_{crit}$, $T_{lim}$", f"{c['wheat']['tcrit']:.0f}, 35", "\\citet{deryng2014} Table A.1", "PEGASUS model, spring wheat", "$T_{eff}$, 45--70\\% of season; yield", "published model parameter (also used for winter wheat)", "$\\pm$1--3\\,\\si{\\celsius}")
    add("Wheat", "$K_y$", f(c["wheat"]["ky"]), "FAO-66 Table 1 (spring 1.15, winter 1.05)", "--", "seasonal", "DERIVED mean of two FAO values", "--")
    add("Maize", "$T_{crit}$, $T_{lim}$", "32, 45", "\\citet{deryng2014} Table A.1", "PEGASUS model", "$T_{eff}$; yield", "published model parameter", "$\\pm$1--3\\,\\si{\\celsius}")
    add("Maize", "$K_y$", f(c["maize"]["ky"]), "FAO-66 Table 1 (= FAO-33)", "--", "seasonal", "published", "--")
    add("Soybean", "$T_{crit}$, $T_{lim}$", "35, 40", "\\citet{deryng2014} Table A.1", "PEGASUS model", "$T_{eff}$; yield", "published model parameter", "$\\pm$1--3\\,\\si{\\celsius}")
    add("Soybean", "$K_y$", f(c["soybean"]["ky"]), "FAO-66 Table 1 (= FAO-33)", "--", "seasonal", "published", "--")
    add("Chickpea", "$T_{crit}$, $s_T$", f"{f(c['chickpea']['tcrit'], 1)}, {f(c['chickpea']['heat_slope'], 3)}", "\\citet{bhandari2020} Table 3 p.~749", "3 Indian genotypes, pots, growth chambers 30/20--42/32\\,\\si{\\celsius} (12/12 h), flowering to maturity", "seed yield per plant", "DERIVED fit (5 points)", "$T_{crit}$ 30.3 (pod set, \\citealp{devasirvatham2013}); +3\\,\\si{\\celsius}; slope $\\times$0.7")
    add("Chickpea", "$K_y$", f(c["chickpea"]["ky"]), "\\citet{tari2022} p.~143", "field, Konya (Turkey), 2 years, 2 sowing dates", "seasonal (0.85, 0.91)", "DERIVED mean of 2 field values; not in FAO", "0.67, 1.15")
    add("Lentil", "$T_{crit}$, $s_T$", f"{f(c['lentil']['tcrit'], 1)}, {f(c['lentil']['heat_slope'], 3)}", "\\citet{bhandari2020} Table 3", "2 Indian genotypes, as chickpea", "seed yield per plant", "DERIVED fit (4 points, 2 parameters)", "+3\\,\\si{\\celsius}; slope $\\times$0.7")
    add("Lentil", "$K_y$", f(c["lentil"]["ky"]), "\\citet{nandi2021} abstract", "field, Lower Gangetic Plain, after rice", "``1\\% yield loss per 1\\% decline in relative ET''; best treatment 0.87", "PROXY (abstract only)", "0.87, 1.15")
    add("Common bean", "$T_{crit}$, $s_T$", f"{f(c['bean']['tcrit'], 1)}, {f(c['bean']['heat_slope'], 3)}", "\\citet{prasad2002bean} via \\citet{boote2005} p.~470", "cv.\\ Montcalm (Andean red kidney), sunlit chambers, season-long, 10\\,\\si{\\celsius} diurnal range", "seed yield (max at 28/18, zero at 37/27\\,\\si{\\celsius})", "DERIVED from two published points; full text not read", "$T_{crit}$ +2\\,\\si{\\celsius}; slope $\\times$0.7")
    add("Common bean", "$K_y$", f(c["bean"]["ky"]), "FAO-33 Table 24 p.~39; FAO-66 Table 1", "--", "seasonal (IAEA field 0.59, 1.43)", "published", "0.6, 1.4")
    add("Groundnut", "$T_{crit}$, $s_T$", f"{f(c['groundnut']['tcrit'], 1)}, {f(c['groundnut']['heat_slope'], 3)}", "\\citet{prasad2003peanut} abstract", "cv.\\ Georgia Green, sunlit chambers 32/22--44/34\\,\\si{\\celsius}, season-long, ambient CO$_2$", "seed yield ($-$14, $-$59, $-$90\\%)", "DERIVED fit (4 points); full text not read", "29.0/0.074 \\citep{boote2005}; +3\\,\\si{\\celsius}; slope $\\times$0.7")
    add("Groundnut", "$K_y$", f(c["groundnut"]["ky"]), "FAO-33 Table 24; FAO-66 Table 1", "--", "seasonal", "published", "--")
    add("Rapeseed-mustard", "$T_{crit}$", f(c["rapeseed"]["tcrit"], 1), "\\citet{morrison2002} abstract", "field, Ottawa, 3 years $\\times$ 3 sowing dates, 3 \\emph{Brassica} species incl.\\ \\emph{B.~juncea}", "accumulated daily $T_{\\max}$ above 29.5\\,\\si{\\celsius} at flowering; seed yield", "PROXY conversion to $T_{eff}$ with an assumed 12\\,\\si{\\celsius} diurnal range", "$\\pm$1--3\\,\\si{\\celsius}")
    add("Rapeseed-mustard", "$s_T$", f(c["rapeseed"]["heat_slope"], 2), "borrowed: \\citet{deryng2014} spring-wheat span (10\\,\\si{\\celsius})", "--", "--", "PROXY (no published slope found)", "0.07, 0.18")
    add("Rapeseed-mustard", "$K_y$", f(c["rapeseed"]["ky"]), "FAO-56 Rev.1 Table 8.7 p.~279 \\citep{fao56rev1}", "no source stated by FAO; field 0.87 \\citep{istanbulluoglu2010}", "seasonal", "published, origin not traceable", "0.85, 0.95")
    for k in CROPS:
        add(LAB[k], "$K_c$ ini, mid, end; $\\bar K_c$", ", ".join(f(x) for x in c[k]["kc"]) + f"; {season_kc(k):.2f}", "FAO-56 Tables 11--12 \\citep{fao56}" + ("; stages: lentil arid row" if k == "chickpea" else "; stages: Rev.1 Table 6.11 GDD shares" if k == "rapeseed" else ""),
            "subhumid reference conditions", "crop water need ($\\mathrm{ET_c}=K_c\\mathrm{ET_0}$)", "published; stages PROXY" if k in ("chickpea", "rapeseed") else "published", "--")
    add("All", "Flowering window", "45--70\\% of season", "\\citet{deryng2014}", "anthesis at 0.5 of the season", "--", "published (model convention)", "--")
    add("Chickpea, lentil, rapeseed", "Calendar", "cool-season rule", "\\citet{sacks2010} (own observed calendar, else wheat/spring-wheat calendar)", "Sacks ``Pulses'' calendar is 95\\% gap-filled in India and monsoon-season", "--", "PROXY (borrowed calendars)", "plain Sacks calendar")
    add("All", "$\\mathrm{ET_0}$", "Hargreaves", "FAO-56 Eq.~52 \\citep{fao56}", "needs $T_{\\max}$, $T_{\\min}$, $R_a$ only", "--", "published", "--")
    add("All", "Zn requirement", f"{ZN_REQ:.1f} mg/d", "WHO/FAO 2004 Table 12.4 p.~240 \\citep{whofao2004}", "adults, low bioavailability (women 9.8, men 14.0)", "RNI (upper percentile)", "DERIVED mean of two RNIs", f"{ZINC_REQUIREMENT_MODERATE:.2f} (moderate)")
    add("All", "Fe requirement", f"{FE_REQ:.2f} mg/d", "WHO/FAO 2004 Table 13.5 p.~271", "adults, 10\\% bioavailability (women 29.4, men 13.7)", "RNI (95th percentile)", "DERIVED mean of two RNIs", f"{IRON_REQUIREMENT_15PCT:.2f} (15\\%)")
    add("All", "Energy, protein, fat requirement", "ADER; 10\\%, 15\\% of energy", "FAOSTAT food-security indicators; \\citet{who2003}", "country- and year-specific energy requirement", "population average (energy); lower bounds of goals", "published", "--")
    add("All", "Zn, Fe composition", "per FBS item", "USDA SR Legacy \\citep{usda2019}; \\texttt{code/fbs\\_usda\\_map.csv}", "raw, unprocessed form (whole grain; primary weight)", "mg/100 g", "mapping choice (overstates Zn, Fe for refined cereals, meat)", "--")
    write("tab_ledger.tex", longtable("p{1.5cm}p{1.6cm}p{1.6cm}p{2.8cm}p{3.0cm}p{2.3cm}p{2.0cm}p{1.6cm}",
                                      ["Crop", "Parameter", "Value", "Source and location", "Experiment / conditions", "Metric and outcome", "Status", "Alternatives tested"], R,
                                      "Parameter and source ledger. Values are read from \\texttt{code/config.py}. Status: published = value printed in the source; DERIVED = our arithmetic or fit on published values; PROXY = value borrowed from another crop, outcome or metric. Read levels and verbatim quotes: \\texttt{docs/literature\\_verification\\_new\\_crops.md}.", "tab:ledger"))


def crop_mapping():
    comp = pd.read_csv(P("composition_used.csv")).set_index("fbs_item")
    rows = []
    for k, v in CROPS.items():
        items = v.get("fbs_items", []) or []
        sua = v.get("sua_items", []) or []
        usda = "; ".join(dict.fromkeys(esc(comp.loc[i, "description"]) for i in (items or sua) if i in comp.index and isinstance(comp.loc[i, "description"], str)))
        cal = v.get("calendar_rule") or ""
        rows.append([LAB[k], esc(v["group"]), esc(v["faostat_item"]), v["spam"], esc(", ".join(v["sacks"])) + (" (cool-season rule)" if "cool" in str(cal).lower() else ""),
                     esc("; ".join(items)) if items else "--", esc("; ".join(sua)) if sua else "--", usda])
    write("tab_crop_mapping.tex", longtable("p{1.6cm}p{1.1cm}p{1.9cm}p{0.9cm}p{2.1cm}p{2.6cm}p{1.5cm}p{3.6cm}",
                                           ["Crop", "Group", "FAOSTAT item", "SPAM", "Sacks calendar", "FBS items", "SUA item", "USDA composition (Zn, Fe)"], rows,
                                           "How each crop is identified in each dataset (from \\texttt{code/config.py} and \\texttt{code/fbs\\_usda\\_map.csv}).", "tab:cropmap"))


def fits():
    d = pd.read_csv(P("parameter_fits.csv"))
    rows = [[LAB[r.crop], esc(r.points_teff) if isinstance(r.points_teff, str) else "", esc(r.points_loss) if isinstance(r.points_loss, str) else "",
             f"{r.tcrit_fit:.2f}", f"{r.slope_fit:.4f}", f"{r.tlim_fit:.2f}", "" if pd.isna(r.rmse) else f"{r.rmse:.3f}", f"{r.tcrit_config:.1f} / {r.slope_config:.3f}",
             "yes" if r.reproduces_config else "NO"] for r in d.itertuples()]
    write("tab_fits.tex", tabular("lp{2.6cm}p{2.6cm}rrrrrc", ["Crop", "$T_{eff}$ points (\\si{\\celsius})", "relative loss", "$T_{crit}$", "$s_T$", "$T_{lim}$", "RMSE", "config", "match"], rows))
    assert d.reproduces_config.all()


def checks():
    d = pd.read_csv(P("consistency_checks.csv"))
    rows = [[i + 1, esc(r.check), "pass" if r.passed else "FAIL", esc(r.detail) if isinstance(r.detail, str) else ""] for i, r in enumerate(d.itertuples())]
    write("tab_checks.tex", longtable("rp{9.6cm}cp{4.4cm}", ["", "Check (\\texttt{code/24\\_checks.py})", "Result", "Detail"], rows,
                                      "Consistency checks run on the saved results.", "tab:checks"))
    mac("checksN", len(d))
    mac("checksPassed", int(d.passed.sum()))


def audit():
    f = P("audit_rerun_comparison.csv")
    if not os.path.exists(f):
        mac("auditAvailable", "no")
        return
    d = pd.read_csv(f)
    s = d.groupby(["area", "status"]).size().unstack(fill_value=0)
    cols = [c for c in ["identical", "within tolerance", "differs", "new", "missing", "error"] if c in s.columns]
    rows = [[esc(a)] + [int(s.loc[a, c]) for c in cols] for a in s.index]
    write("tab_audit_summary.tex", tabular("l" + "r" * len(cols), ["Output area"] + cols, rows))
    diff = d[~d.status.isin(["identical"])].copy()
    # one row per file pattern (crop names replaced by *), so 72 legacy per-crop files do not fill pages
    diff["pattern"] = diff.file.str.replace("\\", "/", regex=False).str.replace(r"(rice|wheat|maize|soybean|chickpea|lentil|bean|groundnut|rapeseed)(__altcal)?", "*", regex=True)
    g = diff.groupby(["area", "pattern", "status"], sort=False).agg(n=("file", "size"), mx=("max_abs_diff", "max"), rel=("max_rel_diff", "max")).reset_index()
    rows = [["\\file{" + esc(r.area.replace("data/", "")) + "}", "\\file{" + esc(r.pattern) + "}", r.status, r.n, "" if pd.isna(r.mx) else f"{r.mx:.2g}",
             "" if pd.isna(r.rel) else f"{r.rel:.2g}"] for r in g.itertuples()]
    if rows:
        write("tab_audit_diff.tex", longtable("p{4.2cm}p{6.4cm}p{1.9cm}rrr", ["Area", "File (* = each crop)", "Status", "Files", "max abs", "max rel"], rows,
                                              "Outputs that are not identical in both runs: new outputs of this audit, and previous files the pipeline no longer writes. No file present in both runs differs.", "tab:auditdiff"))
    else:
        write("tab_audit_diff.tex", "All compared outputs are identical.\n")
    mac("auditAvailable", "yes")
    mac("auditFiles", len(d))
    for st in ["identical", "within tolerance", "differs", "new", "missing", "error"]:
        mac("audit" + st.title().replace(" ", ""), int((d.status == st).sum()))


def worked_shock():
    """Standard -10 % shock for wheat in India, from saved inputs to the saved scenario row."""
    sc = pd.read_csv(P("yield_diet_scenarios.csv"))
    r = sc[(sc.crop == "wheat") & (sc.country == "India") & sc.scenario.str.startswith("S3")].iloc[0]
    cc, adq = pd.read_csv(P("crop_contrib.csv")), pd.read_csv(P("adequacy.csv"))
    last = int(adq.Year.max())
    b = adq[(adq.m49 == 356) & adq.Year.between(last - 2, last)].mean(numeric_only=True)
    c = cc[(cc.m49 == 356) & (cc.crop == "wheat") & cc.Year.between(last - 2, last)].mean(numeric_only=True)
    ssr = c["prod"] / c["dom"]
    frac = 0.10 * min(1.0, max(0.0, ssr))
    lower = min(frac, max(0.0, 0.10 * c["prod"] - c["exp"]) / c["dom"])
    nar0 = {n: min(1, b[n] / b[f"req_{n}"]) for n in ["kcal", "protein", "fat", "zinc", "iron"]}
    nar1 = {n: min(1, (b[n] - frac * c[n]) / b[f"req_{n}"]) for n in nar0}
    dmar = 100 * (np.mean(list(nar1.values())) - np.mean(list(nar0.values())))
    assert abs(frac - r.cut_frac_upper) < 1e-9 and abs(dmar - r.dMAR_pts_upper) < 1e-9 and abs(lower - r.cut_frac_lower) < 1e-9
    assert abs(-100 * frac * c.iron / b.iron - r.diron_pct_upper) < 1e-9
    for k, v in {"Prod": c["prod"], "Dom": c["dom"], "Exp": c["exp"]}.items():
        mac(f"wsWheatInd{k}", f"{v:,.0f}".replace(",", "{,}"))
    mac("wsSSR", f"{ssr:.3f}"); mac("wsFrac", f"{frac:.4f}"); mac("wsLower", f"{lower:.4f}")
    for n in ["kcal", "iron", "zinc"]:
        mac(f"wsC{n.capitalize()}", f"{c[n]:.2f}"); mac(f"wsB{n.capitalize()}", f"{b[n]:.2f}"); mac(f"wsR{n.capitalize()}", f"{b[f'req_{n}']:.2f}")
        mac(f"wsNARzero{n.capitalize()}", f"{nar0[n]:.3f}"); mac(f"wsNARone{n.capitalize()}", f"{nar1[n]:.3f}")
        mac(f"wsD{n.capitalize()}", f"{-100 * frac * c[n] / b[n]:.2f}")
    mac("wsMARzero", f"{100 * np.mean(list(nar0.values())):.2f}"); mac("wsMARone", f"{100 * np.mean(list(nar1.values())):.2f}"); mac("wsDMAR", f"{dmar:+.2f}")
    mac("wsDMARlower", f"{r.dMAR_pts_lower:+.2f}")


def worked_future():
    """Future yield accounting for wheat in India (year-level losses are averaged by 16_future_yield_nutrition.py)."""
    y = pd.read_csv(P("future_yield.csv"))
    r = y[(y.crop == "wheat") & (y.country == "India")].iloc[0]
    dy = -100 * (r.loss_fut - r.loss_hist) / (1 - r.loss_hist)
    assert abs(dy - r.dY_lit_pct) < 1e-9
    for k in ["heat_loss_hist", "heat_loss_fut", "water_loss_hist", "water_loss_fut", "loss_hist", "loss_fut"]:
        mac("wf" + k.title().replace("_", ""), f"{r[k]:.4f}")
    mac("wfdTeff", f"{r.dTeff_C:+.2f}"); mac("wfdY", f"{r.dY_lit_pct:+.2f}"); mac("wfdYemp", f"{r.dY_emp_pct:+.2f}")
    mac("wfSlope", f"{CROPS['wheat']['heat_slope']:.2f}"); mac("wfKy", f"{CROPS['wheat']['ky']:.2f}")
    fn = pd.read_csv(P("future_nutrition.csv"))
    q = fn[(fn.crop == "wheat") & (fn.country == "India") & fn.model.str.startswith("literature")].iloc[0]
    mac("wfDIron", f"{q.diron_pct_upper:+.2f}"); mac("wfDMAR", f"{q.dMAR_pts_upper:+.2f}"); mac("wfDKcal", f"{q.dkcal_pct_upper:+.2f}")
    fc = pd.read_csv(P("future_components.csv"))
    w = fc[(fc.crop == "wheat") & (fc.m49 == 356)].iloc[0]
    for k in ["H_heat", "H_water", "E_heat", "E_water", "F4_hazard_paired"]:
        for lbl, nm in (("historical_1971_2000", "Hist"), ("future_2041_2060", "Fut")):
            mac("wf" + k.replace("_", "").replace("hazardpaired", "") + nm, f"{w[f'{k}_{lbl}']:.4f}")
    mac("wfdFfourHeat", f"{w.dF4_from_heat:+.4f}"); mac("wfdFfourWater", f"{w.dF4_from_water:+.4f}")


def india_shares():
    d = pd.read_csv(P("food_supply_diversity.csv")).set_index("Area")
    rows = []
    for n, lab in (("kcal", "Energy"), ("protein", "Protein"), ("fat", "Fat"), ("zinc", "Zinc"), ("iron", "Iron")):
        a, b, cl = (100 * d.loc["India", f"share_{k}_{n}"] for k in ("fbs_item_crops", "nine_crops", "chickpea_lentil"))
        rows.append([lab, f"{a:.2f}", f"{cl:.2f}", f"{b:.2f}"])
        mac(f"shareOld{n.capitalize()}", f"{a:.2f}"); mac(f"shareNew{n.capitalize()}", f"{b:.2f}"); mac(f"shareCL{n.capitalize()}", f"{cl:.2f}")
    write("tab_india_shares.tex", tabular("lrrr", ["Nutrient", "seven FBS-item crops (\\%)", "+ chickpea, lentil (SUA, \\%)", "nine crops (\\%)"], rows))


def diversity():
    d = pd.read_csv(P("food_supply_diversity.csv")).sort_values("eff_sources_kcal")
    fix = lambda s: s.encode("latin-1").decode("utf-8") if isinstance(s, str) and "\u00c3" in s else s
    pct = lambda v: "--" if pd.isna(v) else f"{100 * v:.0f}"
    rows = [[esc(fix(r.Area)), f"{r.eff_sources_kcal:.1f}", f"{r.eff_sources_protein:.1f}", f"{r.eff_sources_zinc:.1f}", f"{r.eff_sources_iron:.1f}",
             pct(r.cereal_share_kcal), esc(r.top_source_iron), pct(r.share_nine_crops_kcal), pct(r.share_nine_crops_iron)] for r in d.itertuples()]
    write("tab_diversity.tex", tabular("lrrrrrlrr", ["Country", "kcal", "protein", "Zn", "Fe", "cereal \\% kcal", "top iron source", "9 crops \\% kcal", "9 crops \\% Fe"], rows))


def india_sources():
    import importlib
    gran = importlib.import_module("23_sources_doc").GRANULARITY
    d = pd.read_csv(os.path.join(ROOT_DIR, "data", "external", "india_hyderabad_indicators.csv"))
    rows = []
    for s, g in d.groupby("source_short", sort=False):
        rows.append(["\\file{" + esc(s) + "}", esc(str(g.iloc[0].source_full_citation)), esc(gran.get(s, "")), len(g), esc(", ".join(sorted(g.read_level.dropna().unique())))])
    write("tab_india_sources.tex", longtable("p{2.2cm}p{5.4cm}p{5.2cm}rp{1.6cm}", ["Source", "Citation", "Granularity and use", "Rows", "Read level"], rows,
                                            "Official sources of the India/Telangana/Hyderabad analysis (from \\texttt{data/external/india\\_hyderabad\\_indicators.csv}).", "tab:indiasources"))
    mac("indiaIndicatorRows", len(d))


def misc():
    fg = pd.read_csv(P("future_group.csv")).set_index("group")
    for g in fg.index:
        h, f = fg.loc[g, "F4_eq_historical_1971_2000"], fg.loc[g, "F4_eq_future_2041_2060"]
        mac(f"grp{g.capitalize()}Pct", f"{100 * (f - h) / h:+.0f}")
    fastest = max(fg.index, key=lambda g: (fg.loc[g, "F4_eq_future_2041_2060"] - fg.loc[g, "F4_eq_historical_1971_2000"]) / fg.loc[g, "F4_eq_historical_1971_2000"])
    mac("grpFastest", {"cereal": "cereals", "pulse": "pulses", "oilseed": "oilseeds"}[fastest])
    fy = pd.read_csv(P("future_yield.csv"))
    mac("fyLitNeg", int((fy.dY_lit_pct < 0).sum())); mac("fyEmpNeg", int((fy.dY_emp_pct < 0).sum())); mac("fyN", len(fy))
    mac("fyEmpDetected", int(fy.emp_detected.sum()))
    sgn = (np.sign(fy.dY_lit_pct.round(6)) == np.sign(fy.dY_emp_pct.round(6))).mean()
    mac("fySameSign", f"{100 * sgn:.0f}")


def main():
    data_sources()
    ledger()
    crop_mapping()
    fits()
    checks()
    audit()
    worked_shock()
    worked_future()
    india_shares()
    diversity()
    india_sources()
    misc()
    write("numbers_report.tex", "% generated by code/26_report_tables.py -- do not edit\n" + "\n".join(macros) + "\n")
    print(len(macros), "report macros")


if __name__ == "__main__":
    main()
