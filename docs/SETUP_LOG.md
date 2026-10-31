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
| Versi Wireshark | ____ (Dumpcap 4.6.9 terlihat di metadata capture) | Help → About |
| Versi Npcap | ____ | Wireshark → Help → About → Folders |
| Versi Python | ____ (target 3.12) | `python --version` |
| Versi Git | ____ | `git --version` |
| Nama interface laptop ke port mirror | Ethernet (Realtek Gaming GbE, ether3) | Wireshark → Capture → Options |

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

**Catatan:**
- IP HTTP berubah dari `.242` (capture lama) menjadi `.233` (label MikroTik dan trafik port 80 saat ini).
- IP CoAP `.236` tercatat dari capture lama. Lease-nya `waiting`, sehingga ESP#2 belum tersambung ke jaringan.
- Kolom `LAST-SEEN` di MikroTik tidak dipakai sebagai indikator aktivitas. Yang dipakai adalah status lease dan trafik di Pi.

---

## 4. Layanan di Raspberry Pi

| Layanan | Port | Status | Proses | Keterangan |
|---|---|---|---|---|
| Mosquitto (MQTT) | TCP 1883 | Aktif | PID 1301 (systemd) | `listener 0.0.0.0:1883`, `allow_anonymous true` (hanya jaringan uji) |
| Server CoAP | UDP 5683 dan TCP 5683 | Aktif (manual) | PID 2911, `python server.py` | Listener TCP 5683 kemungkinan bawaan library. Satu instance saja. Sempat restart (PID sebelumnya 2703). Belum di tmux atau systemd |
| Server HTTP | TCP 80 | Aktif (manual) | PID 1803, `http_server.py` (python) | Listen 0.0.0.0:80. Proses terkait: PID 1797 dan 1802 (sudo wrapper). Belum di tmux atau systemd |

**Status respons saat uji:**
- CoAP PUT `/motion`: awalnya 4.05 Method Not Allowed, lalu 2.04 Changed setelah perbaikan server. Uji manual ke `coap://127.0.0.1/motion` menghasilkan kode respons `44` (2.04 Changed), payload `OK`.
- HTTP POST `/api/sensor/http`: awalnya 404. Status sekarang ____. Harus 200 sebelum run tiga protokol.

**Catatan operasional:**
- Server dijalankan manual. Jika sesi SSH ditutup, proses bisa ikut mati. Sebelum run resmi, pastikan prosesnya masih hidup dengan `pgrep -af server.py` dan `sudo ss -tulnp | grep -E ':80 |5683'`.
- `localhost` di-resolve ke IPv6 (`::1`) sedangkan server aktif di IPv4. Uji lokal memakai `127.0.0.1`.

- 1 Nov 2026 (server dipindah ke tmux): Mosquitto PID 1301 (TCP 1883). Server CoAP PID 4538 di tmux sesi `coap` (UDP dan TCP 5683). Server HTTP PID 4585 di tmux sesi `http` (TCP 80). PID lama 2911 dan 1803 sudah dihentikan.
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
- Setiap run diberi nomor ulang. Run yang gagal tidak ditimpa.
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
| 29 Okt 2026 | Respons CoAP 2.04 dari uji lokal (`aiocoap-client` ke `127.0.0.1`) | Kode `44` (2.04 Changed), payload `OK`, dibaca dari `tcpdump -i lo -X` |
| 29 Okt 2026 | Pilot ESP#1 (192.168.12.234), 120 detik, filter `tcp port 1883` | conn.log: 1 koneksi persisten 115 detik. mqtt_publish.log: 24 publish |
| 29 Okt 2026 | Verifikasi port mirror dengan trafik ESP (`ip.addr == 192.168.12.234 && tcp.port == 1883`) | Publish dan keep-alive ESP terlihat di laptop |
| 29 Okt 2026 | Hitung UDP 5683 dari 192.168.12.236, 60 detik (dua arah, `wc -l`) | Hasil 1. Tidak valid karena menghitung balasan server. Tidak dijadikan bukti |
| 29 Okt 2026 | Hitung UDP 5683 dari 192.168.12.236, 120 detik (`src host`, `-tt`) | Tidak ada paket. ESP#2 tidak mengirim dari IP ini |
| 29 Okt 2026 | Lease ESP#2 (`E0:8C:FE:5C:75:..`) di MikroTik | `waiting`. Tidak tersambung jaringan saat tes |
| 29 Okt 2026 | Pengecekan duplikasi mirror (60 detik) | Lulus. Laju 0,63 vs 0,69 paket/detik. Detail di bagian 5 |
| 29 Okt 2026 | Cek layanan Pi sebelum S1 | Mosquitto PID 1301, HTTP PID 1803, CoAP PID 2911 |
| ____ | Ping laptop ke Pi, ICMP di Wireshark | Tidak dijadikan bukti (lihat bagian 5) |

