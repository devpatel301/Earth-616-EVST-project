"""
16_future_yield_nutrition.py -- conditional future yield change and its nutrient consequences
(end evaluation, the planned "future climate -> yield -> nutrient adequacy" step; decision E10).

MAIN: literature damage accounting (consistent with the literature-only index). Physical stress and its
response coefficient are paired BEFORE any normalisation (the normalised F4 score is never read as a
yield loss):
    heat loss_t  = min(1, s_T * H_heat_t)          s_T = 1/(T_lim - T_crit) per deg C (Deryng 2014 linear
                                                    damage); H_heat_t = area-weighted deg C of flowering
                                                    T_eff above T_crit in season-year t
    water loss_t = min(1, K_y * H_water_t)         FAO: 1 - Ya/Ym = K_y (1 - ETa/ETm); H_water_t = rainfed
                                                    share x seasonal deficit 1 - P/ETc (screening proxy for
                                                    1 - ETa/ETm: no soil storage, irrigated area = 0 stress)
    loss_t       = 1 - (1 - heat loss_t)(1 - water loss_t)
    period loss  = mean over 1971-2000 season-years, historical vs MRI-ESM2-0 SSP2-4.5 2041-2060 change factors
    dY (%)       = -100 * (loss_fut - loss_hist) / (1 - loss_hist)
The LEVEL of loss_hist is not interpreted (the deficit proxy overstates absolute water losses); only the
CHANGE is propagated. Excludes: CO2 fertilisation, adaptation (sowing dates, cultivars, irrigation
expansion), crop-area change, pests, extremes below monthly resolution, price/trade response.

CROSS-CHECK: empirical coefficients (06_sensitivity.py, fitted 1971-2000; country if robust, else pooled,
else 0): dY_emp = b_T * dT_eff + b_W * 10 * dMR (the existing S1 logic applied to the future change).

NUTRITION: the same accounting as scenario S3 (09_yield_diet.py): national supply in 2021-23, upper bound
f = |dY| * min(1, SSR), lower bound with exports absorbing the loss first; NAR capped at 1; MAR change in
points out of 100. Only losses are propagated (yield gains are reported but not added to supply).
Outputs: future_yield.csv, future_nutrition.csv
"""
import os

import numpy as np
import pandas as pd

from config import CROPS, PROC

NUTRIENTS = ["kcal", "protein", "fat", "zinc", "iron"]
FUT = "future_MRI-ESM2-0_ssp245_2041-2060"
HIST = "historical_1971_2000"


def period_loss(df, crop):
    s_t, k_y = CROPS[crop]["heat_slope"], CROPS[crop]["ky"]
    heat = np.minimum(1.0, s_t * df.H_heat)
    water = np.minimum(1.0, k_y * df.H_water)
    return pd.Series({"heat_loss": heat.mean(), "water_loss": water.mean(),
                      "loss": (1 - (1 - heat) * (1 - water)).mean(),
                      "teff": df.teff_flow.mean(), "mr": df.mr_rainfed.mean()})


def main():
    panels = pd.read_csv(os.path.join(PROC, "panels.csv"))
    fs = pd.read_pickle(os.path.join(PROC, "future_country_series.pkl"))
    sens = pd.read_csv(os.path.join(PROC, "sensitivity.csv"))
    adequacy = pd.read_csv(os.path.join(PROC, "adequacy.csv"))
    contrib = pd.read_csv(os.path.join(PROC, "crop_contrib.csv"))
    last = int(adequacy.Year.max())
    base_adq = adequacy[adequacy.Year.between(last - 2, last)].groupby("m49").mean(numeric_only=True)
    base_con = contrib[contrib.Year.between(last - 2, last)].groupby(["crop", "m49"]).mean(numeric_only=True)

    yrows, nrows = [], []
    for _, p in panels.iterrows():
        g = fs[(fs.crop == p.crop) & (fs.m49 == p.m49)]
        h, f = period_loss(g[g.scenario == HIST], p.crop), period_loss(g[g.scenario == FUT], p.crop)
        dy_lit = -100.0 * (f.loss - h.loss) / max(1e-9, 1 - h.loss)
        s = sens[(sens.crop == p.crop) & (sens.m49 == p.m49)].iloc[0]
        d_mr = (f.mr - h.mr) if np.isfinite(f.mr) and np.isfinite(h.mr) else 0.0
        dy_emp = s.b_T_used * (f.teff - h.teff) + s.b_W_used * 10.0 * d_mr
        yrows.append({"crop": p.crop, "group": CROPS[p.crop]["group"], "country": p.country, "m49": p.m49,
                      "loss_hist": h.loss, "loss_fut": f.loss, "heat_loss_hist": h.heat_loss, "heat_loss_fut": f.heat_loss,
                      "water_loss_hist": h.water_loss, "water_loss_fut": f.water_loss,
                      "dTeff_C": f.teff - h.teff, "dMR": d_mr,
                      "dY_lit_pct": dy_lit, "dY_emp_pct": dy_emp, "emp_T_source": s.T_source,
                      "emp_detected": bool(s.b_T_used != 0 or s.b_W_used != 0)})
        if p.m49 not in base_adq.index or (p.crop, p.m49) not in base_con.index:
            continue
        b, c = base_adq.loc[p.m49], base_con.loc[(p.crop, p.m49)]
        for model, dy in (("literature damage accounting (main)", dy_lit), ("empirical coefficients (cross-check)", dy_emp)):
            loss = max(0.0, -dy) / 100.0
            r = {"crop": p.crop, "group": CROPS[p.crop]["group"], "country": p.country, "model": model,
                 "dY_pct": dy, "ssr": c.ssr, "MAR_base": b.MAR}
            for bound, frac in (("upper", loss * min(1.0, c.ssr)),
                                ("lower", max(0.0, loss * c["prod"] - c["exp"]) / c["dom"] if c["dom"] > 0 else 0.0)):
                nar = []
                for n in NUTRIENTS:
                    new = b[n] - frac * c[n]
                    nar.append(min(1.0, new / b[f"req_{n}"]))
                    r[f"d{n}_pct_{bound}"] = -100.0 * frac * c[n] / b[n]
                r[f"dMAR_pts_{bound}"] = 100.0 * (np.mean(nar) - b.MAR)
            nrows.append(r)
    ydf = pd.DataFrame(yrows)
    ydf.to_csv(os.path.join(PROC, "future_yield.csv"), index=False)
    ndf = pd.DataFrame(nrows)
    ndf.to_csv(os.path.join(PROC, "future_nutrition.csv"), index=False)
    pd.set_option("display.width", 250)
    print(ydf.groupby("crop", sort=False)[["dTeff_C", "dY_lit_pct", "dY_emp_pct"]].agg(["mean", "min", "max"]).round(2).to_string())
    main_n = ndf[ndf.model.str.startswith("literature")]
    print(main_n.sort_values("dMAR_pts_upper").head(10)[["crop", "country", "dY_pct", "dkcal_pct_upper", "diron_pct_upper", "dMAR_pts_upper", "dMAR_pts_lower"]].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
