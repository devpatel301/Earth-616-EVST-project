# run_extensions.ps1 -- rerun ONLY the research extensions (CO2 nutrient quality, diversity after losses, future
# literature coverage, parameter evidence) from the existing verified nine-crop outputs; no climate processing.
# Run from code\:   powershell -ExecutionPolicy Bypass -File .\run_extensions.ps1
# Prerequisites: data\processed\nine_crop\ from run_all.ps1 (nutrient_supply.pkl, adequacy.csv, crop_contrib.csv,
# panels.csv, country_series.pkl, future_country_series.pkl, future_yield.csv, future_components.csv, ...).
# The extensions only READ those files; they write new files and never modify the established results.
# Afterwards rebuild the report tables and PDF:  run_all.ps1 -SkipClimate  (or the tail of it: 19, 26, Tectonic).
$ErrorActionPreference = "Stop"
$py = if ($env:CNVI_PY) { $env:CNVI_PY } else { "..\.venv\Scripts\python" }
$env:CNVI_RUN = "nine_crop"
foreach ($s in "28_co2_quality.py", "29_diversity_losses.py", "30_future_literature.py", "31_parameter_evidence.py",
               "32_extension_checks.py", "33_extension_tables.py") {
    Write-Host "== [nine_crop] $s"
    & $py $s
    if ($LASTEXITCODE -ne 0) { throw "$s failed" }
}
