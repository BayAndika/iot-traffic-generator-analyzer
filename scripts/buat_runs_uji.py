#!/usr/bin/env python3
"""Buat metadata/runs_uji.csv dari pcap/uji_*.pcap (burst dan gangguan).

Pemakaian (dari ~/proyek):
  python3 scripts/buat_runs_uji.py
"""
import hashlib
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scapy.all import rdpcap

WIB = timezone(timedelta(hours=7))
FILTER = "tcp port 1883 or udp port 5683 or tcp port 80"
HEADER = ("run_id,jalur,skenario,ulang,file_pcap,filter,interface,waktu_mulai,waktu_selesai,"
          "durasi_detik,packets_captured,packets_received_by_filter,packets_dropped_by_kernel,"
          "sha256,catatan")
POLA = re.compile(r"^(uji_S2_rate\d+|uji_err_E\d)_run(\d+b?)$")

baris = []
for p in sorted(Path("pcap").glob("uji_*.pcap")):
    m = POLA.match(p.stem)
    if not m:
        print("LEWATI (nama tidak sesuai pola):", p.name)
        continue
    skenario, ulang = m.group(1), m.group(2)
    pk = rdpcap(str(p))
    if len(pk) == 0:
        print("LEWATI (pcap kosong):", p.name)
        continue
    awal = datetime.fromtimestamp(float(pk[0].time), WIB).isoformat(timespec="seconds")
    akhir = datetime.fromtimestamp(float(pk[-1].time), WIB).isoformat(timespec="seconds")
    sha = hashlib.sha256(p.read_bytes()).hexdigest()
    if skenario.startswith("uji_err"):
        jenis = skenario.split("_")[2]
        catatan = f"uji gangguan {jenis} - lihat catatan waktu kejadian - bukan dataset resmi"
    else:
        catatan = "uji burst bertahap - bukan dataset resmi"
    baris.append([p.stem, "tiga", skenario, ulang, p.name, FILTER, "eth0",
                  awal, akhir, "600", str(len(pk)), "tidak_tercatat", "tidak_tercatat",
                  sha, catatan])

Path("metadata").mkdir(exist_ok=True)
Path("metadata/runs_uji.csv").write_text(
    HEADER + "\n" + "\n".join(",".join(b) for b in baris) + ("\n" if baris else ""),
    encoding="utf-8")
print(len(baris), "run uji ditulis ke metadata/runs_uji.csv")