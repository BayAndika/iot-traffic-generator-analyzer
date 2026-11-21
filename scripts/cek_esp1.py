#!/usr/bin/env python3
"""Cek kapan ESP#1 (192.168.12.234) mengirim paket MQTT di sebuah PCAP.

Pemakaian: python3 scripts/cek_esp1.py pcap/<nama>.pcap
"""
import sys

from scapy.all import rdpcap, IP, TCP

if len(sys.argv) != 2:
    sys.exit(__doc__)

p = rdpcap(sys.argv[1])
t0 = float(p[0].time)
t_akhir = float(p[-1].time)
esp = sorted(float(x.time) for x in p
             if x.haslayer(IP) and x[IP].src == "192.168.12.234"
             and x.haslayer(TCP) and x[TCP].dport == 1883)

print(f"durasi capture : {t_akhir - t0:.1f} detik")
print(f"paket ESP#1    : {len(esp)}")
if not esp:
    print("ESP#1 tidak mengirim sama sekali selama capture.")
    sys.exit()
print(f"paket pertama  : {esp[0] - t0:.1f} detik sejak awal capture")
print(f"paket terakhir : {esp[-1] - t0:.1f} detik sejak awal capture")
for a, b in zip(esp, esp[1:]):
    if b - a > 10:
        print(f"jeda {b - a:.1f} detik, dari {a - t0:.1f} sampai {b - t0:.1f} detik")