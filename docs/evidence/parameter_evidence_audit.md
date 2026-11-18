# Parameter evidence audit (crop-response parameters)

Audit date: 2026-11-18. Companion file: `docs/evidence/parameter_evidence_register.csv` (97 rows, one per crop × parameter
actually used in `code/config.py` / `code/04_hazards.py` / `code/08_index.py`, including every `PARAM_RANGES`
perturbation and the all-crop T_crit offsets −2, −1, +1, +2, +3 °C).

Rules followed:
- Checks already documented with quotes in `docs/evidence/literature_verification_new_crops.md` (cited "LV-NC §x") and in the
  mid-evaluation notes `c:\sem_5\est\project\S_rice_precipitation\docs\literature_verification.md` /
  `literature_verification_v2.md` (cited "LV1 §x", "LV2 §x") were not redone. This file adds what was missing.
- Bibliographic details checked against Crossref (`api.crossref.org/works/<DOI>`) on 2026-11-18; the GGCMI
  calendar DOI is a DataCite DOI and was checked against `api.datacite.org`.
- **Read level** is given for every source: *full text*, *abstract* (verbatim from Crossref / Europe PMC /
  Semantic Scholar / publisher metadata), *search excerpt* (seen only in a search-tool snippet; not usable as
  evidence), or *secondary* (known only through another publication).
- Quotes are verbatim apart from line-wrap. Numbers marked **DERIVED** are my arithmetic, not printed in any source.
- Published treatment ranges are **not** confidence intervals and are not presented as such.
- No existing file was edited and nothing was committed.

Model recap (confirmed in code): heat hazard = flowering-window mean of monthly
max(0, T_eff − T_crit) with T_eff = (T_mean + T_max)/2 and the window = 45–70 % of the calendar-day season
(`03_build_grids.py`, `04_hazards.py`); heat loss = min(1, s_T × hazard); water loss = min(1, K_y × rainfed share ×
(1 − P/(Kc·ET0))) (`05_country_series.py`, decision E14). Stage days only enter through the stage-weighted seasonal Kc
(`season_kc()`); the season length itself comes from the calendar.

---

## Q1. Rice K_y 1.25 (maize value). Is there a field-derived seasonal rice K_y on the FAO definition?

**Verdict: none found that satisfies the FAO definition (seasonal, 1 − Ya/Ym = K_y(1 − ETa/ETm), measured ETa,
unstressed Ym). Keep 1.25 as a labelled proxy; its robustness values 1.0 and 1.5 are exploratory perturbations.**

