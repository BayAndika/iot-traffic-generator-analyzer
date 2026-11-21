#!/usr/bin/env python3
"""Cari jeda jendela (lubang di urutan waktu) per run dan protokol.

Pemakaian:
  python3 scripts/cek_celah.py data/uji/traffic_features_uji.csv
"""
import sys

import pandas as pd

W = 5
if len(sys.argv) != 2:
    sys.exit(__doc__)

d = pd.read_csv(sys.argv[1]).sort_values(["run_id", "protokol", "jendela"])
temuan = []
for (run, proto), g in d.groupby(["run_id", "protokol"]):
    j = g["jendela"].to_numpy()
    for i in range(len(j) - 1):
        selisih = j[i + 1] - j[i]
        if selisih > W:
            jeda = int(selisih // W) - 1
            temuan.append({"run_id": run, "protokol": proto, "jeda_jendela": jeda,
                           "jeda_detik": jeda * W, "setelah_epoch": int(j[i])})

out = pd.DataFrame(temuan)
print(out.to_string(index=False) if len(out) else "Tidak ada jeda.")