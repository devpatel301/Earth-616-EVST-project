# Elevated-CO2 effects on nutrient concentration in edible crop parts: verified evidence

Companion to `docs/co2_nutrient_effects.csv` (137 rows, one per crop x nutrient x evidence set). Compiled 2026-11-18 for the elevated-CO2 stress test on FAOSTAT FBS 2021-2023 nutrient supply.

Rules used: a value goes in only if species, edible part, nutrient, CO2 treatment and units match. Nonsignificant estimates are recorded as nonsignificant, not as zero. Missing combinations stay missing. Field-pea effects are not transferred to chickpea, lentil or bean. Soybean effects are not transferred to groundnut or rapeseed. Downloaded copies are in the session scratchpad, `papers_co2/`.

## 1. Sources and what was read

| Key | Source | DOI | Read level | Parts read |
|---|---|---|---|---|
| myers2014 | Myers et al. 2014, Nature 510:139-142 | 10.1038/nature13179 | full text (PMC4810679 author manuscript). Published Table 1 and Extended Data (ED) Tables 1-3 were checked against nature.com | main text, Methods, Table 1, ED Tables 1-6 (ED 1-3 compared with the published images) |
| myers2019correction | Author Correction, Nature 574:E14 | 10.1038/s41586-019-1602-8 | full text | whole notice |
| smith2018 | Smith & Myers 2018, Nat. Clim. Change 8:834-839 | 10.1038/s41558-018-0253-3 | abstract and Supplementary Tables S1-S3 (xlsx files open on nature.com). Main text is paywalled and was **not read** | abstract, figure titles, Table S2, Table S3 |
| medek2017 | Medek, Schwartz & Myers 2017, EHP 125:087002 | 10.1289/EHP41 | full text and Supplemental Material | Methods, Table 1, Tables S1-S3, reference list |
| loladze2014 | Loladze 2014, eLife 3:e02245 | 10.7554/eLife.02245 | full text (PMC4034684). Figure 1-source data was not read | Results, Figs 2-6 legends, Methods, Table 3 |
| dietterich2015 | Dietterich et al. 2015, Sci. Data 2:150036 | 10.1038/sdata.2015.36 | full text (PMC4508823) | Background, Methods by crop |
| zhu2018 | Zhu et al. 2018, Sci. Adv. 4:eaaq1012 | 10.1126/sciadv.aaq1012 | full text (PMC5966189) | Results, Methods |
| terhaar2025 | ter Haar, van Bodegom & Scherer 2025, Glob. Change Biol. 31:e70568 | 10.1111/gcb.70568 | full text (PMC12616468) and Zenodo Data S1 and S3 (10.5281/zenodo.17274164) | Methods 2.1-2.3, Results, Table 2, database and results CSVs |
| alhadeethi2019 | Al-Hadeethi et al. 2019, Ecol. Evol. 9:7425-7437 | 10.1002/ece3.5210 | full text (PMC6635941), skimmed | Methods (CO2 classes), Results text. No CSV rows (covers only the Myers crops; CIs only in figures) |
| parvin2019 | Parvin et al. 2019, Crop Pasture Sci. 70:244-253 | 10.1071/CP18421 | published paper: abstract only. Numbers come from the author's PhD thesis, Chapter 8 (parvin2019thesis) | thesis Ch. 8 Methods, Table 8.3, Results |
| parvin2018 | Parvin et al. 2018, Plant Cell Environ. 41:2418-2434 | 10.1111/pce.13360 | full text (accepted manuscript, Univ. Melbourne repository) | Abstract, Results "N concentration and content" |
| saha2015 | Saha et al. 2015, Food Chem. 187:431-436 | 10.1016/j.foodchem.2015.04.116 | abstract only | abstract (PubMed 25977047) |
| hogy2010 | Högy et al. 2010, Agric. Ecosyst. Environ. 139:239-244 | 10.1016/j.agee.2010.08.009 | abstract only (author abstract PDF, Univ. Hohenheim) | abstract |
| jin2019 | Jin, Armstrong & Tang 2019, Sci. Total Environ. 651:2641-2647 | 10.1016/j.scitotenv.2018.10.170 | abstract only | abstract (PubMed 30463119) |
| singh2013 | Singh et al. 2013, Environ. Monit. Assess. 185:6517-6529 | 10.1007/s10661-012-3043-9 | abstract only | abstract (PubMed 23283603) |
| burkey2007 | Burkey et al. 2007, Crop Sci. 47:1488-1497 | 10.2135/cropsci2006.08.0538 | abstract only | abstract (Crossref) |
| bagudam2023 | Bagudam et al. 2023, Acta Physiol. Plant. 45:67 | 10.1007/s11738-023-03553-4 | abstract only | abstract (link.springer.com) |
| soares2019 | Soares et al. 2019, Plants 8:465 | 10.3390/plants8110465 | full text (PMC6918337) | Results, Methods |
| myers2015, smith2017 | Myers et al. 2015 Lancet Glob. Health; Smith, Golden & Myers 2017 GeoHealth | see BibTeX | **not read** | cited only because Smith & Myers' Table S3 names them as sources of composite-group values |

