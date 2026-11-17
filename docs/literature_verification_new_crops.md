# Literature verification: five new crops

**Crops:** chickpea, lentil, common bean (dry), groundnut, and rapeseed/mustard.

All items were checked on 2026-11-17. The rule is the same as in `literature_verification.md` and `_v2.md`:

- Every number below was read in the source named next to it.
- Quotes are verbatim, apart from line-wrap and PDF-extraction clean-up.
- Each item states whether I read the **primary full text**, only the **abstract**, or only a **secondary source or search excerpt**.
- Numbers marked **DERIVED** are my own arithmetic on published values. They are not printed in any source.
- **If a value is not in this file, do not state it.**

Method recap (from `code/config.py`):

- **Heat effective temperature.** T_eff = (T_mean + T_max)/2, averaged over 45–70 % of the season.
- **Heat loss.** loss = s_T · max(0, T_eff − T_crit), where s_T = 1/(T_lim − T_crit), following Deryng et al. 2014.
- **Existing heat parameters:** rice 35 / 0.07; wheat 25/35; maize 32/45; soybean 35/40.
- **Water.** Seasonal K_y.
- **Crop coefficients.** Seasonal Kc is the stage-weighted mean of Kc ini/mid/end. Only the stage *proportions* matter for `season_kc()`.

---

## 1. Summary table (recommended values; details and alternatives in sections 2–6)

T_crit and T_lim are on the **T_eff** scale used by the index unless stated otherwise. "DERIVED" means converted or fitted by me from the cited data (see section 7).

