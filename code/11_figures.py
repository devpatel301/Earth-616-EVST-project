import os


import geopandas as gpd
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import BoundaryNorm, ListedColormap, TwoSlopeNorm

from config import CLASS_NAME, CROPS, FIG, NX, NY, PROC, WORK, ZHAO

matplotlib.rcParams.update({"font.size": 13, "font.family": "DejaVu Sans", "axes.spines.top": False,
                            "axes.spines.right": False, "savefig.bbox": "tight", "savefig.pad_inches": 0.05,
                            "axes.titlesize": 14, "axes.titleweight": "bold", "xtick.labelsize": 11.5,
                            "ytick.labelsize": 11.5, "legend.fontsize": 11.5, "axes.labelsize": 12.5})
CC = {"rice": "#2a7f62", "wheat": "#c8961a", "maize": "#c0504d", "soybean": "#5b5ea6"}
KGC = ["#1b7837", "#e08a1e", "#8e6bb3", "#3b78b5", "#bdbdbd"]       # A B C D E
INK, MUTED = "#222222", "#777777"
EXT = [-180, 180, -90, 90]
SHORT = {"China, mainland": "China", "United States of America": "USA", "Russian Federation": "Russia",
         "Iran (Islamic Republic of)": "Iran", "Republic of Korea": "S. Korea", "South Africa": "S. Africa"}
sn = lambda c: SHORT.get(c, c)


# Every graph gets explicit axis titles. LABELS[name] = (x title, y title); the x title goes on the bottom
# row and the y title on the first column of every multi-panel figure. Axes that already have a title keep it.
LABELS = {
    "F01_panels_koppen": ("Longitude", "Latitude"),
    "F02a_heat_shift_map": ("Longitude", "Latitude"),
    "F02b_water_shift_map": ("Longitude", "Latitude"),
    "F03_water_hazard_map": ("Longitude", "Latitude"),
    "F04_exposure_by_country": ("Country (climate class)", "Exposure score (0-1)"),
    "F05_sensitivity_coefficients": (None, "Crop and country (POOLED = all panel countries together)"),
    "F06_importance_heatmap": ("Nutrient", "Crop: country"),
    "F07_adequacy_panel": ("Nutrient", "Country"),
    "F08_index_forms": ("Crop", "Index value relative to the highest crop (1 = most vulnerable)"),
    "F09_country_index": ("Index F4 value (higher = more vulnerable)", "Country (climate class)"),
    "F10_montecarlo_ranks": ("Share of 2,000 random-weight draws", "Crop"),
    "F11_zhao_validation": ("Zhao et al. (2017): yield loss per \u00b0C of warming (%)", None),
    "F12_shock_validation": (None, None),
    "F13_yield_supply_passthrough": (None, "Crop and country"),
    "F14_scenario_shock": (None, "Crop and country"),
    "F15_example_series": ("Year", None),
    "F16_myers_check": ("Crop (photosynthesis type)", None),
}


def apply_labels(fig, name):
    lab = LABELS.get(name)
    if not lab:
        return
    xl, yl = lab
    for ax in fig.axes:
        if ax.get_label() == "<colorbar>" or not ax.get_visible():
            continue
        try:
            ss = ax.get_subplotspec()
            first_col, last_row = ss.is_first_col(), ss.is_last_row()
        except Exception:
            first_col = last_row = True
        small = name.startswith(("F01", "F02", "F03"))
        if xl and not ax.get_xlabel() and last_row:
            ax.set_xlabel(xl, fontsize=8 if small else None)
        if yl and not ax.get_ylabel() and first_col:
            ax.set_ylabel(yl, fontsize=8 if small else None)


def save(fig, name, png=False):
    apply_labels(fig, name)
    fig.savefig(os.path.join(FIG, name + (".png" if png else ".pdf")), dpi=200)
    plt.close(fig)


def borders():
    shp = [f for f in os.listdir(os.path.join(WORK, "naturalearth")) if f.endswith(".shp")][0]
    return gpd.read_file(os.path.join(WORK, "naturalearth", shp))


def grid_from_cells(cells, vals):
    g = np.full(NY * NX, np.nan)
    g[cells] = vals
    return g.reshape(NY, NX)


def panel_extent(ax, bounds):
    ax.set_xlim(-170, 180)
    ax.set_ylim(-58, 75)
    ax.set_xticks([-120, -60, 0, 60, 120], ["120\u00b0W", "60\u00b0W", "0\u00b0", "60\u00b0E", "120\u00b0E"], fontsize=7)
    ax.set_yticks([-40, 0, 40], ["40\u00b0S", "0\u00b0", "40\u00b0N"], fontsize=7)
    ax.set_xlabel(""); ax.set_ylabel("")
    ax.tick_params(length=2, pad=1)
    for s in ax.spines.values():
        s.set_visible(False)