## 2. Myers et al. 2014: original FACE table versus pooled tables

### 2.1 The original experiments (Table 1 and ED Table 1)

> "Here we report findings from meta-analysis of newly acquired data from 143 comparisons of the edible portions of crops grown at ambient and elevated [CO2] from seven different FACE experimental locations in Japan, Australia, and the United States involving six food crops (see Table 1)." (main text, paragraph 4)

> "...forty genotypes were tested over 1 to 6 growing seasons at ambient and elevated [CO2], where the latter was in the range of 546–586 ppm across all seven study sites." (main text, paragraph 4)

> "Ambient [CO2] ranges between 363 and 386 ppm while elevated [CO2] is between 546 and 584 ppm." (Methods, Agricultural Methods)

Table 1 (ambient/elevated ppm):

| Crop | Site and years | Ambient/elevated (ppm) | C3/C4 |
|---|---|---|---|
| Wheat | Australia, Site 1 2007-10 and Site 2 2007-09 | 382/546-550 | C3 |
| Field pea | Australia 2010 | 382/546-550 | C3 legume |
| Rice | Japan, Site 1 2007-08 | 376-379/570-576 | C3 |
| Rice | Japan, Site 2 2010 | 386/584 | C3 |
| Maize | USA 2008 | 385/550 | C4 |
| Soybean | USA 2001, 2002, 2004, 2006-08 | 372-385/550 | C3 legume |
| Sorghum | USA 1998-99 | 363-373/556-579 | C4 |

All experiments are FACE. ED Table 1 (manuscript "Table E1") gives % change with 95% CI and P for Zn, Fe, protein and phytate. It uses **only these experiments** and is the source of every primary value for wheat, rice, maize and soybean.

| Crop (N pairs) | Zn % (95% CI), P | Fe % (95% CI), P | Protein % (95% CI), P | Phytate % (95% CI), P |
|---|---|---|---|---|
| Wheat (64) | -9.3 (-12.7, -5.9), <.0001 | -5.1 (-6.5, -3.7), <.0001 | -6.3 (-7.5, -5.2), <.0001 | -4.2 (-7.5, -0.8), 0.009 |
| Rice (31) | -3.3 (-5.0, -1.7), <.0001 | -5.2 (-7.6, -2.9), <.0001 | -7.8 (-8.9, -6.8), <.0001 | 1.2 (-4.6, 7.4), 0.697 |
| Field pea (10) | -6.8 (-9.8, -3.8), 0.002 | -4.1 (-6.7, -1.4), 0.003 | -2.1 (-4.0, -0.1), 0.039 | -5.8 (-11.5, 0.1), 0.055 |
| Soybean (25) | -5.1 (-6.4, -3.9), <.0001 | -4.1 (-5.8, -2.5), <.0001 | 0.5 (-0.4, 1.3), 0.267 | -1.3 (-3.7, 1.2), 0.303 |
| Maize (4) | -5.2 (-10.7, 0.6), 0.077 | -5.8 (-10.9, -0.3), 0.038 | -4.6 (-13.0, 4.5), 0.312 | -6.1 (-15.0, 3.7), 0.215 |
| Sorghum (4) | -1.3 (-6.2, 3.8), 0.603 | 1.6 (-5.8, 9.7), 0.674 | 0.0 (-4.9, 5.2), 0.993 | 12.8 (-15.8, 51.1), 0.418 |

Supporting quotes:
- "wheat grains grown at elevated [CO2] have 9.3% (95% CI: −12.7, −5.9) lower zinc and 5.1% (95% CI: −6.5, −3.7) lower iron ... a 6.3% (95% CI: −7.5, −5.2) decrease in wheat grains and a 7.8% (95% CI: −8.9, −6.8) decrease in rice grains." (main text, Results)
- "Phytate decreased significantly at elevated [CO2] only in wheat (P < 0.01)." (main text)
- "Protein values are based on measurement of nitrogen and conversion to protein per the equation below where k=5.36" (Methods, Minerals Method)
- "The global [CO2] in the atmosphere is expected to reach 550 ppm in the next 40–60 years" (main text)

Crops and nutrients present: wheat, rice, field pea, soybean, maize and sorghum, each with Zn, Fe, protein and phytate (ED Table 1). ED Table 4 adds Mn, Mg, Cu, Ca, S, K, B and P for all crops except wheat. There is **no** chickpea, lentil, Phaseolus bean, groundnut or rapeseed, and **no** energy, fat or oil data.

### 2.2 Pooled tables (do not confuse with ED Table 1)