| Crop | T_crit (°C, T_eff) | T_lim (°C) / slope s_T (/°C) | Metric in source | Outcome measured | K_y (source type) | Kc ini / mid / end (FAO-56 1998, Table 12) | Stage days ini/dev/mid/late (FAO-56 1998, Table 11 row) | Confidence |
|---|---|---|---|---|---|---|---|---|
| **Chickpea** | **34.0** (DERIVED fit); alt. 30.3 (pod-set threshold 34/19 °C) | **41.1 / 0.14** (DERIVED fit); range 0.10–0.20 | Growth-chamber day/night step regimes 30/20 → 42/32 °C (12 h/12 h), from flowering to maturity | Seed yield per plant (pots) | **0.88** = mean of 0.85 and 0.91, field (Turkey); **not in FAO**. Range 0.67–1.15 | 0.40 (group) / **1.00** / 0.35 ("Chick pea" row). Table also has a "Grabanzo" row 0.4/1.15/0.35 (see 4c) | **No FAO-56 row.** Proxy: Lentil "Arid Region" 25/35/70/40 (170 d) | Heat: medium-low. K_y: low-medium. Kc: medium. Stages: low |
| **Lentil** | **31.9** (DERIVED fit); field cross-check 29.0 (32/20 °C max/min) | **37.8 / 0.17** (DERIVED fit, 4 points); range 0.11–0.20 | Growth-chamber day/night step regimes, as for chickpea | Seed yield per plant (pots) | **1.0** proxy (field: 0.87 in the best treatment; ≈1 on average, paraphrase). Range 0.87–1.15 | 0.40 (group) / 1.10 / 0.30 | "Arid Region", Oct/Nov: **25/35/70/40** (170 d). Alt. "Europe", Apr: 20/30/60/40 | Heat: low-medium. K_y: low. Kc/stages: medium-high |
| **Common bean (dry)** | **25.5** (DERIVED from 28/18 °C optimum, 23 °C mean) | **34.5 / 0.111** (DERIVED: zero yield at 37/27 °C, 32 °C mean). Range 0.065–0.111 | Sunlit chambers, season-long day max/night min (28/18 → 40/30), 10 °C diurnal range | Seed yield (linear decline to zero) | **1.15**, FAO-33 via FAO-66 Table 1 and FAO-56 Rev.1 Table 8.7 | 0.4 / 1.15 / 0.35 ("Beans, dry and Pulses") | "Pakistan, Calif.", June: **15/25/35/20** (95 d). Alts: 20/30/40/20 (continental), 25/25/30/20 (Idaho) | Heat: medium. K_y: high. Kc/stages: high |
| **Groundnut** | **31.8** (DERIVED fit); alt. 29.0 | **42.3 / 0.095** (DERIVED fit); alt. 42.5 / 0.074 | Sunlit chambers, season-long day max/night min 32/22 → 44/34 °C | Seed yield | **0.70**, FAO-33 via FAO-66 Table 1 and FAO-56 Rev.1 Table 8.7 | 0.40 (group) / 1.15 / 0.60 | "West Africa", dry season: **25/35/45/25** (130 d). Alts: 35/35/35/35 (high latitudes), 35/45/35/25 (Mediterranean) | Heat: medium. K_y: high. Kc/stages: high |
| **Rapeseed / mustard** | **29.5 on daily T_max** (field), ≈ **26.5 on T_eff** (PROXY conversion) | **No published slope or T_lim found.** PROXY s_T = 0.10 (wheat's Deryng 10 °C span); range 0.07–0.18 | Field, three seeding dates × 3 years, Ottawa; accumulated daily T_max above threshold during flowering | Seed yield (threshold only) | **0.90**, FAO-56 Rev.1 (2025) Table 8.7 (**not** in FAO-33/FAO-66). Field: 0.87 | 0.35 (group) / 1.0–1.15 (fn 9: lower for rainfed) / 0.35 ("Rapeseed, Canola") | **No FAO-56 1998 row.** Proxy: FAO-56 Rev.1 Table 6.11 canola GDD shares (short season 330/310/450/595) | Heat T_crit: high. Slope: **low (proxy)**. K_y: medium. Kc: medium. Stages: low |

**FAO-56 Rev.1 (2025) Table 6.2 Kc**, an alternative to the 1998 values, for use only if all nine crops switch together:

| Crop | Kc ini | Kc mid | Kc end |
|---|---|---|---|
| Common bean (dry) | 0.40 | 1.05 | 0.40 |
| Chickpea | 0.40 | 1.05 | 0.35 |
| Groundnut | 0.40 | 1.05 | 0.60 |
| Lentil | 0.40 | 1.05 | 0.30 |
| Canola | 0.50 | 1.10 | 0.35 |
| Mustard (*B. juncea*) | 0.35 | 1.10 | 0.40 |

**Suggested `config.py` entries (not applied; this file only documents them):**

| Crop | tcrit | heat_slope | ky | kc | stages |
|---|---|---|---|---|---|
| chickpea | 34.0 | 0.14 | 0.88 | (0.40, 1.00, 0.35) | (25, 35, 70, 40), proxy |
| lentil | 31.9 | 0.17 | 1.0 | (0.40, 1.10, 0.30) | (25, 35, 70, 40) |
| bean | 25.5 | 1/9 ≈ 0.111 | 1.15 | (0.40, 1.15, 0.35) | (15, 25, 35, 20) |
| groundnut | 31.8 | 0.095 | 0.70 | (0.40, 1.15, 0.60) | (25, 35, 45, 25) |
| rapeseed | 26.5 | 0.10 (proxy) | 0.90 | (0.35, 1.15, 0.35) | proxy proportions 330:310:450:595 |

For rapeseed, use Kc mid 1.0 if mainly rainfed (fn 9).

---

## 2. Heat parameters, crop by crop

### 2a. Common bean (dry bean, *Phaseolus vulgaris*)

**Source 1 (abstract, verbatim via Crossref API and Wiley page).** Prasad PVV, Boote KJ, Allen LH Jr, Thomas JMG (2002). Effects of elevated temperature and carbon dioxide on seed-set and yield of kidney bean (*Phaseolus vulgaris* L.). *Global Change Biology* 8(8): 710–721. https://doi.org/10.1046/j.1365-2486.2002.00508.x

URLs:
- https://api.crossref.org/works/10.1046/j.1365-2486.2002.00508.x
- https://onlinelibrary.wiley.com/doi/10.1046/j.1365-2486.2002.00508.x

**Full text not read** (paywalled; Semantic Scholar reports "CLOSED").

> "Red kidney bean cv. Montcalm was grown in controlled environments at day/night temperatures ranging from 28/18 to 40/30 °C under ambient (350 µmol mol−1) or elevated (700 µmol mol−1) CO2 levels. There were strong negative relations between temperature over a range of 28/18–40/30 °C and seed‐set (slope, − 6.5% °C−1) and seed number per pod (− 0.34 °C−1) … Exposure to temperature > 28/18 °C also reduced … seed yield (− 1.1 and − 1.5 g plant−1 °C−1) … yield losses owing to high temperature (> 34/24 °C) are likely to occur".

**Source 2 (primary full text, same research group).** Boote KJ, Allen LH, Prasad PVV, Baker JT, Gesch RW, Snyder AM, Pan D, Thomas JMG (2005). Elevated temperature and CO2 impacts on pollination, reproductive growth, and yield of several globally important crops. *Journal of Agricultural Meteorology* 60(5): 469–474. https://doi.org/10.2480/agrmet.469

URL: https://www.jstage.jst.go.jp/article/agrmet/60/5/60_469/_pdf. I read the PDF. Its text layer is one character per line, so I joined it, and spaces are lost in places.

- Abstract: "Dry bean was more sensitive, with highest yield and seed size at 23°C, reaching zero at 32°C."
- p. 470: "In experiments by Prasad et al. (2002), the highest seed yield occurred at 28/18°C, with yield declining linearly as temperature increased, reaching zero yield at 37/27°C. Seed HI followed the same trend."
- Also p. 470: "pollen production per flower was reduced above 31/21°C, and pollen viability was dramatically reduced above 34/24°C, falling to near zero at 37/27°C".
- Methods (p. 469): "Air temperature was programmed to follow a natural diurnal cycle described by maximum/minimum temperature set-points. Typical temperature treatments were 28/18, 32/22, 36/26, 40/30, and 44/34°C, following a sinusoidal shape during the day and a decay function at night, as suggested by Parton and Logan (1981). The difference between day/night maximum/minimum was 10°C". The chambers were sunlit, with plants grown "from sowing to maturity as a closed stand".
- p. 470 also notes that red kidney bean is a large-seeded Andean type "known to be heat-susceptible, when contrasted to small-seeded Mesoamerican ecotypes".

**Source 3 (secondary review, full PDF read).** Hatfield JL, Boote KJ, Kimball BA, Ziska LH, Izaurralde RC, Ort D, Thomson AM, Wolfe D (2011). Climate impacts on agriculture: implications for crop production. *Agronomy Journal* 103: 351–370. https://doi.org/10.2134/agronj2010.0303

URL: http://www.regionalclimateperspectives.com/uploads/4/4/2/5/44250401/hatfieldetal2011climateimpactsagr.pdf

- Table 2, p. 357, Bean row: "Opt. temp. range reprod. yield 23–24"; "Failure temp. reprod. yield 32" (source: Prasad et al. 2002). The table title says these are "mean temperatures from studies where diurnal temperature range was up to 10°C".
- Text: "highest seed yield at 28/18ºC (23ºC mean) or lower (lower temperatures were not tested), and a linear decline to zero yield with temperature increases to 37/27ºC (32ºC mean)".
- Text: "Using the decline slope for temperature response based on the data of Prasad et al. (2002), bean yield is projected to decrease 7.2% per 1ºC temperature rise."
- Crossref lists issue 2; the PDF footer says Issue 1. Cite as 103: 351–370.

**Values for the index (DERIVED).** T_eff = (T_mean + T_max)/2.
- Optimum: 28/18 °C (mean 23 °C) gives T_eff = (23 + 28)/2 = **25.5 °C**. This is the lowest temperature tested, so the true onset could be lower.
- Zero yield: 37/27 °C (mean 32 °C) gives T_eff = **34.5 °C**.
- Linear slope: **1/9 = 0.111 /°C** of seed yield.
- Lower-bound alternatives:
  - 0.065 /°C, which is the seed-**set** slope, not yield;
  - 0.072 /°C, Hatfield's "7.2 % per 1 °C" projection.

### 2b. Groundnut (peanut, *Arachis hypogaea*)

**Source 1 (abstract, verbatim via Crossref API).** Prasad PVV, Boote KJ, Allen LH Jr, Thomas JMG (2003). Super-optimal temperatures are detrimental to peanut (*Arachis hypogaea* L.) reproductive processes and yield at both ambient and elevated carbon dioxide. *Global Change Biology* 9(12): 1775–1787. https://doi.org/10.1046/j.1365-2486.2003.00708.x

**Full text not read** (closed access).

> "season‐long exposure to daytime maximum/nighttime minimum temperatures of 32/22, 36/26, 40/30 and 44/34°C … At ambient CO2, seed yield decreased progressively by 14%, 59% and 90% as temperature increased from 32/22 to 36/26, 40/30 and 44/34°C, respectively. … Seed harvest index decreased from 0.41 to 0.05 as temperature increased from 32/22 to 44/34°C".

**Source 2 (primary full text).** Boote et al. 2005, as in 2a, p. 471–472:

- "Experiments by Prasad et al. (2003) showed that the optimum mean temperature for grain yield of peanut was either at or possibly below 26°C (32/22°C treatment)".
- "For both soybean and peanut, the seed harvest index … was optimum at 26°C and the decline in HI was more gradual, reaching zero at approximately 40°C (above the 44/34°C treatments)".
- "pollen viability … and seed-set percentage … of peanut maintained well between 26°C (32/22°C) to 32°C (36/26°C), but were progressively decreased above 32°C (36/26°C), reaching zero at about 39°C (44/34°C)".

**Source 3 (secondary, Hatfield et al. 2011, full text read).**

- "Using quadratic projections to peak and minimum showed the optimum temperature was 23 to 24ºC, along with a failure point temperature of 40ºC for zero yield and zero HI."
- "temperature increases will further reduce seed yields (4.1% per 1ºC …)". This is a local slope near 26–27 °C, not the full-range slope.

**Supporting flower-level evidence.** These use bud (tissue) temperatures and are not seed-yield-per-season data.

- **Prasad PVV, Craufurd PQ, Kakani VG, Wheeler TR, Boote KJ (2001).** *Australian Journal of Plant Physiology* 28(3): 233–240. https://doi.org/10.1071/PP00127. Abstract via Crossref API: "The critical bud temperature at these stages was 33°C, above which fruit-set was reduced by 6% °C–1."
- **Prasad PVV, Craufurd PQ, Summerfield RJ, Wheeler TR (2000).** *Journal of Experimental Botany* 51(345): 777–784. https://doi.org/10.1093/jexbot/51.345.777. Abstract via Europe PMC: "only floral bud temperatures > 36 degrees C during AM and WD significantly reduced fruit-set".

**Values for the index (DERIVED).** I used the midpoint daily mean, (max + min)/2. Boote quotes realised means within about ±1 °C of the midpoints.

- T_eff for the four regimes: 29.5, 33.5, 37.5 and 41.5 °C.
- Seed-yield losses (Prasad 2003 abstract): 0, 0.14, 0.59 and 0.90.
- A least-squares broken-stick fit gives **T_crit = 31.8, s_T = 0.095 /°C, T_lim = 42.3** (RMSE 0.03).
- Alternative from Boote's optimum and failure points:
  - optimum 26 °C mean at 32/22 → T_eff 29.0;
  - zero at about 40 °C mean, about 45/35 → T_eff ≈ 42.5;
  - giving s_T = 0.074.

### 2c. Chickpea (*Cicer arietinum*)

**Source 1 (primary full text; graded seed-yield series).** Bhandari K, Sita K, Sehgal A, Bhardwaj A, Gaur P, Kumar S, Singh S, Siddique KHM, Prasad PVV, Jha U, Nayyar H (2020). Differential heat sensitivity of two cool-season legumes, chickpea and lentil, at the reproductive stage, is associated with responses in pollen function, photosynthetic ability and oxidative damage. *Journal of Agronomy and Crop Science* 206(6): 734–758. https://doi.org/10.1111/jac.12433

URL: http://oar.icrisat.org/11785/1/jac.12433.pdf. I read the PDF, and checked Table 3 visually on a rendered page.

- Methods (p. 735–736): plants were grown at "30/20°C (day/night; 12 hr/12 hr …)" until flowering. "Thereafter, sets of the plants were grown in controlled environments at varying high temperatures of 35/25°C, 38/28°C, 40/30°C and 42/32°C … until maturity." Plants were in pots of 7 kg capacity and irrigated three times a day. "The stress was imposed from flowering to maturity, and the impact was assessed on yield components at maturity."
- Table 3 (p. 749), seed yield (g/plant):

| Genotype | 30/20 | 35/25 | 38/28 | 40/30 | 42/32 °C |
|---|---|---|---|---|---|
| ICCV07110 | 5.98 | 5.76 | 4.59 | 3.09 | 1.14 |
| ICCV92944 | 5.27 | 5.19 | 4.23 | 2.89 | 1.11 |
| ICC5912 | 5.13 | 4.98 | 3.96 | 2.84 | 1.18 |

- Text: "At 35/25°C, seed yield was unaffected in chickpea genotypes".

**Source 2 (primary full text, ICRISAT post-print).** Devasirvatham V, Gaur PM, Mallikarjuna N, Raju TN, Trethowan RM, Tan DKY (2013). Reproductive biology of chickpea response to heat stress in the field is associated with the performance in controlled environments. *Field Crops Research* 142: 9–19. https://doi.org/10.1016/j.fcr.2012.11.011

URL: https://oar.icrisat.org/6360/7/CP_pollen%20study_2012.pdf

- Abstract: "The critical temperature for pod set was ≥37°C in heat tolerant genotypes … and ≥33°C for heat sensitive genotypes … a 67% reduction was observed at ≥34/19°C compared to the control (27/16°C). In the field, a pod set reduction of more than 50% occurred at high ambient day temperature (36°C)".
- Results: "pod set was reduced by 39% per 1°C above the threshold temperature".
- Conclusion: "the threshold temperature for pod set was ≥34/19°C".
- The outcome is **pod set**, not seed yield, and the chamber step-ups lasted only days, so this slope is **not** a seed-yield slope.

**Source 3 (abstract, verbatim via Crossref API).** Wang J, Gan YT, Clarke F, McDonald CL (2006). Response of chickpea yield to high temperature stress during reproductive development. *Crop Science* 46(5): 2171–2178. https://doi.org/10.2135/cropsci2006.02.0092

> "High (35/16°C) and moderate (28/16°C) temperature stresses were imposed for 10 d during early flowering and pod development. … the high temperature stress during pod development decreased (P < 0.01) seed yield by 59% for Myles and 53% for Xena."

**Source 4 (abstract seen only as a search excerpt of the publisher page).** Kumar S, Thakur P, Kaushal N, Malik JA, Gaur P, Nayyar H (2013). *Archives of Agronomy and Soil Science* 59(6): 823–843. https://doi.org/10.1080/03650340.2012.683424

> "Biomass, pod set and yield were not affected significantly at 35/25°C, but began to decrease at 40/30°C and were lowest at 45/35°C."

**Values for the index (DERIVED).**

- T_eff for a 12 h/12 h step regime = ((T_day + T_night)/2 + T_day)/2. The regimes 30/20, 35/25, 38/28, 40/30 and 42/32 give T_eff 27.5, 32.5, 35.5, 37.5 and 39.5.
- Mean relative seed-yield loss across the 3 genotypes: 0, 0.027, 0.22, 0.46, 0.79.
- A broken-stick fit gives **T_crit 34.0, s_T 0.142, T_lim 41.1** (RMSE 0.02).
- Sensitivity variant: Devasirvatham's pod-set threshold 34/19 °C gives T_eff (3·34 + 19)/4 = **30.3**.

### 2d. Lentil (*Lens culinaris*)

**Source 1.** Bhandari et al. 2020, as in 2c (primary full text). Table 3, seed yield (g/plant):

| Genotype | 30/20 | 35/25 | 38/28 | 40/30 | 42/32 °C |
|---|---|---|---|---|---|
| LL699 | 2.19 | 1.98 | 1.06 | 0 | 0 |
| LL931 | 2.28 | 1.87 | 1.02 | 0 | 0 |

- Abstract: "At 38/28°C, lentil showed … 53% and 46% reduction in pods and seed yield … At 40/30°C, lentil did not produce any pods".

**Source 2 (primary full text, open access; read through a page-summarising fetch with quotes).** Sita K, Sehgal A, Kumar J, Kumar S, Singh S, Siddique KHM, Nayyar H (2017). Identification of high-temperature tolerant lentil (*Lens culinaris* Medik.) genotypes through leaf and pollen traits. *Frontiers in Plant Science* 8: 744. https://doi.org/10.3389/fpls.2017.00744

- Abstract: late sowing "(first week of January; max/min temperature >32/20°C during the reproductive stage)" vs normal sowing "(first week of November; max/min temperature <32/20°C during the reproductive stage)".
- Abstract: "temperatures >35/25°C were highly detrimental for growth and yield in lentil".
- Results: seed weight per plant under late sowing was "36–41% less in HT genotypes and 55–70% less in HS genotypes". This is a **field** pot/plot comparison, not a dose–response.

**Source 3 (read only as a search excerpt of the BioOne full text).** Delahunty A, Nuttall J, Nicolas M, Brand J (2018). Response of lentil to high temperature under variable water supply and carbon dioxide enrichment. *Crop & Pasture Science* 69(11): 1103–1112. https://doi.org/10.1071/CP18004

> "heat load was calculated as a sum of degrees Celsius (°C) above the threshold value (32°C) for the logged temperature data (5-min intervals), expressed as degree-hours"

> "Overall this translated to a 0.13% reduction in grain yield per degree-hour"

The heat was applied at early pod-filling, in a polyhouse or glasshouse. The unit is degree-hours, so it cannot be mapped directly onto monthly T_eff.

**Values for the index (DERIVED).**

- Same T_eff conversion as chickpea.
- Mean losses: 0, 0.139, 0.535, 1.0 at T_eff 27.5, 32.5, 35.5, 37.5.
- A fit to the first four points gives **T_crit 31.9, s_T 0.168, T_lim 37.8**. Note this is only 4 points for 2 parameters.
- Field cross-check: 32/20 °C max/min gives T_eff = ((32 + 20)/2 + 32)/2 = **29.0**.

### 2e. Rapeseed / canola (*Brassica napus*) and mustard (*B. juncea*)

**Source 1 (abstract, verbatim via Crossref API and Wiley page).** Morrison MJ, Stewart DW (2002). Heat stress during flowering in summer *Brassica*. *Crop Science* 42(3): 797–803. https://doi.org/10.2135/cropsci2002.7970

**Full text not read.**

> "Cultivars of the three Brassica species were grown in a split‐plot design in the field for 3 yr at Ottawa, Canada. Three seeding dates were used each year to obtain different levels of heat stress during flowering. … A heat stress index was developed on the basis of the accumulation of daily maximum temperatures greater than a threshold temperature. The threshold temperature during flowering, which resulted in seed yield losses, was 29.5°C for all Brassica species. … Seed yield decreased as heat stress during flowering increased."

"All Brassica species" includes *B. juncea*.

**Source 2 (abstract via the ISC index mirror).** Kutcher HR, Warland JS, Brandt SA (2010). Temperature and precipitation effects on canola yields in Saskatchewan, Canada. *Agricultural and Forest Meteorology* 150(2): 161–165. https://doi.org/10.1016/j.agrformet.2009.09.011. The ISC record also lists A.P. Moulin as an author.

URL: https://search.isc.ac/Inventory/10/964929.htm

> "the beginning of July, which coincides with the early part of the flowering period of the crop in SK, was the critical time in which high temperatures (>30 °C) and low precipitation led to yield loss."

The abstract gives **no** loss-per-day or loss-per-°C number.

**Source 3 (abstract, verbatim via Crossref API).** Angadi SV, Cutforth HW, Miller PR, McConkey BG, Entz MH, Brandt SA, Volkmar KM (2000). Response of three *Brassica* species to high temperature stress during reproductive growth. *Canadian Journal of Plant Science* 80(4): 693–701. https://doi.org/10.4141/P99-152

> "subjected to high temperature stress of 28/15 °C or 35/15 °C for 7 d … On the main stem, mean seed yield reduction due to heat stress was 89%, but partial compensation by pods on the branches reduced mean per-plant seed yield decrease to 52%. … Species differed in optimum temperatures, with B. juncea and B. rapa having higher optimum temperature than B. napus."

**Source 4 (abstract seen as a search excerpt of the publisher page).** Gan Y, Angadi SV, Cutforth H, Potts D, Angadi VV, McDonald CL (2004). *Canadian Journal of Plant Science* 84(3): 697–704. https://doi.org/10.4141/P03-109

> "Seed yield per plant was reduced by 15% when plants were severely (35/18°C) stressed during bud formation, 58% when stressed during flowering, and 77% when stressed during pod development."

The stress lasted 10 days.

**Values for the index.**

- **T_crit = 29.5 °C on daily T_max (verified).** The index uses T_eff = T_max − (T_max − T_min)/4.
  - **PROXY conversion:** assuming a flowering-period diurnal range of 10–14 °C (my assumption, not sourced), T_crit,eff ≈ 26.0–27.0. I recommend **26.5**.
  - Alternatively, apply 29.5 °C to monthly mean T_max directly.
- **No verified slope or T_lim.**
  - **PROXY:** s_T = 0.10 /°C, borrowing the 10 °C T_lim − T_crit span of Deryng's spring wheat (25/35), another temperate C3 crop.
  - Range 0.07–0.18. The upper end reflects the 52–58 % per-plant loss from only 7–10 days at 35 °C day temperature in Angadi 2000 and Gan 2004.
- For *B. juncea* (South Asia), the same 29.5 °C threshold applies (Morrison & Stewart). Angadi 2000 suggests juncea's optimum is higher than napus's, so napus-based parameters probably **overstate** mustard's heat sensitivity.

### 2f. Cross-check against the existing Deryng parameters (an important caveat)

- Boote et al. 2005 (same chambers) report for soybean an optimum of about 26 °C mean and zero harvest index near 40 °C mean. With a 10 °C diurnal range, that is about T_eff 28.5 for onset and 42.5 for failure.
- Hatfield 2011 Table 2 gives soybean an optimum of 22–24 °C and failure at 39 °C (mean).
- Deryng et al. 2014, used in `config.py`, has soybean at **35/40** on T_eff. That is a later onset and a steeper decline.
- So **chamber-derived thresholds (beans, groundnut, chickpea, lentil) are not on the same footing as the Deryng model parameters** used for maize, wheat and soybean. The new legumes will tend to look more heat-exposed than soybean partly for this reason.
- Recommend a sensitivity run with T_crit + 3 °C for the four new legumes (section 5, item 5).

---

## 3. Water: seasonal yield response factor K_y

### 3a. FAO-66 Table 1 (= FAO-33 seasonal values), primary, re-read

Steduto P, Hsiao TC, Fereres E, Raes D (2012). *Crop yield response to water.* FAO I&D Paper 66, Chapter 2.

URL: https://www.fao.org/4/i2800e/i2800e02.pdf. I downloaded it and extracted the text.

Table 1, printed p. 7: "Seasonal Ky values from FAO Irrigation and Drainage Paper No. 33." Rows, verbatim:

| Crop | Ky | Crop | Ky |
|---|---|---|---|
| Alfalfa | 1.1 | Safflower | 0.8 |
| Beans | 1.15 | Soybean | 0.85 |
| Groundnuts | 0.70 | Sunflower | 0.95 |
| Peas | 1,15 (comma in original) | | |

**No chickpea, lentil, rapeseed/canola or mustard.**

Table 2, p. 12, compares FAO-33 with IAEA field values (FAO Water Report 22), whole-season deficit "Tr-0000":
- Beans: FAO 1.15 vs IAEA **0.59** (−49 %) and **1.43** (+24 %).
- Groundnut: FAO 0.70; no IAEA seasonal value given.
- Text: "the within-crop variation in Ky may be as large as that between crops (Stanhill et al., 1985)."

### 3b. FAO-56 Rev.1 (2025), new and primary

Santos Pereira L, Allen RG, Paredes P, López-Urrea R, Raes D, Smith M, Kilic A, Salman M (2025). *Crop evapotranspiration – Guidelines for computing crop water requirements.* Second edition, revised 2025. FAO Irrigation and Drainage Paper No. 56 Rev.1. Rome, FAO. ISBN 978-92-5-140060-9. https://doi.org/10.4060/cd6621en

Read from the FAO PDF, with the FAO title, ISBN and CC-BY page, hosted at https://agrhysmo.agr.unipi.it/wp-content/uploads/2025/09/FAO56%202025.pdf. Pages were rendered and read visually.

Table 8.7, p. 279: "Seasonal yield response factor (Ky) for field and vegetable crops, fruit trees and vines":

| Group | Crop | Ky |
|---|---|---|
| Grain legumes | Beans | **1.15** |
| Grain legumes | Groundnut | **0.70** |
| Grain legumes | Pea | 1.15 |
| Grain legumes | Soybean | 0.85–1.30 |
| Oil Crops | **Rapeseed** | **0.90** |
| Oil Crops | Safflower | 0.80–0.93 |
| Oil Crops | Sunflower | 0.95 |

Still **no chickpea or lentil**. Text below the table:

> "Tabulated values for Ky cover relatively few crops. … For the crops not included in Table 8.7, users are advised to consider Ky for crops of the same family or that have similar behaviour. Nevertheless, care must be used for this purpose."

The rapeseed value **0.90 is new in Rev.1**. The table does not say which study it comes from. Origin: **NOT VERIFIED**.

### 3b′. FAO-33 itself (Doorenbos & Kassam 1979), primary, scanned copy

Doorenbos J, Kassam AH (with Bentvelsen CLM, Branscheid V, Plusje JMGA, Smith M, Uittenbogaard GO, Van Der Wal HK). *Yield response to water.* FAO Irrigation and Drainage Paper 33. FAO, Rome.

URL (a scanned copy on a university course page): https://posmet.ufv.br/wp-content/uploads/2017/04/MET-477-Doorenbos-e-Kassam-Yield-response.pdf. I rendered and read the page visually.

Table 24, p. 39, "Yield Response Factor (ky)":

| Crop | Vegetative (total) | Flowering (2) | Yield formation (3) | Ripening (4) | **Total growing period** |
|---|---|---|---|---|---|
| Bean | 0.2 | 1.1 | 0.75 | 0.2 | **1.15** |
| Groundnut | 0.2 | 0.8 | 0.6 | 0.2 | **0.7** |
| Pea | 0.2 (early veg.) | 0.9 | 0.7 | 0.2 | **1.15** |
| Soybean | 0.2 | 0.8 | 1.0 | – | 0.85 |

- This confirms that FAO-66 Table 1 reproduces FAO-33.
- The Part B crop chapters (contents p. viii) are: alfalfa, banana, bean, cabbage, citrus, cotton, grape, groundnut, maize, olive, onion, pea, pepper, pineapple, potato, rice, safflower, sorghum, soybean, sugarbeet, sugarcane, sunflower, tobacco, tomato, watermelon and wheat. **There is no chickpea, lentil, rapeseed or mustard.**
- Table 24 also has **no rice row**, even though Part B has a Rice chapter (p. 118), which I did not read. This bears on the "FAO-33 rice" item that `literature_verification_v2.md` lists as NOT VERIFIED.

**So your belief is confirmed:**
- bean 1.15 and groundnut 0.70 are FAO-tabulated;
- chickpea and lentil are not;
- rapeseed is not in FAO-33/FAO-66 but **is** in FAO-56 Rev.1 (0.90).

### 3c. Field-derived K_y where FAO has none

**Chickpea.** Tarı AF, Bahçeci B (2022). Optimal sowing times and irrigation schedule of the chickpea (*Cicer arietinum* L.) in semi-arid regions. *Selcuk Journal of Agriculture and Food Sciences* 36(2): 139–145. https://doi.org/10.15316/SJAFS.2022.020

**Primary full text read** (PDF via dergipark.org.tr). Two-year field trial, Konya, Central Anatolia.

> "The yield response factor (ky) … was determined as 0.85 for early sowing and 0.91 for late sowing, respectively." (p. 143, Fig. 5)

They also cite values that I did **not** verify (secondary only):
- "1.06 (Yilmaz, 2011)" for Çukurova;
- "in northwest India between 0.67 and 0.93 (Jalota et al., 2006)".

**Recommended: 0.88** (mean of 0.85 and 0.91). Range **0.67–1.15**. The upper end is the FAO family proxy (pea/beans 1.15) recommended by Rev.1's text.

**Lentil.** Nandi R, Mondal K, Singh KC, Saha M, Bandyopadhyay PK, Ghosh PK (2021). Yield-water relationships of lentil grown under different rice establishments in Lower Gangetic Plain of India. *Agricultural Water Management* 246: 106675. https://doi.org/10.1016/j.agwat.2020.106675

**Abstract only.** URL: https://ideas.repec.org/a/eee/agiwat/v246y2021ics0378377420322198.html

- Verbatim fragment: "exhibited the lowest yield response factor (Ky = 0.87) of lentil". This is for the treatment of puddled transplanted rice + zero tillage + improved package.
- The abstract also says that relative yield loss averaged about 1 % per 1 % decline in relative ET. **This is a paraphrase from tool summaries and search snippets; I could not read that sentence verbatim.**

**Recommended: 1.0** (labelled proxy). Range **0.87–1.15** (pea).

**Rapeseed/canola.** Istanbulluoglu A, Arslan B, Gocmen E, Gezer E, Pasa C (2010). Effects of deficit irrigation regimes on the yield and growth of oilseed rape (*Brassica napus* L.). *Biosystems Engineering* 105(3): 388–394. https://doi.org/10.1016/j.biosystemseng.2009.12.010

**Abstract only**, via the ISC index mirror https://search.isc.ac/Inventory/10/1267486.htm (publisher abstract elided in Semantic Scholar).

> "The seasonal yield response factor value was 0.87 (coefficient of determination, R2 = 0.71)."

Field trial, Trakya (Turkey); flowering-stage stress hurt yield most. Use as a cross-check of the FAO-56 Rev.1 value 0.90.

Secondary values (search excerpts only; not usable as primary):
- Mila & Ali (2016, *Int. J. Expt. Agric.* 6(1): 15–21) cite "Majnooni-Heris (2014) … canola k_y value of 0.93". Their own *B. rapa* mustard values (Bangladesh) are per-treatment (0.1–1.24), not one seasonal K_y.
- Bilibio et al. (2014, *CIGR J.* 16(1): 1–11) report "ky … 0.3699". This is based on **irrigation depth**, not ET, so it is not comparable.

---

## 4. Crop coefficients and stage lengths

### 4a. FAO-56 (1998) Table 12, primary, raw HTML parsed cell by cell

Allen RG, Pereira LS, Raes D, Smith M (1998). FAO I&D Paper 56.

URL: https://www.fao.org/4/x0490e/x0490e0b.htm. Superscripts are footnote markers, so "1.15²" means 1.15 with footnote 2.

| Table 12 row | Kc ini | Kc mid | Kc end | h (m) |
|---|---|---|---|---|
| *e. Legumes* (group row) | 0.4 | 1.15 | 0.55 | – |
| Beans, dry and Pulses | **0.4** | **1.15** (fn 2) | **0.35** | 0.4 |
| Chick pea | (blank → group 0.4) | **1.00** | **0.35** | 0.4 |
| Grabanzo [sic] | 0.4 | 1.15 | 0.35 | 0.8 |
| Groundnut (Peanut) | (blank → 0.4) | **1.15** | **0.60** | 0.4 |
| Lentil | (blank → 0.4) | **1.10** | **0.30** | 0.5 |
| *h. Oil Crops* (group row) | 0.35 | 1.15 | 0.35 | – |
| Rapeseed, Canola | (blank → 0.35) | **1.0–1.15** (fn 9) | **0.35** | 0.6 |

Footnotes:
- fn 2: "For green beans, peppers and cucumbers, 1.15 can be taken, and for tomatoes, dry beans and peas, 1.20" (when grown on stakes 1.5–2 m tall).
- fn 9: "The lower values are for rainfed crops having less dense plant populations."

Two caveats:
1. As noted for soybean and wheat in `_v2.md`, the blank Kc ini cells take the group value. This is a reading of the table layout, not a per-crop number.
2. Table 12 contains **both** "Chick pea" (mid 1.00, h 0.4) and "Grabanzo" (= garbanzo = chickpea; mid 1.15, h 0.8). I recommend **"Chick pea" 1.00** for the short desi types of South Asia. Range 1.00–1.15.

### 4b. FAO-56 (1998) Table 11 stage lengths (days), primary, raw HTML parsed

| Crop | Init | Dev | Mid | Late | Total | Plant date | Region |
|---|---|---|---|---|---|---|---|
| Beans (dry) | 20 | 30 | 40 | 20 | 110 | May/June | Continental Climates |
| Beans (dry) | **15** | **25** | **35** | **20** | **95** | June | **Pakistan, Calif.** ← recommended |
| Beans (dry) | 25 | 25 | 30 | 20 | 100 | June | Idaho, USA |
| Groundnut | **25** | **35** | **45** | **25** | **130** | Dry season | **West Africa** ← recommended (tropical) |
| Groundnut | 35 | 35 | 35 | 35 | 140 | (see note) | High Latitudes |
| Groundnut | 35 | 45 | 35 | 25 | 140 | May / May/June (see note) | Mediterranean |
| Lentil | 20 | 30 | 60 | 40 | 150 | April | Europe |
| Lentil | **25** | **35** | **70** | **40** | **170** | Oct/Nov | **Arid Region** ← recommended (rabi-like) |

- **Groundnut note (resolved).** In the HTML the plant-date cells read "Dry" / "season" / "May May/June". The FAO-56 PDF (copy with the Feb 2006 errata, https://irre.ku.ac.th/books/pdf/142.pdf, Table 11, p. 106) prints:
  - "Groundnut 25 35 45 25 130 Dry season West Africa"
  - "35 35 35 35 140 May High Latitudes"
  - "35 45 35 25 140 May/June Mediterranean"
- The same PDF Table 12 (p. 111, rendered and read visually) confirms the HTML values: "Chick pea | (blank) | 1.00 | 0.35 | 0.4" and "Grabanzo | 0.4 | 1.15 | 0.35 | 0.8".
- **There is no chickpea row and no rapeseed/canola row in Table 11.** Its oil crops are castor beans, safflower, sesame and sunflower only. I confirmed this by searching the whole table.
- **Proxies.**
  - **Chickpea:** the Lentil "Arid Region" row (25/35/70/40). It has similar proportions (15/21/41/24 %) to the FAO-56 Rev.1 chickpea GDD shares (Table 6.12, "Min length": 80/200/400/220 GDD = 9/22/44/24 %).
  - **Rapeseed:** FAO-56 Rev.1 Table 6.11, canola (*B. napus*). Short season 330/310/450/595 GDD (total 1685); long season 460/555/905/595 (total 2515). These are GDD, not days. Use them as proportions in `season_kc()`.

### 4c. FAO-56 Rev.1 (2025): alternative values (primary; pages rendered and read)

**Table 6.2, pp. 168–169** ("Single (time-averaged) crop coefficients … standardized subhumid climate (RHmin ≈ 45%, u2 ≈ 2 m s-1)"):

| Crop | Kc ini | Kc mid | Kc end |
|---|---|---|---|
| Common bean, Dry | 0.40 | 1.05 | 0.40 |
| Chickpea, garbanzo | 0.40 | 1.05 | 0.35 |
| Groundnut (peanut) | 0.40 | 1.05 | 0.60 |
| Lentil | 0.40 | 1.05 | 0.30 |
| Canola (*B. napus*) | 0.50 | 1.10 | 0.35 |
| Mustard (*B. juncea*) | 0.35 | 1.10 | 0.40 |

**Table 6.10, p. 205**, T_base / T_upper for GDD:

| Crop | T_base (°C) | T_upper (°C) |
|---|---|---|
| Bean | 10 | 32 |
| Chickpea | 5 | 32 |
| Groundnut | 10 | 35 |
| Lentil | 2 | 35 |
| Canola | 2 | 30 |
| Mustard | 5 | 40 |

These are **development cut-offs for GDD (Eq. 6.23), not yield-damage thresholds**. The text says: "when the mean daily air temperature exceeds an upper temperature threshold (Tupper), crop development is assumed to be limited to the GDD below that limit". Do not use them as T_crit.

**Table 6.12, pp. 211–212.** Stage GDD for chickpea, groundnut and lentil, "derived from the original Table 11 of the 1998 FAO56 publication". Note that the 1998 HTML Table 11 itself has no chickpea row.

| Crop | Length | Init | Dev | Mid | Late |
|---|---|---|---|---|---|
| Chickpea | Min | 80 | 200 | 400 | 220 |
| Chickpea | Max | 120 | 250 | 430 | 210 |
| Groundnut | Min | 240 | 470 | 760 | 460 |
| Groundnut | Max | 430 | 800 | 600 | 310 |
| Lentil | Min | 130 | 270 | 830 | 620 |
| Lentil | Max | 120 | 300 | 860 | 650 |

**Rev.1 has no days-based stage table equivalent to the 1998 Table 11.** It uses GDD.

**Effect on seasonal Kc** (`season_kc()`, DERIVED). The choices change seasonal Kc by 0.03–0.08:

| Crop | Option | Seasonal Kc |
|---|---|---|
| Bean | 1998 Kc, Pakistan row | 0.849 |
| Bean | Rev.1 Kc | 0.793 |
| Chickpea | 1.00 with lentil-arid stages | 0.774 |
| Chickpea | "Grabanzo" 1.15 | 0.868 |
| Chickpea | Rev.1 Kc | 0.805 |
| Groundnut | West Africa row | 0.852 |
| Groundnut | Mediterranean row | 0.793 |
| Lentil | Arid row | 0.831 |
| Lentil | Europe row | 0.830 |
| Canola | mid 1.15, short GDD shares | 0.778 |
| Canola | mid 1.0 | 0.698 |
| Canola | mid 1.15, long GDD shares | 0.821 |

---

## 5. Proxies and approximations: direction of bias and suggested sensitivity range

1. **Day/night regime → T_eff** (bean, groundnut, chickpea, lentil).
   - Assumption: daily mean = midpoint of max/min, and T_max = day set-point. For 12 h/12 h step chambers (Bhandari 2020) this is exact. For sunlit sinusoidal chambers (Prasad/Boote), the realised means quoted by Boote differ from the midpoints by about ±1 °C.
   - Bias: ±1 °C in T_crit and T_lim. Sensitivity: **T_crit ±1.5 °C**.
2. **Chamber or pot → field.**
   - Pots, constant irrigation, season-long or flowering-to-maturity exposure, and no recovery days. Devasirvatham 2013 found pod set more sensitive in controlled environments than in the field.
   - Bias: **overstates sensitivity** (slope too steep, T_crit too low). Sensitivity: **s_T × 0.7–1.0**.
3. **Monthly T_eff vs daily thresholds.**
   - Monthly means smooth out hot days. Canola's 29.5 °C is a *daily T_max* accumulation threshold, and Delahunty's lentil threshold is in degree-hours.
   - Bias: **understates exposure**, strongest for canola. This partly offsets item 2.
   - Sensitivity: canola T_crit,eff 25.5–27.5; or apply 29.5 °C on monthly T_max.
4. **Single or few genotypes.**
   - Bean is from one Andean red-kidney cultivar, which the authors call heat-susceptible relative to Mesoamerican types. Groundnut is cv. Georgia Green; chickpea 3 and lentil 2 Indian genotypes.
   - Bias: bean sensitivity is **overstated** for tropical lowland (Mesoamerican) beans. Sensitivity: **bean T_crit +2 °C** (27.5).
5. **Inconsistency with the Deryng parameters** (section 2f).
   - Chamber-derived onsets for legumes sit 3–6 °C below what Deryng-style model calibrations would give (soybean comparison).
   - Bias: new legumes look relatively more heat-exposed than soybean, maize and wheat. Sensitivity: **T_crit +3 °C** for all four new legumes.
6. **Canola slope borrowed from wheat** (s_T 0.10). No primary canola dose–response slope was found. The direction is unknown. Range **0.07–0.18**.
7. **Canola T_max → T_eff**, using an assumed diurnal range of 10–14 °C. ±1 °C.
8. ***B. napus* parameters applied to *B. juncea*** (Indian mustard). Juncea has a higher optimum (Angadi 2000). Bias: **overstates** mustard heat loss. If mustard dominates the rapeseed area, sensitivity is T_crit +1–2 °C. This number is a judgement and is not sourced.
9. **Chickpea K_y 0.88** from one Turkish site. Range 0.67–1.15 (Jalota 2006 via secondary; FAO family proxy).
10. **Lentil K_y 1.0** from an abstract paraphrase plus a best-treatment 0.87. Range 0.87–1.15. A pea/bean proxy (1.15) would **overstate** drought loss relative to the field evidence.
11. **Rapeseed K_y 0.90** (FAO-56 Rev.1). Its provenance was not traced, but it agrees with field values of 0.87 (verified abstract) and 0.93 (secondary). Range 0.85–0.95.
12. **Bean K_y 1.15.** The IAEA field values are 0.59 and 1.43 (FAO-66 Table 2). Range **0.6–1.4** if a robustness check is wanted.
13. **Kc edition choice.** Rev.1 lowers Kc mid for these legumes (1.10–1.15 → 1.05). Use 1998 for consistency with the existing four crops, or switch all nine crops.
14. **Chickpea Kc mid ambiguity** (1.00 "Chick pea" vs 1.15 "Grabanzo"). Range 1.00–1.15; seasonal Kc 0.77–0.87.
15. **Stage proxies.** Chickpea uses the lentil-arid row; canola uses Rev.1 GDD shares. The effect on seasonal Kc is ≤ 0.04 (section 4c).
16. **Heat outcome mismatch.** Bean and groundnut use season-long exposure but the index uses a flowering window. Chickpea and lentil use flowering-to-maturity exposure. Canola is field flowering-period exposure. No adjustment is proposed; this is documented only.

---

## 6. What I could not verify (do not state as fact)

1. **Prasad et al. 2002 and 2003 full texts.** Only the abstracts (Crossref), plus Boote 2005 and Hatfield 2011, were read. The exact daily means achieved in each treatment and any regression of yield on temperature in those papers were not seen.
2. **Morrison & Stewart 2002 full text.** The slope of seed yield on the heat-stress index is not known. The page timed out and the paper is closed access.
3. **Kutcher et al. 2010 full text.** The secondary claims below are **NOT VERIFIED**, and the abstract has no slope:
   - "12% yield loss for every week of temperatures above 30 °C" (*Can. J. Plant Sci.* 2023 review, cdnsciencepub.com/doi/10.1139/cjps-2022-0215);
   - "18 to 75 kg ha−1 per day" (Secchi et al. 2023, *Field Crops Res.* 293: 108848, search excerpt).
4. **Kaushal et al. 2016, Bhandari et al. 2016 (lentil, *J. Crop Improv.*), Devasirvatham et al. 2012 (review), Kalra et al. 2008 and Delahunty et al. 2015** were not opened. Statements attributed to them here appear only as secondary citations, e.g. "87% yield reduction" for Bhandari 2016, via Delahunty 2018.
5. **Crop-model cardinal temperatures** (CROPGRO-drybean, -peanut, -chickpea and -canola species files; APSIM; LPJmL; GGCMI) were **not read**. Teixeira et al. 2013 (*Agric. For. Meteorol.* 170: 206–215) covers only wheat, maize, rice and soybean. Deryng 2014 does not include these five crops.
6. **Chickpea K_y of Yilmaz 2011 (1.06) and Jalota et al. 2006 (0.67–0.93)**, and **canola K_y of Majnooni-Heris 2014 (0.93)**: secondary only.
7. **The source study behind FAO-56 Rev.1's rapeseed K_y = 0.90.**
8. **Nandi et al. 2021**: only the Ky = 0.87 fragment is verbatim. The "≈1 % per 1 %" average is a paraphrase.
9. **Delahunty 2018** was read only via a search-tool excerpt of the full text. The pages and DOI were confirmed through Crossref.
10. FAO-33 itself and the groundnut Table 11 plant dates were both **resolved** during this check (sections 3b′ and 4b).
11. The FAO-56 Rev.1 PDF was read from a university-hosted copy of the FAO publication (FAO title, ISBN and DOI pages present), not downloaded from fao.org.

---

## 7. Derivation notes (reproducible)

- **Fits.** Least-squares broken-stick fits: loss = min(1, s·max(0, T − T_crit)), grid search on T_crit in 0.05 °C steps, then s by least squares. Code: session scratchpad `fit.py`.
- **Chickpea fit on other temperature scales:**
  - mean (T_day + T_night)/2: T_crit 31.6, T_lim 38.6;
  - day temperature: T_crit 36.6, T_lim 43.6.
- **Lentil fit on other temperature scales:**
  - mean: T_crit 29.4, T_lim 35.3;
  - day temperature: T_crit 34.4, T_lim 40.3.
- **Groundnut fit on other temperature scales:**
  - mean: T_crit 29.3, T_lim 39.8. This matches Hatfield's "failure point temperature of 40ºC".
  - T_max: T_crit 34.3, T_lim 44.8.
- **Bean:** T_eff = (mean + max)/2 → (23 + 28)/2 = 25.5; (32 + 37)/2 = 34.5.
