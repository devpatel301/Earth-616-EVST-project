"""
33_extension_tables.py -- LaTeX tables, macros and figures for the research extensions (report sections on
future literature coverage, parameter evidence, elevated-CO2 nutrient quality, diversity after losses).
Reads only extension outputs (28-32) and established result tables. Writes docs/nine_crop/generated/ext_*.tex,
docs/nine_crop/generated/numbers_ext.tex and figures/nine_crop/X*.pdf/png.
"""
import os
import sys

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
import ext_common as E  # noqa: E402
from config import CROP_ORDER, CROPS, FIG, ROOT_DIR, TEX  # noqa: E402

matplotlib.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10.5, "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": "#8a8984", "axes.labelcolor": "#52514e", "xtick.color": "#52514e", "ytick.color": "#52514e",
    "axes.titlesize": 12, "axes.titleweight": "bold", "axes.titlecolor": "#0b0b0b", "text.color": "#0b0b0b",
    "axes.grid": False, "savefig.bbox": "tight", "savefig.pad_inches": 0.06, "figure.facecolor": "white",
})
GRID = "#e4e3df"
INK2 = "#52514e"
GEN = os.path.join(TEX, "generated")
os.makedirs(GEN, exist_ok=True)
os.makedirs(FIG, exist_ok=True)
NUT_LABEL = {"kcal": "Energy", "protein": "Protein", "fat": "Fat", "zinc": "Zinc", "iron": "Iron"}
LABEL = {c: CROPS[c]["label"] for c in CROPS}
LABEL["rapeseed"] = "Rapeseed-mustard"
LABEL["bean"] = "Common bean"
MACROS = {}


def tex_escape(s):
    s = str(s)
    for a, b in (("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"), ("$", r"\$"), ("#", r"\#"), ("_", r"\_"),
                 ("{", r"\{"), ("}", r"\}"), ("~", r"\textasciitilde{}"), ("^", r"\textasciicircum{}")):
        s = s.replace(a, b)
    return s.replace("–", "--").replace("—", "---").replace("−", "-")


def plot_area(a):
    a = E.fix_area(a)
    return {"United States of America": "USA", "China, mainland": "China", "Russian Federation": "Russia",
            "United Republic of Tanzania": "Tanzania"}.get(a, a)


def short_area(a):
    """LaTeX form (sources are ASCII-only)."""
    return plot_area(a).replace("ü", "\\\"u")


def macro(name, value, fmt=None):
    """LaTeX control sequences cannot contain digits: 'co2Ind...' becomes 'cotwoInd...', 'scrV0...' 'scrVzero...'."""
    import re
    words = {"0": "zero", "1": "one", "2": "two", "3": "three", "4": "four", "5": "five", "6": "six", "7": "seven", "8": "eight", "9": "nine"}
    name = re.sub(r"\d", lambda m: words[m.group(0)], name)
    text = fmt.format(value) if fmt else str(value)
    if re.match(r"^[+-]\d", text):
        MACROS[name + "Abs"] = text[1:]            # magnitude, for sentences that already say "lowers by"
    MACROS[name] = re.sub(r"(?<![\w$\\-])-(?=\d)", r"\\ensuremath{-}", text)      # typographic minus, valid in text and math


def minus(x):
    """Plain hyphen before a digit -> typographic minus (not in math mode, not in ranges such as 546--550)."""
    import re
    s = re.sub(r"(?<![\w$\\-])-(?=\d)", "$-$", str(x))
    return re.sub(r"(?:\+|\$-\$)(0\.0+)(?!\d)", r"\1", s)      # no signed zeros such as -0.00 or +0.00


