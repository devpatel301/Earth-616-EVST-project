# Climate Change and Nutritional Security: Which Crops Are Most Vulnerable?

Earth 616 (EVS) project — Arpit Mahtele, Dev Patel, Navey Puri, Shreyash Lohare.

A Climate–Nutrition Vulnerability Index (CNVI) per crop and country,
`F4 = ½ (E_heat·S_heat + E_water·S_water) · Ĩ`, combining observed climatic **exposure** (flowering-window
heat above a crop threshold; rainfed water deficit), literature **sensitivity** (heat yield-loss slope; FAO
K_y) and nutritional **importance** (share of national kcal, protein, fat, zinc and iron supply).

**End evaluation** (this version): nine crops in three groups — cereals (wheat, rice, maize), pulses
(chickpea, lentil, common bean), oilseeds (soybean, groundnut, rapeseed-mustard) — for the present
(2001–2024), a historical baseline (1971–2000) and the future (2041–2060, WorldClim CMIP6 MRI-ESM2-0,
SSP2-4.5), plus the nutrient consequences of yield losses. The mid-evaluation (four crops) is frozen in
[archive/mid_evaluation/](archive/mid_evaluation/).

## Where things are

| Path | Contents |
|---|---|
| [docs/final_report.pdf](docs/final_report.pdf) | **Comprehensive final report** (self-contained): method with numbered equations, worked examples, all results, India/Hyderabad, robustness and validation, limitations, reproduction and audit; appendices with the parameter and source ledger, full tables, record of corrections and audit evidence. Sources: `docs/final_report.tex` + `docs/report/` |
| [docs/final_slides.pdf](docs/final_slides.pdf) | Final slide deck |
| [docs/final_appendix.pdf](docs/final_appendix.pdf) | Short stand-alone appendix (equations, full tables); its content is also in the report |
| [docs/END_EVAL_RESULTS_REGISTER.md](docs/END_EVAL_RESULTS_REGISTER.md) | Commitments C1–C10 → evidence, results and limitations register |
| `docs/co2_nutrient_effects.csv/.md`, `co2_effects_used.csv`, `co2_reference_levels.csv` | CO2 nutrient-quality evidence: every candidate effect with read level and locator; our selection with reasons; reference CO2 levels |
| `docs/future_literature_sources.csv/.md`, `future_literature_assessment.csv` | 39 future-impact study rows (24 publications) covering all nine crops, with quotes, read level and our verdicts |
| `docs/parameter_evidence_register.csv`, `parameter_evidence_audit.md` | Evidence register of every crop parameter used (status, applicability, replacement, treatment) and its audit |
| [docs/DECISION_REGISTER_END_EVAL.md](docs/DECISION_REGISTER_END_EVAL.md) | Every end-evaluation method/scope decision (E1–E24) with its reason and test |
| [docs/input_register.csv](docs/input_register.csv) / [.md](docs/input_register.md) | Nine-crop input register (items, panels, maps, calendars, parameters, mappings, proxies, sign-off) |
| [docs/literature_verification_new_crops.md](docs/literature_verification_new_crops.md) | Source checks (quotes, pages, read level) for the five new crops' parameters; section 8 = follow-up checks of the 18 Nov 2026 audit |
| [docs/literature_comparison_sources.md](docs/literature_comparison_sources.md) | Published findings used for the comparison with our results |
| [docs/DATA_MANIFEST.csv](docs/DATA_MANIFEST.csv) | Every raw input: path, size, date, SHA-256 |
| [docs/DATA_SOURCES.md](docs/DATA_SOURCES.md) | Data source register (mid-evaluation datasets) |
| `data/processed/nine_crop/` | End-evaluation result tables (machine readable) |
| `data/processed/four_crop/` | Mid-evaluation crops re-run with the presented (literature-only) method |
| `figures/nine_crop/G*.pdf` | End-evaluation figures; `figures/four_crop/` the regenerated mid-evaluation figure set |
| `docs/nine_crop/generated/` | LaTeX tables and macros written by the code (no hand-typed result values) |

## Reproducing

