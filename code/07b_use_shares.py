import io
import os
import zipfile

import pandas as pd

from config import CROPS, PROC, RAW

PRIMARY_CROP_ITEMS = {crop_info["fbs_items"][0]: crop_name for crop_name, crop_info in CROPS.items()}
ELEMENT_NAMES = {
    "Food": "food",
    "Feed": "feed",
    "Processing": "processing",
    "Other uses (non-food)": "other_nonfood",
    "Domestic supply quantity": "domestic"
}


def main():
    fbs_zip_path = os.path.join(RAW, "faostat", "FoodBalanceSheets_E_All_Data_(Normalized).zip")
    with zipfile.ZipFile(fbs_zip_path) as zip_ref:
        csv_filename = [entry for entry in zip_ref.namelist() if entry.endswith("(Normalized).csv")][0]
        raw_fbs_df = pd.read_csv(
            io.BytesIO(zip_ref.read(csv_filename)),
            encoding="latin-1",
            low_memory=False,
            usecols=["Area", "Item", "Element", "Year", "Value"]
        )
        
    latest_year = int(raw_fbs_df.Year.max())
    recent_fbs_df = raw_fbs_df[
        raw_fbs_df.Year.between(latest_year - 2, latest_year)
        & raw_fbs_df.Item.isin(PRIMARY_CROP_ITEMS)
        & raw_fbs_df.Element.isin(ELEMENT_NAMES)
    ]
    
    pivoted_uses = recent_fbs_df.pivot_table(
        index=["Area", "Item"],
        columns="Element",
        values="Value",
        aggfunc="mean"
    ).rename(columns=ELEMENT_NAMES)
    
    for use_category in ("food", "feed", "processing", "other_nonfood"):
        pivoted_uses[use_category] = 100.0 * pivoted_uses[use_category].fillna(0.0) / pivoted_uses["domestic"]
        
    pivoted_uses = pivoted_uses.reset_index()
    pivoted_uses["crop"] = pivoted_uses.Item.map(PRIMARY_CROP_ITEMS)
    pivoted_uses.drop(columns=["domestic"]).to_csv(os.path.join(PROC, "crop_use_shares.csv"), index=False)
    
    sample_countries = ["World", "India", "United States of America", "China, mainland", "Brazil", "South Africa"]
    print(pivoted_uses[pivoted_uses.Area.isin(sample_countries)][
        ["Area", "crop", "food", "feed", "processing", "other_nonfood"]
    ].round(0).to_string(index=False))


if __name__ == "__main__":
    main()
