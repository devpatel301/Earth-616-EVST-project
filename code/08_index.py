import os

import numpy as np
import pandas as pd
from scipy import stats

from config import CROPS, PROC, RECENT, ZHAO

INDEX_FORMULAS = ["F1_multiplicative", "F2_geometric", "F3_additive", "F4_hazard_paired"]


def normalize_by_max(values_series):
    values_array = np.asarray(values_series, float)
    max_val = np.nanmax(values_array)
    return values_array / max_val if max_val > 0 else values_array * 0.0


def normalize_min_max(values_series):
    values_array = np.asarray(values_series, float)
    min_val, max_val = np.nanmin(values_array), np.nanmax(values_array)
    return (values_array - min_val) / (max_val - min_val)


def load_index_components():
    panels_dataframe = pd.read_csv(os.path.join(PROC, "panels.csv"))
    country_series_dataframe = pd.read_pickle(os.path.join(PROC, "country_series.pkl"))
    country_shift_dataframe = pd.read_csv(os.path.join(PROC, "country_shift.csv"))
    sensitivity_dataframe = pd.read_csv(os.path.join(PROC, "sensitivity.csv"))
    importance_dataframe = pd.read_csv(os.path.join(PROC, "importance.csv"))
    
    recent_climate = country_series_dataframe[
        (country_series_dataframe.year >= RECENT[0]) & (country_series_dataframe.year <= RECENT[1])
    ].groupby(["crop", "m49"])[["H_heat", "H_water"]].mean().reset_index()
    
    merged_components = panels_dataframe[["crop", "country", "m49", "share_pct", "production_t", "classes"]].merge(
        recent_climate, on=["crop", "m49"]
    ).merge(
        country_shift_dataframe[["crop", "m49", "snr_heat_mean", "snr_water_mean", "rainfed_share"]], on=["crop", "m49"]
    ).merge(
        sensitivity_dataframe[["crop", "m49", "S_heat", "S_water", "S_lit_heat_n", "S_lit_water_n", "S_emp_heat_n", "S_emp_water_n"]], on=["crop", "m49"]
    ).merge(
        importance_dataframe[["crop", "m49", "I", "sh_kcal", "sh_protein", "sh_fat", "sh_zinc", "sh_iron"]], on=["crop", "m49"], how="left"
    )
    
    assert merged_components.I.notna().all(), merged_components[merged_components.I.isna()]
    merged_components["D_heat"] = merged_components.snr_heat_mean.clip(lower=0)
    merged_components["D_water"] = merged_components.snr_water_mean.clip(lower=0)
    return merged_components


def calculate_indices(input_dataframe, norm_func=normalize_by_max, weight_level=1.0, sensitivity_mode="lit", rice_ky_override=None, importance_column="I"):
    dataframe = input_dataframe.copy()
    for hazard_name in ("heat", "water"):
        hazard_level = norm_func(dataframe[f"H_{hazard_name}"])
        hazard_shift = norm_func(dataframe[f"D_{hazard_name}"])
        dataframe[f"E_{hazard_name}"] = weight_level * hazard_level + (1.0 - weight_level) * hazard_shift
        
        if sensitivity_mode == "lit":
            dataframe[f"S_{hazard_name}"] = dataframe[f"S_lit_{hazard_name}_n"]
        elif sensitivity_mode == "emp":
            dataframe[f"S_{hazard_name}"] = dataframe[f"S_emp_{hazard_name}_n"]
        elif sensitivity_mode == "both":
            dataframe[f"S_{hazard_name}"] = 0.5 * (dataframe[f"S_lit_{hazard_name}_n"] + dataframe[f"S_emp_{hazard_name}_n"])
            
    if rice_ky_override is not None:
        from config import CROPS as CROP_CONFIG
        lit_ky = dataframe.crop.map(lambda crop_k: CROP_CONFIG[crop_k]["ky"]).astype(float)
        lit_ky[dataframe.crop == "rice"] = rice_ky_override
        dataframe["S_lit_water_n"] = lit_ky / lit_ky.max()
        dataframe["S_water"] = (
            0.5 * (dataframe.S_lit_water_n + dataframe.S_emp_water_n)
            if sensitivity_mode == "both"
            else dataframe.S_lit_water_n
        )
        
    dataframe["E"] = (dataframe.E_heat + dataframe.E_water) / 2.0
    dataframe["S"] = (dataframe.S_heat + dataframe.S_water) / 2.0
    dataframe["In"] = norm_func(dataframe[importance_column])
    
    dataframe["F1_multiplicative"] = dataframe.E * dataframe.S * dataframe.In
    dataframe["F2_geometric"] = (dataframe.E * dataframe.S * dataframe.In) ** (1.0 / 3.0)
    dataframe["F3_additive"] = (dataframe.E + dataframe.S + dataframe.In) / 3.0
    dataframe["F4_hazard_paired"] = 0.5 * (dataframe.E_heat * dataframe.S_heat + dataframe.E_water * dataframe.S_water) * dataframe.In
    dataframe["ES_paired"] = 0.5 * (dataframe.E_heat * dataframe.S_heat + dataframe.E_water * dataframe.S_water)
    return dataframe


