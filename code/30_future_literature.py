"""
30_future_literature.py -- future-impact literature coverage for all nine crops (research extension 1).

Inputs
  docs/future_literature_sources.csv     verified study rows (citation, read level, locator, period, scenario,
                                         CO2/adaptation treatment, outcome, paraphrased conclusion, direction,
                                         mechanism); quotes in docs/future_literature_sources.md
  docs/future_literature_assessment.csv  our reviewed judgement per row: consistency verdict, likely reasons,
                                         what the comparison cannot establish, shared-input flag; and one
                                         coverage note per crop (row id "COVERAGE-<crop>")
Our corresponding conclusion is COMPUTED here from the result tables for the panel countries the study covers
(or, where the study covers none of them, for the crop's whole panel, flagged as not geographically matched):
direction of the conditional yield change (literature accounting, hybrid and present-relative reference), the
empirical cross-check, the direction of the F4 change and whether heat or water drives it. Only directions,
mechanisms and conclusions are compared, never magnitudes on different metrics.
Outputs: future_literature_comparison.csv, future_literature_coverage.csv
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
import ext_common as E  # noqa: E402
from config import CROP_ORDER, CROPS, ROOT_DIR  # noqa: E402

DOCS = os.path.join(ROOT_DIR, "docs")
SHORT = {"United States of America": "USA", "China, mainland": "China", "Russian Federation": "Russia",
         "United Republic of Tanzania": "Tanzania"}
VERDICTS = {"consistent", "partly consistent", "different", "not directly comparable"}


def direction(values, tol=0.5):
    v = np.asarray(values, float)
    if (v < -tol).all():
        return "loss"
    if (v > tol).all():
        return "gain"
    if (np.abs(v) <= tol).all():
        return "little change"
    return "mixed"


def our_side(crop, countries, fy, fyr, fc):
    panel = fy[fy.crop == crop]
    matched = [c for c in countries if c in set(panel.country)]
    sel = matched if matched else list(panel.country)
    y = panel.set_index("country").loc[sel]
    r = fyr[fyr.crop == crop].set_index("country").loc[sel]
    c = fc[fc.crop == crop].set_index("country").loc[sel]
    heat, water = float(c.dF4_from_heat.sum()), float(c.dF4_from_water.sum())
    tot = abs(heat) + abs(water)
    hs = abs(heat) / tot if tot > 0 else np.nan
    mech = "little change" if tot < 1e-6 else ("heat" if hs > 2 / 3 else "water" if hs < 1 / 3 else "heat and water")
    fmt = lambda s: "; ".join(f"{SHORT.get(k, k)} {v:+.1f}%" for k, v in s.items())
    return {
        "geography_matched": bool(matched),
        "our_countries": "; ".join(SHORT.get(k, k) for k in sel),
        "our_dY_lit_hybrid": fmt(y.dY_lit_pct),
        "our_dY_present_relative": fmt(r.dY_present_relative_pct),
        "our_dY_empirical": fmt(y.dY_emp_pct),
        "our_direction_lit": direction(y.dY_lit_pct),
        "our_direction_present_relative": direction(r.dY_present_relative_pct),
        "our_direction_empirical": direction(y.dY_emp_pct),
        "our_F4_change": "rises" if (c.dF4_abs > 0).all() else "falls" if (c.dF4_abs < 0).all() else "mixed",
        "our_mechanism_of_F4_change": mech,
        "our_heat_share_of_F4_change": hs,
        "our_dTeff_C": "; ".join(f"{SHORT.get(k, k)} {v:+.1f}" for k, v in c.dTeff_C.items()),
    }


def main():
    src = pd.read_csv(os.path.join(DOCS, "future_literature_sources.csv"))
    ass = pd.read_csv(os.path.join(DOCS, "future_literature_assessment.csv"))
    fy = pd.read_csv(E.P("future_yield.csv"))
    fyr = pd.read_csv(E.P("future_yield_reference_periods.csv"))
    fc = pd.read_csv(E.P("future_components.csv"))
    bad_crop = set(src.crop) - set(CROPS)
    if bad_crop:
        raise ValueError(f"unknown crops in sources: {bad_crop}")
    rows = []
    for _, s in src.iterrows():
        countries = [c.strip() for c in str(s.panel_countries_matched).split(";") if c.strip() and c.strip().lower() != "none"]
        rows.append({**s.to_dict(), **our_side(s.crop, countries, fy, fyr, fc)})
    comp = pd.DataFrame(rows)
    a = ass[~ass.id.astype(str).str.startswith("COVERAGE-")]
    missing = set(comp.id) - set(a.id)
    if missing:
        raise ValueError(f"source rows without a reviewed assessment: {sorted(missing)}")
    if not set(a.consistency) <= VERDICTS:
        raise ValueError(f"unknown verdicts: {set(a.consistency) - VERDICTS}")
    comp = comp.merge(a, on="id", how="left", suffixes=("", "_assessment"))
    comp.to_csv(E.P("future_literature_comparison.csv"), index=False)

    cov_notes = ass[ass.id.astype(str).str.startswith("COVERAGE-")].assign(crop=lambda d: d.id.str.replace("COVERAGE-", "", regex=False))
    cov = []
    for crop in [c for c in CROP_ORDER if c in CROPS]:
        g = comp[comp.crop == crop]
        note = cov_notes[cov_notes.crop == crop]
        cov.append({"crop": crop, "n_rows": len(g), "n_studies": g.doi.nunique() if len(g) else 0,
                    "geographies": "; ".join(sorted(set(g.geography.astype(str)))) if len(g) else "",
                    "panel_matched_rows": int(g.geography_matched.sum()) if len(g) else 0,
                    "full_text_rows": int(g.read_level.astype(str).str.contains("full", case=False).sum()) if len(g) else 0,
                    **{f"n_{v.replace(' ', '_')}": int((g.consistency == v).sum()) if len(g) else 0 for v in sorted(VERDICTS)},
                    "coverage_note": note.iloc[0].reasons if len(note) else "",
                    "gaps": note.iloc[0].cannot_establish if len(note) else ""})
    cov = pd.DataFrame(cov)
    if (cov.coverage_note == "").any():
        raise ValueError(f"crops without a coverage assessment: {list(cov.crop[cov.coverage_note == ''])}")
    cov.to_csv(E.P("future_literature_coverage.csv"), index=False)
    pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 60)
    print(cov[["crop", "n_rows", "n_studies", "panel_matched_rows"] + [c for c in cov.columns if c.startswith("n_") and c not in ("n_rows", "n_studies")]].to_string(index=False))


if __name__ == "__main__":
    main()
