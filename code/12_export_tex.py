import os
import re

import numpy as np
import pandas as pd

from config import CLASS_NAME, CROPS, PROC, TEX, WORK, ZHAO, season_kc

OUTPUT_DIR = os.path.join(TEX, "generated")
os.makedirs(OUTPUT_DIR, exist_ok=True)

COUNTRY_SHORT_NAMES = {
    "China, mainland": "China",
    "United States of America": "USA",
    "Russian Federation": "Russia",
    "Iran (Islamic Republic of)": "Iran",
    "Republic of Korea": "S. Korea",
    "South Africa": "S. Africa"
}


def shorten_country_name(country_full_name):
    return COUNTRY_SHORT_NAMES.get(country_full_name, country_full_name)


latex_macros = {}


def register_macro(macro_name, macro_value, format_string="{:.2f}"):
    assert re.fullmatch(r"[A-Za-z]+", macro_name), macro_name
    latex_macros[macro_name] = format_string.format(macro_value) if not isinstance(macro_value, str) else macro_value


def write_tex_file(filename, file_body):
    with open(os.path.join(OUTPUT_DIR, filename), "w", encoding="utf-8") as tex_file:
        tex_file.write(file_body)


def escape_latex_characters(text_string):
    return str(text_string).replace("&", r"\&").replace("%", r"\%").replace("_", r"\_").replace(">=", r"$\geq$")


def get_crop_label(crop_key):
    return CROPS[crop_key]["label"]


