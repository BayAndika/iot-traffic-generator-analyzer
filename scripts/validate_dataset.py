#!/usr/bin/env python3
"""Validasi data/traffic_dataset.csv sebelum dipakai dashboard."""
import sys

import pandas as pd

WAJIB = ["run_id", "skenario", "label", "protokol", "jendela",
         "packet_count", "packet_rate", "byte_rate", "connection_count",
         "connection_rate", "durasi_sesi_rata", "frekuensi_request",
         "subscribe_observe", "topic_resource_unik", "interval_mean", "interval_std"]

path = sys.argv[1] if len(sys.argv) > 1 else "data/traffic_dataset.csv"
df = pd.read_csv(path)

kurang = [c for c in WAJIB if c not in df.columns]
if kurang:
    sys.exit(f"GAGAL: kolom hilang: {kurang}")

print("Jumlah baris :", len(df))
print("Jumlah run   :", df["run_id"].nunique())
print("Protokol     :", sorted(df["protokol"].dropna().unique()))
print("Label        :", df["label"].value_counts(dropna=False).to_dict())
print("Label kosong :", int(df["label"].isna().sum()))
print("Jendela kosong:", int(df["jendela"].isna().sum()))

if df["label"].isna().any() or df["jendela"].isna().any():
    sys.exit("GAGAL: ada baris tanpa label atau jendela")
print("LULUS")
