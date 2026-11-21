#!/usr/bin/env python3
"""Analisis keberhasilan membaca untuk uji burst bertahap (uji_S2_rate*).

Aturan ambang (docs/uji_batas_pembacaan.md bagian 1, sudah disetujui):
- connection_rate MQTT dan CoAP : ada koneksi baru (> 0)
- topic_resource_unik CoAP      : 1,5 x baseline
- lainnya                        : 2 x baseline

TPR = jendela anomali yang terbaca anomali
FPR = jendela normal yang salah dibaca anomali

Pemakaian:
  python3 scripts/analisis_membaca.py data/uji/traffic_uji.csv data/traffic_dataset.csv [BASE_RUN]
"""
import sys
from pathlib import Path

import pandas as pd

AMBANG = 2.0
AMBANG_COAP_TOPIK = 1.5
TERBACA_MIN = 0.80
LUPUT_MAKS = 0.20
PARAM = "connection_rate"

if len(sys.argv) < 3:
    sys.exit(__doc__)

uji = pd.read_csv(sys.argv[1])
resmi = pd.read_csv(sys.argv[2])
base_run = sys.argv[3] if len(sys.argv) > 3 else "S1_normal_run1"

base = resmi[resmi["run_id"] == base_run].groupby("protokol")[PARAM].mean()
uji = uji[uji["skenario"].str.startswith("uji_S2_rate")].copy()
uji["rate"] = uji["skenario"].str.extract(r"rate(\d+)")[0].astype(int)


def flag_anomali(proto, nilai, b):
    if proto in ("MQTT", "CoAP") and PARAM == "connection_rate":
        return nilai > 0
    if proto == "CoAP" and PARAM == "topic_resource_unik":
        return nilai > AMBANG_COAP_TOPIK * b
    return nilai > AMBANG * b


rows = []
for (run, proto), g in uji.groupby(["run_id", "protokol"]):
    if proto not in base.index:
        continue
    b = base.loc[proto]
    anom = g["label"].eq("anomali")
    normal = ~anom
    rate = int(g["rate"].iloc[0])
    if anom.sum() == 0:
        rows.append({"rate": rate, "protokol": proto, "run_id": run,
                     "TPR": None, "FPR": None, "catatan": "tanpa jendela anomali"})
        continue
    flag = flag_anomali(proto, g[PARAM], b)
    tpr = (flag & anom).sum() / anom.sum()
    fpr = (flag & normal).sum() / normal.sum() if normal.sum() else None
    rows.append({"rate": rate, "protokol": proto, "run_id": run,
                 "TPR": round(tpr, 3),
                 "FPR": round(fpr, 3) if fpr is not None else None,
                 "catatan": ""})

per_run = pd.DataFrame(rows)
ring = (per_run.dropna(subset=["TPR"])
        .groupby(["rate", "protokol"])
        .agg(TPR_rata=("TPR", "mean"), TPR_min=("TPR", "min"),
             TPR_maks=("TPR", "max"), FPR_rata=("FPR", "mean"),
             jumlah_run=("TPR", "size"))
        .round(3).reset_index())


def status(t):
    if t >= TERBACA_MIN:
        return "terbaca"
    if t <= LUPUT_MAKS:
        return "luput"
    return "batas"


ring["status"] = ring["TPR_rata"].apply(status)
Path("docs/uji").mkdir(parents=True, exist_ok=True)
per_run.to_csv("docs/uji/analisis_per_run.csv", index=False)
ring.to_csv("docs/uji/ringkasan_per_rate.csv", index=False)
muat = pd.read_csv(sys.argv[1])
mqtt_norm = muat[(muat["protokol"] == "MQTT") & (muat["label"] == "normal")]
mqtt_anom = muat[(muat["protokol"] == "MQTT") & (muat["label"] == "anomali")]
fpr_mqtt_global = round((mqtt_norm[PARAM] > 0).sum() / len(mqtt_norm), 3)
tpr_mqtt_global = round((mqtt_anom[PARAM] > 0).sum() / len(mqtt_anom), 3)
print(f"MQTT keseluruhan (semua run uji): TPR={tpr_mqtt_global} ({len(mqtt_anom)} anomali), FPR={fpr_mqtt_global} ({len(mqtt_norm)} normal)")
print("Per run:\n", per_run.to_string(index=False))
print("\nRingkasan per rate:\n", ring.to_string(index=False))
print("\nDisimpan di docs/uji/")