def write_table(name, header, rows, colspec, caption=None):
    lines = [r"\begin{tabular}{" + colspec + "}", r"\toprule", " & ".join(header) + r" \\", r"\midrule"]
    lines += [" & ".join(minus(x) for x in r) + r" \\" for r in rows]
    lines += [r"\bottomrule", r"\end{tabular}"]
    with open(os.path.join(GEN, name), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def fmt_pct(v, nd=2):
    return "--" if pd.isna(v) else f"{v:+.{nd}f}"


# ---------------------------------------------------------------- diversity after losses
def diversity():
    d = pd.read_csv(E.P("diversity_after_losses.csv"))
    base = d[d.scenario.str.startswith("baseline")].set_index("Area")
    ind = d[d.Area == "India"]
    sc_order = [("A", "wheat"), ("A", "rice"), ("A", "chickpea"), ("A", "bean"), ("B", None), ("C", None), ("C'", None), ("D", "primary")]
    rows = []
    for key, sub in sc_order:
        if key == "A":
            r = ind[ind.scenario.str.startswith("A ") & (ind.bound == "upper") & (ind.crop == sub)]
            lab = f"A: {LABEL[sub]} $-10\\%$"
        elif key == "B":
            r = ind[ind.scenario.str.startswith("B ")]
            lab = "B: all nine $-10\\%$ (stress test)"
        elif key == "C":
            r = ind[ind.scenario.str.startswith("C future")]
            lab = "C: future climate, loss-only (hybrid)"
        elif key == "C'":
            r = ind[ind.scenario.str.startswith("C' ")]
            lab = "C$'$: same, present-relative"
        else:
            r = ind[ind.scenario.str.startswith("D ") & ind.scenario.str.contains("(primary)", regex=False)]
            lab = "D: C + elevated CO$_2$ quality"
        if r.empty:
            continue
        r = r.iloc[0]
        rows.append([lab] + [f"{r[f'pct_total_{n}']:+.2f} / {r[f'd_eff_{n}']:+.2f}" for n in ("kcal", "protein", "zinc", "iron")]
                    + [f"{100 * r.d_MAR:+.2f}"])
    write_table("ext_div_india.tex", ["Scenario (India)", "Energy", "Protein", "Zinc", "Iron", "$\\Delta$MAR"],
                rows, "@{}lrrrrr@{}")
    b = base.loc["India"]
    macro("divIndBaseEffKcal", b.eff_kcal, "{:.1f}")
    macro("divIndBaseEffIron", b.eff_iron, "{:.1f}")
    macro("divIndBaseTopKcal", b.top_share_kcal * 100, "{:.0f}")
    macro("divIndBaseTopIron", b.top_share_iron * 100, "{:.0f}")
    w = ind[ind.scenario.str.startswith("A ") & (ind.bound == "upper") & (ind.crop == "wheat")].iloc[0]
    macro("divIndWheatIronPct", w.pct_total_iron, "{:+.2f}")
    macro("divIndWheatIronEff", w.eff_iron, "{:.2f}")
    macro("divIndWheatIronDEff", w.d_eff_iron, "{:+.2f}")
    bb = ind[ind.scenario.str.startswith("B ")].iloc[0]
    for n in ("kcal", "zinc", "iron"):
        macro(f"divIndB{n.capitalize()}Pct", bb[f"pct_total_{n}"], "{:+.1f}")
        macro(f"divIndB{n.capitalize()}DEff", bb[f"d_eff_{n}"], "{:+.2f}")
    macro("divIndBMAR", 100 * bb.d_MAR, "{:+.2f}")
    dd = ind[ind.scenario.str.startswith("D ") & ind.scenario.str.contains("(primary)", regex=False)].iloc[0]
    for n in ("zinc", "iron"):
        macro(f"divIndD{n.capitalize()}Pct", dd[f"pct_total_{n}"], "{:+.2f}")
        macro(f"divIndD{n.capitalize()}DEff", dd[f"d_eff_{n}"], "{:+.2f}")
    macro("divIndDMAR", 100 * dd.d_MAR, "{:+.2f}")
    macro("divWorldEffKcal", base.loc["World", "eff_kcal"], "{:.1f}")
    macro("divWorldEffIron", base.loc["World", "eff_iron"], "{:.1f}")

    def sc_row(area, prefix, bound=None, crop=None):
        x = d[(d.Area == area) & d.scenario.str.startswith(prefix)]
        if bound:
            x = x[x.bound == bound]
        if crop:
            x = x[x.crop == crop]
        return x.iloc[0]
    for tag, area in (("Bd", "Bangladesh"), ("Cn", "China, mainland"), ("Ru", "Russian Federation"), ("Tz", "United Republic of Tanzania"),
                      ("Mm", "Myanmar"), ("Ua", "Ukraine")):
        b_ = base.loc[area]
        macro(f"div{tag}EffKcal", b_.eff_kcal, "{:.1f}")
        macro(f"div{tag}TopKcalShare", 100 * b_.top_share_kcal, "{:.0f}")
        macro(f"div{tag}TopIronShare", 100 * b_.top_share_iron, "{:.0f}")
        rb = sc_row(area, "B ")
        rc = sc_row(area, "C future")
        for n in ("kcal", "iron"):
            macro(f"div{tag}B{n.capitalize()}Pct", rb[f"pct_total_{n}"], "{:+.2f}")
            macro(f"div{tag}B{n.capitalize()}DEff", rb[f"d_eff_{n}"], "{:+.2f}")
            macro(f"div{tag}C{n.capitalize()}Pct", rc[f"pct_total_{n}"], "{:+.2f}")
            macro(f"div{tag}C{n.capitalize()}DEff", rc[f"d_eff_{n}"], "{:+.2f}")
    macro("divBdTopKcalName", str(base.loc["Bangladesh", "top_kcal"]).replace(" and products", "").lower())
    cc_ = pd.read_csv(E.P("crop_contrib.csv"))
    cc_ = cc_[cc_.Year.isin(E.latest_years())].groupby(["crop", "m49"]).mean(numeric_only=True)
    macro("divArgSoyKcalShare", 100 * cc_.loc[("soybean", 32), "sh_kcal"], "{:.1f}")
    macro("divFrRapeKcalShare", 100 * cc_.loc[("rapeseed", 250), "sh_kcal"], "{:.1f}")
    macro("divItRiceKcalShare", 100 * cc_.loc[("rice", 380), "sh_kcal"], "{:.1f}")
    # Tanzania: the bean share against the 1/N_eff threshold that decides the sign of the diversity change
    items_tz, _ = E.baseline_items(E.latest_years(), [834])
    tot_tz = items_tz[E.NUTRIENTS].clip(lower=0).sum()
    mt = E.diversity_metrics(items_tz)
    bean_tz = items_tz[items_tz.Item == "Beans"].iloc[0]
    macro("divTzBeanIronShare", 100 * bean_tz.iron / tot_tz.iron, "{:.1f}")
    macro("divTzBeanKcalShare", 100 * bean_tz.kcal / tot_tz.kcal, "{:.1f}")
    macro("divTzThreshIron", 100 / mt["eff_iron"], "{:.1f}")
    macro("divTzThreshKcal", 100 / mt["eff_kcal"], "{:.1f}")
    # cross-country table: B and C for energy and iron
    rows = []
    for area in base.index:
        if area == "World":
            continue
        rb = d[(d.Area == area) & d.scenario.str.startswith("B ")]
        rc = d[(d.Area == area) & d.scenario.str.startswith("C future")]
        if rb.empty:
            continue
        rb, rc = rb.iloc[0], rc.iloc[0]
        n_crops = len(str(rb.crops_shocked).split(";"))
        rows.append((area, [short_area(area), str(n_crops), f"{base.loc[area, 'eff_kcal']:.1f}",
                            f"{rb.pct_total_kcal:+.2f}", f"{rb.d_eff_kcal:+.2f}", f"{rb.pct_total_iron:+.2f}", f"{rb.d_eff_iron:+.2f}",
                            f"{rc.pct_total_iron:+.2f}", f"{rc.d_eff_iron:+.2f}", f"{100 * rc.d_MAR:+.2f}"]))
    rows = [r for _, r in sorted(rows, key=lambda x: x[0])]
    write_table("ext_div_countries.tex",
                ["Country", "Crops", "$N_{\\text{eff}}$ energy", "B energy \\%", "B $\\Delta N$", "B iron \\%", "B $\\Delta N$",
                 "C iron \\%", "C $\\Delta N$", "C $\\Delta$MAR"], rows, "@{}lrrrrrrrrr@{}")
    # which crops are modelled in each country, which have a loss in scenario C, which gains are left out
    panels_ = pd.read_csv(E.P("panels.csv"))
    crop_short = {c: LABEL[c].replace("Rapeseed-mustard", "rapeseed").replace("Common bean", "bean").lower() for c in LABEL}
    rows = []
    for area in sorted(set(panels_.country), key=lambda a: plot_area(a)):
        g = panels_[panels_.country == area]
        rc = d[(d.Area == area) & d.scenario.str.startswith("C future")]
        if rc.empty:
            continue
        rc = rc.iloc[0]
        loss = [x for x in str(rc.crops_shocked).split(";") if x and x != "nan"]
        gain = [x for x in str(rc.gains_excluded).split(";") if x and x != "nan"]
        rows.append([short_area(area), str(len(g)), ", ".join(crop_short[c] for c in g.crop), ", ".join(crop_short[c] for c in loss) or "none",
                     ", ".join(crop_short[c] for c in gain) or "none"])
    write_table("ext_div_coverage.tex", ["Country", "Pairs", "Crops modelled", "Loss applied in C", "Gain left out of C"], rows,
                "@{}lrp{4.6cm}p{3.6cm}p{3.0cm}@{}")
    # divergence counts
    s = d[~d.scenario.str.startswith("baseline") & ~(d.scenario.str.startswith("A ") & (d.bound == "lower"))]
    s = s[~s.scenario.str.startswith("D ") | s.scenario.str.contains("(primary)", regex=False)]
    tot_down = up = 0
    for n in E.NUTRIENTS:
        down = s[f"pct_total_{n}"] < -1e-9
        tot_down += int(down.sum())
        up += int((down & (s[f"d_eff_{n}"] > 1e-9)).sum())
    macro("divNCases", tot_down)
    macro("divNUp", up)
    macro("divPctUp", 100 * up / tot_down, "{:.0f}")
    # figure: % change in total vs change in effective number, energy and iron, scenarios B and C
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.9))
    styles = {"B ": ("#2a78d6", "o", "B: every modelled crop of the country $-10\\%$ (stress test)"),
              "C future": ("#eb6834", "s", "C: future climate, loss-only (hybrid reference)")}
    for ax, n in zip(axes, ("kcal", "iron")):
        placed = []
        for pre, (col, mk, lab) in styles.items():
            x = d[d.scenario.str.startswith(pre)]
            x = x[x[f"pct_total_{n}"] < -1e-6]
            ax.scatter(x[f"pct_total_{n}"], x[f"d_eff_{n}"], s=46, color=col, marker=mk, edgecolor="white", linewidth=1.2, label=lab, zorder=3)
            for _, r in x.sort_values(f"pct_total_{n}").iterrows():
                px, py = r[f"pct_total_{n}"], r[f"d_eff_{n}"]
                if not (r.Area == "India" or px < -3.0):
                    continue
                dy = 4
                for qx, qy in placed:   # stagger labels that would sit on top of each other
                    if abs(qx - px) < 0.9 and abs(qy - py) < 0.06:
                        dy -= 12
                placed.append((px, py))
                if pre.startswith("C") and r.Area == "India":
                    ax.annotate("India (C)", (px, py), xytext=(-22, -26), textcoords="offset points", fontsize=8.5, color=INK2,
                                fontweight="bold", ha="right", arrowprops={"arrowstyle": "-", "color": INK2, "lw": 0.8})
                    continue
                ax.annotate(plot_area(r.Area), (px, py), xytext=(5, dy),
                            textcoords="offset points", fontsize=8.5, color=INK2, fontweight="bold" if r.Area == "India" else "normal")
        ax.axhline(0, color="#8a8984", lw=0.9)
        ax.set_xlabel(f"Change in national {NUT_LABEL[n].lower()} supply (%)")
        ax.set_ylabel("Change in effective number of sources $e^H$")
        ax.set_title(NUT_LABEL[n], loc="left")
        ax.grid(color=GRID, lw=0.8)
        ax.set_axisbelow(True)
        ax.text(0.98, 0.97, "above 0: remaining sources\nmore even", transform=ax.transAxes, va="top", ha="right", fontsize=8.5, color=INK2)
        ax.text(0.02, 0.03, "below 0: less even", transform=ax.transAxes, va="bottom", fontsize=8.5, color=INK2)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=2, fontsize=9, frameon=False, bbox_to_anchor=(0.5, -0.02))
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(FIG, f"X04_diversity_vs_supply.{ext}"), dpi=200)
    plt.close(fig)


