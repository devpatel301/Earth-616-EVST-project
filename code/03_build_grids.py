import gzip
import os
import shutil
import sys
import zipfile

import geopandas as gpd
import numpy as np
import rasterio
import xarray as xr
from rasterio import features
from rasterio.transform import from_origin

from config import CROPS, GRID_COLUMNS, GRID_ROWS, GRID_RESOLUTION, RAW_DIR, WORK_DIR

TRANSFORM_10M = from_origin(-180, 90, GRID_RESOLUTION, GRID_RESOLUTION)
DAYS_PER_MONTH = np.array([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])
MONTH_START_DOY = np.concatenate([[1], 1 + np.cumsum(DAYS_PER_MONTH)[:-1]])


def country_grid():
    output_path = os.path.join(WORK_DIR, "country_grid.npy")
    shapefile_dir = os.path.join(WORK_DIR, "naturalearth")
    zip_path = os.path.join(RAW_DIR, "naturalearth", "ne_50m_admin_0_countries.zip")
    with zipfile.ZipFile(zip_path) as shapefile_archive:
        shapefile_archive.extractall(shapefile_dir)
    shapefile_name = [f for f in os.listdir(shapefile_dir) if f.endswith(".shp")][0]
    countries_gdf = gpd.read_file(os.path.join(shapefile_dir, shapefile_name))
    country_numeric_codes = countries_gdf["ISO_N3_EH"].astype(str).replace("-99", "-1").astype(int)
    geometry_code_pairs = list(zip(countries_gdf.geometry, country_numeric_codes))
    country_id_grid = features.rasterize(
        geometry_code_pairs,
        out_shape=(GRID_ROWS, GRID_COLUMNS),
        transform=TRANSFORM_10M,
        fill=-1,
        dtype="int32",
        all_touched=False
    )
    np.save(output_path, country_id_grid)
    countries_gdf[["ADMIN", "ADM0_A3", "ISO_N3_EH"]].to_csv(
        os.path.join(WORK_DIR, "naturalearth_codes.csv"), index=False
    )
    print("country grid done:", len(np.unique(country_id_grid)) - 1, "countries")
    return country_id_grid


def aggregate_5min_to_10min(fine_grid):
    cleaned_grid = np.where(fine_grid < 0, 0, fine_grid)
    return cleaned_grid.reshape(GRID_ROWS, 2, GRID_COLUMNS, 2).sum(axis=(1, 3))


def load_spam_areas(crop_code):
    area_dict = {}
    for area_type in ("A", "I", "R"):
        tiff_path = os.path.join(WORK_DIR, "spam", f"spam2010V2r0_global_H_{crop_code}_{area_type}.tif")
        if not os.path.exists(tiff_path):
            spam_zip = os.path.join(RAW_DIR, "spam", "spam2010v2r0_global_harv_area.geotiff.zip")
            with zipfile.ZipFile(spam_zip) as spam_archive:
                spam_archive.extract(os.path.basename(tiff_path), os.path.join(WORK_DIR, "spam"))
        with rasterio.open(tiff_path) as raster_reader:
            area_dict[area_type] = aggregate_5min_to_10min(raster_reader.read(1).astype("float64"))
    return area_dict


def load_sacks_calendar(crop_name, is_filled):
    nc_filename = f"{crop_name}.crop.calendar{'.fill' if is_filled else ''}.nc"
    source_path = os.path.join(RAW_DIR, "sacks", nc_filename + ".gz")
    dest_path = os.path.join(WORK_DIR, "sacks", nc_filename)
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    if not os.path.exists(dest_path):
        with gzip.open(source_path) as compressed_file, open(dest_path, "wb") as output_file:
            shutil.copyfileobj(compressed_file, output_file)
    dataset = xr.open_dataset(dest_path)
    assert dataset.latitude.values[0] > dataset.latitude.values[-1], "expect north-up"
    return dataset["plant"].values.astype("float64"), dataset["harvest"].values.astype("float64")


def resample_calendar_to_10min(values_5min, area_5min):
    values_blocks = values_5min.reshape(GRID_ROWS, 2, GRID_COLUMNS, 2).transpose(0, 2, 1, 3).reshape(GRID_ROWS, GRID_COLUMNS, 4)
    area_blocks = area_5min.reshape(GRID_ROWS, 2, GRID_COLUMNS, 2).transpose(0, 2, 1, 3).reshape(GRID_ROWS, GRID_COLUMNS, 4)
    weighted_area = np.where(np.isfinite(values_blocks), area_blocks + 1e-6, -1.0)
    best_subcell_idx = weighted_area.argmax(axis=2)
    return np.take_along_axis(values_blocks, best_subcell_idx[..., None], axis=2)[..., 0]


