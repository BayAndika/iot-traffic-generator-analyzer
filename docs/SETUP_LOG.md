# Setup Log

**Proyek:** IoT Traffic Generator & Analyzer
**Peran:** Network Capture & Dataset Engineer
**Pemilik catatan:** Bayu Andika Wibisono
**Terakhir diperbarui:** 1 November 2026

> Aturan pengisian: nilai yang belum diketahui tetap `____`. Jangan diisi dengan perkiraan. Setiap perubahan konfigurasi dicatat dengan tanggal dan alasannya.

---

## 1. Perangkat

| Item | Nilai | Cara cek |
|---|---|---|
| Model Raspberry Pi | Raspberry Pi 3 Model B | `cat /proc/device-tree/model` |
| Hostname Pi | ragoon-broker | `hostname` |
| User Pi | ragoon | - |
| Versi Raspberry Pi OS | Debian GNU/Linux 13 (trixie), versi 13.7 | `cat /etc/os-release` |
| Kernel Pi | 6.18.50+rpt-rpi-v8 | `uname -r` |
| IP Pi | 192.168.10.199 | `hostname -I` |
| Versi Mosquitto | 2.0.21 | `mosquitto -h` |
| Versi tcpdump (Pi) | 4.99.5 (libpcap 1.10.5, TPACKET_V3, OpenSSL 3.5.7) | `tcpdump --version` |
| Model MikroTik | switch1 (Atheros 8227) | `/system resource print` |
| Versi RouterOS | 7.16.2 | `/system resource print` |

---

## 2. Laptop dan WSL

| Item | Nilai | Cara cek |
|---|---|---|
| Versi Windows | Windows 10 (21H2, build 19044) | `winver` |
| Versi WSL | 2 | `wsl -l -v` |
| Distro WSL | Ubuntu-22.04 | `lsb_release -a` |
| Versi Zeek | 9.0.0 | `zeek --version` |
| Versi Wireshark | 4.6.9 (dari metadata capture Dumpcap) | Help → About |
| Versi Npcap | ____ | Wireshark → Help → About → Folders |
| Versi Python | ____ (target 3.12) | `python --version` |
| Versi Git | 2.34.1 (di WSL Ubuntu 22.04) | `git --version` |
| Interface laptop ke port mirror | Ethernet (Realtek Gaming GbE), tersambung ke ether3 | Wireshark → Capture → Options |

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

| IP | MAC | Host name | Identitas | Status lease | Dikonfirmasi dengan |
|---|---|---|---|---|---|
| 192.168.12.234 | E0:8C:FE:5D:03:68 | esp32-5D0368 | ESP#1, MQTT, topik sensor/node1/fc28 | bound, static | Lease static (dynamic=no), publish berkala terlihat |
| 192.168.12.233 | E0:8C:FE:5C:95:48 | esp32-5C9548 | ESP#3, HTTP, device_id node_02_http | bound, static | Lease static, 165 paket port 80 per 120 detik, log server POST 200 |
| 192.168.12.236 | E0:8C:FE:5C:75:00 | esp32-5C7500 | ESP#2, CoAP, device_id node_03_coap | bound, static | Lease static, 25 paket UDP 5683 per 120 detik, log server Data Masuk |
| 192.168.11.253 | 08:97:98:7E:AF:CA | NITRO-5 | Laptop, pengirim pilot MQTT awal (bukan ESP) | - | `ipconfig /all` dan MikroTik lease |
| 192.168.12.242 | ____ | ____ | Dugaan ESP#3 dari capture HTTP lama, sekarang tidak terpakai | ____ | Belum dikonfirmasi |
| 192.168.12.251 | ____ | ____ | Dugaan laptop (sesi lama) | ____ | Belum dikonfirmasi |
| 192.168.12.238 | ____ | ____ | Dugaan laptop (sesi lama) | ____ | Belum dikonfirmasi |
| 192.168.11.254 dan 192.168.12.254 | B8:27:EB:CB:6A:9C dan B8:27:EB:9E:3F:C9 | ragoon-broker | Lease `waiting` lama dari interface Pi yang tidak aktif | waiting | `/ip dhcp-server lease print` (1 Nov 2026). Jangan dihapus sebelum dicek |

