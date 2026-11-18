"""
22_literature_comparison.py -- comparison of our results with published findings (commitment C7).
Published values are copied from docs/literature_comparison_sources.md (each verified there with a quote,
page/table and read level). Our comparable quantity is COMPUTED here from the result tables, so every row
pairs a sourced number with a reproducible one. Only signs and rank orders are compared, never an index
value with a yield percentage. Output: data/processed/nine_crop/literature_comparison.csv
"""
import os

import numpy as np
import pandas as pd

from config import MYERS, PROC

P = lambda f: os.path.join(PROC, f)


def main():
    comp = pd.read_csv(P("index_components.csv"))
    crop = pd.read_csv(P("index_crop.csv")).set_index("crop")
    fy = pd.read_csv(P("future_yield.csv"))
    fc = pd.read_csv(P("future_components.csv"))
    vz = pd.read_csv(P("val_zhao.csv")).set_index("measure")
    adq = pd.read_csv(P("adequacy.csv"))
    imp = pd.read_csv(P("importance.csv"))
    pair = lambda c, k: comp[(comp.crop == c) & (comp.country == k)].iloc[0]
    fpair = lambda c, k: fy[(fy.crop == c) & (fy.country == k)].iloc[0]
    rows = []

    def add(pid, paper, crop_, geo, period, scen, published, ours, agree, why):
        rows.append({"id": pid, "paper": paper, "crop": crop_, "geography": geo, "period": period, "scenario": scen,
                     "published_finding": published, "our_comparable_result": ours, "agreement": agree, "interpretation": why})

    # 1 Zhao 2017: crop ordering of temperature sensitivity
    clim = comp.assign(es=comp.ES_paired).groupby("crop").es.mean()
    add("Z1", "Zhao et al. 2017 PNAS", "wheat, rice, maize, soybean", "global", "+1 C", "no CO2, no adaptation",
        "yield change per +1 C: maize -7.4, wheat -6.0, rice -3.2, soybean -3.1 (n.s.) -> maize > wheat > rice > soybean",
        f"climate part E x S (equal weights): " + " > ".join(clim.reindex(["maize", "wheat", "rice", "soybean"]).sort_values(ascending=False).index)
        + f"; Spearman rho with Zhao = {vz.loc['climate part E x S (hazard-paired, no I)', 'rho']:+.1f} (n = 4)",
        "agree (order of maize, wheat)" if clim["maize"] > clim["wheat"] else "partial",
        "Our climate part (E x S, no importance) orders maize above wheat as Zhao does; rice and soybean swap (Zhao's soybean estimate is not significant). Importance, not climate, moves wheat above maize in the full index. n = 4: descriptive only.")
    # 2 Zhao 2017 country: wheat India largest loss
    w = comp[comp.crop == "wheat"].set_index("country")
    add("Z2", "Zhao et al. 2017 PNAS (Fig. 3)", "wheat", "India, Russia, USA, China", "+1 C", "no CO2",
        "wheat loss per +1 C: India -9.1, Russia -7.8, USA -5.5, China -2.6 %",
        "wheat heat exposure E_heat: " + ", ".join(f"{k.split(',')[0].replace('Russian Federation', 'Russia').replace('United States of America', 'USA')} {w.loc[k, 'E_heat']:.3f}"
                                                   for k in ["India", "Russian Federation", "United States of America", "China, mainland"]),
        "agree (heat)" if w.loc["India", "E_heat"] == w.loc[["India", "Russian Federation", "United States of America", "China, mainland"], "E_heat"].max() else "differ",
        "India has the highest wheat heat exposure in both; Russia's high index score comes from water deficit, a channel Zhao's temperature regression does not isolate.")
    # 3 Lobell 2011
    r = pair("wheat", "Russian Federation")
    add("L1", "Lobell, Schlenker & Costa-Roberts 2011 Science", "wheat", "Russia", "1980-2008", "observed trends",
        "Russia wheat production about -15 % from temperature trends",
        f"wheat-Russia F4 = {r.F4_hazard_paired:.4f} (top pair); heat part {0.5 * r.E_heat * r.S_heat * r.In:.4f} vs water part {0.5 * r.E_water * r.S_water * r.In:.4f}",
        "differ (mechanism)", "Both flag Russian wheat; Lobell attributes it to temperature, our monthly-threshold measure attributes it mostly to rainfed water deficit (heat above 25 C T_eff is rare in monthly means).")
    # 4 Ray 2015 / 2019 rice least climate-driven
    order_es = clim.sort_values()
    add("R1", "Ray et al. 2015 Nat. Commun.; Ray et al. 2019 PLoS ONE", "rice vs other cereals and soybean", "global", "~1979-2008; recent",
        "observed", "climate explains 32-39 % of yield variability; rice least",
        f"rice climate part E x S = {clim['rice']:.4f}, lowest of the four ({', '.join(f'{k} {clim[k]:.4f}' for k in ['wheat', 'maize', 'soybean'])})",
        "not directly comparable (different outcome)",
        "Ray et al. measure the share of observed yield VARIABILITY that climate explains, not vulnerability. Low explained variability is "
        "not evidence of low vulnerability (irrigation can buffer variability, and damage that monthly data cannot see is not in either "
        "measure). Our rice climate part is lowest of the four, in line with their ordering, but the earlier reading as independent "
        "support for a low rice score is withdrawn (18-19 Nov 2026 audit).")
    # 5 Deryng 2014 future no CO2
    fym = fy.groupby("crop").dY_lit_pct.mean()
    add("D1", "Deryng et al. 2014 ERL (Table 1)", "maize, wheat, soybean", "global", "2050s", "RCP8.5 without CO2 (RCP4.5 with CO2 in brackets)",
        "maize -10.5, wheat -10.1, soybean -6.9 % (RCP4.5 with CO2: -4.9, +13.0, +10.8)",
        "our conditional yield change (mean over countries, no CO2): " + ", ".join(f"{k} {fym[k]:+.1f} %" for k in ["maize", "wheat", "soybean"]),
        "; ".join([("sign agrees" if np.sign(fym[k]) == -1 else "sign differs") + f" for {k}" for k in ["maize", "wheat", "soybean"]]) + "; our magnitudes smaller", "Ours counts only heat above thresholds and rainfed deficit at monthly resolution under SSP2-4.5, so smaller losses are expected; with CO2 fertilisation C3 wheat and soybean gain in Deryng, which our index excludes.")
    # 6 Challinor 2014
    neg = (fy.dY_lit_pct < 0).mean()
    add("C1", "Challinor et al. 2014 Nat. Clim. Change", "wheat, rice, maize", "global", "2040s-2050s", "mixed",
        "> 70 % of projections show yield losses", f"{100 * neg:.0f} % of our 59 pairs show a climate-driven yield loss (literature accounting); cereals only: {100 * (fy[fy.group == 'cereal'].dY_lit_pct < 0).mean():.0f} %",
        "agree" if neg > 0.7 else "partial", "Our losses come only from heat above crop thresholds and rainfed deficit; pairs below the heat threshold and getting wetter show gains.")
    # 7 Ramirez-Cabral 2017 maize
    mz = fc[fc.crop == "maize"].set_index("country")
    add("RC", "Ramirez-Cabral et al. 2017 Sci. Rep.", "maize", "Africa, South America, India", "2050", "A2 (approx. RCP8.5), 2 GCMs",
        "suitable area: Africa -7 to -11 %, South America -5 %, India marginal areas become unsuitable",
        "maize change in F4 2041-60 vs 1971-2000: " + ", ".join(f"{k.replace(', mainland', '')} {mz.loc[k, 'dF4_abs']:+.4f}" for k in ["South Africa", "Brazil", "India"]),
        "differ", "Our maize scores fall in South Africa because MRI-ESM2-0 gives a smaller rainfed deficit there; suitability models use annual climate envelopes and more extreme scenarios. Single-GCM result.")
    # 8 Rippke 2016 / Hummel 2018 beans in East/South-East Africa
    bt = fpair("bean", "United Republic of Tanzania")
    add("RP/HU", "Rippke et al. 2016 Nat. Clim. Change; Hummel et al. 2018 Sci. Rep.", "common bean", "sub-Saharan / SE Africa", "2040-2069 (HU); 2050s (RP)",
        "RCP6.0 / RCP8.5", "beans ~10 % area needing transformation in Uganda/Tanzania by the 2050s (RP); most SE African bean areas unsuitable by 2040-69, drought-driven (HU)",
        f"bean-Tanzania F4 change {fc[(fc.crop == 'bean') & (fc.country == 'United Republic of Tanzania')].dF4_abs.iloc[0]:+.4f}; conditional yield change {bt.dY_lit_pct:+.1f} %",
        "agree (direction)", "Beans are among the crops whose vulnerability rises most in our results too; ours is driven by heat above the bean threshold.")
    # 9 Qian 2019 canola Canada
    qc = fpair("rapeseed", "Canada")
    add("Q1", "Qian et al. 2019 ERL (Table 2)", "canola", "Canada", "+2 C global warming", "20 GCMs; CO2 fixed",
        "-0.8 to -5.7 % production at +2 C with CO2 fixed (+3 to +11 % with CO2)",
        f"rapeseed-Canada conditional yield change {qc.dY_lit_pct:+.1f} % (no CO2); flowering T_eff change {qc.dTeff_C:+.1f} C",
        "agree (sign)" if qc.dY_lit_pct < 0 else "differ", "Same sign when CO2 fertilisation is excluded.")
    # 10 Kalra 2008 chickpea / mustard India
    ch, ms = fpair("chickpea", "India"), fpair("rapeseed", "India")
    add("K1", "Kalra et al. 2008 Curr. Sci.", "chickpea, mustard", "NW India", "historic", "observed seasonal temperature",
        "yields fall with warmer seasons: chickpea -0.53 to -3.01, mustard -0.92 to -2.01 q/ha per C",
        f"India 2041-60: chickpea T_eff {ch.dTeff_C:+.1f} C, yield {ch.dY_lit_pct:+.1f} %; rapeseed-mustard T_eff {ms.dTeff_C:+.1f} C, yield {ms.dY_lit_pct:+.1f} %",
        "agree (sign)" if (ch.dY_lit_pct < 0 and ms.dY_lit_pct < 0) else "partial", "Direction consistent; Kalra is a seasonal-mean regression, ours a flowering-threshold measure.")
    # 11 Beach 2019 / Nelson 2018 iron
    last = int(adq.Year.max())
    ind = adq[(adq.m49 == 356) & adq.Year.between(last - 2, last)].mean(numeric_only=True)
    add("BE/NE", "Beach et al. 2019 Lancet Planet. Health; Nelson et al. 2018 Nat. Sustain.", "diet", "South Asia / global", "2050", "SSP2, RCP4.5/8.5",
        "South Asia iron availability below the recommended intake; micronutrients, not calories, are the binding constraint",
        f"India 2021-23 iron supply / requirement = {ind.nar_iron:.2f} (15 % bioavailability: {ind.nar_iron_15pct:.2f}); energy {ind.nar_kcal:.2f}, protein {ind.nar_protein:.2f}",
        "agree (main requirement)" if ind.nar_iron < 1 else "differ", "Consistent under the presented requirement; not under the more favourable bioavailability assumption.")
    # 12 Myers 2014 CO2 pathway (additional, not validation)
    sh = imp[imp.m49 == 356].set_index("crop")
    myers_fe = {c: MYERS[c]["iron"][0] for c in MYERS if MYERS[c]["iron"][1]}
    fe_loss = sum(sh.loc[c, "sh_iron"] * myers_fe[c] for c in myers_fe if c in sh.index)
    add("M1", "Myers et al. 2014 Nature", "wheat, rice, soybean (C3)", "FACE experiments", "-", "546-586 ppm CO2",
        "iron concentration: wheat -5.1, rice -5.2, soybean -4.1 % (significant)",
        f"applied to India's 2021-23 iron supply shares, these declines alone would lower national iron supply by {abs(fe_loss):.1f} % (an additional pathway the index excludes)",
        "additional pathway", "Not a validation: Myers values are an input here. It shows the CO2 channel would add to the climate channel on the nutrient already closest to shortfall. "
        "The full CO2 nutrient-quality stress test (all covered crops, with envelopes and coverage) is in 28_co2_quality.py and report Section 'elevated CO2'.")
    df = pd.DataFrame(rows)
    df.to_csv(P("literature_comparison.csv"), index=False)
    pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 120)
    print(df[["id", "our_comparable_result", "agreement"]].to_string(index=False))


if __name__ == "__main__":
    main()