> "In addition to our own observations, we obtained data from ten of eleven previously published studies investigating nutrient changes in the edible portion of food crops (Table E6) and combined these data with our own observations in a larger meta-analysis. Analysis of our results combined with previously published FACE data (Table E2), or combined with previously published data from both FACE and chamber experiments (Table E3), is consistent with the results obtained using only our new data." (main text)

- **ED Table 2**: own data plus published FACE studies 3, 4, 6 and 7 of ED Table 6. Barley and potato are added. Wheat changes to N=70 (Zn -8.8, Fe -5.5, protein -6.5) and rice to N=32 (Zn -3.1, Fe -4.9, protein -8.0). Field pea, soybean, maize and sorghum rows are identical to ED Table 1. **Smith & Myers 2018 use this table for Zn and Fe.**
- **ED Table 3**: own data plus FACE, open-top chamber, temperature-gradient-tunnel and growth-chamber studies 1-10. Wheat N=78 (Zn -9.1, Fe -5.9, protein -7.2). Soybean N=28 (Zn -5.0, Fe -5.2, protein 0.1, P=0.865). Sorghum N=7 (Fe +33.8, n.s.). The pooled tables do not report CO2 levels for the added studies.
- **ED Table 4** repeats the ED Table 1 values with more elements. It gives field-pea Zn and Fe P values of "<.0001", while ED Table 1 gives 0.002 and 0.003. This is an internal inconsistency in the paper. The CSV uses ED Table 1.

### 2.3 Discrepancies noted (not resolved)
- Elevated CO2 maximum: 586 ppm in the main text and Dietterich 2015, but 584 ppm in Methods and Table 1.
- Field pea cultivars: 4 in the manuscript text and manuscript Table 1, but 5 in the published Table 1 and in Dietterich 2015 ("five cultivars (Bohatyr, Kaspa, OZP0601, OZP0902, and Sturt)").
- The text says "143 comparisons", but the ED Table 1 N values sum to 138.
- Dietterich 2015 gives ambient as 364-386 ppm; Myers Methods gives 363-386 ppm. Dietterich also says sorghum CO2 was elevated "during both day and night" and rice "by approximately 200 ppm".
- The 2019 Author Correction only adds four missing Fernando et al. citations (AGFACE wheat): "The original Letter has not been corrected." No numbers changed.

### 2.4 Check of the repo's `MYERS_BENCHMARKS` (code/config.py)
All 12 values (wheat, rice, soybean and maize x Zn, Fe and protein) and all significance flags **match ED Table 1 exactly**. They come from the original-experiment table, not a pooled table. Nothing needs correcting. Gaps in the dict:
- No 95% CIs and no table locator.
- No phytate.
- Maize Zn is correctly flagged n.s. (P=0.077), but Smith & Myers treated it as an effect under their p<0.1 rule.
- The Smith & Myers 2018 values differ: wheat Zn -8.8 and Fe -5.5, rice Zn -3.1 and Fe -4.9 (from ED Table 2), and Medek protein values. These must not be mixed with the dict.

## 3. Smith & Myers 2018: inputs and assumptions

> "Atmospheric CO2 is on pace to surpass 550 ppm in the next 30–80 years. Many food crops grown under 550 ppm have protein, iron and zinc contents that are reduced by 3–17% compared with current conditions." ... "assuming constant diets and excluding other climate impacts on food production" ... "(assuming 2050 population and CO2 projections)" (Abstract). Fig. 2 title: "Risk of inadequate nutrient intake from elevated atmospheric CO2 concentrations of 550 ppm."

Supplementary Table S3 ("Percentage declines in nutritional content of each food (with 95% confidence intervals)") contains three blocks:
- **Zinc and iron** (source "a" = Myers 2014): the values equal **ED Table 2** (FACE pooled), not ED Table 1. Examples: wheat Zn -8.8 (N=70) and Fe -5.5; rice -3.1 and -4.9; soybean -5.1 and -4.1; maize -5.2 (P=0.077) and -5.8. The column header is "Significant difference (p<0.1), included in our analysis". Maize Zn is ticked as included. Sorghum and potato are not.
- **Phytate**: wheat only, -4.2 (-7.5, -0.8).
- **Protein** (source "c" = Medek 2017): wheat -7.78, rice -7.61, chickpea -13.47 and barley, potato and C3-vegetable rows are included. Maize +3.08, peas -1.69, beans -4.58, soy -0.49 and rapeseed/mustard +0.92 are listed but **not** included because they are nonsignificant.
- **Crops without data**: Table S2 assigns FAOSTAT items to composite groups. "C3 legumes" covers Beans, Chick peas, Lentils, Pigeon peas, Groundnuts (Shelled Eq) and **Groundnut Oil**. "C3 plants" covers Rape and Mustardseed, **Rape and Mustard Oil**, Sunflowerseed and other items. The composite values are:
  - Zn: C3 legumes -5.30 (-8.69, -4.02) and C3 plants -7.91 (-12.45, -2.14), from source "b" = Myers et al. 2015.
  - Fe: C3 legumes -4.8 (-7.7, -2.1) and C3 grains -5.7 (-10.3, -3.3), from source "d" = Smith, Golden & Myers 2017.
  - Protein: "Pulses, legumes" -3.51 and "Oilcrops" -0.78, both n.s. and not included.

  Our rules forbid transferring a composite proxy to a crop, so those rows are labelled "do not use". The main text, which may say how oils were treated, was not accessible.

