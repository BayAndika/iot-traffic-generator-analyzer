#!/usr/bin/env python3
"""Ekstraksi 8 parameter traffic per jendela dan parameter performa per run.

Sumber:
  - PCAP (scapy): packet_count, byte_total, pesan MQTT dan CoAP, topik, interval
  - Log Zeek conn.log: connection_count, durasi_sesi
  - Log Zeek http.log: request HTTP, metode, URI

Pemakaian:
  python3 scripts/extract_features.py <folder_zeek> <folder_pcap> <out_features> <out_summary> <runs.csv>
Contoh:
  python3 scripts/extract_features.py ~/proyek/zeek ~/proyek/pcap \
      data/traffic_features.csv data/run_summary.csv metadata/runs.csv
"""
import sys
from pathlib import Path

import pandas as pd
from scapy.all import rdpcap, TCP, UDP, Raw

W = 5  # lebar jendela, detik. Jangan diubah di tengah pengumpulan
PORTS = {"MQTT": 1883, "CoAP": 5683, "HTTP": 80}
COAP_METODE = {1: "get", 2: "post", 3: "put", 4: "delete"}
COAP_OPSI_URI_PATH = 11
COAP_OPSI_OBSERVE = 6


# ---------- utilitas log Zeek ----------
def baca_zeek(path):
    """Baca log Zeek (tab-separated) dengan nama kolom dari baris #fields."""
    path = Path(path)
    if not path.exists():
        return None
    fields = None
    with open(path) as f:
        for line in f:
            if line.startswith("#fields"):
                fields = line.rstrip("\n").split("\t")[1:]
                break
    if fields is None:
        return None
    return pd.read_csv(path, sep="\t", comment="#", header=None, names=fields,
                       na_values="-", low_memory=False)


# ---------- parser protokol dari byte payload ----------
def mqtt_fixed_header(payload):
    """Kembalikan (tipe_paket, body) dari satu paket MQTT, atau None."""
    if len(payload) < 2:
        return None
    tipe = payload[0] >> 4
    i, mult, panjang = 1, 1, 0
    while True:
        if i >= len(payload):
            return None
        b = payload[i]
        i += 1
        panjang += (b & 127) * mult
        if not (b & 128):
            break
        mult *= 128
        if mult > 128 ** 3:
            return None
    return tipe, payload[i:i + panjang]


def mqtt_topik_publish(body):
    """Topik dari body PUBLISH: 2 byte panjang lalu string topik."""
    if len(body) < 2:
        return None
    panjang = int.from_bytes(body[:2], "big")
    return body[2:2 + panjang].decode("utf-8", errors="replace")


def coap_parse(payload):
    """Kembalikan dict {code, opsi} dari paket CoAP, atau None."""
    if len(payload) < 4:
        return None
    tkl = payload[0] & 0x0F
    code = payload[1]
    idx = 4 + tkl
    opsi = []
    nomor = 0
    while idx < len(payload) and payload[idx] != 0xFF:
        b = payload[idx]
        idx += 1
        delta = b >> 4
        panjang = b & 0x0F
        if delta == 13:
            delta = payload[idx] + 13
            idx += 1
        elif delta == 14:
            delta = int.from_bytes(payload[idx:idx + 2], "big") + 269
            idx += 2
        if panjang == 13:
            panjang = payload[idx] + 13
            idx += 1
        elif panjang == 14:
            panjang = int.from_bytes(payload[idx:idx + 2], "big") + 269
            idx += 2
        nomor += delta
        opsi.append((nomor, payload[idx:idx + panjang]))
        idx += panjang
    return {"code": code, "opsi": opsi}