# ---------------------------------------------------------------- elevated-CO2 nutrient quality
CITE = {"Myers": "myers2014", "Medek": "medek2017", "Hogy": "hogy2010", "Parvin": "parvin2019", "Smith": "smith2018",
        "Saha": "saha2015", "Jin": "jin2019", "ter Haar": "terhaar2025", "Bagudam": "bagudam2023"}


def cite_of(src):
    for k, v in CITE.items():
        if str(src).startswith(k):
            return v
    return None


def ppm_clean(v):
    import re
    s = re.sub(r"\s*\([^)]*\)", "", str(v)).replace("+/-", "$\\pm$").replace("~", "$\\approx$")
    return s.replace("-", "--").replace("; ", ", ")


def co2():
    f = pd.read_csv(E.P("co2_effects_selected.csv"))
    res = pd.read_csv(E.P("co2_nutrient_results.csv"))
    cov = pd.read_csv(E.P("co2_coverage.csv")).set_index("Area")
    mat = pd.read_csv(E.P("co2_coverage_matrix.csv")).set_index("crop")
    sc = {"primary": "primary", "extended": "extended", "extended_wet": "extended (wet season)", "extended_dry": "extended (dry season)",
          "not used": "not used"}
    order = {"primary": 0, "extended": 1, "extended_wet": 2, "extended_dry": 3, "not used": 4}
    f["o"] = f["set"].map(order)
    f["c_o"] = f["crop"].map({k: i for i, k in enumerate(CROP_ORDER)})
    def ci_text(r):
        v = r["pct_change"]
        if pd.isna(v):
            return "size not reported"
        if r["ci_available"]:
            return f"{v:+.1f} ({r['ci_low']:+.1f}, {r['ci_high']:+.1f})"
        return f"{v:+.1f} (CI not reported)"
    f["ci"] = f.apply(ci_text, axis=1)
    f["sig"] = f.significant.astype(str).str.split(r"[ (]").str[0]
    ff = f[f["set"].isin(["primary", "extended", "extended_wet", "extended_dry"])].sort_values(["o", "c_o", "nutrient"])
    rows = []
    for _, r in ff.iterrows():
        k = cite_of(r.source)
        rows.append([LABEL[r.crop], NUT_LABEL[r.nutrient], r.ci, r.sig, f"{ppm_clean(r.co2_elevated_ppm)} / {ppm_clean(r.co2_ambient_ppm)}",
                     r.exposure_system.split(" (")[0].split(":")[0][:30], f"\\citet{{{k}}}", tex_escape(sc[r['set']])])
    write_table("ext_co2_params.tex", ["Crop", "Nutrient", "Change \\% (95\\% CI)", "Signif.", "CO$_2$ elev. / amb. (ppm)", "System", "Source", "Set"],
                rows, "@{}llllllll@{}")
    prim = f[f["set"] == "primary"]
    fr = pd.read_csv(E.P("future_yield_reference_periods.csv"))
    macro("refMeanHybrid", fr.dY_hybrid_pct.mean(), "{:+.1f}")
    macro("refMeanPresent", fr.dY_present_relative_pct.mean(), "{:+.1f}")
    macro("refMeanObserved", fr.dY_already_observed_pct.mean(), "{:+.1f}")
    macro("refShareOccurred", 100 * fr.dY_already_observed_pct.mean() / fr.dY_hybrid_pct.mean(), "{:.0f}")
    macro("co2NPrimary", len(prim))
    macro("co2NPrimarySig", int(prim.significant_bool.sum()))
    macro("co2NPrimaryNs", int((~prim.significant_bool).sum()))
    macro("co2NExtended", int(f["set"].isin(["extended", "extended_wet", "extended_dry"]).sum()))

    def code(v):
        v = str(v)
        if v.startswith("primary: significant"):
            return "\\textbf{S}"
        if v.startswith("primary: nonsig"):
            return "\\textbf{n.s.}"
        if v.startswith("extended"):
            return "ext."
        if v.startswith("not used"):
            return "rev."
        return "n/e"
    rows = [[LABEL[c]] + [code(mat.loc[c, n]) for n in E.NUTRIENTS] for c in CROP_ORDER if c in mat.index]
    write_table("ext_co2_matrix.tex", ["Crop"] + [NUT_LABEL[n] for n in E.NUTRIENTS], rows, "@{}lccccc@{}")
    flat = [code(mat.loc[c, n]) for c in mat.index for n in E.NUTRIENTS]
    macro("co2CellsTotal", len(flat))
    macro("co2CellsPrimary", sum(x.startswith("\\textbf") for x in flat))
    macro("co2CellsExt", sum(x == "ext." for x in flat))
    macro("co2CellsRev", sum(x == "rev." for x in flat))
    macro("co2CellsNE", sum(x == "n/e" for x in flat))

    med = cov.drop(index="World")
    def covrow(label, src, agg):
        cells = [label]
        for n in E.NUTRIENTS:
            cells.append(f"{100 * agg(src[f'covered_share_{n}']):.0f}" if n in ("protein", "zinc", "iron") else "0")
        for n in ("fat", "zinc", "iron"):
            cells.append(f"{100 * agg(src[f'uncovered_study_crop_share_{n}']):.0f}")
        return cells
    rows = [covrow("India", cov.loc["India"], lambda x: x), covrow("World", cov.loc["World"], lambda x: x),
            covrow("Median of 20 countries", med, lambda x: x.median())]
    rows.insert(0, ["", "Energy", "Protein", "Fat", "Zinc", "Iron", "Fat", "Zinc", "Iron"])
    write_table("ext_co2_supplycov.tex", ["", "\\multicolumn{5}{c}{Supply with a CO$_2$ effect applied (\\%)}",
                                          "\\multicolumn{3}{c}{No evidence (\\%)}"],
                rows, "@{}lrrrrrrrr@{}")
    for n in ("protein", "zinc", "iron"):
        macro(f"co2IndCov{n.capitalize()}", 100 * cov.loc["India", f"covered_share_{n}"], "{:.0f}")
        macro(f"co2MedCov{n.capitalize()}", 100 * med[f"covered_share_{n}"].median(), "{:.0f}")
    macro("co2IndUncZinc", 100 * cov.loc["India", "uncovered_study_crop_share_zinc"], "{:.0f}")
    macro("co2IndUncIron", 100 * cov.loc["India", "uncovered_study_crop_share_iron"], "{:.0f}")

    def row(scn, area="India"):
        return res[(res.Area == area) & (res.scenario == scn)].iloc[0]
    hyb = "hybrid 1971-2000 -> 2041-60"
    pre = "present-relative 2001-24 -> 2041-60"
    spec = [("A: climate yield loss only (hybrid)", f"A future yield loss only ({hyb})", None, None),
            ("B: CO$_2$ quality only", "B CO2 concentration only (primary)", "B CO2 concentration only (low)", "B CO2 concentration only (high)"),
            ("C: combined (hybrid)", f"C combined quantity x concentration ({hyb}; primary)", f"C combined quantity x concentration ({hyb}; low)",
             f"C combined quantity x concentration ({hyb}; high)"),
            ("A$'$: yield loss only (present-relative)", f"A future yield loss only ({pre})", None, None),
            ("C$'$: combined (present-relative)", f"C combined quantity x concentration ({pre}; primary)",
             f"C combined quantity x concentration ({pre}; low)", f"C combined quantity x concentration ({pre}; high)")]
    rows = []
    for lab, a, lo, hi in spec:
        r = row(a)
        cells = [lab]
        for n in ("protein", "zinc", "iron"):
            cells.append(f"{r[f'pct_{n}']:+.2f} [{row(lo)[f'pct_{n}']:+.2f}, {row(hi)[f'pct_{n}']:+.2f}]" if lo else f"{r[f'pct_{n}']:+.2f}")
        cells.append(f"{r.composite_pct_protein_zinc_iron:+.2f}")
        cells.append(f"{r.dMAR_pts:+.2f}" + (f" [{row(lo).dMAR_pts:+.2f}, {row(hi).dMAR_pts:+.2f}]" if lo else ""))
        cells.append(f"{r.nar_iron:.3f}")
        rows.append(cells)
    write_table("ext_co2_india.tex", ["Scenario (India)", "Protein \\%", "Zinc \\%", "Iron \\%", "Mean of three \\%", "$\\Delta$MAR (pts)", "Iron NAR"],
                rows, "@{}lrrrrrr@{}")
    macro("co2IndIronNARzero", row("baseline 2021-23").nar_iron, "{:.3f}")
    for tag, a in (("Qty", spec[0][1]), ("Qual", spec[1][1]), ("Comb", spec[2][1]), ("CombPre", spec[4][1])):
        r = row(a)
        for n in ("protein", "zinc", "iron"):
            macro(f"co2Ind{tag}{n.capitalize()}", r[f"pct_{n}"], "{:+.2f}")
        macro(f"co2Ind{tag}MAR", r.dMAR_pts, "{:+.2f}")
        macro(f"co2Ind{tag}IronNAR", r.nar_iron, "{:.3f}")
    for n in ("protein", "zinc", "iron"):
        macro(f"co2IndQualLow{n.capitalize()}", row(spec[1][2])[f"pct_{n}"], "{:+.2f}")
        macro(f"co2IndQualHigh{n.capitalize()}", row(spec[1][3])[f"pct_{n}"], "{:+.2f}")
        macro(f"co2IndCombLow{n.capitalize()}", row(spec[2][2])[f"pct_{n}"], "{:+.2f}")
        macro(f"co2IndCombHigh{n.capitalize()}", row(spec[2][3])[f"pct_{n}"], "{:+.2f}")
    for n in ("protein", "zinc", "iron"):
        macro(f"co2IndRatio{n.capitalize()}", row(spec[1][1])[f"pct_{n}"] / row(spec[0][1])[f"pct_{n}"], "{:.1f}")
        macro(f"co2IndAdd{n.capitalize()}", row(spec[0][1])[f"pct_{n}"] + row(spec[1][1])[f"pct_{n}"], "{:+.2f}")
    # how much of India's quality-only effect falls on wheat and rice (primary set)
    items_in, _ = E.baseline_items(E.latest_years(), [356])
    shares = []
    for n in ("protein", "zinc", "iron"):
        parts = {r.crop: items_in.loc[items_in.Item.isin(E.eligible_items(r.crop)), n].sum() * (r.factor_primary - 1.0)
                 for _, r in f[(f["set"] == "primary") & (f.nutrient == n)].iterrows()}
        shares.append(100 * (parts["wheat"] + parts["rice"]) / sum(parts.values()))
    macro("co2IndWheatRiceMin", min(shares), "{:.0f}")
    macro("co2IndWheatRiceMax", max(shares), "{:.0f}")
    macro("co2IndCombLowMAR", row(spec[2][2]).dMAR_pts, "{:+.2f}")
    macro("co2IndCombHighMAR", row(spec[2][3]).dMAR_pts, "{:+.2f}")
    sw = row("B CO2 concentration only (significant only)")
    macro("co2IndSigOnlyZinc", sw.pct_zinc, "{:+.2f}")
    macro("co2IndSigOnlyProtein", sw.pct_protein, "{:+.2f}")
    ew = row("B CO2 concentration only (extended, wet-season lentil)")
    ed = row("B CO2 concentration only (extended, dry-season lentil)")
    macro("co2IndExtWetProtein", ew.pct_protein, "{:+.2f}")
    macro("co2IndExtWetZinc", ew.pct_zinc, "{:+.2f}")
    macro("co2IndExtDryZinc", ed.pct_zinc, "{:+.2f}")
    macro("co2IndExtDryIron", ed.pct_iron, "{:+.2f}")

    rows, allr = [], []
    for area in sorted(set(res.Area) - {"World"}):
        a, b, c = row(spec[0][1], area), row(spec[1][1], area), row(spec[2][1], area)
        allr.append((area, a, b, c))
        rows.append([short_area(area), f"{a.pct_zinc:+.2f}", f"{b.pct_zinc:+.2f}", f"{c.pct_zinc:+.2f}", f"{a.pct_iron:+.2f}", f"{b.pct_iron:+.2f}",
                     f"{c.pct_iron:+.2f}", f"{c.pct_protein:+.2f}", f"{c.dMAR_pts:+.2f}"])
    write_table("ext_co2_countries.tex", ["Country", "Zn A", "Zn B", "Zn C", "Fe A", "Fe B", "Fe C", "Protein C", "$\\Delta$MAR C"], rows, "@{}lrrrrrrrr@{}")
    macro("co2NZeroQtyQual", sum(1 for _, a, b, c in allr if a.pct_zinc > -0.05 and b.pct_zinc < -1.0))
    macro("co2NCountries", len(allr))
    macro("co2NQualGtQtyZinc", sum(1 for _, a, b, c in allr if abs(b.pct_zinc) > abs(a.pct_zinc)))
    macro("co2NQualGtQtyIron", sum(1 for _, a, b, c in allr if abs(b.pct_iron) > abs(a.pct_iron)))
    zr = sorted(allr, key=lambda t: t[3].pct_zinc)[:3]
    macro("co2TopZincCountries", ", ".join(f"{short_area(t[0])} ({t[3].pct_zinc:+.1f}\\%)" for t in zr))
    wq = row(spec[1][1], "World")
    macro("co2WorldZinc", wq.pct_zinc, "{:+.2f}")
    macro("co2WorldIron", wq.pct_iron, "{:+.2f}")
    macro("co2WorldProtein", wq.pct_protein, "{:+.2f}")
    mar_drop = [(short_area(a_), c.dMAR_pts) for a_, a, b, c in allr if c.dMAR_pts < -0.05]
    macro("co2NMarDrop", len(mar_drop))
    macro("co2MarDropList", ", ".join(x for x, _ in mar_drop))
    macro("co2ZincNARmin", min(res[res.scenario == spec[2][1]].nar_zinc), "{:.3f}")

    fig, axes = plt.subplots(1, 2, figsize=(11.4, 4.9), gridspec_kw={"width_ratios": [1, 1.25]})
    ax = axes[0]
    nuts = ["protein", "zinc", "iron"]
    xs = np.arange(len(nuts))
    w = 0.26
    for j, (lab, key, lo, hi, col) in enumerate((("A: climate yield loss", spec[0][1], None, None, "#8a8984"),
                                                 ("B: CO$_2$ quality", spec[1][1], spec[1][2], spec[1][3], "#1baf7a"),
                                                 ("C: combined", spec[2][1], spec[2][2], spec[2][3], "#2a78d6"))):
        r = row(key)
        v = [r[f"pct_{n}"] for n in nuts]
        ax.bar(xs + (j - 1) * w, v, w * 0.92, color=col, label=lab, zorder=3)
        if lo:
            l = [row(lo)[f"pct_{n}"] for n in nuts]
            h = [row(hi)[f"pct_{n}"] for n in nuts]
            ax.errorbar(xs + (j - 1) * w, v, yerr=[np.array(v) - np.array(l), np.array(h) - np.array(v)], fmt="none", ecolor="#0b0b0b", capsize=3, lw=1.1, zorder=4)
        for xx, vv, n in zip(xs + (j - 1) * w, v, nuts):
            lowv = row(lo)[f"pct_{n}"] if lo else vv
            ax.text(xx, min(vv, lowv) - 0.12, f"{vv:.1f}".replace("-", "−"), ha="center", va="top", fontsize=8.5, color=INK2)
    ax.axhline(0, color="#8a8984", lw=0.9)
    ax.set_xticks(xs)
    ax.set_xticklabels([NUT_LABEL[n] for n in nuts])
    ax.set_ylabel("Change in India's national supply (%)")
    ax.set_title("India", loc="left")
    ax.set_ylim(ax.get_ylim()[0] - 0.9, 0.5)
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    ax = axes[1]
    order_ = sorted(allr, key=lambda t: t[3].pct_zinc, reverse=True)
    ys = np.arange(len(order_))
    ax.hlines(ys, [t[3].pct_zinc for t in order_], [0] * len(order_), color=GRID, lw=2.2, zorder=1)
    ax.scatter([t[1].pct_zinc for t in order_], ys, s=44, color="#8a8984", marker="s", edgecolor="white", linewidth=1.1, label="A: climate yield loss", zorder=3)
    ax.scatter([t[2].pct_zinc for t in order_], ys, s=44, color="#1baf7a", marker="o", edgecolor="white", linewidth=1.1, label="B: CO$_2$ quality", zorder=3)
    ax.scatter([t[3].pct_zinc for t in order_], ys, s=52, color="#2a78d6", marker="D", edgecolor="white", linewidth=1.1, label="C: combined", zorder=4)
    ax.set_yticks(ys)
    ax.set_yticklabels([plot_area(t[0]) for t in order_], fontsize=9)
    ax.set_xlabel("Change in national zinc supply (%)")
    ax.set_title("Zinc, 20 panel countries", loc="left")
    ax.axvline(0, color="#8a8984", lw=0.9)
    ax.grid(axis="x", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    h2, l2 = axes[1].get_legend_handles_labels()     # the right panel carries one marker per scenario
    fig.legend(h2, l2, loc="lower center", ncol=3, fontsize=9, frameon=False, bbox_to_anchor=(0.5, -0.01))
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(FIG, f"X03_co2_quality.{ext}"), dpi=200)
    plt.close(fig)