Requirements: Windows or Linux, Python **3.13** (not 3.14: rasterio builds from source and hangs),
packages in [requirements.txt](requirements.txt), and [Tectonic](https://tectonic-typesetting.github.io)
for the PDFs.

```powershell
py -3.13 -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
cd code
python 00_data_manifest.py --check          # which raw inputs are missing or differ
powershell -ExecutionPolicy Bypass -File .\run_all.ps1          # everything from raw inputs (~21 min on the audit machine)
powershell -ExecutionPolicy Bypass -File .\run_all.ps1 -SkipClimate   # reuse data\work climate files
```

`run_all.ps1` runs, in order: downloads (skips files present) → grids → monthly climate series → hazards
→ for each of `four_crop` and `nine_crop`: panels, country series, empirical sensitivity checks, nutrition,
index + robustness, yield→diet, validation → future climate → future index → future yield/nutrition →
run comparisons → figures → India/Hyderabad → literature comparison → consistency checks (`24`) → parameter refits
(`25`) → LaTeX tables (`19`, `26`) → PDFs. A failing script, check or compile stops the run. The run is selected by the environment variable
`CNVI_RUN` (`nine_crop` default, or `four_crop`).

**Raw data** (≈3.4 GB, 75 files, not in git; listed with checksums in `docs/DATA_MANIFEST.csv`): WorldClim 2.1 monthly
CRU-TS 4.09 (prec, tmax, tmin 1970–2024), WorldClim 1970–2000 normals, WorldClim CMIP6 MRI-ESM2-0 SSP2-4.5
2041–2060, SPAM 2010, Sacks et al. 2010 calendars, FAOSTAT (production, food balances old and new, food
security indicators, Supply Utilization Accounts), USDA FoodData Central SR Legacy, Natural Earth admin-0 and admin-1, the official India/Telangana survey files
(`data/raw/india/`, sources in `docs/india_hyderabad_sources.md`), and
(optional) Beck et al. Köppen map. `01_download_data.py` fetches everything except the Köppen GeoTIFF.
FAOSTAT bulk files change over time: copy the original zips (dates in the manifest) to reproduce the
numbers exactly. **Intermediate data** (`data/work`, ≈10 GB) are regenerated by the pipeline.

## Code

| Script | Step |
|---|---|
| `config.py` | Run selection, periods, crop definitions and literature parameters (sources inline), panels rule, requirements, parameter ranges |
| `00_data_manifest.py` | Raw-data inventory and check |
| `01_download_data.py` | Downloads (parallel byte ranges; slow servers) |
| `02b_climate_zones.py`, `02c_check_koppen.py` | Köppen groups from WorldClim; check against Beck et al. |
| `03_build_grids.py` | SPAM areas and Sacks calendars on the 10′ grid; cool-season calendar rule |
| `03_panels.py` | Country panels (core + Europe/Africa + world top-3) |
| `04_climate_exposure.py`, `04_hazards.py` | Monthly series; Hargreaves ET0, flowering T_eff, heat exceedance (and at T_crit −2…+3 °C) |
| `05_country_series.py` | Area-weighted national hazard series |
| `06_sensitivity.py` | Literature sensitivity; empirical yield regressions (checks only) |
| `07_nutrition.py`, `07b_use_shares.py` | Nutrient supply (FBS; SUA for chickpea/lentil), importance, adequacy, use shares |
| `08_index.py` | Index F1–F4, crop and group scores, normalisation reference, robustness tests, Monte Carlo |
| `09_yield_diet.py` | Pass-through regressions; −10 % shock and S1/S2 scenarios |
| `10_validation.py` | Zhao 2017, yield-shock, Ray 2015, Myers 2014 checks |
| `11_figures.py`, `12_export_tex.py`, `13_lit_sensitivity.py` | Mid-evaluation figure/table set (run for `four_crop`); sensitivity table/figure |
| `14_future_climate.py` | Future hazards by change factors (+ climatology check) |
| `15_future_index.py` | Historical vs future scores with a fixed reference |
| `16_future_yield_nutrition.py` | Conditional future yield change and nutrient consequences |
| `17_compare_runs.py` | Mid-evaluation vs four-crop vs nine-crop comparisons; worked example |
| `18_endeval_figures.py`, `19_endeval_tex.py` | End-evaluation figures and LaTeX tables/macros |
| `20_input_register.py` | Nine-crop input register |
| `21_india_hyderabad.py`, `hyderabad_diet.py` | India profile; food-supply diversity; Telangana crop exposure; Hyderabad climate; Hyderabad/Telangana diet and nutrient sources from official surveys |
| `22_literature_comparison.py` | Our results next to published findings, verdicts computed |
| `23_sources_doc.py` | Writes `docs/india_hyderabad_sources.md` from the indicators table |
| `24_checks.py` | 29 consistency checks on the saved results (arithmetic, fixed reference, no double counting, bounds); stops the run on a failure |
| `25_parameter_fits.py` | Refits the derived new-crop heat thresholds/slopes from the published data and checks them against `config.py` |
| `26_report_tables.py` | Report tables and macros: data sources, parameter ledger, crop mapping, worked examples, checks, audit, India shares |
| `27_compare_rerun.py` | Audit tool (not in `run_all`): compares a fresh run file by file with a preserved copy of the previous outputs |
| `ext_common.py` | Shared accounting of the research extensions (item-level supply, SUA removal from the parent FBS item, SSR*, diversity measures) |
| `28_co2_quality.py` | Elevated-CO2 nutrient-concentration stress test: quantity, quality and combined (multiplicative), envelopes, coverage |
| `29_diversity_losses.py` | National food-source diversity (Shannon, effective number, top share) and adequacy after crop losses, scenarios A-D |
| `30_future_literature.py` | Future-impact literature coverage for all nine crops; our side computed from the saved results |
| `31_parameter_evidence.py` | Evidence-screened view of the index (V0, V1, V2) from the parameter evidence register |
| `32_extension_checks.py` | 37 synthetic and real checks of the extensions; stops the run on a failure |
| `33_extension_tables.py` | Tables, macros and figures of the extensions for the report |
| `run_extensions.ps1` | Reruns only 28-33 from the verified results (seconds, no climate processing) |

## LaTeX

The three end-evaluation documents (`docs/final_report.tex`, `final_slides.tex`, `final_appendix.tex`) are ASCII-only
and use standard packages (`iftex` selects `inputenc`/`fontenc` under pdfLaTeX); they are compiled here with Tectonic.
With pdfLaTeX run `pdflatex` / `bibtex` / `pdflatex` twice inside `docs/`. This pdfLaTeX route has **not** been run on
this machine (no pdfLaTeX installed); only the Tectonic compile is tested.

## Research extensions (19 Nov 2026)

Four extensions were added after the 18 Nov audit; they only read the verified baseline results and change none of
them. Checked with `git diff`: of the tracked files in `data/processed/`, only `literature_comparison.csv` changed (the
text of the Ray et al. and Myers rows); every other baseline result is byte-identical, and the extensions add 17 new files.
- **Parameter evidence** (report section "how well are the crop parameters supported"): 97-row register; the rice and
  rapeseed heat slopes are unsupported, so their F4 is unavailable in the evidence-screened view; wheat stays first
  among the seven crops with supported parameters. Existing robustness ranges are labelled exploratory perturbations.
- **Future literature**: all nine crops accounted for (39 rows, 24 publications; gaps and failed leads listed).
- **CO2 and nutrient quality**: an elevated-CO2 *experimental stress test* (not a 2050 forecast) with partial coverage:
  12 primary crop-nutrient effects (Myers 2014 original FACE table); energy, fat, bean and groundnut are not estimated.
- **Diversity after losses**: whole-food-supply Shannon diversity beside adequacy; losing part of a dominant staple can
  raise the effective number of sources while total supply falls.

Rerun alone: `powershell -ExecutionPolicy Bypass -File .\run_extensions.ps1` (from `code\`); they are also in
`run_all.ps1`. **Not done / open:** teammate review of parameter statuses, CO2 evidence selection and literature
verdicts; pdfLaTeX test; slides not updated (see below); CO2 evidence for bean, groundnut, energy and fat; a supported
rice yield slope, any rapeseed heat slope, a *Vigna* parameter set.

**Presentation statements that will need updating later (`docs/final_slides.tex`, not touched; it still compiles from
the same macros):** the "Result 1: wheat is the most vulnerable crop" slide needs its condition (first in the full
index, which uses proxies; first among the seven crops with supported parameters; rice and rapeseed not established);
the literature slide's counts changed because the Ray et al. row was reclassified (7 of 12 "agree" instead of 8); the
slide that says the CO2 nutrient effect is "shown only as an extra pathway" is superseded by the stress test (partial
coverage, not a forecast); and any statement that the diversity of supply measures dietary quality. The slides do not
present the new material (parameter audit, future-literature coverage, CO2 quality, diversity after losses).

## Reproduction status (18 Nov 2026)

- **Inputs:** `00_data_manifest.py --check`: 74 of 74 raw files present with matching SHA-256 (the 55 original
  entries plus 19 Telangana-mask and Indian survey files added to the manifest in this audit). The climate, SPAM,
  calendar, FAOSTAT and USDA files are the original snapshot files: exact reproduction, not a new data snapshot.
- **Full rerun from raw inputs:** `data/work` was moved aside (kept outside the repository as a comparison copy) and
  `run_all.ps1` was run without `-SkipClimate` in a fresh Python 3.13 environment built from `requirements.txt`.
  Every data step ran (about 21 minutes).
- **Comparison** (`27_compare_rerun.py`, `data/processed/nine_crop/audit_rerun_comparison.csv`): every file present in
  both runs is identical (107 intermediate files, 85 result tables, all generated LaTeX). The 75 previous files that
  were not regenerated are unused leftovers (opt-in legacy per-cell metrics, an old cache, a shell script).
- **Checks:** 29 of 29 consistency checks pass; the derived heat parameters are reproduced from the published data.
- **Not done:** pdfLaTeX compile; independent teammate review; team rehearsal.

Details, corrections and limitations: `docs/END_EVAL_RESULTS_REGISTER.md`, and Section 15 and the appendices of the report.
