#!/usr/bin/env python3
"""Titik kritis dengan leave-one-out pada baseline S1.

Untuk setiap run S1 (sebagai lipatan):
- baseline = rata-rata dua run S1 lainnya (run yang dinilai tidak ikut)
- positif  = jendela anomali skenario sasaran
- negatif  = jendela normal skenario sasaran + jendela normal S1 yang dinilai

Pemakaian:
  python3 scripts/titik_kritis_loo.py data/traffic_dataset.csv docs/titik_kritis_loo.csv
"""
import sys

import numpy as np
import pandas as pd

S1_RUNS = ["S1_normal_run1", "S1_normal_run2b", "S1_normal_run3"]
PETA = {
    "connection_rate": "S2_connburst",
    "frekuensi_request": "S3_pubreq",
    "subscribe_observe": "S4_subpoll",
    "topic_resource_unik": "S5_topic",
}
PROTO = ["MQTT", "CoAP", "HTTP"]
K = np.round(np.concatenate([np.arange(1.0, 1.25, 0.05),
                             np.arange(1.25, 5.01, 0.25),
                             [6, 8, 10, 15, 20]]), 2)

if len(sys.argv) != 3:
    sys.exit(__doc__)

d = pd.read_csv(sys.argv[1])
s1 = d[d.run_id.isin(S1_RUNS)]

rows = []
for lipatan in S1_RUNS:
    lain = [r for r in S1_RUNS if r != lipatan]
    for p, skn in PETA.items():
        for proto in PROTO:
            pos = d[(d.skenario == skn) & (d.protokol == proto) & (d.label == "anomali")]
            neg = pd.concat([
                d[(d.skenario == skn) & (d.protokol == proto) & (d.label == "normal")],
                s1[(s1.run_id == lipatan) & (s1.protokol == proto)],
            ])
            if pos.empty or neg.empty:
                continue  # misalnya HTTP untuk S4: tidak ada anomali
            b = s1[s1.run_id.isin(lain) & (s1.protokol == proto)][p].mean()
            for k in K:
                thr = 0 if b == 0 else k * b
                tpr = (pos[p] > thr).mean()
                fpr = (neg[p] > thr).mean()
                rows.append({"lipatan": lipatan, "parameter": p, "protokol": proto,
                             "skenario": skn, "baseline": round(b, 5), "k": k,
                             "TPR": round(tpr, 3), "FPR": round(fpr, 3),
                             "Youden": round(tpr - fpr, 3)})

h = pd.DataFrame(rows)
h.to_csv(sys.argv[2], index=False)

# Rentang k baik per lipatan: Youden dalam 0,01 dari maksimum lipatan itu
mx = h.groupby(["lipatan", "parameter", "protokol"])["Youden"].transform("max")
baik = h[h["Youden"] >= mx - 0.01]

print("== Rentang k baik per lipatan ==")
rent = (baik.groupby(["parameter", "protokol", "lipatan"])["k"]
        .agg(k_min="min", k_maks="max").reset_index())
print(rent.to_string(index=False))

print("\n== Apakah k = 2,0 baik di ketiga lipatan? ==")
for (p, proto), g in baik.groupby(["parameter", "protokol"]):
    ada = {l: 2.0 in set(x.k) for l, x in g.groupby("lipatan")}
    stabil = all(ada.get(l, False) for l in S1_RUNS)
    print(f"{p:22s} {proto:5s}  2x masuk semua lipatan: {stabil}   {ada}")

print("\n== Baseline per lipatan (MQTT) ==")
print(h[(h.k == 1.0) & (h.protokol == "MQTT")][["lipatan", "parameter", "baseline"]]
      .drop_duplicates().to_string(index=False))