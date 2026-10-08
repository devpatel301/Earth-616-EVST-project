import importlib
import os
import zipfile

import numpy as np
import rasterio

from config import GRID_COLUMNS, GRID_ROWS, RAW_DIR, WORK_DIR

climate_exposure_module = importlib.import_module("04_climate_exposure")
CLIMATOLOGY_PERIOD = (1991, 2020)


def main():
    weather_file_map = {
        source_var: climate_exposure_module.monthly_files(folder, var_name)
        for source_var, folder, var_name in (
            ("prec", "worldclim", "prec"),
            ("tmax", "tmax", "tmax"),
            ("tmin", "tmin", "tmin")
        )
    }
    total_cells = GRID_ROWS * GRID_COLUMNS
    monthly_temperature = np.zeros((12, total_cells))
    monthly_precipitation = np.zeros((12, total_cells))
    num_years = CLIMATOLOGY_PERIOD[1] - CLIMATOLOGY_PERIOD[0] + 1

    for year in range(CLIMATOLOGY_PERIOD[0], CLIMATOLOGY_PERIOD[1] + 1):
        for month_idx in range(12):
            month_num = month_idx + 1
            tmax_data = climate_exposure_module.read(weather_file_map["tmax"][(year, month_num)])
            tmin_data = climate_exposure_module.read(weather_file_map["tmin"][(year, month_num)])
            prec_data = climate_exposure_module.read(weather_file_map["prec"][(year, month_num)])
            monthly_temperature[month_idx] += (tmax_data + tmin_data) / 2.0 / num_years
            monthly_precipitation[month_idx] += prec_data / num_years

    mean_annual_temp = monthly_temperature.mean(0)
    mean_annual_precip = monthly_precipitation.sum(0)
    temp_coldest_month = monthly_temperature.min(0)
    temp_hottest_month = monthly_temperature.max(0)

    apr_to_sep_slice = slice(3, 9)
    temp_apr_sep = monthly_temperature[apr_to_sep_slice].mean(0)
    temp_oct_mar = np.concatenate([monthly_temperature[9:], monthly_temperature[:3]]).mean(0)
    precip_apr_sep = monthly_precipitation[apr_to_sep_slice].sum(0)
    precip_oct_mar = mean_annual_precip - precip_apr_sep

    is_summer_apr_sep = temp_apr_sep >= temp_oct_mar
    precip_summer = np.where(is_summer_apr_sep, precip_apr_sep, precip_oct_mar)
    precip_winter = mean_annual_precip - precip_summer

    with np.errstate(invalid="ignore", divide="ignore"):
        precip_threshold = np.where(
            precip_winter > 0.7 * mean_annual_precip,
            2.0 * mean_annual_temp,
            np.where(
                precip_summer > 0.7 * mean_annual_precip,
                2.0 * mean_annual_temp + 28.0,
                2.0 * mean_annual_temp + 14.0
            )
        )

    koppen_grid = np.full(total_cells, -1, dtype="int8")
    valid_data_mask = np.isfinite(mean_annual_temp) & np.isfinite(mean_annual_precip)
    is_arid_b = valid_data_mask & (mean_annual_precip < 10.0 * precip_threshold)

    koppen_grid[valid_data_mask & ~is_arid_b & (temp_coldest_month >= 18.0)] = 0
    koppen_grid[is_arid_b] = 1
    koppen_grid[valid_data_mask & ~is_arid_b & (temp_hottest_month > 10.0) & (temp_coldest_month > 0.0) & (temp_coldest_month < 18.0)] = 2
    koppen_grid[valid_data_mask & ~is_arid_b & (temp_hottest_month > 10.0) & (temp_coldest_month <= 0.0)] = 3
    koppen_grid[valid_data_mask & ~is_arid_b & (temp_hottest_month <= 10.0)] = 4

    elev_zip_path = os.path.join(RAW_DIR, "worldclim", "wc2.1_10m_elev.zip")
    with zipfile.ZipFile(elev_zip_path) as elevation_archive:
        tif_filename = [name for name in elevation_archive.namelist() if name.endswith(".tif")][0]
        elevation_archive.extract(tif_filename, os.path.join(WORK_DIR, "elev"))

    with rasterio.open(os.path.join(WORK_DIR, "elev", tif_filename)) as elev_raster:
        elevation_grid = elev_raster.read(1).astype("float32")
        elevation_grid[elevation_grid < -1000] = np.nan

    np.savez_compressed(
        os.path.join(WORK_DIR, "zones.npz"),
        kg=koppen_grid.reshape(GRID_ROWS, GRID_COLUMNS),
        elev=elevation_grid,
        mat=mean_annual_temp.reshape(GRID_ROWS, GRID_COLUMNS).astype("float32"),
        map=mean_annual_precip.reshape(GRID_ROWS, GRID_COLUMNS).astype("float32")
    )
    land_cells = koppen_grid >= 0
    print("land cells", land_cells.sum(), "shares A-E:", [round(float((koppen_grid[land_cells] == class_val).mean()), 3) for class_val in range(5)])


if __name__ == "__main__":
    main()
