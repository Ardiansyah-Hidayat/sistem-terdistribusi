# Klaster Penyimpanan Terdistribusi (Distributed File Storage System)

Proyek sistem penyimpanan berkas terdistribusi menggunakan arsitektur **Master-Worker (Coordinator-Worker)** dengan dukungan replikasi otomatis 2x (*Replication Factor = 2*) dan pengalihan unduhan otomatis (*Failover Retrieval*).

Repositori ini mendukung **2 cara menjalankan**:
1. **Mode Lokal (Cepat & Ringan)**: Menjalankan koordinator dan 3 node worker langsung sebagai proses lokal di komputer tanpa perlu VirtualBox atau software tambahan. Cocok untuk pengujian cepat, evaluasi kode, atau menulis paper.
2. **Mode Virtual Machine (Lengkap / Sesuai Paper)**: Menjalankan 3 storage node di dalam 3 VM Ubuntu Server terpisah di VirtualBox via Host-Only Network.

---

## 🌟 Fitur Utama

- **Faktor Replikasi ($N = 2$)**: Setiap berkas diduplikasi ke 2 storage node berbeda secara otomatis.
- **Failover Unduhan**: Jika node penyimpan pertama mati, unduhan dialihkan transparan ke node replika kedua.
- **Simulasi Kegagalan Node**: Administrator (atau Tamu dengan mode eksperimen aktif) dapat mematikan/menyalakan node worker secara real-time langsung melalui dashboard web.
- **Role-Based Access Control (RBAC)**:
  - **Administrator** (`ardi` / `ardi123`): Akses penuh, saklar blokir tamu, dan saklar otoritas eksperimen tamu.
  - **Tamu (Guest)**: Masuk 1-klik tanpa password untuk melihat, mengunggah, dan mengunduh berkas.
- **Dashboard Web Operasional**: Tampilan ringkas, responsif, dengan telemetri kesehatan klaster.

---

## 🚀 Panduan Mode Lokal

Mode ini tidak memerlukan VirtualBox, ISO Ubuntu, atau Ngrok. Koordinator dan seluruh storage node berjalan sebagai proses lokal mandiri.

### 1. Prasyarat
- Python 3.10 atau versi lebih baru.

### 2. Instalasi
Clone repositori dan pasang dependensi:
```bash
git clone https://github.com/Ardiansyah-Hidayat/sistem-terdistribusi.git
cd sistem-terdistribusi
pip install -r requirements.txt
```

### 3. Menjalankan Klaster
Cukup klik ganda file:
```cmd
START_LOCAL.bat
```
*(Atau via terminal: `python run_system.py`)*

Script ini akan otomatis menyalakan:
- **Master Coordinator**: `http://localhost:8000`
- **Storage Node 1**: `http://127.0.0.1:8001`
- **Storage Node 2**: `http://127.0.0.1:8002`
- **Storage Node 3**: `http://127.0.0.1:8003`

### 4. Membuka Dashboard
Buka browser dan kunjungi: **`http://localhost:8000`**
- **Admin**: `ardi` / `ardi123`
- **Tamu**: Klik *"Masuk sebagai tamu"*

### 5. Menghentikan
Tekan `Ctrl + C` di jendela terminal `run_system.py`.

---

## 🖥️ Panduan Detail (Virtual Machine)

Panduan setup lengkap untuk mereplikasi lingkungan komputasi terdistribusi menggunakan 3 Virtual Machine Ubuntu Server terpisah di VirtualBox.

### 1. Prasyarat Tambahan
- **Oracle VirtualBox 7.x** terpasang di komputer host.
- **ISO Ubuntu Server 24.04 LTS** (dapat diunduh dari situs resmi Ubuntu).

### 2. Konfigurasi Jaringan VirtualBox (Host-Only)
1. Buka VirtualBox $\rightarrow$ **Tools** $\rightarrow$ **Network Manager**.
2. Pastikan terdapat adapter **Host-Only Ethernet Adapter** dengan konfigurasi:
   - IPv4 Address: `192.168.56.1`
   - IPv4 Network Mask: `255.255.255.0`
   - DHCP Server: Aktif (rentang IP `192.168.56.101` s.d. `192.168.56.254`).

