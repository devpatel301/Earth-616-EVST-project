import os

import numpy as np
import pandas as pd
from scipy import stats

from config import ALL_YEARS, ALPHA, CROPS, FIT, METHODS, PROC, WORK


def detrend_series(input_series, year_array, detrend_method, is_yield=False):
    series_values = np.asarray(input_series, float)
    if detrend_method == "first-difference":
        return 100.0 * np.diff(np.log(series_values)) if is_yield else np.diff(series_values)
    polynomial_order = 1 if detrend_method == "linear" else 2
    fitted_trend = np.polyval(np.polyfit(year_array, series_values, polynomial_order), year_array)
    return 100.0 * (series_values - fitted_trend) / fitted_trend if is_yield else series_values - fitted_trend


def fit_ols_hc3(design_matrix, response_vector):
    design_with_intercept = np.column_stack([np.ones(len(response_vector)), design_matrix])
    beta_coefficients = np.linalg.lstsq(design_with_intercept, response_vector, rcond=None)[0]
    residuals = response_vector - design_with_intercept @ beta_coefficients
    xtx_inverse = np.linalg.pinv(design_with_intercept.T @ design_with_intercept)
    leverage_diagonal = np.einsum("ij,jk,ik->i", design_with_intercept, xtx_inverse, design_with_intercept)
    hc3_weighted_design = design_with_intercept * (residuals / np.maximum(1.0 - leverage_diagonal, 1e-6))[:, None]
    standard_errors = np.sqrt(np.diag(xtx_inverse @ (hc3_weighted_design.T @ hc3_weighted_design) @ xtx_inverse))
    degrees_of_freedom = len(response_vector) - design_with_intercept.shape[1]
    p_values = 2.0 * stats.t.sf(np.abs(beta_coefficients / standard_errors), degrees_of_freedom)
    r_squared = 1.0 - residuals.var() / response_vector.var()
    return beta_coefficients, standard_errors, p_values, r_squared


def load_merged_yield_and_climate_data():
    qcl_dataframe = pd.read_pickle(os.path.join(WORK, "qcl_4crops.pkl"))
    yield_dataframe = qcl_dataframe[qcl_dataframe.Element == "Yield"][["crop", "m49", "Year", "Value"]].rename(
        columns={"Year": "year", "Value": "yield"}
    )
    country_series_dataframe = pd.read_pickle(os.path.join(PROC, "country_series.pkl"))
    return country_series_dataframe.merge(yield_dataframe, on=["crop", "m49", "year"], how="inner")


def prepare_regression_variables(country_crop_dataframe, start_year, end_year, detrend_method):
    filtered_df = country_crop_dataframe[
        (country_crop_dataframe.year >= start_year) & (country_crop_dataframe.year <= end_year)
    ].sort_values("year").dropna(subset=["yield", "teff_flow"])
    filtered_df = filtered_df[filtered_df["yield"] > 0]
    
    year_array = filtered_df.year.values.astype(float)
    moisture_ratio_array = filtered_df.mr_rainfed.fillna(0.0).values
    
    detrended_yield = detrend_series(filtered_df["yield"].values, year_array, detrend_method, is_yield=True)
    detrended_temperature = detrend_series(filtered_df.teff_flow.values, year_array, detrend_method)
    detrended_moisture = detrend_series(moisture_ratio_array, year_array, detrend_method) * 10.0
    return detrended_yield, detrended_temperature, detrended_moisture


def fit_single_country_model(country_crop_dataframe, start_year, end_year, detrend_method):
    detrended_y, detrended_T, detrended_W = prepare_regression_variables(
        country_crop_dataframe, start_year, end_year, detrend_method
    )
    regressor_columns = [detrended_T] + ([detrended_W] if np.nanstd(detrended_W) > 1e-9 else [])
    beta_coeffs, standard_errs, p_vals, r_sq = fit_ols_hc3(np.column_stack(regressor_columns), detrended_y)
    beta_water, p_water = (beta_coeffs[2], p_vals[2]) if len(regressor_columns) == 2 else (0.0, 1.0)
    return {
        "b_T": beta_coeffs[1],
        "se_T": standard_errs[1],
        "p_T": p_vals[1],
        "b_W": beta_water,
        "p_W": p_water,
        "r2": r_sq,
        "n": len(detrended_y)
    }


def fit_pooled_panel_model(panel_dataframe, start_year, end_year, detrend_method):
    yield_list, temp_list, water_list = [], [], []
    for _, country_group in panel_dataframe.groupby("m49"):
        y_country, T_country, W_country = prepare_regression_variables(
            country_group, start_year, end_year, detrend_method
        )
        yield_list.append(y_country - y_country.mean())
        temp_list.append(T_country - T_country.mean())
        water_list.append(W_country - W_country.mean())
        
    stacked_y, stacked_T, stacked_W = map(np.concatenate, (yield_list, temp_list, water_list))
    beta_coeffs, standard_errs, p_vals, r_sq = fit_ols_hc3(np.column_stack([stacked_T, stacked_W]), stacked_y)
    return {
        "b_T": beta_coeffs[1],
        "p_T": p_vals[1],
        "b_W": beta_coeffs[2],
        "p_W": p_vals[2],
        "r2": r_sq,
        "n": len(stacked_y)
    }


