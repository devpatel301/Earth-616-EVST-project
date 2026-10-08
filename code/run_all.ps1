# run_all.ps1 -- reproduce every number, table and figure (Windows PowerShell, from the code folder).
# Steps 01 (download, hours on a slow network) and 04_climate_exposure (one pass per variable) are
# skipped when their outputs already exist.
$ErrorActionPreference = "Stop"
$py = "..\.venv\Scripts\python"
if (-not (Test-Path ..\data\work\series_tavg_soybean.npz)) {
    & $py 01_download_data.py
    & $py 03_build_grids.py
    foreach ($v in "prec", "tmax", "tmin", "tavg") { & $py 04_climate_exposure.py $v }
}
if (-not (Test-Path ..\data\work\hazards_soybean.npz)) { & $py 04_hazards.py }
& $py 02b_climate_zones.py
& $py 03_panels.py
# optional check of our Koppen groups against Beck et al.'s published 0.5-degree map (manual download, see 01_download_data.py)
if (Test-Path ..\data\raw\koppen\koppen_geiger_1991_2020_0p5.tif) { & $py 02c_check_koppen.py }
& $py 05_country_series.py
& $py 06_sensitivity.py
& $py 07_nutrition.py
& $py 07b_use_shares.py
& $py 08_index.py
& $py 09_yield_diet.py
& $py 10_validation.py
& $py 11_figures.py
& $py 12_export_tex.py
# LaTeX (Tectonic, https://tectonic-typesetting.github.io): slides, appendix and report
Set-Location ..\docs
tectonic -X compile slides.tex
tectonic -X compile appendix.tex
tectonic -X compile report.tex