# ---------------------------------------------------------------- F01 panels on Koppen map
def f_panels():
    Z = np.load(os.path.join(WORK, "zones.npz"))
    kg = Z["kg"].astype(float)
    kg[kg < 0] = np.nan
    cg = np.load(os.path.join(WORK, "country_grid.npy"))
    P = pd.read_csv(os.path.join(PROC, "panels.csv"))
    B = borders()
    fig, axs = plt.subplots(2, 2, figsize=(12, 6.2))
    for ax, crop in zip(axs.ravel(), CROPS):
        ax.imshow(kg, extent=EXT, cmap=ListedColormap(KGC), vmin=-0.5, vmax=4.5, alpha=0.28, interpolation="nearest")
        area = np.load(os.path.join(WORK, f"grids_{crop}.npz"))["area_A"]
        p = P[P.crop == crop]
        dens = np.where(np.isin(cg, p.m49) & (area > 500), kg, np.nan)
        ax.imshow(dens, extent=EXT, cmap=ListedColormap(KGC), vmin=-0.5, vmax=4.5, interpolation="nearest")
        B.boundary.plot(ax=ax, color="#555555", lw=0.2)
        B[B.ISO_N3_EH.astype(str).replace("-99", "-1").astype(int).isin(p.m49)].boundary.plot(ax=ax, color=INK, lw=0.9)
        panel_extent(ax, None)
        names = [sn(c) for c in p.country]
        ax.set_title(CROPS[crop]["label"] + "\n" + ", ".join(names[:4]) + "\n" + ", ".join(names[4:]),
                     fontsize=9, fontweight="normal")
    handles = [plt.Rectangle((0, 0), 1, 1, color=KGC[i]) for i in range(4)]
    fig.legend(handles, [CLASS_NAME[k] for k in "ABCD"],
               loc="lower center", ncol=4, frameon=False, bbox_to_anchor=(0.5, -0.04))
    fig.subplots_adjust(wspace=0.03, hspace=0.45, bottom=0.08)
    save(fig, "F01_panels_koppen", png=True)


# ---------------------------------------------------------------- F02 shift maps
def f_shift_maps(var, fname, label, cmap):
    B = borders()
    fig, axs = plt.subplots(2, 2, figsize=(12, 5.6))
    for ax, crop in zip(axs.ravel(), CROPS):
        m = np.load(os.path.join(WORK, f"cellmaps_{crop}.npz"))
        v = m[var].astype(float)
        keep = m["A"] > 500 if var == "snr_heat" else m["R"] > 500
        g = grid_from_cells(m["cells"][keep], v[keep])
        im = ax.imshow(g, extent=EXT, cmap=cmap, norm=TwoSlopeNorm(0, -2, 2), interpolation="nearest")
        B.boundary.plot(ax=ax, color="#888888", lw=0.2)
        panel_extent(ax, None)
        ax.set_title(CROPS[crop]["label"])
    cb = fig.colorbar(im, ax=axs, orientation="horizontal", fraction=0.04, pad=0.03, extend="both")
    cb.set_label(label)
    save(fig, fname, png=True)


# ---------------------------------------------------------------- F03 water deficit level
def f_deficit_map():
    B = borders()
    fig, axs = plt.subplots(2, 2, figsize=(12, 5.6))
    for ax, crop in zip(axs.ravel(), CROPS):
        m = np.load(os.path.join(WORK, f"cellmaps_{crop}.npz"))
        keep = m["A"] > 500
        rain_share = np.where(m["A"] > 0, m["R"] / m["A"], 0)
        g = grid_from_cells(m["cells"][keep], (m["def_R"] * rain_share)[keep])
        im = ax.imshow(g, extent=EXT, cmap="YlOrBr", vmin=0, vmax=0.8, interpolation="nearest")
        B.boundary.plot(ax=ax, color="#888888", lw=0.2)
        panel_extent(ax, None)
        ax.set_title(CROPS[crop]["label"])
    cb = fig.colorbar(im, ax=axs, orientation="horizontal", fraction=0.04, pad=0.03, extend="max")
    cb.set_label("Water hazard 2001-24: rainfed share x seasonal deficit (1 - rain / crop water need)")
    save(fig, "F03_water_hazard_map", png=True)


# ---------------------------------------------------------------- F04 exposure bars
def f_exposure_bars():
    d = pd.read_csv(os.path.join(PROC, "index_components.csv"))
    fig, axs = plt.subplots(1, 4, figsize=(12.5, 5.0), sharey=True)
    for ax, crop in zip(axs, CROPS):
        g = d[d.crop == crop]
        x = np.arange(len(g))
        ax.bar(x - 0.2, g.E_heat, 0.38, color=CC[crop], label="heat")
        ax.bar(x + 0.2, g.E_water, 0.38, color=CC[crop], alpha=0.4, label="water")
        ax.set_xticks(x, [f"{sn(c)} ({k})" for c, k in zip(g.country, g.classes)], fontsize=10.5, rotation=45, ha="right")
        ax.set_title(CROPS[crop]["label"])
        ax.legend(frameon=False, fontsize=11, labels=["heat", "water"])
    axs[0].set_ylabel("Exposure (0-1)")
    save(fig, "F04_exposure_by_country")


# ---------------------------------------------------------------- F05 sensitivity coefficients
def f_sensitivity():
    S = pd.read_csv(os.path.join(PROC, "sensitivity.csv"))
    pool = pd.read_csv(os.path.join(PROC, "sensitivity_pooled.csv"))
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.2))
    y = 0
    ticks, labs = [], []
    for crop in CROPS:
        g = S[S.crop == crop]
        for _, r in g.iterrows():
            vals = [r[f"b_T_{m}"] for m in ("line", "quad", "firs")]
            ax = axs[0]
            ax.plot([min(vals), max(vals)], [y, y], color=CC[crop], lw=2, alpha=0.5)
            ax.plot(np.mean(vals), y, "o", color=CC[crop], ms=6, mfc=CC[crop] if r.T_source == "country" else "white")
            ticks.append(y); labs.append(f"{CROPS[crop]['label']} {sn(r.country)}")
            vw = [r[f"b_W_{m}"] for m in ("line", "quad", "firs")]
            axs[1].plot([min(vw), max(vw)], [y, y], color=CC[crop], lw=2, alpha=0.5)
            axs[1].plot(np.mean(vw), y, "o", color=CC[crop], ms=6, mfc=CC[crop] if r.W_source == "country" else "white")
            y -= 1
        pb = pool[(pool.crop == crop) & (pool.period == "fit 1971-2000")]
        for ax, k in ((axs[0], "b_T"), (axs[1], "b_W")):
            ax.plot(pb[k].mean(), y, "D", color=CC[crop], ms=7)
        ticks.append(y); labs.append(f"{CROPS[crop]['label']} POOLED")
        y -= 1.6
    for ax, t in ((axs[0], "Yield response to +1 C flowering Teff (%)"), (axs[1], "Yield response to +0.1 moisture ratio (%)")):
        ax.axvline(0, color=MUTED, lw=0.8)
        ax.set_yticks(ticks, labs, fontsize=7.5)
        ax.set_xlabel(t)
    axs[1].set_yticklabels([])
    axs[0].set_title("Heat: filled = robust in all 3 detrendings")
    axs[1].set_title("Water: bar = range over 3 detrendings")
    save(fig, "F05_sensitivity_coefficients")


