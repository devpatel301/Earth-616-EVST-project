import os
import sys
import zipfile

import numpy as np
import rasterio
from scipy import stats

from config import ALL_YEARS, BASE, CROPS, DRY_PCTL, MAIN_CROPS, RAW, RECENT, WORK

VARIABLE_NAME = sys.argv[1] if len(sys.argv) > 1 else "prec"
DATA_SOURCES = {
    "prec": [("worldclim", "prec")],
    "tmax": [("tmax", "tmax")],
    "tmin": [("tmin", "tmin")],
    "tavg": [("tmax", "tmax"), ("tmin", "tmin")]
}
IS_TEMPERATURE = VARIABLE_NAME != "prec"
DECADES_LIST = ["1970-1979", "1980-1989", "1990-1999", "2000-2009", "2010-2019", "2020-2024"]
START_YEAR_BUFFER, END_YEAR = 1970, ALL_YEARS[1]
ANALYSIS_YEARS = np.arange(ALL_YEARS[0], ALL_YEARS[1] + 1)
TEMPERATURE_THRESHOLDS = (33.7, 35.0)


def extract_and_index_monthly_files(source_folder, metric_tag):
    output_directory = os.path.join(WORK, f"wc_{metric_tag}")
    os.makedirs(output_directory, exist_ok=True)
    for decade_str in DECADES_LIST:
        zip_path = os.path.join(RAW, source_folder, f"wc2.1_cruts4.09_10m_{metric_tag}_{decade_str}.zip")
        with zipfile.ZipFile(zip_path) as zip_file:
            for zip_member in zip_file.namelist():
                destination_tif = os.path.join(output_directory, os.path.basename(zip_member))
                if zip_member.endswith(".tif") and not os.path.exists(destination_tif):
                    zip_file.extract(zip_member, output_directory)
    
    file_mapping = {}
    for filename in os.listdir(output_directory):
        if filename.endswith(".tif"):
            year_month_str = filename.rsplit("_", 1)[-1][:-4]
            year_num, month_num = int(year_month_str[:4]), int(year_month_str[5:7])
            file_mapping[(year_num, month_num)] = os.path.join(output_directory, filename)
            
    missing_month_tuples = [
        (y, m) for y in range(START_YEAR_BUFFER, END_YEAR + 1) for m in range(1, 13)
        if (y, m) not in file_mapping
    ]
    assert not missing_month_tuples, f"missing months: {missing_month_tuples[:5]}..."
    return file_mapping


def read_raster_layer(raster_filepath):
    with rasterio.open(raster_filepath) as dataset:
        raster_data = dataset.read(1).astype("float64").ravel()
        nodata_val = dataset.nodata
    invalid_mask = ~np.isfinite(raster_data) | (raster_data < -1000) | (raster_data > 1e5)
    if nodata_val is not None:
        invalid_mask |= (raster_data == nodata_val)
    return np.where(invalid_mask, np.nan, raster_data)


def compute_and_save_summary_metrics(crop_name, values_array_by_year, window_tag):
    baseline_year_mask = (ANALYSIS_YEARS >= BASE[0]) & (ANALYSIS_YEARS <= BASE[1])
    recent_year_mask = (ANALYSIS_YEARS >= RECENT[0]) & (ANALYSIS_YEARS <= RECENT[1])
    
    baseline_values = values_array_by_year[baseline_year_mask]
    recent_values = values_array_by_year[recent_year_mask]
    
    baseline_mean = np.nanmean(baseline_values, axis=0)
    recent_mean = np.nanmean(recent_values, axis=0)
    baseline_std = np.nanstd(baseline_values, axis=0, ddof=1)
    recent_std = np.nanstd(recent_values, axis=0, ddof=1)
    
    with np.errstate(divide="ignore", invalid="ignore"):
        metrics_dict = {
            "mean_B": baseline_mean,
            "mean_R": recent_mean,
            "sd_B": baseline_std,
            "sd_R": recent_std,
            "change": recent_mean - baseline_mean,
            "pct_change": 100 * (recent_mean - baseline_mean) / baseline_mean,
            "snr": (recent_mean - baseline_mean) / baseline_std,
            "cv_B": baseline_std / baseline_mean,
            "cv_R": recent_std / recent_mean,
        }
        metrics_dict["p_welch"] = stats.ttest_ind(recent_values, baseline_values, axis=0, equal_var=False, nan_policy="omit").pvalue
        percentile_20th = np.nanpercentile(baseline_values, DRY_PCTL, axis=0)
        percentile_80th = np.nanpercentile(baseline_values, 100 - DRY_PCTL, axis=0)
        
        metrics_dict["dry_freq_R"] = np.nanmean(recent_values < percentile_20th[None, :], axis=0)
        metrics_dict["dry_freq_B"] = np.nanmean(baseline_values < percentile_20th[None, :], axis=0)
        metrics_dict["hot_freq_R"] = np.nanmean(recent_values > percentile_80th[None, :], axis=0)
        metrics_dict["hot_freq_B"] = np.nanmean(baseline_values > percentile_80th[None, :], axis=0)
        
        centered_years = ANALYSIS_YEARS - ANALYSIS_YEARS.mean()
        metrics_dict["trend_per_decade"] = 10 * np.nansum(
            centered_years[:, None] * (values_array_by_year - np.nanmean(values_array_by_year, axis=0)), axis=0
        ) / np.sum(centered_years ** 2)
        
        if VARIABLE_NAME in ("tmax", "tavg"):
            for threshold_temp in TEMPERATURE_THRESHOLDS:
                metrics_dict[f"exceed{threshold_temp}_B"] = np.nanmean(baseline_values >= threshold_temp, axis=0)
                metrics_dict[f"exceed{threshold_temp}_R"] = np.nanmean(recent_values >= threshold_temp, axis=0)
                
    np.savez_compressed(
        os.path.join(WORK, f"metrics_{VARIABLE_NAME}_{crop_name}_{window_tag}.npz"),
        **{metric_key: np.asarray(metric_val, "float32") for metric_key, metric_val in metrics_dict.items()}
    )


