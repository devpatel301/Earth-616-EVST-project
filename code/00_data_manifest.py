"""
00_data_manifest.py -- inventory of every raw input (path, size, modified date, SHA-256) -> docs/DATA_MANIFEST.csv.
A fresh checkout compares its data/raw against this file to see exactly which inputs are missing or differ.
Run:  python 00_data_manifest.py            (writes the manifest)
      python 00_data_manifest.py --check    (compares local data/raw with the manifest)
"""
import datetime
import hashlib
import os
import sys

import pandas as pd

from config import RAW_DIR, ROOT_DIR

MANIFEST = os.path.join(ROOT_DIR, "docs", "DATA_MANIFEST.csv")
SOURCE = {"worldclim": "WorldClim 2.1 (CRU-TS 4.09 monthly prec; 1970-2000 prec normals; elevation)",
          "tmax": "WorldClim 2.1 CRU-TS 4.09 monthly tmax", "tmin": "WorldClim 2.1 CRU-TS 4.09 monthly tmin",
          "normals": "WorldClim 2.1 1970-2000 monthly normals (tmax, tmin)",
          "cmip6": "WorldClim 2.1 CMIP6 MRI-ESM2-0 SSP2-4.5 2041-2060",
          "spam": "SPAM 2010 v2.0 (IFPRI)", "sacks": "Sacks et al. 2010 crop calendars",
          "faostat": "FAOSTAT bulk (QCL, FBS, FBS historic, food security)", "faostat_sua": "FAOSTAT SUA crops & livestock",
          "usda": "USDA FoodData Central SR Legacy 2018-04", "naturalearth": "Natural Earth 1:50m admin-0",
          "koppen": "Beck et al. 2023 Koppen-Geiger 0.5 deg (manual download)"}


def sha256(path, block=1 << 22):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(block), b""):
            h.update(chunk)
    return h.hexdigest()


def scan():
    rows = []
    for folder in sorted(os.listdir(RAW_DIR)):
        base = os.path.join(RAW_DIR, folder)
        for dirpath, _, files in os.walk(base):
            for fn in sorted(files):
                if fn.endswith((".part", ".chunks")):
                    continue
                p = os.path.join(dirpath, fn)
                rows.append({"path": os.path.relpath(p, ROOT_DIR).replace("\\", "/"), "folder": folder,
                             "source": SOURCE.get(folder, ""), "bytes": os.path.getsize(p),
                             "modified": datetime.datetime.fromtimestamp(os.path.getmtime(p)).strftime("%Y-%m-%d"),
                             "sha256": sha256(p)})
                print(rows[-1]["path"], rows[-1]["bytes"], flush=True)
    return pd.DataFrame(rows)


if __name__ == "__main__":
    local = scan()
    if "--check" in sys.argv:
        ref = pd.read_csv(MANIFEST)
        m = ref.merge(local, on="path", how="left", suffixes=("", "_local"))
        m["status"] = ["missing" if pd.isna(x) else ("ok" if x == y else "differs") for x, y in zip(m.sha256_local, m.sha256)]
        print(m.status.value_counts().to_string())
        print(m[m.status != "ok"][["path", "status"]].to_string(index=False))
    else:
        local.to_csv(MANIFEST, index=False)
        print(f"{len(local)} files, {local.bytes.sum() / 1e9:.2f} GB -> {MANIFEST}")