- FAO gives no rice K_y: FAO-33 Table 2 lists rice only as "high"; FAO-66 Table 1 and FAO-56 Rev.1 Table 8.7 have no
  rice row (LV-NC §8.1, full text). FAO Water Report 22 (Moutonnet 2002, Tables 1–2; HTML read in full this audit,
  https://www.fao.org/4/y3655e/y3655e04.htm) has no rice row either: its IAEA field values cover bean, cotton,
  groundnut, maize, potato, soybean, sugar cane, sugar beet, sunflower and wheat.
- **Anupoju & Kambhammettu 2020**, *Irrigation Science* 38(4): 415–430, doi:10.1007/s00271-020-00684-1.
  Read level: abstract (publisher page metadata, verbatim). Setting: four paddy fields in a south-Indian command
  area, 2017–18, three deficit levels against farmers' practice. ET was partitioned with a model, and yield was
  simulated with a simple algorithm: "The FAO-56-based SIMDualKc model was parameterized to partition the
  evapotranspiration (ET) fluxes" and "The calibrated soil–water balance model was further applied to simulate crop
  yield using a simple crop growth algorithm." Result: "crop yield is sensitive to water stress during vegetation
  (ky = 1.14 ± 0.10) followed by transplantation (ky = 1.07 ± 0.16) and reproduction stages (ky = 1.02 ± 0.17)".
  These are **stage** K_y values that are partly model-derived, with no seasonal value and a stressed (farmer-practice)
  control. They are **not** compatible with the seasonal FAO K_y used here, and they are not a replacement.
- **Raes et al. 2007**, *Agricultural Water Management* 89(3): 229–235, doi:10.1016/j.agwat.2007.01.005 (rainfed
  lowland rice, SE Tanzania). The seasonal K_y = 1.7 is known **only from a search excerpt**. The full text is
  closed (ScienceDirect HTTP 403; the ORBi copy is restricted). The search summary says transpiration was
  **simulated** (BUDGET model) and the yield–transpiration relation fitted on farmers' plots. This is not verified
  and not usable.
- **Guimarães et al. 2016**, *Rev. Bras. Eng. Agríc. Ambiental* 20(5): 441–446,
  doi:10.1590/1807-1929/agriambi.v20n5p441-446 (upland rice, field, Brazil). Read level: publisher page via a
  summarising fetch. The paper reports absolute slopes ("about 218 kg ha-1 per each 1 mm reduction of ET") and
  **no K_y**.
- The FAO K_y applicability problem goes beyond the value. The index uses 1 − P/(Kc·ET0), not 1 − ETa/ETm (register
  row "all / water-deficit metric"), and 61 % of rice area is irrigated (SPAM), so rice's water term is damped by the
  rainfed share whatever K_y is used.
- `config.py` `ky_source` reads "FAO 66; Brouwer and Heibloem 1986", which implies FAO-66 gives a rice value. It does
  not. Suggested wording: "PROXY: maize K_y (FAO-33 via FAO-66 Table 1); FAO gives no rice K_y".

## Q2. Rice heat: is fertility loss usable as yield loss? Is there a yield response per degree?

**Verdict: the slope 0.07/°C is not justified as a yield slope on T_eff (mark unsupported as such). The only
yield-based per-degree evidence found comes from sunlit-chamber, season-long experiments (≈ −10 %/°C of mean
temperature above ~25 °C). It is convertible to T_eff, but it is a partial candidate for a sensitivity run, not a
supported replacement.**

- **Jagadish et al. 2007**, *J. Exp. Bot.* 58(7): 1627–1635, doi:10.1093/jxb/erm003. Read level: abstract (Europe
  PMC, verbatim). Plants were "grown at 30/24 °C day/night temperature in a greenhouse and transferred to growth
  cabinets"; treatments were "29.6 °C (control), 33.7 °C, and 36.2 °C tissue temperatures"; "≤1 h exposure to
  ≥33.7 °C at anthesis caused sterility"; "In IR64 … spikelet fertility was reduced by about 7% per °C > 29.6 °C. In
  Azucena … spikelet fertility was reduced by 2.4% °Cd-1 above a threshold of 33 °C."
  - Outcome: fertility of individually marked spikelets.
  - Metric: tissue temperature for hours at anthesis.
  - Growth stage: anthesis only.
  - The model instead applies this slope **above 35 °C** of monthly T_eff, a different threshold on a different metric.
  - Fertility is one yield component. Prasad et al. 2006 (below) show that it propagates to yield, but not 1:1.
  - The same abstract shows the slope is genotype-specific in form and size (IR64 vs Azucena).
- **Prasad et al. 2006**, *Field Crops Res.* 95(2–3): 398–411, doi:10.1016/j.fcr.2005.04.008. Read level: abstract
  (Europe PMC). Fourteen cultivars were grown at ambient and ambient + 5 °C. "Lower spikelet fertility at elevated
  temperature resulted in fewer filled grains, lower grain weight per panicle, and decreased harvest index." Through
  Hatfield 2011 (p. 360): "9 to 86% reduction in spikelet fertility, 0 to 93% reduction in grain weight per panicle,
  and 16 to 86% reduction in HI". This supports a link between fertility and yield, but not a per-degree yield slope.
- **Hatfield et al. 2011**, *Agron. J.* 103(2): 351–370, doi:10.2134/agronj2010.0303. Read level: full text (PDF;
  the footer says Issue 1, Crossref says issue 2).
  - p. 360: "Baker et al. (1995) concluded from their sunlit controlled-environment chambers experiments that the
    optimum mean temperature for grain formation and grain yield of rice is 25ºC and grain yield is reduced 10% per
    1ºC temperature increase above 25ºC until 35 to 36ºC mean temperature when no yield is obtained. In their
    experiments they used a 7ºC day/night temperature differential".
  - Table 2 (p. 357), rice row: "Opt. temp. range reprod. yield 23–26"; "Failure temp. reprod. yield 35–36". The
    table note says these "represent mean temperatures from studies where diurnal temperature range was up to 10ºC".
  - Baker et al. 1995 itself (ASA Special Publication 59, pp. 31–47, doi:10.2134/asaspecpub59.c2, a book chapter)
    was **not read**, so this value is **secondary**.
- **Baker, Allen & Boote 1992**, *J. Exp. Bot.* 43(7): 959–964, doi:10.1093/jxb/43.7.959. Read level: abstract
  fragments extracted by a page-summarising fetch of the publisher page (not a clean verbatim copy; the OUP page is
  bot-protected). The fragments are: cv. "IR–30", "outdoor, naturally sunlit, controlled-environment, plant growth
  chambers", "temperature regimes ranging from 25/18/21°C to 37/30/34°C" (day air / night air / paddy water),
  "grown season-long", and at 660 µmol mol⁻¹ CO₂ "grain yield decreased from 10.4 to 1.0 Mg ha−1 with increasing
  temperature" from 28/21/25 °C to 37/30/34 °C. The intermediate regimes were not seen.
- **Field evidence on other metrics, not convertible to a T_eff threshold:**
  - Peng et al. 2004 (*PNAS* 101: 9971, doi:10.1073/pnas.0403720101; abstract, verbatim): "Grain yield declined by
    10% for each 1 °C increase in growing-season minimum temperature in the dry season, whereas the effect of
    maximum temperature on crop yield was insignificant."
  - Welch et al. 2010 (*PNAS* 107: 14562, doi:10.1073/pnas.1001222107; LV1 §14): "Higher minimum temperature
    reduced yield, whereas higher maximum temperature raised it."
  - Neither gives a T_max/T_eff threshold-plus-slope.
- **DERIVED conversion (candidate for sensitivity only).** With T_eff = T_mean + DTR/4 and the 7 °C differential:
  - onset T_eff = 25 + 1.75 = **26.75 °C**;
  - zero yield at T_eff = 36.75–37.75 °C;
  - slope ≈ **0.10 per °C** (the conversion shifts thresholds only).
  - Baker 1992's end points give the same slope: 28/21 → T_eff 26.25 and 37/30 → T_eff 35.25 (step-regime
    convention; the chamber diurnal shape was not checked); relative loss 0.904 over 9 °C ≈ 0.10/°C, at elevated CO₂.

  This would move rice from T_crit 35 to about 27 on T_eff, which makes rice heat exposure large almost everywhere in
  the tropics. That contradicts the field T_max evidence (Welch 2010), and it would put rice on the same
  chamber-versus-model footing that LV-NC §2f flags for the legumes. **Replacement supported: partial (sensitivity
  only).**
