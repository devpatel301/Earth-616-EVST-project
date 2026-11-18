"""
18_endeval_figures.py -- end-evaluation figures (nine-crop run) -> figures/nine_crop/G*.pdf (+ .png)

Colour rules (validated with the dataviz palette validator, light mode, all pairs): crops are coloured by
GROUP (cereal blue #2a78d6, pulse orange #eb6834, oilseed aqua #1baf7a) and always direct-labelled, so
identity never rests on colour alone; heat red #e34948 vs water violet #6250d6; magnitudes use one blue
ramp; changes use a blue <-> red diverging pair with a grey midpoint. One y-axis per panel.
"""
import os

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap, LogNorm, TwoSlopeNorm

from config import CROP_GROUPS, CROP_ORDER, CROPS, FIG, PROC, ROOT_DIR

matplotlib.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10.5, "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": "#8a8984", "axes.labelcolor": "#52514e", "xtick.color": "#52514e", "ytick.color": "#52514e",
    "axes.titlesize": 12, "axes.titleweight": "bold", "axes.titlecolor": "#0b0b0b", "text.color": "#0b0b0b",
    "axes.grid": False, "savefig.bbox": "tight", "savefig.pad_inches": 0.06, "figure.facecolor": "white",
    "legend.frameon": False,
})
GROUP_COLOR = {"cereal": "#2a78d6", "pulse": "#eb6834", "oilseed": "#1baf7a"}
HEAT, WATER = "#e34948", "#6250d6"
TEXT2, MUTED, GRID = "#52514e", "#8a8984", "#e6e5e1"
BLUES = LinearSegmentedColormap.from_list("blues", ["#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"])
DIVERGE = LinearSegmentedColormap.from_list("div", ["#1c5cab", "#86b6ef", "#f0efec", "#ec8f8e", "#b52b2b"])
CROPS_ORD = [c for c in CROP_ORDER if c in CROPS]
LABEL = {c: CROPS[c]["label"] for c in CROPS}
color_of = lambda c: GROUP_COLOR[CROPS[c]["group"]]
F4 = "F4_hazard_paired"
SHORT = {"United States of America": "USA", "China, mainland": "China", "Russian Federation": "Russia",
         "United Republic of Tanzania": "Tanzania", "Türkiye": "Turkey", "Iran (Islamic Republic of)": "Iran"}
def short(s):
    """FAOSTAT area names are UTF-8 but were read as latin-1 upstream: repair, then shorten to ASCII."""
    if isinstance(s, str) and "Ã" in s:
        s = s.encode("latin-1").decode("utf-8")
    return SHORT.get(s, s)


def save(fig, name):
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(FIG, f"{name}.{ext}"), dpi=200)
    plt.close(fig)
    print("wrote", name)


def group_legend(ax, loc="lower right"):
    handles = [plt.Rectangle((0, 0), 1, 1, color=GROUP_COLOR[g]) for g in GROUP_COLOR]
    ax.legend(handles, ["Cereals", "Pulses", "Oilseeds"], loc=loc, fontsize=9)


def light_grid(ax, axis="x"):
    ax.grid(axis=axis, color=GRID, lw=0.8)
    ax.set_axisbelow(True)


def g01_ranking(crop):
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))
    for ax, wt, title in ((axes[0], "eq", "Equal country weights"), (axes[1], "pw", "Production-weighted")):
        d = crop.sort_values(f"{F4}_{wt}")
        y = np.arange(len(d))
        ax.barh(y, d[f"{F4}_{wt}"], color=[color_of(c) for c in d.crop], height=0.62)
        ax.set_yticks(y, [LABEL[c] for c in d.crop])
        for yi, v in zip(y, d[f"{F4}_{wt}"]):
            ax.text(v, yi, f"  {v:.4f}", va="center", fontsize=8.5, color=TEXT2)
        ax.set_xlim(0, d[f"{F4}_{wt}"].max() * 1.28)
        ax.set_title(title)
        ax.set_xlabel("Vulnerability index F4 (2001–2024)")
        light_grid(ax)
    group_legend(axes[1])
    save(fig, "G01_crop_ranking")


