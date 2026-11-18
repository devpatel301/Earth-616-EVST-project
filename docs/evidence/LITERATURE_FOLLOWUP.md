# Literature follow-up and interpretation of disagreements

Research date: 18 November 2026. This is a research addendum, not a model rerun. No pipeline, tests, climate calculation, or PDF build was run. Existing result tables and the final report retain their previous values and coverage counts. The companion `literature_followup_pairs.csv` records all 29 previously unmatched pairs and the outcomes of this targeted search.

## What the original 29 gaps meant

The earlier count meant that the repository had not recorded a verified geographically matched future study for those pairs. It did NOT establish that no relevant paper exists. The search was incomplete, some accessible material was abstract-only, and many pulse papers address historical experiments or breeding rather than future country-specific yields. A global map is useful context but cannot automatically supply a country-specific conclusion.

This follow-up identifies geographically relevant future evidence for **10 of the 29 pairs**: six have regional yield-projection evidence and four have regional climatic-suitability evidence. These are partial geographical matches, not national model validation. Nineteen pairs still lack a verified future yield/suitability comparison in this search. Some have useful mechanism evidence, identified separately below. This is a targeted search, not a systematic review or proof of absence. No claim is made that the original report's coverage count has already been regenerated.

## New future comparisons

Our side below is read from `data/processed/nine_crop/future_yield_reference_periods.csv`. Directions are compared; published numerical loss magnitudes are not compared with ours. The country-wide model output and a regional study are not identical spatial samples. Small signed changes should not be described as a substantial gain or loss.

| Pair | New evidence | Interpretation against our saved results |
|---|---|---|
| Wheat, Egypt | Ali et al., North Nile Delta, two DSSAT crop models, three GCMs, RCP8.5; yield declines and sowing-date responses | Our historical-reference change is a small loss, but present-relative change is slightly positive. Direction is therefore baseline-sensitive. Local cultivar, regional climate, phenology, irrigation and scenario differences are plausible explanations; trade is not an explanation for the biological yield difference. |
| Rice, Italy | Bocchiola, irrigated Po Valley site, climate/CO2 simulations; mid-century gains can precede later losses | Our present-relative result is positive, whereas the historical-reference result is negative. This is a partial agreement after identifying the reference period, not simply a disagreement. CO2 yield benefits and irrigation demand are treated differently. |
| Rice, USA | Wilson et al., Texas Gulf Coast; historical commercial data with a 2050 extrapolation, grain yield and milling-quality effects | Our small negative climate-only result is a different estimand from their combined climate/genetic/management analysis. Grain quantity and milling quality can move differently. This is not a national USA projection or a measurement of Fe/Zn/protein changes. |
| Maize, South Africa | Ferreira et al., Limpopo, WOFOST, five GCMs and multiple SSPs; declining yield, drought and shorter grain filling | Both our reference variants give gains. This is a useful disagreement. Their local drought/phenology findings differ from our single-model national water-balance result. A controlled common-input experiment would be needed to attribute the difference quantitatively. |
| Soybean, South Africa | Olabanji et al., Olifants catchment, WEAP-MABIA/CORDEX RCP4.5/8.5; generally declining yields with warming and drying | Our two reference variants give gains. Regional rainfall, water accounting, soil information and management distinguish the methods. The paper tests adaptations; our main calculation does not. Their local losses do not establish that every South African producing region loses. |
| Groundnut, USA | Zhen et al., Southeastern USA, modified CROPGRO-Peanut; northern gains but central/southern risks, drought-tolerant cultivar benefits | Our near-zero historical-reference loss and negative present-relative result compress heterogeneous local outcomes into one national value. Do not declare universal agreement or disagreement. Cultivar response and aggregation are documented differences; their isolated contribution to the discrepancy has not been measured. |
| Rapeseed, China | Borges et al., CLIMEX, two GCMs, RCP8.5 2040-59; shifts and some losses in suitability | Our yield direction is negative, but suitability is not yield. Tian et al. additionally report regional production-potential increases at some Yangtze sites: literature itself is heterogeneous. Our borrowed heat slope prevents treating numerical agreement as validation. |
| Rapeseed, USA | Borges et al.; future suitability reductions, with GCM-dependent extent | Qualitatively compatible with our negative yield direction, but the outcome, climate scenario and geography differ. Neither independently establishes the magnitude of the other. |
| Rapeseed, Brazil | Borges et al.; future suitability losses in some regions | Qualitative risk is compatible with our negative yield direction. Existing planted areas and all climatically suitable territory are different spatial denominators. |
| Rapeseed, South Africa | Borges et al.; future suitability losses in some regions | Compatible with our historical-reference loss, but our present-relative result is positive. A 2026 Western Cape review supplies mechanism context, not an independent country yield projection. |

