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
| C9 | Final communication | report implemented as one comprehensive document; slides not redesigned (presentation work pending) | `docs/final_report.pdf` (sources `docs/final_report.tex` + `docs/report/`), `final_slides.pdf`, `final_appendix.pdf`; figures `figures/nine_crop/G*.pdf` | Team rehearsal not done; slides compile from the same macros but do not yet present the report's new material (ledger, worked examples, audit) |
| C10 | Reproducible evidence | implemented; full rerun from raw inputs reproduces all outputs exactly (second audit below) | `code/run_all.ps1`, `requirements.txt`, `docs/DATA_MANIFEST.csv` (55 raw files with SHA-256), `consistency_checks.csv` (29 checks), `README.md` | A teammate should run `00_data_manifest.py --check` and one representative step on a fresh checkout |

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
| Wheat is the most vulnerable crop | Yes, conditional on proxies (third audit: also first among the seven crops with supported parameters; rice and rapeseed not established) | first in all but two of 46 robustness rankings of F4 (the exceptions are the empirical-sensitivity-only tests); first in ~92% of 2,000 random weightings |
| Order of positions 2-9 | No (moves with weighting and pulse parameters) | `index_robustness.csv` |
| Vulnerability rises mainly through heat by 2041-2060 | Yes for the sum over pairs (~72 % heat); wheat in Russia is mainly water-driven, wheat in the USA and bean in Tanzania shared heat/water (earlier text said "Russia/USA water-driven": corrected 18 Nov) | `future_components.csv` |
| Iron is the nutrient closest to shortfall | Yes under the main requirement; no under the 15%-bioavailability requirement | `adequacy.csv` |
| Index predicts yield-shock frequency | Partly: positive association in the 59-pair sample; null in the mid-evaluation 26-pair sample | `val_shocks_test.csv`; read as an association |
| Future nutrient numbers | Conditional screening only | `future_nutrition.csv` |

## Limitations (tied to findings)

1. Monthly climate hides hot days (rice and soybean ~0 heat exposure); water ratio has no soil storage.
2. Common-bean threshold (one Andean variety, chamber data, FAO "Beans, dry" includes tropical *Vigna* pulses in India and Myanmar) sets the heat reference for all crops.
3. SPAM 2010 maps: Telangana's paddy area is about three times larger in 2023-24 state statistics.
4. Pigeon pea (tur) and moong are major in Hyderabad's diet but outside the nine crops.
5. One climate model, one scenario; no CO2 fertilisation or adaptation (a separate CO2 nutrient-quality stress test is in the third audit below).
6. HCES and NSS describe state rural/urban households, not Hyderabad city; NFHS has a district fact sheet.
7. Not verified in the sources: Prasad 2002/2003, Morrison and Stewart 2002 full texts; the origin of FAO-56 Rev.1's rapeseed K_y; see `docs/literature_verification_new_crops.md` section 6.
8. Not done: the team rehearsal; reviewer sign-off; a test of the documents with `pdflatex` itself (see README). (The climate steps were re-run from raw inputs in the second audit.)

## Corrected earlier claims

- The submitted literature review and `refs.bib` cited Beach et al. (2019, Lancet Planet. Health) as "Smith and Myers 2019"; `refs.bib` now has the correct entry (`beach2019`). Reference [16] of the submitted paper still carries the wrong authorship.
- The handoff said the (blended) mid-evaluation values would "roughly double" under literature-only sensitivity; the median ratio of the regenerated four-crop run to the mid-evaluation numbers is in `compare_mideval_vs_fourcrop.csv`.

## Audit and re-run, 18 Nov 2026

Done on this machine: the data-manifest check (55 of 55 raw files present, checksums match); a fresh Python 3.13
environment built from `requirements.txt`; `run_all.ps1 -SkipClimate` end to end (every script exits 0; a failing
script or a failing `tectonic` compile stops the run; `24_checks.py` runs before the documents are built);
all three PDFs rebuilt with Tectonic and inspected page by page for layout and stale values.
**Not done:** the climate steps (`01`-`04`, `14`) were not re-run: their outputs in `data/work` come from the raw files
that the manifest verifies, but they were not regenerated in this audit. No `pdflatex` run. No teammate review or rehearsal.

Defects found and fixed:

