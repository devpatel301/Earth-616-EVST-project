import os

import numpy as np
import pandas as pd
from scipy import stats

from config import BASE, PROC, RECENT, WORK

NUTRIENT_NAMES = ["kcal", "protein", "fat", "zinc", "iron"]


def compute_percentage_detrended_anomaly(values_series, time_index_array):
    fitted_linear_trend = np.polyval(np.polyfit(time_index_array, values_series, 1), time_index_array)
    return 100.0 * (values_series - fitted_linear_trend) / fitted_linear_trend


def main():
    panels_df = pd.read_csv(os.path.join(PROC, "panels.csv"))
    qcl_df = pd.read_pickle(os.path.join(WORK, "qcl_4crops.pkl"))
    yield_df = qcl_df[qcl_df.Element == "Yield"].rename(columns={"Year": "year", "Value": "yield"})[["crop", "m49", "year", "yield"]]
    supply_df = pd.read_pickle(os.path.join(PROC, "nutrient_supply.pkl"))
    crop_supply_df = supply_df.dropna(subset=["crop"]).groupby(["method", "crop", "m49", "Year"])[NUTRIENT_NAMES].sum().reset_index()
    adequacy_df = pd.read_csv(os.path.join(PROC, "adequacy.csv"))
    crop_contrib_df = pd.read_csv(os.path.join(PROC, "crop_contrib.csv"))
    sensitivity_df = pd.read_csv(os.path.join(PROC, "sensitivity.csv"))
    country_series_df = pd.read_pickle(os.path.join(PROC, "country_series.pkl"))

    historical_elasticity_rows = []
    for _, panel_row in panels_df.iterrows():
        yield_series = yield_df[(yield_df.crop == panel_row.crop) & (yield_df.m49 == panel_row.m49)].set_index("year")["yield"]
        
        for fbs_method, (start_yr, end_yr) in (("new", (2010, 2023)), ("old", (1961, 2013))):
            supply_series_subset = crop_supply_df[
                (crop_supply_df.method == fbs_method) & (crop_supply_df.crop == panel_row.crop) & (crop_supply_df.m49 == panel_row.m49)
            ].set_index("Year")
            
            common_years = sorted(set(supply_series_subset.index) & set(yield_series.index) & set(range(start_yr, end_yr + 1)))
            if len(common_years) < 8 or (supply_series_subset.loc[common_years, "kcal"] <= 0).any():
                continue
                
            time_vector = np.array(common_years, float)
            yield_anomalies = compute_percentage_detrended_anomaly(yield_series.loc[common_years].values, time_vector)
            
            record = {
                "crop": panel_row.crop,
                "country": panel_row.country,
                "fbs": fbs_method,
                "n": len(common_years)
            }
            
            for nutrient_key in ("kcal", "protein", "zinc"):
                nutrient_anomalies = compute_percentage_detrended_anomaly(supply_series_subset.loc[common_years, nutrient_key].values, time_vector)
                regression_result = stats.linregress(yield_anomalies, nutrient_anomalies)
                record[f"beta_{nutrient_key}"] = regression_result.slope
                record[f"p_{nutrient_key}"] = regression_result.pvalue
                record[f"r_{nutrient_key}"] = regression_result.rvalue
                
            if fbs_method == "new":
                mar_series = adequacy_df[adequacy_df.m49 == panel_row.m49].set_index("Year").MAR
                mar_common_years = sorted(set(mar_series.index) & set(common_years))
                if len(mar_common_years) >= 8:
                    mar_detrended = mar_series.loc[mar_common_years].values - np.polyval(
                        np.polyfit(mar_common_years, mar_series.loc[mar_common_years].values, 1), mar_common_years
                    )
                    mar_regression = stats.linregress(
                        compute_percentage_detrended_anomaly(yield_series.loc[mar_common_years].values, np.array(mar_common_years, float)),
                        100.0 * mar_detrended
                    )
                    record["beta_MAR_pts_per_pct"] = mar_regression.slope
                    record["p_MAR"] = mar_regression.pvalue
                    
            historical_elasticity_rows.append(record)
            
    historical_elasticity_df = pd.DataFrame(historical_elasticity_rows)
    historical_elasticity_df.to_csv(os.path.join(PROC, "yield_diet_historical.csv"), index=False)
    pd.set_option("display.width", 250)
    print(historical_elasticity_df.round(3).to_string(index=False))

    latest_fbs_year = int(adequacy_df.Year.max())
    baseline_adequacy_df = adequacy_df[adequacy_df.Year.between(latest_fbs_year - 2, latest_fbs_year)].groupby("m49").mean(numeric_only=True)
    baseline_contrib_df = crop_contrib_df[crop_contrib_df.Year.between(latest_fbs_year - 2, latest_fbs_year)].groupby(["crop", "m49"]).mean(numeric_only=True)
    
    scenario_output_rows = []
    for _, panel_row in panels_df.iterrows():
        sensitivity_record = sensitivity_df[(sensitivity_df.crop == panel_row.crop) & (sensitivity_df.m49 == panel_row.m49)].iloc[0]
        country_climate_history = country_series_df[(country_series_df.crop == panel_row.crop) & (country_series_df.m49 == panel_row.m49)].set_index("year")
        
        baseline_climate = country_climate_history.loc[BASE[0]:BASE[1]]
        recent_climate = country_climate_history.loc[RECENT[0]:RECENT[1]]
        
        delta_teff = recent_climate.teff_flow.mean() - baseline_climate.teff_flow.mean()
        delta_mr = (recent_climate.mr_rainfed.mean() - baseline_climate.mr_rainfed.mean()) if country_climate_history.mr_rainfed.notna().any() else 0.0
        
        scenario_1_shock = sensitivity_record.b_T_used * delta_teff + sensitivity_record.b_W_used * 10.0 * np.nan_to_num(delta_mr)
        
        recent_years_vector = recent_climate.index.values.astype(float)
        detrended_recent_temp = recent_climate.teff_flow.values - np.polyval(np.polyfit(recent_years_vector, recent_climate.teff_flow.values, 1), recent_years_vector)
        recent_mr_vector = recent_climate.mr_rainfed.fillna(0.0).values
        detrended_recent_mr = recent_mr_vector - np.polyval(np.polyfit(recent_years_vector, recent_mr_vector, 1), recent_years_vector)
        
        scenario_2_shock = np.percentile(sensitivity_record.b_T_used * detrended_recent_temp + sensitivity_record.b_W_used * 10.0 * detrended_recent_mr, 10)
        
        if panel_row.m49 not in baseline_adequacy_df.index or (panel_row.crop, panel_row.m49) not in baseline_contrib_df.index:
            continue
            
        base_nutrients = baseline_adequacy_df.loc[panel_row.m49]
        crop_base_contrib = baseline_contrib_df.loc[(panel_row.crop, panel_row.m49)]
        
        scenarios_to_evaluate = [
            ("S1 observed climate shift", scenario_1_shock),
            ("S2 1-in-10 bad season", scenario_2_shock),
            ("S3 standard -10% shock", -10.0)
        ]
        
        for scenario_name, predicted_delta_yield in scenarios_to_evaluate:
            fractional_yield_loss = max(0.0, -predicted_delta_yield) / 100.0
            upper_loss_fraction = fractional_yield_loss * min(1.0, crop_base_contrib.ssr)
            lower_loss_fraction = max(0.0, fractional_yield_loss * crop_base_contrib["prod"] - crop_base_contrib["exp"]) / crop_base_contrib["dom"] if crop_base_contrib["dom"] > 0 else 0.0
            
            scenario_result = {
                "crop": panel_row.crop,
                "country": panel_row.country,
                "scenario": scenario_name,
                "dY_pct": predicted_delta_yield,
                "dTEFF": delta_teff,
                "dMR": delta_mr,
                "ssr": crop_base_contrib.ssr,
                "MAR_base": base_nutrients.MAR
            }
            
            for bound_label, loss_fraction in (("upper", upper_loss_fraction), ("lower", lower_loss_fraction)):
                simulated_nar_values = []
                for nutrient_name in NUTRIENT_NAMES:
                    post_shock_supply = base_nutrients[nutrient_name] - loss_fraction * crop_base_contrib[nutrient_name]
                    simulated_nar_values.append(min(1.0, post_shock_supply / base_nutrients[f"req_{nutrient_name}"]))
                    scenario_result[f"d{nutrient_name}_pct_{bound_label}"] = -100.0 * loss_fraction * crop_base_contrib[nutrient_name] / base_nutrients[nutrient_name]
                scenario_result[f"MAR_{bound_label}"] = np.mean(simulated_nar_values)
                scenario_result[f"dMAR_pts_{bound_label}"] = 100.0 * (np.mean(simulated_nar_values) - base_nutrients.MAR)
                scenario_result[f"cut_frac_{bound_label}"] = loss_fraction
                
            scenario_output_rows.append(scenario_result)
            
    scenarios_df = pd.DataFrame(scenario_output_rows)
    scenarios_df.to_csv(os.path.join(PROC, "yield_diet_scenarios.csv"), index=False)
    print(scenarios_df[["crop", "country", "scenario", "dY_pct", "ssr", "MAR_base", "dkcal_pct_upper", "dzinc_pct_upper", "dMAR_pts_upper", "dMAR_pts_lower"]].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
