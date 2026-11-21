#!/usr/bin/env python3
"""Titik kritis per parameter, dinilai pada skenario sasarannya saja.

TPR = jendela anomali skenario sasaran yang melewati k x baseline
FPR = jendela normal (S1 selain baseline, dan normal skenario sasaran) yang melewati k x baseline
Pemakaian:
  python3 scripts/titik_kritis_per_skenario.py data/traffic_dataset.csv docs/titik_kritis_per_skenario.csv
"""
import sys

import numpy as np
import pandas as pd

BASE_RUN = sys.argv[3] if len(sys.argv) > 3 else "S1_normal_run1"
PETA = {
    "connection_rate": "S2_connburst",
    "frekuensi_request": "S3_pubreq",
    "subscribe_observe": "S4_subpoll",
    "topic_resource_unik": "S5_topic",
}
K = np.round(np.concatenate([np.arange(1.0, 1.25, 0.05),
                             np.arange(1.25, 5.01, 0.25),
                             [6, 8, 10, 15, 20]]), 2)

if len(sys.argv) not in (3, 4):
    sys.exit(__doc__)

d = pd.read_csv(sys.argv[1])
base = d[d.run_id == BASE_RUN].groupby("protokol")[list(PETA)].mean()
ev = d[d.run_id != BASE_RUN]

rows = []
for p, skn in PETA.items():
    for proto in ["MQTT", "CoAP", "HTTP"]:
        if proto not in base.index:
            continue
        b = base.loc[proto, p]
        pos = ev[(ev.skenario == skn) & (ev.protokol == proto) & (ev.label == "anomali")]
        neg = ev[(ev.protokol == proto) & (ev.label == "normal") &
                 (ev.skenario.isin(["S1_normal", skn]))]
        if pos.empty or neg.empty:
            continue  # misalnya HTTP untuk S4: tidak ada anomali
        for k in K:
            thr = 0 if b == 0 else k * b
            rows.append({
                "parameter": p, "protokol": proto, "skenario": skn, "k": k,
                "TPR": round((pos[p] > thr).mean(), 3),
                "FPR": round((neg[p] > thr).mean(), 3),
            })

h = pd.DataFrame(rows)
h["Youden"] = (h["TPR"] - h["FPR"]).round(3)
h.to_csv(sys.argv[2], index=False)

# Rentang k dengan Youden dalam 0,01 dari maksimum (bukan satu nilai)
mx = h.groupby(["parameter", "protokol"])["Youden"].transform("max")
rentang = h[h["Youden"] >= mx - 0.01]
print("Rentang k terbaik (Youden dalam 0,01 dari maksimum):")
print(rentang.groupby(["parameter", "protokol"]).agg(
    k_min=("k", "min"), k_maks=("k", "max"), Youden_maks=("Youden", "max")
).reset_index().to_string(index=False))
print("\nNilai pada k = 2,0:")
print(h[h.k == 2.0].to_string(index=False))