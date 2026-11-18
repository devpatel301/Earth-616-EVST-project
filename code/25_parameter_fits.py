"""
25_parameter_fits.py -- reproduces the DERIVED heat parameters of the new crops from the published data tabulated in
docs/literature_verification_new_crops.md (section 2), and checks them against config.py.

Model (Deryng et al. 2014 form, on the index's temperature scale T_eff = (T_mean + T_max)/2):
    relative seed-yield loss = min(1, s_T * max(0, T_eff - T_crit)),   T_lim = T_crit + 1/s_T.
Fit: least squares; grid search over T_crit (0.05 C steps) and s_T (0.0005 /C steps).

Temperature conversion of chamber regimes (day / night set-points, D/N):
    12 h / 12 h step regimes (Bhandari et al. 2020):  T_mean = (D + N)/2,  T_max = D,  T_eff = (T_mean + D)/2
    sunlit sinusoidal chambers (Prasad et al. 2002/2003 via Boote et al. 2005): same midpoint convention
    (Boote reports realised means within about +-1 C of the midpoints; that +-1 C is a stated uncertainty).
Writes data/processed/nine_crop/parameter_fits.csv; exits non-zero if a fit does not reproduce config.py.
"""
import os
import sys

import numpy as np
import pandas as pd

from config import ALL_CROPS, ROOT_DIR

SLOPES = np.arange(0.001, 1.0, 0.0005)
OUT = os.path.join(ROOT_DIR, "data", "processed", "nine_crop", "parameter_fits.csv")


def teff(day, night):
    return ((day + night) / 2.0 + day) / 2.0


def fit(t, loss):
    t, loss = np.asarray(t, float), np.asarray(loss, float)
    best = None
    for tc in np.arange(t.min() - 5, t.max(), 0.05):
        x = np.maximum(0.0, t - tc)
        if x.max() <= 0:
            continue
        sse = ((np.minimum(1.0, SLOPES[:, None] * x[None, :]) - loss[None, :]) ** 2).sum(axis=1)   # grid: the min(1,.) cap
        i = int(sse.argmin())                                                                        # makes 1-D optimisers stop at local minima
        if best is None or sse[i] < best[2] - 1e-12:
            best = (round(float(tc), 2), float(SLOPES[i]), float(sse[i]))
    tc, s, sse = best
    return tc, s, tc + 1.0 / s, float(np.sqrt(sse / len(t)))


def main():
    rows = []
    # Chickpea: Bhandari et al. 2020, Table 3 (seed yield g/plant), 3 genotypes, flowering-to-maturity exposure
    regimes = [(30, 20), (35, 25), (38, 28), (40, 30), (42, 32)]
    cp = np.array([[5.98, 5.76, 4.59, 3.09, 1.14], [5.27, 5.19, 4.23, 2.89, 1.11], [5.13, 4.98, 3.96, 2.84, 1.18]])
    loss_cp = (1 - cp / cp[:, :1]).mean(axis=0)
    t_cp = [teff(d, n) for d, n in regimes]
    rows.append(("chickpea", "Bhandari et al. 2020 Table 3; 3 genotypes; 12h/12h step regimes", t_cp, loss_cp, "fit, 5 points"))
    # Lentil: Bhandari et al. 2020, Table 3, 2 genotypes; the 42/32 point (also zero yield) is not used (4 points)
    le = np.array([[2.19, 1.98, 1.06, 0.0], [2.28, 1.87, 1.02, 0.0]])
    loss_le = (1 - le / le[:, :1]).mean(axis=0)
    rows.append(("lentil", "Bhandari et al. 2020 Table 3; 2 genotypes; first 4 regimes", t_cp[:4], loss_le, "fit, 4 points / 2 parameters"))
    # Groundnut: Prasad et al. 2003 abstract (seed yield -0, -14, -59, -90 % at 32/22, 36/26, 40/30, 44/34 C, ambient CO2)
    t_gn = [teff(d, n) for d, n in [(32, 22), (36, 26), (40, 30), (44, 34)]]
    rows.append(("groundnut", "Prasad et al. 2003 abstract; cv. Georgia Green; season-long", t_gn, np.array([0, 0.14, 0.59, 0.90]), "fit, 4 points"))

    out = []
    ok = True
    for crop, src, t, loss, note in rows:
        tc, s, tl, rmse = fit(t, loss)
        cfg = ALL_CROPS[crop]
        match = abs(tc - cfg["tcrit"]) <= 0.1 and abs(s - cfg["heat_slope"]) <= 0.005
        ok &= match
        out.append({"crop": crop, "source": src, "points_teff": "; ".join(f"{x:.1f}" for x in t), "points_loss": "; ".join(f"{x:.3f}" for x in loss),
                    "tcrit_fit": tc, "slope_fit": round(s, 4), "tlim_fit": round(tl, 2), "rmse": round(rmse, 4),
                    "tcrit_config": cfg["tcrit"], "slope_config": round(cfg["heat_slope"], 4), "reproduces_config": match, "status": "DERIVED: " + note})
    # Bean: Prasad et al. 2002 via Boote et al. 2005 p.470 -- highest yield at 28/18 C, linear decline to zero at 37/27 C
    tc, tl = (23 + 28) / 2, (32 + 37) / 2
    match = abs(tc - ALL_CROPS["bean"]["tcrit"]) < 1e-9 and abs(1 / (tl - tc) - ALL_CROPS["bean"]["heat_slope"]) < 1e-9
    ok &= match
    out.append({"crop": "bean", "source": "Prasad et al. 2002 via Boote et al. 2005 p.470 (optimum 28/18, zero yield 37/27 C)", "points_teff": "25.5; 34.5",
                "points_loss": "0; 1", "tcrit_fit": tc, "slope_fit": round(1 / (tl - tc), 4), "tlim_fit": tl, "rmse": np.nan,
                "tcrit_config": ALL_CROPS["bean"]["tcrit"], "slope_config": round(ALL_CROPS["bean"]["heat_slope"], 4), "reproduces_config": match,
                "status": "DERIVED: two published points; optimum is the lowest regime tested"})
    # Rapeseed: Morrison & Stewart 2002 threshold 29.5 C on daily T_max; T_eff = T_max - DTR/4 with an ASSUMED DTR 10-14 C
    out.append({"crop": "rapeseed", "source": "Morrison & Stewart 2002 abstract (29.5 C daily T_max); slope borrowed from Deryng spring wheat (10 C span)",
                "points_teff": "", "points_loss": "", "tcrit_fit": 29.5 - 12 / 4, "slope_fit": 0.1, "tlim_fit": 29.5 - 3 + 10, "rmse": np.nan,
                "tcrit_config": ALL_CROPS["rapeseed"]["tcrit"], "slope_config": ALL_CROPS["rapeseed"]["heat_slope"],
                "reproduces_config": ALL_CROPS["rapeseed"]["tcrit"] == 26.5 and ALL_CROPS["rapeseed"]["heat_slope"] == 0.1,
                "status": "PROXY: threshold converted with an assumed diurnal range; slope borrowed"})
    d = pd.DataFrame(out)
    d.to_csv(OUT, index=False)
    print(d[["crop", "tcrit_fit", "slope_fit", "tlim_fit", "rmse", "tcrit_config", "slope_config", "reproduces_config"]].to_string(index=False))
    sys.exit(0 if ok and d.reproduces_config.all() else 1)


if __name__ == "__main__":
    main()
