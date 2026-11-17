# run_all.ps1 -- reproduce every end-evaluation number, table, figure and PDF (Windows PowerShell, run from code\).
#   powershell -ExecutionPolicy Bypass -File .\run_all.ps1            full run
#   powershell -ExecutionPolicy Bypass -File .\run_all.ps1 -SkipClimate   reuse data\work climate series/hazards
# Python: set $env:CNVI_PY to the interpreter (default ..\.venv\Scripts\python). Requirements: ..\requirements.txt
# Raw data: data\raw (see docs\DATA_MANIFEST.csv; check with `python 00_data_manifest.py --check`).
param([switch]$SkipClimate)
$ErrorActionPreference = "Stop"
$py = if ($env:CNVI_PY) { $env:CNVI_PY } else { "..\.venv\Scripts\python" }
function Run($script, $run, $extra) {
    $env:CNVI_RUN = $run
    Write-Host "== [$run] $script $extra"
    & $py $script $extra
    if ($LASTEXITCODE -ne 0) { throw "$script failed ($run)" }
}

# ---- 1. shared climate processing (all 9 crops + 3 alternative-calendar pseudo-crops; hours on first run) ----
if (-not $SkipClimate) {
    Run 01_download_data.py nine_crop          # skips files already present
    Run 02b_climate_zones.py nine_crop        # Koppen groups: needed by the cool-season calendar rule
    Run 03_build_grids.py nine_crop
    foreach ($v in "prec", "tmax", "tavg") { Run 04_climate_exposure.py nine_crop $v }   # tmin series unused
    Run 04_hazards.py nine_crop
    Run 14_future_climate.py nine_crop       # future hazards (change factors) -- climate-only, run once
}

# ---- 2. both crop sets: four_crop = mid-evaluation crops with the presented (literature-only) method;
#         nine_crop = end-evaluation main run ----
foreach ($run in "four_crop", "nine_crop") {
    Run 03_panels.py $run
    if (Test-Path ..\data\raw\koppen\koppen_geiger_1991_2020_0p5.tif) { Run 02c_check_koppen.py $run }
    Run 05_country_series.py $run
    Run 06_sensitivity.py $run
    Run 07_nutrition.py $run
    Run 07b_use_shares.py $run
    Run 08_index.py $run
    Run 09_yield_diet.py $run
    Run 10_validation.py $run
    Run 13_lit_sensitivity.py $run
}
# mid-evaluation figure/table set, regenerated for the four-crop literature-only run (P1 evidence)
Run 11_figures.py four_crop
Run 12_export_tex.py four_crop

# ---- 3. future, nutrition, comparisons, end-evaluation figures and tables (nine_crop) ----
Run 15_future_index.py nine_crop
Run 16_future_yield_nutrition.py nine_crop
Run 17_compare_runs.py nine_crop
Run 18_endeval_figures.py nine_crop
Run 20_input_register.py nine_crop
Run 21_india_hyderabad.py nine_crop
Run 22_literature_comparison.py nine_crop
Run 23_sources_doc.py nine_crop
Run 19_endeval_tex.py nine_crop

# ---- 4. documents (Tectonic, https://tectonic-typesetting.github.io) ----
$tectonic = if (Get-Command tectonic -ErrorAction SilentlyContinue) { "tectonic" } else { "$env:LOCALAPPDATA\tectonic\tectonic.exe" }
Set-Location ..\docs
foreach ($doc in "final_report", "final_slides", "final_appendix") { & $tectonic -X compile "$doc.tex" }
Set-Location ..\code