## 4. Crops not covered by Myers 2014

**Chickpea (*Cicer arietinum*).**
- Saha et al. 2015, open-top chamber (OTC), New Delhi. Abstract only: "Experiments were conducted in open-top chambers ... Increase in carbohydrates and reduction in protein made the grains more carbonaceous (higher C:N) under E-CO2. Among other mineral nutrients, K, Ca and Zn concentrations decreased, while P, Mg, Cu, Fe, Mn and B concentrations did not change."
- Magnitudes appear only in the ter Haar 2025 Data S1 extraction (OTC, ~389-391 vs 580 ppm): Zn -41.0% and -36.0%, Fe -3.5% and -9.3%, N -10.9% and -8.4%. These were not verified against the Saha full text.
- ter Haar main text: "Chickpeas (Cicer arietinum) have the largest powerful and significant mean change of a single nutrient (zinc: −37.5%)". This is the Saha data rescaled to 350->550 ppm.
- Medek 2017 Table 1 gives chickpea protein -13.47 (-21.36, -5.58), n=4. This is the only pooled chickpea protein estimate.

**Lentil (*Lens culinaris*).**
- Parvin et al. 2019, AGFACE, Horsham, ~400 vs ~550 ppm. Published abstract: "Elevated [CO2] decreased Fe, Zn, P and S concentrations in both crops; however, the relative decrease was greater under dry (20–25%) than wet (4–10%) growing conditions."
- Thesis Table 8.3 (n=8: 2 genotypes x 4 rings), mg/kg means:
  - Zn: 68.03 vs 49.46 in the dry 2015 season (-27.3%) and 32.63 vs 30.61 in the wet 2016 season (-6.2%).
  - Fe: 89.94 vs 71.74 dry (-20.2%) and 62.13 vs 59.39 wet (-4.4%).
  - CO2 main effect P<0.001. CO2 x season interaction P=0.020 for Zn and 0.048 for Fe.
- The percentages are our arithmetic from the table means. They match the ter Haar Data S1 extraction of the published paper (-27.30, -6.19, -20.24 and -4.41%), which suggests the published table carries the same means.
- The thesis text says the dry-season decrease was "20-24%", but Zn computes to -27.3%. The CSV reports the computed value.
- Grain N (Parvin et al. 2018): "Elevated [CO2] depressed grain [N] by 4% in the dry season and increased it by 3% in the high rainfall season (significant year × [CO2] interaction, p = 0.048)".

**Common bean (*Phaseolus vulgaris*).**
- No field (FACE or OTC) seed-quality study was found.
- Soares et al. 2019 used a growth chamber with nutrient-film hydroponics at 400 vs 800 ppm (18 varieties): "eCO2 increased seed protein concentration in beans" (+6.0%, p<0.0001). "Lipid concentration was not affected by eCO2 in either legume species." Mn, Fe and K decreased, and Zn was not changed. The mean Fe change appears only in Fig. 3.
- Medek's "Beans" group (n=7, -4.58, n.s.) has a reference list that also includes mung bean (*Vigna radiata*) and faba bean (*Vicia faba*) studies, so its species match cannot be confirmed.
- ter Haar's *Phaseolus* seed rows rest only on two growth-chamber studies at 800 ppm.

**Groundnut (*Arachis hypogaea*).**
- Burkey et al. 2007, OTC, ambient 375 ppm plus ~173 or ~355 ppm: "No treatment effects were observed on the protein and oil contents of seeds, but there were changes in fatty acid composition."
- Bagudam et al. 2023, OTC, 380 vs 550 and 700 ppm: "Kernel oil (6.54% and 2.98%) and protein content (7.07% and 4.56%) declined at 550 and 700 ppm ... kernel iron and manganese content remained unaffected". The abstract gives no Zn and no P values.
- The two OTC studies disagree, so no primary protein or fat value is set.

**Rapeseed / mustard (*Brassica napus*, *B. juncea*).**
- Högy et al. 2010, FACE, 388 vs 494 ppm: "Total protein concentration declined significantly by 4.6%". The abstract also says "zinc and manganese tended to decrease (0.1 ≥ P > 0.05)", "Amino acids on a per protein basis and total oil concentrations were unaffected", and "energy contents per dry weight were identical in both CO2 treatments".
- Jin et al. 2019, FACE, 390 vs 550 ppm, seven years, wheat-field pea-canola rotation: "the concentrations of N, P and Zn decreased by 6%, 5% and 10% under eCO2, respectively, irrespective of soil, crop and year ... The concentrations of K, Fe, Mn and Cu were not affected by eCO2 in any crop".
- Singh et al. 2013, *B. juncea* OTC, 550±50 ppm (one sentence of the abstract says 500±50): "Elevated CO2, however, decreased protein, calcium, zinc, iron, magnesium, and sulfur content in seed as compared to the nonfiltered control". The abstract gives no magnitudes. ter Haar's database lists this study's elevated CO2 as 890 ppm, which conflicts with the abstract.
- Medek "Rapeseed/mustard seed" protein: +0.92 (-8.9, 10.74), n=5, n.s.

