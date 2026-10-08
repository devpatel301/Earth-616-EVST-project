import os

import numpy as np
import pandas as pd
from scipy import stats

from config import ALL_YEARS, CROPS, MYERS, PROC, RAY, RECENT, SHOCK_SD, WORK, ZHAO, BASE

FORMULA_LIST = ["F1_multiplicative", "F2_geometric", "F3_additive", "F4_hazard_paired"]


def main():
    components_df = pd.read_csv(os.path.join(PROC, "index_components.csv"))
    crop_index_df = pd.read_csv(os.path.join(PROC, "index_crop.csv")).set_index("crop")
    sensitivity_df = pd.read_csv(os.path.join(PROC, "sensitivity.csv"))
    pooled_sensitivity_df = pd.read_csv(os.path.join(PROC, "sensitivity_pooled.csv"))
    qcl_df = pd.read_pickle(os.path.join(WORK, "qcl_4crops.pkl"))
    country_series_df = pd.read_pickle(os.path.join(PROC, "country_series.pkl"))
    importance_df = pd.read_csv(os.path.join(PROC, "importance.csv"))

    zhao_loss_magnitudes = pd.Series({crop_name: -zhao_tuple[0] for crop_name, zhao_tuple in ZHAO.items()})
    heat_component = components_df.assign(heat_prod=components_df.E_heat * components_df.S_heat).groupby("crop").heat_prod.mean()
    climate_component = components_df.groupby("crop").ES_paired.mean()
    pooled_temp_coeff = pooled_sensitivity_df[(pooled_sensitivity_df.period == "full 1971-2024")].groupby("crop").b_T.mean()
    
    validation_1_rows = []
    comparison_series_list = (
        [(f"{form_name} (equal-weighted)", crop_index_df[f"{form_name}_eq"]) for form_name in FORMULA_LIST]
        + [(f"{form_name} (production-weighted)", crop_index_df[f"{form_name}_pw"]) for form_name in FORMULA_LIST]
        + [
            ("climate part E x S (hazard-paired, no I)", climate_component),
            ("heat part E_heat x S_heat", heat_component),
            ("pooled empirical -b_T (%/C)", -pooled_temp_coeff)
        ]
    )
    
    for measure_name, measure_series in comparison_series_list:
        reindexed_series = measure_series.reindex(zhao_loss_magnitudes.index)
        spearman_corr = stats.spearmanr(reindexed_series, zhao_loss_magnitudes)[0]
        ranking_str = " > ".join(reindexed_series.sort_values(ascending=False).index)
        validation_1_rows.append({
            "measure": measure_name,
            "rho": spearman_corr,
            "order": ranking_str,
            **{k: reindexed_series[k] for k in zhao_loss_magnitudes.index}
        })
        
    validation_1_df = pd.DataFrame(validation_1_rows)
    validation_1_df.to_csv(os.path.join(PROC, "val_zhao.csv"), index=False)
    print("Zhao order:", " > ".join(zhao_loss_magnitudes.sort_values(ascending=False).index))
    print(validation_1_df[["measure", "rho", "order"]].round(2).to_string(index=False))

    yield_data = qcl_df[qcl_df.Element == "Yield"]
    shock_validation_rows = []
    
    for _, comp_row in components_df.iterrows():
        yield_series = yield_data[
            (yield_data.crop == comp_row.crop) & (yield_data.m49 == comp_row.m49)
        ].set_index("Year").Value.loc[ALL_YEARS[0]:ALL_YEARS[1]]
        
        years_vector = yield_series.index.values.astype(float)
        trend_line = np.polyval(np.polyfit(years_vector, yield_series.values, 1), years_vector)
        percentage_anomalies = 100.0 * (yield_series.values - trend_line) / trend_line
        anomaly_std = percentage_anomalies.std(ddof=1)
        
        recent_years_mask = (years_vector >= RECENT[0]) & (years_vector <= RECENT[1])
        shock_indicator = percentage_anomalies < -SHOCK_SD * anomaly_std
        
        country_sensitivity = sensitivity_df[(sensitivity_df.crop == comp_row.crop) & (sensitivity_df.m49 == comp_row.m49)].iloc[0]
        country_climate = country_series_df[(country_series_df.crop == comp_row.crop) & (country_series_df.m49 == comp_row.m49)].set_index("year").loc[RECENT[0]:RECENT[1]]
        
        recent_time_index = country_climate.index.values.astype(float)
        detrended_recent_temp = country_climate.teff_flow.values - np.polyval(np.polyfit(recent_time_index, country_climate.teff_flow.values, 1), recent_time_index)
        moisture_array = country_climate.mr_rainfed.fillna(0.0).values
        detrended_recent_mr = moisture_array - np.polyval(np.polyfit(recent_time_index, moisture_array, 1), recent_time_index)
        
        predicted_yield_anomaly = country_sensitivity.b_T_used * detrended_recent_temp + country_sensitivity.b_W_used * 10.0 * detrended_recent_mr
        
        observed_recent_yields = yield_series.loc[RECENT[0]:RECENT[1]]
        recent_time_vector = observed_recent_yields.index.values.astype(float)
        observed_trend = np.polyval(np.polyfit(recent_time_vector, observed_recent_yields.values, 1), recent_time_vector)
        observed_recent_anomalies = 100.0 * (observed_recent_yields.values - observed_trend) / observed_trend
        
        oos_skill_r = np.corrcoef(predicted_yield_anomaly, observed_recent_anomalies)[0, 1] if predicted_yield_anomaly.std() > 0 else np.nan
        
        shock_validation_rows.append({
            "crop": comp_row.crop,
            "country": comp_row.country,
            "shock_freq_recent": shock_indicator[recent_years_mask].mean(),
            "shock_freq_base": shock_indicator[(years_vector >= BASE[0]) & (years_vector <= BASE[1])].mean(),
            "mean_shock_depth": percentage_anomalies[shock_indicator & recent_years_mask].mean() if (shock_indicator & recent_years_mask).any() else 0.0,
            "ES_paired": comp_row.ES_paired,
            "E": comp_row.E,
            "S": comp_row.S,
            "oos_skill_r": oos_skill_r
        })
        
    validation_2_df = pd.DataFrame(shock_validation_rows)
    validation_2_df.to_csv(os.path.join(PROC, "val_shocks.csv"), index=False)
    
    random_generator = np.random.default_rng(20261005)
    permutation_test_rows = []
    for predictor_col in ("ES_paired", "E", "S"):
        observed_rho = stats.spearmanr(validation_2_df[predictor_col], validation_2_df.shock_freq_recent)[0]
        permutation_distribution = np.array([
            stats.spearmanr(random_generator.permutation(validation_2_df[predictor_col].values), validation_2_df.shock_freq_recent)[0]
            for _ in range(5000)
        ])
        permutation_test_rows.append({
            "predictor": predictor_col,
            "rho": observed_rho,
            "p_perm_one_sided": (permutation_distribution >= observed_rho).mean(),
            "n": len(validation_2_df)
        })
        
    permutation_test_df = pd.DataFrame(permutation_test_rows)
    permutation_test_df.to_csv(os.path.join(PROC, "val_shocks_test.csv"), index=False)
    print(validation_2_df.round(3).to_string(index=False))
    print(permutation_test_df.round(3).to_string(index=False))
    print("out-of-sample skill r: median", round(validation_2_df.oos_skill_r.median(), 3), "share > 0:", round((validation_2_df.oos_skill_r > 0).mean(), 3))

    r2_summary = sensitivity_df.groupby("crop").r2_full_linear.agg(["median", "min", "max"])
    validation_3_df = pd.DataFrame({
        "crop": list(CROPS),
        "our_r2_median": [r2_summary.loc[k, "median"] for k in CROPS],
        "our_r2_min": [r2_summary.loc[k, "min"] for k in CROPS],
        "our_r2_max": [r2_summary.loc[k, "max"] for k in CROPS],
        "ray_pct": [RAY.get(k) for k in CROPS]
    })
    validation_3_df.to_csv(os.path.join(PROC, "val_ray.csv"), index=False)
    print(validation_3_df.round(3).to_string(index=False))

    world_importance_df = importance_df[importance_df.Area == "World"].set_index("crop") if (importance_df.Area == "World").any() else None
    panel_mean_importance = components_df.groupby("crop")[["sh_zinc", "sh_iron", "sh_protein"]].mean()
    
    validation_4_rows = []
    for crop_key in CROPS:
        myers_info = MYERS.get(crop_key, {})
        crop_record = {"crop": crop_key, "photo": CROPS[crop_key]["photo"]}
        for nutrient_name in ("zinc", "iron", "protein"):
            decline_val, is_significant = myers_info.get(nutrient_name, (np.nan, False))
            crop_record[f"myers_{nutrient_name}_pct"] = decline_val
            crop_record[f"myers_{nutrient_name}_sig"] = is_significant
            crop_record[f"panel_share_{nutrient_name}"] = panel_mean_importance.loc[crop_key, f"sh_{nutrient_name}"]
            if world_importance_df is not None:
                crop_record[f"world_share_{nutrient_name}"] = world_importance_df.loc[crop_key, f"sh_{nutrient_name}"]
            effective_decline = decline_val if (is_significant and np.isfinite(decline_val)) else 0.0
            crop_record[f"at_risk_{nutrient_name}_pp"] = -effective_decline * panel_mean_importance.loc[crop_key, f"sh_{nutrient_name}"]
        validation_4_rows.append(crop_record)
        
    validation_4_df = pd.DataFrame(validation_4_rows)
    validation_4_df.to_csv(os.path.join(PROC, "val_myers.csv"), index=False)
    print(validation_4_df.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
