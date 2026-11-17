# End-evaluation results and limitations register

Status vocabulary (plan, section 3): *not started / in progress / awaiting data / verified*. **Nothing is marked
"verified" here**: the plan requires a second teammate to check each parameter against its source, one calculation,
and the interpretation. Status below is therefore **"implemented, awaiting team review"** unless stated, and the
last column says what the reviewer should check. All numbers are in `data/processed/nine_crop/` (machine readable)
and the generated LaTeX macros; none is typed by hand in the documents.

## Commitments C1-C10

| ID | Commitment | Status | Evidence (files) | What a reviewer should check |
|---|---|---|---|---|
| C1 | Common index, reproducible crop x country scores, F4 | implemented, awaiting review | `index_components.csv`, `index_crop.csv`, `worked_example.csv` (wheat-India from raw values to F4; the code asserts hand = pipeline) | Re-derive one other pair by hand |
| C2 | Nine crops in three groups | implemented, awaiting review | `docs/input_register.csv/.md`, `docs/literature_verification_new_crops.md`, `panels.csv` (59 pairs, 20 countries) | Each new-crop heat value is a *fit* (chamber or field data), not a quoted threshold; rapeseed slope and lentil K_y are proxies |
| C3 | Refined implementation: literature-only main sensitivity, regenerated tables and figures | implemented | `config.py` (blended kept only as a labelled robustness row); four-crop regenerated set in `figures/four_crop/`, `docs/four_crop/generated/`; `compare_mideval_vs_fourcrop.csv` | Mid-evaluation crop order unchanged under literature-only (four-crop run) |
| C4 | Present comparison, nine crops, both weightings | implemented | `index_crop.csv`, `index_components.csv`, `compare_fourcrop_vs_ninecrop.csv` (normalisation-reference effect separated from physical stress, which is identical) | Original-pair scores roughly halve because the new maxima (bean heat, chickpea water) enlarge the reference |
| C5 | Future vulnerability, comparable processing | implemented, awaiting review | `future_components.csv`, `future_crop.csv`, `future_group.csv`, `future_check_hist_vs_main.csv` (historical run reproduces the main 1971-2000 series, max difference ~4e-6), `future_clim_check.csv` | Change-factor choice (decision E9); single model |
| C6 | Crop group comparison | implemented | `index_group.csv`, `future_group.csv` | Group = mean of three selected crops; not all cereals/pulses/oilseeds |
| C7 | Comparison with published findings, incl. disagreements | implemented | `literature_comparison.csv` (verdicts computed from our results), `docs/literature_comparison_sources.md` (quotes, page/table, read level) | Re-check 3 quotes against the papers; two disagreements are reported, not hidden |
| C8 | Nutritional significance | implemented, awaiting review | `adequacy.csv`, `yield_diet_scenarios.csv`, `future_nutrition.csv`, `food_supply_diversity.csv`, `india_nutrient_sources.csv` | Requirement choice changes the iron shortfall count (main vs moderate-bioavailability variant) |
| C9 | Final communication | implemented | `docs/final_report.pdf`, `final_slides.pdf`, `final_appendix.pdf`; figures `figures/nine_crop/G*.pdf` | Team rehearsal not done |
| C10 | Reproducible evidence | implemented | `code/run_all.ps1`, `requirements.txt`, `docs/DATA_MANIFEST.csv` (55 raw files with SHA-256), `README.md` | A teammate should run `00_data_manifest.py --check` and one representative step on a fresh checkout |

## Plan-specific items

| Plan item | Outcome |
|---|---|
| P0 recover and record | Original inputs reused from the mid-evaluation folder (no re-download of FAOSTAT etc.). New inputs are a **new data snapshot, 17 Nov 2026**: Sacks calendars (pulses, groundnut, rapeseed), WorldClim 1970-2000 tmax/tmin normals, WorldClim CMIP6 MRI-ESM2-0 SSP2-4.5 2041-2060, FAOSTAT SUA, Natural Earth admin-1, India/Telangana survey files (`data/raw/india/`). Four-crop grids, precipitation series, hazards, importance, adequacy, crop contributions and the four-crop panel are bit-identical to the mid-evaluation run. |
| P1 four-crop completion | Done (see C3). The one-pair worked example is in the report. |
| P2 five new crops | Input register complete; every proxy visible. Unresolved: heat thresholds are fits, not stated by sources; no published canola slope. |
| P3 present analysis | Done (C4, C6). |
| P4 future | Done (C5). Decisions E9-E12 in `docs/DECISION_REGISTER_END_EVAL.md`. |
| P5 nutrition and future yield accounting | Standard 10% shock extended to nine crops; future yield accounting implemented as a **conditional screening estimate** (literature damage accounting, empirical cross-check). **Scope decision:** this is not a climate-driven nutrient *forecast*; the two methods do not agree pair by pair (rank correlation ~0). |
| P6 credibility | Robustness (one-at-a-time and Monte Carlo), validation, literature comparison done under the final method. Mid-evaluation counts (80/80, 97.5%) are **not** reused. |
| P7 submission | Report, slides, appendix, input/decision register, result tables, code and manifest present. |

## Results register: which conclusions survive

| Conclusion | Survives | Evidence |
|---|---|---|
| Wheat is the most vulnerable crop | Yes | first in all but two of 46 robustness rankings of F4 (the exceptions are the empirical-sensitivity-only tests); first in ~92% of 2,000 random weightings |
| Order of positions 2-9 | No (moves with weighting and pulse parameters) | `index_robustness.csv` |
| Vulnerability rises mainly through heat by 2041-2060 | Yes for the sum over pairs; wheat in Russia/USA is water-driven | `future_components.csv` |
| Iron is the nutrient closest to shortfall | Yes under the main requirement; no under the 15%-bioavailability requirement | `adequacy.csv` |
| Index predicts yield-shock frequency | Partly: positive association in the 59-pair sample; null in the mid-evaluation 26-pair sample | `val_shocks_test.csv`; read as an association |
| Future nutrient numbers | Conditional screening only | `future_nutrition.csv` |

## Limitations (tied to findings)

1. Monthly climate hides hot days (rice and soybean ~0 heat exposure); water ratio has no soil storage.
2. Common-bean threshold (one Andean variety, chamber data, FAO "Beans, dry" includes tropical *Vigna* pulses in India and Myanmar) sets the heat reference for all crops.
3. SPAM 2010 maps: Telangana's paddy area is about three times larger in 2023-24 state statistics.
4. Pigeon pea (tur) and moong are major in Hyderabad's diet but outside the nine crops.
5. One climate model, one scenario; no CO2 fertilisation or adaptation.
6. HCES and NSS describe state rural/urban households, not Hyderabad city; NFHS has a district fact sheet.
7. Not verified in the sources: Prasad 2002/2003, Morrison and Stewart 2002 full texts; the origin of FAO-56 Rev.1's rapeseed K_y; see `docs/literature_verification_new_crops.md` section 6.
8. Not done: the team rehearsal; reviewer sign-off; a test of the documents with `pdflatex` itself (see README).

## Corrected earlier claims

- The submitted literature review and `refs.bib` cited Beach et al. (2019, Lancet Planet. Health) as "Smith and Myers 2019"; `refs.bib` now has the correct entry (`beach2019`). Reference [16] of the submitted paper still carries the wrong authorship.
- The handoff said the (blended) mid-evaluation values would "roughly double" under literature-only sensitivity; the median ratio of the regenerated four-crop run to the mid-evaluation numbers is in `compare_mideval_vs_fourcrop.csv`.