# ---------------------------------------------------------------- parameter evidence
def parameters():
    reg = pd.read_csv(os.path.join(ROOT_DIR, "docs", "evidence", "parameter_evidence_register.csv"))
    st = reg.status.str.strip()
    ap = reg.applicability.fillna("not assessed").str.strip()
    stat_order = ["published", "derived", "borrowed", "assumption", "unsupported"]
    ap_order = ["good", "partial", "poor", "not assessed"]
    rows = []
    for s_ in stat_order:
        rows.append([s_.capitalize(), str(int((st == s_).sum()))] + [str(int(((st == s_) & (ap == a)).sum())) for a in ap_order])
    rows.append(["All", str(len(reg))] + [str(int((ap == a).sum())) for a in ap_order])
    write_table("ext_param_status.tex", ["Status", "Rows", "Good", "Partial", "Poor", "Not assessed"], rows, "@{}lrrrrr@{}")
    macro("parNRows", len(reg))
    for s_ in stat_order:
        macro(f"parN{s_.capitalize()}", int((st == s_).sum()))
    macro("parNPoor", int((ap == "poor").sum()))
    macro("parNPartial", int((ap == "partial").sum()))
    macro("parNGood", int((ap == "good").sum()))
    rng = reg.range_status.fillna("none").astype(str)
    is_lit = rng.str.startswith("literature range") | rng.str.startswith("treatment range")
    macro("parNExploratory", int((rng.str.contains("exploratory") & ~is_lit).sum()))     # disjoint from the next count
    macro("parNLitRange", int(is_lit.sum()))

    cs = pd.read_csv(E.P("evidence_screened_crops.csv"))
    refs = pd.read_csv(E.P("evidence_screened_references.csv")).set_index("view")
    rows = []
    for crop in CROP_ORDER:
        r = [LABEL[crop]]
        for w in ("eq", "pw"):
            for v in ("V0", "V1", "V2"):
                x = cs[(cs.view == v) & (cs.crop == crop)].iloc[0]
                r.append("unavailable" if pd.isna(x[f"F4_{w}"]) else f"{x[f'F4_{w}']:.4f} ({int(x[f'rank_{w}'])})")
        x2 = cs[(cs.view == "V2") & (cs.crop == crop)].iloc[0]
        r.append(f"{int(x2.n_pairs_available)}/{int(x2.n_pairs_total)}")
        rows.append(r)
    write_table("ext_screened.tex", ["Crop", "V0 eq.", "V1 eq.", "V2 eq.", "V0 prod.", "V1 prod.", "V2 prod.", "V2 pairs"], rows, "@{}lrrrrrrr@{}")
    for v in ("V0", "V1", "V2"):
        for w in ("eq", "pw"):
            top = cs[cs.view == v].sort_values(f"F4_{w}", ascending=False).iloc[0]
            macro(f"scr{v}{w.upper()}Top", LABEL[top.crop])
            macro(f"scr{v}{w.upper()}N", int(cs[cs.view == v][f"F4_{w}"].notna().sum()))
    macro("scrRescale", refs.loc["V1", "F4_rescale_vs_V0"], "{:.3f}")
    macro("scrVTwoHeatMax", f"{refs.loc['V2', 'H_heat']:.2f}")
    macro("scrVZeroHeatMax", f"{refs.loc['V0', 'H_heat']:.2f}")
    macro("scrVTwoHeatPair", refs.loc["V2", "heat_max_pair"].replace("-", " in "))
    macro("scrHeatRatio", refs.loc["V0", "H_heat"] / refs.loc["V2", "H_heat"], "{:.1f}")
    # how much of the headline rests on the unsupported heat slopes (rice, rapeseed)
    comp = pd.read_csv(E.P("index_components.csv"))
    comp["hp"] = 0.5 * comp.E_heat * comp.S_heat * comp.In
    comp["wp"] = 0.5 * comp.E_water * comp.S_water * comp.In
    fc = pd.read_csv(E.P("future_components.csv"))
    for crop, tag in (("rice", "Rice"), ("rapeseed", "Rape"), ("wheat", "Wheat"), ("bean", "Bean")):
        g = comp[comp.crop == crop]
        macro(f"parHeatPres{tag}", 100 * g.hp.sum() / (g.hp.sum() + g.wp.sum()), "{:.2f}" if crop == "rice" else "{:.1f}")
        h = fc[fc.crop == crop]
        macro(f"parHeatFut{tag}", 100 * h.dF4_from_heat.abs().sum() / (h.dF4_from_heat.abs().sum() + h.dF4_from_water.abs().sum()), "{:.0f}")
    pr = pd.read_csv(E.P("evidence_screened_pairs.csv"))
    w_ = pr[(pr.crop == "wheat") & (pr.country == "India")].iloc[0]
    macro("scrWheatIndVzero", w_.F4_V0, "{:.4f}")
    macro("scrWheatIndVtwo", w_.F4_V2, "{:.4f}")