**Loladze 2014** (all crops). The edible-tissue dataset averages 373 vs 674 ppm, and the FACE subset 376 vs 560 ppm. The main text gives no crop-specific results for our five non-Myers crops: "results for chromium (Cr) or the bean ionome are not shown here due to low power". Table 3 lists rapeseed, mustard (Singh 2013) and oilseed rape (Högy 2010) entries but no chickpea, lentil or groundnut. Loladze is used only as context.

## 5. Energy (kcal), fat/oil and extracted vegetable oils
- **No source gives a change in metabolisable food energy (kcal) for any of the nine crops.**
  - Högy 2010 reports unchanged gross calorific "energy contents per dry weight" of rapeseed seed. That is a bioenergy measure, not food kcal.
  - Saha 2015 (chickpea) and Loladze 2014 report higher carbohydrate (total non-structural carbohydrate, TNC) only qualitatively.
  - Medek 2017 and Smith & Myers 2018 hold diets and energy constant.
  - ter Haar's "food will become more caloric" (abstract) is not a measured kcal effect.
- **Seed fat/oil concentration**:
  - Rapeseed: unchanged under FACE (Högy 2010).
  - Groundnut: OTC results conflict (Burkey: no effect; Bagudam: -6.54% at 550 ppm).
  - Soybean and bean: no change, but only in a growth chamber at 800 ppm (Soares 2019).
  - No data for wheat, rice, maize, chickpea or lentil.
- **Extracted oils** (FBS "Rape and Mustard Oil", "Groundnut Oil", "Soyabean Oil"): no source quantifies an eCO2 effect on the energy or fat content of extracted oil. Högy 2010 and Burkey 2007 report only shifts in fatty-acid composition. Seed mineral or protein effects must not be applied to oils. The Smith & Myers Table S2 groupings include oils, but how they were treated is not verifiable without the main text.

## 6. Dose-response (effect per ppm)
These sources do **not** support an empirical per-ppm effect for our crops:
- Myers 2014 used one elevated level (~546-586 ppm).
- Smith & Myers 2018 model a single 550 ppm scenario (2050).
- Medek 2017: "Because there was no reliable dose-dependent decrease in protein content with degree of CO2 elevation, we used meta-analysis to derive average response ratios ... where eCO2 was in the range of 500–700 ppm." Linear slopes were significant only for maize, peas and mustard seed (Table S2), and the authors did not use them.
- ter Haar 2025 **assumes** linearity to rescale every study to 350->550 ppm ("This method assumes that response heterogeneity is driven mainly by the variation in CO2 levels").
- Zhu 2018 says decline "can be reasonably ... approximated as linear (for example, protein)" (citing another study) but does not estimate a slope.

Any scaling of these % changes to a CO2 level other than ~550 ppm is therefore our own assumption. The Myers values describe ~380 -> ~550 ppm. ter Haar values describe 350 -> 550 ppm, a larger step.

## 7. Primary values selected (one per crop-nutrient where defensible)

| Crop | Zinc | Iron | Protein | Fat | kcal |
|---|---|---|---|---|---|
| Wheat | -9.3 (-12.7, -5.9) ED T1 | -5.1 (-6.5, -3.7) ED T1 | -6.3 (-7.5, -5.2) ED T1 | none | none |
| Rice | -3.3 (-5.0, -1.7) ED T1 | -5.2 (-7.6, -2.9) ED T1 | -7.8 (-8.9, -6.8) ED T1 | none | none |
| Maize | -5.2 (-10.7, 0.6) **n.s.** ED T1 | -5.8 (-10.9, -0.3) ED T1 | -4.6 (-13.0, 4.5) **n.s.** ED T1 | none | none |
| Soybean | -5.1 (-6.4, -3.9) ED T1 | -4.1 (-5.8, -2.5) ED T1 | +0.5 (-0.4, 1.3) **n.s.** ED T1 | none (chamber only) | none |
| Chickpea | none (single OTC study; sensitivity -37.5% ter Haar) | n.s., no size (Saha 2015 abstract) | -13.47 (-21.36, -5.58) Medek T1 | none | none |
| Lentil | -6.2, wet season (Parvin; dry -27.3 as sensitivity) | -4.4, wet season (Parvin; dry -20.2) | none (-4% dry / +3% wet) | none | none |
| Bean | none (chamber only) | none (chamber only) | none (chamber +6.0%; Medek mixed "Beans" n.s.) | none | none |
| Groundnut | none (only ter Haar rescaled, n.s.) | n.s., no size (Bagudam 2023) | none (OTC conflict) | none (OTC conflict) | none |
| Rapeseed | -10 (FACE, pooled across 3 crops; Jin 2019 abstract) | n.s., no size (Jin 2019) | -4.6 (FACE 494 ppm; Högy 2010) | n.s., no size (Högy 2010) | none (gross energy unchanged, Högy) |