1. **Nine-crop supply share** excluded chickpea and lentil (no FBS item of their own). Fixed in `21_india_hyderabad.py` (decision E18). India 2021-23: energy 55.19 -> 58.00 %, protein 48.94 -> 55.30 %, iron 50.56 -> 55.82 %, fat 35.71 %, zinc 64.48 %. The three diagnostic values match the earlier inspection exactly, so the input snapshot did not change.
2. **Negative or inverted yield-to-nutrient bounds** (decision E19). `yield_diet_scenarios.csv` and `future_nutrition.csv` regenerated; 7 of the historical scenario rows (Canada lentil with its negative SSR in S1-S3; rice-Bangladesh, lentil-Ethiopia, bean-Belarus and rapeseed-India where the lower bound exceeded the upper) and 3 future rows (Canada lentil, bean-Belarus) changed; the largest change in any nutrient-supply percentage is 0.26 points.
3. **Stale four-crop outputs.** The committed `data/processed/four_crop/` empirical sensitivities and the S1/S2 scenarios were not what the current code produces (the empirical water slope differed by up to 33, S1/S2 yield changes by up to 20 points). The re-run reproduces the nine-crop run exactly on the 24 shared pairs. The empirical slopes are checks only, so the four-crop index scores and the nine-crop results are unchanged.
4. **Layout:** the future crop table in the report was a bare tabular 174 pt too wide, tables with notes were shrunk to unreadable size, the worked-example backup slide cut off its F4 row, overlapping tick labels in Figure 2, long file names overflowing in methods and appendix. All fixed.
5. `run_all.ps1` did not stop on a failed document compile; it does now.

Checks (`code/24_checks.py`, saved in `consistency_checks.csv`; 29 of 29 pass): nine crops and 59 pairs; every crop in the input register; E = level / fixed maximum; S equals literature slope and K_y over their maxima (literature-only); F4 recomputed from components; crop scores (equal, production-weighted) and group scores recomputed; the future run's present column equals the main F4; the future and 1971-2000 scores use the present-period reference; S and importance are identical across periods; heat part + water part = change in F4; the 1971-2000 comparator matches the main series (relative difference 2e-7); future yield change comes from loss accounting; crop contribution totals equal the FBS totals; nine crops never exceed 100 % of any supply; SUA chickpea and lentil stay within the parent FBS aggregate in 99.9 % of country-years and are kept out of totals; the India nine-crop share equals the summed contributions; the shock is -10 % everywhere; nutrient changes are never positive and lower bounds never exceed upper bounds.

Unchanged by the re-run: every `index_*`, `future_components/crop/group`, `adequacy`, `importance` and `crop_contrib` table of the nine-crop run is identical to the committed version (git shows no change).

## Second audit: full reproduction from raw inputs and source review, 18 Nov 2026

**Reproduction.**
- **Manifest.** 74 of 74 raw files match their SHA-256: the 55 original entries plus 19 files added in this audit (Telangana admin-1 mask and the India/Telangana survey files, which were used but not listed). The climate, SPAM, calendar, FAOSTAT and USDA files are the original snapshot files (symlinked from the mid-evaluation folder), so this is exact reproduction, not a new snapshot.
- **Rerun.** `data/work` (~10 GB) was moved outside the repository as a comparison copy, so no cached file could be reused; copies of `data/processed`, the figures and the generated LaTeX were taken too. `run_all.ps1` was then run **without** `-SkipClimate` in a fresh Python 3.13 venv from `requirements.txt`. All steps ran: 02b, 03 grids, 04 climate series (prec, tmax, tavg), 04 hazards, 14 future climate, then 03_panels through 13 for both runs, 11/12, 15–23, 24, 19.
- **Run outcome.** It stopped, as designed, at the report compile: the new report referenced audit macros that did not exist yet. Every data step had finished, in 21 minutes.
- **Comparison** (`code/27_compare_rerun.py` → `data/processed/nine_crop/audit_rerun_comparison.csv`, tolerance 1e-9 absolute and relative):
  - 107 intermediate files, 85 result tables and 31 generated LaTeX files are **identical**; 0 within tolerance only; 0 differ.
  - 75 previous files were not regenerated, and none is used by the pipeline: 72 legacy per-cell metric files (written only with `CNVI_LEGACY_METRICS=1`), an old production cache, a pulse cache and a shell script.
  - New: the outputs of `25` and `26`.
- **Final check.** A final `run_all.ps1 -SkipClimate` with the complete pipeline order (24 → 25 → 19 → 26 → documents) is reported in the final response of this audit.

**Source review** (`docs/literature_verification_new_crops.md` §8; report Appendix A ledger):
- **FAO-33 rice.** Read: no K_y; rice is classed "high" (Table 2 p. 7), the same class as maize. The rice K_y 1.25 is therefore explicitly a proxy.
- **Nandi 2021.** The "1 % per 1 %" sentence is now verbatim (abstract). It supports the lentil proxy K_y 1.0.
- **FAO-56 Rev.1 rapeseed K_y 0.90.** The whole text was searched; no source is stated.
- **Jalota 2006.** Identified as a CROPMAN simulation; its abstract gives no K_y. The range 0.67–0.93 stays secondary.
- **Still not accessible:** Prasad 2002 and 2003 and Morrison & Stewart 2002 full texts.
- **Derived heat fits** are now reproducible (`code/25_parameter_fits.py`) and match `config.py`.
- **SUA stock-variation sign** checked against the sum of uses (100 % identity). Canada lentil's negative supply is a published FAOSTAT 2023 balance (residuals −267 kt).

**No numerical result changed in the second audit.** Wording corrections:
- wheat-USA future increase is shared heat/water;
- bean has no empirical response in **any** country;
- maize's empirical response is much larger than the literature accounting.

