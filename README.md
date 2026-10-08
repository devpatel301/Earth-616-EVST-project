# Climate Change and Nutritional Security: Which Crops Are Most Vulnerable?

A Climate-Nutrition Vulnerability Index (CNVI) evaluating rice, wheat, maize, and soybean across major global producing countries.

---

## File Directory & Description Table

### Code Scripts (`code/`)

| File | Description |
| :--- | :--- |
| `code/config.py` | Global project configuration, crop physiological constants (Tcrit, Tlim, Ky, Kc), and directory path definitions. |
| `code/01_download_data.py` | Multi-threaded downloader fetching all raw WorldClim, SPAM, Sacks, FAOSTAT, and USDA datasets. |
| `code/02b_climate_zones.py` | Computes 10-arcminute Köppen-Geiger climate zones from historical monthly weather grids. |
| `code/02c_check_koppen.py` | Evaluates calculated Köppen-Geiger climate zones against the published Beck et al. (2023) benchmark map. |
| `code/03_build_grids.py` | Standardizes harvested crop area and Sacks crop calendar data onto unified 10-arcminute grids with flowering weights. |
| `code/03_panels.py` | Selects representative country panels based on top global output and diverse agro-climatic zone representation. |
| `code/04_climate_exposure.py` | Extracts monthly timeseries and calculates growing-season climate exposure statistics for temperature and precipitation. |
| `code/04_hazards.py` | Computes non-linear climate hazards including Hargreaves reference evapotranspiration (ET0) and flowering heat stress. |
| `code/05_country_series.py` | Computes crop-area-weighted national climate hazard series and baseline-to-recent exposure shifts (SNR). |
| `code/06_sensitivity.py` | Fits country-specific and pooled panel yield regressions across detrending methods as an out-of-sample check. |
| `code/07_nutrition.py` | Calculates national nutrient availability (kcal, protein, fat, zinc, iron), crop Importance shares (I), and adequacy (MAR). |
| `code/07b_use_shares.py` | Computes domestic crop utilization shares (food, feed, processing, other uses) from FAO Food Balance Sheets. |
| `code/08_index.py` | Evaluates composite vulnerability indices across functional forms F1-F4, robustness tests, and Monte Carlo simulations. |
| `code/09_yield_diet.py` | Evaluates historical yield pass-through to food supply and models dietary nutrient loss under yield shock scenarios. |
| `code/10_validation.py` | Validates index behavior against independent benchmarks (Zhao et al. 2017, Ray et al. 2015, Myers et al. 2014, yield shocks). |
| `code/11_figures.py` | Generates all project figures in high-resolution PDF and PNG formats. |
| `code/12_export_tex.py` | Exports auto-generated LaTeX macros (numbers.tex) and all dynamic LaTeX tables to docs/generated/. |
| `code/13_lit_sensitivity.py` | Generates literature sensitivity parameter tables and comparison charts against Zhao et al. (2017). |
| `code/fbs_usda_map.csv` | Item-by-item mapping connecting FAOSTAT Food Balance Sheet commodities to USDA FoodData Central nutritional IDs. |
| `code/run_all.ps1` | Automated pipeline reproduction script for Windows PowerShell. |

### Processed Datasets (`data/processed/`)

| File | Description |
| :--- | :--- |
| `data/processed/adequacy.csv` | National Nutrient Adequacy Ratios (NAR) and Mean Adequacy Ratio (MAR) metrics per country and year. |
| `data/processed/composition_used.csv` | Matched USDA nutrient composition parameters per 100g for each FAO Food Balance Sheet commodity. |
| `data/processed/country_series.pkl` | Pickled dataframe of national area-weighted climate hazard timeseries (1971-2024). |
| `data/processed/country_shift.csv` | National climate signal-to-noise ratio (SNR) shifts and rainfed harvested area shares. |
| `data/processed/crop_contrib.csv` | Annual national food and nutrient supply contributions by crop. |
| `data/processed/crop_use_shares.csv` | Percentage breakdown of domestic crop supply allocated to food, animal feed, industrial processing, and other uses. |
| `data/processed/importance.csv` | Baseline dietary Importance shares (I) averaged across energy, protein, fat, zinc, and iron supplies. |
| `data/processed/index_components.csv` | Full dataset of crop-by-country index components (Exposure, Sensitivity, Importance, and F1-F4 vulnerability scores). |
| `data/processed/index_crop.csv` | Aggregate crop-level vulnerability index scores and rankings under equal and production weighting. |
| `data/processed/index_form_agreement.csv` | Pairwise Kendall's rank correlation (tau) matrix across candidate index formulas F1-F4. |
| `data/processed/index_montecarlo.csv` | Rank probability distributions from 2,000 Monte Carlo iterations with randomized sub-component weights. |
| `data/processed/index_robustness.csv` | Crop vulnerability rankings under 10 one-at-a-time sensitivity and robustness specifications. |
| `data/processed/koppen_check.csv` | Agreement statistics between calculated Köppen-Geiger zones and Beck et al. (2023) published maps. |
| `data/processed/koppen_check_countries.csv` | National-level Köppen climate zone classifications and cell agreement percentages. |
| `data/processed/nutrient_supply.pkl` | Pickled commodity-level food and nutrient supply timeseries from FAO Food Balance Sheets. |
| `data/processed/panels.csv` | Selected country panels with global production ranks, output shares, mean elevations, and climate zones. |
| `data/processed/sensitivity.csv` | Literature sensitivity parameters, empirical regression coefficients, and model R-squared values by country. |
| `data/processed/sensitivity_pooled.csv` | Pooled panel regression coefficients across detrending methods and calibration periods. |
| `data/processed/shared_panel.csv` | List of core panel countries producing all four evaluated crops (Brazil, China, India, Russia, USA). |
| `data/processed/val_myers.csv` | Dietary nutrient shares at risk evaluated against Myers et al. (2014) elevated CO2 nutrient reduction benchmarks. |
| `data/processed/val_ray.csv` | Climate-explained yield variability (R-squared) compared with Ray et al. (2015) global findings. |
| `data/processed/val_shocks.csv` | Historical out-of-sample yield shock anomaly occurrences and climate prediction skill scores (2001-2024). |
| `data/processed/val_shocks_test.csv` | Spearman rank correlation and permutation test significance metrics for yield shock validation. |
| `data/processed/val_zhao.csv` | Crop vulnerability rankings and Spearman correlation against Zhao et al. (2017) warming loss estimates. |
| `data/processed/yield_diet_historical.csv` | Empirical regression pass-through elasticities of dietary nutrient availability to crop yield anomalies. |
| `data/processed/yield_diet_scenarios.csv` | Simulated nutrient supply losses and MAR dietary adequacy changes under 10% crop yield reductions. |