def check_estimate_robustness(fits_list, coeff_key, pvalue_key):
    coefficient_signs = [np.sign(fit_dict[coeff_key]) for fit_dict in fits_list]
    all_significant = all(fit_dict[pvalue_key] < ALPHA for fit_dict in fits_list)
    consistent_sign = len(set(coefficient_signs)) == 1
    return all_significant and consistent_sign


def main():
    combined_data = load_merged_yield_and_climate_data()
    panels_dataframe = pd.read_csv(os.path.join(PROC, "panels.csv"))
    
    sensitivity_records = []
    pooled_records = []
    
    for crop_name, panel_subset in panels_dataframe.groupby("crop", sort=False):
        crop_panel_data = combined_data[(combined_data.crop == crop_name) & combined_data.m49.isin(panel_subset.m49)]
        pooled_fit_baseline = {method: fit_pooled_panel_model(crop_panel_data, *FIT, method) for method in METHODS}
        pooled_fit_full = {method: fit_pooled_panel_model(crop_panel_data, *ALL_YEARS, method) for method in METHODS}
        
        for method in METHODS:
            pooled_records.append({"crop": crop_name, "method": method, "period": "fit 1971-2000", **pooled_fit_baseline[method]})
            pooled_records.append({"crop": crop_name, "method": method, "period": "full 1971-2024", **pooled_fit_full[method]})
            
        pooled_temp_robust = check_estimate_robustness(list(pooled_fit_baseline.values()), "b_T", "p_T")
        pooled_water_robust = check_estimate_robustness(list(pooled_fit_baseline.values()), "b_W", "p_W")
        
        pooled_beta_temp = np.mean([pooled_fit_baseline[m]["b_T"] for m in METHODS]) if pooled_temp_robust else 0.0
        pooled_beta_water = np.mean([pooled_fit_baseline[m]["b_W"] for m in METHODS]) if pooled_water_robust else 0.0
        
        for _, panel_row in panel_subset.iterrows():
            country_crop_data = crop_panel_data[crop_panel_data.m49 == panel_row.m49]
            country_baseline_fits = {m: fit_single_country_model(country_crop_data, *FIT, m) for m in METHODS}
            country_full_fits = {m: fit_single_country_model(country_crop_data, *ALL_YEARS, m) for m in METHODS}
            
            country_temp_robust = check_estimate_robustness(list(country_baseline_fits.values()), "b_T", "p_T")
            country_water_robust = check_estimate_robustness(list(country_baseline_fits.values()), "b_W", "p_W")
            
            selected_beta_temp = np.mean([country_baseline_fits[m]["b_T"] for m in METHODS]) if country_temp_robust else pooled_beta_temp
            selected_beta_water = np.mean([country_baseline_fits[m]["b_W"] for m in METHODS]) if country_water_robust else pooled_beta_water
            
            row_dict = {
                "crop": crop_name,
                "country": panel_row.country,
                "m49": panel_row.m49,
                "s_lit_heat": CROPS[crop_name]["heat_slope"],
                "s_lit_water": CROPS[crop_name]["ky"],
                "b_T_used": selected_beta_temp,
                "b_W_used": selected_beta_water,
                "T_source": "country" if country_temp_robust else "pooled",
                "W_source": "country" if country_water_robust else "pooled",
                "s_emp_heat": max(0.0, -selected_beta_temp),
                "s_emp_water": max(0.0, selected_beta_water),
                "pooled_T_robust": pooled_temp_robust,
                "pooled_W_robust": pooled_water_robust,
                "r2_full_linear": country_full_fits["linear"]["r2"],
                "n_fit": country_baseline_fits["linear"]["n"]
            }
            
            for method in METHODS:
                for metric_name in ("b_T", "p_T", "b_W", "p_W", "r2"):
                    row_dict[f"{metric_name}_{method[:4]}"] = country_baseline_fits[method][metric_name]
                    row_dict[f"full_{metric_name}_{method[:4]}"] = country_full_fits[method][metric_name]
            sensitivity_records.append(row_dict)
            
    sensitivity_df = pd.DataFrame(sensitivity_records)
    for hazard_type in ("heat", "water"):
        lit_series = sensitivity_df[f"s_lit_{hazard_type}"]
        emp_series = sensitivity_df[f"s_emp_{hazard_type}"]
        sensitivity_df[f"S_lit_{hazard_type}_n"] = lit_series / lit_series.max()
        ref_p90 = np.percentile(emp_series[emp_series > 0], 90) if (emp_series > 0).any() else 1.0
        sensitivity_df[f"S_emp_{hazard_type}_n"] = np.minimum(1.0, emp_series / ref_p90)
        sensitivity_df[f"S_{hazard_type}"] = sensitivity_df[f"S_lit_{hazard_type}_n"]
        
    sensitivity_df.to_csv(os.path.join(PROC, "sensitivity.csv"), index=False)
    pd.DataFrame(pooled_records).to_csv(os.path.join(PROC, "sensitivity_pooled.csv"), index=False)
    
    pd.set_option("display.width", 250)
    print(sensitivity_df[["crop", "country", "b_T_used", "T_source", "b_W_used", "W_source", "S_heat", "S_water", "r2_full_linear"]].round(3).to_string(index=False))
    print(pd.DataFrame(pooled_records).round(3).to_string(index=False))


if __name__ == "__main__":
    main()