def main():
    source_file_mappings = [extract_and_index_monthly_files(folder, tag) for folder, tag in DATA_SOURCES[VARIABLE_NAME]]
    target_crops = list(CROPS) if VARIABLE_NAME == "prec" else MAIN_CROPS
    grids_by_crop = {crop: np.load(os.path.join(WORK, f"grids_{crop}.npz")) for crop in target_crops}
    
    valid_cell_indices = {}
    window_weights = {}
    for crop in target_crops:
        crop_grid = grids_by_crop[crop]
        valid_mask = (crop_grid["area_A"] > 0) & (crop_grid["w_cur"].sum(-1) + crop_grid["w_prev"].sum(-1) > 0)
        valid_cell_indices[crop] = np.flatnonzero(valid_mask.ravel())
        window_weights[crop] = {
            "gs": (
                crop_grid["w_cur"].reshape(-1, 12)[valid_cell_indices[crop]],
                crop_grid["w_prev"].reshape(-1, 12)[valid_cell_indices[crop]]
            ),
            "flow": (
                crop_grid["wf_cur"].reshape(-1, 12)[valid_cell_indices[crop]],
                crop_grid["wf_prev"].reshape(-1, 12)[valid_cell_indices[crop]]
            )
        }
        
    num_years = len(ANALYSIS_YEARS)
    accumulated_values = {
        crop: {window: np.zeros((num_years, len(valid_cell_indices[crop]))) for window in ("gs", "flow", "annual")}
        for crop in target_crops
    }
    missing_value_counts = {crop: 0 for crop in target_crops}

    for year_idx in range(START_YEAR_BUFFER, END_YEAR + 1):
        for month_idx in range(1, 13):
            month_raster_arrays = [read_raster_layer(source_dict[(year_idx, month_idx)]) for source_dict in source_file_mappings]
            mean_monthly_raster = np.mean(month_raster_arrays, axis=0) if len(month_raster_arrays) > 1 else month_raster_arrays[0]
            
            for crop in target_crops:
                cell_values = mean_monthly_raster[valid_cell_indices[crop]]
                missing_value_counts[crop] += int(np.isnan(cell_values).sum())
                
                for window_type in ("gs", "flow"):
                    current_year_weight = window_weights[crop][window_type][0][:, month_idx - 1]
                    prev_year_weight = window_weights[crop][window_type][1][:, month_idx - 1]
                    
                    if ANALYSIS_YEARS[0] <= year_idx <= ANALYSIS_YEARS[-1]:
                        accumulated_values[crop][window_type][year_idx - ANALYSIS_YEARS[0]] += np.where(
                            current_year_weight > 0, current_year_weight * cell_values, 0.0
                        )
                    if ANALYSIS_YEARS[0] <= year_idx + 1 <= ANALYSIS_YEARS[-1]:
                        accumulated_values[crop][window_type][year_idx + 1 - ANALYSIS_YEARS[0]] += np.where(
                            prev_year_weight > 0, prev_year_weight * cell_values, 0.0
                        )
                if ANALYSIS_YEARS[0] <= year_idx <= ANALYSIS_YEARS[-1]:
                    accumulated_values[crop]["annual"][year_idx - ANALYSIS_YEARS[0]] += cell_values
        print(VARIABLE_NAME, year_idx, flush=True)

    for crop in target_crops:
        processed_series = {}
        for window_type in ("gs", "flow", "annual"):
            series_data = accumulated_values[crop][window_type]
            if IS_TEMPERATURE:
                if window_type == "annual":
                    series_data = series_data / 12.0
                else:
                    weight_sum = window_weights[crop][window_type][0].sum(1) + window_weights[crop][window_type][1].sum(1)
                    series_data = series_data / np.where(weight_sum > 0, weight_sum, np.nan)[None, :]
            processed_series[window_type] = series_data.astype("float32")
            compute_and_save_summary_metrics(crop, series_data, window_type)
            
        np.savez_compressed(
            os.path.join(WORK, f"series_{VARIABLE_NAME}_{crop}.npz"),
            years=ANALYSIS_YEARS,
            cells=valid_cell_indices[crop],
            **processed_series
        )
        print(crop, "cells", len(valid_cell_indices[crop]), "missing monthly values", missing_value_counts[crop], flush=True)


if __name__ == "__main__":
    main()