"ED T1" = Myers 2014 Extended Data Table 1. Rationale for the non-Myers choices:
- **Lentil**: the wet-season value is primary because it is the smaller, conservative FACE effect. The dry 2015 season (128 mm vs 274 mm long-term average) drought-amplified the loss, so it is kept as an upper-bound sensitivity.
- **Rapeseed protein**: Högy's 494 ppm treatment probably understates a 550 ppm effect. No rescaling was applied.
- **"n.s., no size" rows**: these are marked primary to record "no detectable change". The effect size is not available and **must not be imputed as 0** unless the model states that choice explicitly.

## 8. Coverage matrix (best available direct evidence)

S = covered, significant effect; NS = covered, nonsignificant; NC = not covered; † = only controlled-environment (800 ppm) evidence; ‡ = conflicting or single-study evidence, no primary.

| Crop | kcal | protein | fat | zinc | iron |
|---|---|---|---|---|---|
| Wheat | NC | S | NC | S | S |
| Rice | NC | S | NC | S | S |
| Maize | NC | NS | NC | NS (P=0.077) | S |
| Soybean | NC | NS | NS† | S | S |
| Chickpea | NC (carbohydrate up, qualitative) | S (n=4) | NC | S‡ (single OTC) | NS |
| Lentil | NC | S/NS by season‡ (-4%/+3%) | NC | S | S |
| Bean | NC | S† (+6%) | NS† | NS† | S† |
| Groundnut | NC | ‡ (NS vs -7.07%) | ‡ (NS vs -6.54%) | NS (ter Haar rescaled only) | NS |
| Rapeseed | NS (gross energy only) | S | NS | S | NS |

## 9. Gaps
- No source estimates eCO2 effects on food kcal for any crop, or on the energy or fat content of extracted vegetable oils.
- Bean has no field (FACE or OTC) evidence.
- Groundnut OTC evidence conflicts.
- Chickpea Zn and Fe rest on one OTC study whose magnitudes were seen only via a secondary dataset.
- Lentil data come from one FACE site whose effect depends strongly on season.
- Fat in cereals, chickpea and lentil is not covered.
- Maize has only 4 pairs from one site and year.
- No crop-specific dose-response is available.
- Every effect is CO2-only. Interactions with warming or drought are not represented, except in the Parvin seasons.

## 10. BibTeX
These entries were generated from Crossref metadata (api.crossref.org/works/<DOI>) on 2026-11-18. Normalisation: "CO 2" was rewritten as {CO2} and Unicode hyphens as "-". `terhaar2025data` was verified on DataCite because Zenodo DOIs are not in Crossref. `parvin2019thesis` has no DOI and could not be Crossref-verified.