**Report.** `docs/final_report.pdf` was rewritten as one comprehensive document (59 pages, clickable contents, lists of figures and tables, numbered equations). It contains the parameter ledger, worked examples, record of corrections and audit evidence. The old `docs/sections/{methods,results,checks,interpretation,india_hyderabad}.tex` were superseded by `docs/report/` and removed.

**Human tasks still open** (not implementation):
- teammate review and sign-off of parameters, one calculation and the interpretation;
- team rehearsal;
- updating the slide deck to the report;
- correcting reference [16] in the submitted literature review;
- optional pdfLaTeX test.

## Third audit: research extensions (parameter evidence, future literature, CO2 quality, diversity), 19 Nov 2026

This section is new; the second audit above is kept as the record of 18 Nov 2026 and is not rewritten. The extensions
read the verified baseline results and change none of them. Report: `docs/final_report.pdf` (new sections after the
India/Hyderabad section; appendix "Research-extension evidence"). Decisions E20-E24 in `DECISION_REGISTER_END_EVAL.md`.

**Baseline unchanged.** No number of the nine-crop index, the future change, the -10% shock or the adequacy tables
changed. Text changes only: wheat's first place is now stated as conditional on proxies; the robustness ranges are
labelled exploratory perturbations; the Ray et al. row of the literature comparison was reclassified (not directly
comparable); the rice K_y source text in `config.py` and the ledger no longer implies an FAO value.

| Extension | Implemented | Main result | Unresolved |
|---|---|---|---|
| 2 Parameter evidence | `31_parameter_evidence.py`, `docs/parameter_evidence_register.csv` (97 rows), `parameter_evidence_audit.md` | Published 38, derived 18, borrowed 13, assumption 27, unsupported 1 (rapeseed heat slope); rice heat slope (fertility) also unsupported as a yield slope. Evidence-screened view: rice and rapeseed unavailable; bean India and Myanmar flagged (Vigna). Wheat first in V0, V1 (7 crops) and V2 under both weightings. Heat is 0.02% (rice) and 1.4% (rapeseed) of present F4 but 55% of rapeseed's projected change. | No supported rice yield slope on T_eff; no Brassica slope; no Vigna set; Prasad 2002/2003 and Morrison and Stewart 2002 full texts; Baker-derived rice candidate not computed |
| 1 Future literature | `30_future_literature.py`, `docs/future_literature_sources.csv/.md`, `future_literature_assessment.csv` | 39 rows, 24 publications, 26 read in full, 13 abstract only; all nine crops accounted for; verdicts 12 consistent, 21 partly, 5 different, 1 not comparable (a description of the evidence, not an accuracy score). 29 of 59 pairs have no verified study. Studies with CO2 fertilisation or adaptation find gains where we find losses (Canada lentil, Brazil bean). MRI-ESM2 described by one study as the least pessimistic model. | Verdicts not reviewed by teammates; Qian 2026 and Singh 2014 abstract only; no study for most Australian, Turkish, Russian, USA and Chinese pulse pairs |
| 3 CO2 quality | `28_co2_quality.py`, `docs/co2_nutrient_effects.csv/.md`, `co2_effects_used.csv`, `co2_reference_levels.csv` | Stress test, not a forecast. 12 primary effects (Myers 2014 original FACE table; 9 significant). India: quality only protein -2.96%, zinc -3.85%, iron -2.24%; climate yield only -1.55, -1.72, -2.03; combined -4.45, -5.44, -4.20 (multiplicative); MAR -0.75 points. Zinc falls more from quality than from the climate yield channel in all 20 panel countries. MAR hides it (zinc adequacy stays at or above 1). | Energy, fat, bean, groundnut not estimated; chickpea, lentil, rapeseed thin or extended-only; no dose-response, so no scaling to SSP2-4.5 (507 ppm in 2050 vs 546-586 ppm in the experiments); FACE sites not in India |
| 4 Diversity after losses | `29_diversity_losses.py` | Whole-supply Shannon over FBS items; SUA chickpea and lentil removed from the parent item. A loss raises the effective number of sources exactly when the item share exceeds 1/N_eff (predicts the sign in 142 of 142 single-item cases). India: wheat -10% lowers iron 2.95% and raises N_eff(iron) by 0.58; CO2+climate scenario iron -4.20%, N_eff +0.49. | Loss-only; no substitution, trade or household response; N_eff depends on the FBS classification |

**Checks.** `32_extension_checks.py`: 37 of 37 pass (10 synthetic edge cases for accounting; real outputs against the
established tables: baseline totals, no FBS/SUA double counting, non-negative supply, scenario A equals the existing
-10% table, multiplicative quantity x quality by independent recomputation, ordered envelopes, missing parameters stay
missing, reference periods, DOIs in `refs.bib`).

**Human review tasks (not implementation):** teammate review of parameter statuses, the CO2 evidence selection and the
literature verdicts; decision on whether to adopt any rice or rapeseed heat parameter once evidence exists; pdfLaTeX
test; correct reference [16] of the submitted literature review (earlier item).

**Presentation items (slides not touched):** see README, "Presentation statements that will need updating later".