# ---------------------------------------------------------------- F06 importance heatmap
def f_importance():
    d = pd.read_csv(os.path.join(PROC, "index_components.csv"))
    imp = pd.read_csv(os.path.join(PROC, "importance.csv"))
    w = imp[imp.Area == "World"]
    rows, labels = [], []
    for crop in CROPS:
        g = d[d.crop == crop]
        for _, r in g.iterrows():
            rows.append([r.sh_kcal, r.sh_protein, r.sh_fat, r.sh_zinc, r.sh_iron])
            labels.append(f"{CROPS[crop]['label']}: {sn(r.country)}")
        ww = w[w.crop == crop].iloc[0]
        rows.append([ww.sh_kcal, ww.sh_protein, ww.sh_fat, ww.sh_zinc, ww.sh_iron])
        labels.append(f"{CROPS[crop]['label']}: WORLD")
    a = 100 * np.array(rows)
    fig, ax = plt.subplots(figsize=(6.6, 9))
    im = ax.imshow(a, cmap="YlGn", vmin=0, vmax=60, aspect="auto")
    for i in range(a.shape[0]):
        for j in range(a.shape[1]):
            ax.text(j, i, f"{a[i, j]:.0f}", ha="center", va="center", fontsize=7.5, color="white" if a[i, j] > 35 else INK)
    ax.set_xticks(range(5), ["kcal", "protein", "fat", "zinc", "iron"])
    ax.set_yticks(range(len(labels)), labels, fontsize=7.5)
    ax.xaxis.tick_top()
    fig.colorbar(im, ax=ax, fraction=0.04, label="% of national supply from the crop")
    save(fig, "F06_importance_heatmap")


# ---------------------------------------------------------------- F07 adequacy of panel countries
def f_adequacy():
    a = pd.read_csv(os.path.join(PROC, "adequacy.csv"))
    P = pd.read_csv(os.path.join(PROC, "panels.csv"))
    last = a.Year.max()
    x = a[(a.Year.between(last - 2, last)) & a.m49.isin(P.m49.unique())].groupby("Area").mean(numeric_only=True)
    for n in ("kcal", "protein", "fat", "zinc", "iron"):
        x[f"ratio_{n}"] = x[n] / x[f"req_{n}"]
    x = x.sort_values("MAR")
    cols = ["ratio_kcal", "ratio_protein", "ratio_fat", "ratio_zinc", "ratio_iron"]
    fig, axs = plt.subplots(1, 2, figsize=(9, 6), gridspec_kw=dict(width_ratios=[5, 1.2], wspace=0.05))
    ax = axs[0]
    im = ax.imshow(x[cols].values, cmap="RdYlGn", norm=TwoSlopeNorm(1.0, 0.4, 2.5), aspect="auto")
    for i in range(len(x)):
        for j, c in enumerate(cols):
            ax.text(j, i, f"{x[c].iloc[i]:.2f}", ha="center", va="center", fontsize=10.5)
    ax.set_xticks(range(len(cols)), ["energy", "protein", "fat", "zinc", "iron"])
    ax.set_yticks(range(len(x)), [sn(c) for c in x.index], fontsize=11)
    ax.xaxis.tick_top()
    ax.set_title("supply / requirement (1 = just adequate)", fontsize=9.5, fontweight="normal", pad=22)
    ax2 = axs[1]
    ax2.imshow(x[["MAR"]].values, cmap="RdYlGn", vmin=0.6, vmax=1.0, aspect="auto")
    for i in range(len(x)):
        ax2.text(0, i, f"{x.MAR.iloc[i]:.3f}", ha="center", va="center", fontsize=10.5)
    ax2.set_xticks([0], ["MAR"]); ax2.xaxis.tick_top(); ax2.set_yticks([])
    ax2.set_title("capped mean", fontsize=9.5, fontweight="normal", pad=22)
    fig.colorbar(im, ax=axs, fraction=0.03, label="supply / requirement")
    save(fig, "F07_adequacy_panel")


# ---------------------------------------------------------------- F08 crop index forms
def f_index():
    c = pd.read_csv(os.path.join(PROC, "index_crop.csv"))
    forms = [("F1_multiplicative", "F1  E x S x I"), ("F2_geometric", "F2  (E S I)^1/3"),
             ("F3_additive", "F3  (E+S+I)/3"), ("F4_hazard_paired", "F4  hazard-paired x I")]
    fig, axs = plt.subplots(2, 4, figsize=(13, 5.2))
    for row, (a, lab) in enumerate((("eq", "equal-weighted"), ("pw", "production-weighted"))):
        for ax, (f, t) in zip(axs[row], forms):
            v = c.set_index("crop")[f"{f}_{a}"].reindex(list(CROPS))
            v = v / v.max()
            ax.bar(range(4), v, color=[CC[k] for k in CROPS])
            for i, k in enumerate(CROPS):
                ax.text(i, v[k] + 0.02, int(c.set_index("crop").loc[k, f"rank_{f}_{a}"]), ha="center", fontsize=9)
            ax.set_xticks(range(4), [CROPS[k]["label"] for k in CROPS], fontsize=8)
            ax.set_ylim(0, 1.15)
            ax.set_title(t if row == 0 else "", fontsize=10)
            if ax is axs[row][0]:
                ax.set_ylabel(f"{lab}\n(relative to top crop)")
    save(fig, "F08_index_forms")


