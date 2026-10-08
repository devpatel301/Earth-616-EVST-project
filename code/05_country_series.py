import os

import numpy as np
import pandas as pd

from config import BASE, CROPS, RECENT, WORK, PROC, season_kc

STANDARD_DEVIATION_FLOOR = {"teff": 0.05, "mr": 0.01}


def compute_weighted_mean_1d(values_matrix, weights_vector):
    finite_mask = np.isfinite(values_matrix)
    safe_values = np.where(finite_mask, values_matrix, 0.0)
    effective_weights = np.maximum(finite_mask.astype(float) @ weights_vector, 1e-12)
    return (safe_values @ weights_vector) / effective_weights


def main():
    country_grid = np.load(os.path.join(WORK, "country_grid.npy")).ravel()
    annual_series_records = []
    country_shift_records = []
    
    for crop_name in CROPS:
        precip_data = np.load(os.path.join(WORK, f"series_prec_{crop_name}.npz"))
        hazard_data = np.load(os.path.join(WORK, f"hazards_{crop_name}.npz"))
        tmax_data = np.load(os.path.join(WORK, f"series_tmax_{crop_name}.npz"))
        tavg_data = np.load(os.path.join(WORK, f"series_tavg_{crop_name}.npz"))
        grid_data = np.load(os.path.join(WORK, f"grids_{crop_name}.npz"))
        
        valid_cells = precip_data["cells"]
        assert (valid_cells == hazard_data["cells"]).all() and (valid_cells == tmax_data["cells"]).all()
        
        analysis_years = precip_data["years"]
        total_area_vector = grid_data["area_A"].ravel()[valid_cells]
        rainfed_area_vector = np.minimum(grid_data["area_R"].ravel()[valid_cells], total_area_vector)
        
        precip_gs = precip_data["gs"].astype("float64")
        crop_kc = season_kc(crop_name)
        etc_gs = crop_kc * hazard_data["et0_gs"].astype("float64")
        
        moisture_ratio = np.where(etc_gs > 0, precip_gs / np.where(etc_gs > 0, etc_gs, 1.0), np.nan)
        water_deficit = np.clip(1.0 - moisture_ratio, 0.0, 1.0)
        
        heat_exceedance = hazard_data["heat_flow"].astype("float64")
        teff_flowering = hazard_data["teff_flow"].astype("float64")
        tmax_flowering = tmax_data["flow"].astype("float64")
        tavg_gs = tavg_data["gs"].astype("float64")
        
        baseline_mask = (analysis_years >= BASE[0]) & (analysis_years <= BASE[1])
        recent_mask = (analysis_years >= RECENT[0]) & (analysis_years <= RECENT[1])
        
        snr_temperature = (
            np.nanmean(teff_flowering[recent_mask], axis=0) - np.nanmean(teff_flowering[baseline_mask], axis=0)
        ) / np.maximum(np.nanstd(teff_flowering[baseline_mask], axis=0, ddof=1), STANDARD_DEVIATION_FLOOR["teff"])
        
        snr_water = -(
            np.nanmean(moisture_ratio[recent_mask], axis=0) - np.nanmean(moisture_ratio[baseline_mask], axis=0)
        ) / np.maximum(np.nanstd(moisture_ratio[baseline_mask], axis=0, ddof=1), STANDARD_DEVIATION_FLOOR["mr"])
        
        np.savez_compressed(
            os.path.join(WORK, f"cellmaps_{crop_name}.npz"),
            cells=valid_cells,
            A=total_area_vector,
            R=rainfed_area_vector,
            heat_R=np.nanmean(heat_exceedance[recent_mask], axis=0),
            heat_B=np.nanmean(heat_exceedance[baseline_mask], axis=0),
            def_R=np.nanmean(water_deficit[recent_mask], axis=0),
            def_B=np.nanmean(water_deficit[baseline_mask], axis=0),
            snr_heat=snr_temperature,
            snr_water=snr_water,
            teff_B=np.nanmean(teff_flowering[baseline_mask], axis=0),
            teff_R=np.nanmean(teff_flowering[recent_mask], axis=0),
            mr_B=np.nanmean(moisture_ratio[baseline_mask], axis=0),
            mr_R=np.nanmean(moisture_ratio[recent_mask], axis=0)
        )
        
        country_codes_in_cells = country_grid[valid_cells]
        for country_m49_code in np.unique(country_codes_in_cells):
            if country_m49_code < 0:
                continue
            country_mask = country_codes_in_cells == country_m49_code
            total_crop_area_country = total_area_vector[country_mask]
            rainfed_crop_area_country = rainfed_area_vector[country_mask]
            
            if total_crop_area_country.sum() <= 0:
                continue

            national_heat_hazard_by_year = compute_weighted_mean_1d(heat_exceedance[:, country_mask], total_crop_area_country)
            national_water_deficit_by_year = np.where(
                np.isfinite(water_deficit[:, country_mask]), water_deficit[:, country_mask], 0.0
            ) @ rainfed_crop_area_country / total_crop_area_country.sum()
            
            national_moisture_ratio_by_year = (
                compute_weighted_mean_1d(moisture_ratio[:, country_mask], rainfed_crop_area_country)
                if rainfed_crop_area_country.sum() > 0
                else np.full(len(analysis_years), np.nan)
            )
            national_teff_by_year = compute_weighted_mean_1d(teff_flowering[:, country_mask], total_crop_area_country)
            
            for year_idx, year_val in enumerate(analysis_years):
                annual_series_records.append({
                    "crop": crop_name,
                    "m49": int(country_m49_code),
                    "year": int(year_val),
                    "H_heat": national_heat_hazard_by_year[year_idx],
                    "H_water": national_water_deficit_by_year[year_idx],
                    "mr_rainfed": national_moisture_ratio_by_year[year_idx],
                    "teff_flow": national_teff_by_year[year_idx],
                    "tmax_flow": compute_weighted_mean_1d(tmax_flowering[year_idx:year_idx + 1, country_mask], total_crop_area_country)[0],
                    "tavg_gs": compute_weighted_mean_1d(tavg_gs[year_idx:year_idx + 1, country_mask], total_crop_area_country)[0],
                    "prec_gs": compute_weighted_mean_1d(precip_gs[year_idx:year_idx + 1, country_mask], total_crop_area_country)[0],
                    "etc_gs": compute_weighted_mean_1d(etc_gs[year_idx:year_idx + 1, country_mask], total_crop_area_country)[0]
                })
                
            snr_t_country = snr_temperature[country_mask]
            snr_w_country = snr_water[country_mask]
            finite_t_mask = np.isfinite(snr_t_country)
            finite_w_mask = np.isfinite(snr_w_country) & (rainfed_crop_area_country > 0)
            
            mean_snr_heat = (
                (snr_t_country[finite_t_mask] * total_crop_area_country[finite_t_mask]).sum() / total_crop_area_country[finite_t_mask].sum()
                if finite_t_mask.any() else np.nan
            )
            mean_snr_water = (
                (snr_w_country[finite_w_mask] * rainfed_crop_area_country[finite_w_mask]).sum() / total_crop_area_country.sum()
                if finite_w_mask.any() else 0.0
            )
            
            country_shift_records.append({
                "crop": crop_name,
                "m49": int(country_m49_code),
                "area_ha": total_crop_area_country.sum(),
                "rainfed_share": rainfed_crop_area_country.sum() / total_crop_area_country.sum(),
                "snr_heat_mean": mean_snr_heat,
                "snr_water_mean": mean_snr_water,
                "share_area_warming_sig": (total_crop_area_country[finite_t_mask & (snr_t_country > 1)]).sum() / total_crop_area_country.sum(),
                "kc_season": crop_kc
            })
            
        print(crop_name, "countries:", len(np.unique(country_codes_in_cells[country_codes_in_cells >= 0])), flush=True)
        
    pd.DataFrame(annual_series_records).to_pickle(os.path.join(PROC, "country_series.pkl"))
    pd.DataFrame(country_shift_records).to_csv(os.path.join(PROC, "country_shift.csv"), index=False)


if __name__ == "__main__":
    main()
