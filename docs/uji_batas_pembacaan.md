# Uji Batas Pembacaan

**Pemilik:** Bayu Andika Wibisono (Network Capture & Dataset Engineer)
**Permintaan:** dosen pembimbing (Ayu Rosyida Zain S.ST., M.T.)
**Status dokumen:** Bagian 1 selesai secara teknis. Keputusan ambang menunggu persetujuan Aslan. Bagian 2 sampai 4 belum dikerjakan.

---

## Bagian 1: Titik kritis dan ambang

### 1.1 Metode

- Data: `data/traffic_dataset.csv` (6462 jendela 5 detik, 3 protokol, skenario S1 sampai S6).
- Evaluasi per skenario sasaran. Parameter dinilai hanya pada skenario yang memang menguji parameter tersebut:
  - `connection_rate` untuk S2 (burst koneksi)
  - `frekuensi_request` untuk S3 (publish berulang)
  - `subscribe_observe` untuk S4 (subscribe dan observe)
  - `topic_resource_unik` untuk S5 (topik tidak wajar)
- Positif: jendela anomali skenario sasaran. Negatif: jendela normal skenario sasaran dan jendela normal S1.
- Ambang: k kali baseline, dengan k dari 1,00 sampai 20.
- Baseline dihitung dengan **leave-one-out** pada tiga run S1 (`S1_normal_run1`, `S1_normal_run2b`, `S1_normal_run3`). Setiap run dinilai menggunakan baseline dari dua run lainnya.
- Rentang k "baik": Youden (TPR − FPR) dalam 0,01 dari maksimum lipatan itu.
- Skrip: `scripts/titik_kritis_loo.py`. Keluaran: `docs/titik_kritis_loo.csv` dan `docs/titik_kritis_loo.txt`.

### 1.2 Hasil

Rentang k baik sama di ketiga lipatan untuk setiap kombinasi di bawah ini.

| Parameter | Protokol | Rentang k baik | 2× masuk di ketiga lipatan? | Keputusan ambang |
|---|---|---|---|---|
| connection_rate | MQTT | 1,00 sampai 20 | Ya | Ada atau tidak ada koneksi baru (lihat 1.3) |
| connection_rate | CoAP | 1,00 sampai 20 | Ya | Ada atau tidak ada koneksi baru (lihat 1.3) |
| connection_rate | HTTP | 1,05 sampai 20 | Ya | 2× |
| frekuensi_request | MQTT | 1,05 sampai 2,00 | Ya (di batas atas) | 2×, dicatat sebagai batas |
| frekuensi_request | CoAP | 1,00 sampai 3,75 | Ya | 2× |
| frekuensi_request | HTTP | 1,05 sampai 4,00 | Ya | 2× |
| topic_resource_unik | MQTT | 1,00 sampai 2,75 | Ya | 2× |
| topic_resource_unik | CoAP | 1,00 sampai 1,75 | **Tidak** | 1,5 |
| topic_resource_unik | HTTP | 1,00 sampai 3,75 | Ya | 2× |
| subscribe_observe | MQTT | 1,00 sampai 20 | Tidak relevan | Ada atau tidak ada SUBSCRIBE |
| subscribe_observe | CoAP | 1,00 sampai 20 | Tidak relevan | Ada atau tidak ada observe |
| interval_std | semua | tidak diuji | - | Dikeluarkan dari evaluasi |

### 1.3 Penjelasan keputusan

- **2× stabil untuk `frekuensi_request` ketiga protokol dan `topic_resource_unik` MQTT dan HTTP.** Untuk `frekuensi_request` MQTT, batas atas rentang tepat 2,00. Normal bisa mencapai 2 publish per jendela (0,4 per detik), yaitu dua kali baseline 0,2. Jadi ambang ini berada di tepi perilaku normal, bukan di tengah.
- **2× tidak cocok untuk `topic_resource_unik` CoAP.** Rentang baiknya hanya 1,00 sampai 1,75 di ketiga lipatan. Diambil 1,5 sebagai nilai yang berada di dalam rentang.
- **`connection_rate` MQTT dan CoAP tidak memakai ambang relatif.** Baseline normal sekitar 0,0017 sampai 0,0033 per detik (sekitar satu koneksi dalam seluruh run). Ambang `k × baseline` hampir nol, sehingga rentang "1 sampai 20" hanya berarti batas atas tidak pernah tercapai. Keputusan: sebuah jendela dinyatakan anomali jika ada koneksi baru di dalamnya.
- **`subscribe_observe` tidak memakai ambang relatif.** Baseline MQTT sekitar 0,004 sampai 0,008, dan CoAP 0. Keputusan: ada atau tidak ada SUBSCRIBE (MQTT) atau observe (CoAP).
- **`interval_std` dikeluarkan.** TPR bernilai nol di semua k untuk semua protokol, sehingga parameter ini tidak membedakan normal dan anomali pada data ini.

### 1.4 Batasan

- Skenario sasaran hanya tiga run per protokol, jadi estimasi FPR kasar.
- Baseline hanya dari tiga run S1. Uji leave-one-out menunjukkan stabilitas terhadap pemilihan baseline, tetapi bukan validasi terhadap data baru.
- Jendela anomali dan normal yang dinilai berasal dari dataset yang sama dengan yang dipakai memilih k. Hasilnya bisa optimistis.
- Kriteria "baik" (Youden dalam 0,01 dari maksimum) adalah pilihan tim.
- Keputusan ambang di atas **belum disetujui secara tertulis** oleh Aslan. Persetujuan: ____ (tanggal ____).

## Bagian 2: Burst bertahap (belum dikerjakan)

Menunggu persetujuan kriteria terbaca (TPR ≥ 80%), batas (20% sampai 80%), dan luput (TPR ≤ 20%) oleh dosen dan Aslan.

## Bagian 3: Potensi error E1 sampai E4 (belum dikerjakan)

| Uji | Hasil | Status (berhasil / gagal) | Catatan |
|---|---|---|---|
| E1 ESP mati 60 detik | | | |
| E2 broker restart | | | |
| E3 packet loss 2% | | | |
| E4 kapasitas tcpdump | | | |

## Bagian 4: Kesimpulan

Belum ditulis. Diisi setelah Bagian 2 dan 3 selesai.