# ---------------------------------------------------------------- F09 country index heatmap
def f_country_index():
    d = pd.read_csv(os.path.join(PROC, "index_components.csv"))
    fig, axs = plt.subplots(1, 4, figsize=(13, 4.4), sharey=False)
    vmax = d.F4_hazard_paired.max()
    for ax, crop in zip(axs, CROPS):
        g = d[d.crop == crop].sort_values("F4_hazard_paired")
        ax.barh(range(len(g)), g.F4_hazard_paired, color=CC[crop])
        ax.set_yticks(range(len(g)), [f"{sn(c)} ({k})" for c, k in zip(g.country, g.classes)], fontsize=11)
        ax.set_xlim(0, vmax * 1.05)
        ax.set_title(CROPS[crop]["label"])
        ax.set_xlabel("F4 index value")
    save(fig, "F09_country_index")


# ---------------------------------------------------------------- F10 Monte Carlo ranks
def f_montecarlo():
    m = pd.read_csv(os.path.join(PROC, "index_montecarlo.csv"))
    fig, axs = plt.subplots(1, 4, figsize=(13, 3.3), sharey=True)
    shades = ["#1a1a1a", "#666666", "#aaaaaa", "#dddddd"]
    for ax, f in zip(axs, ["F1_multiplicative", "F2_geometric", "F3_additive", "F4_hazard_paired"]):
        g = m[m.form == f].set_index("crop").reindex(list(CROPS))
        left = np.zeros(4)
        for r in range(1, 5):
            v = g[str(r)].values
            ax.barh(range(4), v, left=left, color=shades[r - 1], label=f"rank {r}", edgecolor="white", lw=1)
            left += v
        ax.set_yticks(range(4), [CROPS[k]["label"] for k in CROPS])
        ax.set_title(f.split("_")[0] + " " + f.split("_", 1)[1].replace("_", "-"), fontsize=10)
        ax.set_xlabel("share of 2000 draws")
    axs[0].invert_yaxis()
    h, l = axs[-1].get_legend_handles_labels()
    fig.legend(h, l, frameon=False, fontsize=9, loc="lower center", ncol=4)
    fig.subplots_adjust(bottom=0.27)
    save(fig, "F10_montecarlo_ranks")


# ---------------------------------------------------------------- F11 Zhao
def f_zhao():
    v = pd.read_csv(os.path.join(PROC, "val_zhao.csv")).set_index("measure")
    z = {k: -ZHAO[k][0] for k in CROPS}
    picks = [("F4_hazard_paired (equal-weighted)", "Full index F4"),
             ("climate part E x S (hazard-paired, no I)", "Climate part E x S (no I)"),
             ("heat part E_heat x S_heat", "Heat part only"), ("pooled empirical -b_T (%/C)", "Our pooled heat loss (%/C)")]
    fig, axs = plt.subplots(1, 4, figsize=(14, 3.6), gridspec_kw=dict(wspace=0.35))
    for ax, (k, t) in zip(axs, picks):
        r = v.loc[k]
        for crop in CROPS:
            ax.scatter(z[crop], r[crop], s=80, color=CC[crop], zorder=3)
            ax.annotate(CROPS[crop]["label"], (z[crop], r[crop]), xytext=(6, 4), textcoords="offset points", fontsize=9)
        ax.set_xlabel("Zhao et al. 2017 yield loss (%/C)")
        ax.set_title(f"{t}\nSpearman rho = {r.rho:+.1f} (n = 4)", fontsize=10)
    for ax, yl in zip(axs, ("Index score (higher = more vulnerable)", "Climate-part score (E x S)",
                            "Heat-part score (E_heat x S_heat)", "Our yield loss per \u00b0C of warming (%)")):
        ax.set_ylabel(yl, fontsize=9)
    save(fig, "F11_zhao_validation")


# ---------------------------------------------------------------- F12 shocks
def f_shocks():
    v = pd.read_csv(os.path.join(PROC, "val_shocks.csv"))
    t = pd.read_csv(os.path.join(PROC, "val_shocks_test.csv")).set_index("predictor")
    fig, axs = plt.subplots(1, 2, figsize=(11, 4))
    ax = axs[0]
    for crop in CROPS:
        g = v[v.crop == crop]
        ax.scatter(g.ES_paired, 100 * g.shock_freq_recent, s=55, color=CC[crop], label=CROPS[crop]["label"], zorder=3)
        for _, r in g.iterrows():
            if r.ES_paired > 0.25 or r.shock_freq_recent > 0.15:          # label only the outliers
                ax.annotate(f"{CROPS[crop]['label']} {sn(r.country)}", (r.ES_paired, 100 * r.shock_freq_recent),
                            xytext=(-4, 5), textcoords="offset points", fontsize=7.5, ha="right")
    ax.set_xlabel("Climate part of index (hazard-paired E x S)")
    ax.set_ylabel("Shock years 2001-24 (% of years)")
    ax.set_title(f"rho = {t.loc['ES_paired','rho']:+.2f}, permutation p = {t.loc['ES_paired','p_perm_one_sided']:.3f} (n = {int(t.loc['ES_paired','n'])})", fontsize=10)
    ax.legend(frameon=False, fontsize=8)
    ax = axs[1]
    g = v.sort_values("oos_skill_r", na_position="first")
    ax.barh(range(len(g)), g.oos_skill_r.fillna(0), color=[CC[c] for c in g.crop])
    for i, val in enumerate(g.oos_skill_r):
        if not np.isfinite(val):
            ax.text(0.01, i, "no response detected -> no prediction", va="center", fontsize=7, color=MUTED)
    ax.set_yticks(range(len(g)), [f"{CROPS[c]['label']} {sn(k)}" for c, k in zip(g.crop, g.country)], fontsize=7)
    ax.axvline(0, color=MUTED, lw=0.8)
    ax.set_xlabel("r(predicted, observed yield anomaly), 2001-24")
    ax.set_title("Out-of-sample skill of the fitted climate response", fontsize=10)
    axs[1].set_ylabel("Crop and country")
    save(fig, "F12_shock_validation")


