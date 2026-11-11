# Dataset Traffic MQTT, CoAP, dan HTTP

## Ringkasan

- File: traffic_dataset.csv
- Jumlah baris: 6462
- Satu baris: satu jendela 5 detik, untuk satu run dan satu protokol.
- Run: S1 (3 run valid), S2 sampai S6 (masing-masing 3 run valid). Run gagal (S1_normal_run2) tidak masuk.
- Label: normal atau anomali.
- Dataset sintetis dari generator di jaringan uji. Bukan data serangan nyata.

## Skenario

| Kode | Keterangan | Protokol |
|---|---|---|
| S1_normal | Traffic normal ESP (baseline) | MQTT, CoAP, HTTP |
| S2_connburst | Burst koneksi 20 aksi/detik selama 60 detik | MQTT, CoAP, HTTP |
| S3_pubreq | Publish/request berulang 2 aksi/detik selama 60 detik | MQTT, CoAP, HTTP |
| S4_subpoll | Subscribe/observe 2 aksi/detik selama 60 detik | MQTT, CoAP (HTTP tidak dipakai) |
| S5_topic | Topik/endpoint/resource tidak wajar 2 aksi/detik selama 60 detik | MQTT, CoAP, HTTP |
| S6_campuran | Burst (120 detik) dan publish (120 detik) dalam satu run | MQTT, CoAP, HTTP |

Setiap run berdurasi nominal 600 detik.

## Kolom

| Kolom | Arti |
|---|---|
| run_id | Nama run, misalnya S2_connburst_run1 |
| skenario | Kode skenario (lihat tabel di atas) |
| label | normal atau anomali |
| protokol | MQTT, CoAP, atau HTTP (huruf besar) |
| jendela | Awal jendela 5 detik, dalam epoch detik (UTC) |
| packet_count | Jumlah paket dua arah dalam jendela |
| packet_rate | packet_count dibagi 5 (paket per detik) |
| byte_rate | Byte per detik dalam jendela |
| connection_count | Jumlah koneksi (TCP) atau flow (UDP) yang dimulai dalam jendela |
| connection_rate | connection_count dibagi 5 |
| durasi_sesi_rata | Rata-rata durasi koneksi (detik). Kosong untuk CoAP |
| frekuensi_request | Jumlah request per jendela dibagi 5. MQTT: publish. CoAP dan HTTP: semua metode |
| subscribe_observe | Jumlah SUBSCRIBE (MQTT) atau Observe (CoAP) per jendela. HTTP selalu 0 |
| topic_resource_unik | Jumlah topik, URI, atau path unik per jendela |
| interval_mean | Rata-rata selisih waktu antar request dalam jendela (detik) |
| interval_std | Simpangan baku selisih waktu antar request (detik) |

## Cara membaca label

Jendela berlabel `anomali` jika awalnya berada di dalam jadwal burst, publish, subscribe, atau topik untuk run dan protokol tersebut. Jadwal ada di `metadata/anomali_interval.csv` (tidak ikut di dataset ini).

Untuk S1, semua jendela `normal`.

## Hal yang perlu diketahui

- **Baris HTTP pada S4 berlabel normal.** Ini traffic normal dari ESP#3 yang tetap berjalan selama run. HTTP tidak dijalankan sebagai skenario S4.
- **SUBSCRIBE awal dari ESP#1.** Baseline MQTT memiliki sekitar 0,1 subscribe per jendela karena firmware ESP melakukan subscribe saat tersambung. Itu perilaku normal, bukan anomali.
- **CoAP tidak punya durasi sesi.** CoAP berbasis UDP, jadi `durasi_sesi_rata` kosong untuk CoAP.
- **`topic_resource_unik` untuk S3.** Naik sedikit karena topik `sensor/anomali/suhu` ikut dipublish.
- **Nilai frekuensi dan rate per jendela.** Dihitung per detik dengan membagi jumlah dengan 5.

## Cara membuat ulang

Skrip yang digunakan ada di folder `scripts/`:
1. `extract_features.py`: membaca PCAP dan log Zeek, menghasilkan `data/traffic_features.csv` dan `data/run_summary.csv`.
2. `label_dataset.py`: memberi label berdasarkan `metadata/anomali_interval.csv`, menghasilkan `data/traffic_dataset.csv`.
3. `validate_dataset.py`: memeriksa kolom dan label kosong.
4. `cek_label.py`: membandingkan label dengan jadwal.

## Pemeriksaan

- Validasi otomatis: LULUS
- Pemeriksaan label terhadap jadwal: 6462 baris cocok, 0 tidak cocok
- Lihat `docs/VALIDASI_LABEL.md` untuk detail
