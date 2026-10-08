import importlib
import os

import numpy as np

from config import ALL_YEARS, CROPS, NX, NY, RES, WORK

climate_exposure_module = importlib.import_module("04_climate_exposure")

ANALYSIS_YEARS = np.arange(ALL_YEARS[0], ALL_YEARS[1] + 1)
START_YEAR_BUFFER, END_YEAR = 1970, ALL_YEARS[1]
MONTH_DAYS = np.array([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])
MID_MONTH_DAY_OF_YEAR = np.cumsum(MONTH_DAYS) - MONTH_DAYS / 2.0
SOLAR_CONSTANT = 0.0820


def compute_extraterrestrial_radiation_grid():
    latitude_radians = np.deg2rad(90 - RES * (np.arange(NY) + 0.5))
    radiation_grid = np.zeros((12, NY))
    for month_index, day_of_year in enumerate(MID_MONTH_DAY_OF_YEAR):
        relative_distance = 1 + 0.033 * np.cos(2 * np.pi * day_of_year / 365)
        solar_declination = 0.409 * np.sin(2 * np.pi * day_of_year / 365 - 1.39)
        sunset_hour_angle = np.arccos(np.clip(-np.tan(latitude_radians) * np.tan(solar_declination), -1, 1))
        radiation_grid[month_index] = (24 * 60 / np.pi) * SOLAR_CONSTANT * relative_distance * (
            sunset_hour_angle * np.sin(latitude_radians) * np.sin(solar_declination)
            + np.cos(latitude_radians) * np.cos(solar_declination) * np.sin(sunset_hour_angle)
        )
    return np.maximum(radiation_grid, 0)


def main():
    tmax_files = climate_exposure_module.extract_and_index_monthly_files("tmax", "tmax")
    tmin_files = climate_exposure_module.extract_and_index_monthly_files("tmin", "tmin")
    radiation_table = compute_extraterrestrial_radiation_grid()
    cell_row_indices = np.repeat(np.arange(NY), NX)
    
    crop_hazard_accumulators = {}
    for crop_name in CROPS:
        crop_grids = np.load(os.path.join(WORK, f"grids_{crop_name}.npz"))
        valid_cells = np.load(os.path.join(WORK, f"series_prec_{crop_name}.npz"))["cells"]
        crop_hazard_accumulators[crop_name] = {
            "cells": valid_cells,
            "rows": cell_row_indices[valid_cells],
            "weights_gs": (
                crop_grids["w_cur"].reshape(-1, 12)[valid_cells],
                crop_grids["w_prev"].reshape(-1, 12)[valid_cells]
            ),
            "weights_flow": (
                crop_grids["wf_cur"].reshape(-1, 12)[valid_cells],
                crop_grids["wf_prev"].reshape(-1, 12)[valid_cells]
            ),
            "et0_gs": np.zeros((len(ANALYSIS_YEARS), len(valid_cells))),
            "heat_exceedance": np.zeros((len(ANALYSIS_YEARS), len(valid_cells))),
            "teff_flow": np.zeros((len(ANALYSIS_YEARS), len(valid_cells)))
        }

    for year_idx in range(START_YEAR_BUFFER, END_YEAR + 1):
        for month_idx in range(1, 13):
            tmax_raster = climate_exposure_module.read_raster_layer(tmax_files[(year_idx, month_idx)])
            tmin_raster = climate_exposure_module.read_raster_layer(tmin_files[(year_idx, month_idx)])
            
            for crop_name, crop_data in crop_hazard_accumulators.items():
                tmax_crop = tmax_raster[crop_data["cells"]]
                tmin_crop = tmin_raster[crop_data["cells"]]
                tmean_crop = (tmax_crop + tmin_crop) / 2.0
                
                et0_monthly = 0.0023 * (tmean_crop + 17.8) * np.sqrt(np.maximum(tmax_crop - tmin_crop, 0)) * 0.408 * radiation_table[month_idx - 1, crop_data["rows"]] * MONTH_DAYS[month_idx - 1]
                et0_monthly = np.maximum(et0_monthly, 0)
                
                teff_monthly = (tmean_crop + tmax_crop) / 2.0
                critical_temp = CROPS[crop_name]["tcrit"]
                heat_exceedance_monthly = np.maximum(teff_monthly - critical_temp, 0)
                
                mappings = [
                    (crop_data["weights_gs"], "et0_gs", et0_monthly),
                    (crop_data["weights_flow"], "heat_exceedance", heat_exceedance_monthly),
                    (crop_data["weights_flow"], "teff_flow", teff_monthly)
                ]
                
                for (cur_weights, prev_weights), series_key, monthly_val in mappings:
                    w_cur_m = cur_weights[:, month_idx - 1]
                    w_prev_m = prev_weights[:, month_idx - 1]
                    
                    if ANALYSIS_YEARS[0] <= year_idx <= ANALYSIS_YEARS[-1]:
                        crop_data[series_key][year_idx - ANALYSIS_YEARS[0]] += np.where(w_cur_m > 0, w_cur_m * monthly_val, 0.0)
                    if ANALYSIS_YEARS[0] <= year_idx + 1 <= ANALYSIS_YEARS[-1]:
                        crop_data[series_key][year_idx + 1 - ANALYSIS_YEARS[0]] += np.where(w_prev_m > 0, w_prev_m * monthly_val, 0.0)
                        
        print("hazards", year_idx, flush=True)

    for crop_name, crop_data in crop_hazard_accumulators.items():
        flowering_weight_sum = crop_data["weights_flow"][0].sum(axis=1) + crop_data["weights_flow"][1].sum(axis=1)
        flowering_weight_sum = np.where(flowering_weight_sum > 0, flowering_weight_sum, np.nan)
        
        np.savez_compressed(
            os.path.join(WORK, f"hazards_{crop_name}.npz"),
            years=ANALYSIS_YEARS,
            cells=crop_data["cells"],
            et0_gs=crop_data["et0_gs"].astype("float32"),
            heat_flow=(crop_data["heat_exceedance"] / flowering_weight_sum).astype("float32"),
            teff_flow=(crop_data["teff_flow"] / flowering_weight_sum).astype("float32")
        )
        print(crop_name, "saved", len(crop_data["cells"]), "cells")


if __name__ == "__main__":
    main()
