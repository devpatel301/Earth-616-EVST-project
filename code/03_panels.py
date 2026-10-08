import io
import os
import zipfile

import geopandas as gpd
import numpy as np
import pandas as pd

from config import CORE, CROPS, FAO_YEARS, MIN_SHARE_PCT, MOUNTAIN_M, PROC, RAW, TOP_N, WORK

QCL_ZIP_PATH = os.path.join(RAW, "faostat", "Production_Crops_Livestock_E_All_Data_(Normalized).zip")
TARGET_CONTINENTS = ("Africa", "Europe")


def load_qcl_dataframe():
    with zipfile.ZipFile(QCL_ZIP_PATH) as zip_ref:
        csv_filename = [name for name in zip_ref.namelist() if name.endswith("(Normalized).csv")][0]
        qcl_df = pd.read_csv(io.BytesIO(zip_ref.read(csv_filename)), encoding="latin-1", low_memory=False)
    crop_item_map = {crop_info["faostat_item"]: crop_name for crop_name, crop_info in CROPS.items()}
    filtered_df = qcl_df[
        qcl_df.Item.isin(crop_item_map) & qcl_df.Element.isin(["Production", "Area harvested", "Yield"])
    ].copy()
    filtered_df["crop"] = filtered_df.Item.map(crop_item_map)
    filtered_df["m49"] = filtered_df["Area Code (M49)"].astype(str).str.replace("'", "").astype(int)
    filtered_df = filtered_df[(filtered_df["Area Code"] < 5000) & (filtered_df["Area Code"] != 351)]
    return filtered_df


def load_continent_mapping():
    shapefile_name = [filename for filename in os.listdir(os.path.join(WORK, "naturalearth")) if filename.endswith(".shp")][0]
    geo_df = gpd.read_file(os.path.join(WORK, "naturalearth", shapefile_name))
    geo_df["m49"] = geo_df["ISO_N3_EH"].astype(str).replace("-99", "-1").astype(int)
    return geo_df.set_index("m49")["CONTINENT"].to_dict()


