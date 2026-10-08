import csv
import os

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from config import CROPS, FIG, PROC, TEX, ZHAO

matplotlib.rcParams.update({
    "font.size": 13,
    "font.family": "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.05,
    "axes.titlesize": 14,
    "axes.titleweight": "bold",
    "xtick.labelsize": 11.5,
    "ytick.labelsize": 11.5,
    "axes.labelsize": 12.5
})

CROP_COLORS = {"rice": "#2a7f62", "wheat": "#c8961a", "maize": "#c0504d", "soybean": "#5b5ea6"}
CROP_LABELS = [CROPS[c]["label"] for c in CROPS]
s_temperature = np.array([CROPS[c]["heat_slope"] for c in CROPS])
ky_water = np.array([CROPS[c]["ky"] for c in CROPS])
S_temp_normalized = s_temperature / s_temperature.max()
S_water_normalized = ky_water / ky_water.max()


def save_figure(figure_obj, figure_name):
    figure_obj.savefig(os.path.join(FIG, figure_name + ".pdf"), dpi=200)
    plt.close(figure_obj)


rows_temp_table = []
rows_water_table = []
for crop_idx, crop_name in enumerate(CROPS):
    crop_info = CROPS[crop_name]
    limit_temp_str = "--" if crop_name == "rice" else f"{crop_info['tcrit'] + 1.0 / crop_info['heat_slope']:.0f}"
    rows_temp_table.append(
        f"{crop_info['label']} & {crop_info['tcrit']:.0f} & {limit_temp_str} & {100.0 * s_temperature[crop_idx]:.1f} & {S_temp_normalized[crop_idx]:.2f} \\\\"
    )
    rows_water_table.append(
        f"{crop_info['label']} & {ky_water[crop_idx]:.2f} & {S_water_normalized[crop_idx]:.2f} \\\\"
    )

latex_temp_table = (
    "\\begin{tabular}{lcccc}\n\\toprule\n"
    "Crop & $T_{crit}$ & $T_{lim}$ & loss per \\si{\\celsius} (\\%) & $S^{T}$\\\\\n\\midrule\n"
    + "\n".join(rows_temp_table)
    + "\n\\bottomrule\n\\end{tabular}\n"
)
latex_water_table = (
    "\\begin{tabular}{lcc}\n\\toprule\n"
    "Crop & $K_y$ & $S^{P}$\\\\\n\\midrule\n"
    + "\n".join(rows_water_table)
    + "\n\\bottomrule\n\\end{tabular}\n"
)

output_tex_dir = os.path.join(TEX, "generated")
os.makedirs(output_tex_dir, exist_ok=True)
with open(os.path.join(output_tex_dir, "tab_lit_sens.tex"), "w", encoding="utf-8") as f:
    f.write(latex_temp_table)
with open(os.path.join(output_tex_dir, "tab_lit_sens_temp.tex"), "w", encoding="utf-8") as f:
    f.write(latex_temp_table)
with open(os.path.join(output_tex_dir, "tab_lit_sens_water.tex"), "w", encoding="utf-8") as f:
    f.write(latex_water_table)

fig_lit, axes_lit = plt.subplots(1, 2, figsize=(10.5, 4.3))
for ax, values, scores, title_text, y_label_text in (
    (axes_lit[0], 100.0 * s_temperature, S_temp_normalized, "Temperature", "Yield lost per °C above the heat limit (%)"),
    (axes_lit[1], ky_water, S_water_normalized, "Precipitation", "FAO water factor $K_y$")
):
    ax.bar(range(4), values, color=[CROP_COLORS[c] for c in CROPS])
    for i in range(4):
        ax.text(i, values[i] * 1.02, f"S = {scores[i]:.2f}", ha="center", va="bottom", fontsize=11.5)
    ax.set_xticks(range(4), CROP_LABELS)
    ax.set_ylim(0, values.max() * 1.22)
    ax.set_title(title_text)
    ax.set_ylabel(y_label_text)
    ax.set_xlabel("Crop")
save_figure(fig_lit, "F05l_literature_sensitivity")

pooled_rows = []
with open(os.path.join(PROC, "sensitivity_pooled.csv"), mode="r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row["period"] == "fit 1971-2000":
            pooled_rows.append({
                "crop": row["crop"],
                "b_T": float(row["b_T"]),
                "p_T": float(row["p_T"])
            })

fig_check, ax_check = plt.subplots(figsize=(8.6, 4.6))
bar_width = 0.36
for crop_idx, crop_name in enumerate(CROPS):
    b_T_vals = [r["b_T"] for r in pooled_rows if r["crop"] == crop_name]
    p_T_vals = [r["p_T"] for r in pooled_rows if r["crop"] == crop_name]
    mean_val, min_val, max_val = float(np.mean(b_T_vals)), float(np.min(b_T_vals)), float(np.max(b_T_vals))
    is_robust = max(p_T_vals) < 0.05 and np.sign(min_val) == np.sign(max_val)
    
    ax_check.bar(
        crop_idx - bar_width / 2.0,
        mean_val,
        bar_width,
        color=CROP_COLORS[crop_name],
        alpha=1.0 if is_robust else 0.35,
        hatch=None if is_robust else "//",
        edgecolor=CROP_COLORS[crop_name]
    )
    ax_check.plot([crop_idx - bar_width / 2.0] * 2, [min_val, max_val], color="#222222", lw=1.6)
    
    zhao_val, zhao_se = ZHAO[crop_name]
    ax_check.bar(crop_idx + bar_width / 2.0, zhao_val, bar_width, color="#888888")
    if zhao_se:
        ax_check.plot([crop_idx + bar_width / 2.0] * 2, [zhao_val - zhao_se, zhao_val + zhao_se], color="#222222", lw=1.6)
        
    ax_check.text(crop_idx - bar_width / 2.0 - 0.02, min(min_val, mean_val) - 0.6, f"{mean_val:+.1f}", ha="right", va="top", fontsize=10.5)
    ax_check.text(crop_idx + bar_width / 2.0 + 0.02, min(zhao_val - (zhao_se or 0), zhao_val) - 0.6, f"{zhao_val:+.1f}", ha="left", va="top", fontsize=10.5)

ax_check.axhline(0, color="#777777", lw=0.8)
ax_check.set_xticks(range(4), CROP_LABELS)
ax_check.set_xlabel("Crop")
ax_check.set_ylabel("Yield change (%) per +1 °C")
ax_check.set_ylim(-20, 3)
ax_check.legend(
    [plt.Rectangle((0, 0), 1, 1, color="#2a7f62"), plt.Rectangle((0, 0), 1, 1, color="#888888")],
    ["our observed yields (hatched = not clear)", "Zhao et al. 2017 (line = 2 SE)"],
    frameon=False,
    loc="lower left",
    fontsize=10
)
save_figure(fig_check, "F05v_data_check")
print("written: F05l, F05v, tab_lit_sens.tex")
print(latex_temp_table)