def g02_matrix(comp):
    countries = comp.groupby("country")[F4].max().sort_values(ascending=False).index
    m = comp.pivot_table(index="country", columns="crop", values=F4).reindex(index=countries, columns=CROPS_ORD)
    fig, ax = plt.subplots(figsize=(10.5, 0.42 * len(countries) + 1.6))
    vmin = max(1e-5, np.nanmin(m.values[m.values > 0]))
    im = ax.imshow(np.where(m.values > 0, m.values, np.nan), cmap=BLUES, norm=LogNorm(vmin=vmin, vmax=np.nanmax(m.values)), aspect="auto")
    for i in range(m.shape[0]):
        for j in range(m.shape[1]):
            v = m.values[i, j]
            if np.isnan(v):
                ax.text(j, i, "–", ha="center", va="center", color=MUTED, fontsize=8)
            else:
                dark = v > np.nanmax(m.values) ** 0.5 * vmin ** 0.5
                ax.text(j, i, "<0.0001" if v < 1e-4 else f"{v:.4f}", ha="center", va="center", fontsize=7.5,
                        color="white" if dark else "#0b0b0b")
    ax.set_xticks(range(len(CROPS_ORD)), [LABEL[c] for c in CROPS_ORD], rotation=30, ha="right")
    for t, c in zip(ax.get_xticklabels(), CROPS_ORD):
        t.set_color(color_of(c))
    ax.set_yticks(range(len(countries)), [short(c) for c in countries])
    for s in ax.spines.values():
        s.set_visible(False)
    cb = fig.colorbar(im, ax=ax, shrink=0.7, pad=0.01)
    cb.set_label("F4 (log scale)")
    ax.set_title("Vulnerability by country and crop, 2001–2024 (– = country not in the crop's panel)")
    save(fig, "G02_country_crop_matrix")


def g03_components(comp, crop):
    d = crop.set_index("crop").reindex(CROPS_ORD)
    heat = comp.assign(v=comp.E_heat * comp.S_heat).groupby("crop").v.mean().reindex(CROPS_ORD)
    water = comp.assign(v=comp.E_water * comp.S_water).groupby("crop").v.mean().reindex(CROPS_ORD)
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.2), sharey=True, gridspec_kw={"width_ratios": [1.3, 1, 1]})
    y = np.arange(len(CROPS_ORD))[::-1]
    axes[0].barh(y + 0.19, heat, height=0.36, color=HEAT, label="heat: E_heat × S_heat")
    axes[0].barh(y - 0.19, water, height=0.36, color=WATER, label="water: E_water × S_water")
    axes[0].set_title("Climate part (mean over countries)")
    axes[0].legend(loc="lower right", fontsize=8.5)
    axes[1].barh(y, d.S_heat_eq, height=0.36, color=HEAT, label="S_heat")
    axes[1].barh(y - 0.38, d.S_water_eq, height=0.36, color=WATER, label="S_water")
    axes[1].set_title("Literature sensitivity")
    axes[1].legend(loc="lower right", fontsize=8.5)
    axes[2].barh(y, d.In_eq, height=0.5, color=[color_of(c) for c in CROPS_ORD])
    axes[2].set_title("Importance (normalised)")
    axes[0].set_yticks(y, [LABEL[c] for c in CROPS_ORD])
    for ax in axes:
        light_grid(ax)
    save(fig, "G03_components")


