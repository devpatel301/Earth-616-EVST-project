import io
import os
import zipfile

import numpy as np
import pandas as pd

from config import CROPS, FE_REQ, PROC, RAW, WORK, ZN_REQ

ELEMENT_MAP = {
    "Food supply (kcal/capita/day)": "kcal",
    "Protein supply quantity (g/capita/day)": "protein",
    "Fat supply quantity (g/capita/day)": "fat",
    "Food supply quantity (kg/capita/yr)": "kg",
    "Production": "prod",
    "Domestic supply quantity": "dom",
    "Export quantity": "exp",
    "Import quantity": "imp",
    "Food": "food_kt"
}
NUTRIENT_LIST = ["kcal", "protein", "fat", "zinc", "iron"]


def read_food_balance_sheets(zip_filename):
    with zipfile.ZipFile(os.path.join(RAW, "faostat", zip_filename)) as zip_ref:
        csv_name = [entry for entry in zip_ref.namelist() if entry.endswith("(Normalized).csv")][0]
        raw_df = pd.read_csv(
            io.BytesIO(zip_ref.read(csv_name)),
            encoding="latin-1",
            low_memory=False,
            usecols=["Area Code", "Area Code (M49)", "Area", "Item Code", "Item", "Element", "Year", "Value"]
        )
    filtered_df = raw_df[raw_df.Element.isin(ELEMENT_MAP)].copy()
    filtered_df["el"] = filtered_df.Element.map(ELEMENT_MAP)
    filtered_df["m49"] = filtered_df["Area Code (M49)"].astype(str).str.replace("'", "").astype(int)
    filtered_df["leaf"] = filtered_df["Item Code"] < 2900
    return filtered_df


def load_food_composition_data():
    map_csv_path = os.path.join(os.path.dirname(__file__), "fbs_usda_map.csv")
    usda_mapping_df = pd.read_csv(map_csv_path, comment="#")
    
    usda_zip_path = os.path.join(RAW, "usda", "FoodData_Central_sr_legacy_food_csv_2018-04.zip")
    with zipfile.ZipFile(usda_zip_path) as zip_ref:
        def read_usda_csv(target_name):
            matching_name = [entry for entry in zip_ref.namelist() if entry.endswith(target_name)][0]
            return pd.read_csv(io.BytesIO(zip_ref.read(matching_name)), low_memory=False)
        food_table = read_usda_csv("/food.csv")
        nutrient_table = read_usda_csv("/food_nutrient.csv")
        
    nutrient_id_map = {1095: "zinc_mg100", 1089: "iron_mg100", 1003: "protein_g100", 1008: "kcal100"}
    pivoted_nutrients = nutrient_table[nutrient_table.nutrient_id.isin(nutrient_id_map)].pivot_table(
        index="fdc_id", columns="nutrient_id", values="amount"
    ).rename(columns=nutrient_id_map)
    
    merged_comp = usda_mapping_df.merge(pivoted_nutrients, left_on="fdc_id", right_index=True, how="left")
    merged_comp = merged_comp.merge(food_table[["fdc_id", "description"]], on="fdc_id", how="left")
    
    unmatched_mask = merged_comp.fdc_id == 0
    merged_comp.loc[unmatched_mask, ["zinc_mg100", "iron_mg100"]] = 0.0
    assert merged_comp.loc[~unmatched_mask, "zinc_mg100"].notna().all(), merged_comp[merged_comp.zinc_mg100.isna()]
    
    merged_comp.to_csv(os.path.join(PROC, "composition_used.csv"), index=False)
    return merged_comp.set_index("fbs_item")


def compute_nutrient_supply_table(fbs_dataframe, composition_dataframe):
    leaf_items = fbs_dataframe[fbs_dataframe.leaf & fbs_dataframe.Item.isin(composition_dataframe.index)]
    pivoted_supply = leaf_items.pivot_table(
        index=["m49", "Area", "Year", "Item"],
        columns="el",
        values="Value",
        aggfunc="sum"
    ).reset_index()
    
    for element_col in ELEMENT_MAP.values():
        if element_col not in pivoted_supply:
            pivoted_supply[element_col] = np.nan
            
    grams_per_capita_day = pivoted_supply["kg"].fillna(0.0) * 1000.0 / 365.0
    pivoted_supply["zinc"] = grams_per_capita_day * pivoted_supply.Item.map(composition_dataframe.zinc_mg100) / 100.0
    pivoted_supply["iron"] = grams_per_capita_day * pivoted_supply.Item.map(composition_dataframe.iron_mg100) / 100.0
    return pivoted_supply


def map_item_to_crop(fbs_item_name):
    for crop_name, crop_info in CROPS.items():
        if fbs_item_name in crop_info["fbs_items"]:
            return crop_name
    return None