```bibtex
@article{myers2014,
  author = {Myers, Samuel S. and Zanobetti, Antonella and Kloog, Itai and Huybers, Peter and Leakey, Andrew D. B. and Bloom, Arnold J. and Carlisle, Eli and Dietterich, Lee H. and Fitzgerald, Glenn and Hasegawa, Toshihiro and Holbrook, N. Michele and Nelson, Randall L. and Ottman, Michael J. and Raboy, Victor and Sakai, Hidemitsu and Sartor, Karla A. and Schwartz, Joel and Seneweera, Saman and Tausz, Michael and Usui, Yasuhiro},
  title = {Increasing {CO2} threatens human nutrition},
  journal = {Nature}, volume = {510}, number = {7503}, pages = {139--142}, year = {2014}, doi = {10.1038/nature13179}}
@article{myers2019correction,
  author = {Myers, Samuel S. and Zanobetti, Antonella and Kloog, Itai and Huybers, Peter and Leakey, Andrew D. B. and Bloom, Arnold J. and Carlisle, Eli and Dietterich, Lee H. and Fitzgerald, Glenn and Hasegawa, Toshihiro and Holbrook, N. Michele and Nelson, Randall L. and Ottman, Michael J. and Raboy, Victor and Sakai, Hidemitsu and Sartor, Karla A. and Schwartz, Joel and Seneweera, Saman and Tausz, Michael and Usui, Yasuhiro},
  title = {Author Correction: Increasing {CO2} threatens human nutrition},
  journal = {Nature}, volume = {574}, number = {7778}, pages = {E14}, year = {2019}, doi = {10.1038/s41586-019-1602-8}}
@article{smith2018,
  author = {Smith, Matthew R. and Myers, Samuel S.},
  title = {Impact of anthropogenic {CO2} emissions on global human nutrition},
  journal = {Nature Climate Change}, volume = {8}, number = {9}, pages = {834--839}, year = {2018}, doi = {10.1038/s41558-018-0253-3}}
@article{medek2017,
  author = {Medek, Danielle E. and Schwartz, Joel and Myers, Samuel S.},
  title = {Estimated Effects of Future Atmospheric {CO2} Concentrations on Protein Intake and the Risk of Protein Deficiency by Country and Region},
  journal = {Environmental Health Perspectives}, volume = {125}, number = {8}, pages = {087002}, year = {2017}, doi = {10.1289/EHP41}}
@article{myers2015,
  author = {Myers, Samuel S. and Wessells, K. Ryan and Kloog, Itai and Zanobetti, Antonella and Schwartz, Joel},
  title = {Effect of increased concentrations of atmospheric carbon dioxide on the global threat of zinc deficiency: a modelling study},
  journal = {The Lancet Global Health}, volume = {3}, number = {10}, pages = {e639--e645}, year = {2015}, doi = {10.1016/S2214-109X(15)00093-5}}
@article{smith2017,
  author = {Smith, M. R. and Golden, C. D. and Myers, S. S.},
  title = {Potential rise in iron deficiency due to future anthropogenic carbon dioxide emissions},
  journal = {GeoHealth}, volume = {1}, number = {6}, pages = {248--257}, year = {2017}, doi = {10.1002/2016GH000018}}
@article{loladze2014,
  author = {Loladze, Irakli},
  title = {Hidden shift of the ionome of plants exposed to elevated {CO2} depletes minerals at the base of human nutrition},
  journal = {eLife}, volume = {3}, pages = {e02245}, year = {2014}, doi = {10.7554/eLife.02245}}
@article{dietterich2015,
  author = {Dietterich, Lee H. and Zanobetti, Antonella and Kloog, Itai and Huybers, Peter and Leakey, Andrew D. B. and Bloom, Arnold J. and Carlisle, Eli and Fernando, Nimesha and Fitzgerald, Glenn and Hasegawa, Toshihiro and Holbrook, N. Michele and Nelson, Randall L. and Norton, Robert and Ottman, Michael J. and Raboy, Victor and Sakai, Hidemitsu and Sartor, Karla A. and Schwartz, Joel and Seneweera, Saman and Usui, Yasuhiro and Yoshinaga, Satoshi and Myers, Samuel S.},
  title = {Impacts of elevated atmospheric {CO2} on nutrient content of important food crops},
  journal = {Scientific Data}, volume = {2}, number = {1}, pages = {150036}, year = {2015}, doi = {10.1038/sdata.2015.36}}
@article{zhu2018,
  author = {Zhu, Chunwu and Kobayashi, Kazuhiko and Loladze, Irakli and Zhu, Jianguo and Jiang, Qian and Xu, Xi and Liu, Gang and Seneweera, Saman and Ebi, Kristie L. and Drewnowski, Adam and Fukagawa, Naomi K. and Ziska, Lewis H.},
  title = {Carbon dioxide ({CO2}) levels this century will alter the protein, micronutrients, and vitamin content of rice grains with potential health consequences for the poorest rice-dependent countries},
  journal = {Science Advances}, volume = {4}, number = {5}, pages = {eaaq1012}, year = {2018}, doi = {10.1126/sciadv.aaq1012}}
@article{alhadeethi2019,
  author = {Al-Hadeethi, Ikhlas and Li, Yan and Odhafa, Abdul Kareem H. and Al-Hadeethi, Hanan and Seneweera, Saman and Lam, Shu K.},
  title = {Assessment of grain quality in terms of functional group response to elevated [{CO2}], water, and nitrogen using a meta-analysis: Grain protein, zinc, and iron under future climate},
  journal = {Ecology and Evolution}, volume = {9}, number = {13}, pages = {7425--7437}, year = {2019}, doi = {10.1002/ece3.5210}}
@article{terhaar2025,
  author = {ter Haar, Sterre F. and van Bodegom, Peter M. and Scherer, Laura},
  title = {{CO2} Rise Directly Impairs Crop Nutritional Quality},
  journal = {Global Change Biology}, volume = {31}, number = {11}, pages = {e70568}, year = {2025}, doi = {10.1111/gcb.70568}}
@misc{terhaar2025data,
  author = {ter Haar, Sterre Frédérique and van Bodegom, Peter and Scherer, Laura},
  title = {{CO2} Rise Directly Impairs Crop Nutritional Quality (data and code, version 1.0.0)},
  publisher = {Zenodo}, year = {2025}, doi = {10.5281/zenodo.17274164}}
@article{parvin2019,
  author = {Parvin, Shahnaj and Uddin, Shihab and Tausz-Posch, Sabine and Armstrong, Roger and Fitzgerald, Glenn and Tausz, Michael},
  title = {Grain mineral quality of dryland legumes as affected by elevated {CO2} and drought: a {FACE} study on lentil (\textit{Lens culinaris}) and faba bean (\textit{Vicia faba})},
  journal = {Crop \& Pasture Science}, volume = {70}, number = {3}, pages = {244--253}, year = {2019}, doi = {10.1071/CP18421}}
@phdthesis{parvin2019thesis,
  author = {Parvin, Shahnaj},
  title = {Biochemical and physiological mechanisms of legume nitrogen fixation under higher atmospheric {CO2} concentrations},
  school = {The University of Melbourne}, year = {2019}, month = mar,
  note = {Chapter 8. Retrieved from Minerva Access, https://rest.mars-prod.its.unimelb.edu.au/server/api/core/bitstreams/7dd9a24a-a658-5181-aa8d-8cfa89c3d02f/content}}
@article{parvin2018,
  author = {Parvin, Shahnaj and Uddin, Shihab and Bourgault, Maryse and Roessner, Ute and Tausz-Posch, Sabine and Armstrong, Roger and O'Leary, Garry and Fitzgerald, Glenn and Tausz, Michael},
  title = {Water availability moderates {N2} fixation benefit from elevated [{CO2}]: A 2-year free-air {CO2} enrichment study on lentil (\textit{Lens culinaris} {MEDIK}.) in a water limited agroecosystem},
  journal = {Plant, Cell \& Environment}, volume = {41}, number = {10}, pages = {2418--2434}, year = {2018}, doi = {10.1111/pce.13360}}
@article{saha2015,
  author = {Saha, Saurav and Chakraborty, Debashis and Sehgal, Vinay K. and Pal, Madan},
  title = {Potential impact of rising atmospheric {CO2} on quality of grains in chickpea (\textit{Cicer arietinum} {L}.)},
  journal = {Food Chemistry}, volume = {187}, pages = {431--436}, year = {2015}, doi = {10.1016/j.foodchem.2015.04.116}}
@article{hogy2010,
  author = {Högy, Petra and Franzaring, Jürgen and Schwadorf, Klaus and Breuer, Jörn and Schütze, Wolfgang and Fangmeier, Andreas},
  title = {Effects of free-air {CO2} enrichment on energy traits and seed quality of oilseed rape},
  journal = {Agriculture, Ecosystems \& Environment}, volume = {139}, number = {1-2}, pages = {239--244}, year = {2010}, doi = {10.1016/j.agee.2010.08.009}}
@article{jin2019,
  author = {Jin, Jian and Armstrong, Roger and Tang, Caixian},
  title = {Impact of elevated {CO2} on grain nutrient concentration varies with crops and soils -- A long-term {FACE} study},
  journal = {Science of The Total Environment}, volume = {651}, pages = {2641--2647}, year = {2019}, doi = {10.1016/j.scitotenv.2018.10.170}}
@article{singh2013,
  author = {Singh, Satyavan and Bhatia, Arti and Tomer, Ritu and Kumar, Vinod and Singh, B. and Singh, S. D.},
  title = {Synergistic action of tropospheric ozone and carbon dioxide on yield and nutritional quality of {Indian} mustard (\textit{Brassica juncea} ({L}.) {Czern}.)},
  journal = {Environmental Monitoring and Assessment}, volume = {185}, number = {8}, pages = {6517--6529}, year = {2013}, doi = {10.1007/s10661-012-3043-9}}
@article{burkey2007,
  author = {Burkey, Kent O. and Booker, Fitzgerald L. and Pursley, Walter A. and Heagle, Allen S.},
  title = {Elevated Carbon Dioxide and Ozone Effects on Peanut: {II}. Seed Yield and Quality},
  journal = {Crop Science}, volume = {47}, number = {4}, pages = {1488--1497}, year = {2007}, doi = {10.2135/cropsci2006.08.0538}}
@article{bagudam2023,
  author = {Bagudam, Rachana and Kancherla, Eswari and Abady, Seltene and Wankhade, Ankush Purushottam and Deshmukh, Dnyaneshwar Bandu and Vemula, AnilKumar and Kadirimangalam, Sai Rekha and Kumar, S. Sudheer and Reddy, S. Narender and Pasupuleti, Janila},
  title = {Influence of elevated {CO2} on growth, yield, haulm, and kernel quality of groundnut (\textit{Arachis hypogaea} {L}.)},
  journal = {Acta Physiologiae Plantarum}, volume = {45}, number = {5}, pages = {67}, year = {2023}, doi = {10.1007/s11738-023-03553-4}}
@article{soares2019,
  author = {Soares, José and Deuchande, Teresa and Valente, Luísa M. P. and Pintado, Manuela and Vasconcelos, Marta W.},
  title = {Growth and Nutritional Responses of Bean and Soybean Genotypes to Elevated {CO2} in a Controlled Environment},
  journal = {Plants}, volume = {8}, number = {11}, pages = {465}, year = {2019}, doi = {10.3390/plants8110465}}
```