def g04_present_future(fc):
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))
    for ax, wt, title in ((axes[0], "eq", "Equal country weights"), (axes[1], "pw", "Production-weighted")):
        d = fc.set_index("crop").reindex(CROPS_ORD)
        y = np.arange(len(d))[::-1]
        h, f = d[f"F4_{wt}_historical_1971_2000"], d[f"F4_{wt}_future_2041_2060"]
        for yi, a, b, c in zip(y, h, f, d.index):
            ax.plot([a, b], [yi, yi], color=MUTED, lw=1.6, zorder=1)
            ax.scatter([a], [yi], s=46, facecolor="white", edgecolor=color_of(c), lw=1.8, zorder=2)
            ax.scatter([b], [yi], s=52, color=color_of(c), zorder=3, edgecolor="white", lw=1)
        ax.set_yticks(y, [LABEL[c] for c in d.index])
        ax.set_xscale("log")
        ax.xaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter("%g"))
        ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
        ax.set_xlabel("F4 (log scale)")
        ax.set_title(title)
        light_grid(ax)
    axes[1].scatter([], [], s=46, facecolor="white", edgecolor=TEXT2, lw=1.8, label="historical 1971–2000")
    axes[1].scatter([], [], s=52, color=TEXT2, label="2041–2060, MRI-ESM2-0 SSP2-4.5")
    axes[1].legend(loc="lower right", fontsize=8.5)
    save(fig, "G04_present_future_crops")


def g05_future_pairs(fcomp):
    d = fcomp.reindex(fcomp.dF4_abs.abs().sort_values(ascending=False).index).head(20).sort_values("dF4_abs")
    fig, ax = plt.subplots(figsize=(8.5, 6.2))
    y = np.arange(len(d))
    lim = d.dF4_abs.abs().max()
    ax.barh(y, d.dF4_abs, color=[DIVERGE(TwoSlopeNorm(0, -lim, lim)(v)) for v in d.dF4_abs], height=0.65)
    ax.axvline(0, color=MUTED, lw=0.8)
    ax.set_yticks(y, [f"{LABEL[c]} – {short(k)}" for c, k in zip(d.crop, d.country)])
    for yi, v, p in zip(y, d.dF4_abs, d["pct_change"]):
        ax.text(v, yi, (f"  {p:+.0f}%  " if np.isfinite(p) else "  n/a  "), va="center", ha="left" if v >= 0 else "right", fontsize=8, color=TEXT2)
    ax.set_xlim(-lim * 1.35 if d.dF4_abs.min() < 0 else -lim * 0.05, lim * 1.35)
    ax.set_xlabel("Change in F4, 2041–2060 minus 1971–2000 (fixed reference)")
    ax.set_title("Largest changes by crop and country")
    light_grid(ax)
    save(fig, "G05_future_pairs")


def g06_groups(crop, fc):
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.0), sharey=True)
    groups = list(CROP_GROUPS)
    for ax, (label, col_src, col) in zip(axes, (("Present (2001–2024)", crop, f"{F4}_eq"),
                                                ("Future (2041–2060)", fc, "F4_eq_future_2041_2060"))):
        for gi, g in enumerate(groups):
            members = [c for c in CROP_GROUPS[g] if c in CROPS]
            vals = col_src.set_index("crop").loc[members, col]
            ax.barh(gi, vals.mean(), color=GROUP_COLOR[g], height=0.55, alpha=0.35)
            ax.scatter(vals, [gi] * len(vals), color=GROUP_COLOR[g], s=40, zorder=3, edgecolor="white")
            for c, v in vals.items():
                ax.annotate(LABEL[c], (v, gi), xytext=(0, 9), textcoords="offset points", ha="center", fontsize=7.5, color=TEXT2)
        ax.set_yticks(range(len(groups)), ["Cereals", "Pulses", "Oilseeds"])
        ax.set_xlabel("F4, equal weights (bar = mean of the three crops)")
        ax.set_title(label)
        light_grid(ax)
    save(fig, "G06_crop_groups")