| 1 Nov 2026 | Pilot tiga protokol 120 detik, filter `tcp port 1883 or udp port 5683 or tcp port 80` | tcpdump: 430 captured, 440 received by filter, 0 dropped. Per protokol: MQTT 80, CoAP 48, HTTP 302 paket. Zeek conn.log: 1883 (1 koneksi), 5683 (1 flow), 80 (24 koneksi). Lulus |

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
- **IP laptop dan ESP berubah antar sesi.** Laptop tercatat di `.236`, `.238`, `.251`, `.253`. HTTP tercatat di `.242` dan `.233`. Kolom IP sumber di dataset dicatat per sesi, dan identitas selalu dicocokkan dengan MAC.
- **Pesan `Data Masuk: {"test":1}` di server CoAP** berasal dari uji manual, bukan dari ESP#2.
- **Port mirror routed:** trafik ESP ke Pi dirutekan MikroTik. Dari uji Wireshark, paket ESP tetap terlihat di ether3, tetapi cakupannya hanya dianggap valid setelah pengecekan jumlah dan arah.

---

## 10. Yang belum dikerjakan

- [x] Pengecekan duplikasi mirror (lulus, 29 Okt 2026)
- [x] Ruang disk Pi dicek (Avail 104G)
- [x] Server CoAP aktif dan satu instance saja (PID 2911)
- [x] Server HTTP mendengarkan port 80 (PID 1803)
- [x] Mosquitto aktif (PID 1301)
- [x] Respons HTTP 200 terverifikasi (curl, 29 Okt 2026)
- [x] ESP#3 mengirim HTTP dengan respons 200
- [x] ESP#2 mengirim CoAP dan data sensor diterima server (bukan hanya uji manual)
- [x] Lease ESP#1, ESP#2, dan ESP#3 static (dynamic=no, 29 Okt 2026)
- [ ] Lease waiting 192.168.11.254 dan 192.168.12.254 (host ragoon-broker) diperiksa dan dihapus jika tidak dipakai
- [ ] Arah mirror dicatat (ingress / egress / keduanya)
- [ ] Penjelasan 28.666 paket tanpa filter di Wireshark (port lain atau flood)
- [ ] Server CoAP dan HTTP dijalankan di tmux atau systemd
- [ ] Respons HTTP 200 terverifikasi (`curl -i -X POST`)
- [ ] ESP#2 (`E0:8C:FE:5C:75:..`) lease `bound`, dan mengirim CoAP dengan isi selain `{"test":1}`
- [ ] ESP#3 (`E0:8C:FE:5C:95:..`, IP `.233`) mengirim HTTP dengan respons 200
- [ ] MAC dan identitas 192.168.12.242, .251, dan .238 dikonfirmasi, atau dicatat sebagai tidak dipakai
- [ ] Lease ESP#1, ESP#2, dan ESP#3 diubah menjadi static di MikroTik
- [ ] Durasi S1 sampai S6 disepakati dengan Aslan
- [ ] Ambang kriteria anomali disepakati dengan Aslan
- [ ] Pemetaan S1 sampai S6 disetujui Aslan dan dosen
- [ ] Keputusan dataset final (tiga protokol atau fallback MQTT) disetujui dosen
- [ ] Penjelasan frame 176 byte di capture
- [x] Pilot tiga protokol 2 menit lulus (1 Nov 2026)
- [ ] Run S1 resmi (3 kali)
- [ ] Skrip ekstraksi, pelabelan, dan validasi dijalankan pada data nyata
- [ ] Dataset dan validasi 20 persen sampel
- [ ] Dokumen wajib (PANDUAN_CAPTURE, KEBIJAKAN_FILTER, PANDUAN_LABEL, VALIDASI_LABEL, README dataset, notebook EDA)