# ---------------------------------------------------------------- F13 yield -> supply pass-through
def f_passthrough():
    h = pd.read_csv(os.path.join(PROC, "yield_diet_historical.csv"))
    fig, ax = plt.subplots(figsize=(8, 6.5))
    y = 0
    ticks, labs = [], []
    for crop in CROPS:
        for c in h[h.crop == crop].country.unique():
            for meth, mk, off in (("old", "o", 0.15), ("new", "s", -0.15)):
                r = h[(h.crop == crop) & (h.country == c) & (h.fbs == meth)]
                if len(r):
                    r = r.iloc[0]
                    ax.plot(r.beta_kcal, y + off, mk, color=CC[crop], ms=7, mfc=CC[crop] if r.p_kcal < 0.05 else "white")
            ticks.append(y); labs.append(f"{CROPS[crop]['label']} {sn(c)}")
            y -= 1
        y -= 0.5
    ax.axvline(0, color=MUTED, lw=0.8)
    ax.axvline(1, color=MUTED, lw=0.8, ls=":")
    ax.set_xlim(-2.5, 5.2)
    ax.set_yticks(ticks, labs, fontsize=8)
    ax.set_xlabel("% change in the crop's food-energy supply per 1 % yield anomaly")
    ax.plot([], [], "o", color=INK, label="FBS 1961-2013 (n = 53; Russia 22)")
    ax.plot([], [], "s", color=INK, label="FBS 2010-2023 (n = 14)")
    ax.plot([], [], "o", color=INK, mfc="white", label="open = p >= 0.05")
    ax.legend(frameon=False, fontsize=8, loc="lower right")
    save(fig, "F13_yield_supply_passthrough")


# ---------------------------------------------------------------- F14 scenario
def f_scenario():
    s = pd.read_csv(os.path.join(PROC, "yield_diet_scenarios.csv"))
    s3 = s[s.scenario.str.startswith("S3")]
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.8), gridspec_kw=dict(wspace=0.55))
    g = s3.sort_values("dkcal_pct_upper")
    lab = [f"{CROPS[c]['label']} {sn(k)}" for c, k in zip(g.crop, g.country)]
    axs[0].barh(range(len(g)), g.dkcal_pct_upper, color=[CC[c] for c in g.crop])
    axs[0].set_yticks(range(len(g)), lab, fontsize=7)
    axs[0].set_xlabel("% change in TOTAL national kcal supply")
    axs[0].set_title("A -10 % yield shock: energy supply (no trade buffer)", fontsize=10)
    g = s3.sort_values("dMAR_pts_upper")
    lab = [f"{CROPS[c]['label']} {sn(k)}" for c, k in zip(g.crop, g.country)]
    axs[1].barh(np.arange(len(g)) + 0.2, g.dMAR_pts_upper, 0.4, color=[CC[c] for c in g.crop], label="no trade buffer")
    axs[1].barh(np.arange(len(g)) - 0.2, g.dMAR_pts_lower, 0.4, color=[CC[c] for c in g.crop], alpha=0.4, label="exports absorb loss")
    axs[1].set_yticks(range(len(g)), lab, fontsize=7)
    axs[1].set_xlabel("change in Mean Adequacy Ratio (points out of 100)")
    axs[1].set_title("A -10 % yield shock: nutrient adequacy", fontsize=10)
    axs[1].legend(frameon=False, fontsize=8)
    save(fig, "F14_scenario_shock")


# ---------------------------------------------------------------- F15 example series
def f_examples():
    cs = pd.read_pickle(os.path.join(PROC, "country_series.pkl"))
    qcl = pd.read_pickle(os.path.join(WORK, "qcl_4crops.pkl"))
    ex = [("rice", 356, "Rice, India"), ("maize", 840, "Maize, USA"), ("wheat", 356, "Wheat, India"), ("soybean", 32, "Soybean, Argentina")]
    fig, axs = plt.subplots(2, 2, figsize=(11, 6.4), gridspec_kw=dict(wspace=0.35, hspace=0.5))
    for ax, (crop, m49, t) in zip(axs.ravel(), ex):
        y = qcl[(qcl.crop == crop) & (qcl.m49 == m49) & (qcl.Element == "Yield")].set_index("Year").Value.loc[1971:2024]
        tt = y.index.values.astype(float)
        fit = np.polyval(np.polyfit(tt, y.values, 1), tt)
        ya = 100 * (y.values - fit) / fit
        c = cs[(cs.crop == crop) & (cs.m49 == m49)].set_index("year").loc[1971:2024]
        drv = c.teff_flow if crop in ("rice", "maize", "wheat") else c.mr_rainfed
        dd = drv.values - np.polyval(np.polyfit(tt, drv.values, 1), tt)
        z = lambda v: (v - v.mean()) / v.std()
        ax.bar(tt, z(ya), color=CC[crop], alpha=0.6, width=0.8, label="yield anomaly")
        ax.plot(tt, z(dd), color=INK, lw=1.2, label="flowering-season temperature anomaly" if crop in ("rice", "maize", "wheat") else "moisture-ratio anomaly")
        ax.set_ylabel("standardised anomaly (z)", fontsize=8)
        ax.legend(frameon=False, fontsize=7.5, loc="lower left", ncol=2)
        r = np.corrcoef(ya, dd)[0, 1]
        ax.set_title(f"{t}   r = {r:+.2f}", fontsize=10)
        ax.axvspan(1971, 2000.5, color="#eeeeee", zorder=0)
    save(fig, "F15_example_series")


