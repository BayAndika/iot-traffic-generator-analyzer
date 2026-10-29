# Setup Log

**Proyek:** IoT Traffic Generator & Analyzer
**Peran:** Network Capture & Dataset Engineer
**Pemilik catatan:** Bayu Andika Wibisono
**Terakhir diperbarui:** 29 Oktober 2026

> Aturan pengisian: nilai yang belum diketahui tetap `____`. Jangan diisi dengan perkiraan. Setiap perubahan konfigurasi dicatat dengan tanggal dan alasannya.

---

## 1. Perangkat

| Item | Nilai | Cara cek |
|---|---|---|
| Model Raspberry Pi | Raspberry Pi 3 Model B | `cat /proc/device-tree/model` |
| Hostname Pi | ragoon-broker | `hostname` |
| User Pi | ragoon | - |
| Versi Raspberry Pi OS | ____ | `cat /etc/os-release` |
| Kernel Pi | 6.18.50+rpt-rpi-v8 | `uname -r` |
| IP Pi | 192.168.10.199 | `hostname -I` |
| Versi Mosquitto | ____ | `mosquitto -h` |
| Versi tcpdump (Pi) | ____ | `tcpdump --version` |
| Model MikroTik | ____ | `/system resource print` |
| Versi RouterOS | 7.16.2 | `/system resource print` |

---

## 2. Laptop dan WSL

| Item | Nilai | Cara cek |
|---|---|---|
| Versi Windows | ____ | `winver` |
| Versi WSL | 2 | `wsl -l -v` |
| Distro WSL | Ubuntu-22.04 | `lsb_release -a` |
| Versi Zeek | 9.0.0 | `zeek --version` |
| Versi Wireshark | ____ | Help → About |
| Versi Npcap | ____ | Wireshark → Help → About → Folders |
| Versi Python | ____ (target 3.12) | `python --version` |
| Versi Git | ____ | `git --version` |
| Nama interface laptop ke port mirror | ____ | Wireshark → Capture → Options |

---

## 3. Jaringan

| Item | Nilai |
|---|---|
| Subnet Pi | 192.168.10.0/24 |
| Subnet laptop dan ESP | 192.168.11.x (laptop), 192.168.12.x (ESP) |
| Subnet di proposal | 192.168.1.0/24 (belum diselaraskan) |
| Gateway laptop | 192.168.11.1 (MikroTik) |
| Catatan | Pi, laptop, dan ESP berada di subnet berbeda. Trafik antar subnet dirutekan MikroTik. |

### Identitas perangkat

Setiap IP dicocokkan dengan MAC address di MikroTik atau di laptop. IP dari DHCP dapat berubah, jadi identifikasi berbasis MAC.

| IP | MAC | Host name | Identitas | Dikonfirmasi dengan |
|---|---|---|---|---|
| 192.168.12.234 | E0:8C:FE:5D:03:68 | esp32-5D0368 | ESP32, ESP#1 (MQTT, topik `sensor/node1/fc28`) | MikroTik lease + tcpdump di Pi (publish berkala terlihat) |
| 192.168.11.253 | 08:97:98:7E:AF:CA | NITRO-5 | Laptop, pengirim pilot MQTT awal (bukan ESP) | `ipconfig /all` dan MikroTik lease |
| 192.168.12.236 | ____ | ____ | Dugaan ESP#2 (CoAP PUT `/motion`) | ____ |
| 192.168.12.242 | ____ | ____ | Dugaan ESP#3 (HTTP POST `/api/sensor/http`) | ____ |
| 192.168.12.251 | ____ | ____ | Dugaan laptop (sesi lama) | ____ |
| 192.168.12.238 | ____ | ____ | Dugaan laptop (sesi lama) | ____ |

**Catatan:** IP `192.168.12.236`, `.242`, `.251`, dan `.238` berasal dari capture sesi sebelumnya. Belum ada MAC yang dikonfirmasi untuk keempatnya.

---

## 4. Layanan di Raspberry Pi

