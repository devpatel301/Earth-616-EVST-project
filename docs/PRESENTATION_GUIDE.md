# Professor presentation

The slides recreate the supplied Big Longs theme: black backgrounds, white section labels, large grey uppercase titles, numbered rounded white panels and geometric ornaments reused from the reference. Graphs, maps and equation images retain white backgrounds, with coloured data series. The reference PDF uses outlined Type3 lettering, approximated with editable Arial Black headings and Arial body text. Visible footers, source footers and slide numbers are removed; citations and timings remain in the PowerPoint speaker notes.

The structure follows the explanatory progression of the mid-evaluation presentation (`est-project/S_rice_precipitation/latex/slides_new.pdf` in the sibling repository). It introduces each metric before showing the broad patterns across crops and nutrients, then develops the wheat, India, CO2-quality and diversity findings. It retains the final nine-crop methodology, including literature-only sensitivity rather than the superseded empirical/literature blend in the old slides.

Present `docs/final_slides.pdf`, or use `output/presentation/EST_Earth616_PPT.pptx` for PowerPoint presenter view. There are 25 main slides, timed to 1,200 seconds in the speaker notes, followed by four backup slides for questions. The PowerPoint contains editable summary charts and tables; equations and scientific plots are embedded images. The PDF is the matching projection copy.

New metric graphs explain heat exposure, water exposure, crop sensitivity and nutritional importance using saved results. The overview includes all nine crop rankings, historical/future trajectories under both weightings, stress contributions, crop nutrient profiles and a 20-country summary of nutrient changes. Country maps and the diversity scatterplot support the later focused findings. Source data and basemap provenance are recorded in `figures/presentation/PROVENANCE.md`. Maps show national aggregates for selected wheat countries, not local crop-grid estimates.

## Running order

| Slides | Subject | Time |
|---|---|---:|
| 1-3 | Question, coverage and comparison periods | 1:30 |
| 4-10 | Framework, each index component, F4 and nutrient accounting | 6:00 |
| 11-16 | Overall crop patterns, future trends, nutrient roles, changes and adequacy | 5:20 |
| 17-22 | Wheat maps, India dependence, CO2 quality and diversity after losses | 5:10 |
| 23-25 | Literature, limitations and conclusions | 2:00 |
| 26-29 | Backup only | Outside the 20 minutes |

The notes provide talking points and timing, not a word-for-word script. Rehearse aloud: speaking speed and questions will change the elapsed time. Finish slide 10 at 7:30, the overview at 12:50, and the focused results at 18:00.

## Explaining the figures

- Slide 3 maps the 20 selected countries, coloured by number of crops evaluated. Coverage is not a risk score; grey countries are outside the panels. Slide 18 maps observed state wheat production shares and irrigation coverage from the official Agricultural Statistics at a Glance 2024-25, using its 2023-24 columns. These contextual state statistics are separate from the national model. Source details and limitations are in `docs/evidence/INDIA_STATE_MAP_SOURCES.md`.
- Heat exposure is monthly temperature exceedance during the flowering window, normalised by a reference maximum. A low or rounded-zero value does not exclude damaging daily extremes.
- Water exposure is unmet growing-season demand on rainfed land. The model assumes irrigation fully buffers the deficit and omits soil-water storage.
- Sensitivity is a crop coefficient per unit stress, normalised across crops. The wheat example explains the raw slope; the graph shows the normalised coefficient. Empirical regressions do not enter the main index.
- Importance averages the crop's national supply shares of energy, protein, fat, zinc and iron. The teaching graph shows the mean unnormalised importance as a percentage.
- The broad nutrient-change chart shows the median of 20 national percentage changes, giving each country equal weight. It is not a population-weighted global loss. Source values remain unchanged; chart workbooks round these medians to six decimal places, while visible labels show two.
- Graphs averaging crop-country pairs use each crop's own selected panel. These panels differ, so their mean shares cannot be added to construct a world diet.

## Claims to keep precise

- F4 is a relative screening index, not a percentage yield loss. Its combination and weighting are project choices built from established component methods.
- Wheat leads within the model and panel. The restricted seven-crop screen still retains some derived and borrowed assumptions.
- The group future comparison and the 72% heat contribution use the historical reference. The 20-country and India quantity/quality charts use the present-relative variant. The two references are compared in backup.
- Pulses rise fastest proportionally under equal-country weighting. Cereals rise fastest proportionally under production weighting. Avoid presenting the first statement as true under both weightings.
- CO2 nutrient effects are a partial-evidence experimental stress test, not calibrated SSP2-4.5 effects. No quality effect is estimated for energy/fat or transferred between species.
- The diversity example is a 10% wheat production shock under upper supply pass-through. Effective sources can rise because wheat becomes less dominant, even as iron availability falls.
- Seven-versus-zero countries below an iron requirement is sensitivity to bioavailability assumptions. It is not observed deficiency prevalence.
- The literature follow-up adds regional evidence for six previously unmatched pairs and suitability evidence for four, leaving 19 future comparisons unverified. These are partial matches, not ten validations.
- Trade is already present in static supply accounting. Future price, demand and trade behaviour are not modelled. They may explain availability/economic differences, not automatically biological yield differences.

## Build and source

Run `code/build_presentables.ps1 -Tectonic <path-to-tectonic.exe>` from PowerShell. It reads saved CSVs, builds the editable deck and matching PDF, and compiles the comprehensive report. It does not rerun analyses or their tests. It requires the bundled Codex Artifact Tool runtime, Python with pandas/matplotlib, and Tectonic. The presentation source is `code/build_presentation.mjs`; mathematical assets are prepared by `code/presentation_data.py`. Subsequent builds preserve existing PowerPoints and give new revisions a timestamp; the private `data/work/presentation/deliverables.json` records the current output paths.

The comprehensive report is `docs/final_report.pdf`; its appendices include the supporting tables and equations. Literature and parameter files are in `docs/evidence/`, and decision/results history is in `docs/records/`.