- **No conversion was applied to the rice heat parameters at all.** Yoshida's 35 °C (anthesis air temperature;
  recorded in LV1 §3 as a daily mean) is applied directly to T_eff ≥ T_mean. If the same conversion used for the other
  crops were applied, the threshold would rise to 35 + DTR/4 (DERIVED; illustrative only, not proposed).

## Q3. Rapeseed: slope 0.10/°C (borrowed) and T_crit 26.5 °C. Is canola evidence applicable to Indian mustard?

**Verdict: no defensible slope found, so mark s_T = 0.10 as unsupported. T_crit 26.5 is a published daily-T_max
threshold converted by assumption, and its meaning changes from a daily accumulation threshold to a monthly-mean
threshold. Keep it as a labelled proxy. B. napus → B. juncea transfer: the threshold is partly supported (the field
study included B. juncea), but the evidence comes from Canadian cultivars, not Indian mustard.**

- **Morrison & Stewart 2002**, *Crop Sci.* 42(3): 797–803, doi:10.2135/cropsci2002.7970. Read level: abstract
  (Crossref, verbatim); the full text is closed and remains unread (LV-NC §6.2).
  - Field: "grown in a split‐plot design in the field for 3 yr at Ottawa, Canada. Three seeding dates were used each
    year".
  - Index: "A heat stress index was developed on the basis of the accumulation of daily maximum temperatures greater
    than a threshold temperature. The threshold temperature during flowering, which resulted in seed yield losses,
    was 29.5°C for all Brassica species."
  - The species studied were "B. napus L., B. rapa L., and B. juncea (L.) Czernj. & Cosson".
  - Newly noted in the Crossref abstract: "Temperatures greater than 27°C, in a growth cabinet, have resulted in
    floral sterility and yield loss in Brassica napus L." This is a cabinet-versus-field contrast of about 2.5 °C
    (see Q6).
  - No slope appears in the abstract.
- **Kutcher, Warland & Brandt 2010**, *Agric. For. Meteorol.* 150(2): 161–165, doi:10.1016/j.agrformet.2009.09.011.
  Crossref lists three authors; the A.P. Moulin listed in the ISC mirror is not on Crossref. Read level: abstract via
  the ISC mirror (LV-NC §2e); the full text is closed (Semantic Scholar "CLOSED").
  - Design: crop-district statistics, correlation and principal-components analysis.
  - Abstract: "the beginning of July … was the critical time in which high temperatures (>30 °C) and low
    precipitation led to yield loss." No per-degree slope.
  - "12 % loss per week above 30 °C" is **secondary only** and is a weeks-count metric, so it cannot be converted to
    s_T on T_eff.
- **Gan et al. 2004**, *Can. J. Plant Sci.* 84(3): 697–704, doi:10.4141/P03-109. Read level: abstract (Crossref,
    verbatim).
  - Setting: "A growth chamber study"; "Two canola-quality Brassica juncea … a Brassica napus canola 'Quantum', and a
    B. juncea oriental mustard 'Cutlass'"; "High (35/18°C) and moderate (28/18°C) temperature stress was imposed for
    10 d".
  - Result: "Seed yield per plant was reduced by 15% when plants were severely (35/18°C) stressed during bud
    formation, 58% when stressed during flowering, and 77% when stressed during pod development"; "B. juncea produced
    greater number of pods per plant but had a great rate of pod infertility than B. napus."
  - This is a single-stress-regime treatment result, not a dose–response.
- **Angadi et al. 2000**, *Can. J. Plant Sci.* 80(4): 693–701, doi:10.4141/P99-152. Read level: abstract (Crossref).
  "B. juncea and B. rapa having higher optimum temperature than B. napus"; "Brassica rapa was more sensitive to heat
  stress than B. napus and B. juncea." The conference version (Angadi et al. 1999, Univ. Saskatchewan Soils & Crops
  workshop; full text read; **not peer-reviewed**) says "the optimum daytime temperature for B. juncea L. and B. rapa
  L. cultivar was above 20 °C and is close to 28 °C", whereas for B. napus "the optimum … is around 20 °C" (7-day
  chamber stresses).
- **Nuttall, Moulin & Townley-Smith 1992**, *Agron. J.* 84(5): 765–768,
  doi:10.2134/agronj1992.00021962008400050001x. Read level: abstract (Crossref).
  - Design: a 16-year field study, B. napus, Melfort SK.
  - Result: "Grain yield was positively correlated to total precipitation and negatively correlated to mean maximum
    daily temperature for the months of July and August (R2 = 0.32)." This is joint with precipitation, and no
    per-degree coefficient appears in the abstract.
  - "0.4 t/ha … for every 3 °C" is secondary (Angadi 1999). It is in absolute units, over a T_max range of 21–25 °C
    with no threshold, so it does not convert into our broken-stick form.
- **Indian mustard (B. juncea, South Asia):** the searches found sowing-date studies and conference or regional
  papers only. Sowing date confounds temperature with photoperiod, season length and pests, and no dose–response on
  a convertible metric was found. Gap.
- **Applicability:**
  - The 29.5 °C threshold is the best-supported number, and it covers B. juncea (Canadian cultivars).
  - The chamber evidence suggests juncea's optimum is higher than napus's, so the direction (napus parameters
    overstate juncea loss) has support. The magnitude does not.
  - The conversion 29.5 − 12/4 = 26.5 is an assumption: the diurnal-range (DTR) value is unsourced, and an
    accumulated-daily-exceedance threshold has become a monthly-mean threshold (see Q4).