| Layanan | Port | Status | Keterangan |
|---|---|---|---|
| Mosquitto (MQTT) | TCP 1883 | Aktif | `listener 0.0.0.0:1883`, `allow_anonymous true` (hanya jaringan uji) |
| Server CoAP | UDP 5683 | Berjalan manual | `~/coap-server/server.py`, belum dijadikan service (perlu tmux atau systemd) |
| Server HTTP | TCP 80 | Berjalan manual | `~/coap-server/http_server.py`, belum dijadikan service |

**Status respons saat uji:**
- CoAP PUT `/motion`: awalnya 4.05 Method Not Allowed, sekarang 2.04 Changed (setelah perbaikan server).
- HTTP POST `/api/sensor/http`: awalnya 404, status sekarang ____. Harus 200 sebelum run tiga protokol.

---

## 5. Konfigurasi

**Mosquitto** (`/etc/mosquitto/conf.d/lab.conf`):

```
listener 1883 0.0.0.0
allow_anonymous true
```

**Sudoers** (`/etc/sudoers.d/tcpdump`):

```
ragoon ALL=(root) NOPASSWD: /usr/sbin/tcpdump
```

**Port mirror MikroTik:**
- Switch: switch1 (Atheros 8227)
- Port sumber (mirror source): ether2 (Raspberry Pi 3)
- Port target (mirror target): ether3 (laptop)
- Arah mirror (ingress / egress / keduanya): ____
- Verifikasi trafik ESP: **lulus**. Filter `ip.addr == 192.168.12.234 && tcp.port == 1883` di laptop menampilkan publish dan keep-alive ESP tanpa melibatkan IP laptop (29 Okt 2026).
- Uji ping laptop ke Pi: **tidak dapat dijadikan bukti**, karena laptop melihat trafiknya sendiri.
- Pengecekan duplikasi: Wireshark ____ paket vs tcpdump ____ paket (60 detik, filter sama). **Belum dilakukan.**

**Filter capture:**
- Jalur B (MQTT saja): `tcp port 1883`
- Jalur A (tiga protokol): `tcp port 1883 or udp port 5683 or tcp port 80`

---

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
- Sumber baseline MQTT adalah ESP#1 (192.168.12.234). Pilot awal dari laptop hanya untuk menguji pipeline, bukan baseline.
- Selama run resmi, laptop tidak mengirim trafik MQTT (`mosquitto_pub` dan `mosquitto_sub` dihentikan).
- Trafik ESP ke Pi dirutekan MikroTik. Pi tetap menjadi sumber utama dataset, mirror menjadi sumber verifikasi.
- Topik baseline ESP#1 adalah `sensor/node1/fc28`.

---

## 7. Uji coba

| Tanggal | Uji | Hasil |
|---|---|---|
| ____ | Mosquitto publish dari WSL dan PowerShell | Berhasil, topik `test/capture` |
| ____ | tcpdump `-c 5` port 1883 | 5 paket tertangkap |
| ____ | tcpdump filter gabungan (1883, 5683, 80) | Berhasil setelah perbaikan ketik |
| ____ | SHA-256 Pi dan WSL untuk `uji_coba.pcap` | Cocok: `948658811b5defc...` |
| ____ | `frame contains "halo"` di Wireshark | Ditemukan pada paket publish |
| ____ | `mqtt_publish.log` untuk `test/capture` | ____ |
| ____ | Pilot MQTT (2 menit) dengan `tcp port 1883` dari laptop | conn.log memuat 1883, service `mqtt` |
| ____ | Respons HTTP 200 (`curl -i -X POST`) | ____ |
| ____ | Respons CoAP 2.04 (`aiocoap-client`) | ____ |
| 29 Okt 2026 | Pilot ESP#1 (192.168.12.234), 120 detik, filter `tcp port 1883` | conn.log: 1 koneksi persisten 115 detik. mqtt_publish.log: 24 publish |
| 29 Okt 2026 | Verifikasi port mirror dengan trafik ESP (`ip.addr == 192.168.12.234 && tcp.port == 1883`) | Publish dan keep-alive ESP terlihat di laptop |
| 29 Okt 2026 | Pengecekan duplikasi mirror (60 detik) | **Belum dilakukan** |
| ____ | Ping laptop ke Pi, ICMP di Wireshark | Tidak dijadikan bukti (lihat bagian 5) |