# ---------- membaca PCAP menjadi tabel paket ----------
def kumpulkan_pcap(pcap_path):
    """Satu baris per paket MQTT/HTTP/CoAP dengan waktu, panjang, arah, dan isi penting."""
    baris = []
    for p in rdpcap(str(pcap_path)):
        if not (p.haslayer(TCP) or p.haslayer(UDP)):
            continue
        t = float(p.time)
        panjang = len(p)
        payload = bytes(p[Raw].load) if p.haslayer(Raw) else b""

        if p.haslayer(TCP):
            tcp = p[TCP]
            if 1883 in (tcp.sport, tcp.dport):
                proto = "MQTT"
            elif 80 in (tcp.sport, tcp.dport):
                proto = "HTTP"
            else:
                continue
            arah = "req" if tcp.dport in (1883, 80) else "resp"
            kind, topik = None, None
            if proto == "MQTT" and arah == "req" and payload:
                m = mqtt_fixed_header(payload)
                if m and m[0] == 3:
                    kind, topik = "publish", mqtt_topik_publish(m[1])
                elif m and m[0] == 8:
                    kind = "subscribe"
        else:
            udp = p[UDP]
            if 5683 not in (udp.sport, udp.dport):
                continue
            proto = "CoAP"
            arah = "req" if udp.dport == 5683 else "resp"
            kind, topik = None, None
            if arah == "req" and payload:
                c = coap_parse(payload)
                if c and c["code"] in COAP_METODE:
                    kind = COAP_METODE[c["code"]]
                    path = "/".join(v.decode("utf-8", errors="replace")
                                    for n, v in c["opsi"] if n == COAP_OPSI_URI_PATH)
                    topik = "/" + path if path else "/"
                    if any(n == COAP_OPSI_OBSERVE for n, _ in c["opsi"]):
                        kind = "observe"

        baris.append({"t": t, "ln": panjang, "proto": proto, "arah": arah,
                      "kind": kind, "topik": topik})
    return pd.DataFrame(baris)


# ---------- event request per protokol ----------
def event_request(proto, pp, http):
    """Tabel event dengan kolom t, kind, topik (sudah dipisah per protokol)."""
    if proto == "HTTP":
        if http is None or http.empty:
            return pd.DataFrame(columns=["t", "kind", "topik"])
        h = http.copy()
        return pd.DataFrame({
            "t": h["ts"].astype(float),
            "kind": h["method"].astype(str).str.lower(),
            "topik": h["uri"].astype(str),
        })
    r = pp[pp["arah"] == "req"][["t", "kind", "topik"]].copy()
    return r[r["kind"].notna()].reset_index(drop=True)