def g07_nutrient_profiles(comp):
    nut = ["sh_kcal", "sh_protein", "sh_fat", "sh_zinc", "sh_iron"]
    m = comp.groupby("crop")[nut].mean().reindex(CROPS_ORD) * 100
    fig, ax = plt.subplots(figsize=(7.2, 5.0))
    im = ax.imshow(m.values, cmap=BLUES, aspect="auto", vmin=0)
    for i in range(m.shape[0]):
        for j in range(m.shape[1]):
            v = m.values[i, j]
            ax.text(j, i, f"{v:.1f}", ha="center", va="center", fontsize=8.5, color="white" if v > m.values.max() * 0.55 else "#0b0b0b")
    ax.set_xticks(range(5), ["Energy", "Protein", "Fat", "Zinc", "Iron"])
    ax.set_yticks(range(len(CROPS_ORD)), [LABEL[c] for c in CROPS_ORD])
    for t, c in zip(ax.get_yticklabels(), CROPS_ORD):
        t.set_color(color_of(c))
    for s in ax.spines.values():
        s.set_visible(False)
    fig.colorbar(im, ax=ax, shrink=0.8, pad=0.02).set_label("share of national supply (%), panel mean")
    ax.set_title("What each crop supplies (FBS/SUA 2021–2023)")
    save(fig, "G07_nutrient_profiles")


def g08_shock(sc):
    s3 = sc[sc.scenario.str.startswith("S3")].copy()
    d = s3.sort_values("dMAR_pts_upper").head(18).iloc[::-1]
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.6), sharey=True)
    y = np.arange(len(d))
    axes[0].barh(y, d.dMAR_pts_upper, color=[color_of(c) for c in d.crop], height=0.6, label="no trade buffer")
    axes[0].scatter(d.dMAR_pts_lower, y, marker="|", s=160, color="#0b0b0b", zorder=3, label="exports absorb first")
    axes[0].set_xlabel("Change in MAR (points out of 100)")
    axes[0].set_title("−10 % yield shock: adequacy")
    axes[0].legend(loc="lower left", fontsize=8.5)
    axes[1].barh(y, d.dkcal_pct_upper, color=[color_of(c) for c in d.crop], height=0.6)
    axes[1].set_xlabel("Change in national energy supply (%)")
    axes[1].set_title("−10 % yield shock: energy")
    axes[0].set_yticks(y, [f"{LABEL[c]} – {short(k)}" for c, k in zip(d.crop, d.country)])
    for ax in axes:
        light_grid(ax)
    save(fig, "G08_yield_shock")


def g09_future_yield(fy):
    fig, ax = plt.subplots(figsize=(9, 4.6))
    for i, c in enumerate(CROPS_ORD):
        g = fy[fy.crop == c]
        ax.scatter(g.dY_lit_pct, [i + 0.12] * len(g), color=color_of(c), s=30, edgecolor="white", zorder=3)
        ax.scatter(g.dY_emp_pct, [i - 0.12] * len(g), facecolor="white", edgecolor=color_of(c), s=28, lw=1.3, zorder=3)
    ax.axvline(0, color=MUTED, lw=0.8)
    ax.set_yticks(range(len(CROPS_ORD)), [LABEL[c] for c in CROPS_ORD])
    ax.invert_yaxis()
    ax.scatter([], [], color=TEXT2, s=30, label="literature damage accounting (main)")
    ax.scatter([], [], facecolor="white", edgecolor=TEXT2, s=28, label="empirical coefficients (cross-check)")
    ax.legend(loc="lower left", fontsize=8.5)
    ax.set_xlabel("Conditional yield change, 2041–2060 vs 1971–2000 (%), one dot per country")
    ax.set_title("Climate-driven yield change (no CO2 fertilisation, no adaptation)")
    light_grid(ax)
    save(fig, "G09_future_yield")


