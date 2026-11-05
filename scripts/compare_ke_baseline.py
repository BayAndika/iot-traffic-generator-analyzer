#!/usr/bin/env python3
"""Bandingkan satu skenario dengan baseline S1.

Pemakaian:
  python3 scripts/compare_ke_baseline.py data/traffic_features.csv docs/BASELINE_S1.csv S2_connburst
"""
import sys
import pandas as pd

if len(sys.argv) != 4:
    sys.exit(__doc__)

fitur = pd.read_csv(sys.argv[1])
base = pd.read_csv(sys.argv[2])
skenario = sys.argv[3]

# Ambil run dari skenario yang diminta (run_id diawali nama skenario)
sub = fitur[fitur["run_id"].str.startswith(skenario)]
if sub.empty:
    sys.exit(f"Tidak ada data untuk {skenario}")

base_jendela = base[base["sumber"] == "jendela"].set_index(["protokol", "parameter"])
hasil = []
for (proto, p), row in base_jendela.iterrows():
    if p not in sub.columns:
        continue
    nilai = sub[sub["protokol"] == proto][p].dropna()
    if nilai.empty or pd.isna(row["mean"]) or row["mean"] == 0:
        rasio = float("nan")
    else:
        rasio = nilai.mean() / row["mean"]
    hasil.append({"protokol": proto, "parameter": p,
                  "mean_s1": round(row["mean"], 4),
                  "mean_skenario": round(nilai.mean(), 4) if len(nilai) else float("nan"),
                  "rasio": round(rasio, 3) if pd.notna(rasio) else float("nan")})

out = pd.DataFrame(hasil)
print(f"Perbandingan {skenario} dengan baseline S1:")
print(out.to_string(index=False))
print("\nParameter dengan rasio >= 2 atau <= 0.5 (kandidat 'terlihat'):")
print(out[(out["rasio"] >= 2) | (out["rasio"] <= 0.5)].to_string(index=False))
