# Setup Log

## Perangkat
- Raspberry Pi 3 Model B, hostname ragoon-broker, IP 192.168.10.199
- Laptop IP saat uji: 192.168.12.251 (subnet berbeda, dirutekan MikroTik)

## Keputusan
- Capture resmi: tcpdump di Pi, disimpan sebagai file (bukan RPCAP)
- Zeek dijalankan offline di WSL Ubuntu 22.04
- Mosquitto: listener 0.0.0.0:1883, allow_anonymous true (hanya jaringan uji)