# ---------------------------------------------------------------- future-impact literature coverage
BIBKEY = {"F01": "zhao2017", "F07": "zhao2017", "F11": "zhao2017", "F17": "zhao2017",
          "F02": "jagermeyr2021", "F08": "jagermeyr2021", "F12": "jagermeyr2021", "F18": "jagermeyr2021",
          "F03": "deryng2014", "F13": "deryng2014", "F19": "deryng2014", "F04": "asseng2015", "F05": "nareshkumar2014wheat",
          "F06": "chandran2023", "F10": "chandran2023", "F27": "chandran2023", "F34": "chandran2023", "F09": "soora2013",
          "F14": "tigchelaar2018", "F15": "ramirez2017", "F16": "zilli2020", "F20": "zilli2020", "F21": "walikar2018",
          "F22": "singh2014chickpea", "F23": "singh2014chickpea", "F24": "abera2026", "F25": "qian2026",
          "F26": "chandran2022", "F33": "chandran2022", "F28": "rippke2016", "F35": "rippke2016", "F29": "hummel2018",
          "F30": "heinemann2017", "F31": "antolin2021", "F32": "kadiyala2021", "F36": "qian2019",
          "F37": "nareshkumar2016mustard", "F38": "boomiraj2010", "F39": "pullens2019"}


