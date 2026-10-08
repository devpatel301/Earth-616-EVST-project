import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(ROOT_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(ROOT_DIR, "data", "processed")
WORK_DIR = os.path.join(ROOT_DIR, "data", "work")
FIGURES_DIR = os.path.join(ROOT_DIR, "figures")
LATEX_DIR = os.path.join(ROOT_DIR, "latex")

PROC = PROCESSED_DIR
WORK = WORK_DIR
FIG = FIGURES_DIR
TEX = LATEX_DIR

for directory_path in (PROCESSED_DIR, WORK_DIR, FIGURES_DIR, LATEX_DIR):
    os.makedirs(directory_path, exist_ok=True)

BASELINE_PERIOD = (1971, 2000)
RECENT_PERIOD = (2001, 2024)
ALL_YEARS_PERIOD = (1971, 2024)
FIT_PERIOD = BASELINE_PERIOD

BASE = BASELINE_PERIOD
RECENT = RECENT_PERIOD
ALL_YEARS = ALL_YEARS_PERIOD
FIT = FIT_PERIOD

GRID_COLUMNS, GRID_ROWS = 2160, 1080
GRID_RESOLUTION = 1.0 / 6.0
NX, NY = GRID_COLUMNS, GRID_ROWS
RES = GRID_RESOLUTION

MIN_PRODUCTION_SHARE_PERCENT = 0.5
FAO_AVERAGE_YEARS = 5
TOP_PRODUCERS_COUNT = 3

MIN_SHARE_PCT = MIN_PRODUCTION_SHARE_PERCENT
FAO_YEARS = FAO_AVERAGE_YEARS
TOP_N = TOP_PRODUCERS_COUNT

CORE_PANEL_COUNTRIES = ["United States of America", "Brazil", "India", "China, mainland"]
CORE = CORE_PANEL_COUNTRIES

MOUNTAIN_ELEVATION_METERS = 1000
MOUNTAIN_M = MOUNTAIN_ELEVATION_METERS

KOPPEN_GROUPS = {
    "A": range(1, 4),
    "B": range(4, 8),
    "C": range(8, 17),
    "D": range(17, 29),
    "E": range(29, 31)
}
KG_GROUPS = KOPPEN_GROUPS

CLIMATE_CLASS_ORDER = ["A", "B", "C", "D", "M"]
CLASS_ORDER = CLIMATE_CLASS_ORDER

CLIMATE_CLASS_NAMES = {
    "A": "Tropical",
    "B": "Arid / semi-arid",
    "C": "Temperate",
    "D": "Cold continental",
    "M": "Mountain (>=1000 m)"
}
CLASS_NAME = CLIMATE_CLASS_NAMES

CROPS = {
    "rice": {
        "label": "Rice",
        "faostat_item": "Rice",
        "spam": "RICE",
        "sacks": ["Rice"],
        "fbs_items": ["Rice and products", "Rice (Milled Equivalent)"],
        "photo": "C3",
        "tcrit": 35.0,
        "heat_slope": 0.07,
        "heat_source": "Yoshida 1981; Jagadish et al. 2007",
        "ky": 1.25,
        "ky_source": "FAO 66; Brouwer and Heibloem 1986",
        "kc": (1.05, 1.20, 0.75),
        "stages": (30, 30, 60, 30)
    },
    "wheat": {
        "label": "Wheat",
        "faostat_item": "Wheat",
        "spam": "WHEA",
        "sacks": ["Wheat.Winter", "Wheat"],
        "fbs_items": ["Wheat and products"],
        "photo": "C3",
        "tcrit": 25.0,
        "heat_slope": 1.0 / (35.0 - 25.0),
        "heat_source": "Deryng et al. 2014",
        "ky": 1.10,
        "ky_source": "FAO-66 (mean of spring 1.15, winter 1.05)",
        "kc": (0.40, 1.15, 0.33),
        "stages": (15, 25, 50, 30)
    },
    "maize": {
        "label": "Maize",
        "faostat_item": "Maize (corn)",
        "spam": "MAIZ",
        "sacks": ["Maize"],
        "fbs_items": ["Maize and products"],
        "photo": "C4",
        "tcrit": 32.0,
        "heat_slope": 1.0 / (45.0 - 32.0),
        "heat_source": "Deryng et al. 2014",
        "ky": 1.25,
        "ky_source": "FAO-66",
        "kc": (0.30, 1.20, 0.48),
        "stages": (20, 35, 40, 30)
    },
    "soybean": {
        "label": "Soybean",
        "faostat_item": "Soya beans",
        "spam": "SOYB",
        "sacks": ["Soybeans"],
        "fbs_items": ["Soyabeans", "Soyabean Oil"],
        "photo": "C3",
        "tcrit": 35.0,
        "heat_slope": 1.0 / (40.0 - 35.0),
        "heat_source": "Deryng et al. 2014",
        "ky": 0.85,
        "ky_source": "FAO-66",
        "kc": (0.40, 1.15, 0.50),
        "stages": (15, 15, 40, 15)
    },
}

CROP_LIST = list(CROPS.keys())
MAIN_CROPS = CROP_LIST
DRY_PERCENTILE_THRESHOLD = 20
DRY_PCTL = DRY_PERCENTILE_THRESHOLD


def season_kc(crop_name):
    initial_kc, mid_kc, end_kc = CROPS[crop_name]["kc"]
    stage_initial, stage_dev, stage_mid, stage_late = CROPS[crop_name]["stages"]
    total_stage_days = stage_initial + stage_dev + stage_mid + stage_late
    weighted_kc_sum = (
        stage_initial * initial_kc +
        stage_dev * (initial_kc + mid_kc) / 2.0 +
        stage_mid * mid_kc +
        stage_late * (mid_kc + end_kc) / 2.0
    )
    return weighted_kc_sum / total_stage_days


ZHAO_BENCHMARKS = {
    "maize": (-7.4, 4.5),
    "wheat": (-6.0, 2.9),
    "rice": (-3.2, 3.7),
    "soybean": (-3.1, None)
}
ZHAO = ZHAO_BENCHMARKS

RAY_BENCHMARKS = {"maize": 39, "rice": 32, "wheat": 35, "soybean": 35}
RAY = RAY_BENCHMARKS

MYERS_BENCHMARKS = {
    "wheat": {"zinc": (-9.3, True), "iron": (-5.1, True), "protein": (-6.3, True)},
    "rice": {"zinc": (-3.3, True), "iron": (-5.2, True), "protein": (-7.8, True)},
    "soybean": {"zinc": (-5.1, True), "iron": (-4.1, True), "protein": (0.5, False)},
    "maize": {"zinc": (-5.2, False), "iron": (-5.8, True), "protein": (-4.6, False)}
}
MYERS = MYERS_BENCHMARKS

DETRENDING_METHODS = ("linear", "quadratic", "first-difference")
METHODS = DETRENDING_METHODS
SIGNIFICANCE_ALPHA = 0.05
ALPHA = SIGNIFICANCE_ALPHA

YIELD_SHOCK_STANDARD_DEVIATIONS = 1.0
SHOCK_SD = YIELD_SHOCK_STANDARD_DEVIATIONS

ZINC_REQUIREMENT_MG_PER_DAY = (14.0 + 9.8) / 2.0
IRON_REQUIREMENT_MG_PER_DAY = (13.7 + 29.4) / 2.0
ZN_REQ = ZINC_REQUIREMENT_MG_PER_DAY
FE_REQ = IRON_REQUIREMENT_MG_PER_DAY
