# Validasi Label Dataset

**Dataset:** data/traffic_dataset.csv
**Pemilik:** Bayu Andika Wibisono
**Pemeriksa kedua:** ____ (nama anggota yang memeriksa sampel)

## 1. Pemeriksaan otomatis

- Perintah: python3 scripts/validate_dataset.py data/traffic_dataset.csv
- Hasil: LULUS
- Tanggal: ____

## 2. Distribusi label

| Skenario | Normal | Anomali | Keterangan |
|---|---|---|---|
| S1_normal | 1079 | 0 | Semua normal (sesuai rancangan) |
| S2_connburst | 971 | 108 | 60 detik burst × 3 protokol × 3 run |
| S3_pubreq | 971 | 108 | Sama seperti S2 |
| S4_subpoll | 1000 | 72 | MQTT dan CoAP saja (HTTP tidak dipakai) |
| S5_topic | 969 | 108 | Sama seperti S2 |
| S6_campuran | 642 | 434 | Dua bagian 120 detik per run |

## 3. Pemeriksaan burst terlihat (MQTT, rata-rata per label)

### Parameter utama per skenario (MQTT, rata-rata per label)

| Skenario | Parameter utama | Normal | Anomali | Keterangan |
|---|---|---|---|---|
| S2_connburst | connection_rate | 0,194 | 18,106 | Terlihat |
| S3_pubreq | frekuensi_request | 0,222 | 2,000 | Terlihat |
| S4_subpoll | subscribe_observe | 0,111 | 9,000 | Terlihat |
| S5_topic | topic_resource_unik | 1,096 | 10,139 | Terlihat |
| S6_campuran | connection_rate dan frekuensi_request | 0,473 dan 0,229 | 9,172 dan 1,152 | Terlihat |

Catatan: S3 `topic_resource_unik` naik kecil (1,01 ke 1,94), karena topik `sensor/anomali/suhu` ditambahkan. Normal S4 sedikit di atas nol karena SUBSCRIBE awal dari ESP#1.

Isi dari perintah pengecekan burst. Nilai anomali harus lebih tinggi dari normal.

## 4. Pemeriksaan label terhadap jadwal

- Mode: semua baris (`python3 scripts/cek_label.py all`)
- Total diperiksa: 6462
- Cocok: 6462
- Tidak cocok: 0
- Tanggal pemeriksaan: 06 November 3036

Setiap baris dibandingkan dengan jadwal di metadata/anomali_interval.csv, dengan aturan: jendela dianggap anomali jika awal jendela berada di dalam [mulai, selesai) untuk run dan protokol yang sama.

Catatan: pemeriksaan awal dengan sampel acak 20 baris hanya menemukan dua baris anomali. Pemeriksaan seluruh baris dilakukan agar tidak bergantung pada sampel dan pembulatan tampilan.
- Pemeriksaan tambahan, sampel acak: 50 baris (seed 7), cocok 50, tidak cocok 0.
- Pemeriksaan tambahan, sampel anomali: 20 baris (seed 9), cocok 20, tidak cocok 0.

## 5. Kesimpulan

- Status: lulus
- Catatan keterbatasan:
  - CoAP tidak memiliki durasi sesi (UDP), sehingga kolom durasi_sesi_rata kosong untuk CoAP.
  - Dataset sintetis dari generator di jaringan uji. Bukan data serangan nyata.
  - Normal S4 sedikit di atas nol karena SUBSCRIBE awal dari ESP#1.
  - Baris HTTP S4 berlabel normal berasal dari traffic normal ESP#3, bukan burst.
  - Label mengikuti jadwal dari log generator (anomali_log.csv). Jadwal tersebut dianggap benar, dan keakuratannya bergantung pada waktu yang dicatat generator.
  - Ambang "terlihat" menggunakan rasio 2 kali baseline sesuai keputusan tim.

## 6. Tanda tangan

- Pemeriksa 1 : Bayu tanggal 06 November 2026
- Pemeriksa 2 (anggota lain): ____ tanggal ____
