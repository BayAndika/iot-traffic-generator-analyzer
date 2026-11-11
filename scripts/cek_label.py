#!/usr/bin/env python3
"""Bandingkan label di dataset dengan label yang seharusnya dari jadwal burst.

Pemakaian:
  python3 scripts/cek_label.py all            (semua baris)
  python3 scripts/cek_label.py acak 20 1      (20 baris acak, seed 1)
  python3 scripts/cek_label.py anomali 10 2   (10 baris anomali acak, seed 2)
"""
import sys

import pandas as pd

d = pd.read_csv("data/traffic_dataset.csv")
iv = pd.read_csv("metadata/anomali_interval.csv")
iv["protokol"] = iv["protokol"].astype(str).str.upper()
iv["m"] = iv["mulai"].apply(lambda s: pd.Timestamp(s).timestamp())
iv["s"] = iv["selesai"].apply(lambda s: pd.Timestamp(s).timestamp())


def seharusnya(row):
    if row["skenario"] == "S1_normal":
        return "normal"
    sub = iv[(iv.run_id == row["run_id"]) & (iv.protokol == str(row["protokol"]).upper())]
    for _, x in sub.iterrows():
        if x.m <= row["jendela"] < x.s:
            return "anomali"
    return "normal"


mode = sys.argv[1] if len(sys.argv) > 1 else "all"
if mode == "all":
    sampel = d.copy()
elif mode == "anomali":
    n, seed = int(sys.argv[2]), int(sys.argv[3])
    sampel = d[d.label == "anomali"].sample(n=n, random_state=seed)
else:
    n, seed = int(sys.argv[2]), int(sys.argv[3])
    sampel = d.sample(n=n, random_state=seed)

sampel = sampel.copy()
sampel["seharusnya"] = sampel.apply(seharusnya, axis=1)
sampel["cocok"] = sampel["label"] == sampel["seharusnya"]
sampel["jendela"] = sampel["jendela"].astype("int64")

tidak = sampel[~sampel.cocok]
print(sampel[["run_id", "protokol", "jendela", "label", "seharusnya", "cocok"]].head(30).to_string(index=False))
print()
print("Total diperiksa :", len(sampel))
print("Cocok           :", int(sampel.cocok.sum()))
print("Tidak cocok     :", len(tidak))
if len(tidak):
    print("\nBaris tidak cocok (maks 30):")
    print(tidak[["run_id", "protokol", "jendela", "label", "seharusnya"]].head(30).to_string(index=False))