# ---------------------------------------------------------------- F16 Myers check
def f_myers():
    v = pd.read_csv(os.path.join(PROC, "val_myers.csv")).set_index("crop").reindex(list(CROPS))
    fig, axs = plt.subplots(1, 3, figsize=(12, 3.4), sharey=True)
    for ax, n in zip(axs, ("zinc", "protein", "iron")):
        ax.bar(range(4), v[f"at_risk_{n}_pp"], color=[CC[k] for k in CROPS])
        ax.set_xticks(range(4), [f"{CROPS[k]['label']}\n({v.loc[k,'photo']})" for k in CROPS], fontsize=8)
        ax.set_title(f"{n}", fontsize=10)
    axs[0].set_ylabel("supply share x Myers decline\n(% of national supply at risk)")
    save(fig, "F16_myers_check")


# =================================================================== SLIDE VERSIONS (simplified, large fonts)
LABELS.update({
    "F05s_sensitivity_pooled": (None, None),
    "F06s_importance_summary": ("Nutrient", "Crop"),
    "F08s_index_F4": ("Crop", None),
    "F13s_passthrough_by_crop": ("% change in the crop's food-energy supply per 1% yield anomaly", "Crop"),
    "F14s_scenario_top": (None, "Crop and country"),
})


def f_sens_slide():
    pool = pd.read_csv(os.path.join(PROC, "sensitivity_pooled.csv"))
    pool = pool[pool.period == "fit 1971-2000"]
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.6))
    for ax, (k, pk, ttl, yl) in zip(axs, (("b_T", "p_T", "Heat", "Yield change (%) for +1 \u00b0C\nflowering-season temperature"),
                                          ("b_W", "p_W", "Water", "Yield change (%) for +0.1 in moisture ratio\n(rain \u00f7 crop water need)"))):
        for i, crop in enumerate(CROPS):
            g = pool[pool.crop == crop]
            m, lo, hi, pmax = g[k].mean(), g[k].min(), g[k].max(), g[pk].max()
            clear = pmax < 0.05 and np.sign(lo) == np.sign(hi)
            ax.bar(i, m, color=CC[crop], alpha=1.0 if clear else 0.35, edgecolor=CC[crop], hatch=None if clear else "//")
            ax.plot([i, i], [lo, hi], color=INK, lw=1.6)
            ax.text(i + 0.46, m, f"{m:+.1f}%" + ("" if clear else "\nnot clear"), ha="left", va="center", fontsize=11)
        ax.axhline(0, color=MUTED, lw=0.8)
        ax.set_xticks(range(4), [CROPS[c]["label"] for c in CROPS])
        ax.set_title(ttl)
        ax.set_ylabel(yl)
        ax.set_xlabel("Crop")
        ax.margins(y=0.25, x=0.15)
    save(fig, "F05s_sensitivity_pooled")


def f_importance_slide():
    imp = pd.read_csv(os.path.join(PROC, "importance.csv"))
    d = pd.read_csv(os.path.join(PROC, "index_components.csv"))
    w = imp[imp.Area == "World"].set_index("crop")
    nuts = ["kcal", "protein", "fat", "zinc", "iron"]
    rows, labels = [], []
    for crop in CROPS:
        rows.append([w.loc[crop, f"sh_{n}"] for n in nuts]); labels.append(f"{CROPS[crop]['label']}: world")
    for crop in CROPS:
        g = d[d.crop == crop]
        rows.append([g[f"sh_{n}"].mean() for n in nuts]); labels.append(f"{CROPS[crop]['label']}: panel-country average")
    a = 100 * np.array(rows)
    fig, ax = plt.subplots(figsize=(7.8, 5.0))
    im = ax.imshow(a, cmap="YlGn", vmin=0, vmax=40, aspect="auto")
    for i in range(a.shape[0]):
        for j in range(a.shape[1]):
            ax.text(j, i, f"{a[i, j]:.0f}", ha="center", va="center", fontsize=12, color="white" if a[i, j] > 25 else INK)
    ax.axhline(3.5, color="white", lw=4)
    ax.set_xticks(range(5), ["calories", "protein", "fat", "zinc", "iron"])
    ax.set_yticks(range(len(labels)), labels)
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position("top")
    fig.colorbar(im, ax=ax, fraction=0.04, label="% of the nutrient supplied by the crop")
    save(fig, "F06s_importance_summary")