**Catatan:**
- IP HTTP berubah dari `.242` (capture lama) menjadi `.233` (label MikroTik dan trafik port 80 saat ini).
- IP CoAP `.236` tercatat dari capture lama. Sempat `waiting` (29 Okt), lalu kembali `bound` dan static (1 Nov).
- Kolom `LAST-SEEN` di MikroTik tidak dipakai sebagai indikator aktivitas. Yang dipakai adalah status lease dan trafik di Pi.

---

## 4. Layanan di Raspberry Pi

| Layanan | Port | Status | Proses | Keterangan |
|---|---|---|---|---|
| Mosquitto (MQTT) | TCP 1883 | Aktif | PID 1301 (systemd) | `listener 0.0.0.0:1883`, `allow_anonymous true` (hanya jaringan uji) |
| Server CoAP | UDP 5683 dan TCP 5683 | Aktif (tmux sesi `coap`) | PID 4538, `python server.py` | Listener TCP 5683 kemungkinan bawaan library. Dicek 1 Nov 2026 |
| Server HTTP | TCP 80 | Aktif (tmux sesi `http`, sudo) | PID 4585, `http_server.py` | Listen 0.0.0.0:80. Dicek 1 Nov 2026 |

**Status respons saat uji:**
- CoAP PUT `/motion`: awalnya 4.05 Method Not Allowed, lalu 2.04 Changed setelah perbaikan server. Uji manual ke `coap://127.0.0.1/motion` menghasilkan kode respons `44` (2.04 Changed), payload `OK`.
- HTTP POST `/api/sensor/http`: awalnya 404, lalu 200 OK (curl, 29 Okt 2026, payload `{"status":"ok"}`).

**Catatan operasional:**
- Server CoAP dan HTTP dijalankan di tmux. Sesi `coap` dan `http` tetap hidup walau SSH ditutup. Masuk lagi dengan `tmux attach -t coap` atau `tmux attach -t http`. Keluar tanpa mematikan server: Ctrl+B lalu D.
- Server HTTP memakai `sudo ./venv/bin/python http_server.py`, karena port 80 butuh root dan Python dari venv harus dipakai langsung.
- Sebelum run resmi, cek `tmux ls` dan `sudo ss -tulnp | grep -E '1883|5683|:80 '`.
- `localhost` di-resolve ke IPv6 (`::1`) sedangkan server aktif di IPv4. Uji lokal memakai `127.0.0.1`.
- Pi belum bisa `apt install` karena DNS. Ping `8.8.8.8` berhasil, tapi nama domain gagal. Penyebab: MikroTik DNS tidak mengizinkan remote request. Perbaikan: aktifkan **Allow Remote Requests** di `/ip dns`. Belum dicatat sebagai selesai.

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
- Pengecekan duplikasi (29 Okt 2026, 60 detik): Pi tcpdump 38 captured, 40 received by filter, 0 dropped. Wireshark ether3 dengan filter `ip.addr == 192.168.12.234 && tcp.port == 1883`: 200,7 detik, 138 displayed. Laju 0,63 vs 0,69 paket/detik, rasio sekitar 1,1. **Hasil: lulus, tidak ada duplikasi.**
- Wireshark ether3 tanpa filter menangkap 28.666 paket dalam 206,9 detik. Belum dijelaskan. Perlu dicek port lain di switch1 dan apakah ada broadcast atau flood: ____

**Filter capture:**
- Jalur B (MQTT saja, fallback): `tcp port 1883`
- Jalur A (tiga protokol): `tcp port 1883 or udp port 5683 or tcp port 80`

**Ruang disk Pi (29 Okt 2026):** Avail 104G (`df -h ~`). Cukup untuk 18 run.

---

## 6. Keputusan

