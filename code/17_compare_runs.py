"""
17_compare_runs.py -- the comparisons the end-evaluation plan asks for (written to data/processed/nine_crop/):

compare_mideval_vs_fourcrop.csv   P1: every pair, mid-evaluation (blended S, archive) vs four-crop literature-only run
compare_crop_rank_runs.csv        crop rankings: mid-evaluation / four-crop literature-only / nine-crop run
compare_fourcrop_vs_ninecrop.csv  P3: pairs present in both runs. Physical stress is identical, so any difference
                                  comes from the normalisation reference (heat, water, importance maxima and the
                                  literature-S maxima over crops). The F4 ratio is decomposed multiplicatively.
worked_example.csv                one pair (wheat, India) from raw components to F4 in each run
"""
import os

import numpy as np
import pandas as pd

from config import ROOT_DIR

P = lambda run, f: os.path.join(ROOT_DIR, "data", "processed", run, f)
MID = lambda f: os.path.join(ROOT_DIR, "archive", "mid_evaluation", "data", "processed", f)
OUT = lambda f: P("nine_crop", f)
F4 = "F4_hazard_paired"


def main():
    mid = pd.read_csv(MID("index_components.csv"))
    four = pd.read_csv(P("four_crop", "index_components.csv"))
    nine = pd.read_csv(P("nine_crop", "index_components.csv"))

    # P1: mid-evaluation (blended) vs four-crop literature-only, same 26 pairs
    a = mid[["crop", "country", "S_heat", "S_water", F4]].merge(
        four[["crop", "country", "E_heat", "E_water", "S_heat", "S_water", "In", F4]], on=["crop", "country"], suffixes=("_mideval", "_lit"))
    a["ratio_lit_to_mideval"] = a[f"{F4}_lit"] / a[f"{F4}_mideval"]
    a["rank_mideval"] = a[f"{F4}_mideval"].rank(ascending=False).astype(int)
    a["rank_lit"] = a[f"{F4}_lit"].rank(ascending=False).astype(int)
    a.to_csv(OUT("compare_mideval_vs_fourcrop.csv"), index=False)

    rows = []
    for label, path in (("mid-evaluation (blended S)", MID("index_crop.csv")),
                        ("four-crop, literature-only S", P("four_crop", "index_crop.csv")),
                        ("nine-crop, literature-only S", P("nine_crop", "index_crop.csv"))):
        c = pd.read_csv(path)
        for wt in ("eq", "pw"):
            order = c.sort_values(f"{F4}_{wt}", ascending=False)
            rows.append({"run": label, "weighting": wt, "order": " > ".join(order.crop),
                         "order_original_four": " > ".join(order.crop[order.crop.isin(["rice", "wheat", "maize", "soybean"])]),
                         **{f"{k}": v for k, v in zip(order.crop, order[f"{F4}_{wt}"])}})
    pd.DataFrame(rows).to_csv(OUT("compare_crop_rank_runs.csv"), index=False)

    # P3: normalisation-reference effect on pairs common to both runs
    ref4 = pd.read_csv(P("four_crop", "index_reference.csv")).set_index("quantity").max_value
    ref9 = pd.read_csv(P("nine_crop", "index_reference.csv")).set_index("quantity").max_value
    b = four.merge(nine, on=["crop", "country"], suffixes=("_4", "_9"))
    b["heat_ref_ratio"] = ref4["H_heat"] / ref9["H_heat"]
    b["water_ref_ratio"] = ref4["H_water"] / ref9["H_water"]
    b["importance_ref_ratio"] = ref4["I"] / ref9["I"]
    b["S_heat_ratio"] = b.S_heat_9 / b.S_heat_4
    b["S_water_ratio"] = b.S_water_9 / b.S_water_4
    b["H_heat_identical"] = np.isclose(b.H_heat_4, b.H_heat_9)
    b["H_water_identical"] = np.isclose(b.H_water_4, b.H_water_9)
    b["F4_ratio_9_to_4"] = b[f"{F4}_9"] / b[f"{F4}_4"]
    b["rank_within_original_pairs_4"] = b[f"{F4}_4"].rank(ascending=False).astype(int)
    b["rank_within_original_pairs_9"] = b[f"{F4}_9"].rank(ascending=False).astype(int)
    keep = ["crop", "country", f"{F4}_4", f"{F4}_9", "F4_ratio_9_to_4", "heat_ref_ratio", "water_ref_ratio", "importance_ref_ratio",
            "S_heat_ratio", "S_water_ratio", "H_heat_identical", "H_water_identical", "rank_within_original_pairs_4", "rank_within_original_pairs_9"]
    b[keep].to_csv(OUT("compare_fourcrop_vs_ninecrop.csv"), index=False)

    # worked example: wheat, India
    ex = []
    for run, comp, ref in (("four_crop", four, ref4), ("nine_crop", nine, ref9)):
        r = comp[(comp.crop == "wheat") & (comp.country == "India")].iloc[0]
        sens = pd.read_csv(P(run, "sensitivity.csv")).query("crop == 'wheat' and country == 'India'").iloc[0]
        sm = pd.read_csv(P(run, "sensitivity.csv"))
        ex.append({"run": run, "L_heat_C": r.H_heat, "max_L_heat": ref["H_heat"], "E_heat": r.E_heat,
                   "L_water": r.H_water, "max_L_water": ref["H_water"], "E_water": r.E_water,
                   "s_T_per_C": sens.s_lit_heat, "max_s_T": sm.s_lit_heat.max(), "S_heat": r.S_heat,
                   "K_y": sens.s_lit_water, "max_K_y": sm.s_lit_water.max(), "S_water": r.S_water,
                   "sh_kcal": r.sh_kcal, "sh_protein": r.sh_protein, "sh_fat": r.sh_fat, "sh_zinc": r.sh_zinc, "sh_iron": r.sh_iron,
                   "I": r.I, "max_I": ref["I"], "I_norm": r.In,
                   "F4_by_hand": 0.5 * (r.E_heat * r.S_heat + r.E_water * r.S_water) * r.In, "F4_pipeline": r[F4]})
    ex = pd.DataFrame(ex)
    assert np.allclose(ex.F4_by_hand, ex.F4_pipeline), ex
    ex.to_csv(OUT("worked_example.csv"), index=False)
    pd.set_option("display.width", 250)
    print(pd.DataFrame(rows)[["run", "weighting", "order"]].to_string(index=False))
    print(ex.T.to_string())


if __name__ == "__main__":
    main()
