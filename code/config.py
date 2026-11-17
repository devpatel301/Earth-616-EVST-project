import os

# ---------------------------------------------------------------------------
# Run selection (end evaluation)
# ---------------------------------------------------------------------------
# CNVI_RUN = "nine_crop" (default; the end-evaluation main run, 9 crops) or "four_crop" (the
# mid-evaluation crop set re-run with the presented literature-only method, kept for comparison).
# Each run writes to its own processed / figures / docs folders, so results never overwrite each
# other. The frozen mid-evaluation record (blended sensitivity) is in archive/mid_evaluation/.
RUN = os.environ.get("CNVI_RUN", "nine_crop")
assert RUN in ("nine_crop", "four_crop"), RUN

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(ROOT_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(ROOT_DIR, "data", "processed", RUN)
WORK_DIR = os.path.join(ROOT_DIR, "data", "work")
FIGURES_DIR = os.path.join(ROOT_DIR, "figures", RUN)
DOCS_DIR = os.path.join(ROOT_DIR, "docs", RUN)

RAW = RAW_DIR
PROC = PROCESSED_DIR
WORK = WORK_DIR
FIG = FIGURES_DIR
TEX = DOCS_DIR
QCL_PKL = os.path.join(WORK_DIR, f"qcl_{RUN}.pkl")

for directory_path in (PROCESSED_DIR, WORK_DIR, FIGURES_DIR, os.path.join(DOCS_DIR, "generated")):
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

ALL_CROPS = {
    "rice": {
        "heat_metric": 'T_crit 35 C = anthesis temperature (Yoshida 1981 Table 2.4; FAO-66 p.106); slope 0.07/C = spikelet fertility loss per C above 29.6 C, tissue temperature, IR64 growth-chamber study (Jagadish et al. 2007), applied above 35 C on T_eff',
        "proxy_notes": "K_y = maize value 1.25 (FAO gives no rice K_y; rice is FAO 'high' drought-sensitivity class vs maize 'medium-high'); heat slope from one chamber experiment; main season only (Rice.2 calendar unused)",
        "expected_bias": 'heat exposure ~0 with monthly data (hot days hidden) -> rice vulnerability understated; K_y proxy is a lower bound',
        "sens_range_note": 'K_y 1.0 and 1.5; T_crit -2..+2 C',
        "oil_note": 'Rice and products + Rice (Milled Equivalent); rice bran oil is a separate FBS item (not counted)',
        "group": "cereal",
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
        "heat_metric": 'Deryng et al. 2014 Table A.1 spring-wheat T_crit/T_lim on T_eff = (T_mean+T_max)/2 (PEGASUS damage function); also applied to winter wheat',
        "proxy_notes": 'spring-wheat heat parameters applied to winter wheat; K_y = mean of spring 1.15 and winter 1.05',
        "expected_bias": '',
        "sens_range_note": 'T_crit -2..+2 C',
        "oil_note": 'Wheat and products',
        "group": "cereal",
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
        "heat_metric": 'Deryng et al. 2014 Table A.1 maize T_crit/T_lim on T_eff',
        "proxy_notes": '',
        "expected_bias": '',
        "sens_range_note": 'T_crit -2..+2 C',
        "oil_note": 'Maize and products; maize germ oil separate (not counted); ~60 % of world maize is feed',
        "group": "cereal",
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
        "heat_metric": 'Deryng et al. 2014 Table A.1 soybean T_crit/T_lim on T_eff',
        "proxy_notes": '',
        "expected_bias": '',
        "sens_range_note": 'T_crit -2..+2 C',
        "oil_note": 'Soyabeans + Soyabean Oil (oil carries most of its fat contribution)',
        "group": "oilseed",
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
    # ---- end-evaluation crops (parameters: docs/literature_verification_new_crops.md;
    #      every proxy is listed in docs/input_register.csv with its sensitivity range) ----
    "chickpea": {
        "group": "pulse",
        "label": "Chickpea",
        "faostat_item": "Chick peas, dry",
        "spam": "CHIC",
        "sacks": ["Pulses"],                   # used only by the sensitivity calendar (see CLIMATE_CROPS)
        "calendar_rule": "cool_season",        # main calendar: wheat-season rule (03_build_grids.py)
        "fbs_items": [],                       # not separate in FBS (inside "Pulses, Other and products")
        "sua_items": ["Chick peas, dry"],      # food supply taken from FAOSTAT SUA instead
        "photo": "C3",
        "tcrit": 34.0,
        "tlim": 41.14285714285714,
        "heat_slope": 0.14,
        "heat_source": 'Bhandari et al. 2020 (J. Agron. Crop Sci., Table 3): growth-chamber seed yield vs day/night regime 30/20->42/32 C (flowering to maturity), 3 Indian genotypes; DERIVED T_eff fit (docs/literature_verification_new_crops.md s2c)',
        "heat_metric": '12 h/12 h step chambers converted to T_eff = (mean+max)/2; outcome seed yield per plant (pots)',
        "ky": 0.88,
        "ky_source": 'Tari & Bahceci 2022 (Konya field trial: 0.85 early, 0.91 late sowing); not in FAO-33/66',
        "kc": (0.4, 1.0, 0.35),
        "kc_source": "FAO-56 Table 12 'Chick pea' (Kc ini = legume group value)",
        "stages": (25, 35, 70, 40),
        "proxy_notes": "calendar: cool-season wheat-based rule (no Sacks chickpea calendar); stage days: lentil 'Arid Region' row (no FAO-56 chickpea row); chamber/pot heat response; K_y from one Turkish site",
        "expected_bias": 'chamber thresholds sit below model-calibrated values -> heat sensitivity overstated relative to wheat/maize/soybean; monthly data understate exposure',
        "sens_range_note": 'T_crit +3 C (all new legumes); s_T x0.7; K_y 0.67-1.15; calendar = plain Sacks Pulses; T_crit -2..+2 C',
        "oil_note": "no oil; food supply from FAOSTAT SUA 'Chick peas, dry'",
        "missing_inputs": 'no FBS item (SUA used); no old-methodology FBS series',
    },
    "lentil": {
        "group": "pulse",
        "label": "Lentil",
        "faostat_item": "Lentils, dry",
        "spam": "LENT",
        "sacks": ["Pulses"],
        "calendar_rule": "cool_season",
        "fbs_items": [],
        "sua_items": ["Lentils, dry"],
        "photo": "C3",
        "tcrit": 31.9,
        "tlim": 37.78235294117647,
        "heat_slope": 0.17,
        "heat_source": 'Bhandari et al. 2020 (J. Agron. Crop Sci.): growth-chamber seed yield vs day/night regime (4 points, 2 Indian genotypes); DERIVED T_eff fit; field cross-check 32/20 C (docs/literature_verification_new_crops.md s2d)',
        "heat_metric": '12 h/12 h step chambers converted to T_eff; outcome seed yield per plant (pots)',
        "ky": 1.0,
        "ky_source": 'PROXY 1.0: field best-treatment 0.87 (Nandi et al. 2021, abstract) and ~1 on average (paraphrase); not in FAO',
        "kc": (0.4, 1.1, 0.3),
        "kc_source": "FAO-56 Table 12 'Lentil' (Kc ini = legume group value)",
        "stages": (25, 35, 70, 40),
        "proxy_notes": 'calendar: cool-season wheat-based rule; chamber/pot heat response (4 points); K_y proxy',
        "expected_bias": 'heat sensitivity likely overstated (chamber, few genotypes); K_y uncertain',
        "sens_range_note": 'T_crit +3 C (all new legumes); s_T x0.7; K_y 0.87-1.15; calendar = plain Sacks Pulses',
        "oil_note": "no oil; food supply from FAOSTAT SUA 'Lentils, dry'",
        "missing_inputs": 'no FBS item (SUA used); no old-methodology FBS series',
    },
    "bean": {
        "group": "pulse",
        "label": "Common bean",
        "faostat_item": "Beans, dry",
        "spam": "BEAN",
        "sacks": ["Pulses"],
        "fbs_items": ["Beans"],
        "photo": "C3",
        "tcrit": 25.5,
        "tlim": 34.5,
        "heat_slope": 0.1111111111111111,
        "heat_source": 'Prasad et al. 2002 Glob. Change Biol. (sunlit chambers, 28/18 optimum -> zero seed yield at 37/27 C); DERIVED to T_eff 25.5/34.5 (docs/literature_verification_new_crops.md s2a; abstract + Boote 2005/Hatfield 2011 read)',
        "heat_metric": 'season-long day max/night min regimes (10 C diurnal range) converted to T_eff; outcome seed yield, linear decline to zero',
        "ky": 1.15,
        "ky_source": 'FAO-33 via FAO-66 Table 1 (Beans) and FAO-56 Rev.1 Table 8.7',
        "kc": (0.4, 1.15, 0.35),
        "kc_source": "FAO-56 Table 12 'Beans, dry and Pulses'",
        "stages": (15, 25, 35, 20),
        "proxy_notes": "Sacks generic 'Pulses' calendar (86 % gap-filled); one Andean kidney-bean cultivar; FAOSTAT 'Beans, dry' may include Vigna spp. in some countries",
        "expected_bias": 'heat sensitivity overstated for heat-tolerant Mesoamerican beans; chamber vs field',
        "sens_range_note": 'T_crit +2 C (bean) and +3 C (all new legumes); s_T x0.7; K_y 0.6-1.4 (IAEA field values)',
        "oil_note": "no oil; FBS 'Beans'",
    },
    "groundnut": {
        "group": "oilseed",
        "label": "Groundnut",
        "faostat_item": "Groundnuts, excluding shelled",
        "spam": "GROU",
        "sacks": ["Groundnuts"],
        "fbs_items": ["Groundnuts", "Groundnut Oil"],
        "photo": "C3",
        "tcrit": 31.8,
        "tlim": 42.32631578947368,
        "heat_slope": 0.095,
        "heat_source": 'Prasad et al. 2003 Glob. Change Biol. (sunlit chambers 32/22 -> 44/34 C, seed yield); DERIVED T_eff fit (docs/literature_verification_new_crops.md s2b)',
        "heat_metric": 'season-long day max/night min regimes converted to T_eff; outcome seed yield',
        "ky": 0.7,
        "ky_source": 'FAO-33 via FAO-66 Table 1 (Groundnuts) and FAO-56 Rev.1 Table 8.7',
        "kc": (0.4, 1.15, 0.6),
        "kc_source": "FAO-56 Table 12 'Groundnut (Peanut)'",
        "stages": (25, 35, 45, 25),
        "proxy_notes": 'one cultivar (Georgia Green); chamber vs field',
        "expected_bias": 'heat sensitivity possibly overstated (chamber)',
        "sens_range_note": 'T_crit +3 C (all new legumes); s_T x0.7 (alt. slope 0.074)',
        "oil_note": 'Groundnuts + Groundnut Oil (oil carries most fat)',
    },
    "rapeseed": {
        "group": "oilseed",
        # Definition used everywhere: rapeseed incl. Indian rapeseed-mustard. FAOSTAT QCL item "Rape or
        # colza seed" (India reports rapeseed-mustard here; the separate "Mustard seed" item is ~1 % of the
        # combined total and is excluded); SPAM RAPE; Sacks Rapeseed.Winter (the only rapeseed calendar);
        # FBS "Rape and Mustardseed" + "Rape and Mustard Oil" (FBS cannot separate mustard).
        "label": "Rapeseed-mustard",
        "faostat_item": "Rape or colza seed",
        "spam": "RAPE",
        "sacks": ["Rapeseed.Winter"],
        "calendar_rule": "cool_season",
        "sacks_observed_first": ["Rapeseed.Winter"],
        "fbs_items": ["Rape and Mustardseed", "Rape and Mustard Oil"],
        "photo": "C3",
        "tcrit": 26.5,
        "tlim": 36.5,
        "heat_slope": 0.1,
        "heat_source": "T_crit: canola yield loss with daily T_max > 29.5 C during flowering (Morrison & Stewart 2002, field, Ottawa) converted to T_eff ~26.5 (PROXY); slope PROXY = wheat's Deryng 10 C span (no published canola slope found)",
        "heat_metric": 'field threshold on daily T_max (accumulated during flowering), converted to T_eff with an assumed 10-14 C diurnal range',
        "ky": 0.9,
        "ky_source": 'FAO-56 Rev.1 (2025) Table 8.7 Rapeseed; field cross-check 0.87 (Istanbulluoglu et al. 2010, abstract)',
        "kc": (0.35, 1.15, 0.35),
        "kc_source": "FAO-56 Table 12 'Rapeseed, Canola' (mid 1.0-1.15; 1.15 for consistency with other crops)",
        "stages": (330, 310, 450, 595),
        "proxy_notes": 'heat slope borrowed from wheat; B. napus parameters applied to B. juncea (Indian mustard); stage proportions from FAO-56 Rev.1 canola GDD shares; calendar rule (spring sowing in cold-winter cells)',
        "expected_bias": 'slope direction unknown; mustard heat loss overstated; monthly data understate daily T_max exceedance',
        "sens_range_note": 's_T 0.07-0.18; K_y 0.85-0.95; calendar = plain Sacks Rapeseed.Winter',
        "oil_note": 'Rape and Mustardseed + Rape and Mustard Oil (oil carries most fat; seed mostly crushed)',
    },
}

FOUR_CROPS = ["rice", "wheat", "maize", "soybean"]
CROP_ORDER = ["wheat", "rice", "maize", "chickpea", "lentil", "bean", "soybean", "groundnut", "rapeseed"]
CROP_GROUPS = {"cereal": ["wheat", "rice", "maize"], "pulse": ["chickpea", "lentil", "bean"],
               "oilseed": ["soybean", "groundnut", "rapeseed"]}
_run_crops = FOUR_CROPS if RUN == "four_crop" else [c for c in ALL_CROPS if c in CROP_ORDER]
CROPS = {k: ALL_CROPS[k] for k in _run_crops}

# Climate-only pseudo-crops: the same crop under its plain Sacks calendar (no cool-season rule).
# Processed through grids -> hazards -> country series only, for the calendar robustness test.
ALT_CALENDAR_CROPS = {f"{k}__altcal": {**ALL_CROPS[k], "parent": k, "calendar_rule": None,
                                       "label": ALL_CROPS[k]["label"] + " (plain Sacks calendar)"}
                      for k in ("chickpea", "lentil", "rapeseed")}
CLIMATE_CROPS = dict(CROPS) if RUN == "four_crop" else {**CROPS, **ALT_CALENDAR_CROPS}
CROP_PARAMS = {**ALL_CROPS, **ALT_CALENDAR_CROPS}

# Parameter ranges for the new crops' proxies (robustness rows in 08_index.py; docs/literature_verification_new_crops.md s5)
_LEG = ("chickpea", "lentil", "bean", "groundnut")
PARAM_RANGES = {
    "new legumes: heat slope x0.7 (chamber -> field)": {c: {"s_lit_heat": 0.7 * ALL_CROPS[c]["heat_slope"]} for c in _LEG},
    "rapeseed heat slope 0.07 (proxy low)": {"rapeseed": {"s_lit_heat": 0.07}},
    "rapeseed heat slope 0.18 (proxy high)": {"rapeseed": {"s_lit_heat": 0.18}},
    "new crops K_y low (chickpea 0.67, lentil 0.87, bean 0.6, rapeseed 0.85)": {
        "chickpea": {"s_lit_water": 0.67}, "lentil": {"s_lit_water": 0.87}, "bean": {"s_lit_water": 0.6}, "rapeseed": {"s_lit_water": 0.85}},
    "new crops K_y high (chickpea 1.15, lentil 1.15, bean 1.4, rapeseed 0.95)": {
        "chickpea": {"s_lit_water": 1.15}, "lentil": {"s_lit_water": 1.15}, "bean": {"s_lit_water": 1.4}, "rapeseed": {"s_lit_water": 0.95}},
}
CROP_LIST = list(CROPS.keys())
MAIN_CROPS = CROP_LIST
DRY_PERCENTILE_THRESHOLD = 20
DRY_PCTL = DRY_PERCENTILE_THRESHOLD


def season_kc(crop_name):
    initial_kc, mid_kc, end_kc = CROP_PARAMS[crop_name]["kc"]
    stage_initial, stage_dev, stage_mid, stage_late = CROP_PARAMS[crop_name]["stages"]
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
# Sensitivity variant (end evaluation, decision E13): WHO/FAO 2004 RNIs at MODERATE bioavailability --
# zinc moderate class (men 7.0, women 4.9 mg/d; Table 12.4) and iron at 15 % bioavailability (men 9.1,
# women 19.6 mg/d; Table 13.5). RNIs are upper-percentile INDIVIDUAL requirements compared with a national
# MEAN supply, so both variants overstate shortfall; the moderate variant shows how much the claim depends on it.
ZINC_REQUIREMENT_MODERATE = (7.0 + 4.9) / 2.0
IRON_REQUIREMENT_15PCT = (9.1 + 19.6) / 2.0
ZN_REQ = ZINC_REQUIREMENT_MG_PER_DAY
FE_REQ = IRON_REQUIREMENT_MG_PER_DAY