- Capture resmi dilakukan dengan tcpdump di Pi dan disimpan sebagai file PCAP.
- Remote capture RPCAP tidak dipakai karena Pi tidak menjalankan `rpcapd`.
- Remote capture SSH (sshdump) dipakai hanya untuk inspeksi, bukan dataset.
- Zeek dijalankan offline di WSL Ubuntu 22.04, tidak di Pi.
- Wireshark dipasang tanpa tshark. Npcap dipasang untuk port mirror.
- Target dataset utama adalah tiga protokol (Jalur A). Jalur B (MQTT saja) dipakai sebagai fallback jika gerbang CoAP dan HTTP gagal sampai tenggat, dan hanya dengan persetujuan dosen.
- Dataset final hanya memakai satu jalur. Run tiga protokol tidak dicampur dengan run MQTT saja.
- Durasi S1 sementara 600 detik. Menunggu persetujuan Aslan.
- Pemetaan skenario: S1 traffic normal, S2 connection burst, S3 abnormal publishing/request, S4 abnormal subscription/observe/polling, S5 abnormal topic/resource/endpoint, S6 traffic campuran. Mengikuti Rencana Pengujian di proposal. Persetujuan Aslan: ____
- Setiap run diberi nomor ulang. Run yang gagal tidak ditimpa, tetap tercatat di `runs.csv` dengan status GAGAL.
- Run dianggap valid jika: hash Pi dan WSL sama, ketiga protokol lebih dari 0 paket, dan `dropped by kernel` = 0.
- Interface capture tetap `eth0`. Jika berubah, catat di sini dan buat run baru.
- Timeline dashboard bersifat offline, bukan real-time.
- Sumber baseline MQTT adalah ESP#1 (192.168.12.234). Pilot awal dari laptop hanya untuk menguji pipeline, bukan baseline.
- Selama run resmi, laptop tidak mengirim trafik MQTT (`mosquitto_pub` dan `mosquitto_sub` dihentikan).
- Trafik ESP ke Pi dirutekan MikroTik. Pi tetap menjadi sumber utama dataset, mirror menjadi sumber verifikasi.
- Topik baseline ESP#1 adalah `sensor/node1/fc28`.
- Identifikasi perangkat dilakukan lewat MAC address dan status lease, bukan IP saja.
- Selama CoAP belum `bound` dan mengirim data selain `{"test":1}`, CoAP tidak masuk dataset.
- Pelabelan: S1 seluruhnya normal. Skenario S2 sampai S5 seluruhnya anomali. S6 dilabeli per jendela berdasarkan `metadata/anomali_interval.csv`.
- Ukuran jendela pelabelan 5 detik, sama untuk semua run.
- S2 tidak dijalankan sebelum generator burst diuji Farel dan pilot 2 menit menunjukkan kenaikan jumlah koneksi dibanding S1.

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
| 29 Okt 2026 | Respons HTTP 200 (`curl -i -X POST`) | 200 OK, `{"status":"ok"}` |
| 29 Okt 2026 | Respons CoAP 2.04 dari uji lokal (`aiocoap-client` ke `127.0.0.1`) | Kode `44` (2.04 Changed), payload `OK`, dibaca dari `tcpdump -i lo -X` |
| 29 Okt 2026 | Pilot ESP#1 (192.168.12.234), 120 detik, filter `tcp port 1883` | conn.log: 1 koneksi persisten 115 detik. mqtt_publish.log: 24 publish |
| 29 Okt 2026 | Verifikasi port mirror dengan trafik ESP (`ip.addr == 192.168.12.234 && tcp.port == 1883`) | Publish dan keep-alive ESP terlihat di laptop |
| 29 Okt 2026 | Hitung UDP 5683 dari 192.168.12.236, 60 detik (dua arah, `wc -l`) | Hasil 1. Tidak valid karena menghitung balasan server |
| 29 Okt 2026 | Hitung UDP 5683 dari 192.168.12.236, 120 detik (`src host`, `-tt`) | Tidak ada paket. ESP#2 tidak mengirim saat itu |
| 29 Okt 2026 | Lease ESP#2 (`E0:8C:FE:5C:75:..`) di MikroTik | `waiting` saat tes. Kemudian `bound` static |
| 29 Okt 2026 | Pengecekan duplikasi mirror (60 detik) | Lulus. Laju 0,63 vs 0,69 paket/detik. Detail di bagian 5 |
| 29 Okt 2026 | Tiga gerbang tiga protokol (HTTP 200, ESP#3 port 80, ESP#2 UDP 5683, data sensor diterima, lease static) | Lulus. ESP#3 165 paket, ESP#2 25 paket per 120 detik |
| 1 Nov 2026 | Ulang cek UDP 5683 dari 192.168.12.236, 60 detik (`src host`) | 13 paket. ESP#2 mengirim |
| 1 Nov 2026 | Pilot tiga protokol 120 detik, filter `tcp port 1883 or udp port 5683 or tcp port 80` | tcpdump: 430 captured, 440 received by filter, 0 dropped. Per protokol: MQTT 80, CoAP 48, HTTP 302 paket. Zeek conn.log: 1883 (1 koneksi), 5683 (1 flow), 80 (24 koneksi). Lulus |
| 1 Nov 2026 | Ping laptop ke Pi, ICMP di Wireshark | Tidak dijadikan bukti (lihat bagian 5) |

---

## 8. Pola MQTT ESP#1 (baseline)

| Item | Nilai | Sumber |
|---|---|---|
| Sumber | 192.168.12.234 (ESP32, `esp32-5D0368`) | MikroTik lease |
| Broker | 192.168.10.199:1883 | Konfigurasi firmware |
| Topik | `sensor/node1/fc28` | Wireshark |
| Interval publish | Sekitar 5 detik (terlihat 7005, 7010, 7015, 7020, 7025 pada capture) | Wireshark |
| Ukuran frame Ethernet publish | 141 byte | Wireshark |
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
- **Password MikroTik** sudah diganti. Nilainya tidak dicatat di dokumen ini.
- **Dokumen proposal dan diagram** masih memuat `192.168.1.1` dan Raspberry Pi 4 di beberapa bagian. Perlu diselaraskan dengan kondisi sekarang (192.168.10.199 dan Raspberry Pi 3 Model B).
- **IP laptop dan ESP berubah antar sesi.** Laptop tercatat di `.236`, `.238`, `.251`, `.253`. HTTP tercatat di `.242` dan `.233`. Kolom IP sumber di dataset dicatat per sesi, dan identitas selalu dicocokkan dengan MAC.
- **Pesan `Data Masuk: {"test":1}` di server CoAP** berasal dari uji manual, bukan dari ESP#2.
- **Port mirror routed:** trafik ESP ke Pi dirutekan MikroTik. Dari uji Wireshark, paket ESP tetap terlihat di ether3, tetapi cakupannya hanya dianggap valid setelah pengecekan jumlah dan arah.
- **Run 2 gagal** karena ESP#2 tidak mengirim (lease sempat hilang). Run 2b diulang setelah lease static dan ESP#2 terbukti mengirim.
- **Run 1 dan run 2b punya hasil Zeek identik** (2 / 1 / 119). Itu mungkin wajar, tapi belum dicek dengan timestamp pertama `conn.log` di folder `S1_normal_run2b`.
- Run 1 sempat tercampur log Zeek run 2b (folder zeek). Sudah diperbaiki dengan Zeek ulang dari PCAP. Timestamp pertama 1793471318 sesuai runs.csv.
- Ekstraksi fitur menghitung 3 run S1 valid (run 1, run 2b, run 3). Run 2 tidak dipakai.
- ESP#1 mengirim SUBSCRIBE sekali per koneksi (run 1 dan run 2b). Dicatat sebagai perilaku firmware. Run 3 tidak tercatat di jendela S1.
- Baseline S1 dibuat dari run_summary dan traffic_features (docs/BASELINE_S1.csv).

---

## 10. Yang belum dikerjakan

**Sudah selesai:**
- [x] Pengecekan duplikasi mirror (lulus, 29 Okt 2026)
- [x] Ruang disk Pi dicek (Avail 104G)
- [x] Mosquitto aktif (PID 1301)
- [x] Server CoAP dan HTTP dipindah ke tmux (1 Nov 2026)
- [x] Respons HTTP 200 terverifikasi (curl, 29 Okt 2026)
- [x] ESP#3 mengirim HTTP dengan respons 200
- [x] ESP#2 mengirim CoAP dan data sensor diterima server
- [x] Lease ESP#1, ESP#2, dan ESP#3 static (dynamic=no)
- [x] Pilot tiga protokol 2 menit lulus (1 Nov 2026)
- [x] Gerbang tiga protokol lulus (29 Okt sampai 1 Nov 2026)
- [x] S1 run 1, run 2b, dan run 3 valid (lihat bagian 11)

**Belum selesai:**
- [ ] Arah mirror dicatat (ingress / egress / keduanya)
- [ ] Penjelasan 28.666 paket tanpa filter di Wireshark (port lain atau flood)
- [ ] Lease waiting 192.168.11.254 dan 192.168.12.254 diperiksa dan dihapus jika tidak dipakai
- [ ] DNS Pi: aktifkan Allow Remote Requests di MikroTik agar `apt install` bisa jalan
- [ ] Timestamp `conn.log` run 2b dicek (apakah benar milik run 2b)
- [ ] MAC dan identitas 192.168.12.242, .251, dan .238 dikonfirmasi, atau dicatat sebagai tidak dipakai
- [ ] Durasi S1 sampai S6 disepakati dengan Aslan
- [ ] Ambang kriteria anomali disepakati dengan Aslan
- [ ] Pemetaan S1 sampai S6 disetujui Aslan dan dosen
- [ ] Keputusan dataset final (tiga protokol atau fallback MQTT) disetujui dosen
- [ ] Penjelasan frame 176 byte di capture
- [ ] Generator burst S2 diuji Farel dan pilot S2 lolos
- [ ] Run S2 sampai S6 (masing-masing 3 run)
- [ ] Skrip ekstraksi, pelabelan, dan validasi dijalankan pada data nyata
- [ ] Dataset dan validasi 20 persen sampel
- [ ] Dokumen wajib (PANDUAN_CAPTURE, KEBIJAKAN_FILTER, PANDUAN_LABEL, VALIDASI_LABEL, README dataset, notebook EDA)

---

## 11. Ringkasan run

| Run | Skenario | Ulang | Status | Hash Pi = WSL | Captured | Received by filter | Dropped | MQTT / CoAP / HTTP (paket) | Catatan |
|---|---|---|---|---|---|---|---|---|---|
| S1_normal_run1 | S1_normal | 1 | Valid | Ya | 2193 | 2206 | 0 | - | Waktu 01:28:34 sampai 01:39:27 (653 detik nyata). Zeek: 1883 (2), 5683 (1), 80 (119) |
| S1_normal_run2 | S1_normal | 2 | GAGAL | - | 1951 | 1953 | 0 | 404 / 0 / 1547 | CoAP 0 paket. ESP#2 tidak mengirim. Tidak dipakai |
| S1_normal_run2b | S1_normal | 2 | Valid, timestamp Zeek belum dicek | Ya | 2189 | 2192 | 0 | 409 / 240 / 1540 | Waktu 04:22:32 sampai 04:32:47 (615 detik nyata). Hash `46f2098d...` |
| S1_normal_run3 | S1_normal | 3 | Valid | Ya | 2171 | 2171 | 0 | 400 / 240 / 1531 | Waktu 04:46:07 sampai 04:56:32 (625 detik nyata). Hash `4e55b1df...` |
| S2 sampai S6 | - | - | Belum | - | - | - | - | - | Menunggu generator anomali (Farel dan Aslan) |

**Status S1:** 3 run valid, baseline dibuat. Run 2 tetap disimpan sebagai catatan kegagalan.