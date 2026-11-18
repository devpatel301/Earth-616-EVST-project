# Build documents and slides from SAVED results. No scientific analysis or tests are run.
param([string]$Python='python', [string]$Tectonic='tectonic')
$ErrorActionPreference='Stop'
$repoRoot=Split-Path $PSScriptRoot -Parent
Push-Location $repoRoot
try {
    & $Python code/presentation_data.py
    if ($LASTEXITCODE -ne 0) { throw 'Presentation assets failed' }
    & $Python code/presentation_figures.py
    if ($LASTEXITCODE -ne 0) { throw 'Presentation figures failed' }
    & $Python code/presentation_maps.py
    if ($LASTEXITCODE -ne 0) { throw 'Presentation maps failed' }
    & $Python code/presentation_india_states.py
    if ($LASTEXITCODE -ne 0) { throw 'India state maps failed' }
    $runtimeDir="$env:USERPROFILE/.cache/codex-runtimes/codex-primary-runtime/dependencies"
    $env:RUNTIME_NODE_MODULES="$runtimeDir/node/node_modules"
    & "$runtimeDir/node/bin/node.exe" code/build_presentation.mjs
    # Artifact Tool may retain a child process exit status; verify its successful receipt too.
    $deliverables=Get-Content data/work/presentation/deliverables.json -Raw | ConvertFrom-Json
    if (-not (Test-Path -LiteralPath $deliverables.powerpoint)) { throw 'PowerPoint export failed' }
    $receipt=Get-Content data/work/presentation/validation.json -Raw | ConvertFrom-Json
    $deckHash=(Get-FileHash -LiteralPath $deliverables.powerpoint -Algorithm SHA256).Hash.ToLower()
    if ($receipt.finalSha256 -ne $deckHash -or -not $receipt.firstPartyImport.passed) { throw 'PowerPoint validation did not pass' }
    if (-not (Test-Path docs/final_slides.pdf)) { throw 'Slide PDF export failed' }
    Push-Location docs
    try {
        foreach ($doc in 'final_report') {
            & $Tectonic -X compile "$doc.tex"
            if ($LASTEXITCODE -ne 0) { throw "Compile failed: $doc" }
        }
    } finally { Pop-Location }
} finally { Pop-Location }
