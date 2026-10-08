import os

import numpy as np
import pandas as pd
import rasterio

from config import CROPS, PROCESSED_DIR, RAW_DIR, WORK_DIR


def main():
    beck_file_path = os.path.join(RAW_DIR, "koppen", "koppen_geiger_1991_2020_0p5.tif")
    with rasterio.open(beck_file_path) as raster_reader:
        beck_raw_grid = raster_reader.read(1).astype(int)
        assert beck_raw_grid.shape == (360, 720)

    class_lookup_table = np.full(256, -1)
    group_ranges = (range(1, 4), range(4, 8), range(8, 17), range(17, 29), range(29, 31))
    for group_idx, code_range in enumerate(group_ranges):
        class_lookup_table[list(code_range)] = group_idx

    beck_10min_grid = np.repeat(np.repeat(class_lookup_table[beck_raw_grid], 3, axis=0), 3, axis=1)
    our_zones_data = np.load(os.path.join(WORK_DIR, "zones.npz"))["kg"]
    valid_comparison_mask = (our_zones_data >= 0) & (beck_10min_grid >= 0)

    results_rows = [
        dict(
            weight="all land cells",
            agreement=float((our_zones_data[valid_comparison_mask] == beck_10min_grid[valid_comparison_mask]).mean()),
            n=int(valid_comparison_mask.sum())
        )
    ]

    for crop_name in CROPS:
        crop_area_grid = np.load(os.path.join(WORK_DIR, f"grids_{crop_name}.npz"))["area_A"]
        crop_weight_grid = np.where(valid_comparison_mask, crop_area_grid, 0.0)
        agreement_rate = float(
            (crop_weight_grid * (our_zones_data == beck_10min_grid)).sum() / crop_weight_grid.sum()
        )
        results_rows.append(
            dict(
                weight=f"{crop_name} harvested area",
                agreement=agreement_rate,
                n=int((crop_weight_grid > 0).sum())
            )
        )

    summary_df = pd.DataFrame(results_rows)
    summary_df.to_csv(os.path.join(PROCESSED_DIR, "koppen_check.csv"), index=False)
    print(summary_df.round(3).to_string(index=False))

    panel_countries_df = pd.read_csv(os.path.join(PROCESSED_DIR, "panels.csv"))
    country_id_grid = np.load(os.path.join(WORK_DIR, "country_grid.npy"))
    country_class_checks = []

    for _, row in panel_countries_df.iterrows():
        crop_area_grid = np.load(os.path.join(WORK_DIR, f"grids_{row.crop}.npz"))["area_A"]
        country_crop_mask = (country_id_grid == row.m49) & (crop_area_grid > 0) & (beck_10min_grid >= 0)
        beck_class_shares = [
            (crop_area_grid[country_crop_mask] * (beck_10min_grid[country_crop_mask] == class_code)).sum()
            for class_code in range(5)
        ]
        dominant_beck_class = "ABCDE"[int(np.argmax(beck_class_shares))]
        country_class_checks.append(
            dict(
                crop=row.crop,
                country=row.country,
                ours=row.dominant,
                beck=dominant_beck_class
            )
        )

    country_check_df = pd.DataFrame(country_class_checks)
    country_check_df.to_csv(os.path.join(PROCESSED_DIR, "koppen_check_countries.csv"), index=False)
    disagreements = country_check_df[country_check_df.ours != country_check_df.beck]
    print(
        "panel countries whose dominant class differs:",
        disagreements.to_string(index=False) if len(disagreements) > 0 else "none",
        f"({(country_check_df.ours == country_check_df.beck).sum()}/{len(country_check_df)} agree)"
    )


if __name__ == "__main__":
    main()