def first_word(v):
    s = str(v).strip().lower()
    for w in ("both reported", "not modelled", "not stated", "excluded", "included", "both"):
        if s.startswith(w):
            return {"both reported": "both", "not modelled": "not modelled", "not stated": "not stated"}.get(w, w)
    return s.split()[0] if s else "--"


def write_longtable(name, header, rows, colspec, caption, label):
    lines = [r"\begin{longtable}{" + colspec + "}", r"\caption{" + caption + r"}\label{" + label + r"}\\", r"\toprule",
             " & ".join(header) + r" \\", r"\midrule", r"\endfirsthead", r"\toprule", " & ".join(header) + r" \\", r"\midrule", r"\endhead",
             r"\bottomrule", r"\endfoot"]
    lines += [" & ".join(minus(x) for x in r) + r" \\" for r in rows]
    lines += [r"\end{longtable}"]
    with open(os.path.join(GEN, name), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def literature():
    c = pd.read_csv(E.P("future_literature_comparison.csv"))
    cov = pd.read_csv(E.P("future_literature_coverage.csv")).set_index("crop")
    panels = pd.read_csv(E.P("panels.csv"))
    ver = {"consistent": "consistent", "partly consistent": "partly", "different": "different", "not directly comparable": "not comparable"}
    # per-crop coverage table
    rows = []
    for crop in CROP_ORDER:
        g = c[c.crop == crop]
        panel = list(panels[panels.crop == crop].country)
        covered = set()
        for s_ in g.panel_countries_matched.astype(str):
            covered |= {x.strip() for x in s_.split(";") if x.strip() and x.strip().lower() != "none"}
        n_cov = len([p_ for p_ in panel if p_ in covered])
        miss = [short_area(p_) for p_ in panel if p_ not in covered]
        full = int(g.read_level.astype(str).str.contains("full", case=False).sum())
        rows.append([LABEL[crop], str(g.doi.nunique()), str(len(g)), f"{full} / {len(g) - full}", f"{n_cov} of {len(panel)}",
                     " / ".join(str(int((g.consistency == v).sum())) for v in ("consistent", "partly consistent", "different", "not directly comparable")),
                     ", ".join(miss) if miss else "none"])
    write_table("ext_lit_coverage.tex", ["Crop", "Studies", "Rows", "Full / abstract", "Panel countries covered", "Cons. / partly / diff. / n.c.", "Panel countries without a verified study"],
                rows, "@{}lrrrrlp{4.4cm}@{}")
    macro("litNRows", len(c))
    macro("litNStudies", c.doi.nunique())
    macro("litNFull", int(c.read_level.astype(str).str.contains("full", case=False).sum()))
    macro("litNAbstract", int((~c.read_level.astype(str).str.contains("full", case=False)).sum()))
    for v, k in (("consistent", "Cons"), ("partly consistent", "Partly"), ("different", "Diff"), ("not directly comparable", "NC")):
        macro(f"litN{k}", int((c.consistency == v).sum()))
    co2inc = c.co2_fertilisation.astype(str).str.lower().str.startswith(("included", "both"))
    adinc = c.adaptation.astype(str).str.lower().str.startswith(("included", "both"))
    macro("litNCoTwoIncl", int(co2inc.sum()))
    macro("litNAdaptIncl", int(adinc.sum()))
    macro("litNNoCoTwo", int(c.co2_fertilisation.astype(str).str.lower().str.startswith(("excluded", "not modelled")).sum()))
    macro("litNShared", int(c.shared_input.astype(str).str.lower().str.startswith("yes").sum()))
    macro("litNChallenge", int(c.direction.isin(["gain", "mixed"]).sum()))
    miss_total = sum(len(panels[panels.crop == crop]) - len({p_ for p_ in panels[panels.crop == crop].country
                     if any(p_ in {x.strip() for x in str(s_).split(";")} for s_ in c[c.crop == crop].panel_countries_matched)}) for crop in CROP_ORDER)
    macro("litNPairsNoStudy", miss_total)
    macro("litNPairs", len(panels))

    # appendix longtable (all rows)
    rows = []
    for _, r in c.sort_values("id").iterrows():
        k = BIBKEY.get(r["id"])
        rows.append([r["id"], LABEL[r["crop"]], f"\\citet{{{k}}}", tex_escape(r.geography)[:70] if len(str(r.geography)) <= 70 else tex_escape(str(r.geography)[:67]) + "...",
                     f"{first_word(r.co2_fertilisation)} / {first_word(r.adaptation)}", f"{r.direction}; {r.mechanism}",
                     f"{r.our_direction_lit}; {r.our_mechanism_of_F4_change}", ver[r.consistency]])
    write_longtable("ext_lit_rows.tex", ["ID", "Crop", "Study", "Geography", "CO$_2$ / adapt.", "Paper: direction; mechanism", "Ours: yield; F4 driver", "Verdict"],
                    rows, r"@{}p{0.7cm}p{1.5cm}>{\raggedright\arraybackslash}p{2.0cm}>{\raggedright\arraybackslash}p{2.9cm}>{\raggedright\arraybackslash}p{1.9cm}>{\raggedright\arraybackslash}p{2.0cm}>{\raggedright\arraybackslash}p{2.0cm}p{1.3cm}@{}",
                    "Future-impact studies and the comparison (one row per study and crop; CO$_2$ and adaptation columns say whether the paper included them)", "tab:litrows")


# ---------------------------------------------------------------- extension checks and CO2 reference levels
def checks_and_levels():
    ck = pd.read_csv(E.P("extension_checks.csv"))
    macro("extChecksN", len(ck))
    macro("extChecksPassed", int(ck.passed.sum()))
    rows = [[r["id"], tex_escape(r["check"]), "pass" if r.passed else "FAIL", tex_escape(r.detail if str(r.detail) != "nan" else "")[:80]]
            for _, r in ck.iterrows()]
    write_longtable("ext_checks.tex", ["ID", "Check", "Result", "Detail"], rows, "@{}lp{9.0cm}lp{3.8cm}@{}",
                    "Checks of the research extensions (\\file{code/32\\_extension\\_checks.py}). S: synthetic edge cases; R: real outputs against the established tables.",
                    "tab:extchecks")
    lv = pd.read_csv(os.path.join(ROOT_DIR, "docs", "evidence", "co2_reference_levels.csv"))
    import re

    def brk(x):      # let long unbreakable tokens (DOIs, paths) wrap inside narrow columns
        return re.sub(r"(\S{22,})", r"\\seqsplit{\1}", tex_escape(x))
    rows = [[tex_escape(r.quantity), tex_escape(r.value_ppm), tex_escape(r.period), brk(r.source), brk(r.locator)] for _, r in lv.iterrows()]
    write_table("ext_co2_levels.tex", ["Quantity", "ppm", "Period", "Source", "Locator"], rows, "@{}lllp{4.6cm}p{3.6cm}@{}")


def write_macros():
    with open(os.path.join(GEN, "numbers_ext.tex"), "w", encoding="utf-8") as fh:
        for k, v in sorted(MACROS.items()):
            fh.write(f"\\newcommand{{\\{k}}}{{{v}}}\n")


def main():
    diversity()
    co2()
    parameters()
    literature()
    checks_and_levels()
    write_macros()
    print(f"{len(MACROS)} macros written")


if __name__ == "__main__":
    main()