def main():
    qcl_df = load_qcl_dataframe()
    qcl_df.to_pickle(os.path.join(WORK, "qcl_4crops.pkl"))
    latest_year = int(qcl_df.Year.max())
    analysis_years = list(range(latest_year - FAO_YEARS + 1, latest_year + 1))
    
    window_df = qcl_df[qcl_df.Year.isin(analysis_years)].pivot_table(
        index=["crop", "Area", "m49"],
        columns="Element",
        values="Value",
        aggfunc="mean"
    ).reset_index()
    window_df = window_df.dropna(subset=["Production"])
    window_df = window_df[window_df.Production > 0]
    
    continent_map = load_continent_mapping()
    window_df["continent"] = window_df.m49.map(continent_map)
    window_df["share_pct"] = 100 * window_df.Production / window_df.groupby("crop").Production.transform("sum")
    window_df["world_rank"] = window_df.groupby("crop").Production.rank(ascending=False, method="first").astype(int)
    window_df["cont_rank"] = window_df.groupby(["crop", "continent"]).Production.rank(ascending=False, method="first").astype(int)

    shared_continent_countries = {}
    for continent_name in TARGET_CONTINENTS:
        best_candidate = None
        for country_m49, country_group in window_df[window_df.continent == continent_name].groupby("m49"):
            if len(country_group) == len(CROPS) and (country_group.cont_rank <= TOP_N).all():
                total_production = country_group.Production.sum()
                best_candidate = (country_m49, total_production) if best_candidate is None or total_production > best_candidate[1] else best_candidate
        shared_continent_countries[continent_name] = best_candidate[0] if best_candidate else None
        selected_country_name = window_df[window_df.m49 == best_candidate[0]].Area.iloc[0] if best_candidate else "none (per-crop largest producer used)"
        print(f"{continent_name}: country in continent top-{TOP_N} for ALL crops -> {selected_country_name}")

    country_grid = np.load(os.path.join(WORK, "country_grid.npy"))
    zones_data = np.load(os.path.join(WORK, "zones.npz"))
    koppen_one_hot = np.stack([(zones_data["kg"] == k).astype("float32") for k in range(5)])
    elevation_grid = zones_data["elev"]
    
    core_m49_dict = window_df[window_df.Area.isin(CORE)].drop_duplicates("m49").set_index("Area").m49.to_dict()
    assert len(core_m49_dict) == len(CORE), core_m49_dict

    panel_rows = []
    for crop_name in CROPS:
        crop_group = window_df[window_df.crop == crop_name]
        selected_countries = {}
        
        for core_country_name in CORE:
            selected_countries[core_m49_dict[core_country_name]] = "core (USA, Brazil, India, China)"
            
        for continent_name in TARGET_CONTINENTS:
            if shared_continent_countries[continent_name] is not None:
                selected_countries.setdefault(
                    shared_continent_countries[continent_name],
                    f"{continent_name}: top-{TOP_N} in {continent_name} for every crop"
                )
            else:
                top_continent_producer = crop_group[crop_group.continent == continent_name].sort_values("Production", ascending=False).iloc[0]
                selected_countries.setdefault(
                    int(top_continent_producer.m49),
                    f"{continent_name}: largest {continent_name} producer of this crop"
                )
                
        for _, top_row in crop_group.sort_values("Production", ascending=False).head(TOP_N).iterrows():
            selected_countries.setdefault(int(top_row.m49), f"world top-{TOP_N} producer")
            
        crop_area_grid = np.load(os.path.join(WORK, f"grids_{crop_name}.npz"))["area_A"]
        
        for country_m49, selection_reason in selected_countries.items():
            country_record = crop_group[crop_group.m49 == country_m49].iloc[0]
            country_mask = (country_grid == country_m49) & (crop_area_grid > 0)
            valid_area = crop_area_grid[country_mask]
            assert valid_area.sum() > 0, (crop_name, country_record.Area)
            
            koppen_shares = [(koppen_one_hot[k][country_mask] * valid_area).sum() / valid_area.sum() for k in range(5)]
            finite_elevation_mask = np.isfinite(elevation_grid[country_mask])
            mean_elevation = (elevation_grid[country_mask][finite_elevation_mask] * valid_area[finite_elevation_mask]).sum() / valid_area[finite_elevation_mask].sum()
            dominant_koppen_letter = "ABCDE"[int(np.argmax(koppen_shares))]
            is_mountainous = bool(mean_elevation >= MOUNTAIN_M)
            climate_class_label = dominant_koppen_letter + ("+M" if is_mountainous else "")
            
            panel_rows.append({
                "crop": crop_name,
                "country": country_record.Area,
                "m49": int(country_m49),
                "continent": country_record.continent,
                "rank": int(country_record.world_rank),
                "share_pct": country_record.share_pct,
                "production_t": country_record.Production,
                "yield_kg_ha": country_record.Yield,
                "area_ha": country_record["Area harvested"],
                "kgA": koppen_shares[0],
                "kgB": koppen_shares[1],
                "kgC": koppen_shares[2],
                "kgD": koppen_shares[3],
                "kgE": koppen_shares[4],
                "elev_m": mean_elevation,
                "dominant": dominant_koppen_letter,
                "mountain": is_mountainous,
                "classes": climate_class_label,
                "small_producer": bool(country_record.share_pct < MIN_SHARE_PCT),
                "reason": selection_reason,
                "spam_area_ha": valid_area.sum()
            })
            
    panels_dataframe = pd.DataFrame(panel_rows)
    panels_dataframe.insert(0, "years", f"{analysis_years[0]}-{analysis_years[-1]}")
    crop_order_map = {crop_key: idx for idx, crop_key in enumerate(CROPS)}
    panels_dataframe = panels_dataframe.sort_values(
        by=["crop", "rank"],
        key=lambda series: series.map(crop_order_map) if series.name == "crop" else series
    ).reset_index(drop=True)
    
    panels_dataframe.to_csv(os.path.join(PROC, "panels.csv"), index=False)
    
    crops_per_country = panels_dataframe.groupby("country").crop.nunique()
    shared_countries = sorted(crops_per_country[crops_per_country == len(CROPS)].index)
    pd.DataFrame({"country": shared_countries}).to_csv(os.path.join(PROC, "shared_panel.csv"), index=False)
    
    pd.set_option("display.width", 220)
    print(panels_dataframe[["crop", "country", "continent", "rank", "share_pct", "classes", "elev_m", "small_producer", "reason"]].round(2).to_string(index=False))
    print("panel share of world production (%):", panels_dataframe.groupby("crop").share_pct.sum().round(1).to_dict())
    print("shared by all four crops:", shared_countries)


if __name__ == "__main__":
    main()
