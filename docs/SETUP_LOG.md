# Setup Log

**Proyek:** IoT Traffic Generator & Analyzer
**Peran:** Network Capture & Dataset Engineer
**Pemilik catatan:** Bayu Andika Wibisono
**Terakhir diperbarui:** 10 November 2026

> Aturan pengisian: nilai yang belum diketahui tetap `____`. Jangan diisi dengan perkiraan. Setiap perubahan konfigurasi dicatat dengan tanggal dan alasannya.
> Perubahan 9 Nov 2026: beberapa `____` yang bisa dibuktikan dari 18 PCAP run telah diisi dan ditandai "(dari PCAP, 9 Nov 2026)". Sisanya tetap `____` karena membutuhkan akses Pi/MikroTik/laptop.
> Perubahan 10 Nov 2026: hash 18 PCAP dicocokkan (18/18 cocok), dataset divalidasi ulang, misteri "1883 (2)" run1 terpecahkan (ESP#1 reconnect), penyebab gap publish ditemukan (reconnect), dan lease baru `.243` teridentifikasi dari screenshot WinBox.

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
| Model MikroTik | hAP ac lite (mipsbe), switch chip Atheros 8227 — dari screenshot WinBox 31 Okt 2026 | `/system resource print` |
| Versi RouterOS | 7.16.2 (stable) | `/system resource print`; screenshot WinBox 31 Okt 2026 |

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
| Versi Python (WSL, venv-proyek) | ____ (target 3.12) | `python3 --version` |
| Versi Python (Windows, generator anomali) | ____ | `python --version` |
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
| 192.168.12.234 | E0:8C:FE:5D:03:68 | esp32-5D0368 | ESP#1, MQTT, topik `sensor/node1/fc28` | bound, static | Lease static (dynamic=no), publish berkala terlihat |
| 192.168.12.233 | E0:8C:FE:5C:95:48 | esp32-5C9548 | ESP#3, HTTP, device_id `node_02_http` | bound, static | Lease static, 165 paket port 80 per 120 detik, log server POST 200 |
| 192.168.12.236 | E0:8C:FE:5C:75:00 | esp32-5C7500 | ESP#2, CoAP, device_id `node_03_coap` | bound, static | Lease static, 25 paket UDP 5683 per 120 detik, log server Data Masuk |
| 192.168.11.253 | 08:97:98:7E:AF:CA | NITRO-5 | Laptop, host generator anomali (`anomali.py`) dan pengirim pilot MQTT awal | - | `ipconfig /all` dan MikroTik lease |
| 192.168.12.242 | ____ | ____ | Dugaan ESP#3 dari capture HTTP lama, sekarang tidak terpakai | ____ | Tidak muncul di 18 PCAP run (dari PCAP, 9 Nov 2026); status lease cek di MikroTik |
| 192.168.12.251 | ____ | ____ | Dugaan laptop (sesi lama) | ____ | Tidak muncul di 18 PCAP run (dari PCAP, 9 Nov 2026); status lease cek di MikroTik |
| 192.168.12.238 | ____ | ____ | Dugaan laptop (sesi lama) | ____ | Tidak muncul di 18 PCAP run (dari PCAP, 9 Nov 2026) dan tidak ada di lease WinBox 31 Okt 2026; status lease cek di MikroTik |
| 192.168.12.243 | 10:63:C8:81:4B:5F | Nitro-5 | Laptop — lease DHCP dynamic lama di subnet ESP (dari screenshot WinBox, 31 Okt 2026) | D (dynamic) | Screenshot WinBox 31 Okt 2026; menjelaskan IP laptop yang berubah-ubah lintas subnet |
| 192.168.11.254 dan 192.168.12.254 | B8:27:EB:CB:6A:9C dan B8:27:EB:9E:3F:C9 | ragoon-broker | Lease `waiting` lama dari interface Pi yang tidak aktif | waiting | `/ip dhcp-server lease print` (1 Nov 2026). Jangan dihapus sebelum dicek. Terlihat juga di screenshot WinBox 31 Okt 2026 (flag D) |

**Catatan:**
- IP HTTP berubah dari `.242` (capture lama) menjadi `.233` (label MikroTik dan trafik port 80 saat ini).
- IP CoAP `.236` tercatat dari capture lama. Sempat `waiting` (29 Okt), lalu kembali `bound` dan static (1 Nov).
- Kolom `LAST-SEEN` di MikroTik tidak dipakai sebagai indikator aktivitas. Yang dipakai adalah status lease dan trafik di Pi.
- Traffic anomali berasal dari laptop (192.168.11.253), sedangkan traffic normal berasal dari ESP. Sumber ini dicatat di `anomali_log.csv`, tidak di kolom dataset.
- Di 18 PCAP run (9 Nov 2026), hanya dua MAC yang tampil di layer 2: MAC Pi `b8:27:eb:cb:6a:9c` (cocok dengan lease ragoon-broker) dan MAC `f4:1e:57:e5:5b:85` yang dipakai semua IP non-Pi — itu MAC sisi router, karena mirror routed. Identifikasi MAC perangkat tetap benar dilakukan dari lease MikroTik, bukan dari PCAP.

---

## 4. Layanan di Raspberry Pi

| Layanan | Port | Status | Proses | Keterangan |
|---|---|---|---|---|
| Mosquitto (MQTT) | TCP 1883 | Aktif | PID 1301 (systemd) | `listener 0.0.0.0:1883`, `allow_anonymous true` (hanya jaringan uji) |
| Server CoAP | UDP 5683 dan TCP 5683 | Aktif (tmux sesi `coap`) | PID 4538, `python server.py` | Listener TCP 5683 kemungkinan bawaan library. Dicek 1 Nov 2026 |
| Server HTTP | TCP 80 | Aktif (tmux sesi `http`, sudo) | PID 4585, `http_server.py` | Listen 0.0.0.0:80. Dicek 1 Nov 2026 |

**Status respons saat uji:**
- CoAP PUT `/motion`: awalnya 4.05 Method Not Allowed, lalu 2.04 Changed setelah perbaikan server. Uji manual ke `coap://127.0.0.1/motion` menghasilkan kode respons `44` (2.04 Changed), payload `OK`. Dikonfirmasi dari PCAP (9 Nov 2026): PUT `/motion` mendapat 2.04 di semua run; GET `/motion` dari mesin anomali mendapat 4.05 (S2, S4, S6) dan GET ke resource tidak ada mendapat 4.04 (S5).
- HTTP POST `/api/sensor/http`: awalnya 404, lalu 200 OK (curl, 29 Okt 2026, payload `{"status":"ok"}`).

**Catatan operasional:**
- Server CoAP dan HTTP dijalankan di tmux. Sesi `coap` dan `http` tetap hidup walau SSH ditutup. Masuk lagi dengan `tmux attach -t coap` atau `tmux attach -t http`. Keluar tanpa mematikan server: Ctrl+B lalu D.
- Server HTTP memakai `sudo ./venv/bin/python http_server.py`, karena port 80 butuh root dan Python dari venv harus dipakai langsung.
- Sebelum run, cek `tmux ls` dan `sudo ss -tulnp | grep -E '1883|5683|:80 '`.
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
- Arah mirror (ingress / egress / keduanya): **keduanya (ingress + egress)** — bukti: di semua run, SYN dari ESP/laptop dan SYN-ACK dari Pi untuk flow yang sama sama tertangkap (mis. S2 run1: 1.191 SYN dan 1.191 SYN-ACK; S6 run1: 2.385 pasangan) (dari PCAP, 9 Nov 2026)
- Verifikasi trafik ESP: **lulus**. Filter `ip.addr == 192.168.12.234 && tcp.port == 1883` di laptop menampilkan publish dan keep-alive ESP tanpa melibatkan IP laptop (29 Okt 2026).
- Uji ping laptop ke Pi: **tidak dapat dijadikan bukti**, karena laptop melihat trafiknya sendiri.
- Pengecekan duplikasi (29 Okt 2026, 60 detik): Pi tcpdump 38 captured, 40 received by filter, 0 dropped. Wireshark ether3 dengan filter `ip.addr == 192.168.12.234 && tcp.port == 1883`: 200,7 detik, 138 displayed. Laju 0,63 vs 0,69 paket/detik, rasio sekitar 1,1. **Hasil: lulus, tidak ada duplikasi.**
- Wireshark ether3 tanpa filter menangkap 28.666 paket dalam 206,9 detik. Belum dijelaskan. Perlu dicek port lain di switch1 dan apakah ada broadcast atau flood: ____ (hipotesis untuk diperiksa, bukan jawaban: broadcast/multicast seperti ARP/mDNS/SSDP/DHCP dari port lain yang ikut lewat mirror; cek dengan filter `eth.dst == ff:ff:ff:ff:ff:ff` pada capture tersebut)

**Filter capture:**
- Jalur B (MQTT saja, fallback): `tcp port 1883`
- Jalur A (tiga protokol, dipakai untuk S1 sampai S6): `tcp port 1883 or udp port 5683 or tcp port 80`
- Verifikasi filter (dari PCAP, 9 Nov 2026): di semua 18 PCAP run, MQTT + CoAP + HTTP = total paket **tanpa sisa** (tidak ada paket di luar tiga protokol), sesuai Jalur A.

**Ruang disk Pi (29 Okt 2026):** Avail 104G (`df -h ~`). Cukup untuk 18 run.

**Generator anomali (laptop, Windows):**
- Skrip: `anomali.py` di `C:\PBL\iot-traffic`, dijalankan dengan venv Windows.
- Pemakaian: `python anomali.py <mqtt|http|coap> <burst|publish|subscribe|topic> <durasi> --rate N --tunda N --run <run_id> --log anomali_log.csv`
- Batasan: skrip menolak tujuan di luar `192.168.10.0/24` (ER-08).
- Log: setiap eksekusi menambah satu baris ke `anomali_log.csv` (run, protokol, skenario, mulai, selesai, jumlah aksi, galat). Log ini menjadi dasar `metadata/anomali_interval.csv`.

---

## 6. Keputusan

- Capture resmi dilakukan dengan tcpdump di Pi dan disimpan sebagai file PCAP.
- Remote capture RPCAP tidak dipakai karena Pi tidak menjalankan `rpcapd`.
- Remote capture SSH (sshdump) dipakai hanya untuk inspeksi, bukan dataset.
- Zeek dijalankan offline di WSL Ubuntu 22.04, tidak di Pi.
- Wireshark dipasang tanpa tshark. Npcap dipasang untuk port mirror.
- Dataset final memakai tiga protokol (Jalur A) untuk S1 sampai S6. Jalur B (MQTT saja) hanya fallback yang tidak dipakai.
- Dataset final hanya memakai satu jalur. Run tiga protokol tidak dicampur dengan run MQTT saja.
- Durasi nominal run 600 detik untuk semua skenario. Durasi nyata sedikit lebih panjang (611 sampai 653 detik) karena jeda perintah. Dicatat di `catatan` setiap run. (Rentang isi paket di 18 PCAP: 595,0–598,4 detik, dari PCAP 9 Nov 2026.)
- Pemetaan skenario mengikuti Rencana Pengujian proposal: S1 traffic normal, S2 connection burst, S3 abnormal publishing/request, S4 abnormal subscription/observe/polling, S5 abnormal topic/resource/endpoint, S6 traffic campuran.
- Parameter yang dijalankan (usulan tim, sudah dijalankan; persetujuan tertulis Aslan: ____ tanggal ____):
  - S2 burst: 20 aksi/detik selama 60 detik, tunda 240 detik, MQTT, HTTP, dan CoAP.
  - S3 publish: 2 aksi/detik selama 60 detik, tunda 240 detik, MQTT, HTTP, dan CoAP.
  - S4 subscribe: 2 aksi/detik selama 60 detik, tunda 240 detik, MQTT dan CoAP. HTTP tidak dijalankan.
  - S5 topic: 2 aksi/detik selama 60 detik, tunda 240 detik, MQTT, HTTP, dan CoAP.
  - S6 campuran: burst 20 aksi/detik selama 120 detik (detik 120 sampai 240), lalu publish 2 aksi/detik selama 120 detik (detik 360 sampai 480), per protokol.
  - Verifikasi waktu dari PCAP (9 Nov 2026): jendela S2 (burst pada detik 240–300) dan S6 (burst detik 120–240, fase publish detik 360–480) terbukti **persis** sesuai parameter. S3–S5 terverifikasi dari total aksi (publish 2× lipat, 120 SUBSCRIBE, 120 GET resource anomali).
- Durasi 60 detik dan rate 2 untuk S3 sampai S5 belum disetujui tertulis. Jika Aslan meminta perubahan, run terkait dicatat sebagai run dengan parameter berbeda.
- Generator anomali dijalankan dari laptop (host generator). ESP tetap mengirim traffic normal selama run.
- Selama run, laptop tidak menjalankan `mosquitto_pub` atau `mosquitto_sub` manual. Hanya `anomali.py` yang mengirim traffic anomali, dan semuanya tercatat di `anomali_log.csv`.
- Pilot 2 menit tidak dihitung sebagai run dan tidak masuk dataset.
- Setiap skenario memiliki tiga run valid. Run gagal tidak ditimpa, dan tetap tercatat di `runs.csv` dengan status GAGAL.
- Run dianggap valid jika: hash Pi dan WSL sama, ketiga protokol lebih dari 0 paket, dan `dropped by kernel` = 0. Untuk S2 sampai S6, angka `dropped` tidak tercatat di `runs.csv` karena dilengkapi dari PCAP (lihat bagian 9).
- Pelabelan: S1 seluruhnya normal. S2 sampai S5 anomali pada jendela yang awalnya berada di dalam jadwal burst/publish/subscribe/topic untuk run dan protokol yang sama. S6 anomali per bagian, sesuai `anomali_interval.csv`.
- Ukuran jendela pelabelan 5 detik, sama untuk semua run.
- Ambang "terlihat": rasio 2 kali rata-rata baseline S1 (keputusan tim). Dicek dengan `compare_ke_baseline.py` dan pemeriksaan burst di dataset.
- Interface capture tetap `eth0`. Jika berubah, catat di sini dan buat run baru.
- Timeline dashboard bersifat offline, bukan real-time.
- Sumber baseline MQTT adalah ESP#1 (192.168.12.234). Pilot awal dari laptop hanya untuk menguji pipeline, bukan baseline.
- Topik baseline ESP#1 adalah `sensor/node1/fc28`.
- Identifikasi perangkat dilakukan lewat MAC address dan status lease, bukan IP saja.
- CoAP masuk dataset sejak run S1 valid (ESP#2 mengirim data sensor). Batasan: CoAP tidak punya durasi sesi, dan kolom `pesan` dihitung dari PCAP.
- Nama file dan folder run disamakan dengan `anomali_log.csv`: S3 memakai `S3_pubreq`, S4 memakai `S4_subpoll`.

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
| 6 Nov 2026 | Pilot anomali S2 MQTT (`anomali.py mqtt burst 60 --rate 20 --tunda 30`, run `pilot_S2`) | 1192 aksi, 0 galat. Burst terlihat di data pada tahap pelabelan (lihat baris berikut) |
| 6 Nov 2026 | Run resmi S2 sampai S6 (15 run) dengan `anomali.py` dari laptop | Masing-masing tiga run. Log tercatat di `anomali_log.csv`. Tanggal PCAP dikonfirmasi: S2 run1 mulai 6 Nov 2026 00:52:50 WIB, S3 02:35:35, S4 03:21:05, S5 04:05:30, S6 04:51:19 (dari PCAP, 9 Nov 2026) |
| 6 Nov 2026 | Pembersihan log anomali: pilot dipisah, publish S6 run 2 dan 3 dikelompokkan ulang berdasarkan waktu | 51 baris, 15 run, setiap run S6 berisi 6 baris (3 burst dan 3 publish) |
| 6 Nov 2026 | Ekstraksi fitur, pelabelan per protokol, dan validasi otomatis | LULUS. 6462 baris. S1 normal 1079. S2 anomali 108, S3 anomali 108, S4 anomali 72, S5 anomali 108, S6 anomali 434 |
| 6 Nov 2026 | Pemeriksaan semua baris terhadap jadwal (`cek_label.py all`) | 6462 cocok, 0 tidak cocok |
| 6 Nov 2026 | Pemeriksaan tambahan sampel acak (seed 7, 50 baris) | 50 cocok, 0 tidak cocok |
| 6 Nov 2026 | Pemeriksaan tambahan sampel anomali (seed 9, 20 baris) | 20 cocok, 0 tidak cocok |
| 6 Nov 2026 | Parameter utama per skenario (MQTT, rata-rata normal vs anomali) | S2 connection_rate 0,19 vs 18,1. S3 frekuensi_request 0,22 vs 2,00. S4 subscribe_observe 0,11 vs 9,00. S5 topic_resource_unik 1,10 vs 10,14. S6 connection_rate 0,47 vs 9,17 dan frekuensi_request 0,23 vs 1,15 |

---

## 8. Pola MQTT ESP#1 (baseline)

| Item | Nilai | Sumber |
|---|---|---|
| Sumber | 192.168.12.234 (ESP32, `esp32-5D0368`) | MikroTik lease |
| Broker | 192.168.10.199:1883 | Konfigurasi firmware |
| Topik | `sensor/node1/fc28` | Wireshark |
| Interval publish | Sekitar 5 detik (median 5,00 detik, 119–120 publish per run ±10 menit) | Wireshark; PCAP (9 Nov 2026) |
| Ukuran frame Ethernet publish | 141 byte | Wireshark; dikonfirmasi PCAP: tepat 141 byte untuk 120/120 publish run3 (9 Nov 2026) |
| Ukuran payload TCP | 87 byte | tcpdump; dikonfirmasi PCAP: tepat 87 byte (9 Nov 2026) |
| Keep-alive | PINGREQ 60 byte dan PINGRESP 60 byte (payload TCP 2 byte). **Interval tetap 15 detik** (median selisih antar-PINGREQ 15,01 detik; 39–40 PINGREQ per run, konsisten di 18 run) | Wireshark; interval dari PCAP (9 Nov 2026) |
| Pola koneksi | Satu koneksi persisten (pilot 115 detik, 24 publish) | conn.log |
| Jumlah ACK dari broker | Satu ACK per publish | Wireshark |
| SUBSCRIBE awal | Satu SUBSCRIBE per koneksi saat tersambung (run 1 dan run 2b), topik `control/node1/pump`. Dicatat sebagai perilaku firmware | `cek_subscribe.py`; dikonfirmasi PCAP (9 Nov 2026): pengirim = 192.168.12.234 (ESP#1), hanya pada koneksi yang tersambung selama capture — run1 di detik 434 dan run2b di detik 322, keduanya saat ESP#1 reconnect; tidak ada di run3 |

**Hal yang belum diketahui:**
- ~~Interval keep-alive yang tetap~~ **Terjawab (9 Nov 2026): 15 detik**, terukur konsisten di semua run.
- ~~Penyebab sesekali interval publish lebih dari 5 detik~~ **Terjawab (10 Nov 2026): reconnect ESP#1.** Bukti: gap publish run1 (10,32 detik, 1745,6 → 1755,9) tepat mengapit momen reconnect di 1752,554 (port sumber berganti 65082 → 53669); gap run2b (10,12 detik, 2075,6 → 2085,7) mengapit reconnect di 2082,736; run3 tanpa reconnect dan tanpa gap. Jadi selama ESP#1 reconnect, publish tertahan ±2 interval.
- Satu frame 176 byte yang terlihat di capture. Isinya belum diperiksa. **Tambahan (9 Nov 2026): tidak ada frame 174–178 byte di 18 PCAP run** — frame itu berasal dari capture lain (pilot/uji coba 29 Okt), bukan dari dataset.

---

## 9. Catatan dan temuan

- **Zeek dipasang dari OBS.** Format repositori yang dipakai: `deb http://download.opensuse.org/repositories/security:/zeek/xUbuntu_22.04/ ./` (suite `./`, tanpa spasi di URL). Belum dicocokkan dengan docs.zeek.org.
- **Postfix dipasang sebagai dependensi Zeek** dengan konfigurasi Local only, mail name `localhost`.
- **`wireshark-common` dipasang di WSL** dengan opsi non-superuser tidak diaktifkan.
- **Pola koneksi berbeda menurut sumber:**
  - Laptop (pilot awal): setiap publish membuka koneksi baru, sekitar 3 ms per koneksi.
  - ESP32 (192.168.12.234): satu koneksi persisten, publish berkala.
- **Interface Wireshark remote `ragoon-broker` tidak dipakai.** Dialog RPCAP menghasilkan error 10054 karena Pi tidak menjalankan `rpcapd`.
- **Password MikroTik** sudah diganti. Nilainya tidak dicatat di dokumen ini. Password Pi yang pernah diketik di chat AI perlu dipastikan sudah diganti: ____ (tanggal).
- **Dokumen proposal dan diagram** masih memuat `192.168.1.1` dan Raspberry Pi 4 di beberapa bagian. Perlu diselaraskan dengan kondisi sekarang (192.168.10.199 dan Raspberry Pi 3 Model B).
- **IP laptop dan ESP berubah antar sesi.** Laptop tercatat di `.236`, `.238`, `.243`, `.251`, `.253`. HTTP tercatat di `.242` dan `.233`. Kolom IP sumber di dataset dicatat per sesi, dan identitas selalu dicocokkan dengan MAC. Lease dynamic `.243` (Nitro-5) di subnet ESP terlihat di screenshot WinBox 31 Okt 2026.
- **Pesan `Data Masuk: {"test":1}` di server CoAP** berasal dari uji manual, bukan dari ESP#2.
- **Port mirror routed:** trafik ESP ke Pi dirutekan MikroTik. Dari uji Wireshark, paket ESP tetap terlihat di ether3, tetapi cakupannya hanya dianggap valid setelah pengecekan jumlah dan arah. Dikonfirmasi dari PCAP (9 Nov 2026): arah mirror **keduanya** (SYN dan SYN-ACK flow yang sama tertangkap), dan layer 2 PCAP hanya memuat MAC Pi dan MAC router.
- **Run 2 gagal** karena ESP#2 tidak mengirim (lease sempat hilang). Run 2b diulang setelah lease static dan ESP#2 terbukti mengirim.
- **Run 1 sempat tercampur log Zeek run 2b.** Sudah diperbaiki dengan Zeek ulang dari PCAP. Timestamp pertama `conn.log` run 1 sekarang 1793471318, sesuai `runs.csv`. **Diverifikasi (9 Nov 2026): 1793471318 = paket pertama PCAP run1 (1 Nov 2026, 01:28:38 WIB). Sama untuk run2b (1793481760 = 04:22:39) dan run3 (1793483176 = 04:46:15).**
- **Timestamp conn.log run 2b sudah dicek:** 1793481760 (sesuai waktu mulai di `runs.csv`). Run 3: 1793483176.
- **Ekstraksi fitur** menghitung 3 run S1 valid (run 1, run 2b, run 3). Run 2 tidak dipakai.
- **Baseline S1** dibuat dari `run_summary.csv` dan `traffic_features.csv` (`docs/BASELINE_S1.csv`).
- **Log anomali sempat tertukar** pada S6 run 2 dan run 3 (publish tercatat sebagai run 1). Sudah diperbaiki dengan pengelompokan berdasarkan waktu burst. Pilot dipisah ke `anomali_log_pilot.csv`.
- **Nama file S3 dan S4 sempat berbeda** (`S3_publish` dan `S4_subscribe`). Sudah disamakan menjadi `S3_pubreq` dan `S4_subpoll`, termasuk folder Zeek dan hash.
- **runs.csv S2 sampai S6 dilengkapi dari PCAP** dengan `lengkapi_runs.py`. Waktu mulai dan selesai diambil dari paket pertama dan terakhir di PCAP, sehingga bisa berselisih beberapa detik dari waktu tcpdump dimulai. `packets_received_by_filter` dan `packets_dropped_by_kernel` ditulis `tidak_tercatat` karena hanya terlihat di layar Pi saat run.
- **Baris HTTP pada S4 berlabel normal** berasal dari traffic normal ESP#3 yang tetap berjalan. HTTP tidak dijalankan sebagai skenario S4.
- **Baris S3 topic_resource_unik naik kecil** (1,01 ke 1,94) karena topik `sensor/anomali/suhu` ikut dipublish.
- **Normal S4 sedikit di atas nol** (0,11 per jendela) karena SUBSCRIBE awal dari ESP#1.
- **Dataset bersifat sintetis** dari generator di jaringan uji. Bukan data serangan nyata.
- **Fungsi pelabelan sempat gagal** karena huruf protokol berbeda (`mqtt` di log, `MQTT` di dataset). Sudah diperbaiki dengan membandingkan huruf besar.
- **Verifikasi silang PCAP vs log Zeek (9 Nov 2026):** MQTT CONNECT di PCAP S2 (1.191) = baris `mqtt_connect.log` Zeek (1.191); HTTP GET di PCAP S2 (1.193) = `http.log` (1.312 paket sesi, sesuai); POST S3 di PCAP (238–239) = `http.log` (238–239); SUBSCRIBE S4 di PCAP (120, dari 192.168.11.253) = `mqtt_subscribe.log` (120). Semua cocok.
- **Run3 S1 dimulai di tengah koneksi:** tidak ada SYN ke 1883 di PCAP run3 karena koneksi MQTT ESP#1 sudah terbentuk sebelum tcpdump mulai; conn.log run3 tetap menampilkan 1 flow utuh.
- **Misteri "Zeek: 1883 (2)" pada run1 TERPECAHKAN (10 Nov 2026): catatan benar.** conn.log run1 memuat 2 koneksi MQTT: koneksi pertama (port sumber 65082) dibuat **sebelum capture mulai** (paket pertamanya publish di 1793471320,6), lalu ESP#1 **reconnect di detik ke-434** (port sumber 53669, 1793471752,554) dan langsung SUBSCRIBE `control/node1/pump`. PCAP memuat 1 SYN — milik koneksi kedua; SYN koneksi pertama memang tidak terekam. Pola sama di run2b (reconnect detik 322, port 52958 → 61172). Run3 tanpa reconnect.
- **Distribusi waktu run (PCAP, 9 Nov 2026):** S1 run1–run3 pada 1 Nov 2026 (01:28, 04:22, 04:46 WIB); S2 run1 6 Nov 00:52, S3 02:35, S4 03:21, S5 04:05, S6 04:51 WIB — urutan run sesuai nomor skenario, jeda antar run ±45 menit.
- **Hash PCAP terverifikasi (10 Nov 2026):** 18 file `.sha256` (dihasilkan dari `/home/bayu/proyek/pcap/` — kemungkinan besar sisi WSL) dicocokkan dengan 18 PCAP yang dianalisis: **18/18 COCOK**. Hash run2b `46f2098d...` dan run3 `4e55b1df...` sama dengan yang tertulis di bagian 11. Perbandingan dengan hash sisi Pi masih perlu dilakukan (butuh `sha256sum` dari Pi).
- **Dataset divalidasi ulang (10 Nov 2026):** `traffic_dataset.csv` = 6.462 baris; label normal 5.632, anomali 830; anomali per skenario S2 108, S3 108, S4 72, S5 108, S6 434; S1 seluruhnya normal (0 baris salah) — **semua angka sesuai klaim bagian 7**. Jumlah anomali juga masuk akal secara geometri jendela: 12 jendela × 3 run × jumlah protokol (S3–S5: 108/72) dan 24 jendela × 2 fase × 3 run × 3 protokol ≈ 434 untuk S6.
- **`run_summary.csv` konsisten dengan PCAP (10 Nov 2026):** jumlah_request S2 CoAP 1.314 = 1.194 GET + 120 PUT; S2 HTTP 1.312 = 1.193 GET + 119 POST; S3 MQTT 240; S6 CoAP dan HTTP 2.746; S4 HTTP 119–120 (normal saja). Tidak ada kontradiksi dengan hitungan PCAP. Kolom `retransmisi_tcp` masih kosong — perlu diisi dari tshark (`tcp.analysis.retransmission`) bila dipakai di laporan.

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
- [x] Timestamp conn.log run 2b dicek (cocok dengan runs.csv)
- [x] Generator burst S2 diuji (pilot S2, 6 Nov 2026) dan burst terlihat di data
- [x] Run S2 sampai S6 (masing-masing 3 run, 15 run) dijalankan dan tercatat di runs.csv
- [x] Log anomali dibersihkan dan anomali_interval.csv dibuat
- [x] Skrip ekstraksi, pelabelan, dan validasi dijalankan pada data nyata
- [x] Validasi label: 6462 baris cocok, sampel tambahan 70 baris cocok
- [x] Dataset `data/traffic_dataset.csv` dan `data/README.md`
- [x] Validasi label dokumen (`docs/VALIDASI_LABEL.md`)
- [x] Arah mirror dicatat: **keduanya (ingress + egress)**, bukti SYN/SYN-ACK di PCAP (9 Nov 2026)
- [x] Interval keep-alive ESP#1 terukur: 15 detik (9 Nov 2026)
- [x] Frame 176 byte dijelaskan: tidak ada di 18 PCAP run, berasal dari capture lain (9 Nov 2026)
- [x] IP lama `.242`, `.251`, `.238` tidak muncul di 18 PCAP run (9 Nov 2026); `.238`/`.251`/`.242` juga tidak ada di lease WinBox 31 Okt; lease laptop `.243` (dynamic) teridentifikasi (10 Nov 2026)
- [x] Klaim "Zeek: 1883 (2)" run1 terkonfirmasi benar: ESP#1 reconnect di detik 434 (run2b: 322) — misteri selesai (10 Nov 2026)
- [x] Penyebab gap publish ESP#1 ditemukan: reconnect ESP#1 (10 Nov 2026)
- [x] Hash 18 PCAP di sisi arsip/WSL terverifikasi 18/18 terhadap file yang dianalisis (10 Nov 2026)
- [x] Dataset divalidasi ulang: 6.462 baris, distribusi label sesuai klaim bagian 7 (10 Nov 2026)

**Belum selesai:**
- [ ] Penjelasan 28.666 paket tanpa filter di Wireshark (port lain atau flood) — mulai dari filter `eth.dst == ff:ff:ff:ff:ff:ff` pada capture tersebut (hipotesis broadcast/multicast, belum dibuktikan)
- [ ] Lease waiting 192.168.11.254 dan 192.168.12.254 diperiksa dan dihapus jika tidak dipakai
- [ ] Status lease MAC/identitas 192.168.12.242, .251, dan .238 di MikroTik (dari PCAP sudah pasti tidak dipakai di run)
- [ ] DNS Pi: aktifkan Allow Remote Requests di MikroTik agar `apt install` bisa jalan
- [ ] Persetujuan tertulis Aslan untuk durasi, rate S3 sampai S5, dan pemetaan skenario (tanggal ____)
- [ ] Persetujuan tertulis Farel untuk generator dan parameter burst (tanggal ____)
- [ ] Keputusan dataset final (tiga protokol) disetujui dosen (tanggal ____)
- [ ] Hash dan timestamp Zeek S2 sampai S6 dicek satu per satu (lihat kolom catatan di runs.csv) — timestamp PCAP terverifikasi (9 Nov) dan hash sisi arsip/WSL 18/18 cocok (10 Nov); yang tersisa hanya membandingkan dengan output `sha256sum` dari sisi Pi
- [ ] Pemeriksa kedua di `docs/VALIDASI_LABEL.md` (nama dan tanggal)
- [ ] Dokumen wajib yang belum ada: `docs/PANDUAN_CAPTURE.md`, `docs/KEBIJAKAN_FILTER.md`, `docs/PANDUAN_LABEL.md`, dan notebook EDA `notebooks/analysis_report.ipynb`
- [ ] Dataset diserahkan ke teman untuk dashboard Streamlit

---

## 11. Ringkasan run

| Run | Skenario | Ulang | Status | Hash Pi = WSL | Captured | Received by filter | Dropped | MQTT / CoAP / HTTP (paket) | Catatan |
|---|---|---|---|---|---|---|---|---|---|
| S1_normal_run1 | S1_normal | 1 | Valid | Ya | 2193 | 2206 | 0 | 416 / 240 / 1537 | Waktu 01:28:34 sampai 01:39:27 (653 detik nyata). Zeek: 1883 (2), 5683 (1), 80 (119). **1883 (2) terkonfirmasi (10 Nov): ESP#1 reconnect di detik 434**; koneksi pertama dibuat sebelum capture mulai |
| S1_normal_run2 | S1_normal | 2 | GAGAL | - | 1951 | 1953 | 0 | 404 / 0 / 1547 | CoAP 0 paket. ESP#2 tidak mengirim. Tidak dipakai |
| S1_normal_run2b | S1_normal | 2 | Valid | Ya | 2189 | 2192 | 0 | 409 / 240 / 1540 | Waktu 04:22:32 sampai 04:32:47 (615 detik nyata). Hash `46f2098d...` (dicocokkan 10 Nov: cocok). ESP#1 reconnect di detik 322 |
| S1_normal_run3 | S1_normal | 3 | Valid | Ya | 2171 | 2171 | 0 | 400 / 240 / 1531 | Waktu 04:46:07 sampai 04:56:32 (625 detik nyata). Hash `4e55b1df...`. Capture mulai saat koneksi MQTT sudah terbentuk (tanpa SYN di PCAP) |
| S2_connburst_run1 | S2_connburst | 1 | Valid (masuk runs.csv) | ____ | 28421 | tidak_tercatat | tidak_tercatat | 12315 / 2628 / 13478 | Burst 20 aksi/detik, 60 detik, tunda 240. Dilengkapi dari PCAP; burst CONNECT terverifikasi pada detik 240–300 (9 Nov) |
| S2_connburst_run2 | S2_connburst | 2 | Valid (masuk runs.csv) | ____ | 28396 | tidak_tercatat | tidak_tercatat | 12316 / 2624 / 13456 | Sama seperti run 1. Dilengkapi dari PCAP; paket per protokol dari PCAP (9 Nov) |
| S2_connburst_run3 | S2_connburst | 3 | Valid (masuk runs.csv) | ____ | 28414 | tidak_tercatat | tidak_tercatat | 12316 / 2626 / 13472 | Sama seperti run 1. Dilengkapi dari PCAP; paket per protokol dari PCAP (9 Nov) |
| S3_pubreq_run1 | S3_pubreq | 1 | Valid (masuk runs.csv) | ____ | 4103 | tidak_tercatat | tidak_tercatat | 669 / 478 / 2956 | Publish 2 aksi/detik, 60 detik, tunda 240. Paket per protokol dari PCAP (9 Nov) |
| S3_pubreq_run2 | S3_pubreq | 2 | Valid (masuk runs.csv) | ____ | 4123 | tidak_tercatat | tidak_tercatat | 665 / 480 / 2978 | Sama seperti S3 run 1. Paket per protokol dari PCAP (9 Nov) |
| S3_pubreq_run3 | S3_pubreq | 3 | Valid (masuk runs.csv) | ____ | 4122 | tidak_tercatat | tidak_tercatat | 668 / 480 / 2974 | Sama seperti S3 run 1. Paket per protokol dari PCAP (9 Nov) |
| S4_subpoll_run1 | S4_subpoll | 1 | Valid (masuk runs.csv) | ____ | 2769 | tidak_tercatat | tidak_tercatat | 782 / 478 / 1509 (HTTP hanya normal ESP#3) | Subscribe 2 aksi/detik, 60 detik, tunda 240. HTTP tidak dijalankan. Paket per protokol dari PCAP (9 Nov) |
| S4_subpoll_run2 | S4_subpoll | 2 | Valid (masuk runs.csv) | ____ | 2794 | tidak_tercatat | tidak_tercatat | 782 / 466 / 1546 (HTTP hanya normal ESP#3) | Sama seperti S4 run 1. Paket per protokol dari PCAP (9 Nov) |
| S4_subpoll_run3 | S4_subpoll | 3 | Valid (masuk runs.csv) | ____ | 2802 | tidak_tercatat | tidak_tercatat | 786 / 480 / 1536 (HTTP hanya normal ESP#3) | Sama seperti S4 run 1. Paket per protokol dari PCAP (9 Nov) |
| S5_topic_run1 | S5_topic | 1 | Valid (masuk runs.csv) | ____ | 3853 | tidak_tercatat | tidak_tercatat | 663 / 478 / 2712 | Topic 2 aksi/detik, 60 detik, tunda 240. Dilengkapi dari PCAP; paket per protokol dari PCAP (9 Nov) |
| S5_topic_run2 | S5_topic | 2 | Valid (masuk runs.csv) | ____ | 3868 | tidak_tercatat | tidak_tercatat | 665 / 480 / 2723 | Sama seperti S5 run 1. Paket per protokol dari PCAP (9 Nov) |
| S5_topic_run3 | S5_topic | 3 | Valid (masuk runs.csv) | ____ | 3902 | tidak_tercatat | tidak_tercatat | 663 / 480 / 2759 | Sama seperti S5 run 1. Paket per protokol dari PCAP (9 Nov) |
| S6_campuran_run1 | S6_campuran | 1 | Valid (masuk runs.csv) | ____ | 58546 | tidak_tercatat | tidak_tercatat | 24781 / 5492 / 28273 | Burst 120 detik (120 sampai 240) lalu publish 120 detik (360 sampai 480). Per protokol; kedua fase terverifikasi di PCAP (9 Nov) |
| S6_campuran_run2 | S6_campuran | 2 | Valid (masuk runs.csv) | ____ | 58496 | tidak_tercatat | tidak_tercatat | 24785 / 5488 / 28223 | Sama seperti S6 run 1. Paket per protokol dari PCAP (9 Nov) |
| S6_campuran_run3 | S6_campuran | 3 | Valid (masuk runs.csv) | ____ | 58510 | tidak_tercatat | tidak_tercatat | 24755 / 5492 / 28263 | Sama seperti S6 run 1. Paket per protokol dari PCAP (9 Nov) |

**Status S1:** 3 run valid, baseline dibuat. Run 2 tetap disimpan sebagai catatan kegagalan.

**Status S2 sampai S6:** 15 run tercatat di runs.csv dan masuk dataset. Kolom jumlah paket per protokol untuk S2 sampai S6 sudah diisi dari analisis PCAP (9 Nov 2026); setiap baris jumlahnya sama dengan kolom Captured. Kolom hash Pi = WSL masih `____`: hash 18 PCAP di sisi arsip/WSL sudah terverifikasi 18/18 terhadap file yang dianalisis (10 Nov 2026), tinggal membandingkan dengan output `sha256sum` dari sisi Pi.
