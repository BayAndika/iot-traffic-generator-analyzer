#!/usr/bin/env python3
"""Baseline S1: rata-rata dan simpangan baku tiap parameter dari run S1 yang valid.

Pemakaian:
  python3 scripts/baseline_s1.py data/traffic_features.csv data/run_summary.csv docs/BASELINE_S1.csv
"""
import sys
import pandas as pd

# Ubah jika daftar run S1 valid berubah. Harus sama dengan runs.csv
S1_VALID = ["S1_normal_run1", "S1_normal_run2b", "S1_normal_run3"]

PARAMETER_JENDELA = ["packet_rate", "byte_rate", "connection_rate", "durasi_sesi_rata",
                     "frekuensi_request", "subscribe_observe", "topic_resource_unik",
                     "interval_mean", "interval_std"]
PARAMETER_RUN = ["throughput_Bps", "throughput_bps", "jumlah_request",
                 "interval_rata_s", "jitter_s"]

if len(sys.argv) != 4:
    sys.exit(__doc__)

fitur = pd.read_csv(sys.argv[1])
ringkas = pd.read_csv(sys.argv[2])
fitur = fitur[fitur["run_id"].isin(S1_VALID)]
ringkas = ringkas[ringkas["run_id"].isin(S1_VALID)]

hasil = []
for proto, g in fitur.groupby("protokol"):
    for p in PARAMETER_JENDELA:
        s = g[p].dropna()
        hasil.append({"sumber": "jendela", "protokol": proto, "parameter": p,
                      "mean": s.mean(), "std": s.std(), "n": len(s)})
for proto, g in ringkas.groupby("protokol"):
    for p in PARAMETER_RUN:
        s = g[p].dropna()
        hasil.append({"sumber": "run", "protokol": proto, "parameter": p,
                      "mean": s.mean(), "std": s.std(), "n": len(s)})

out = pd.DataFrame(hasil).round(4)
out.to_csv(sys.argv[3], index=False)
print(out.to_string(index=False))
print("Tersimpan:", sys.argv[3])
