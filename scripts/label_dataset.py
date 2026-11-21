#!/usr/bin/env python3
"""Beri label normal atau anomali pada setiap baris traffic_features.csv.

Aturan:
- S1_normal: semua jendela normal.
- S2 sampai S6: jendela dianggap anomali jika awal jendela berada di dalam
  interval burst/publish untuk run dan protokol yang sama (dari anomali_interval.csv).
- Nama protokol diseragamkan ke MQTT, CoAP, HTTP (sama dengan run_summary.csv).

Pemakaian:
  python3 scripts/label_dataset.py data/traffic_features.csv metadata/runs.csv \
      metadata/anomali_interval.csv data/traffic_dataset.csv
"""
import sys

import pandas as pd

PROTO_MAP = {"MQTT": "MQTT", "COAP": "CoAP", "HTTP": "HTTP"}


def proto_std(x):
    """Ubah nama protokol ke bentuk standar. Nama yang tidak dikenal diberi peringatan."""
    kunci = str(x).strip().upper()
    if kunci not in PROTO_MAP:
        print(f"PERINGATAN: nama protokol tidak dikenal: {x!r}")
        return str(x).strip()
    return PROTO_MAP[kunci]


def epoch(iso):
    return pd.Timestamp(iso).timestamp()


def main():
    if len(sys.argv) != 5:
        sys.exit(__doc__)
    fitur_path, runs_path, interval_path, out = sys.argv[1:5]

    fitur = pd.read_csv(fitur_path)
    runs = pd.read_csv(runs_path)
    interval = pd.read_csv(interval_path)

    # Buang pilot, ambil skenario dari runs.csv
    runs = runs[runs["jalur"] != "pilot"]
    fitur = fitur[fitur["run_id"].isin(runs["run_id"])].copy()
    fitur = fitur.merge(runs[["run_id", "skenario"]], on="run_id", how="left")

    # Seragamkan nama protokol di kedua sisi
    fitur["protokol"] = fitur["protokol"].map(proto_std)
    interval["protokol"] = interval["protokol"].map(proto_std)

    interval["mulai_epoch"] = interval["mulai"].apply(epoch)
    interval["selesai_epoch"] = interval["selesai"].apply(epoch)

    def label_baris(row):
        if row["skenario"] == "S1_normal":
            return "normal"
        sub = interval[(interval["run_id"] == row["run_id"]) &
                       (interval["protokol"] == row["protokol"])]
        jend = row["jendela"]
        for _, iv in sub.iterrows():
            if iv["mulai_epoch"] <= jend < iv["selesai_epoch"]:
                return "anomali"
        return "normal"

    fitur["label"] = fitur.apply(label_baris, axis=1)

    kolom_awal = ["run_id", "skenario", "label", "protokol", "jendela"]
    sisa = [c for c in fitur.columns if c not in kolom_awal]
    fitur = fitur[kolom_awal + sisa].sort_values(["skenario", "run_id", "protokol", "jendela"])
    fitur.to_csv(out, index=False, encoding="utf-8")

    print(f"Tersimpan {len(fitur)} baris ke {out}")
    print(fitur.groupby(["skenario", "label"]).size().unstack(fill_value=0))


if __name__ == "__main__":
    main()