---

## 8. Pola MQTT ESP#1 (baseline)

| Item | Nilai | Sumber |
|---|---|---|
| Sumber | 192.168.12.234 (ESP32, `esp32-5D0368`) | MikroTik lease |
| Broker | 192.168.10.199:1883 | Konfigurasi firmware |
| Topik | `sensor/node1/fc28` | Wireshark |
| Interval publish | Sekitar 5 detik (terlihat 7005, 7010, 7015, 7020, 7025 pada capture) | Wireshark |
| Ukuran frame publish | 141 byte (total frame di Wire) | Wireshark |
| Ukuran payload TCP | 87 byte | tcpdump |
| Keep-alive | PINGREQ 60 byte dan PINGRESP 60 byte, di antara publish. Interval belum diukur | Wireshark |
| Pola koneksi | Satu koneksi persisten (pilot 115 detik, 24 publish) | conn.log |
| Jumlah ACK dari broker | Satu ACK per publish | Wireshark |

**Hal yang belum diketahui:**
- Interval keep-alive yang tetap
- Penyebab sesekali interval publish lebih dari 5 detik (misalnya 7 atau 8 detik)
- Satu frame 176 byte yang terlihat di capture. Isinya belum diperiksa

---

## 9. Catatan dan temuan

- **Zeek dipasang dari OBS.** Format repositori yang dipakai: `deb http://download.opensuse.org/repositories/security:/zeek/xUbuntu_22.04/ ./` (suite `./`, tanpa spasi di URL). Belum dicocokkan dengan docs.zeek.org.
- **Postfix dipasang sebagai dependensi Zeek** dengan konfigurasi Local only, mail name `localhost`.
- **`wireshark-common` dipasang di WSL** dengan opsi non-superuser tidak diaktifkan.
- **Pola koneksi berbeda menurut sumber:**
  - Laptop (pilot awal): setiap publish membuka koneksi baru, sekitar 3 ms per koneksi.
  - ESP32 (192.168.12.234): satu koneksi persisten, publish berkala.
- **Interface Wireshark remote `ragoon-broker` tidak dipakai.** Dialog RPCAP menghasilkan error 10054 karena Pi tidak menjalankan `rpcapd`.
- **Percobaan ganti password MikroTik** gagal karena password baru sama dengan yang lama. Password perlu diganti dengan nilai yang berbeda. Nilainya tidak dicatat di dokumen ini.
- **Dokumen proposal dan diagram** masih memuat `192.168.1.1` dan Raspberry Pi 4 di beberapa bagian. Perlu diselaraskan dengan kondisi sekarang (192.168.10.199 dan Raspberry Pi 3 Model B).
- **IP laptop berubah antar sesi** (`.236`, `.238`, `.251`, `.253`). Kolom IP sumber di dataset dicatat per sesi.

---

## 10. Yang belum dikerjakan

- [ ] Pengecekan duplikasi mirror (Wireshark vs tcpdump, 60 detik, filter sama)
- [ ] Arah mirror dicatat (ingress / egress / keduanya)
- [ ] Ruang disk Pi dicek (`df -h ~`, minimal 2 GB tersisa)
- [ ] Server CoAP dan HTTP dijalankan sebagai service (tmux atau systemd)
- [ ] Respons HTTP 200 terverifikasi
- [ ] MAC dan identitas 192.168.12.236, .242, .251, dan .238 dikonfirmasi
- [ ] Durasi S1 sampai S6 disepakati dengan Aslan
- [ ] Ambang kriteria anomali disepakati dengan Aslan
- [ ] Penjelasan frame 176 byte di capture
- [ ] Run S1 resmi (3 kali)
- [ ] Skrip ekstraksi fitur MQTT
- [ ] Dataset MQTT dan validasi 20 persen sampel