def calculate_month_weights(plant_doy, harvest_doy, fraction_start=0.0, fraction_end=1.0):
    weights_harvest_year = np.zeros(plant_doy.shape + (12,), dtype="float32")
    weights_previous_year = np.zeros_like(weights_harvest_year)
    valid_dates_mask = np.isfinite(plant_doy) & np.isfinite(harvest_doy)
    plant_days = np.where(valid_dates_mask, np.clip(np.round(plant_doy), 1, 365), 1).astype(int)
    harvest_days = np.where(valid_dates_mask, np.clip(np.round(harvest_doy), 1, 365), 1).astype(int)

    unique_date_pairs = set(zip(plant_days[valid_dates_mask].ravel(), harvest_days[valid_dates_mask].ravel()))
    for p_day, h_day in unique_date_pairs:
        crosses_year = p_day > h_day
        season_length_days = (h_day - p_day) + (365 if crosses_year else 0)
        start_day_offset = int(round(p_day + fraction_start * season_length_days))
        end_day_offset = int(round(p_day + fraction_end * season_length_days))

        plant_year_active = np.zeros(365, bool)
        next_year_active = np.zeros(365, bool)
        for day in range(start_day_offset, end_day_offset + 1):
            if day <= 365:
                plant_year_active[day - 1] = True
            else:
                next_year_active[day - 366] = True

        current_year_active, prev_year_active = (
            (next_year_active, plant_year_active) if crosses_year else (plant_year_active, np.zeros(365, bool))
        )
        monthly_current_weights = np.array(
            [current_year_active[start_d - 1:start_d - 1 + num_d].mean() for start_d, num_d in zip(MONTH_START_DOY, DAYS_PER_MONTH)]
        )
        monthly_prev_weights = np.array(
            [prev_year_active[start_d - 1:start_d - 1 + num_d].mean() for start_d, num_d in zip(MONTH_START_DOY, DAYS_PER_MONTH)]
        )

        selected_cells = valid_dates_mask & (plant_days == p_day) & (harvest_days == h_day)
        weights_harvest_year[selected_cells] = monthly_current_weights
        weights_previous_year[selected_cells] = monthly_prev_weights

    return weights_harvest_year, weights_previous_year


def build_crop_calendar(crop_name, area_5min_total):
    calendar_names = CROPS[crop_name]["sacks"]
    plant_doy_grid = np.full((GRID_ROWS, GRID_COLUMNS), np.nan)
    harvest_doy_grid = np.full((GRID_ROWS, GRID_COLUMNS), np.nan)
    calendar_source_grid = np.zeros((GRID_ROWS, GRID_COLUMNS), dtype="int8")

    for is_filled, source_code in ((False, 1), (True, 2)):
        for calendar_name in calendar_names:
            plant_5min, harvest_5min = load_sacks_calendar(calendar_name, is_filled)
            plant_10min = resample_calendar_to_10min(plant_5min, area_5min_total)
            harvest_10min = resample_calendar_to_10min(harvest_5min, area_5min_total)
            cells_to_fill = np.isnan(plant_doy_grid) & np.isfinite(plant_10min) & np.isfinite(harvest_10min)
            plant_doy_grid[cells_to_fill] = plant_10min[cells_to_fill]
            harvest_doy_grid[cells_to_fill] = harvest_10min[cells_to_fill]
            calendar_source_grid[cells_to_fill] = source_code

    return plant_doy_grid, harvest_doy_grid, calendar_source_grid


def main():
    if not os.path.exists(os.path.join(WORK_DIR, "country_grid.npy")):
        country_grid()

    crops_filter = sys.argv[1:]
    for crop_name, crop_info in CROPS.items():
        if crops_filter and crop_name not in crops_filter:
            continue
        spam_area_dict = load_spam_areas(crop_info["spam"])
        spam_all_tif = os.path.join(WORK_DIR, "spam", f"spam2010V2r0_global_H_{crop_info['spam']}_A.tif")
        with rasterio.open(spam_all_tif) as raster_reader:
            area_5min_total = np.where(raster_reader.read(1) < 0, 0, raster_reader.read(1)).astype("float64")

        plant_grid, harvest_grid, source_grid = build_crop_calendar(crop_name, area_5min_total)
        season_w_cur, season_w_prev = calculate_month_weights(plant_grid, harvest_grid)
        flowering_w_cur, flowering_w_prev = calculate_month_weights(plant_grid, harvest_grid, 0.45, 0.70)

        crop_cells_mask = spam_area_dict["A"] > 0
        total_crop_area = spam_area_dict["A"][crop_cells_mask].sum()
        observed_share = spam_area_dict["A"][crop_cells_mask & (source_grid == 1)].sum() / total_crop_area
        filled_share = spam_area_dict["A"][crop_cells_mask & (source_grid == 2)].sum() / total_crop_area
        irrigated_share = spam_area_dict["I"].sum() / spam_area_dict["A"].sum()

        print(
            f"{crop_name}: area {total_crop_area / 1e6:.1f} Mha, irrigated {100 * irrigated_share:.0f}%, "
            f"calendar observed for {100 * observed_share:.1f}% of area, filled {100 * filled_share:.1f}%"
        )
        np.savez_compressed(
            os.path.join(WORK_DIR, f"grids_{crop_name}.npz"),
            area_A=spam_area_dict["A"],
            area_I=spam_area_dict["I"],
            area_R=spam_area_dict["R"],
            w_cur=season_w_cur,
            w_prev=season_w_prev,
            wf_cur=flowering_w_cur,
            wf_prev=flowering_w_prev,
            cal_src=source_grid,
            plant=plant_grid,
            harvest=harvest_grid
        )


if __name__ == "__main__":
    main()
