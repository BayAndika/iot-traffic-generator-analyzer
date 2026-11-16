# Progress PBL: Mikrotik & Raspberry Pi

| | |
|---|---|
| **Nama** | Farel Tre Juandi |
| **Kelas** | TMJ 5A |
| **PIC PBL** | IoT Device Development, Protocol & Broker Configurator, Traffic Simulation & Testing |
| **Mata Kuliah** | Dokumentasi Jaringan |
| **Judul PBL** | Pengembangan IoT Traffic Generator Multi-Protokol MQTT, HTTP, CoAP untuk Pengujian Sistem Deteksi Anomali |

## 1. Mikrotik

### 1.1 Membuat IP DHCP Client dari ISP
![DHCP Client](assets/farel/02.png)

### 1.2 Menyalakan beberapa port dan menambahkan IP pada tabel IP
![IP Address](assets/farel/03.jpeg)

### 1.3 Membuat IP DHCP Server untuk client
![DHCP Server](assets/farel/04.png)

### 1.4 Tabel pengguna IP DHCP pada DHCP Lease
![DHCP Lease](assets/farel/05.png)

### 1.5 Membuat interface wireless wlan1
![Wlan1](assets/farel/06.png)

### 1.6 Konfigurasi SSID dan password pada Security Profiles (Wireless Table)
![Security Profiles](assets/farel/07.png)

### 1.7 Membuat NAT mode srcnat Masquerade
Agar client bisa mengakses internet. Konfigurasi berada pada tabel Firewall.

![NAT Masquerade](assets/farel/08.png)

### 1.8 Membuat Port Mirroring di port ether2 dan ether3
![Port Mirroring](assets/farel/09.png)

## 2. Raspberry Pi

### 2.1 Instalasi lewat Raspberry Pi Imager: pilih device
![Pilih device](assets/farel/10.png)

### 2.2 Memilih operating system
![Pilih OS](assets/farel/11.png)

### 2.3 Memilih storage device untuk instalasi
![Pilih storage](assets/farel/12.png)

### 2.4 Mengisi hostname
![Hostname](assets/farel/13.png)

### 2.5 Memilih lokasi, timezone, dan keyboard layout
![Localisation](assets/farel/14.png)

### 2.6 Membuat akun (username dan password)
![User](assets/farel/15.png)

### 2.7 Mengisi jaringan Wi-Fi (SSID dan password)
![Wi-Fi](assets/farel/16.png)

### 2.8 Menyalakan SSH
Opsi password dipilih agar Raspberry Pi bisa diremote.

![SSH](assets/farel/17.png)

### 2.9 Review sebelum proses write
Menampilkan ringkasan device, OS, storage, dan customisation sebelum instalasi.

![Review](assets/farel/18.png)

### 2.10 Tampilan setelah terinstall (remote via SSH)
![Remote SSH](assets/farel/19.jpeg)