### Documentation & LaTeX Source Documents (`docs/`)

| File | Description |
| :--- | :--- |
| `docs/slides.pdf` / `docs/slides.tex` | Final 24-slide presentation deck (Beamer) presenting the study motivation, methods, results, and conclusions. |
| `docs/report.pdf` / `docs/report.tex` | Complete academic project report documenting problem context, methodology, index calculations, and findings. |
| `docs/appendix.pdf` / `docs/appendix.tex` | Extended technical appendix containing full derivation details, complete data tables, and robustness checks. |
| `docs/common.tex` | Shared LaTeX styling, package inclusions, color definitions, crop macros, and path configurations. |
| `docs/refs.bib` | BibTeX bibliography containing complete references for all cited datasets and peer-reviewed literature. |
| `docs/DATA_SOURCES.md` | Catalog of all public data sources, download URLs, descriptions, citations, and licenses. |

### Auto-Generated LaTeX Tables & Macros (`docs/generated/`)

| File | Description |
| :--- | :--- |
| `docs/generated/numbers.tex` | Auto-generated LaTeX macros containing exact project figures, values, and ranking statistics. |
| `docs/generated/tab_components.tex` | LaTeX table displaying detailed exposure, sensitivity, importance, and F4 vulnerability values by country. |
| `docs/generated/tab_country_crop_index.tex` | LaTeX table displaying the country-by-crop F4 vulnerability matrix. |
| `docs/generated/tab_crop_index.tex` | LaTeX table displaying aggregate crop vulnerability scores and ranks across formulas F1-F4. |
| `docs/generated/tab_lit_sens.tex` | LaTeX table of literature-derived heat sensitivity thresholds (Tcrit, Tlim) and normalized scores (S_T). |
| `docs/generated/tab_lit_sens_temp.tex` | LaTeX table of temperature sensitivity thresholds and heat loss parameters. |
| `docs/generated/tab_lit_sens_water.tex` | LaTeX table of precipitation sensitivity factors (Ky) and normalized water scores (S_P). |
| `docs/generated/tab_panels.tex` | LaTeX table of representative panel countries, world ranks, global shares, and Köppen climate classes. |
| `docs/generated/tab_params.tex` | LaTeX table of agronomic parameters (Tcrit, Tlim, s_T, Ky, Kc) for all four crops. |
| `docs/generated/tab_passthrough.tex` | LaTeX table of empirical yield-to-diet pass-through regression coefficients across FBS eras. |
| `docs/generated/tab_robust.tex` | LaTeX table of crop vulnerability rankings across 10 one-at-a-time robustness tests. |
| `docs/generated/tab_scenario.tex` | LaTeX table of simulated nutrient availability and MAR adequacy changes under 10% yield shocks. |
| `docs/generated/tab_sensitivity.tex` | LaTeX table of country-level empirical yield regression coefficients and model fit (R-squared). |

### Figures (`figures/`)