def g10_robustness(rob, mc):
    r = rob[(rob.form == F4) & (rob.weighting == "eq")].set_index("test")[[f"rank_{c}" for c in CROPS_ORD]]
    fig, axes = plt.subplots(1, 2, figsize=(13, 0.36 * len(r) + 1.8), gridspec_kw={"width_ratios": [3, 1]})
    ax = axes[0]
    im = ax.imshow(r.values, cmap=LinearSegmentedColormap.from_list("rk", ["#0d366b", "#3987e5", "#cde2fb"]), aspect="auto")
    for i in range(r.shape[0]):
        for j in range(r.shape[1]):
            ax.text(j, i, int(r.values[i, j]), ha="center", va="center", fontsize=8, color="white" if r.values[i, j] <= 3 else "#0b0b0b")
    ax.set_xticks(range(len(CROPS_ORD)), [LABEL[c] for c in CROPS_ORD], rotation=30, ha="right")
    ax.set_yticks(range(len(r)), [t if len(t) < 70 else t[:67] + "…" for t in r.index], fontsize=8)
    ax.set_title("Crop rank under each robustness test (F4, equal weights; 1 = most vulnerable)")
    for s in ax.spines.values():
        s.set_visible(False)
    m = mc[mc.form == F4].set_index("crop").reindex(CROPS_ORD)
    first = m[1.0] if 1.0 in m.columns else m["1"]
    axes[1].barh(range(len(CROPS_ORD))[::-1], first * 100, color=[color_of(c) for c in CROPS_ORD], height=0.6)
    axes[1].set_yticks(range(len(CROPS_ORD))[::-1], [LABEL[c] for c in CROPS_ORD])
    axes[1].set_xlabel("% of 2,000 random weightings ranked first")
    axes[1].set_title("Monte Carlo weights")
    light_grid(axes[1])
    save(fig, "G10_robustness")


def g11_run_comparison(cmp):
    fig, ax = plt.subplots(figsize=(6.2, 5.6))
    for c in cmp.crop.unique():
        g = cmp[cmp.crop == c]
        ax.scatter(g[f"{F4}_mideval"], g[f"{F4}_lit"], color=color_of(c), s=34, label=LABEL[c], edgecolor="white", zorder=3)
    lo = max(1e-8, min(cmp[f"{F4}_mideval"].min(), cmp[f"{F4}_lit"].min()))
    hi = max(cmp[f"{F4}_mideval"].max(), cmp[f"{F4}_lit"].max())
    ax.plot([lo, hi], [lo, hi], color=MUTED, lw=1, ls="--", label="1:1")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("Mid-evaluation F4 (blended sensitivity)")
    ax.set_ylabel("End-evaluation F4 (literature-only sensitivity)")
    ax.set_title("Same 26 pairs, presented method vs mid-eval numbers")
    for _, r in cmp.nlargest(4, f"{F4}_lit").iterrows():
        ax.annotate(f"{LABEL[r.crop]}–{short(r.country)}", (r[f"{F4}_mideval"], r[f"{F4}_lit"]), xytext=(4, -10), textcoords="offset points", fontsize=7.5, color=TEXT2)
    ax.legend(fontsize=8, loc="upper left")
    save(fig, "G11_mideval_vs_literature_only")


def main():
    comp = pd.read_csv(os.path.join(PROC, "index_components.csv"))
    crop = pd.read_csv(os.path.join(PROC, "index_crop.csv"))
    g01_ranking(crop)
    g02_matrix(comp)
    g03_components(comp, crop)
    g07_nutrient_profiles(comp)
    g08_shock(pd.read_csv(os.path.join(PROC, "yield_diet_scenarios.csv")))
    g10_robustness(pd.read_csv(os.path.join(PROC, "index_robustness.csv")), pd.read_csv(os.path.join(PROC, "index_montecarlo.csv")))
    if os.path.exists(os.path.join(PROC, "future_crop.csv")):
        fc = pd.read_csv(os.path.join(PROC, "future_crop.csv"))
        g04_present_future(fc)
        g05_future_pairs(pd.read_csv(os.path.join(PROC, "future_components.csv")))
        g06_groups(crop, fc)
    if os.path.exists(os.path.join(PROC, "future_yield.csv")):
        g09_future_yield(pd.read_csv(os.path.join(PROC, "future_yield.csv")))
    cmp_path = os.path.join(PROC, "compare_mideval_vs_fourcrop.csv")
    if os.path.exists(cmp_path):
        g11_run_comparison(pd.read_csv(cmp_path))


if __name__ == "__main__":
    main()
