"""
29_diversity_losses.py -- national food-source diversity and nutrient adequacy AFTER crop losses
(research extension 4).

Diversity is computed on the WHOLE national food supply (every FAOSTAT FBS leaf item with supply), never by
renormalising the nine study crops. Categories = FBS leaf items (the classification of the existing
diversity table, 21_india_hyderabad.py, and of Remans et al. 2014), listed in food_categories_fbs.csv and
held fixed across baseline and scenarios. For each nutrient: total supply, Shannon entropy H of the item
shares, effective number of sources exp(H), largest source share; and NAR/MAR beside them.

Scenarios (all on the 2021-23 national supply; quantity accounting of ext_common.py, upper bound unless
stated):
  A  single-crop standard loss: one crop loses 10 % of domestic production (the existing S3 shock)
  B  simultaneous loss STRESS TEST: every modelled crop of the country loses 10 % at once
  C  future climate, loss-only: each modelled pair's conditional literature yield change
     (16_future_yield_nutrition.py; 1971-2000 -> 2041-2060, applied to 2021-23 supply = HYBRID
     counterfactual), losses only; gains are listed but not added (convention of decision E14)
  C' the same with the present-relative yield change (observed 2001-2024 -> 2041-2060), sensitivity
  D  C combined with the elevated-CO2 nutrient-concentration stress test (28_co2_quality.py, primary
     evidence set; covered crop-nutrient combinations only, applied to the crop's whole eligible supply
     including imports), with low/high envelopes from the published confidence limits
Only modelled crop-country pairs (panels.csv) are shocked; nothing is extrapolated to other pairs.
No substitution, trade or household response is modelled.
Outputs: diversity_after_losses.csv, food_categories_fbs.csv, diversity_future_pairs_used.csv
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
import ext_common as E  # noqa: E402
from config import CROPS  # noqa: E402

STD_LOSS = 0.10


def scenario_row(label, country, area, crops, base_items, sua_c, qty, conc, req, base_metrics, extra=None):
    items_s, audit = E.apply_scenario(base_items, sua_c, qty, conc)
    neg = items_s[E.NUTRIENTS].lt(-1e-12) & ~base_items[E.NUTRIENTS].lt(-1e-12)
    if neg.any().any():
        bad = items_s.loc[neg.any(axis=1), "Item"].tolist()
        raise ValueError(f"{label} {area}: scenario creates negative supply in {bad}")
    assert list(items_s.Item) == list(base_items.Item), "category set changed"
    m = E.diversity_metrics(items_s)
    m.update(E.adequacy_metrics(m, req))
    r = {"scenario": label, "m49": country, "Area": area, "crops_shocked": ";".join(crops)}
    for k, v in m.items():
        r[k] = v
        if not isinstance(v, str):
            r[f"d_{k}"] = v - base_metrics[k]
    for n in E.NUTRIENTS:
        b = base_metrics[f"total_{n}"]
        r[f"pct_total_{n}"] = 100.0 * (m[f"total_{n}"] - b) / b if b else np.nan
    r["pct_total_mean5"] = float(np.mean([r[f"pct_total_{n}"] for n in E.NUTRIENTS]))
    r["parent_pulses_min_after"] = audit.get("parent_min", np.nan)
    r.update(extra or {})
    return r


def main():
    adq = pd.read_csv(E.P("adequacy.csv"))
    years = E.latest_years(adq)
    panels = pd.read_csv(E.P("panels.csv"))
    countries = sorted(set(panels.m49))
    items, sua = E.baseline_items(years, countries + [E.WORLD])
    bal = E.crop_balance(years)
    req = adq[adq.Year.isin(years)].groupby("m49").mean(numeric_only=True)
    fy = E.future_yield_reference_periods()
    co2_path = E.P("co2_concentration_factors.csv")
    co2 = pd.read_csv(co2_path) if os.path.exists(co2_path) else None

    # explicit, fixed category list
    cat = items.groupby("Item").agg(n_countries=("m49", "nunique")).reset_index()
    cat["study_crop"] = cat.Item.map(E.FBS_ITEM_CROP)
    cat["role"] = np.where(cat.Item == E.PARENT_PULSES, "FBS parent of SUA chickpea and lentil (removal target, not duplicated)",
                  np.where(cat.study_crop.notna() & cat.Item.str.contains("Oil"), "study-crop oil (same quantity fraction as primary)",
                  np.where(cat.study_crop.notna(), "study-crop primary product", "other food (unchanged in all scenarios)")))
    cat["co2_concentration_eligible"] = cat.apply(lambda r: bool(r.study_crop) and isinstance(r.study_crop, str)
                                                  and r.Item in E.eligible_items(r.study_crop), axis=1)
    cat.to_csv(E.P("food_categories_fbs.csv"), index=False)

    rows, used = [], []
    for m49 in countries + [E.WORLD]:
        bi = items[items.m49 == m49].reset_index(drop=True)
        if bi.empty or m49 not in req.index:
            continue
        area = bi.Area.iloc[0]
        sc = sua[sua.m49 == m49].set_index("crop")
        base = E.diversity_metrics(bi)
        base.update(E.adequacy_metrics(base, req.loc[m49]))
        rb = {"scenario": "baseline 2021-23", "m49": m49, "Area": area, "crops_shocked": ""}
        rb.update(base)
        rb["n_categories"] = int((bi.kcal > 0).sum())
        rows.append(rb)
        if m49 == E.WORLD:
            continue
        crops_here = [c for c in panels[panels.m49 == m49].crop if (c, m49) in bal.index]
        # A: single-crop standard loss
        for c in crops_here:
            for bound in ("upper", "lower"):
                f = E.quantity_fraction(STD_LOSS, bal.loc[(c, m49)], bound)
                rows.append(scenario_row(f"A single-crop -10% ({bound})", m49, area, [c], bi, sc, {c: f}, None,
                                         req.loc[m49], base, {"crop": c, "bound": bound, "qty_frac_" + c: f}))
        # B: simultaneous standard loss (stress test)
        qB = {c: E.quantity_fraction(STD_LOSS, bal.loc[(c, m49)]) for c in crops_here}
        rows.append(scenario_row("B simultaneous -10% all modelled crops (stress test)", m49, area, crops_here, bi, sc, qB, None,
                                 req.loc[m49], base, {"bound": "upper", **{f"qty_frac_{c}": v for c, v in qB.items()}}))
        # C / C': future climate, loss-only
        for col, label in (("dY_hybrid_pct", "C future climate loss-only (hybrid 1971-2000 -> 2041-60)"),
                           ("dY_present_relative_pct", "C' future climate loss-only (present-relative 2001-24 -> 2041-60)")):
            f_c = fy[fy.m49 == m49].set_index("crop")
            q, gains = {}, []
            for c in crops_here:
                dy = float(f_c.loc[c, col])
                used.append({"m49": m49, "Area": area, "crop": c, "reference": col, "dY_pct": dy,
                             "applied": dy < 0, "qty_frac": E.quantity_fraction(-dy / 100.0, bal.loc[(c, m49)]) if dy < 0 else 0.0})
                if dy < 0:
                    q[c] = E.quantity_fraction(-dy / 100.0, bal.loc[(c, m49)])
                else:
                    gains.append(c)
            rows.append(scenario_row(label, m49, area, sorted(q), bi, sc, q, None, req.loc[m49], base,
                                     {"bound": "upper", "gains_excluded": ";".join(gains), **{f"qty_frac_{c}": v for c, v in q.items()}}))
            if co2 is not None and col == "dY_hybrid_pct":
                for env in ("primary", "low", "high"):
                    conc = {(r.crop, r.nutrient): r[f"factor_{env}"] for _, r in co2.iterrows()}
                    rows.append(scenario_row(f"D future climate loss-only + elevated-CO2 concentration ({env})", m49, area, sorted(q),
                                             bi, sc, q, conc, req.loc[m49], base,
                                             {"bound": "upper", "gains_excluded": ";".join(gains), "co2_envelope": env,
                                              "co2_crops": ";".join(sorted(set(co2.crop)))}))
    out = pd.DataFrame(rows)
    out.to_csv(E.P("diversity_after_losses.csv"), index=False)
    pd.DataFrame(used).to_csv(E.P("diversity_future_pairs_used.csv"), index=False)
    show = out[out.Area == "India"][["scenario", "crops_shocked", "total_iron", "eff_iron", "top_share_iron", "pct_total_iron",
                                      "d_eff_kcal", "d_eff_iron", "d_MAR"]]
    pd.set_option("display.width", 250)
    print(show.round(4).to_string(index=False))


if __name__ == "__main__":
    main()