- **Replacement: none found.** The PARAM_RANGES values 0.07 and 0.18 are exploratory perturbations. The 52–58 %
  losses after 7–10 days at 35 °C are treatment results, not slopes.

## Q4. Converting daily-maximum or day/night chamber thresholds to T_eff

**Verdict: documented (in the `code/25_parameter_fits.py` docstring and LV-NC §5 item 1 and §7). It is a DERIVED
calculation resting on ASSUMPTIONS, not a published relation.**

- **What is published:** the T_eff definition, (T_mean + T_max)/2 (Deryng et al. 2014; LV1 §2).
- **What is derived:**
  - For a 12 h/12 h step regime D/N, T_mean = (D+N)/2 and T_max = D exactly, so T_eff = ((D+N)/2 + D)/2 (an
    algebraic identity; Bhandari 2020 chickpea and lentil).
  - For sunlit sinusoidal chambers (Prasad 2002/2003 via Boote 2005), the same midpoint convention is used. Boote
    reports realised means within about ±1 °C of the midpoints, which is a stated uncertainty.
- **What is assumed:**
  1. A plant held at a constant daily regime responds as it would to the same **monthly-mean** T_eff under variable
     field weather. This ignores day-to-day variance. Deryng applies the damage function daily, so with a convex
     damage function the monthly-mean exceedance understates the expected damage.
  2. The chamber exposure window (season-long for bean and groundnut; flowering-to-maturity for chickpea and lentil)
     equals the index's 45–70 % window.
  3. Rapeseed: T_eff = T_max − DTR/4 with **DTR = 12 °C, assumed and unsourced** (range 10–14), applied to a threshold
     that the source defines for accumulated daily T_max exceedances.
  4. Rice: no conversion at all (Q2).
- **Label:** derived calculation (algebra) plus assumption (equivalence, DTR). No published relation linking chamber
  regimes to monthly T_eff thresholds was found.

## Q5. Lentil K_y 1.0 (Nandi et al. 2021)

**Verdict: the bibliography is verified, the sentence is verbatim, and the design is a field study. FAO-definition
compatibility is only partial. No other field lentil K_y was found. Keep as a labelled proxy.**

- **Bibliography (Crossref):** Nandi R, Mondal K, Singh KC, Saha M, Bandyopadhyay PK, Ghosh PK (2021). *Agricultural
  Water Management* 246: 106675, doi:10.1016/j.agwat.2020.106675. Already in refs.bib.
- **Read level:** abstract, verbatim (Semantic Scholar API). The full text is paywalled.
- **Design** (abstract): field, "rainfed rice-fallows of Lower Gangetic Plain (LGP) of India during 2014–15 and
  2015–16". Factors: rice establishment (DSR/PTR) × tillage (ZT/CT) × nutrient management (IP/FP); lentil grown on
  "carry-over residual soil water".
- **Results** (abstract): "PTR–ZT–IP produced the highest ETa (80 mm) with maximum seed yield (1281 kg ha−1) … and
  also exhibited the lowest yield response factor (Ky = 0.87)"; "An average of 1% relative yield loss per 1% decline
  in relative ET suggests the suitability of growing of lentil crop in this post-rice residual water regimes of LGP."
- **Compatibility with FAO:**
  - FAO's K_y requires Ym = yield without water limitation under the same management.
  - The abstract reports no irrigated or unstressed control, and the treatments differ in tillage and fertiliser.
    The relative-yield / relative-ET ratio therefore mixes water and non-water effects.
  - The best-treatment ETa is only 80 mm, so even the reference is water-limited.
  - Per-treatment "Ky" values are not the single seasonal regression coefficient FAO tabulates.
  - Status: published (abstract level); applicability partial.
- **Other lentil K_y:** none found in FAO-33, FAO-66, FAO-56 Rev.1 Table 8.7 or FAO Water Report 22 Tables 1–2, and a
  targeted search found no field study. Gap.
- **Robustness values:**
  - 0.87 is the best-treatment value: a treatment value, not a range end.
  - 1.15 is the FAO pea/bean family value: a borrowed exploratory perturbation.

## Q6. Chamber-to-field transfer for legume heat parameters

**Verdict: the direction (controlled environments show heat damage at lower temperatures, i.e. overstate
sensitivity) has primary support for chickpea pod set and Brassica yield, with offsets of about 2–4 °C on day
temperature. There is no evidence on the slope multiplier, so ×0.7 is an exploratory perturbation. The +3 °C
T_crit test is an exploratory perturbation whose direction and order of magnitude are informed by the literature.**

- **Devasirvatham et al. 2013**, *Field Crops Res.* 142: 9–19, doi:10.1016/j.fcr.2012.11.011. Read level: full text
  (ICRISAT post-print). This audit adds verbatim quotes beyond LV-NC §2c:
  - Abstract (p. 2): "Overall, pod set showed greater sensitivity in the controlled environments where a 67%
    reduction was observed at ≥ 34/19˚C compared to the control (27/16˚C). In the field, a pod set reduction of more
    than 50% occurred at high ambient day temperature (36˚C)".
  - Discussion (p. 18): "short style was observed in heat sensitive genotypes such as ICC 4567 in both field (39˚C)
    and controlled environments (35˚C). Plants were continuously stressed for more than 10 days in the field and seven
    days in the controlled environments".
  - Outcome: pod set, not yield. Four genotypes. Day temperatures.
- **Morrison & Stewart 2002** (abstract): growth cabinet >27 °C vs field threshold 29.5 °C (daily T_max) for B.
  napus. Same direction, about 2.5 °C. Different metrics (cabinet set-point vs field daily maximum).
