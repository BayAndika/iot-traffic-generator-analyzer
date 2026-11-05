import csv
import hashlib
from datetime import datetime, timedelta, timezone
from pathlib import Path
from scapy.all import rdpcap

WIB = timezone(timedelta(hours=7))
FILTER = "tcp port 1883 or udp port 5683 or tcp port 80"
HEADER = ["run_id", "jalur", "skenario", "ulang", "file_pcap", "filter", "interface",
          "waktu_mulai", "waktu_selesai", "durasi_detik", "packets_captured",
          "packets_received_by_filter", "packets_dropped_by_kernel", "sha256", "catatan"]

RUNS = {
    "S2_connburst": 3, "S3_pubreq": 3, "S4_subpoll": 3,
    "S5_topic": 3, "S6_campuran": 3,
}
daftar = [f"{s}_run{i}" for s, n in RUNS.items() for i in range(1, n + 1)]

csv_path = Path("metadata/runs.csv")
with open(csv_path, newline="", encoding="utf-8") as f:
    baris = list(csv.DictReader(f))
ada = {b["run_id"] for b in baris}

def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for blok in iter(lambda: f.read(1 << 20), b""):
            h.update(blok)
    return h.hexdigest()

ditambah = 0
for run in daftar:
    if run in ada:
        continue
    pcap = Path("pcap") / f"{run}.pcap"
    if not pcap.exists():
        print("LEWATI (pcap tidak ada):", run)
        continue
    paket = rdpcap(str(pcap))
    awal = datetime.fromtimestamp(float(paket[0].time), WIB).isoformat(timespec="seconds")
    akhir = datetime.fromtimestamp(float(paket[-1].time), WIB).isoformat(timespec="seconds")
    sha = sha256_file(pcap)
    catatan_hash = ""
    cek = Path("hashes") / f"{run}.sha256"
    if cek.exists():
        catatan_hash = " hash cocok dengan file hashes" if sha in cek.read_text() else " HASH TIDAK COCOK dengan file hashes"
    baris.append({
        "run_id": run,
        "jalur": "tiga",
        "skenario": run.rsplit("_run", 1)[0],
        "ulang": run.rsplit("_run", 1)[1],
        "file_pcap": f"{run}.pcap",
        "filter": FILTER,
        "interface": "eth0",
        "waktu_mulai": awal,
        "waktu_selesai": akhir,
        "durasi_detik": "600",
        "packets_captured": str(len(paket)),
        "packets_received_by_filter": "tidak_tercatat",
        "packets_dropped_by_kernel": "tidak_tercatat",
        "sha256": sha,
        "catatan": "dilengkapi dari pcap - waktu dari paket pertama dan terakhir - dropped tidak tercatat." + catatan_hash,
    })
    ditambah += 1
    print("ditambahkan:", run, len(paket), "paket")

with open(csv_path, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=HEADER)
    w.writeheader()
    w.writerows(baris)
print("Total ditambahkan:", ditambah)
