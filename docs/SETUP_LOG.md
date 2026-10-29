# Setup Log

**Proyek:** IoT Traffic Generator & Analyzer
**Peran:** Network Capture & Dataset Engineer
**Pemilik catatan:** Bayu Andika Wibisono
**Terakhir diperbarui:** ____

---

## 1. Perangkat

| Item | Nilai | Cara cek |
|---|---|---|
| Model Raspberry Pi | Raspberry Pi 3 Model B | `cat /proc/device-tree/model` |
| Hostname Pi | ragoon-broker | `hostname` |
| User Pi | ragoon | - |
| Versi Raspberry Pi OS | ____ | `cat /etc/os-release` |
| Kernel Pi | 6.18.50 (rpt-rpi-v8) | `uname -r` |
| IP Pi | 192.168.10.199 | `hostname -I` |
| Versi Mosquitto | ____ | `mosquitto -h` |
| Versi tcpdump (Pi) | ____ | `tcpdump --version` |
| Model MikroTik | ____ | `/system resource print` |
| Versi RouterOS | ____ | `/system resource print` |

## 2. Laptop dan WSL

| Item | Nilai | Cara cek |
|---|---|---|
| Versi Windows | ____ | `winver` |
| Versi WSL | 2 | `wsl -l -v` |
| Distro WSL | Ubuntu-22.04 | `lsb_release -a` |
| Versi Zeek | 9.0.0 | `zeek --version` |
| Versi Wireshark | ____ | Help → About |
| Versi Npcap | ____ | Wireshark → Help → About → Folders, atau dari panel Npcap |
| Versi Python | ____ (target 3.12) | `python --version` |
| Versi Git | ____ | `git --version` |
| Nama interface laptop ke port mirror | ____ | Wireshark → Capture → Options |

## 3. Jaringan

| Item | Nilai |
|---|---|
| Subnet Pi | 192.168.10.0/24 |
| Subnet proposal | 192.168.1.0/24 (belum diselaraskan) |
| IP laptop yang terlihat di capture | 192.168.12.251, 192.168.12.236, 192.168.12.238 (tidak tetap, dicatat per sesi) |
| IP sumber MQTT pilot | 192.168.11.253 (identitas belum dikonfirmasi, lihat catatan) |
| IP ESP yang terlihat di CoAP | 192.168.12.236 (sumber PUT `/motion`) |
| IP ESP yang terlihat di HTTP | 192.168.12.242 (sumber POST `/api/sensor/http`) |
| Catatan | Laptop dan Pi berada di subnet berbeda, trafik dirutekan MikroTik |

**Catatan:** IP di atas diambil dari capture, belum dikonfirmasi dengan MAC address. Isi kolom "Identitas" setelah dicek dengan `ip neigh` di Pi atau DHCP lease MikroTik.

