# Klaster Penyimpanan Terdistribusi (Distributed File Storage System)

Proyek sistem penyimpanan berkas terdistribusi menggunakan arsitektur **Master-Worker (Coordinator-Worker)** dengan dukungan replikasi otomatis dan failover unduhan.

---

## 🌟 Fitur Utama

- **Replication Factor (2x)**: Setiap berkas yang diunggah secara otomatis diduplikasi ke minimal 2 storage node berbeda.
- **Failover Download**: Jika salah satu storage node tempat berkas disimpan mati, sistem secara transparan mengalihkan permintaan unduhan ke node replika yang masih aktif.
- **Simulasi Kegagalan Node (Node Failure Simulation)**: Administrator (atau Guest dengan mode eksperimen aktif) dapat mematikan/menyalakan node worker secara real-time langsung melalui dashboard web untuk mendemonstrasikan keandalan sistem.
- **Kontrol Akses Bertingkat (Role-Based Access Control)**:
  - **Administrator** (`ardi` / `ardi123`): Kontrol penuh atas seluruh klaster, saklar izin tamu, mode eksperimen, dan hapus berkas.
  - **Guest**: Masuk 1-klik tanpa kata sandi untuk melihat, mengunggah, dan mengunduh berkas.
- **Konsol Manajemen Web Modern**: Antarmuka bersih, responsif, dan bebas elemen visual berlebihan (*clean operational console*).

---

## 🏗️ Arsitektur

- **Coordinator (Master)**: Menjalankan FastAPI di `http://localhost:8000`. Mengelola metadata berkas, pelacakan kesehatan node (*heartbeat loop*), penentuan replika, dan otentikasi.
- **Storage Nodes (Workers)**: 3 node penyimpanan worker (dapat dijalankan di VM Ubuntu atau lokal):
  - Node 1: Port `8001`
  - Node 2: Port `8002`
  - Node 3: Port `8003`

---

## 🚀 Panduan Menjalankan

### 1. Prasyarat & Instalasi Dependensi
Pastikan Python 3.10+ telah terinstal, lalu jalankan:
```bash
pip install -r requirements.txt
```

### 2. Menjalankan Sistem

Sistem mendukung 2 mode:

#### ⚡ Mode A: Mode Lokal (Tanpa VirtualBox / Tanpa Ngrok) - **Direkomendasikan untuk Teman/Pengguna Baru**
Tidak perlu install VirtualBox atau download ISO Ubuntu. Cukup klik ganda:
```cmd
START_LOCAL.bat
```
*(atau jalankan perintah `python run_system.py`)*.  
Perintah ini akan secara otomatis menyalakan Koordinator (Port 8000) dan ketiga Storage Node (Port 8001, 8002, 8003) sebagai proses lokal. Fitur replikasi 2x dan simulasi failover berjalan penuh 100%!

#### 🖥️ Mode B: Mode Virtual Machine (3 VM Ubuntu Server)
Jika Anda memiliki VirtualBox dengan 3 VM Ubuntu Server terkonfigurasi:
```cmd
START_ALL.bat
```

- **Membuka Dashboard**:
  Buka browser dan akses:
  [http://localhost:8000](http://localhost:8000)

- **Akun Masuk**:
  - **Admin**: Username: `ardi` | Password: `ardi123`
  - **Tamu**: Klik tombol *"Masuk sebagai tamu"*

### 3. Mematikan Sistem
Untuk mematikan semua proses dan melepaskan sumber daya:
- Jika di Mode Lokal: Cukup tekan `Ctrl + C` di jendela terminal `run_system.py`.
- Jika di Mode VM: Klik ganda `STOP_ALL.bat` *(atau jalankan `python stop_all.py`)*.

---

## 📁 Struktur Direktori

```text
├── coordinator/           # Logika Master Coordinator
│   ├── auth_manager.py    # Manajemen otentikasi sesi & hak akses
│   ├── main.py            # Endpoint API FastAPI koordinator
│   ├── metadata_mgr.py    # Katalog metadata berkas
│   ├── node_tracker.py    # Pelacak status dan heartbeat node
│   └── static/
│       └── index.html     # Dashboard web frontend
├── node/                  # Logika Worker Storage Node
│   └── main.py            # API penyimpan berkas per node
├── config.py              # Konfigurasi IP, port, dan cluster
├── deploy_vm_nodes.py     # Script deploy otomatis ke VirtualBox VM via SSH
├── run_system.py          # Peluncur koordinator & node lokal
├── START_ALL.bat          # Script peluncur 1-klik
├── STOP_ALL.bat           # Script pemati sistem 1-klik
└── requirements.txt       # Daftar dependensi Python
```
