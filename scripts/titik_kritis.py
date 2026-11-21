#!/usr/bin/env python3
"""Cari ambang kelipatan baseline yang paling seimbang per parameter dan protokol.

Baseline: rata-rata jendela S1_normal_run1 per protokol.
Evaluasi: semua jendela dari run lain. Youden = TPR - FPR.

Pemakaian:
  python3 scripts/titik_kritis.py data/traffic_dataset.csv docs/titik_kritis.csv
"""
import sys

import numpy as np
import pandas as pd

PARAM = ["packet_rate", "byte_rate", "connection_rate", "frekuensi_request",
         "subscribe_observe", "topic_resource_unik", "interval_std"]
BASE_RUN = "S1_normal_run1"
K = np.round(np.arange(1.25, 5.01, 0.25), 2)

d = pd.read_csv(sys.argv[1])
base = d[d.run_id == BASE_RUN].groupby("protokol")[PARAM].mean()
ev = d[d.run_id != BASE_RUN]

hasil = []
for proto, g in ev.groupby("protokol"):
    anom = g["label"].eq("anomali")
    if anom.sum() == 0:
        continue  # protokol tanpa anomali (misalnya HTTP di S4) dilewati
    for p in PARAM:
        b = base.loc[proto, p]
        for k in K:
            flag = (g[p] > 0) if b == 0 else (g[p] > k * b)
            tpr = (flag & anom).sum() / anom.sum()
            fpr = (flag & ~anom).sum() / (~anom).sum()
            hasil.append((proto, p, k, round(tpr, 3), round(fpr, 3), round(tpr - fpr, 3)))

h = pd.DataFrame(hasil, columns=["protokol", "parameter", "k", "TPR", "FPR", "Youden"])
h.to_csv(sys.argv[2], index=False)
terbaik = h.loc[h.groupby(["protokol", "parameter"])["Youden"].idxmax()]
print("Titik kritis (Youden tertinggi) per protokol dan parameter:")
print(terbaik.to_string(index=False))