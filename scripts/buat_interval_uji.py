#!/usr/bin/env python3
"""Buat metadata/anomali_interval_uji.csv dari log Windows.

Hanya burst uji_* yang ada di metadata/runs_uji.csv dan tidak dibatalkan.
"""
from pathlib import Path

import pandas as pd

LOG = Path("/mnt/c/PBL/iot-traffic/anomali_log.csv")
KOLOM = ["run", "protokol", "skenario", "mulai", "selesai", "aksi", "galat"]
BATAL = ["uji_S2_rate3_run1"]

log = pd.read_csv(LOG, header=None, names=KOLOM)
log = log[log["run"].astype(str).str.startswith("uji_")]
log = log[~log["run"].isin(BATAL)]

runs_ok = pd.read_csv("metadata/runs_uji.csv")["run_id"].tolist()
log = log[log["run"].isin(runs_ok)]

iv = pd.DataFrame({
    "run_id": log["run"],
    "protokol": log["protokol"],
    "mulai": log["mulai"],
    "selesai": log["selesai"],
    "skenario_anomali": log["skenario"],
})
iv.to_csv("metadata/anomali_interval_uji.csv", index=False)
print(len(iv), "baris interval uji ditulis")