| File | Description |
| :--- | :--- |
| `figures/F01_panels_koppen.png` | Global map displaying study panel countries overlaid on Köppen climate classification zones. |
| `figures/F02a_heat_shift_map.png` | Global map of observed shifts in flowering-window heat stress (2001-2024 vs 1971-2000). |
| `figures/F02b_water_shift_map.png` | Global map of observed shifts in growing-season moisture deficit. |
| `figures/F02c_heat_stress_map.png` | Global map of absolute flowering-season heat stress level where effective temperature exceeds Tcrit. |
| `figures/F03_water_hazard_map.png` | Global map of rainfed crop water deficit levels based on Hargreaves ET0 demand. |
| `figures/F04_exposure_by_country.pdf` | Bar chart of national temperature (E_T) and precipitation (E_P) exposure scores by country. |
| `figures/F05_sensitivity_coefficients.pdf` | Empirical temperature and moisture sensitivity coefficients compared across three detrending methods. |
| `figures/F05c_sensitivity_by_country.pdf` | Country-specific empirical yield sensitivity regression estimates. |
| `figures/F05l_literature_sensitivity.pdf` | Bar chart of physiological literature sensitivity parameters and normalized scores (S_T, S_P). |
| `figures/F05s_sensitivity_pooled.pdf` | Pooled panel regression coefficients for crop heat and moisture sensitivity. |
| `figures/F05v_data_check.pdf` | Validation plot comparing observed empirical yield sensitivity against Zhao et al. (2017) meta-analysis estimates. |
| `figures/F06_importance_heatmap.pdf` | Heatmap matrix of national dietary importance shares across calories, protein, fat, zinc, and iron. |
| `figures/F06s_importance_summary.pdf` | Summary bar chart of nutritional importance contributions by crop. |
| `figures/F07_adequacy_panel.pdf` | Baseline national nutrient adequacy ratios (NAR) and Mean Adequacy Ratio (MAR) by country. |
| `figures/F08_index_forms.pdf` | Comparison of crop vulnerability scores across candidate functional formulations F1-F4. |
| `figures/F08s_index_F4.pdf` | Headline vulnerability index chart under the chosen hazard-paired formulation (F4). |
| `figures/F09_country_index.pdf` | Country-level breakdown of F4 vulnerability index scores. |
| `figures/F10_montecarlo_ranks.pdf` | Cumulative rank probability distributions across 2,000 Monte Carlo sub-weight assignments. |
| `figures/F11_zhao_validation.pdf` | Scatter plot evaluating index vulnerability against Zhao et al. (2017) global warming yield loss benchmarks. |
| `figures/F12_shock_validation.pdf` | Evaluation plot of climate vulnerability against historical out-of-sample yield shock frequencies. |
| `figures/F13_yield_supply_passthrough.pdf` | Regression timeseries of historical crop yield anomalies vs national food-energy supply fluctuations. |
| `figures/F13c_passthrough_clear.pdf` | Summary chart of statistically significant yield-to-diet pass-through elasticities. |
| `figures/F13s_passthrough_by_crop.pdf` | Pass-through elasticity distributions grouped by crop. |
| `figures/F14_scenario_shock.pdf` | Simulated nutrient supply reductions and MAR loss across countries under yield shocks. |
| `figures/F14c_scenario_simple.pdf` | Summary of MAR adequacy score reductions following a 10% crop yield reduction. |
| `figures/F14s_scenario_top.pdf` | Slide comparison chart of nutritional adequacy impacts under simulated yield shocks. |
| `figures/F15_example_series.pdf` | Representative historical timeseries illustrating climate hazard, yield anomaly, and dietary availability dynamics. |
| `figures/F16_myers_check.pdf` | Comparison of nutritional importance against elevated CO2 nutrient loss from Myers et al. (2014). |
| `figures/F17_country_crop_matrix.pdf` | Heatmap matrix displaying within-country crop vulnerability rankings across shared panel countries. |

---

## Compilation & Reproduction Commands

### Recomputing Data & Generating Figures
```bash
python3 code/02b_climate_zones.py
python3 code/03_panels.py
python3 code/05_country_series.py
python3 code/06_sensitivity.py
python3 code/07_nutrition.py
python3 code/07b_use_shares.py
python3 code/08_index.py
python3 code/09_yield_diet.py
python3 code/10_validation.py
python3 code/11_figures.py
python3 code/12_export_tex.py
python3 code/13_lit_sensitivity.py
```

### Compiling LaTeX Documents
From the repository root directory:
```bash
pdflatex -interaction=nonstopmode -output-directory=docs docs/slides.tex
pdflatex -interaction=nonstopmode -output-directory=docs docs/report.tex
bibtex docs/report
pdflatex -interaction=nonstopmode -output-directory=docs docs/report.tex
pdflatex -interaction=nonstopmode -output-directory=docs docs/report.tex
pdflatex -interaction=nonstopmode -output-directory=docs docs/appendix.tex
bibtex docs/appendix
pdflatex -interaction=nonstopmode -output-directory=docs docs/appendix.tex
pdflatex -interaction=nonstopmode -output-directory=docs docs/appendix.tex
```
Or from within the `docs/` directory:
```bash
cd docs
pdflatex -interaction=nonstopmode slides.tex
pdflatex -interaction=nonstopmode report.tex && bibtex report && pdflatex -interaction=nonstopmode report.tex && pdflatex -interaction=nonstopmode report.tex
pdflatex -interaction=nonstopmode appendix.tex && bibtex appendix && pdflatex -interaction=nonstopmode appendix.tex && pdflatex -interaction=nonstopmode appendix.tex
```