def load_average_dietary_energy_requirement():
    food_security_zip = os.path.join(RAW, "faostat", "Food_Security_Data_E_All_Data_(Normalized).zip")
    with zipfile.ZipFile(food_security_zip) as zip_ref:
        csv_name = [entry for entry in zip_ref.namelist() if entry.endswith("(Normalized).csv")][0]
        security_df = pd.read_csv(io.BytesIO(zip_ref.read(csv_name)), encoding="latin-1", low_memory=False)
        
    ader_subset = security_df[security_df.Item == "Average dietary energy requirement (kcal/cap/day)"].copy()
    ader_subset["m49"] = ader_subset["Area Code (M49)"].astype(str).str.replace("'", "").astype(int)
    ader_subset["Year"] = ader_subset.Year.astype(str).str[:4].astype(int)
    ader_subset["ader"] = pd.to_numeric(ader_subset.Value, errors="coerce")
    return ader_subset[["m49", "Year", "ader"]].dropna()


def main():
    comp_df = load_food_composition_data()
    current_fbs_df = read_food_balance_sheets("FoodBalanceSheets_E_All_Data_(Normalized).zip")
    historical_fbs_df = read_food_balance_sheets("FoodBalanceSheetsHistoric_E_All_Data_(Normalized).zip")
    
    for tag_name, fbs_table in (("new", current_fbs_df), ("old", historical_fbs_df)):
        unmapped_items = sorted(set(fbs_table[fbs_table.leaf].Item) - set(comp_df.index))
        print(f"FBS {tag_name}: leaf items with no composition mapping:", unmapped_items)
        
    supply_dict = {}
    for tag_name, fbs_table in (("new", current_fbs_df), ("old", historical_fbs_df)):
        calculated_supply = compute_nutrient_supply_table(fbs_table, comp_df)
        calculated_supply["crop"] = calculated_supply.Item.map(map_item_to_crop)
        calculated_supply["method"] = tag_name
        supply_dict[tag_name] = calculated_supply
        
    combined_supply_df = pd.concat(supply_dict.values())
    combined_supply_df.to_pickle(os.path.join(PROC, "nutrient_supply.pkl"))

    grand_total_calories = current_fbs_df[
        (current_fbs_df.Item == "Grand Total") & (current_fbs_df.el == "kcal")
    ].set_index(["m49", "Year"]).Value
    calculated_total_calories = supply_dict["new"].groupby(["m49", "Year"]).kcal.sum()
    check_ratio = (calculated_total_calories / grand_total_calories).dropna()
    print(f"leaf-sum / Grand Total kcal: median {check_ratio.median():.4f}, 5-95% {check_ratio.quantile(0.05):.3f}-{check_ratio.quantile(0.95):.3f}")

    current_supply_df = supply_dict["new"]
    total_national_supply = current_supply_df.groupby(["m49", "Area", "Year"])[NUTRIENT_LIST].sum()
    crop_contribution_df = current_supply_df.dropna(subset=["crop"]).groupby(
        ["m49", "Area", "Year", "crop"]
    )[NUTRIENT_LIST + ["prod", "dom", "exp", "imp"]].sum()
    crop_contribution_df = crop_contribution_df.reset_index().merge(
        total_national_supply.reset_index(), on=["m49", "Area", "Year"], suffixes=("", "_tot")
    )
    
    for nutrient_name in NUTRIENT_LIST:
        crop_contribution_df[f"sh_{nutrient_name}"] = crop_contribution_df[nutrient_name] / crop_contribution_df[f"{nutrient_name}_tot"]
    crop_contribution_df["ssr"] = crop_contribution_df["prod"] / crop_contribution_df["dom"]
    crop_contribution_df.to_csv(os.path.join(PROC, "crop_contrib.csv"), index=False)

    latest_year_num = int(crop_contribution_df.Year.max())
    importance_df = crop_contribution_df[crop_contribution_df.Year >= latest_year_num - 2].groupby(
        ["m49", "Area", "crop"]
    )[[f"sh_{n}" for n in NUTRIENT_LIST] + ["ssr"]].mean().reset_index()
    importance_df["I"] = importance_df[[f"sh_{n}" for n in NUTRIENT_LIST]].mean(axis=1)
    importance_df["years"] = f"{latest_year_num - 2}-{latest_year_num}"
    importance_df.to_csv(os.path.join(PROC, "importance.csv"), index=False)

    ader_df = load_average_dietary_energy_requirement()
    adequacy_df = total_national_supply.reset_index().merge(ader_df, on=["m49", "Year"], how="inner")
    adequacy_df["req_kcal"] = adequacy_df.ader
    adequacy_df["req_protein"] = 0.10 * adequacy_df.ader / 4.0
    adequacy_df["req_fat"] = 0.15 * adequacy_df.ader / 9.0
    adequacy_df["req_zinc"] = ZN_REQ
    adequacy_df["req_iron"] = FE_REQ
    
    for nutrient_name in NUTRIENT_LIST:
        adequacy_df[f"nar_{nutrient_name}"] = np.minimum(1.0, adequacy_df[nutrient_name] / adequacy_df[f"req_{nutrient_name}"])
    adequacy_df["MAR"] = adequacy_df[[f"nar_{n}" for n in NUTRIENT_LIST]].mean(axis=1)
    adequacy_df.to_csv(os.path.join(PROC, "adequacy.csv"), index=False)
    
    print(adequacy_df[adequacy_df.Year == latest_year_num].sort_values("MAR")[["Area", "MAR"] + [f"nar_{n}" for n in NUTRIENT_LIST]].head(15).round(3).to_string(index=False))


if __name__ == "__main__":
    main()