def f_index_slide():
    c = pd.read_csv(os.path.join(PROC, "index_crop.csv")).set_index("crop")
    fig, axs = plt.subplots(1, 2, figsize=(10.5, 4.4), sharey=True)
    for ax, (a, ttl) in zip(axs, (("eq", "Every country counts equally\n(vulnerability across climates)"),
                                 ("pw", "Countries weighted by production\n(share of world supply at risk)"))):
        v = c["F4_hazard_paired_" + a].reindex(list(CROPS))
        v = v / v.max()
        ax.bar(range(4), v, color=[CC[k] for k in CROPS])
        for i, k in enumerate(CROPS):
            ax.text(i, v[k] + 0.02, f"rank {int(c.loc[k, 'rank_F4_hazard_paired_' + a])}", ha="center", fontsize=12)
        ax.set_xticks(range(4), [CROPS[k]["label"] for k in CROPS])
        ax.set_ylim(0, 1.18)
        ax.set_title(ttl, fontsize=13)
    axs[0].set_ylabel("F4 index relative to the\nmost vulnerable crop (1 = highest)")
    save(fig, "F08s_index_F4")


def f_passthrough_slide():
    h = pd.read_csv(os.path.join(PROC, "yield_diet_historical.csv"))
    h = h[h.fbs == "old"]
    fig, ax = plt.subplots(figsize=(9, 4.6))
    rng = np.random.default_rng(3)
    for i, crop in enumerate(CROPS):
        g = h[h.crop == crop]
        nsig = 0
        for j, (_, r) in enumerate(g.sort_values("beta_kcal").iterrows()):
            y = -i + 0.22 * ((j % 3) - 1)
            sig = r.p_kcal < 0.05
            ax.plot(r.beta_kcal, y, "o", color=CC[crop], ms=9, mfc=CC[crop] if sig else "white", mew=1.6)
            if sig:
                ax.annotate(sn(r.country), (r.beta_kcal, y), xytext=(0, 10 if nsig % 2 == 0 else -17), textcoords="offset points",
                            ha="center", fontsize=10)
                nsig += 1
    ax.axvline(0, color=MUTED, lw=0.8)
    ax.axvline(1, color=MUTED, lw=0.8, ls=":")
    ax.set_yticks([-i for i in range(4)], [CROPS[c]["label"] for c in CROPS])
    ax.set_ylim(-3.6, 0.6)
    ax.plot([], [], "o", color=INK, label="statistically clear (p < 0.05)")
    ax.plot([], [], "o", color=INK, mfc="white", mew=1.6, label="not clear")
    ax.legend(frameon=False, loc="lower right")
    save(fig, "F13s_passthrough_by_crop")


def f_scenario_slide():
    s = pd.read_csv(os.path.join(PROC, "yield_diet_scenarios.csv"))
    s3 = s[s.scenario.str.startswith("S3")].sort_values("dMAR_pts_upper").head(8).iloc[::-1]
    lab = [f"{CROPS[c]['label']}: {sn(k)}" for c, k in zip(s3.crop, s3.country)]
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.6), gridspec_kw=dict(wspace=0.75))
    axs[0].barh(range(len(s3)), s3.dkcal_pct_upper, color=[CC[c] for c in s3.crop])
    axs[0].set_yticks(range(len(s3)), lab)
    axs[0].set_xlabel("% change in the country's TOTAL calorie supply")
    axs[0].set_title("Calories", fontsize=13)
    axs[1].barh(np.arange(len(s3)) + 0.2, s3.dMAR_pts_upper, 0.4, color=[CC[c] for c in s3.crop], label="no help from trade")
    axs[1].barh(np.arange(len(s3)) - 0.2, s3.dMAR_pts_lower, 0.4, color=[CC[c] for c in s3.crop], alpha=0.4, label="exports absorb part of the loss")
    axs[1].set_yticks(range(len(s3)), lab)
    axs[1].set_xlabel("Change in adequacy score MAR (points out of 100)")
    axs[1].set_title("Nutrient adequacy", fontsize=13)
    axs[1].legend(frameon=False, loc="lower left", fontsize=10)
    save(fig, "F14s_scenario_top")



# =================================================================== SLIDE VERSIONS v3
LABELS.update({
    "F02c_heat_stress_map": ("Longitude", "Latitude"),
    "F05c_sensitivity_by_country": ("Sensitivity score S (0-1)", "Country"),
    "F17_country_crop_matrix": ("Crop", "Country"),
    "F13c_passthrough_clear": ("% change in the crop's food-energy supply per 1% yield anomaly", None),
    "F14c_scenario_simple": ("Change in adequacy score MAR after a 10% yield loss (points out of 100)", None),
})


def f_heat_level_map():
    B = borders()
    fig, axs = plt.subplots(2, 2, figsize=(12, 5.6))
    for ax, crop in zip(axs.ravel(), CROPS):
        m = np.load(os.path.join(WORK, f"cellmaps_{crop}.npz"))
        keep = m["A"] > 500
        g = grid_from_cells(m["cells"][keep], m["heat_R"][keep].astype(float))
        # cells with crop but no exceedance are drawn pale grey so "zero" is visible, not blank
        base = grid_from_cells(m["cells"][keep], np.zeros(keep.sum()))
        ax.imshow(base, extent=EXT, cmap=ListedColormap(["#e4e4e4"]), interpolation="nearest")
        im = ax.imshow(np.where(g > 0.01, g, np.nan), extent=EXT, cmap="YlOrRd", vmin=0, vmax=4, interpolation="nearest")
        B.boundary.plot(ax=ax, color="#888888", lw=0.2)
        panel_extent(ax, None)
        share = float((m["heat_R"][keep] > 0.01).mean())
        ax.set_title(f"{CROPS[crop]['label']}  ({100 * share:.0f}% of crop cells above the limit)", fontsize=11.5)
    cb = fig.colorbar(im, ax=axs, orientation="horizontal", fraction=0.04, pad=0.03, extend="max")
    cb.set_label("Heat stress 2001-24: degrees (\u00b0C) by which flowering-season temperature exceeds the crop's heat limit (grey = crop grows, no excess)")
    save(fig, "F02c_heat_stress_map", png=True)


