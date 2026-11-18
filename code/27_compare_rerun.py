"""
27_compare_rerun.py -- audit tool (not part of run_all): compares a fresh pipeline run with a preserved copy of the
previous outputs, file by file, with numerical tolerances.

    python 27_compare_rerun.py <previous_copy_dir>

<previous_copy_dir> must contain work/, processed/ and docs/ (copies of data/work, data/processed and the generated
LaTeX of the previous run). Writes data/processed/nine_crop/audit_rerun_comparison.csv with one row per file:
identical (bit for bit / exact values), within tolerance (numeric, |diff| <= 1e-9 + 1e-9|x|), differs (with the largest
absolute and relative difference and the columns/arrays concerned), new, or missing.
"""
import os
import sys

import numpy as np
import pandas as pd

from config import ROOT_DIR

ATOL, RTOL = 1e-9, 1e-9


def cmp_arrays(a, b):
    if a.shape != b.shape:
        return "differs", np.nan, np.nan, f"shape {b.shape} -> {a.shape}"
    if a.dtype.kind not in "fiub" or b.dtype.kind not in "fiub":
        same = bool((a.astype(str) == b.astype(str)).all())
        return ("identical" if same else "differs"), np.nan, np.nan, ""
    if np.array_equal(a, b, equal_nan=True):
        return "identical", 0.0, 0.0, ""
    a, b = a.astype(float), b.astype(float)
    if not np.array_equal(np.isnan(a), np.isnan(b)):
        return "differs", np.nan, np.nan, "NaN pattern"
    d = np.abs(a - b)
    mx = float(np.nanmax(d))
    rel = float(np.nanmax(d / np.maximum(np.abs(b), 1e-12)))
    ok = bool(np.all((d <= ATOL + RTOL * np.abs(b)) | np.isnan(d)))
    return ("within tolerance" if ok else "differs"), mx, rel, ""


def cmp_frames(a, b):
    if list(a.columns) != list(b.columns) or len(a) != len(b):
        return "differs", np.nan, np.nan, f"columns/rows {b.shape} -> {a.shape}"
    worst, mx, rel, cols = "identical", 0.0, 0.0, []
    for c in a.columns:
        x, y = a[c], b[c]
        if pd.api.types.is_numeric_dtype(x) and pd.api.types.is_numeric_dtype(y):
            s, m, r, _ = cmp_arrays(x.to_numpy(float), y.to_numpy(float))
        else:
            s, m, r = ("identical" if x.astype(str).equals(y.astype(str)) else "differs"), np.nan, np.nan
        if s != "identical":
            cols.append(c)
            mx, rel = np.nanmax([mx, m]), np.nanmax([rel, r])
            worst = "differs" if "differs" in (s, worst) else "within tolerance"
    return worst, mx, rel, ", ".join(cols[:8])


def compare(new, old):
    ext = os.path.splitext(new)[1]
    try:
        if ext == ".npz":
            a, b = np.load(new, allow_pickle=True), np.load(old, allow_pickle=True)
            if set(a.files) != set(b.files):
                return "differs", np.nan, np.nan, "array names"
            res = [(k,) + cmp_arrays(a[k], b[k]) for k in a.files]
            bad = [r for r in res if r[1] != "identical"]
            if not bad:
                return "identical", 0.0, 0.0, ""
            st = "differs" if any(r[1] == "differs" for r in bad) else "within tolerance"
            return st, float(np.nanmax([r[2] for r in bad])), float(np.nanmax([r[3] for r in bad])), ", ".join(r[0] for r in bad[:8])
        if ext == ".npy":
            return cmp_arrays(np.load(new), np.load(old))
        if ext == ".csv":
            return cmp_frames(pd.read_csv(new, low_memory=False), pd.read_csv(old, low_memory=False))
        if ext == ".pkl":
            a, b = pd.read_pickle(new), pd.read_pickle(old)
            return cmp_frames(a.reset_index(drop=True), b.reset_index(drop=True))
        with open(new, "rb") as f, open(old, "rb") as g:
            return ("identical" if f.read() == g.read() else "differs"), np.nan, np.nan, "bytes"
    except Exception as e:   # noqa: BLE001 -- record and continue
        return "error", np.nan, np.nan, repr(e)[:120]


def main():
    prev = sys.argv[1]
    pairs = [("data/work", "work"), ("data/processed", "processed"), ("docs/nine_crop/generated", "docs/nine_crop/generated"),
             ("docs/four_crop/generated", "docs/four_crop/generated")]
    rows = []
    for new_root, old_root in pairs:
        n_dir, o_dir = os.path.join(ROOT_DIR, new_root), os.path.join(prev, old_root)
        names = set()
        for base in (n_dir, o_dir):
            for dp, _, fs in os.walk(base):
                for f in fs:
                    if f.endswith((".tif", ".nc", ".txt")) or "audit_rerun_comparison" in f:
                        continue   # extracted raw files and logs; raw inputs are checked by 00_data_manifest.py
                    names.add(os.path.relpath(os.path.join(dp, f), base).replace("\\", "/"))
        for rel in sorted(names):
            n, o = os.path.join(n_dir, rel), os.path.join(o_dir, rel)
            if not os.path.exists(o):
                rows.append((new_root, rel, "new", np.nan, np.nan, ""))
            elif not os.path.exists(n):
                rows.append((new_root, rel, "missing", np.nan, np.nan, ""))
            else:
                rows.append((new_root, rel) + compare(n, o))
    d = pd.DataFrame(rows, columns=["area", "file", "status", "max_abs_diff", "max_rel_diff", "detail"])
    out = os.path.join(ROOT_DIR, "data", "processed", "nine_crop", "audit_rerun_comparison.csv")
    d.to_csv(out, index=False)
    print(d.groupby(["area", "status"]).size().to_string())
    print(d[~d.status.isin(["identical"])].to_string(index=False, max_colwidth=60))


if __name__ == "__main__":
    main()