- **Hatfield et al. 2011, p. 358** (full text): "plant temperatures can be quite different than air temperatures and
  can be warmer than air under water stressed conditions or cooler than air under adequate soil water conditions".
  The chamber studies used here were well watered (Bhandari: pots irrigated three times a day), which is a mechanism
  that can run either way. Not quantified.
- **Within-project comparison** (LV-NC §2f, DERIVED): soybean chamber onset ≈ T_eff 28.5 vs Deryng 35.
- **No study was found that gives a field/chamber ratio for yield slopes.** The ×0.7 factor (PARAM_RANGES "new
  legumes: heat slope x0.7") is an **exploratory perturbation**. The bean "+2 °C (Mesoamerican types)" row is also an
  exploratory perturbation: Boote 2005 states only that Andean red kidney is heat-susceptible relative to Mesoamerican
  types, with no magnitude.

## Q7. FAOSTAT "Beans, dry" (item 0176) vs Phaseolus vulgaris parameters

**Verdict: FAO's own definition says several countries include Vigna species in this item. India and Myanmar are
ranks 1 and 3 of the bean panel (26.5 % and 8.8 % of 2020–24 world production). Phaseolus-based heat and K_y
parameters are poorly applicable to those two pairs. No Vigna-specific replacement was assessed.**

- **FAO, *Definition and Classification of Commodities*, ch. 4 "Pulses and derived products"** (FAO 1994). Read
  level: full page, archived copy (https://web.archive.org/web/2015/http://www.fao.org/es/faodef/fdef04e.htm; the
  live fao.org page now returns 404; exact snapshot timestamp not recorded; FAOSTAT definitions API returned error
  521). Verbatim:

  > "0176 BEANS, DRY Phaseolus spp. : kidney, haricot bean (Ph. vulgaris); lima, butter bean (Ph. lunatus); adzuki
  > bean (Ph. angularis); mungo bean, golden, green gram (Ph. aureus); black gram, urd (Ph. mungo); scarlet runner
  > bean (Ph. coccineus); rice bean (Ph. calcaratus); moth bean (Ph. aconitifolius); tepary bean (Ph. acutifolius)
  > Only species of Phaseolus should be included, though several countries also include certain types of beans.
  > Commonly classified as Vigna (angularis, mungo, radiata, aconitifolia). In the past, these species were also
  > classified as Phaseolus."

  Even the "should be included" list contains mung, urd, adzuki and moth beans under their old Phaseolus names.
- **USDA-ARS Phaseolus Crop Germplasm Committee (2020)**, *Phaseolus Beans – Crop Vulnerability Statement*
  (ars-grin.gov). Read level: full text (PDF). Not peer-reviewed. Table 2 footnote (p. 5): "Production amounts from
  FAO data combine common bean with other grain legumes, leading to inflated figures for SE Asia and China (Myers &
  Kmiecik, 2017). It is estimated that Vigna spp. account for 93% of dry bean production in India and 56% in China
  (Akibode and Maredia, 2011). Proportions for other SE Asian countries are unknown." The 93 % is a
  secondary-of-secondary estimate (Akibode & Maredia 2011 is a report, not read).
- **Project data** (`data/processed/nine_crop/panels.csv`, 2020–24): India 7.88 Mt (26.5 %, rank 1); Myanmar 2.63 Mt
  (8.8 %, rank 3).
- **Implication:**
  - For India, and probably Myanmar (no verified share), the "bean" pair is mostly Vigna: mung and urd.
  - Those crops differ from red kidney bean in season (largely kharif, and summer crops in Myanmar), heat tolerance
    and K_y (FAO has no Vigna K_y).
  - The bean calendar (Sacks Pulses, 86 % gap-filled) and the T_crit/s_T derived from cv. Montcalm are therefore
    poorly applicable there.
  - SPAM's BEAN class follows FAOSTAT and inherits the same scope. This is an inference; SPAM documentation was not
    checked.
  - Recommendation: flag the India and Myanmar bean pairs as "Phaseolus parameters applied to a mainly-Vigna item" in
    results, or report them separately. No replacement is proposed.

## Q8. Observed calendars for chickpea, lentil and rapeseed

**Verdict: chickpea and lentil have no global gridded crop-specific observed calendar, so keep the cool-season
proxy, labelled. Rapeseed does have one: the GGCMI Phase 3 calendar. It is a credible candidate for a sensitivity
run, but not a verified improvement.**

- **MIRCA2000** (Portmann et al. 2010, *Global Biogeochem. Cycles* 24: GB1011, doi:10.1029/2008GB003435; class list
  read on the Goethe-University MIRCA page). It has 26 classes, including "rape seed/canola", "groundnuts/peanuts"
  and a generic "pulses". It has no chickpea or lentil class. So the coordinator's premise is right for chickpea and
  lentil but not for rapeseed, which MIRCA2000 does cover.
- **GGCMI Phase 3 crop calendar** (Jägermeyr et al. 2021, Zenodo doi:10.5281/zenodo.5062513, DataCite-verified;
  method in Jägermeyr et al. 2021 *Nature Food* 2: 873–885, already in refs.bib).
  - Record description (verbatim): "provides in each 0.5° land grid cell the planting day and maturity day for 18
    different crops, separating rainfed and irrigated systems."
  - File list read this audit: includes `rap`, `bea`, `nut`, `pea`; **no chickpea and no lentil**.
  - `rap_rf` and `bea_rf` were downloaded and read with netCDF4. The variable `data_source_used` is coded "1 - MIRCA;
    2 - SAGE; 3 - IIZUMI et al. 2019; … 7. IndiaAgStat; 8. Brazil CONAB; 9. Australia ABARES".
  - Rapeseed spot cells (planting/maturity day of year, source):
    - Rajasthan 273/53 (IndiaAgStat), Haryana 280/39 (IndiaAgStat), Uttar Pradesh 274/53 (IndiaAgStat), Maharashtra
      304/53 (IndiaAgStat);
    - Saskatchewan and Alberta 91/266 (MIRCA);
    - Poland 245/176 (SAGE);
    - Hubei 334/112 (SAGE).
  - Caveats: it gives maturity, not harvest; one season per cell; the Canadian planting day 91 is earlier than the
    cool-season rule's ≈136 (decision E7). **Replacement supported: partial (sensitivity run).**
- **FAO Crop Calendar** (cropcalendar.apps.fao.org; API read this audit). It covers 58 countries at
  agro-ecological-zone level and lists "Chick-pea" and "Lentil" for, e.g., Ethiopia, Pakistan and Myanmar. It does not
  cover India, Australia, Canada, Türkiye, the USA or China (not in its country list) and is not gridded, so it
  cannot replace the proxy for the panels.
- RiceAtlas is rice-only. SAGE (Sacks) has no chickpea or lentil calendar (E7).

## Q9. PARAM_RANGES and the T_crit −2..+3 °C offsets

| Range (code) | Status |
|---|---|
| T_crit −2, −1, +1, +2, +3 °C, all crops (`TCRIT_OFFSETS`) | **exploratory perturbation**. For rice only, the cultivar threshold spread of 32–36.5 °C (Yoshida, anthesis metric; LV1 §3) is a literature range of similar width, but it is not a CI. |
| New legumes T_crit +3 °C | **exploratory perturbation**, with literature-informed direction and order of magnitude (Q6) |
| Bean T_crit +2 °C | **exploratory perturbation** (no published magnitude) |
| New legumes s_T × 0.7 | **exploratory perturbation** (no source for 0.7) |
| Rapeseed s_T 0.07 / 0.18 | **exploratory perturbation** (around a borrowed central value) |
| Rice K_y 1.0 / 1.5 | **exploratory perturbation** (no rice K_y exists) |
| Chickpea K_y 0.67 / 1.15 | **exploratory perturbation**. 0.67 is a secondary citation of a simulation study whose abstract has no K_y (Jalota 2006, doi:10.1016/j.agwat.2005.02.014); 1.15 is borrowed (FAO pea/bean). |
| Lentil K_y 0.87 / 1.15 | 0.87 = **treatment value** (Nandi 2021 best treatment); 1.15 borrowed, i.e. an **exploratory perturbation** |
| Bean K_y 0.6 / 1.4 | **literature range**: two IAEA field values, 0.59 and 1.43 (FAO-66 Table 2; FAO Water Report 22 Table 2, verified this audit), not a CI |
| Rapeseed K_y 0.85 / 0.95 | **exploratory perturbation** bracketing 0.87 (field, abstract) and 0.93 (secondary) |
| Calendar = plain Sacks (chickpea, lentil, rapeseed) | **exploratory perturbation** with an alternative dataset |

## Other parameters (brief status; details in the register)

- **Wheat, maize, soybean heat** (Deryng 2014 Table A.1: 25/35, 32/45, 35/40 on T_eff): published model parameters,
  verified in the mid-evaluation (LV1 §2). Not re-read here: the IOP PDF is bot-protected, and a partial download
  was truncated.
  - Caveats: spring-wheat values are applied to winter wheat; Deryng works on daily T_eff while the index uses
    monthly T_eff.
  - The 45–70 % window is in GDD in Deryng (known only from a page summary, LV2 addendum). The index uses calendar
    days, which for long winter-wheat or winter-rapeseed seasons likely places the window before anthesis. This is
    my reasoning and was not quantified.
- **K_y (FAO-33 via FAO-66):** maize 1.25, soybean 0.85, bean 1.15 and groundnut 0.70 are published. Wheat 1.10 is
  derived (mean of 1.15 and 1.05). Rapeseed 0.90 is published in FAO-56 Rev.1 without a stated source.
- **Kc (FAO-56 Table 12):**
  - Kc end values are derived midpoints: rice 0.75 of 0.90–0.60; maize 0.48 of 0.60–0.35; wheat 0.33 of 0.25–0.4.
  - Wheat Kc ini 0.40 is the winter-wheat frozen-soil row (spring wheat 0.3 group; non-frozen 0.7).
  - Group-row Kc ini values for maize, soybean and the legumes are a reading of the table layout.
- **Stage days:** published FAO-56 Table 11 rows. Chickpea uses the lentil row (borrowed). Rapeseed uses FAO-56 Rev.1
  canola GDD shares as day shares (borrowed). Only proportions matter.
- **Derived legume fits** (chickpea 34.0/0.14, lentil 31.9/0.17, groundnut 31.8/0.095, bean 25.5/0.111) are reproduced
  by `code/25_parameter_fits.py` (LV-NC §8.7). They are chamber-based and kept as labelled proxies.

## Parameters that remain unsupported or only partially applicable

**Unsupported (mark as such):**
1. Rapeseed heat slope s_T = 0.10/°C: borrowed from wheat; no Brassica slope found.
2. Rice heat slope 0.07/°C *as a yield slope on T_eff*: a fertility slope on tissue temperature above 29.6 °C,
   applied above 35 °C T_eff.

**Labelled proxies / partially applicable:**
- Rice K_y 1.25 (maize value; no rice K_y).
- Rice T_crit 35 (fertility threshold, unconverted).
- Rapeseed T_crit 26.5 (assumed DTR; daily-to-monthly change of meaning).
- Rapeseed species transfer to B. juncea.
- Lentil K_y 1.0 (FAO-definition compatibility partial).
- Chickpea K_y 0.88 (one site).
- All chamber-derived legume T_crit/s_T values (chickpea, lentil, bean, groundnut).
- Bean parameters for India and Myanmar (FAOSTAT item mostly Vigna).
- Bean calendar (86 % gap-filled generic Pulses).
- Cool-season calendar rule for chickpea, lentil and rapeseed.
- The 45–70 % calendar-day flowering window for all crops (GDD in Deryng; borrowed for non-Deryng crops).
- The temperature-metric conversions (Q4).
- Spring-wheat heat parameters for winter wheat.
- Rapeseed Kc mid 1.15 for a mostly rainfed crop.
- The water-deficit metric P/ETc used in place of ETa/ETm with FAO K_y.

**Ranges that are exploratory perturbations:** see Q9. All of them except bean K_y 0.6–1.4 (literature range) and
lentil K_y 0.87 (treatment value).

## Proposed replacements

**None is genuinely supported as a drop-in replacement.** Partial candidates, for sensitivity runs only:
- Rice heat: T_crit,eff ≈ 26.75 °C, s_T ≈ 0.10/°C. Baker et al. 1995 via Hatfield et al. 2011 (secondary;
  chamber, season-long, yield), with Baker et al. 1992 abstract-level support (IR-30).
- Rapeseed calendar: GGCMI Phase 3 `rap` calendar (Jägermeyr et al. 2021; Zenodo 10.5281/zenodo.5062513).
- Bean calendar: GGCMI Phase 3 `bea` calendar (not evaluated; and it does not solve the Vigna scope problem).

---

## BibTeX for new sources (Crossref-verified unless stated)

```bibtex
@article{baker1992rice,
  author = {Baker, J. T. and Allen, L. H. and Boote, K. J.},
  title = {Temperature effects on rice at elevated {CO2} concentration},
  journal = {Journal of Experimental Botany}, volume = {43}, number = {7}, pages = {959--964}, year = {1992},
  doi = {10.1093/jxb/43.7.959}}
@incollection{baker1995rice,
  author = {Baker, Jeffrey T. and Boote, Kenneth J. and Allen, Leon Hartwell},
  title = {Potential climate change effects on rice: carbon dioxide and temperature},
  booktitle = {Climate Change and Agriculture: Analysis of Potential International Impacts},
  series = {ASA Special Publication}, number = {59}, pages = {31--47}, year = {1995},
  doi = {10.2134/asaspecpub59.c2}, note = {Not read; cited via Hatfield et al. 2011}}
@article{hatfield2011,
  author = {Hatfield, J. L. and Boote, K. J. and Kimball, B. A. and Ziska, L. H. and Izaurralde, R. C. and Ort, D. and Thomson, A. M. and Wolfe, D.},
  title = {Climate impacts on agriculture: implications for crop production},
  journal = {Agronomy Journal}, volume = {103}, number = {2}, pages = {351--370}, year = {2011},
  doi = {10.2134/agronj2010.0303}}
@article{prasad2006rice,
  author = {Prasad, P. V. V. and Boote, K. J. and Allen, L. H. and Sheehy, J. E. and Thomas, J. M. G.},
  title = {Species, ecotype and cultivar differences in spikelet fertility and harvest index of rice in response to high temperature stress},
  journal = {Field Crops Research}, volume = {95}, number = {2--3}, pages = {398--411}, year = {2006},
  doi = {10.1016/j.fcr.2005.04.008}}
@article{peng2004,
  author = {Peng, Shaobing and Huang, Jianliang and Sheehy, John E. and Laza, Rebecca C. and Visperas, Romeo M. and Zhong, Xuhua and Centeno, Grace S. and Khush, Gurdev S. and Cassman, Kenneth G.},
  title = {Rice yields decline with higher night temperature from global warming},
  journal = {Proceedings of the National Academy of Sciences}, volume = {101}, number = {27}, pages = {9971--9975}, year = {2004},
  doi = {10.1073/pnas.0403720101}}
@article{welch2010,
  author = {Welch, Jarrod R. and Vincent, Jeffrey R. and Auffhammer, Maximilian and Moya, Piedad F. and Dobermann, Achim and Dawe, David},
  title = {Rice yields in tropical/subtropical {Asia} exhibit large but opposing sensitivities to minimum and maximum temperatures},
  journal = {Proceedings of the National Academy of Sciences}, volume = {107}, number = {33}, pages = {14562--14567}, year = {2010},
  doi = {10.1073/pnas.1001222107}}
@article{anupoju2020,
  author = {Anupoju, Varaprasad and Kambhammettu, B. V. N. P.},
  title = {Role of deficit irrigation strategies on {ET} partition and crop water productivity of rice in semi-arid tropics of south {India}},
  journal = {Irrigation Science}, volume = {38}, number = {4}, pages = {415--430}, year = {2020},
  doi = {10.1007/s00271-020-00684-1}}
@article{raes2007,
  author = {Raes, D. and Kafiriti, E. M. and Wellens, J. and Deckers, J. and Maertens, A. and Mugogo, S. and Dondeyne, S. and Descheemaeker, K.},
  title = {Can soil bunds increase the production of rain-fed lowland rice in south eastern {Tanzania}?},
  journal = {Agricultural Water Management}, volume = {89}, number = {3}, pages = {229--235}, year = {2007},
  doi = {10.1016/j.agwat.2007.01.005}}
@article{guimaraes2016,
  author = {Guimar{\~a}es, Cleber M. and Stone, Lu{\'i}s F. and Silva, Ana C. de L.},
  title = {Evapotranspiration and grain yield of upland rice as affected by water deficit},
  journal = {Revista Brasileira de Engenharia Agr{\'i}cola e Ambiental}, volume = {20}, number = {5}, pages = {441--446}, year = {2016},
  doi = {10.1590/1807-1929/agriambi.v20n5p441-446}}
@article{kutcher2010,
  author = {Kutcher, H. R. and Warland, J. S. and Brandt, S. A.},
  title = {Temperature and precipitation effects on canola yields in {Saskatchewan}, {Canada}},
  journal = {Agricultural and Forest Meteorology}, volume = {150}, number = {2}, pages = {161--165}, year = {2010},
  doi = {10.1016/j.agrformet.2009.09.011}}
@article{angadi2000,
  author = {Angadi, S. V. and Cutforth, H. W. and Miller, P. R. and McConkey, B. G. and Entz, M. H. and Brandt, S. A. and Volkmar, K. M.},
  title = {Response of three {Brassica} species to high temperature stress during reproductive growth},
  journal = {Canadian Journal of Plant Science}, volume = {80}, number = {4}, pages = {693--701}, year = {2000},
  doi = {10.4141/P99-152}}
@article{gan2004,
  author = {Gan, Y. and Angadi, S. V. and Cutforth, H. and Potts, D. and Angadi, V. V. and McDonald, C. L.},
  title = {Canola and mustard response to short periods of temperature and water stress at different developmental stages},
  journal = {Canadian Journal of Plant Science}, volume = {84}, number = {3}, pages = {697--704}, year = {2004},
  doi = {10.4141/P03-109}}
@article{nuttall1992,
  author = {Nuttall, W. F. and Moulin, A. P. and Townley-Smith, L. J.},
  title = {Yield response of canola to nitrogen, phosphorus, precipitation, and temperature},
  journal = {Agronomy Journal}, volume = {84}, number = {5}, pages = {765--768}, year = {1992},
  doi = {10.2134/agronj1992.00021962008400050001x}}
@article{jalota2006,
  author = {Jalota, S. K. and Sood, Anil and Harman, W. L.},
  title = {Assessing the response of chickpea ({Cicer aeritinum} {L}.) yield to irrigation water on two soils in {Punjab} ({India}): a simulation analysis using the {CROPMAN} model},
  journal = {Agricultural Water Management}, volume = {79}, number = {3}, pages = {312--320}, year = {2006},
  doi = {10.1016/j.agwat.2005.02.014}}
@article{portmann2010,
  author = {Portmann, Felix T. and Siebert, Stefan and D{\"o}ll, Petra},
  title = {{MIRCA2000}---Global monthly irrigated and rainfed crop areas around the year 2000: a new high-resolution data set for agricultural and hydrological modeling},
  journal = {Global Biogeochemical Cycles}, volume = {24}, number = {1}, pages = {GB1011}, year = {2010},
  doi = {10.1029/2008GB003435}}
@misc{ggcmi3calendar,
  author = {J{\"a}germeyr, Jonas and M{\"u}ller, Christoph and Minoli, Sara and Ray, Deepak and Siebert, Stefan},
  title = {{GGCMI} Phase 3 crop calendar}, howpublished = {Zenodo}, year = {2021},
  doi = {10.5281/zenodo.5062513}, note = {DataCite-verified (not a Crossref DOI)}}
% --- no DOI; not Crossref-verifiable ---
@misc{fao1994commodities,
  author = {{FAO}}, title = {Definition and Classification of Commodities, 4. Pulses and Derived Products},
  year = {1994}, howpublished = {\url{https://web.archive.org/web/2015/http://www.fao.org/es/faodef/fdef04e.htm}},
  note = {Archived copy read 18 November 2026; live FAO page no longer available}}
@incollection{moutonnet2002,
  author = {Moutonnet, P.}, title = {Yield response factors of field crops to deficit irrigation},
  booktitle = {Deficit Irrigation Practices}, series = {FAO Water Reports}, number = {22}, publisher = {FAO}, address = {Rome}, year = {2002},
  howpublished = {\url{https://www.fao.org/4/y3655e/y3655e04.htm}}}
@techreport{phaseoluscgc2020,
  author = {{Phaseolus Crop Germplasm Committee}},
  title = {Phaseolus Beans -- Crop Vulnerability Statement (September 2020)},
  institution = {USDA-ARS National Plant Germplasm System}, year = {2020},
  url = {https://www.ars-grin.gov/documents/cgc/cvs/2020-Phaseolus%20Crop%20Vulnerability%20Statement.pdf}, note = {Not peer-reviewed}}
```

## Gaps and access notes

- Full texts not accessible (paywall or bot protection): Morrison & Stewart 2002, Kutcher 2010, Nandi 2021, Raes 2007,
  Anupoju 2020, Baker 1992 (OUP Cloudflare), Prasad 2002/2003 (LV-NC §6), Deryng 2014 PDF (IOP bot check this audit;
  a truncated download was not used).
- Not read: Baker et al. 1995 (book chapter), Akibode & Maredia 2011, Myers & Kmiecik 2017, the Indian mustard
  sowing-date literature.
- Downloads were kept in the session scratchpad `papers_params\` folder and treated as data.