| IP | Identitas | Dikonfirmasi dengan |
|---|---|---|
| 192.168.12.234 |ESP#1 MQTT | ____ |
| 192.168.12.236 | ____ (dugaan ESP#2 CoAP) | ____ |
| 192.168.12.242 | ____ (dugaan ESP#3 HTTP) | ____ |
| 192.168.12.251 | ____ (dugaan laptop) | ____ |
| 192.168.12.238 | ____ | ____ |

## 4. Layanan di Raspberry Pi

| Layanan | Port | Status | Keterangan |
|---|---|---|---|
| Mosquitto (MQTT) | TCP 1883 | Aktif | `listener 0.0.0.0:1883`, `allow_anonymous true` (hanya jaringan uji) |
| Server CoAP | UDP 5683 | Belum tetap | Berjalan manual di `~/coap-server/server.py`, perlu systemd atau tmux |
| Server HTTP | TCP 80 | Belum tetap | Berjalan manual di `~/coap-server/http_server.py`, perlu systemd atau tmux |

**Status respons saat uji:**
- CoAP PUT `/motion`: awalnya 4.05, lalu 2.04 setelah perbaikan server.
- HTTP POST `/api/sensor/http`: awalnya 404, status sekarang ____ (harus 200 sebelum run tiga protokol).

## 5. Konfigurasi

**Mosquitto** (`/etc/mosquitto/conf.d/lab.conf`):

listener 1883 0.0.0.0
allow_anonymous true

**Sudoers** (`/etc/sudoers.d/tcpdump`):

ragoon ALL=(root) NOPASSWD: /usr/sbin/tcpdump


**Port mirror MikroTik:**
- Port sumber: ____
- Port target (laptop): ____
- Arah mirror: ____
- Hasil uji ping: ____

**Filter capture:**
- Jalur B: `tcp port 1883`
- Jalur A: `tcp port 1883 or udp port 5683 or tcp port 80`

## 6. Keputusan

- Capture resmi dilakukan dengan tcpdump di Pi dan disimpan sebagai file PCAP.
- Remote capture RPCAP tidak dipakai karena Pi tidak menjalankan `rpcapd`.
- Remote capture SSH (sshdump) dipakai hanya untuk inspeksi, bukan dataset.
- Zeek dijalankan offline di WSL Ubuntu 22.04, tidak di Pi.
- Wireshark dipasang tanpa tshark. Npcap dipasang untuk port mirror.
- Dataset dibuat per jalur. Jalur B (MQTT saja) adalah hasil antara, bukan dataset final.
- Durasi S1 sementara 600 detik. Menunggu persetujuan Aslan.
- Setiap run diberi nomor ulang. Run yang gagal tidak ditimpa.
- Interface capture tetap `eth0`. Jika berubah, catat di sini dan buat run baru.
- Timeline dashboard bersifat offline, bukan real-time.

## 7. Uji coba

| Tanggal | Uji | Hasil |
|---|---|---|
| ____ | Mosquitto publish dari WSL dan PowerShell | Berhasil, topik `test/capture` |
| ____ | tcpdump `-c 5` port 1883 | 5 paket tertangkap |
| ____ | tcpdump filter gabungan (1883, 5683, 80) | Berhasil setelah perbaikan ketik |
| ____ | SHA-256 Pi dan WSL untuk `uji_coba.pcap` | Cocok: `948658811b5defc...` |
| ____ | `frame contains "halo"` di Wireshark | Ditemukan pada paket publish |
| ____ | `mqtt_publish.log` untuk `test/capture` | ____ |
| ____ | Pilot MQTT (2 menit) dengan `tcp port 1883` | conn.log memuat 1883, service `mqtt` |
| ____ | Ping laptop ke Pi, ICMP di Wireshark (port mirror) | ____ |
| ____ | Tiga angka tcpdump pilot MQTT | captured ____ / received ____ / dropped ____ |
| ____ | Respons HTTP 200 (`curl -i -X POST`) | ____ |
| ____ | Respons CoAP 2.04 (`aiocoap-client`) | ____ |

## 8. Catatan dan temuan

- **Zeek dipasang dari OBS.** Format repositori yang benar: `deb http://download.opensuse.org/repositories/security:/zeek/xUbuntu_22.04/ ./` (suite `./`, tanpa spasi di URL). Belum dicocokkan dengan docs.zeek.org.
- **Postfix dipasang sebagai dependensi Zeek** dengan konfigurasi Local only, mail name `localhost`.
- **`wireshark-common` dipasang di WSL** dengan opsi non-superuser tidak diaktifkan.
- **Pola koneksi MQTT firmware ESP:** setiap publish membuka koneksi baru (connect → publish → disconnect), durasi sekitar 3 ms, sekitar 10 paket dari klien dan 6 dari broker.
- **Laptop tercatat dengan beberapa IP berbeda** selama uji. Kolom IP sumber di dataset harus dicatat per sesi.
- **Interface Wireshark remote `ragoon-broker` tidak dipakai.** Dialog RPCAP menghasilkan error `10054` karena Pi tidak menjalankan `rpcapd`.
- **Sumber IP `192.168.11.253` belum diketahui.** Subnetnya berbeda dari sumber lain.
- **Dokumen proposal dan diagram** masih memuat `192.168.1.1` dan Raspberry Pi 4 di beberapa bagian. Perlu diselaraskan.

## 9. Yang belum dikerjakan

- [ ] Server CoAP dan HTTP dijalankan dengan systemd atau tmux
- [ ] Respons HTTP 200 terverifikasi
- [ ] Port mirror terverifikasi dengan ICMP dan MQTT
- [ ] Identitas semua IP dikonfirmasi
- [ ] Durasi S1 sampai S6 disepakati dengan Aslan
- [ ] Ambang kriteria anomali disepakati dengan Aslan
- [ ] Run S1 resmi (3 kali)
- [ ] Skrip ekstraksi fitur MQTT
- [ ] Dataset MQTT dan validasi 20 persen sampel