def selisih_interval(times):
    """Selisih waktu berurutan dan jendela tempat selisih itu dicatat (kejadian kedua)."""
    times = times.sort_values().reset_index(drop=True)
    dt = times.diff().dropna()
    jendela = (times.iloc[1:].values // W) * W
    return pd.DataFrame({"jendela": jendela, "dt": dt.values})


# ---------- proses satu run ----------
def proses_run(run_dir, pcap_path, run_id):
    pk = kumpulkan_pcap(pcap_path)
    if pk.empty:
        return None, None
    conn = baca_zeek(run_dir / "conn.log")
    http = baca_zeek(run_dir / "http.log")
    if conn is not None:
        conn["ts"] = conn["ts"].astype(float)
        conn["jendela"] = (conn["ts"] // W) * W

    durasi_run = float(pk["t"].max() - pk["t"].min())
    pk["jendela"] = (pk["t"] // W) * W

    fitur_list, ringkas_list = [], []
    for proto, port in PORTS.items():
        pp = pk[pk["proto"] == proto]
        if pp.empty:
            continue
        ev = event_request(proto, pp, http)
        if len(ev):
            ev["jendela"] = (ev["t"] // W) * W

        # request, subscribe/observe, dan topik sesuai protokol
        if proto == "MQTT":
            is_req = ev["kind"].eq("publish") if len(ev) else pd.Series(dtype=bool)
            is_sub = ev["kind"].eq("subscribe") if len(ev) else pd.Series(dtype=bool)
        elif proto == "CoAP":
            pola = ["get", "post", "put", "delete", "observe"]
            is_req = ev["kind"].isin(pola) if len(ev) else pd.Series(dtype=bool)
            is_sub = ev["kind"].eq("observe") if len(ev) else pd.Series(dtype=bool)
        else:  # HTTP
            is_req = ev["kind"].notna() if len(ev) else pd.Series(dtype=bool)
            is_sub = pd.Series([False] * len(ev), dtype=bool)  # HTTP tidak punya subscribe

        req_ev = ev[is_req] if len(ev) else ev
        sub_ev = ev[is_sub] if len(ev) else ev

        # interval antar request dalam run, dan per jendela
        if len(req_ev) >= 2:
            dt = selisih_interval(req_ev["t"])
            grp_dt = dt.groupby("jendela")["dt"]
            interval = pd.DataFrame({"interval_mean": grp_dt.mean(),
                                     "interval_std": grp_dt.std()})
            interval_run_mean = float(dt["dt"].mean())
            interval_run_std = float(dt["dt"].std())
        else:
            interval = pd.DataFrame(columns=["interval_mean", "interval_std"])
            interval_run_mean = float("nan")
            interval_run_std = float("nan")

        # per jendela
        g_pk = pp.groupby("jendela")
        kolom = pd.DataFrame({
            "packet_count": g_pk.size(),
            "byte_total": g_pk["ln"].sum(),
        })
        if conn is not None:
            cp = conn[conn["id.resp_p"] == port]
            g_cp = cp.groupby("jendela")
            kolom["connection_count"] = g_cp.size()
            kolom["durasi_sesi_rata"] = g_cp["duration"].mean()
        else:
            kolom["connection_count"] = pd.Series(dtype=float)
            kolom["durasi_sesi_rata"] = pd.Series(dtype=float)
        kolom["frekuensi_request_count"] = (
            req_ev.groupby("jendela").size() if len(req_ev) else pd.Series(dtype=float))
        kolom["subscribe_observe"] = (
            sub_ev.groupby("jendela").size() if len(sub_ev) else pd.Series(dtype=float))
        kolom["topic_resource_unik"] = (
            req_ev.groupby("jendela")["topik"].nunique() if len(req_ev) else pd.Series(dtype=float))
        kolom = kolom.join(interval, how="outer")

        for c in ["packet_count", "byte_total", "connection_count",
                  "frekuensi_request_count", "subscribe_observe"]:
            kolom[c] = kolom[c].fillna(0)

        kolom["packet_rate"] = kolom["packet_count"] / W
        kolom["byte_rate"] = kolom["byte_total"] / W
        kolom["connection_rate"] = kolom["connection_count"] / W
        kolom["frekuensi_request"] = kolom["frekuensi_request_count"] / W

        kolom = kolom.reset_index()
        kolom.insert(0, "protokol", proto)
        kolom.insert(0, "run_id", run_id)
        fitur_list.append(kolom)

        # rekap per run (parameter performa)
        total_byte = int(pp["ln"].sum())
        ringkas_list.append({
            "run_id": run_id,
            "protokol": proto,
            "durasi_run_s": round(durasi_run, 3),
            "total_byte": total_byte,
            "throughput_Bps": round(total_byte / durasi_run, 3) if durasi_run > 0 else float("nan"),
            "throughput_bps": round(total_byte * 8 / durasi_run, 3) if durasi_run > 0 else float("nan"),
            "jumlah_request": int(len(req_ev)),
            "interval_rata_s": round(interval_run_mean, 4),
            "jitter_s": round(interval_run_std, 4),
            # Latency dan retransmisi TCP belum dihitung otomatis (lihat catatan)
            "latency_rata_s": float("nan"),
            "retransmisi_tcp": float("nan"),
        })

    if not fitur_list:
        return None, None
    fitur = pd.concat(fitur_list, ignore_index=True)
    ringkas = pd.DataFrame(ringkas_list)
    return fitur, ringkas


# ---------- daftar run yang valid dari runs.csv ----------
def run_valid(runs_csv):
    df = pd.read_csv(runs_csv)
    df = df[df["jalur"] != "pilot"]
    df = df[~df["catatan"].astype(str).str.upper().str.startswith("GAGAL")]
    return set(df["run_id"].astype(str))


def main():
    if len(sys.argv) != 6:
        sys.exit(__doc__)
    zeek_root = Path(sys.argv[1]).expanduser()
    pcap_dir = Path(sys.argv[2]).expanduser()
    out_fitur = Path(sys.argv[3])
    out_ringkas = Path(sys.argv[4])
    valid = run_valid(sys.argv[5])

    fitur_all, ringkas_all = [], []
    for run_dir in sorted(zeek_root.iterdir()):
        if not run_dir.is_dir() or run_dir.name.startswith("pilot"):
            continue
        if run_dir.name not in valid:
            print("lewati (tidak valid / bukan run resmi):", run_dir.name)
            continue
        pcap = pcap_dir / f"{run_dir.name}.pcap"
        if not pcap.exists():
            print("lewati (pcap tidak ditemukan):", pcap)
            continue
        f, r = proses_run(run_dir, pcap, run_dir.name)
        if f is None:
            print("lewati (tidak ada paket):", run_dir.name)
            continue
        fitur_all.append(f)
        ringkas_all.append(r)
        print("selesai:", run_dir.name)

    if not fitur_all:
        sys.exit("Tidak ada run yang diproses.")
    pd.concat(fitur_all, ignore_index=True).to_csv(out_fitur, index=False)
    pd.concat(ringkas_all, ignore_index=True).to_csv(out_ringkas, index=False)
    print("Tersimpan:", out_fitur, "dan", out_ringkas)


if __name__ == "__main__":
    main()
"""Ekstraksi 8 parameter traffic per jendela dan parameter performa per run.

Sumber:
  - PCAP (scapy): packet_count, byte_total, pesan MQTT dan CoAP, topik, interval
  - Log Zeek conn.log: connection_count, durasi_sesi
  - Log Zeek http.log: request HTTP, metode, URI

Pemakaian:
  python3 scripts/extract_features.py <folder_zeek> <folder_pcap> <out_features> <out_summary> <runs.csv>
Contoh:
  python3 scripts/extract_features.py ~/proyek/zeek ~/proyek/pcap \
      data/traffic_features.csv data/run_summary.csv metadata/runs.csv
"""
import sys
from pathlib import Path

import pandas as pd
from scapy.all import rdpcap, TCP, UDP, Raw

W = 5  # lebar jendela, detik. Jangan diubah di tengah pengumpulan
PORTS = {"MQTT": 1883, "CoAP": 5683, "HTTP": 80}
COAP_METODE = {1: "get", 2: "post", 3: "put", 4: "delete"}
COAP_OPSI_URI_PATH = 11
COAP_OPSI_OBSERVE = 6


# ---------- utilitas log Zeek ----------
def baca_zeek(path):
    """Baca log Zeek (tab-separated) dengan nama kolom dari baris #fields."""
    path = Path(path)
    if not path.exists():
        return None
    fields = None
    with open(path) as f:
        for line in f:
            if line.startswith("#fields"):
                fields = line.rstrip("\n").split("\t")[1:]
                break
    if fields is None:
        return None
    return pd.read_csv(path, sep="\t", comment="#", header=None, names=fields,
                       na_values="-", low_memory=False)


# ---------- parser protokol dari byte payload ----------
def mqtt_fixed_header(payload):
    """Kembalikan (tipe_paket, body) dari satu paket MQTT, atau None."""
    if len(payload) < 2:
        return None
    tipe = payload[0] >> 4
    i, mult, panjang = 1, 1, 0
    while True:
        if i >= len(payload):
            return None
        b = payload[i]
        i += 1
        panjang += (b & 127) * mult
        if not (b & 128):
            break
        mult *= 128
        if mult > 128 ** 3:
            return None
    return tipe, payload[i:i + panjang]


def mqtt_topik_publish(body):
    """Topik dari body PUBLISH: 2 byte panjang lalu string topik."""
    if len(body) < 2:
        return None
    panjang = int.from_bytes(body[:2], "big")
    return body[2:2 + panjang].decode("utf-8", errors="replace")


def coap_parse(payload):
    """Kembalikan dict {code, opsi} dari paket CoAP, atau None."""
    if len(payload) < 4:
        return None
    tkl = payload[0] & 0x0F
    code = payload[1]
    idx = 4 + tkl
    opsi = []
    nomor = 0
    while idx < len(payload) and payload[idx] != 0xFF:
        b = payload[idx]
        idx += 1
        delta = b >> 4
        panjang = b & 0x0F
        if delta == 13:
            delta = payload[idx] + 13
            idx += 1
        elif delta == 14:
            delta = int.from_bytes(payload[idx:idx + 2], "big") + 269
            idx += 2
        if panjang == 13:
            panjang = payload[idx] + 13
            idx += 1
        elif panjang == 14:
            panjang = int.from_bytes(payload[idx:idx + 2], "big") + 269
            idx += 2
        nomor += delta
        opsi.append((nomor, payload[idx:idx + panjang]))
        idx += panjang
    return {"code": code, "opsi": opsi}


# ---------- membaca PCAP menjadi tabel paket ----------
def kumpulkan_pcap(pcap_path):
    """Satu baris per paket MQTT/HTTP/CoAP dengan waktu, panjang, arah, dan isi penting."""
    baris = []
    for p in rdpcap(str(pcap_path)):
        if not (p.haslayer(TCP) or p.haslayer(UDP)):
            continue
        t = float(p.time)
        panjang = len(p)
        payload = bytes(p[Raw].load) if p.haslayer(Raw) else b""

        if p.haslayer(TCP):
            tcp = p[TCP]
            if 1883 in (tcp.sport, tcp.dport):
                proto = "MQTT"
            elif 80 in (tcp.sport, tcp.dport):
                proto = "HTTP"
            else:
                continue
            arah = "req" if tcp.dport in (1883, 80) else "resp"
            kind, topik = None, None
            if proto == "MQTT" and arah == "req" and payload:
                m = mqtt_fixed_header(payload)
                if m and m[0] == 3:
                    kind, topik = "publish", mqtt_topik_publish(m[1])
                elif m and m[0] == 8:
                    kind = "subscribe"
        else:
            udp = p[UDP]
            if 5683 not in (udp.sport, udp.dport):
                continue
            proto = "CoAP"
            arah = "req" if udp.dport == 5683 else "resp"
            kind, topik = None, None
            if arah == "req" and payload:
                c = coap_parse(payload)
                if c and c["code"] in COAP_METODE:
                    kind = COAP_METODE[c["code"]]
                    path = "/".join(v.decode("utf-8", errors="replace")
                                    for n, v in c["opsi"] if n == COAP_OPSI_URI_PATH)
                    topik = "/" + path if path else "/"
                    if any(n == COAP_OPSI_OBSERVE for n, _ in c["opsi"]):
                        kind = "observe"

        baris.append({"t": t, "ln": panjang, "proto": proto, "arah": arah,
                      "kind": kind, "topik": topik})
    return pd.DataFrame(baris)


# ---------- event request per protokol ----------
def event_request(proto, pp, http):
    """Tabel event dengan kolom t, kind, topik (sudah dipisah per protokol)."""
    if proto == "HTTP":
        if http is None or http.empty:
            return pd.DataFrame(columns=["t", "kind", "topik"])
        h = http.copy()
        return pd.DataFrame({
            "t": h["ts"].astype(float),
            "kind": h["method"].astype(str).str.lower(),
            "topik": h["uri"].astype(str),
        })
    r = pp[pp["arah"] == "req"][["t", "kind", "topik"]].copy()
    return r[r["kind"].notna()].reset_index(drop=True)


def selisih_interval(times):
    """Selisih waktu berurutan dan jendela tempat selisih itu dicatat (kejadian kedua)."""
    times = times.sort_values().reset_index(drop=True)
    dt = times.diff().dropna()
    jendela = (times.iloc[1:].values // W) * W
    return pd.DataFrame({"jendela": jendela, "dt": dt.values})


# ---------- proses satu run ----------
def proses_run(run_dir, pcap_path, run_id):
    pk = kumpulkan_pcap(pcap_path)
    if pk.empty:
        return None, None
    conn = baca_zeek(run_dir / "conn.log")
    http = baca_zeek(run_dir / "http.log")
    if conn is not None:
        conn["ts"] = conn["ts"].astype(float)
        conn["jendela"] = (conn["ts"] // W) * W

    durasi_run = float(pk["t"].max() - pk["t"].min())
    pk["jendela"] = (pk["t"] // W) * W

    fitur_list, ringkas_list = [], []
    for proto, port in PORTS.items():
        pp = pk[pk["proto"] == proto]
        if pp.empty:
            continue
        ev = event_request(proto, pp, http)
        if len(ev):
            ev["jendela"] = (ev["t"] // W) * W

        # request, subscribe/observe, dan topik sesuai protokol
        if proto == "MQTT":
            is_req = ev["kind"].eq("publish") if len(ev) else pd.Series(dtype=bool)
            is_sub = ev["kind"].eq("subscribe") if len(ev) else pd.Series(dtype=bool)
        elif proto == "CoAP":
            pola = ["get", "post", "put", "delete", "observe"]
            is_req = ev["kind"].isin(pola) if len(ev) else pd.Series(dtype=bool)
            is_sub = ev["kind"].eq("observe") if len(ev) else pd.Series(dtype=bool)
        else:  # HTTP
            is_req = ev["kind"].notna() if len(ev) else pd.Series(dtype=bool)
            is_sub = pd.Series([False] * len(ev), dtype=bool)  # HTTP tidak punya subscribe

        req_ev = ev[is_req] if len(ev) else ev
        sub_ev = ev[is_sub] if len(ev) else ev

        # interval antar request dalam run, dan per jendela
        if len(req_ev) >= 2:
            dt = selisih_interval(req_ev["t"])
            grp_dt = dt.groupby("jendela")["dt"]
            interval = pd.DataFrame({"interval_mean": grp_dt.mean(),
                                     "interval_std": grp_dt.std()})
            interval_run_mean = float(dt["dt"].mean())
            interval_run_std = float(dt["dt"].std())
        else:
            interval = pd.DataFrame(columns=["interval_mean", "interval_std"])
            interval_run_mean = float("nan")
            interval_run_std = float("nan")

        # per jendela
        g_pk = pp.groupby("jendela")
        kolom = pd.DataFrame({
            "packet_count": g_pk.size(),
            "byte_total": g_pk["ln"].sum(),
        })
        if conn is not None:
            cp = conn[conn["id.resp_p"] == port]
            g_cp = cp.groupby("jendela")
            kolom["connection_count"] = g_cp.size()
            kolom["durasi_sesi_rata"] = g_cp["duration"].mean()
        else:
            kolom["connection_count"] = pd.Series(dtype=float)
            kolom["durasi_sesi_rata"] = pd.Series(dtype=float)
        kolom["frekuensi_request_count"] = (
            req_ev.groupby("jendela").size() if len(req_ev) else pd.Series(dtype=float))
        kolom["subscribe_observe"] = (
            sub_ev.groupby("jendela").size() if len(sub_ev) else pd.Series(dtype=float))
        kolom["topic_resource_unik"] = (
            req_ev.groupby("jendela")["topik"].nunique() if len(req_ev) else pd.Series(dtype=float))
        kolom = kolom.join(interval, how="outer")

        for c in ["packet_count", "byte_total", "connection_count",
                  "frekuensi_request_count", "subscribe_observe"]:
            kolom[c] = kolom[c].fillna(0)

        kolom["packet_rate"] = kolom["packet_count"] / W
        kolom["byte_rate"] = kolom["byte_total"] / W
        kolom["connection_rate"] = kolom["connection_count"] / W
        kolom["frekuensi_request"] = kolom["frekuensi_request_count"] / W

        kolom = kolom.reset_index()
        kolom.insert(0, "protokol", proto)
        kolom.insert(0, "run_id", run_id)
        fitur_list.append(kolom)

        # rekap per run (parameter performa)
        total_byte = int(pp["ln"].sum())
        ringkas_list.append({
            "run_id": run_id,
            "protokol": proto,
            "durasi_run_s": round(durasi_run, 3),
            "total_byte": total_byte,
            "throughput_Bps": round(total_byte / durasi_run, 3) if durasi_run > 0 else float("nan"),
            "throughput_bps": round(total_byte * 8 / durasi_run, 3) if durasi_run > 0 else float("nan"),
            "jumlah_request": int(len(req_ev)),
            "interval_rata_s": round(interval_run_mean, 4),
            "jitter_s": round(interval_run_std, 4),
            # Latency dan retransmisi TCP belum dihitung otomatis (lihat catatan)
            "latency_rata_s": float("nan"),
            "retransmisi_tcp": float("nan"),
        })

    if not fitur_list:
        return None, None
    fitur = pd.concat(fitur_list, ignore_index=True)
    ringkas = pd.DataFrame(ringkas_list)
    return fitur, ringkas


# ---------- daftar run yang valid dari runs.csv ----------
def run_valid(runs_csv):
    df = pd.read_csv(runs_csv)
    df = df[df["jalur"] != "pilot"]
    df = df[~df["catatan"].astype(str).str.upper().str.startswith("GAGAL")]
    return set(df["run_id"].astype(str))


def main():
    if len(sys.argv) != 6:
        sys.exit(__doc__)
    zeek_root = Path(sys.argv[1]).expanduser()
    pcap_dir = Path(sys.argv[2]).expanduser()
    out_fitur = Path(sys.argv[3])
    out_ringkas = Path(sys.argv[4])
    valid = run_valid(sys.argv[5])

    fitur_all, ringkas_all = [], []
    for run_dir in sorted(zeek_root.iterdir()):
        if not run_dir.is_dir() or run_dir.name.startswith("pilot"):
            continue
        if run_dir.name not in valid:
            print("lewati (tidak valid / bukan run resmi):", run_dir.name)
            continue
        pcap = pcap_dir / f"{run_dir.name}.pcap"
        if not pcap.exists():
            print("lewati (pcap tidak ditemukan):", pcap)
            continue
        f, r = proses_run(run_dir, pcap, run_dir.name)
        if f is None:
            print("lewati (tidak ada paket):", run_dir.name)
            continue
        fitur_all.append(f)
        ringkas_all.append(r)
        print("selesai:", run_dir.name)

    if not fitur_all:
        sys.exit("Tidak ada run yang diproses.")
    pd.concat(fitur_all, ignore_index=True).to_csv(out_fitur, index=False)
    pd.concat(ringkas_all, ignore_index=True).to_csv(out_ringkas, index=False)
    print("Tersimpan:", out_fitur, "dan", out_ringkas)


if __name__ == "__main__":
    main()
