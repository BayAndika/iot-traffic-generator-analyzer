#!/usr/bin/env python3
"""Eksplorasi dataset versi 2: parameter traffic dan performa. Hanya membaca data.

Pemakaian (dari ~/proyek, venv aktif):
  python3 scripts/eksplorasi.py

Input : data/traffic_dataset.csv dan data/run_summary.csv
Output: docs/eksplorasi/tabel/*.csv dan docs/eksplorasi/figures/*.png
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

DATA = Path("data/traffic_dataset.csv")
RINGKAS = Path("data/run_summary.csv")
OUT = Path("docs/eksplorasi")
OUT_TBL = OUT / "tabel"
OUT_FIG = OUT / "figures"

PARAM_TRAFFIC = [
    "packet_rate", "byte_rate", "connection_rate", "durasi_sesi_rata",
    "frekuensi_request", "subscribe_observe", "topic_resource_unik",
    "interval_mean", "interval_std",
]
PARAM_PERF = ["throughput_Bps", "throughput_bps", "jitter_s", "interval_rata_s", "jumlah_request"]

for f in (DATA, RINGKAS):
    if not f.exists():
        sys.exit(f"File tidak ditemukan: {f}")

OUT_TBL.mkdir(parents=True, exist_ok=True)
OUT_FIG.mkdir(parents=True, exist_ok=True)

d = pd.read_csv(DATA)
rs = pd.read_csv(RINGKAS)
rs["skenario"] = rs["run_id"].str.rsplit("_run", n=1).str[0]

print("Baris dataset:", len(d), "| Run:", d["run_id"].nunique())
print("Baris run_summary:", len(rs))

# ---------- Tabel ----------
dist = d.groupby(["skenario", "label"]).size().unstack(fill_value=0)
dist.to_csv(OUT_TBL / "distribusi_label.csv")
print("\nDistribusi label:\n", dist)

traffik = d.groupby(["protokol", "skenario", "label"])[PARAM_TRAFFIC].mean().round(3)
traffik.to_csv(OUT_TBL / "parameter_traffic_per_label.csv")

perf = rs.groupby(["protokol", "skenario"])[PARAM_PERF].mean().round(3)
perf.to_csv(OUT_TBL / "parameter_performa_per_skenario.csv")
print("\nPerforma per skenario (MQTT):\n", perf.loc["MQTT"])

hilang = d[PARAM_TRAFFIC].isna().groupby(d["protokol"]).sum()
hilang.to_csv(OUT_TBL / "nilai_hilang_per_protokol.csv")

if rs[["latency_rata_s", "retransmisi_tcp"]].isna().all().all():
    print("\nCatatan: latency_rata_s dan retransmisi_tcp belum dihitung (kosong).")


# ---------- Grafik ----------
def grafik_run(run_id, kolom, nama_file):
    sub = d[d["run_id"] == run_id].copy()
    if sub.empty:
        print("Lewati (run tidak ada):", run_id)
        return
    sub["detik"] = sub["jendela"] - sub["jendela"].min()
    fig, ax = plt.subplots(figsize=(9, 4))
    for proto, g in sub.groupby("protokol"):
        g = g.sort_values("detik")
        ax.plot(g["detik"], g[kolom], label=proto)
    ax.set_xlabel("Detik sejak awal run")
    ax.set_ylabel(kolom)
    ax.set_title(f"{run_id}: {kolom}")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT_FIG / nama_file, dpi=120)
    plt.close(fig)
    print("Grafik:", OUT_FIG / nama_file)


grafik_run("S2_connburst_run1", "connection_rate", "s2_run1_connection_rate.png")
grafik_run("S3_pubreq_run1", "frekuensi_request", "s3_run1_frekuensi_request.png")
grafik_run("S4_subpoll_run1", "subscribe_observe", "s4_run1_subscribe_observe.png")
grafik_run("S5_topic_run1", "topic_resource_unik", "s5_run1_topic_resource_unik.png")
grafik_run("S6_campuran_run1", "connection_rate", "s6_run1_connection_rate.png")

# Grafik batang throughput per skenario (MQTT)
mq = rs[rs["protokol"] == "MQTT"].groupby("skenario")["throughput_Bps"].mean()
fig, ax = plt.subplots(figsize=(8, 4))
mq.plot(kind="bar", ax=ax)
ax.set_ylabel("Throughput (byte/detik)")
ax.set_title("Throughput MQTT per skenario (rata-rata run)")
fig.tight_layout()
fig.savefig(OUT_FIG / "throughput_mqtt_per_skenario.png", dpi=120)
plt.close(fig)
print("Grafik:", OUT_FIG / "throughput_mqtt_per_skenario.png")

print("\nSelesai. Hasil di", OUT)
