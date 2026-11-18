# Future climate-impact literature: verified sources for the nine crops

Compiled 18 Nov 2026 for *Climate Change and Nutritional Security: Which Crops Are Most Vulnerable?* (research extension 1).
Companion files: `docs/evidence/future_literature_sources.csv` (39 rows, one per study x crop x geography finding) and `docs/evidence/future_literature_assessment.csv` (our verdict per row plus one `COVERAGE-<crop>` row per crop).

How to read this file:
- **Verification.** Every DOI was resolved against the Crossref API (`api.crossref.org/works/<DOI>`) on 18 Nov 2026. Title, journal, volume, issue, pages and author list in the BibTeX below come from Crossref.
- **Read level.** "Full paper" means the article body was read: the publisher HTML, PMC/Europe PMC, the accepted manuscript or proof in an institutional repository, or an open-access PDF. "Abstract only" means only the abstract was available (paywall, bot check or unreachable repository). Abstract-only rows give headline directions only, and their scenario fields say "not stated in abstract" where that is the case.
- **Quotes.** Quotes are verbatim. "[reassembled]" marks text rejoined across PDF line breaks or hyphenation, with no words changed; "[…]" marks an omission. Page numbers refer to the version read (for example "ms p." = accepted-manuscript PDF page, "proof p." = author-proof PDF page).
- **Comparison rule.** Only directions, mechanisms and conclusions are compared with our results, never magnitudes on different metrics. Our setup excludes CO2 fertilisation, adaptation, irrigation change and area change, and uses one GCM (MRI-ESM2-0, SSP2-4.5, 2041-2060) on monthly data. Most studies below differ on at least one of these, as recorded in the CSV column `key_differences_from_our_setup`.
- Downloaded copies and text extracts are in the session scratchpad (`papers_future\`). They are working copies, not project inputs.

## 1. Studies, verification and evidence

### Zhao et al. 2017 (rows F01 wheat, F07 rice, F11 maize, F17 soybean)
Zhao, C., Liu, B., Piao, S., et al. (2017). Temperature increase reduces global yields of major crops in four independent estimates. *PNAS* 114(35):9326-9331. https://doi.org/10.1073/pnas.1701762114
Verified: Crossref. Read: **full paper** (main text, PMC5584412, re-read 18 Nov; SI not read). Already in refs.bib as `zhao2017`.
> "Without CO2 fertilization, effective adaptation, and genetic improvement, each degree-Celsius increase in global mean temperature would, on average, reduce global yields of wheat by 6.0%, rice by 3.2%, maize by 7.4%, and soybean by 3.1%." (Abstract)

> "Estimated wheat yield losses for the United States (−5.5 ± 4.4% per degree Celsius) and France (−6.0 ± 4.2% per degree Celsius) are similar to the global average, while those for India (−9.1 ± 5.4% per degree Celsius) and Russia (−7.8 ± 6.3% per degree Celsius) are more vulnerable to temperature increase." (Results, wheat; Fig. 3A)

> "For India, however, estimates from all methods predict large temperature impacts, with a multimethod average of −6.6 ± 3.8% per degree Celsius." (Results, rice; Fig. 3B)

> "The global average reduction in soybean yield is 3.1% per degree-Celsius rise (Fig. 2A), but the estimates are not statistically significant due to large uncertainties in each method (the 95% CIs go through zero)." (Results, soybean)

> "The simulations were carried out under a scenario of constant CO2 concentration (380 ppm in 2000) and full irrigation" […] "Temperature impact values were calculated from yield changes between 2029 and 2058 (+2 °C of global mean temperature) and 1981–2010 (baseline), which were then halved" (Methods, gridded simulations)

### Jägermeyr et al. 2021 (rows F02 wheat, F08 rice, F12 maize, F18 soybean)
Jägermeyr, J., Müller, C., Ruane, A. C., et al. (2021). Climate impacts on global agriculture emerge earlier in new generation of climate and crop models. *Nature Food* 2(11):873-885. https://doi.org/10.1038/s43016-021-00400-y
Verified: Crossref. Read: **full paper** (accepted author proof, IIASA repository https://pure.iiasa.ac.at/id/eprint/17614/). Already in refs.bib as `jagermeyr2021`.
> "Mean end-of-century maize productivity is shifted from +5% to −6% (SSP126) and from +1% to −24% (SSP585)—explained by warmer climate projections and improved crop model sensitivities. In contrast, wheat shows stronger gains (+9% shifted to +18%, SSP585), linked to higher CO2 concentrations and expanded high-latitude gains." [reassembled] (Abstract, proof p.1)

> "Maize projections show spatially homogeneous losses especially among main growing regions in North America, Mexico, West Africa, Central Asia and China, where crop model agreement is high (Fig. 3c)." […] "Wheat shows distinct geographic gradients with losses in spring wheat regions in Mexico, the southern United States, South America and South Asia, supported by good model agreement. Sizeable wheat gains are projected by many models for the North China Plains, Australia, Central Asia, the Middle East and for the winter-wheat-growing regions in the northern United States and Canada (Fig. 3d)." [reassembled] ('Regional patterns of yield change', proof p.6)

> "Soybean shows the greatest losses in the main-producer regions—the United States, Brazil and Southeast Asia—paired with large gains across parts of China and generally higher latitudes (Supplementary Fig. 3). Major declines in rice yields are simulated in Central Asia, and gains in South Asia, northeastern China and South America." [reassembled] (proof p.6)

> "Generally, the least pessimistic crop impacts are found with MRI-ESM2 (Fig. 1)." [reassembled] (proof p.6). **This bears directly on our design:** MRI-ESM2-0 is our only GCM, so our future losses are probably at the mild end of a CMIP6 ensemble.

> "the ensemble median rainfed response is 19% for maize, 33% for wheat, 48% for soybean and 37% for rice by the year 2099" [reassembled] (CO2 effect, proof p.6). Baseline 1983-2013, end-century 2069-2099 (Fig. 1 caption).

### Deryng et al. 2014 (rows F03 wheat, F13 maize, F19 soybean)
Deryng, D., Conway, D., Ramankutty, N., Price, J., Warren, R. (2014). Global crop yield response to extreme heat stress under multiple climate change futures. *Environmental Research Letters* 9(3):034011. https://doi.org/10.1088/1748-9326/9/3/034011
Verified: Crossref. Read: **full paper** (IOP open-access PDF, re-downloaded 18 Nov). Already in refs.bib as `deryng2014`. **Shared input:** our T_crit/T_lim for wheat, maize and soybean come from its Table A.1, and the rapeseed slope is borrowed from its spring-wheat span. Agreement with Deryng is therefore not independent validation.
> "Our results project maize to face progressively worse impacts under a range of RCPs but spring wheat and soybean to improve globally through to the 2080s due to CO2 fertilization effects, even though parts of the tropic and sub-tropic regions could face substantial yield declines." (Abstract, p.1)

> "When CO2 fertilization effects are excluded from simulations (dashed lines in figure 1), spring wheat and soybean yields follow maize's negative trend, soybean being the most affected crop" (Section 3)

> "Brazil, Mexico and Argentina experience large decreases in national production, exacerbated by HSA (blue and yellow bars). The United States also faces a notable decrease in all simulations. China's small gain owing to CO2 fertilization effects is cancelled out by HSA." (Section 4, maize) […] "the United States, Brazil and India (accounting for more than 60% of global soybean production) are the most affected among the top-five producing countries (figure 3). In contrast, Argentina, the third largest soybean producing country, shows a large increase in its production" (Section 4, soybean)

> "Our simulations allow for adaptation in decision of planting dates and choice of crop cultivars" (Section 2.1). Periods: "baseline corresponding to the 1980s (1971–2000), medium time horizon corresponding to the 2050s (2036–2065)" (Section 2.3). Table 1 (p.4) 2050s values are transcribed in `literature_comparison_sources.md` row D1.

### Asseng et al. 2015 (row F04 wheat)
Asseng, S., Ewert, F., Martre, P., et al. (2015). Rising temperatures reduce global wheat production. *Nature Climate Change* 5(2):143-147. https://doi.org/10.1038/nclimate2470
Verified: Crossref (online 22 Dec 2014, issue Feb 2015). Read: **abstract only** (nature.com abstract page; the Rothamsted repository copy returned HTTP 401).
> "Extrapolating the model ensemble temperature response indicates that warming is already slowing yield gains at a majority of wheat-growing locations. Global wheat production is estimated to fall by 6% for each °C of further temperature increase and become more variable over space and time." (Abstract)

### Naresh Kumar et al. 2014, wheat India (row F05)
Naresh Kumar, S., Aggarwal, P. K., Swaroopa Rani, D. N., Saxena, R., Chauhan, N., Jain, S. (2014). Vulnerability of wheat production to climate change in India. *Climate Research* 59(3):173-187. https://doi.org/10.3354/cr01212
Verified: Crossref. Read: **abstract only** (Inter-Research abstract page).
> "This study projects that climate change will reduce the wheat yield in India in the range of 6 to 23% by 2050 and 15 to 25% by 2080." […] "Despite CO2 fertilization benefits in future climate, wheat yield is projected to be reduced in areas with mean seasonal maximum and minimum temperatures in excess of 27 and 13°C, respectively." (Abstract)

### Chandran et al. 2023 (rows F06 wheat, F10 rice, F27 lentil, F34 groundnut)
Chandran, M. A. S., Banerjee, S., Mukherjee, A., et al. (2023). Coupling crop simulation modelling and multi-criteria decision aid for ranking the sustainability of cropping sequences. *Frontiers in Sustainable Food Systems* 7:1208283. https://doi.org/10.3389/fsufs.2023.1208283
Verified: Crossref. Read: **full paper** (Frontiers HTML).
> "However, the yield of wheat in rice–wheat–groundnut sequence was simulated to decrease by 7–9%. The magnitude of yield decline was higher for lentil (12–31%) and groundnut (3–48%)." (Section 3.3; Fig. 4B)

> "Without considering CO2 fertilization, the yield of rice across the six cropping sequences under study will vary by −20 to +20%, −41to +25%, −15 to +26% and − 58 to +21% during mid-century-RCP4.5, mid-century-RCP-8.5, end-century-RCP4.5 and end-century-RCP8.5, respectively." (Section 4.2)

> "Because the majority of crop production in the study area occurs under irrigated conditions, irrigation was turned to automatic when necessary." (Section 2.6). "However, for lentil, the reduction in total crop duration (ranging 2–6 days) was mainly due to shortened reproductive phase (ranging 1–6 days)." (Section 3.3)

Note: the paper gives the baseline CO2 as 380 ppm in Section 2.4 and as 360 ppm in Section 2.6. The CO2 treatment behind the Section 3.3 ranges is not stated there.

### Soora (Naresh Kumar) et al. 2013, rice India (row F09)
Soora, N. K., Aggarwal, P. K., Saxena, R., Rani, S., Jain, S., Chauhan, N. (2013). An assessment of regional vulnerability of rice to climate change in India. *Climatic Change* 118(3-4):683-699. https://doi.org/10.1007/s10584-013-0698-3
Verified: Crossref. Read: **abstract only** (Springer abstract page).
> "On an aggregated scale, the mean of all emission scenarios indicate that climate change is likely to reduce irrigated rice yields by ~4 % in 2020 (2010–2039), ~7 % in 2050 (2040–2069), and by ~10 % in 2080 (2070–2099) climate scenarios. On the other hand, rainfed rice yields in India are likely to be reduced by ~6 % in the 2020 scenario, but in the 2050 and 2080 scenarios they are projected to decrease only marginally (<2.5 %)." (Abstract)

> "iii) rainfed regions (with currently low rainfall) that are likely to gain due to increase in rainfall can further benefit by adaptation." (Abstract)

### Tigchelaar et al. 2018 (row F14 maize)
Tigchelaar, M., Battisti, D. S., Naylor, R. L., Ray, D. K. (2018). Future warming increases probability of globally synchronized maize production shocks. *PNAS* 115(26):6644-6649. https://doi.org/10.1073/pnas.1718031115
Verified: Crossref. Read: **full paper** (PMC6042138 HTML). Its method is the closest to ours: a delta change on observed climate, no CO2 and no adaptation.
> "In the United States, China, Brazil, and Argentina (the top four producing countries), mean total production is projected to decline by 18% (17.4–18.3), 10% (10.1–10.7), 8% (7.6–8.1), and 12% (11.3–11.9), respectively, under 2 °C of global warming" ('Changes in Mean Yields')

> "The future climate is then calculated by adding the change in the (2 °C or 4 °C warmer) climatology to the observed (1979–2008) climate history, thus preserving the present-day interannual and daily temperature variability." (Materials and Methods)

> "This study isolates the effects of future temperature change on maize yields, primarily because of the high uncertainty in precipitation projections." […] "We have therefore excluded CO2 fertilization effects from our analysis." (Materials and Methods)

> "Under business-as-usual emissions (RCP8.5), the global mean temperature is projected to increase by 2 °C as early as 2042, with a median prediction of 2055" (Results). Table 1 lists India's probability of a >10 % loss at +2 °C as 7.4 %, the lowest of the countries listed.

### Ramírez-Cabral et al. 2017 (row F15 maize)
Ramirez-Cabral, N. Y. Z., Kumar, L., Shabani, F. (2017). Global alterations in areas of suitability for maize production from climate change and using a mechanistic species distribution model (CLIMEX). *Scientific Reports* 7:5910. https://doi.org/10.1038/s41598-017-05804-0
Verified: Crossref/OpenAlex (abstract re-checked 18 Nov). Read: **full paper** on 17 Nov (see `literature_comparison_sources.md`, row RC); only the abstract was re-read today. Already in refs.bib as `ramirez2017`.
> "Regions between the tropics of Cancer and Capricorn indicate the highest loss of climatic suitability, contrary to poleward regions that exhibit an increase of suitability." […] "This study indicates that globally, large areas that are currently suitable for maize cultivation will suffer from heat and dry stresses that may constrain production." (Abstract)

> "In India, marginal areas will become unsuitable, whereas in South East Asia, most medium suitability areas will change to marginal suitability by 2050." (Results; quoted from the 17 Nov reading)

### Zilli et al. 2020 (rows F16 maize, F20 soybean)
Zilli, M., Scarabello, M., Soterroni, A. C., et al. (2020). The impact of climate change on Brazil's agriculture. *Science of the Total Environment* 740:139384. https://doi.org/10.1016/j.scitotenv.2020.139384
Verified: Crossref. Read: **full paper** (accepted manuscript, Oxford Research Archive).
> "Despite this reallocation, production of both crops is expected to decrease when compared to the noCC scenario in 2050, with reduction ranging between -6.3% and -36.5% for soybeans and between -12.9% and -29.4% for corn." [reassembled] (Conclusions, ms p.26)

> "For both GGCMs, the levels of CO2 vary according to the emission scenario and thus the results include effects of CO2 fertilization and water use efficiency. It is important to keep in mind that this choice will produce optimistic scenarios" [reassembled] (Methods, ms p.12)

> "Over Brazil, the biophysical impact of climate change results in an increase (decrease) in soybean and corn potential productivity over subtropical (tropical) regions of the country" [reassembled] (ms p.13)

### Walikar et al. 2018 (row F21 soybean)
Walikar, L. D., Bhan, M., Giri, A. K., Dubey, A. K., Agrawal, K. K. (2018). Impact of projected climate on yield of soybean using CROPGRO-Soybean model in Madhya Pradesh. *Journal of Agrometeorology* 20(3):211-215. https://doi.org/10.54386/jam.v20i3.546
Verified: Crossref and DOAJ. Read: **full paper** (journal PDF).
> "By 2050, however, a decline in seed yield was simulated under both RCP pathways, which may be due to increase in the rate of greenhouse gas emissions." (Abstract)

> "For 2050, seed yield decline in all the selected districts under both RCPs, exhibiting this variety may not fit for the longer period in the 2050s." (p.213). Table 3 (p.213) shows 2050 changes between -5.57 % and +0.49 %, so a few cells are slightly positive despite the text. The GCM source is not reported.

### Singh et al. 2014, chickpea (rows F22 India, F23 Ethiopia)
Singh, P., Nedumaran, S., Boote, K. J., Gaur, P. M., Srinivas, K., Bantilan, M. C. S. (2014). Climate change impacts and potential benefits of drought and heat tolerance in chickpea in South Asia and East Africa. *European Journal of Agronomy* 52:123-137. https://doi.org/10.1016/j.eja.2013.09.018
Verified: Crossref (vol 52, pp 123-137, Jan 2014; the requested DOI resolves correctly). Read: **abstract only** (Europe PMC record). The ICRISAT repository copy (oar.icrisat.org/7209) was unreachable (connection timeout/refused) and ScienceDirect returned 403.
> "As compared to the baseline climate, the climate change by 2050 (including CO2) increased the yield of chickpea by 17% both at Hisar and Indore, 18% at Zaloke, 25% at Debre Zeit and 18% at Kabete; whereas the yields decreased by 16% at Nandhyal and 7% at Ukiriguru. The yield benefit due to increased CO2 by 2050 ranged from 7 to 20% across sites as compared to the yields under current atmospheric CO2 concentration; while the changes in temperature and rainfall had either positive or negative impact on yield at the sites." (Abstract)

### Abera et al. 2026 (row F24 chickpea)
Abera, E. A., Anteneh, A. T., Anteneh, K. A. (2026). Modeling climate change impacts on chickpea growth and yield under RCP climate scenarios and evaluating adaptation strategies in central Ethiopia. *Scientific Reports* 16:34833. https://doi.org/10.1038/s41598-026-70590-7
Verified: Crossref (published 11 Sep 2026). Read: **full paper** (nature.com HTML).
> "Baseline (1971–2009) and future (2010–2039) weather data under the RCP4.5 emission scenario were downscaled from the Coordinated Regional Downscaling Experiment (CORDEX) Africa domain." (Abstract). The Results instead refer to "Table 12 Change in chickpea phenology and yield at the end of the 2040s.", which is an internal inconsistency recorded in the CSV.

> "At the Debre Zeit site, grain yield projections show considerable variability, ranging from a 42.0% reduction to a 43.3% increase, with an average increase of 13.4%." (Results; Fig. 16, Table 12)

### Qian et al. 2026, lentil (row F25)
Qian, B., Jing, Q., Liu, K., Smith, W., Jégo, G., Grant, B., Crépeau, M., Zhang, Y., Boote, K. J., Hoogenboom, G. (2026). Simulating climate change impacts on lentil yield in the Canadian Prairies using the CSM-CROPGRO-lentil model. *Agronomy Journal* 118(2):e70308. https://doi.org/10.1002/agj2.70308
Verified: **the DOI resolves in Crossref** (journal-article, published online 25 Feb 2026, CC BY 4.0). Read: **abstract only** (Crossref/OpenAlex abstract; Wiley pages returned a Cloudflare bot check, so the full text was not read).
> "The simulated yield would maintain 22.7%, 28.3%, and 24.0% with adjusted planting dates, while it could be only 17.8%, 20.4%, and 10.8% above the baseline with fixed planting dates in the 2030s, 2050s, and 2070s, respectively, under SSP3‐7.0. The projections also capture the overall positive impacts of rising CO2 and temperature on lentil growth until the adverse impacts of higher temperatures become more pronounced in the 2070s." (Abstract)

### Chandran et al. 2022 (rows F26 lentil, F33 groundnut)
Chandran, M. A. S., Banerjee, S., Mukherjee, A., Nanda, M. K., Kumari, V. V. (2022). Evaluating the long-term impact of projected climate on rice-lentil-groundnut cropping system in Lower Gangetic Plain of India using crop simulation modelling. *International Journal of Biometeorology* 66(1):55-69. https://doi.org/10.1007/s00484-021-02189-8
Verified: Crossref (online 23 Sep 2021, issue Jan 2022). Read: **abstract only** (Europe PMC record).
> "When CO2 fertilization effect was considered, the yield of rice was projected to increase by 11-32%. On the other hand, yield of lentil and groundnut was estimated to change by - 31 to - 12% and - 33 to + 8%, respectively. Enhanced CO2 could mitigate the magnitude of yield reduction due to enhanced temperature." (Abstract)

### Rippke et al. 2016 (rows F28 bean, F35 groundnut)
Rippke, U., Ramirez-Villegas, J., Jarvis, A., et al. (2016). Timescales of transformational climate change adaptation in sub-Saharan African agriculture. *Nature Climate Change* 6(6):605-609. https://doi.org/10.1038/nclimate2947
Verified: Crossref. Read: **full paper** (accepted manuscript, White Rose eprint 101214, re-downloaded 18 Nov). Already in refs.bib as `rippke2016`.
> "For most crops, however, transformation is limited to small pockets (<15 % of area), and only for beans, maize and banana is transformation more widespread (~30 % area for maize and banana, 60 % for beans)." [reassembled] (Abstract, ms p.2)

> "In the case of beans, Uganda and Tanzania both require transformation for about 10 % of their suitable areas by the 2050s, whereas by the 2090s this increases to more than 30 % (median RCP 8.5, Fig. S5B)." [reassembled] (Results, ms p.6). Baseline: "Crop suitability simulations were carried out for the historical period (1961-1990)" (Methods, ms p.19). Groundnut is one of the nine crops modelled and is not among the three named crops above 15 %.

### Hummel et al. 2018 (row F29 bean)
Hummel, M., Hallahan, B. F., Brychkova, G., et al. (2018). Reduction in nutritional quality and growing area suitability of common bean under climate change induced drought stress in Africa. *Scientific Reports* 8:16187. https://doi.org/10.1038/s41598-018-33952-4
Verified: Crossref. Read: **full paper** (nature.com HTML, re-read 18 Nov). Already in refs.bib as `hummel2018`.
> "The majority of current common bean growing areas in southeastern Africa will become unsuitable for bean cultivation by the year 2050 due to changes in temperature and precipitation." (Results heading)

> "Our results further indicate that a reduction in the temperature-related suitability resulting from increased heat stress by 2050 is predicted as the main cause (ΔT < ΔP) for the overall reduction in climatic suitability of bean growing areas in north western Tanzania, southern Zambia, and western Zimbabwe" […] "Conversely, reductions in precipitation-related suitability by 2050 were found to be the major cause (ΔP < ΔT) of climatic suitability change reductions in western Malawi, northern Zambia, eastern Tanzania, and southern Zimbabwe" (Results; Fig. 1C)

> "EcoCrop suitability simulations for common bean were performed for a historical period (1960–1990, chosen to be a representative baseline) and then for the 2050 period (2040–2069) under the Representative Concentrations Pathway 6.0 (RCP 6.0)." […] "simulations were performed using 19 Global Climate Model (GCM) projections" (Methods)

### Heinemann et al. 2017 (row F30 bean)
Heinemann, A. B., Ramirez-Villegas, J., Stone, L. F., Didonet, A. D. (2017). Climate change determined drought stress profiles in rainfed common bean production systems in Brazil. *Agricultural and Forest Meteorology* 246:64-77. https://doi.org/10.1016/j.agrformet.2017.06.005
Verified: Crossref. Read: **abstract only** (Europe PMC record).
> "Results suggest that, with respect to the historical (1980–2005) period, climate change will make drought more frequent, but less severe, across the region. For the dry TPE, the probability of occurrence of drought stress situations (reproductive and/or terminal) changes from 29.6% (baseline) to ca. 70% (2030, RCP [Representative Concentrations Pathway] 8.5)" (Abstract)

### Antolin et al. 2021 (row F31 bean)
Antolin, L. A. S., Heinemann, A. B., Marin, F. R. (2021). Impact assessment of common bean availability in Brazil under climate change scenarios. *Agricultural Systems* 191:103174. https://doi.org/10.1016/j.agsy.2021.103174
Verified: Crossref. Read: **abstract only** (Semantic Scholar API abstract; the full text is paywalled).
> "On average, we found that yield increased by 5.56% and 9.12% for the RCP 4.5 and 8.5 scenarios, respectively. Increased photosynthetic efficiency due to the increased atmospheric CO2 concentration was identified as the main cause of this yield increase. Crop respiration rates increased due to the raised air temperature, and were responsible for increasing the probability (production risk) of not meeting the future domestic demands for grains" (Abstract)

### Kadiyala et al. 2021 (row F32 groundnut)
Kadiyala, M. D. M., Nedumaran, S., Padmanabhan, J., et al. (2021). Modeling the potential impacts of climate change and adaptation strategies on groundnut production in India. *Science of the Total Environment* 776:145996. https://doi.org/10.1016/j.scitotenv.2021.145996
Verified: Crossref (the requested DOI resolves correctly; CC BY). Read: **full paper** (Europe PMC full text, PMC8111332).
> "The yield penalty under pessimistic GCM were as high as −33.7% in the Ganges basin, with overall yields ranging between −33.7% and 12.2% compared to the baseline. Under optimistic GCM, yield improvements were as high as 43.2% in the Godavari FPU and ranged between −2.3 and 43.2%." (Section 3, Table 1)

> "The positive response is mainly due to increased mean annual rainfall amounts and CO2 fertilization." […] "analysis of model output data across locations revealed that change in the duration of crop growth phases and hastening of crop maturity, decrease in the number of pods per plant and seed size were the main reasons for low yields in groundnut." (Discussion)

The paper is internally inconsistent about its GCMs. Section 2.3 says "Among the two GCMs, HadGEM2-ES is the driest", but Section 3 says "We used two GCMs, one optimistic (HadGEM 2-ES) and another pessimistic (GFDL-ESM2M)". The CSV records both GCMs without labelling either as wetter or drier.

### Qian et al. 2019 (row F36 rapeseed)
Qian, B., Zhang, X., Smith, W., et al. (2019). Climate change impacts on Canadian yields of spring wheat, canola and maize for global warming levels of 1.5 °C, 2.0 °C, 2.5 °C and 3.0 °C. *Environmental Research Letters* 14(7):074005. https://doi.org/10.1088/1748-9326/ab17fb
Verified: Crossref/OpenAlex. Read: **full paper** (published PDF via Government of Canada open-science repository, re-read 18 Nov). Already in refs.bib as `qian2019`.
> "Simulated yield changes demonstrate a potentially positive impact on spring wheat and canola yields at all four temperature levels, particularly when shifting planting date is considered in the simulations." […] "However, these benefits declined after warming reached 2.5 °C." (Abstract)

> Table 2 footnote: "Numbers in brackets are the projected changes when the atmospheric CO2 concentrations are fixed" (canola at +2.0 °C: 3.3 (−5.7), 8.3 (−0.8), 11.1 (−3.7) for DayCent, DNDC, DSSAT). "Crop production in Canada is about 99% rainfed, and spring crops such as wheat and canola are seldom irrigated." (Methods)

### Naresh Kumar et al. 2016, Indian mustard (row F37 rapeseed)
Naresh Kumar, S., Aggarwal, P. K., Uttam, K., Surabhi, J., Rani, D. N. S., Chauhan, N., Saxena, R. (2016). Vulnerability of Indian mustard (*Brassica juncea* (L.) Czernj. Cosson) to climate variability and future adaptation strategies. *Mitigation and Adaptation Strategies for Global Change* 21(3):403-420. https://doi.org/10.1007/s11027-014-9606-z
Verified: Crossref (online 12 Sep 2014; issue Mar 2016). Read: **abstract only** (Springer abstract page).
> "On an all India basis, climate change is projected to reduce mustard grain yield by ∼2 % in 2020 (2010–2039), ∼7.9 % in 2050 (2040–2069) and ∼15 % in 2080 (2070–2099) climate scenarios of MIROC3.2.HI (a global climate model) and Providing Regional Climates for Impact Studies (PRECIS, a regional climate model) models, if no adaptation is followed." […] "Yield is projected to reduce in regions with current mean seasonal temperature regimes above 25/10 °C during crop growth." (Abstract)

### Boomiraj et al. 2010 (row F38 rapeseed)
Boomiraj, K., Chakrabarti, B., Aggarwal, P. K., Choudhary, R., Chander, S. (2010). Assessing the vulnerability of Indian mustard to climate change. *Agriculture, Ecosystems & Environment* 138(3-4):265-273. https://doi.org/10.1016/j.agee.2010.05.010
Verified: Crossref. Read: **abstract only** (Europe PMC record).
> "In both irrigated and rainfed conditions, yield reduction would be higher in eastern India (67 and 57%) followed by central India (48 and 14%) and northern India (40.3 and 21.4%). This was due to maximum temperature rise in eastern part of the country, projected for 2080." (Abstract)

### Pullens et al. 2019 (row F39 rapeseed)
Pullens, J. W. M., Sharif, B., Trnka, M., Balek, J., Semenov, M. A., Olesen, J. E. (2019). Risk factors for European winter oilseed rape production under climate change. *Agricultural and Forest Meteorology* 272-273:30-39. https://doi.org/10.1016/j.agrformet.2019.03.023
Verified: Crossref. Read: **abstract only** (Europe PMC record).
> "Projections under climate change were based on climate scenarios generated by the LARS-WG weather generator for GISS and HadGEM models RCP4.5 and RCP8.5 climate projections (2081–2100), which predicted that the crop will most likely suffer from low temperatures (early and late frost) in areas where the crop is currently grown. In the southern regions of Europe, the crops will suffer from droughts." (Abstract)

## 2. Crop coverage

Rows per crop: wheat 6, rice 4, maize 6, soybean 5, chickpea 3, lentil 3, bean 4, groundnut 4, rapeseed 4 (39 rows from 24 publications). Full-text rows: 26; abstract-only rows: 13.

- **Wheat. Found:** global multi-model and multi-method studies (Zhao, Jägermeyr, Deryng, Asseng) and two India studies (Naresh Kumar 2014, abstract; Chandran 2023, one site). Without CO2, all agree on losses, with India among the more sensitive countries. With CO2, global and high-latitude gains appear (Jägermeyr, Deryng). **Not found:** wheat-specific future studies for Russia, Egypt or Brazil beyond global studies; any CMIP6 India wheat projection.
- **Rice. Found:** Zhao (India large per-°C loss), Jägermeyr (gains in South Asia with CO2), Soora 2013 (India irrigated loss, rainfed marginal; abstract) and Chandran 2023 (one site; result spans zero without CO2). **Not found:** verified future studies specific to Bangladesh, Nigeria, Italy, USA or Brazil rice; CMIP6 India rice.
- **Maize. Found:** Zhao, Jägermeyr, Deryng, Tigchelaar (closest method), Ramírez-Cabral (suitability) and Zilli (Brazil). They agree on losses in the USA and Brazil. **Not found:** South Africa-specific future maize projections (only Africa-wide statements); an Ukraine study beyond Tigchelaar's exporter analysis; India-specific process-model projections.
- **Soybean. Found:** Zhao (weak, non-significant signal), Jägermeyr and Deryng (USA/Brazil losses, China/high-latitude gains with CO2), Zilli (Brazil production loss) and Walikar (Madhya Pradesh, small 2050 declines). **Not found:** Argentina-, Russia- or South Africa-specific studies; Moura da Silva et al. 2021 (Brazil, CROPGRO) could not be read.
- **Chickpea. Found:** Singh 2014 (India and Ethiopia sites with CO2; abstract) and Abera 2026 (central Ethiopia, full). Ethiopia gains; India is site-dependent. **Not found:** any future projection for Australia, Türkiye, Russia, USA or China; an India study separating climate from CO2.
- **Lentil. Found:** Qian 2026 (Canada, gains with CO2 and planting adaptation; abstract) and Chandran 2022/2023 (one West Bengal site, losses). **Not found:** any future lentil study for Australia, USA, Russia, China or Ethiopia. The India evidence is one irrigated site from one group.
- **Bean. Found:** Rippke 2016 and Hummel 2018 (Tanzania/SE Africa; heat and rainfall; drought lowers grain iron), Heinemann 2017 (Brazil, more frequent drought by 2030; abstract) and Antolin 2021 (Brazil, CO2-driven gains; abstract). **Not found:** any future study for India, Myanmar, China, USA or Belarus. FAOSTAT "Beans, dry" in Asia includes *Vigna* species that none of these *Phaseolus* studies covers.
- **Groundnut. Found:** Kadiyala 2021 (India; sign depends on the GCM), Chandran 2022/2023 (West Bengal irrigated summer crop, losses) and Rippke 2016 (SSA, incl. Nigeria; limited transformation pressure). **Not found:** future groundnut projections for China, USA or Brazil, or a Nigeria-specific projection.
- **Rapeseed-mustard. Found:** Qian 2019 (Canada; losses with fixed CO2, gains with CO2), Naresh Kumar 2016 and Boomiraj 2010 (India mustard losses from warming; abstracts) and Pullens 2019 (Europe risk types, end-century; abstract). **Not found:** any verified future study for China, USA, South Africa or Brazil; a CMIP6 Indian mustard projection.

**Studies whose conclusion challenges increasing vulnerability:**
- Jägermeyr 2021: wheat gains globally and in China/USA, and rice gains in South Asia, both with CO2.
- Deryng 2014 with CO2: spring wheat and soybean gains.
- Singh 2014: chickpea gains at Hisar, Indore and Debre Zeit, with CO2.
- Abera 2026: Ethiopian chickpea mean gains.
- Qian 2026: Canadian lentil +20-28 % in the 2050s.
- Antolin 2021: Brazilian bean gains, from CO2.
- Kadiyala 2021: India groundnut gains under one GCM.
- Qian 2019 with CO2: canola gains.
- Chandran 2023 with CO2: rice gains.
- Rippke 2016: groundnut has limited transformation needs.

Most of these gains depend on CO2 fertilisation or adaptation, which our index excludes.

## 3. Leads that could not be verified or accessed

- **Singh et al. 2014, chickpea (EJA, 10.1016/j.eja.2013.09.018).** Exists, and the DOI is correct. Full text not accessed: the ICRISAT OAR copy was unreachable and ScienceDirect returned 403. Used at abstract level.
- **Qian et al. 2026, lentil (Agronomy Journal, 10.1002/agj2.70308).** **Exists** (Crossref: vol 118, issue 2, e70308). Full text blocked by a Cloudflare check on Wiley, so used at abstract level.
- **Kadiyala et al. 2021 (10.1016/j.scitotenv.2021.145996).** Exists; full text read.
- **Zhao 2017, Deryng 2014, Jägermeyr 2021.** Exist; full texts read (Zhao and Deryng re-read on 18 Nov, Jägermeyr author proof read on 18 Nov).
- **Singh, Nedumaran, Ntare et al. 2014, groundnut in India and West Africa** (MASGC 19(5):509-529, 10.1007/s11027-012-9446-7). Exists. The abstract reports only trait-adaptation gains, not baseline climate impacts, so there is no row. The full text (ICRISAT OAR) was unreachable. Kadiyala 2021 cites it for "as much as a 25% decrease in yields" in 2050; that figure is second-hand and not used.
- **Moura da Silva et al. 2021, soybean in Brazil** (EJA, 10.1016/j.eja.2021.126329). Exists (Crossref), but the publisher withholds the abstract from the APIs and ScienceDirect did not serve it. Search-engine summaries (yield +1 to +32 % across Brazilian zones, 2050, CMIP5) are **not used**.
- **Boomiraj et al. 2013, Journal of Agrometeorology (Indian mustard, InfoCrop).** The CORE PDF returned 403, so it is not verified and not used.
- **Balvanshi & Tiwari 2019**, J. Agrometeorology 21(4) (10.54386/jam.v21i4.282). Wheat and soybean in Sehore, AquaCrop + CanESM2, RCP2.6/4.5/8.5. Only the DOAJ abstract was seen, which reports reductions mainly by 2080 under RCP8.5. Not added because the abstract gives no 2050 direction per crop.
- **Mall et al. 2004 and Lal et al. 1999** (soybean in India, CROPGRO). Not read.
- **Beebe et al. 2011 / Ramirez-Villegas global bean heat projections.** Not verified (only secondary summaries seen, as in `literature_comparison_sources.md`).
- **Asseng et al. 2015 full text.** The repository copy returned 401, so it was read at abstract level.

## 4. BibTeX for studies not already in refs.bib

Already in refs.bib and reused: `zhao2017`, `deryng2014`, `jagermeyr2021`, `ramirez2017`, `rippke2016`, `hummel2018`, `qian2019`. All entries below were checked against Crossref on 18 Nov 2026. For the 2022 paper, Crossref splits the first author's name oddly ("Chandran M. A., Sarath"); it is written here in the same form as his 2023 record. The Walikar et al. names are upper-case in Crossref and are given in normal case here.

```bibtex
@article{asseng2015,
  author = {Asseng, S. and Ewert, F. and Martre, P. and R{\"o}tter, R. P. and Lobell, D. B. and Cammarano, D. and Kimball, B. A. and Ottman, M. J. and Wall, G. W. and White, J. W. and Reynolds, M. P. and Alderman, P. D. and Prasad, P. V. V. and Aggarwal, P. K. and Anothai, J. and Basso, B. and Biernath, C. and Challinor, A. J. and De Sanctis, G. and Doltra, J. and Fereres, E. and Garcia-Vila, M. and Gayler, S. and Hoogenboom, G. and Hunt, L. A. and Izaurralde, R. C. and Jabloun, M. and Jones, C. D. and Kersebaum, K. C. and Koehler, A-K. and M{\"u}ller, C. and Naresh Kumar, S. and Nendel, C. and O'Leary, G. and Olesen, J. E. and Palosuo, T. and Priesack, E. and Eyshi Rezaei, E. and Ruane, A. C. and Semenov, M. A. and Shcherbak, I. and St{\"o}ckle, C. and Stratonovitch, P. and Streck, T. and Supit, I. and Tao, F. and Thorburn, P. J. and Waha, K. and Wang, E. and Wallach, D. and Wolf, J. and Zhao, Z. and Zhu, Y.},
  title = {Rising temperatures reduce global wheat production},
  journal = {Nature Climate Change}, volume = {5}, number = {2}, pages = {143--147}, year = {2015}, doi = {10.1038/nclimate2470}}
@article{nareshkumar2014wheat,
  author = {Naresh Kumar, S. and Aggarwal, P. K. and Swaroopa Rani, D. N. and Saxena, R. and Chauhan, N. and Jain, S.},
  title = {Vulnerability of wheat production to climate change in {India}},
  journal = {Climate Research}, volume = {59}, number = {3}, pages = {173--187}, year = {2014}, doi = {10.3354/cr01212}}
@article{soora2013,
  author = {Soora, Naresh Kumar and Aggarwal, P. K. and Saxena, Rani and Rani, Swaroopa and Jain, Surabhi and Chauhan, Nitin},
  title = {An assessment of regional vulnerability of rice to climate change in {India}},
  journal = {Climatic Change}, volume = {118}, number = {3-4}, pages = {683--699}, year = {2013}, doi = {10.1007/s10584-013-0698-3}}
@article{tigchelaar2018,
  author = {Tigchelaar, Michelle and Battisti, David S. and Naylor, Rosamond L. and Ray, Deepak K.},
  title = {Future warming increases probability of globally synchronized maize production shocks},
  journal = {Proceedings of the National Academy of Sciences}, volume = {115}, number = {26}, pages = {6644--6649}, year = {2018}, doi = {10.1073/pnas.1718031115}}
@article{zilli2020,
  author = {Zilli, Marcia and Scarabello, Marluce and Soterroni, Aline C. and Valin, Hugo and Mosnier, Aline and Lecl{\`e}re, David and Havl{\'i}k, Petr and Kraxner, Florian and Lopes, Mauricio Antonio and Ramos, Fernando M.},
  title = {The impact of climate change on {Brazil}'s agriculture},
  journal = {Science of the Total Environment}, volume = {740}, pages = {139384}, year = {2020}, doi = {10.1016/j.scitotenv.2020.139384}}
@article{walikar2018,
  author = {Walikar, L. D. and Bhan, Manish and Giri, A. K. and Dubey, A. K. and Agrawal, K. K.},
  title = {Impact of projected climate on yield of soybean using {CROPGRO-Soybean} model in {Madhya Pradesh}},
  journal = {Journal of Agrometeorology}, volume = {20}, number = {3}, pages = {211--215}, year = {2018}, doi = {10.54386/jam.v20i3.546}}
@article{singh2014chickpea,
  author = {Singh, Piara and Nedumaran, S. and Boote, K. J. and Gaur, P. M. and Srinivas, K. and Bantilan, M. C. S.},
  title = {Climate change impacts and potential benefits of drought and heat tolerance in chickpea in {South Asia} and {East Africa}},
  journal = {European Journal of Agronomy}, volume = {52}, pages = {123--137}, year = {2014}, doi = {10.1016/j.eja.2013.09.018}}
@article{abera2026,
  author = {Abera, Endalew Assefa and Anteneh, Aderaw Tsegaye and Anteneh, Kidist Abera},
  title = {Modeling climate change impacts on chickpea growth and yield under {RCP} climate scenarios and evaluating adaptation strategies in central {Ethiopia}},
  journal = {Scientific Reports}, volume = {16}, pages = {34833}, year = {2026}, doi = {10.1038/s41598-026-70590-7}}
@article{qian2026,
  author = {Qian, Budong and Jing, Qi and Liu, Kui and Smith, Ward and J{\'e}go, Guillaume and Grant, Brian and Cr{\'e}peau, Marianne and Zhang, Yinsuo and Boote, Kenneth J. and Hoogenboom, Gerrit},
  title = {Simulating climate change impacts on lentil yield in the {Canadian Prairies} using the {CSM-CROPGRO}-lentil model},
  journal = {Agronomy Journal}, volume = {118}, number = {2}, pages = {e70308}, year = {2026}, doi = {10.1002/agj2.70308}}
@article{chandran2022,
  author = {Chandran, M. A. Sarath and Banerjee, Saon and Mukherjee, Asis and Nanda, Manoj K. and Kumari, V. Visha},
  title = {Evaluating the long-term impact of projected climate on rice-lentil-groundnut cropping system in {Lower Gangetic Plain} of {India} using crop simulation modelling},
  journal = {International Journal of Biometeorology}, volume = {66}, number = {1}, pages = {55--69}, year = {2022}, doi = {10.1007/s00484-021-02189-8}}
@article{chandran2023,
  author = {Chandran, Malamal Alickal Sarath and Banerjee, Saon and Mukherjee, Asis and Nanda, Manoj Kumar and Venugopalan, Visha Kumari and Laing, Alison M. and Siddiqui, Manzer H. and Hossain, Akbar},
  title = {Coupling crop simulation modelling and multi-criteria decision aid for ranking the sustainability of cropping sequences},
  journal = {Frontiers in Sustainable Food Systems}, volume = {7}, pages = {1208283}, year = {2023}, doi = {10.3389/fsufs.2023.1208283}}
@article{heinemann2017,
  author = {Heinemann, Alexandre Bryan and Ramirez-Villegas, Julian and Stone, Lu{\'i}s Fernando and Didonet, Agostinho Dirceu},
  title = {Climate change determined drought stress profiles in rainfed common bean production systems in {Brazil}},
  journal = {Agricultural and Forest Meteorology}, volume = {246}, pages = {64--77}, year = {2017}, doi = {10.1016/j.agrformet.2017.06.005}}
@article{antolin2021,
  author = {Antolin, Lu{\'i}s A. S. and Heinemann, Alexandre B. and Marin, F{\'a}bio R.},
  title = {Impact assessment of common bean availability in {Brazil} under climate change scenarios},
  journal = {Agricultural Systems}, volume = {191}, pages = {103174}, year = {2021}, doi = {10.1016/j.agsy.2021.103174}}
@article{kadiyala2021,
  author = {Kadiyala, M. D. M. and Nedumaran, Swamikannu and Padmanabhan, Jyosthnaa and Gumma, Murali Krishna and Gummadi, Sridhar and Srigiri, Srinivas Reddy and Robertson, Richard and Whitbread, Anthony},
  title = {Modeling the potential impacts of climate change and adaptation strategies on groundnut production in {India}},
  journal = {Science of the Total Environment}, volume = {776}, pages = {145996}, year = {2021}, doi = {10.1016/j.scitotenv.2021.145996}}
@article{nareshkumar2016mustard,
  author = {Naresh Kumar, Soora and Aggarwal, Pramod Kumar and Uttam, Kumar and Surabhi, Jain and Rani, D. N. Swaroopa and Chauhan, Nitin and Saxena, Rani},
  title = {Vulnerability of {Indian} mustard ({Brassica juncea} ({L}.) {Czernj. Cosson}) to climate variability and future adaptation strategies},
  journal = {Mitigation and Adaptation Strategies for Global Change}, volume = {21}, number = {3}, pages = {403--420}, year = {2016}, doi = {10.1007/s11027-014-9606-z}}
@article{boomiraj2010,
  author = {Boomiraj, K. and Chakrabarti, B. and Aggarwal, P. K. and Choudhary, R. and Chander, S.},
  title = {Assessing the vulnerability of {Indian} mustard to climate change},
  journal = {Agriculture, Ecosystems \& Environment}, volume = {138}, number = {3-4}, pages = {265--273}, year = {2010}, doi = {10.1016/j.agee.2010.05.010}}
@article{pullens2019,
  author = {Pullens, Johannes Wilhelmus Maria and Sharif, Behzad and Trnka, Miroslav and Balek, Jan and Semenov, Mikhail A. and Olesen, J{\o}rgen Eivind},
  title = {Risk factors for {European} winter oilseed rape production under climate change},
  journal = {Agricultural and Forest Meteorology}, volume = {272--273}, pages = {30--39}, year = {2019}, doi = {10.1016/j.agrformet.2019.03.023}}
```