def f_sens_country():
    S = pd.read_csv(os.path.join(PROC, "sensitivity.csv"))
    fig, axs = plt.subplots(1, 4, figsize=(13.5, 4.4), sharex=True)
    for ax, crop in zip(axs, CROPS):
        g = S[S.crop == crop].iloc[::-1]
        y = np.arange(len(g))
        ax.barh(y + 0.2, g.S_heat, 0.38, color="#555555")
        ax.barh(y - 0.2, g.S_water, 0.38, color="#bbbbbb")
        ax.set_yticks(y, [sn(c) for c in g.country])
        ax.set_xlim(0, 1)
        ax.set_title(CROPS[crop]["label"])
    fig.legend([plt.Rectangle((0, 0), 1, 1, color="#555555"), plt.Rectangle((0, 0), 1, 1, color="#bbbbbb")],
               ["heat sensitivity (dark)", "water sensitivity (light)"], frameon=False, loc="lower center", ncol=2,
               bbox_to_anchor=(0.5, -0.09))
    save(fig, "F05c_sensitivity_by_country")


def f_country_matrix():
    d = pd.read_csv(os.path.join(PROC, "index_components.csv"))
    sh = pd.read_csv(os.path.join(PROC, "shared_panel.csv")).country.tolist()
    v = d[d.country.isin(sh)].pivot(index="country", columns="crop", values="F4_hazard_paired").reindex(columns=list(CROPS))
    v = v.loc[v.max(axis=1).sort_values(ascending=False).index]
    fig, ax = plt.subplots(figsize=(7.6, 4.6))
    a = v.values
    im = ax.imshow(a, cmap="YlOrBr", vmin=0, vmax=np.nanmax(a), aspect="auto")
    for i in range(a.shape[0]):
        rk = pd.Series(a[i]).rank(ascending=False).astype(int).values
        for j in range(a.shape[1]):
            ax.text(j, i, f"{a[i, j]:.3f}\n(#{rk[j]})", ha="center", va="center", fontsize=11,
                    color="white" if a[i, j] > 0.6 * np.nanmax(a) else INK)
    ax.set_xticks(range(4), [CROPS[c]["label"] for c in CROPS])
    ax.set_yticks(range(len(v)), [sn(c) for c in v.index])
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position("top")
    fig.colorbar(im, ax=ax, fraction=0.04, label="F4 index (higher = more vulnerable)")
    save(fig, "F17_country_crop_matrix")


def f_passthrough_clear():
    h = pd.read_csv(os.path.join(PROC, "yield_diet_historical.csv"))
    h = h[(h.fbs == "old") & (h.p_kcal < 0.05) & (h.beta_kcal > 0)].sort_values("beta_kcal")
    fig, ax = plt.subplots(figsize=(8.4, 4.4))
    ax.barh(range(len(h)), h.beta_kcal, color=[CC[c] for c in h.crop])
    ax.set_yticks(range(len(h)), [f"{CROPS[c]['label']}: {sn(k)}" for c, k in zip(h.crop, h.country)])
    ax.axvline(1, color=MUTED, lw=0.9, ls=":")
    ax.text(1.02, 0.2, "1 = one-for-one", color=MUTED, fontsize=10)
    for i, v in enumerate(h.beta_kcal):
        ax.text(v + 0.03, i, f"{v:.2f}", va="center", fontsize=10.5)
    ax.set_xlim(0, 2.2)
    save(fig, "F13c_passthrough_clear")


def f_scenario_simple():
    s = pd.read_csv(os.path.join(PROC, "yield_diet_scenarios.csv"))
    x = s[s.scenario.str.startswith("S3")].sort_values("dMAR_pts_upper").head(6).iloc[::-1]
    fig, ax = plt.subplots(figsize=(9, 4.2))
    ax.barh(range(len(x)), x.dMAR_pts_upper, color=[CC[c] for c in x.crop])
    ax.set_yticks(range(len(x)), [f"{CROPS[c]['label']}: {sn(k)}" for c, k in zip(x.crop, x.country)])
    for i, (_, r) in enumerate(x.iterrows()):
        ax.text(r.dMAR_pts_upper - 0.01, i, f"calories {r.dkcal_pct_upper:+.1f}%", va="center", ha="right", fontsize=10.5)
    ax.set_xlim(x.dMAR_pts_upper.min() * 1.9, 0.02)
    save(fig, "F14c_scenario_simple")



def main():
    for f in (f_panels, lambda: f_shift_maps("snr_heat", "F02a_heat_shift_map", "Warming of flowering-window Teff, 2001-24 vs 1971-2000 (in baseline SDs)", "RdBu_r"),
              lambda: f_shift_maps("snr_water", "F02b_water_shift_map", "Drying of moisture ratio P/ETc on rainfed area (in baseline SDs; + = drier)", "BrBG_r"),
              f_deficit_map, f_exposure_bars, f_sensitivity, f_importance, f_adequacy, f_index, f_country_index,
              f_montecarlo, f_zhao, f_shocks, f_passthrough, f_scenario, f_examples, f_myers,
              f_sens_slide, f_importance_slide, f_index_slide, f_passthrough_slide, f_scenario_slide,
              f_heat_level_map, f_sens_country, f_country_matrix, f_passthrough_clear, f_scenario_simple):
        try:
            f()
        except FileNotFoundError as e:
            print("skip (input missing):", e)
    print("figures in", FIG)


if __name__ == "__main__":
    main()