def compute_crop_level_aggregates(components_dataframe):
    summary_rows = []
    for crop_name, crop_group in components_dataframe.groupby("crop", sort=False):
        production_weights = crop_group.production_t / crop_group.production_t.sum()
        row_dict = {"crop": crop_name}
        for metric_name in INDEX_FORMULAS + ["E", "S", "In", "ES_paired", "E_heat", "E_water", "S_heat", "S_water"]:
            row_dict[f"{metric_name}_eq"] = crop_group[metric_name].mean()
            row_dict[f"{metric_name}_pw"] = (crop_group[metric_name] * production_weights).sum()
        summary_rows.append(row_dict)
        
    crop_level_df = pd.DataFrame(summary_rows)
    for formula_name in INDEX_FORMULAS:
        for weight_type in ("eq", "pw"):
            crop_level_df[f"rank_{formula_name}_{weight_type}"] = crop_level_df[f"{formula_name}_{weight_type}"].rank(ascending=False).astype(int)
    return crop_level_df


def main():
    base_components = load_index_components()
    evaluated_components = calculate_indices(base_components)
    evaluated_components.to_csv(os.path.join(PROC, "index_components.csv"), index=False)
    
    crop_level_indices = compute_crop_level_aggregates(evaluated_components)
    crop_level_indices["zhao_pct_per_C"] = crop_level_indices.crop.map(lambda crop_k: ZHAO[crop_k][0])
    crop_level_indices.to_csv(os.path.join(PROC, "index_crop.csv"), index=False)
    
    pd.set_option("display.width", 250)
    print(crop_level_indices[["crop"] + [f"{f}_eq" for f in INDEX_FORMULAS] + [f"rank_{f}_eq" for f in INDEX_FORMULAS]].round(3).to_string(index=False))
    print(crop_level_indices[["crop"] + [f"{f}_pw" for f in INDEX_FORMULAS] + [f"rank_{f}_pw" for f in INDEX_FORMULAS]].round(3).to_string(index=False))

    robustness_specifications = {
        "main (x/max, exposure = stress level, literature S)": {},
        "min-max normalisation": {"norm_func": normalize_min_max},
        "exposure = level + change (average)": {"weight_level": 0.5},
        "exposure = change only": {"weight_level": 0.0},
        "sensitivity = literature + empirical average": {"sensitivity_mode": "both"},
        "sensitivity = empirical only": {"sensitivity_mode": "emp"},
        "rice Ky = 1.0": {"rice_ky_override": 1.0},
        "rice Ky = 1.5": {"rice_ky_override": 1.5},
        "importance = kcal share only": {"importance_column": "sh_kcal"},
        "importance = Zn+Fe+protein only": {"importance_column": "I_micro"},
    }
    
    base_components["I_micro"] = base_components[["sh_zinc", "sh_iron", "sh_protein"]].mean(axis=1)
    robustness_records = []
    
    for test_label, test_kwargs in robustness_specifications.items():
        rebuilt_crop_df = compute_crop_level_aggregates(calculate_indices(base_components, **test_kwargs))
        for formula_name in INDEX_FORMULAS:
            for weight_type in ("eq", "pw"):
                sorted_crops = rebuilt_crop_df.sort_values(f"{formula_name}_{weight_type}", ascending=False).crop.tolist()
                robustness_records.append({
                    "test": test_label,
                    "form": formula_name,
                    "weighting": weight_type,
                    "order": " > ".join(sorted_crops),
                    "top": sorted_crops[0],
                    **{f"rank_{crop_k}": int(rebuilt_crop_df.set_index("crop").loc[crop_k, f"rank_{formula_name}_{weight_type}"]) for crop_k in CROPS}
                })
                
    robustness_df = pd.DataFrame(robustness_records)
    robustness_df.to_csv(os.path.join(PROC, "index_robustness.csv"), index=False)
    print(robustness_df[robustness_df.weighting == "eq"][["test", "form", "order"]].to_string(index=False))

    random_state = np.random.default_rng(20261005)
    monte_carlo_draws = []
    
    for iteration_idx in range(2000):
        rand_weight_level = random_state.uniform(0.0, 1.0)
        rand_hazard_ratio = random_state.uniform(0.0, 1.0)
        rand_nutrient_weights = random_state.dirichlet(np.ones(5))
        
        sim_components = base_components.copy()
        sim_components["I_mc"] = sim_components[["sh_kcal", "sh_protein", "sh_fat", "sh_zinc", "sh_iron"]].values @ rand_nutrient_weights
        
        sim_evaluated = calculate_indices(sim_components, weight_level=rand_weight_level, importance_column="I_mc")
        sim_evaluated["E"] = rand_hazard_ratio * sim_evaluated.E_heat + (1.0 - rand_hazard_ratio) * sim_evaluated.E_water
        sim_evaluated["S"] = rand_hazard_ratio * sim_evaluated.S_heat + (1.0 - rand_hazard_ratio) * sim_evaluated.S_water
        sim_evaluated["F1_multiplicative"] = sim_evaluated.E * sim_evaluated.S * sim_evaluated.In
        sim_evaluated["F2_geometric"] = sim_evaluated.F1_multiplicative ** (1.0 / 3.0)
        sim_evaluated["F3_additive"] = (sim_evaluated.E + sim_evaluated.S + sim_evaluated.In) / 3.0
        sim_evaluated["F4_hazard_paired"] = (
            rand_hazard_ratio * sim_evaluated.E_heat * sim_evaluated.S_heat
            + (1.0 - rand_hazard_ratio) * sim_evaluated.E_water * sim_evaluated.S_water
        ) * sim_evaluated.In
        
        sim_crop_df = compute_crop_level_aggregates(sim_evaluated)
        for formula_name in INDEX_FORMULAS:
            for crop_name, rank_val in zip(sim_crop_df.crop, sim_crop_df[f"rank_{formula_name}_eq"]):
                monte_carlo_draws.append({
                    "it": iteration_idx,
                    "form": formula_name,
                    "crop": crop_name,
                    "rank": rank_val
                })
                
    monte_carlo_df = pd.DataFrame(monte_carlo_draws)
    rank_frequencies = monte_carlo_df.groupby(["form", "crop"])["rank"].value_counts(normalize=True).unstack(fill_value=0).reset_index()
    rank_frequencies.to_csv(os.path.join(PROC, "index_montecarlo.csv"), index=False)
    print(rank_frequencies.round(3).to_string(index=False))

    agreement_results = [
        {"a": formula_a, "b": formula_b, "tau": stats.kendalltau(evaluated_components[formula_a], evaluated_components[formula_b])[0]}
        for i, formula_a in enumerate(INDEX_FORMULAS)
        for formula_b in INDEX_FORMULAS[i + 1:]
    ]
    pd.DataFrame(agreement_results).to_csv(os.path.join(PROC, "index_form_agreement.csv"), index=False)
    print(pd.DataFrame(agreement_results).round(3))


if __name__ == "__main__":
    main()