### 3. Pembuatan 3 Virtual Machine (VM)
Buat 3 buah VM Ubuntu Server dengan spesifikasi minimal per VM:
- RAM: 1024 MB (1 GB)
- Storage: 10 GB
- Network: Adapter 1 diset ke **Host-Only Adapter** (arahkan ke adapter `192.168.56.1`).

Beri nama VM persis seperti berikut:
1. `storage-node-1` $\rightarrow$ IP target: `192.168.56.102`
2. `storage-node-2` $\rightarrow$ IP target: `192.168.56.103`
3. `storage-node-3` $\rightarrow$ IP target: `192.168.56.104`

> **Catatan Kredensial VM:**
> Saat proses instalasi Ubuntu Server di masing-masing VM, gunakan:
> - **Username**: `vboxuser`
> - **Password**: `12345`
> - Pastikan opsi **Install OpenSSH Server** dicentang saat instalasi agar koordinator dapat mengontrol node via SSH.

### 4. Konfigurasi Service di Dalam VM
Di setiap VM, pastikan Python dan dependensi uvicorn terpasang:
```bash
sudo apt update && sudo apt install -y python3 python3-pip
pip install fastapi uvicorn httpx python-multipart --break-system-packages
```

### 5. Menjalankan Klaster VM
Setelah ketiga VM siap dan terdeteksi di VirtualBox:
1. Pastikan script tahu mode VM dengan menjalankan:
   ```cmd
   START_ALL.bat
   ```
   *Script ini akan otomatis menyalakan ketiga VM secara headless di latar belakang, mendeploy service storage node via SSH ke port masing-masing (8001, 8002, 8003), lalu menyalakan Web Console Coordinator di port 8000.*
2. Buka dashboard di `http://localhost:8000`.

### 6. Mematikan Klaster VM
Untuk mematikan seluruh proses dan menyimpan state VM (*free 100% RAM*):
```cmd
STOP_ALL.bat
```
*(Script ini mematikan service node via SSH dan menjalankan `VBoxManage controlvm savestate` ke ketiga VM).*

---

## 🌐 Akses Publik Internet (Opsional - Menggunakan Ngrok)

Jika Anda ingin mendemonstrasikan dashboard kepada dosen/teman di luar jaringan Wi-Fi lokal:
1. Pasang `ngrok.exe` dan daftarkan authtoken gratis Anda di [ngrok.com](https://ngrok.com).
2. Jalankan:
   ```cmd
   start_ngrok.bat
   ```
3. Link publik HTTPS yang dihasilkan dapat langsung diakses dari browser HP atau laptop di mana saja.

---

## 📁 Struktur Direktori

```text
├── coordinator/           # Logika Master Coordinator
│   ├── auth_manager.py    # Manajemen otentikasi sesi & hak akses
│   ├── main.py            # Endpoint API FastAPI koordinator
│   ├── metadata_mgr.py    # Katalog metadata berkas
│   ├── node_tracker.py    # Pelacak status, heartbeat & simulasi failure
│   └── static/
│       └── index.html     # Dashboard web frontend
├── node/                  # Logika Worker Storage Node
│   ├── main.py            # API penyimpanan berkas worker per node
│   └── storage_service.py # Operasi I/O berkas ke disk
├── config.py              # Konfigurasi mode (local vs vm), IP, dan port
├── deploy_vm_nodes.py     # Script deploy otomatis ke VirtualBox VM via SSH
├── run_system.py          # Peluncur koordinator & node lokal
├── START_LOCAL.bat        # Peluncur 1-klik mode lokal (tanpa VM)
├── START_ALL.bat          # Peluncur 1-klik mode VirtualBox VM
├── STOP_ALL.bat           # Pemati sistem 1-klik & pelepasan RAM VM
└── requirements.txt       # Daftar dependensi pustaka Python
```