def main():
    panels_df = pd.read_csv(os.path.join(PROC, "panels.csv"))
    shared_panel_df = pd.read_csv(os.path.join(PROC, "shared_panel.csv"))
    components_df = pd.read_csv(os.path.join(PROC, "index_components.csv"))
    crop_index_df = pd.read_csv(os.path.join(PROC, "index_crop.csv")).set_index("crop")
    robustness_df = pd.read_csv(os.path.join(PROC, "index_robustness.csv"))
    monte_carlo_df = pd.read_csv(os.path.join(PROC, "index_montecarlo.csv"))
    sensitivity_df = pd.read_csv(os.path.join(PROC, "sensitivity.csv"))
    pooled_sensitivity_df = pd.read_csv(os.path.join(PROC, "sensitivity_pooled.csv"))
    importance_df = pd.read_csv(os.path.join(PROC, "importance.csv"))
    adequacy_df = pd.read_csv(os.path.join(PROC, "adequacy.csv"))
    val_zhao_df = pd.read_csv(os.path.join(PROC, "val_zhao.csv")).set_index("measure")
    val_shocks_df = pd.read_csv(os.path.join(PROC, "val_shocks.csv"))
    val_shocks_test_df = pd.read_csv(os.path.join(PROC, "val_shocks_test.csv")).set_index("predictor")
    val_ray_df = pd.read_csv(os.path.join(PROC, "val_ray.csv")).set_index("crop")
    val_myers_df = pd.read_csv(os.path.join(PROC, "val_myers.csv")).set_index("crop")
    yield_diet_hist_df = pd.read_csv(os.path.join(PROC, "yield_diet_historical.csv"))
    yield_diet_scenarios_df = pd.read_csv(os.path.join(PROC, "yield_diet_scenarios.csv"))
    form_agreement_df = pd.read_csv(os.path.join(PROC, "index_form_agreement.csv"))
    country_shift_df = pd.read_csv(os.path.join(PROC, "country_shift.csv"))

    panel_rows_tex = []
    for crop_name in CROPS:
        crop_subset = panels_df[panels_df.crop == crop_name]
        for row_idx, (_, panel_row) in enumerate(crop_subset.iterrows()):
            crop_label_prefix = get_crop_label(crop_name) if row_idx == 0 else ""
            panel_rows_tex.append(
                f"{crop_label_prefix} & {escape_latex_characters(shorten_country_name(panel_row.country))} & {panel_row['rank']:d} & {panel_row.share_pct:.1f} & "
                f"{panel_row.classes} & {panel_row.elev_m:.0f} & {100*panel_row.kgA:.0f}/{100*panel_row.kgB:.0f}/{100*panel_row.kgC:.0f}/{100*panel_row.kgD:.0f} \\\\"
            )
        panel_rows_tex.append(r"\midrule")
        
    write_tex_file(
        "tab_panels.tex",
        "\\begin{tabular}{llrrlrl}\n\\toprule\n"
        "Crop & Country & Rank & Share (\\%) & Class & Elev. (m) & Crop area in A/B/C/D (\\%)\\\\\n\\midrule\n"
        + "\n".join(panel_rows_tex[:-1]) + "\n\\bottomrule\n\\end{tabular}\n"
    )
    
    register_macro("sharedPanel", ", ".join(shorten_country_name(c) for c in shared_panel_df.country))
    for crop_name in CROPS:
        register_macro(f"panelShare{get_crop_label(crop_name)}", panels_df[panels_df.crop == crop_name].share_pct.sum(), "{:.0f}")

    param_rows_tex = []
    for crop_name in CROPS:
        crop_params = CROPS[crop_name]
        limit_str = (r"35 / --" if crop_name == "rice" else f"{crop_params['tcrit']:.0f} / {crop_params['tcrit'] + 1.0 / crop_params['heat_slope']:.0f}")
        param_rows_tex.append(
            f"{get_crop_label(crop_name)} & {crop_params['photo']} & {limit_str} & {crop_params['heat_slope']:.3f} & {crop_params['ky']:.2f} & "
            f"{crop_params['kc'][0]:.2f}/{crop_params['kc'][1]:.2f}/{crop_params['kc'][2]:.2f} & {season_kc(crop_name):.2f} \\\\"
        )
    write_tex_file(
        "tab_params.tex",
        "\\begin{tabular}{llcccll}\n\\toprule\n"
        "Crop & Path & $T_{crit}/T_{lim}$ (\\si{\\celsius}) & $s^{lit}_{heat}$ (per \\si{\\celsius}) & $K_y$ & $K_c$ ini/mid/end & $\\bar K_c$\\\\\n\\midrule\n"
        + "\n".join(param_rows_tex) + "\n\\bottomrule\n\\end{tabular}\n"
    )

    comp_rows_tex = []
    for crop_name in CROPS:
        crop_comps = components_df[components_df.crop == crop_name]
        for row_idx, (_, comp_row) in enumerate(crop_comps.iterrows()):
            crop_label_prefix = get_crop_label(crop_name) if row_idx == 0 else ""
            comp_rows_tex.append(
                f"{crop_label_prefix} & {escape_latex_characters(shorten_country_name(comp_row.country))} ({comp_row.classes}) & {comp_row.H_heat:.2f} & {comp_row.D_heat:.2f} & "
                f"{100*comp_row.H_water:.1f} & {comp_row.D_water:.2f} & {comp_row.E_heat:.2f} & {comp_row.E_water:.2f} & {comp_row.S_heat:.2f} & "
                f"{comp_row.S_water:.2f} & {100*comp_row.I:.1f} & {comp_row.F4_hazard_paired:.3f} \\\\"
            )
        comp_rows_tex.append(r"\midrule")
        
    write_tex_file(
        "tab_components.tex",
        "\\begin{tabular}{llrrrrrrrrrr}\n\\toprule\n"
        " & & \\multicolumn{2}{c}{Heat} & \\multicolumn{2}{c}{Water} & \\multicolumn{2}{c}{Exposure} & \\multicolumn{2}{c}{Sensitivity} & & \\\\\n"
        "\\cmidrule(lr){3-4}\\cmidrule(lr){5-6}\\cmidrule(lr){7-8}\\cmidrule(lr){9-10}\n"
        "Crop & Country & $L$ (\\si{\\celsius}) & $\\Delta$ (SD) & $L$ (\\%) & $\\Delta$ (SD) & $E_h$ & $E_w$ & $S_h$ & $S_w$ & $I$ (\\%) & $V_{F4}\\\\\n\\midrule\n"
        + "\n".join(comp_rows_tex[:-1]) + "\n\\bottomrule\n\\end{tabular}\n"
    )

    formula_definitions = [
        ("F1_multiplicative", r"F1 $E\cdot S\cdot I$"),
        ("F2_geometric", r"F2 $(E S I)^{1/3}$"),
        ("F3_additive", r"F3 $(E+S+I)/3$"),
        ("F4_hazard_paired", r"F4 paired $\times I$")
    ]
    crop_index_rows_tex = []
    for form_key, form_label in formula_definitions:
        equal_weight_cells = " & ".join(f"{crop_index_df.loc[k, form_key + '_eq']:.3f} ({crop_index_df.loc[k, 'rank_' + form_key + '_eq']})" for k in CROPS)
        prod_weight_cells = " & ".join(f"{crop_index_df.loc[k, form_key + '_pw']:.3f} ({crop_index_df.loc[k, 'rank_' + form_key + '_pw']})" for k in CROPS)
        crop_index_rows_tex.append(f"{form_label} & equal & {equal_weight_cells} \\\\")
        crop_index_rows_tex.append(f" & production & {prod_weight_cells} \\\\")
        
    write_tex_file(
        "tab_crop_index.tex",
        "\\begin{tabular}{llrrrr}\n\\toprule\n"
        "Form & Country weights & Rice & Wheat & Maize & Soybean\\\\\n\\midrule\n"
        + "\n".join(crop_index_rows_tex) + "\n\\bottomrule\n\\end{tabular}\n"
    )

    country_crop_table_order = [
        "United States of America", "Brazil", "India", "China, mainland",
        "Russian Federation", "Argentina", "Bangladesh", "Egypt", "Nigeria", "South Africa"
    ]
    country_crop_rows_tex = []
    for country_full in country_crop_table_order:
        country_display = shorten_country_name(country_full)
        cells = [f"\\textbf{{{country_display}}}"]
        for crop_k in ("rice", "wheat", "maize", "soybean"):
            match = components_df[(components_df.country == country_full) & (components_df.crop == crop_k)]
            if len(match) > 0:
                val = match.iloc[0]["F4_hazard_paired"]
                cells.append(f"{val:.4f}" if val >= 0.0001 else "$<0.0001$")
            else:
                cells.append("--")
        country_crop_rows_tex.append(" & ".join(cells) + " \\\\")
        
    write_tex_file(
        "tab_country_crop_index.tex",
        "\\begin{tabular}{lcccc}\n\\toprule\n"
        "\\textbf{Country} & \\textbf{Rice} & \\textbf{Wheat} & \\textbf{Maize} & \\textbf{Soybean} \\\\\n\\midrule\n"
        + "\n".join(country_crop_rows_tex) + "\n\\bottomrule\n\\end{tabular}\n"
    )

    for crop_key in CROPS:
        register_macro(f"Vfour{get_crop_label(crop_key)}", crop_index_df.loc[crop_key, "F4_hazard_paired_eq"], "{:.3f}")
        register_macro(f"VfourPw{get_crop_label(crop_key)}", crop_index_df.loc[crop_key, "F4_hazard_paired_pw"], "{:.3f}")
        register_macro(f"rankFour{get_crop_label(crop_key)}", int(crop_index_df.loc[crop_key, "rank_F4_hazard_paired_eq"]), "{:d}")
        register_macro(f"rankFourPw{get_crop_label(crop_key)}", int(crop_index_df.loc[crop_key, "rank_F4_hazard_paired_pw"]), "{:d}")
        
    ranking_order_f4_eq = crop_index_df.sort_values("F4_hazard_paired_eq", ascending=False).index
    register_macro("orderFour", " $>$ ".join(get_crop_label(k) for k in ranking_order_f4_eq))
    ranking_order_f4_pw = crop_index_df.sort_values("F4_hazard_paired_pw", ascending=False).index
    register_macro("orderFourPw", " $>$ ".join(get_crop_label(k) for k in ranking_order_f4_pw))
    ranking_order_f1_eq = crop_index_df.sort_values("F1_multiplicative_eq", ascending=False).index
    register_macro("orderOne", " $>$ ".join(get_crop_label(k) for k in ranking_order_f1_eq))

    robustness_f4 = robustness_df[(robustness_df.form == "F4_hazard_paired") & (robustness_df.weighting == "eq")]
    robustness_f1 = robustness_df[(robustness_df.form == "F1_multiplicative") & (robustness_df.weighting == "eq")]
    robustness_rows_tex = [
        f"{escape_latex_characters(row_f4.test)} & {row_f4.order.replace(' > ', ' $>$ ')} & {row_f1.order.replace(' > ', ' $>$ ')} \\\\"
        for (_, row_f4), (_, row_f1) in zip(robustness_f4.iterrows(), robustness_f1.iterrows())
    ]
    write_tex_file(
        "tab_robust.tex",
        "\\begin{tabular}{lll}\n\\toprule\n"
        "Test (one choice changed) & F4 hazard-paired order & F1 multiplicative order\\\\\n\\midrule\n"
        + "\n".join(robustness_rows_tex) + "\n\\bottomrule\n\\end{tabular}\n"
    )

    register_macro("robWheatTopAll", int((robustness_df.top == "wheat").sum()), "{:d}")
    register_macro("robN", len(robustness_df), "{:d}")
    
    for form_key, form_tag in (("F4_hazard_paired", "Four"), ("F1_multiplicative", "One")):
        mc_subset = monte_carlo_df[monte_carlo_df.form == form_key].set_index("crop")
        for crop_key in CROPS:
            register_macro(f"mc{form_tag}{get_crop_label(crop_key)}First", 100.0 * mc_subset.loc[crop_key, "1"], "{:.1f}")
            
    register_macro("tauOneFour", form_agreement_df[(form_agreement_df.a == "F1_multiplicative") & (form_agreement_df.b == "F4_hazard_paired")].tau.iloc[0])
    register_macro("tauOneThree", form_agreement_df[(form_agreement_df.a == "F1_multiplicative") & (form_agreement_df.b == "F3_additive")].tau.iloc[0])

    for crop_key in CROPS:
        pool_fit = pooled_sensitivity_df[(pooled_sensitivity_df.crop == crop_key) & (pooled_sensitivity_df.period == "fit 1971-2000")]
        register_macro(f"poolT{get_crop_label(crop_key)}", pool_fit.b_T.mean(), "{:+.1f}")
        register_macro(f"poolW{get_crop_label(crop_key)}", pool_fit.b_W.mean(), "{:+.1f}")
        register_macro(f"poolTp{get_crop_label(crop_key)}", pool_fit.p_T.max(), "{:.3f}")
        register_macro(f"poolWp{get_crop_label(crop_key)}", pool_fit.p_W.max(), "{:.3f}")
        
    register_macro("nRobustT", int((sensitivity_df.T_source == "country").sum()), "{:d}")
    register_macro("nRobustW", int((sensitivity_df.W_source == "country").sum()), "{:d}")
    
    for crop_key, country_name in (("rice", "India"), ("maize", "United States of America"), ("maize", "South Africa"), ("wheat", "India")):
        sens_record = sensitivity_df[(sensitivity_df.crop == crop_key) & (sensitivity_df.country == country_name)].iloc[0]
        macro_suffix = get_crop_label(crop_key) + re.sub("[^A-Za-z]", "", shorten_country_name(country_name))
        register_macro(f"bT{macro_suffix}", sens_record.b_T_used, "{:+.1f}")
        register_macro(f"bW{macro_suffix}", sens_record.b_W_used, "{:+.1f}")
        
    sensitivity_rows_tex = []
    for crop_key in CROPS:
        crop_sens_subset = sensitivity_df[sensitivity_df.crop == crop_key]
        for row_idx, (_, sens_row) in enumerate(crop_sens_subset.iterrows()):
            crop_label_prefix = get_crop_label(crop_key) if row_idx == 0 else ""
            sensitivity_rows_tex.append(
                f"{crop_label_prefix} & {escape_latex_characters(shorten_country_name(sens_row.country))} & {sens_row.b_T_line:+.1f} & {sens_row.b_T_quad:+.1f} & {sens_row.b_T_firs:+.1f} & "
                f"{sens_row.b_T_used:+.1f} ({sens_row.T_source[0]}) & {sens_row.b_W_line:+.1f} & {sens_row.b_W_quad:+.1f} & {sens_row.b_W_firs:+.1f} & "
                f"{sens_row.b_W_used:+.1f} ({sens_row.W_source[0]}) & {sens_row.r2_full_linear:.2f}\\\\"
            )
        sensitivity_rows_tex.append(r"\midrule")
        
    write_tex_file(
        "tab_sensitivity.tex",
        "\\begin{tabular}{llrrrlrrrlr}\n\\toprule\n"
        " & & \\multicolumn{4}{c}{Heat: \\% yield per +1\\si{\\celsius} $T_{eff}$} & \\multicolumn{4}{c}{Water: \\% yield per +0.1 MR} & \\\\\n"
        "\\cmidrule(lr){3-6}\\cmidrule(lr){7-10}\n"
        "Crop & Country & lin & quad & FD & used & lin & quad & FD & used & $R^2$\\\\\n\\midrule\n"
        + "\n".join(sensitivity_rows_tex[:-1]) + "\n\\bottomrule\n\\end{tabular}\n"
    )

    world_importance = importance_df[importance_df.Area == "World"].set_index("crop")
    for crop_key in CROPS:
        for nutrient_name in ("kcal", "protein", "fat", "zinc", "iron"):
            register_macro(f"world{nutrient_name.capitalize()}{get_crop_label(crop_key)}", 100.0 * world_importance.loc[crop_key, f"sh_{nutrient_name}"], "{:.1f}")
        register_macro(f"worldI{get_crop_label(crop_key)}", 100.0 * world_importance.loc[crop_key, "I"], "{:.1f}")
        
    bangladesh_rice_imp = importance_df[(importance_df.Area == "Bangladesh") & (importance_df.crop == "rice")].iloc[0]
    register_macro("bdRiceKcal", 100.0 * bangladesh_rice_imp.sh_kcal, "{:.0f}")
    register_macro("bdRiceZinc", 100.0 * bangladesh_rice_imp.sh_zinc, "{:.0f}")
    
    egypt_wheat_imp = importance_df[(importance_df.Area == "Egypt") & (importance_df.crop == "wheat")].iloc[0]
    register_macro("egWheatKcal", 100.0 * egypt_wheat_imp.sh_kcal, "{:.0f}")
    register_macro("egWheatZinc", 100.0 * egypt_wheat_imp.sh_zinc, "{:.0f}")
    register_macro("egWheatIron", 100.0 * egypt_wheat_imp.sh_iron, "{:.0f}")
    
    latest_adq_year = int(adequacy_df.Year.max())
    adq_recent_mean = adequacy_df[adequacy_df.Year.between(latest_adq_year - 2, latest_adq_year)].groupby("Area").mean(numeric_only=True)
    for country_name in ("India", "Bangladesh", "Nigeria", "Egypt", "Brazil", "Russian Federation", "South Africa"):
        macro_suffix = re.sub("[^A-Za-z]", "", shorten_country_name(country_name))
        register_macro(f"mar{macro_suffix}", adq_recent_mean.loc[country_name, "MAR"], "{:.3f}")
        register_macro(f"feRatio{macro_suffix}", adq_recent_mean.loc[country_name, "iron"] / adq_recent_mean.loc[country_name, "req_iron"], "{:.2f}")
        
    register_macro("nCountriesAdq", int(adequacy_df[adequacy_df.Year == latest_adq_year].m49.nunique()), "{:d}")
    register_macro("adqYears", f"{latest_adq_year-2}--{latest_adq_year}")

    for measure_key, tag_str in (
        ("F4_hazard_paired (equal-weighted)", "Four"),
        ("F1_multiplicative (equal-weighted)", "One"),
        ("F4_hazard_paired (production-weighted)", "FourPw"),
        ("climate part E x S (hazard-paired, no I)", "Clim"),
        ("heat part E_heat x S_heat", "Heat"),
        ("pooled empirical -b_T (%/C)", "Pool")
    ):
        register_macro(f"rhoZhao{tag_str}", val_zhao_df.loc[measure_key, "rho"], "{:+.1f}")
        
    register_macro("rhoShock", val_shocks_test_df.loc["ES_paired", "rho"], "{:+.2f}")
    register_macro("pShock", val_shocks_test_df.loc["ES_paired", "p_perm_one_sided"], "{:.3f}")
    register_macro("rhoShockE", val_shocks_test_df.loc["E", "rho"], "{:+.2f}")
    register_macro("pShockE", val_shocks_test_df.loc["E", "p_perm_one_sided"], "{:.3f}")
    register_macro("rhoShockS", val_shocks_test_df.loc["S", "rho"], "{:+.2f}")
    register_macro("pShockS", val_shocks_test_df.loc["S", "p_perm_one_sided"], "{:.3f}")
    register_macro("nShock", int(val_shocks_test_df.loc["ES_paired", "n"]), "{:d}")
    register_macro("skillMedian", val_shocks_df.oos_skill_r.median(), "{:.2f}")
    register_macro("skillPos", int((val_shocks_df.oos_skill_r > 0).sum()), "{:d}")
    register_macro("skillN", int(val_shocks_df.oos_skill_r.notna().sum()), "{:d}")
    
    for crop_key in CROPS:
        register_macro(f"rtwo{get_crop_label(crop_key)}", val_ray_df.loc[crop_key, "our_r2_median"], "{:.2f}")
        register_macro(f"rtwoMin{get_crop_label(crop_key)}", val_ray_df.loc[crop_key, "our_r2_min"], "{:.2f}")
        register_macro(f"rtwoMax{get_crop_label(crop_key)}", val_ray_df.loc[crop_key, "our_r2_max"], "{:.2f}")
        for nutrient_name in ("zinc", "iron", "protein"):
            register_macro(f"risk{nutrient_name.capitalize()}{get_crop_label(crop_key)}", abs(val_myers_df.loc[crop_key, f"at_risk_{nutrient_name}_pp"]), "{:.2f}")
            register_macro(f"pshare{nutrient_name.capitalize()}{get_crop_label(crop_key)}", 100.0 * val_myers_df.loc[crop_key, f"panel_share_{nutrient_name}"], "{:.1f}")

    old_fbs_hist = yield_diet_hist_df[yield_diet_hist_df.fbs == "old"]
    new_fbs_hist = yield_diet_hist_df[yield_diet_hist_df.fbs == "new"]
    register_macro("nPassOldSig", int(((old_fbs_hist.p_kcal < 0.05) & (old_fbs_hist.beta_kcal > 0)).sum()), "{:d}")
    register_macro("nPassOld", len(old_fbs_hist), "{:d}")
    register_macro("nPassNewSig", int(((new_fbs_hist.p_kcal < 0.05) & (new_fbs_hist.beta_kcal > 0)).sum()), "{:d}")
    register_macro("nPassNew", len(new_fbs_hist), "{:d}")
    
    for country_name in ("China, mainland", "India", "Bangladesh"):
        rice_old_record = old_fbs_hist[(old_fbs_hist.crop == "rice") & (old_fbs_hist.country == country_name)].iloc[0]
        register_macro(f"passRice{re.sub('[^A-Za-z]', '', shorten_country_name(country_name))}", rice_old_record.beta_kcal, "{:.2f}")
        
    passthrough_rows_tex = []
    for crop_key in CROPS:
        for row_idx, country_name in enumerate(panels_df[panels_df.crop == crop_key].country):
            old_subset = old_fbs_hist[(old_fbs_hist.crop == crop_key) & (old_fbs_hist.country == country_name)]
            new_subset = new_fbs_hist[(new_fbs_hist.crop == crop_key) & (new_fbs_hist.country == country_name)]
            format_beta = lambda x: (f"{x.beta_kcal.iloc[0]:+.2f}{'$^*$' if x.p_kcal.iloc[0] < 0.05 else ''}" if len(x) else "--")
            mar_format = (f"{new_subset.beta_MAR_pts_per_pct.iloc[0]:+.3f}" if len(new_subset) and np.isfinite(new_subset.beta_MAR_pts_per_pct.iloc[0]) else "--")
            crop_label_prefix = get_crop_label(crop_key) if row_idx == 0 else ""
            passthrough_rows_tex.append(f"{crop_label_prefix} & {escape_latex_characters(shorten_country_name(country_name))} & {format_beta(old_subset)} & {format_beta(new_subset)} & {mar_format}\\\\")
        passthrough_rows_tex.append(r"\midrule")
        
    write_tex_file(
        "tab_passthrough.tex",
        "\\begin{tabular}{llrrr}\n\\toprule\n"
        "Crop & Country & FBS 1961--2013 & FBS 2010--2023 & MAR pts per 1\\% yield\\\\\n\\midrule\n"
        + "\n".join(passthrough_rows_tex[:-1]) + "\n\\bottomrule\n\\end{tabular}\n"
    )

    scenario_rows_tex = []
    for crop_key in CROPS:
        crop_scenarios = yield_diet_scenarios_df[yield_diet_scenarios_df.crop == crop_key]
        for row_idx, country_name in enumerate(panels_df[panels_df.crop == crop_key].country):
            country_scenarios = crop_scenarios[crop_scenarios.country == country_name].set_index("scenario")
            if not len(country_scenarios):
                continue
            scen_1, scen_2, scen_3 = (country_scenarios.loc[s] for s in ("S1 observed climate shift", "S2 1-in-10 bad season", "S3 standard -10% shock"))
            crop_label_prefix = get_crop_label(crop_key) if row_idx == 0 else ""
            scenario_rows_tex.append(
                f"{crop_label_prefix} & {escape_latex_characters(shorten_country_name(country_name))} & {scen_1.ssr:.2f} & {scen_1.dY_pct:+.1f} & {scen_2.dY_pct:+.1f} & "
                f"{scen_3.dkcal_pct_upper:+.2f} & {scen_3.dzinc_pct_upper:+.2f} & {scen_3.diron_pct_upper:+.2f} & "
                f"{scen_3.dMAR_pts_upper:+.2f} / {scen_3.dMAR_pts_lower:+.2f}\\\\"
            )
        scenario_rows_tex.append(r"\midrule")
        
    write_tex_file(
        "tab_scenario.tex",
        "\\begin{tabular}{llrrrrrrr}\n\\toprule\n"
        " & & & \\multicolumn{2}{c}{Climate-driven $\\Delta Y$ (\\%)} & \\multicolumn{4}{c}{Standard $-10$\\% yield shock (S3)}\\\\\n"
        "\\cmidrule(lr){4-5}\\cmidrule(lr){6-9}\n"
        "Crop & Country & SSR & S1 shift & S2 1-in-10 & $\\Delta$kcal\\% & $\\Delta$Zn\\% & $\\Delta$Fe\\% & $\\Delta$MAR pts (no trade / trade)\\\\\n\\midrule\n"
        + "\n".join(scenario_rows_tex[:-1]) + "\n\\bottomrule\n\\end{tabular}\n"
    )

    scenario_3_df = yield_diet_scenarios_df[yield_diet_scenarios_df.scenario.str.startswith("S3")]
    worst_mar_record = scenario_3_df.sort_values("dMAR_pts_upper").iloc[0]
    register_macro("worstMarCase", f"{get_crop_label(worst_mar_record.crop)} in {shorten_country_name(worst_mar_record.country)}")
    register_macro("worstMar", worst_mar_record.dMAR_pts_upper, "{:+.2f}")
    
    bd_rice_shock = scenario_3_df[(scenario_3_df.crop == "rice") & (scenario_3_df.country == "Bangladesh")].iloc[0]
    register_macro("bdShockKcal", bd_rice_shock.dkcal_pct_upper, "{:+.1f}")
    register_macro("bdShockMar", bd_rice_shock.dMAR_pts_upper, "{:+.2f}")
    
    scenario_1_df = yield_diet_scenarios_df[yield_diet_scenarios_df.scenario.str.startswith("S1")]
    sa_maize_s1 = scenario_1_df[(scenario_1_df.crop == "maize") & (scenario_1_df.country == "South Africa")].iloc[0]
    register_macro("saMaizeSone", sa_maize_s1.dY_pct, "{:+.1f}")
    
    egypt_wheat_s1 = scenario_1_df[(scenario_1_df.crop == "wheat") & (scenario_1_df.country == "Egypt")].iloc[0]
    register_macro("egWheatSone", egypt_wheat_s1.dY_pct, "{:+.1f}")
    
    india_rice_s1 = scenario_1_df[(scenario_1_df.crop == "rice") & (scenario_1_df.country == "India")].iloc[0]
    register_macro("inRiceSone", india_rice_s1.dY_pct, "{:+.1f}")

    use_shares_df = pd.read_csv(os.path.join(PROC, "crop_use_shares.csv"))
    lookup_share = lambda area, crop, col: float(use_shares_df[(use_shares_df.Area == area) & (use_shares_df.crop == crop)][col].iloc[0])
    
    register_macro("maizeFeedWorld", lookup_share("World", "maize", "feed"), "{:.0f}")
    register_macro("maizeFoodWorld", lookup_share("World", "maize", "food"), "{:.0f}")
    register_macro("maizeFeedUS", lookup_share("United States of America", "maize", "feed"), "{:.0f}")
    register_macro("maizeFeedChina", lookup_share("China, mainland", "maize", "feed"), "{:.0f}")
    register_macro("maizeFeedBrazil", lookup_share("Brazil", "maize", "feed"), "{:.0f}")
    register_macro("maizeFoodSAfrica", lookup_share("South Africa", "maize", "food"), "{:.0f}")
    register_macro("soyProcWorld", lookup_share("World", "soybean", "processing"), "{:.0f}")
    register_macro("soyProcUS", lookup_share("United States of America", "soybean", "processing"), "{:.0f}")
    register_macro("soyProcChina", lookup_share("China, mainland", "soybean", "processing"), "{:.0f}")
    register_macro("soyFoodWorld", lookup_share("World", "soybean", "food"), "{:.0f}")
    register_macro("bdShockKcalAbs", abs(bd_rice_shock.dkcal_pct_upper), "{:.1f}")

    koppen_check_df = pd.read_csv(os.path.join(PROC, "koppen_check.csv")).set_index("weight")
    register_macro("koppenAgree", 100.0 * koppen_check_df.loc["all land cells", "agreement"], "{:.0f}")
    for crop_key in CROPS:
        register_macro(f"koppenAgree{get_crop_label(crop_key)}", 100.0 * koppen_check_df.loc[f"{crop_key} harvested area", "agreement"], "{:.0f}")

    for crop_key in CROPS:
        cell_maps = np.load(os.path.join(WORK, f"cellmaps_{crop_key}.npz"))
        large_area_mask = cell_maps["A"] > 500
        register_macro(f"heatCells{get_crop_label(crop_key)}", 100.0 * float((cell_maps["heat_R"][large_area_mask] > 0.01).mean()), "{:.0f}")
        
    shared_countries_list = pd.read_csv(os.path.join(PROC, "shared_panel.csv")).country.tolist()
    top_crop_in_shared = [
        components_df[components_df.country == cn].sort_values("F4_hazard_paired", ascending=False).iloc[0].crop
        for cn in shared_countries_list
    ]
    register_macro("nShared", len(shared_countries_list), "{:d}")
    register_macro("sharedWheatTop", sum(t == "wheat" for t in top_crop_in_shared), "{:d}")
    
    old_fbs_sig = yield_diet_hist_df[(yield_diet_hist_df.fbs == "old") & (yield_diet_hist_df.p_kcal < 0.05) & (yield_diet_hist_df.beta_kcal > 0)]
    soybean_betas = old_fbs_sig[old_fbs_sig.crop == "soybean"].beta_kcal
    register_macro("passSoyLo", soybean_betas.min(), "{:.1f}")
    register_macro("passSoyHi", soybean_betas.max(), "{:.1f}")
    
    india_wheat_s3 = scenario_3_df[(scenario_3_df.crop == "wheat") & (scenario_3_df.country == "India")].iloc[0]
    register_macro("inWheatMar", india_wheat_s3.dMAR_pts_upper, "{:+.2f}")
    register_macro("inWheatMarTrade", india_wheat_s3.dMAR_pts_lower, "{:+.2f}")
    register_macro("inWheatKcal", india_wheat_s3.dkcal_pct_upper, "{:+.1f}")

    india_wheat_comp = components_df[(components_df.crop == "wheat") & (components_df.country == "India")].iloc[0]
    register_macro("exLheat", india_wheat_comp.H_heat, "{:.2f}")
    register_macro("exEheat", india_wheat_comp.E_heat, "{:.2f}")
    register_macro("exEwater", india_wheat_comp.E_water, "{:.2f}")
    register_macro("exLwater", 100.0 * india_wheat_comp.H_water, "{:.1f}")
    register_macro("exShlit", india_wheat_comp.S_lit_heat_n, "{:.2f}")
    register_macro("exShobs", india_wheat_comp.S_emp_heat_n, "{:.2f}")
    register_macro("exSwlit", india_wheat_comp.S_lit_water_n, "{:.2f}")
    register_macro("exSwobs", india_wheat_comp.S_emp_water_n, "{:.2f}")
    register_macro("exSheat", india_wheat_comp.S_heat, "{:.2f}")
    register_macro("exSwater", india_wheat_comp.S_water, "{:.2f}")
    register_macro("exI", india_wheat_comp.I, "{:.3f}")
    register_macro("exImax", components_df.I.max(), "{:.3f}")
    register_macro("exIn", india_wheat_comp.In, "{:.2f}")
    register_macro("exVfour", india_wheat_comp.F4_hazard_paired, "{:.3f}")

    for crop_key in CROPS:
        crop_shift_subset = country_shift_df[country_shift_df.crop == crop_key]
        panel_m49_codes = panels_df[panels_df.crop == crop_key].m49
        crop_shift_panel = crop_shift_subset[crop_shift_subset.m49.isin(panel_m49_codes)]
        mean_snr_heat = (crop_shift_panel.snr_heat_mean * crop_shift_panel.area_ha).sum() / crop_shift_panel.area_ha.sum()
        register_macro(f"snrHeat{get_crop_label(crop_key)}", mean_snr_heat, "{:.2f}")
        
    with open(os.path.join(OUTPUT_DIR, "numbers.tex"), "w", encoding="utf-8") as macros_file:
        macros_file.write("% generated by code/12_export_tex.py -- do not edit by hand\n")
        for macro_key, macro_val in sorted(latex_macros.items()):
            macros_file.write(f"\\newcommand{{\\{macro_key}}}{{{macro_val}}}\n")
            
    print(len(latex_macros), "macros;", len(os.listdir(OUTPUT_DIR)), "files in", OUTPUT_DIR)


if __name__ == "__main__":
    main()
