# Presentation figure provenance

Figures are plot-only views of saved nine-crop CSV results; no scientific pipeline or tests were run.
The wheat maps colour only the six modelled wheat countries. Present scores use 2001-2024; projected differences use 1971-2000 to 2041-2060. Grey is unmodelled, not zero risk. Country fill represents national aggregates, not local crop-area estimates. Boundaries are for visual context.

Basemap: Natural Earth 1:110m admin-0 countries, public domain. Retrieved 18 November 2026.
Source: https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson
SHA256: 6866c877d39cba9c357620878839b336d569f8c662d3cfab4cb1dbe2d39c977f
License: https://www.naturalearthdata.com/about/terms-of-use/

Trajectory: future_crop.csv. Stress components and nutrient profiles: index_components.csv (equal mean over each crop's own panel). Diversity: diversity_after_losses.csv, upper pass-through, scenarios B/C, historical-reference future, fixed FBS categories. Panel means are not world population-weighted means.

Metric teaching graphs: heat_exposure, water_exposure, importance_profile and sensitivity_profile read E_heat, E_water, I, S_heat and S_water from saved index_components.csv. They show equal country means within each crop panel. Sensitivity is literature/proxy only, not the earlier blended empirical method. Stars identify rice/rapeseed unsupported heat-response assumptions; additional transfer limitations remain for other crops.

World overview map: number of unique modelled crops per country in saved index_components.csv (59 pairs, 20 countries), using Natural Earth ISO numeric identifiers. Coverage is not vulnerability. India map: geographic locator for national results only, with no state/district estimates. Same Natural Earth basemap and provenance as above. Built by code/presentation_maps.py without rerunning scientific calculations.

India state wheat maps: official Agricultural Statistics at a Glance 2024-25, Table 2.5(b), printed p54; 2023-24 production and irrigation columns, ten listed states. Contextual observed data, not state model outputs. geoBoundaries IND ADM1 (2011 metadata reference), CC BY 2.5 IN, pinned commit 9469f09. Boundary SHA256: 4c63fe43294a391e8f2de4e9f86f3edb60f8688275b9fee90c61fb2aa0c26061. Details: docs/evidence/INDIA_STATE_MAP_SOURCES.md.