## Verified sources and reading limits

No new response coefficient is taken from these papers. Peer-reviewed status is distinguished from access/read depth. Publisher-indexed abstracts or sections can establish their stated conclusions, but not omitted methods.

1. **Ali et al. (2020), Frontiers of Earth Science 14, 522-536.** *Climate change impact and adaptation on wheat yield, water use and water use efficiency at North Nile Delta.* [DOI](https://doi.org/10.1007/s11707-019-0806-4). Publisher abstract read: North Nile Delta, baseline 1981-2010, 2030s/2050s/2080s, RCP8.5; two cultivars and sowing-date options. Do not infer CO2 treatment from the abstract alone. [Publisher](https://journal.hep.com.cn/fesci/EN/10.1007/s11707-019-0806-4).

2. **Bocchiola (2015), Agricultural Systems 139, 223-237.** *Impact of potential climate change on crop yield and water footprint of rice in the Po valley of Italy.* [DOI](https://doi.org/10.1016/j.agsy.2015.07.009). Publisher-indexed abstract/highlights read, full text blocked. Landriano is a site, not all Italy; PolyCrop, two GCMs and multiple RCPs. Higher CO2 can benefit mid-century yield while irrigation needs grow. [Publisher](https://www.sciencedirect.com/science/article/abs/pii/S0308521X15300135).

3. **Wilson, Samonte and Yang (2026), Global Change Biology 32, e70679.** *Multi-Decadal Analysis on the Impact of Climate Change, Genetic Gain, Cultivar Type, and Harvest Timing on Main and Ratoon Rice Yield and Quality.* [DOI](https://doi.org/10.1111/gcb.70679). Publisher abstract, introduction and data/method sections read, plus indexed 2050 projection. Texas Gulf Coast observations 1991-2023; projection is extrapolative, not a matched SSP2-4.5 national crop-model experiment. CO2 and cultivar effects distinguish the analysis from climate-only losses. [Publisher](https://onlinelibrary.wiley.com/doi/10.1111/gcb.70679).

4. **Ferreira et al. (2023; online 2022), International Journal of Biometeorology 67, 133-148.** *Drought patterns: their spatiotemporal variability and impacts on maize production in Limpopo province, South Africa.* [DOI](https://doi.org/10.1007/s00484-022-02392-1). Publisher abstract, introduction and indexed impacts discussion read. Two locations, five GCMs, three SSPs, multiple emergence dates; drought timing and shortened development are relevant to our omitted mechanisms. [Publisher](https://link.springer.com/article/10.1007/s00484-022-02392-1).

5. **Olabanji, Ndarana and Davis (2021), Climate 9, 6.** *Impact of Climate Change on Crop Production and Potential Adaptive Measures in the Olifants Catchment, South Africa.* [DOI](https://doi.org/10.3390/cli9010006). Publisher-indexed abstract and Results/Table 5 excerpts read; full publisher access timed out. WEAP-MABIA, six CORDEX inputs, RCP4.5/8.5, 1976-2005 baseline and 2040-2069 mid-century window. Soybean and maize losses accompany drying/warming; management variants are investigated. [Publisher](https://www.mdpi.com/2225-1154/9/1/6).

6. **Zhen et al. (2024), Computers and Electronics in Agriculture 224, 109105.** *Drought-tolerant peanut (Arachis hypogaea L.) varieties can mitigate negative impacts of climate change on yield in the Southeastern U.S.* [DOI](https://doi.org/10.1016/j.compag.2024.109105). Publisher-indexed abstract read; full publisher page blocked. Modified CROPGRO-Peanut, 1990-2021 baseline, 2050s/2080s, RCP4.5/8.5. North-versus-south heterogeneity and cultivar traits matter. Do not infer its exact CO2 implementation without the methods. [Publisher](https://www.sciencedirect.com/science/article/pii/S0168169924004964).

7. **Borges et al. (2023), Scientific Reports 13, 12656.** *Forecasting Brassica napus production under climate change with a mechanistic species distribution model.* [DOI](https://doi.org/10.1038/s41598-023-38910-3). Author-hosted article downloaded; abstract and current/future suitability results examined, especially Fig. 3 discussion. Two GCMs, RCP8.5, 2040-2059. Describes losses in parts of USA, Brazil, South Africa and China; not every region loses. It models ecological suitability, despite 'production' in the title. [Author-hosted paper](https://researchnow-admin.flinders.edu.au/ws/portalfiles/portal/84137183/Borges_Forecasting_P2023.pdf). The paper's introduction contains questionable-looking oil trade units; these are not used here.

8. **Tian et al. (2018), Journal of Geographical Sciences 28, 1700-1714.** *Changes in production potentials of rapeseed in the Yangtze River Basin of China under climate change: A multi-model ensemble approach.* [DOI](https://doi.org/10.1007/s11442-018-1538-1). Publisher-indexed future-results section and bibliographic record read; direct page repeatedly timed out. Some stations gain production potential later in the century; this is a regional potential, not national observed yield. Full scenario and CO2 methods need direct inspection before a more specific comparison. [Publisher](https://www.geogsci.com/EN/abstract/article/1009-637X/40856).

## Mechanism evidence that does not close a future-yield gap

- **Australia chickpea:** Lake et al., Annals of Applied Biology 188, 698-713, online December 2025 / issue 2026, [10.1111/aab.70085](https://doi.org/10.1111/aab.70085). Publisher abstract and supplementary descriptions read. Joint heat/dryness/vapour-pressure-deficit stress and flowering traits are relevant, but the accessible evidence concerns realised climate change, including simulations through 2023. Do not call it a matched 2050 projection. NSW's official 2050 assessment is useful context but is not peer-reviewed journal evidence under the user's rule.
- **Turkey chickpea:** [10.3390/agronomy11071389](https://doi.org/10.3390/agronomy11071389) projects wild-chickpea flowering time in Ankara, not cultivated-chickpea national yield. A 2024 Turkish yield-projection thesis was found but is not admitted as peer-reviewed journal evidence.
- **USA chickpea:** Crop Science [10.1002/csc2.21003](https://doi.org/10.1002/csc2.21003) discusses germplasm conservation, heat damage and climate futures for a Washington regeneration site, not national cultivated yield. Do not repurpose the germplasm-site forecast as a crop-yield projection.
- **Australia lentil:** Frontiers in Plant Science [10.3389/fpls.2022.1019491](https://doi.org/10.3389/fpls.2022.1019491) supports genotype, soil and sowing-date mechanisms but simulates historical weather; it does not close a future-scenario gap.
- **South Africa rapeseed:** the Western Cape review [10.1080/02571862.2026.2651687](https://doi.org/10.1080/02571862.2026.2651687) supports discussion of interacting CO2, heat and water mechanisms. It is a review, not an independent national future yield projection.
- **Nigeria rice:** the apparently promising Agronomy Journal paper [10.1002/agj2.70113](https://doi.org/10.1002/agj2.70113) has Nigerian affiliations but studies irrigated farms in Cote d'Ivoire. Rejected as a Nigerian match. Other local projection leads require journal/method and study-area verification.
- **China groundnut:** a China Agricultural Sciences publisher abstract describes future oil-crop suitability/yield modelling for 2021-2060 ([record](https://www.chinaagrisci.com/EN/abstract/abstract23673.shtml)); the peanut-specific outcome and full citation were not verified, so it remains a lead rather than counted coverage. Yield-gap closure under fixed historical weather is a different counterfactual.
- **Brazil wheat:** a JEEM global vulnerability paper and older climate-impact studies are leads; country-specific direction and comparable methods were not sufficiently verified here. Seasonal yield forecasts are not long-term climate projections.
- **Remaining beans and lentils:** global niche papers, historic irrigation experiments, genetic-resource studies and market outlooks were found, but no sufficiently verified crop-country future-yield/suitability conclusion was extracted. Species mismatch remains a particular issue for the Indian/Myanmar bean category.

## Explaining disagreements without inventing causes

Use this order for each disagreement:

1. **Check the outcome:** F4 vulnerability, yield per hectare, total production, ecological suitability, nutrient concentration, national availability and household intake are different quantities. A higher F4 need not contradict a higher yield in a model containing omitted benefits.
2. **Check reference and spatial scale:** compare future relative to the same baseline, region and season before interpreting a sign difference. Our historical and present-relative directions differ for several pairs. A site and a national mean can both be right about their respective domains.
3. **Document model differences:** CO2 yield fertilisation, maturity/season length, daily extremes, soil-water storage, irrigation availability, cultivar and sowing-date adaptation, GCM/scenario, and treatment of favourable yield responses. A difference in model design is documented; its causal contribution to the disagreement is not quantified unless controlled experiments establish it.
4. **Only then examine market mechanisms**, if the compared outcome is production, national food availability, price, welfare or intake.

### Where imports, exports and demand do belong

The project already uses crop production, imports, exports and domestic supply in static accounting. `ext_common.py` maps a domestic production loss to supply using a capped self-sufficiency ratio and offers an exports-first lower bound. This is a fixed balance convention, not a model of future trading behaviour.

Markets can change the chain between crop damage and nutrition:

`climate/CO2 -> biological yield and quality -> production (yield x area) -> trade/stocks/uses -> national food supply -> prices/access/intake`.

Imports can buffer a domestic shortfall if supplies, affordability and trade access permit; overseas shocks can also transmit through prices and trade. Export adjustments and stocks may absorb part of a production shock. Demand, prices and profitability may influence crop area, input use and crop substitution. Those are conditional pathways, not measured explanations in our current model. Feed, seed, processing and waste also separate production from food available to people.

**Supported market reference:** Snyder et al. (2020), PLOS ONE 15, e0237918, [10.1371/journal.pone.0237918](https://doi.org/10.1371/journal.pone.0237918), abstract and introduction/method framing read. Its GCAM analysis shows that international market responses can materially alter US agricultural financial outcomes relative to domestic-only impacts. This supports including market pathways in the discussion; it does not show that trade caused any particular discrepancy in our yield results.

Do not say 'our yield disagrees because we did not model imports.' Trade does not directly alter the experimental biological response to temperature. It may affect realised yield indirectly through management, but that requires evidence and an explicit management pathway. Likewise, a market-driven increase in planted area can increase production despite lower yield; that is not a contradiction about yield.

### Suggested report wording

> Our comparisons reveal both consistent and divergent conclusions. Several divergences coincide with documented differences in CO2 fertilisation, crop phenology, water accounting, adaptation, spatial aggregation and reference period. These are plausible explanations rather than measured attributions: their individual contributions have not been isolated. Our nutrient-supply calculations additionally hold trading behaviour and diets fixed. Studies with endogenous trade, demand and land allocation may therefore find different national availability or economic outcomes, even when their underlying crop-yield responses have the same direction. Agreement is qualitative and does not validate our numerical magnitudes.

### Evidence needed to move from explanation to attribution

- Common climate, baseline, crop geography and cultivar inputs for a controlled model comparison.
- CO2-on/off, dynamic/fixed phenology and irrigation-constrained/unconstrained comparisons from the reference study or a supported future experiment.
- Bilateral trade and origin-specific crop shocks; historical stocks, trade-policy restrictions, transport constraints and food-versus-feed uses.
- Literature-backed price/demand/supply elasticities and future income/population trajectories for a market-response model.
- Household intake distributions, prices, expenditure and access data to discuss dietary behaviour or deficiency risk.

These data are not required to report our existing conditional screening results. They are required before assigning quantitative blame to markets or claiming a prediction of future consumption.

## Integration status

The research is now integrated in report subsection 13.4 and the results-focused presentation. The earlier 39-row generated comparison and its 29-gap count remain explicitly identified as the original assessment; the supplemental ten partial matches and nineteen remaining gaps are stated separately. The numerical outputs and model parameters were not changed. The report and appendix were compiled and the new slides rendered; scientific calculations and tests were not rerun. No commit or push was made.
