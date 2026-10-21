import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

os.makedirs("diagrams", exist_ok=True)

# ----------------- DIAGRAM 1: Cluster Architecture -----------------
fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
ax.set_xlim(0, 10)
ax.set_ylim(0, 7)
ax.axis('off')

# Client Box
ax.add_patch(patches.FancyBboxPatch((0.5, 4.8), 2.2, 1.4, boxstyle="round,pad=0.1", fc="#EFF6FF", ec="#2563EB", lw=2))
ax.text(1.6, 5.7, "Client / Pengguna", ha="center", va="center", fontsize=11, fontweight="bold", color="#1E293B")
ax.text(1.6, 5.2, "Web Browser Console\n(HTTP / REST Client)", ha="center", va="center", fontsize=9, color="#475569")

# Coordinator Box (Master)
ax.add_patch(patches.FancyBboxPatch((3.8, 3.8), 2.6, 2.7, boxstyle="round,pad=0.12", fc="#1E293B", ec="#0F172A", lw=2.5))
ax.text(5.1, 6.1, "MASTER COORDINATOR", ha="center", va="center", fontsize=11, fontweight="bold", color="#FFFFFF")
ax.text(5.1, 5.6, "Port: 8000 (FastAPI)", ha="center", va="center", fontsize=9.5, color="#93C5FD")
ax.text(5.1, 4.9, "• Metadata Catalog (JSON)\n• Least-Loaded Selector\n• Heartbeat Monitor (3s)\n• RBAC Auth & Session\n• Failover Router", 
        ha="center", va="center", fontsize=8.5, color="#E2E8F0")

# Storage Node 1
ax.add_patch(patches.FancyBboxPatch((7.5, 4.9), 2.1, 1.4, boxstyle="round,pad=0.1", fc="#F0FDF4", ec="#16A34A", lw=2))
ax.text(8.55, 5.85, "STORAGE NODE 1", ha="center", va="center", fontsize=10, fontweight="bold", color="#14532D")
ax.text(8.55, 5.4, "Port 8001 | VM / Local", ha="center", va="center", fontsize=8.5, color="#15803D")
ax.text(8.55, 5.05, "IP: 192.168.56.102", ha="center", va="center", fontsize=8, color="#475569")

# Storage Node 2
ax.add_patch(patches.FancyBboxPatch((7.5, 2.8), 2.1, 1.4, boxstyle="round,pad=0.1", fc="#F0FDF4", ec="#16A34A", lw=2))
ax.text(8.55, 3.75, "STORAGE NODE 2", ha="center", va="center", fontsize=10, fontweight="bold", color="#14532D")
ax.text(8.55, 3.3, "Port 8002 | VM / Local", ha="center", va="center", fontsize=8.5, color="#15803D")
ax.text(8.55, 2.95, "IP: 192.168.56.103", ha="center", va="center", fontsize=8, color="#475569")

# Storage Node 3
ax.add_patch(patches.FancyBboxPatch((7.5, 0.7), 2.1, 1.4, boxstyle="round,pad=0.1", fc="#F0FDF4", ec="#16A34A", lw=2))
ax.text(8.55, 1.65, "STORAGE NODE 3", ha="center", va="center", fontsize=10, fontweight="bold", color="#14532D")
ax.text(8.55, 1.2, "Port 8003 | VM / Local", ha="center", va="center", fontsize=8.5, color="#15803D")
ax.text(8.55, 0.85, "IP: 192.168.56.104", ha="center", va="center", fontsize=8, color="#475569")

# Arrows Client <-> Coordinator
ax.annotate("", xy=(3.8, 5.5), xytext=(2.7, 5.5), arrowprops=dict(arrowstyle="<->", color="#2563EB", lw=2))
ax.text(3.25, 5.75, "Upload / Download\nREST API (JSON)", ha="center", va="bottom", fontsize=8, color="#1E293B")

# Arrows Coordinator <-> Storage Nodes
# To Node 1
ax.annotate("", xy=(7.5, 5.6), xytext=(6.4, 5.4), arrowprops=dict(arrowstyle="<->", color="#16A34A", lw=1.8))
# To Node 2
ax.annotate("", xy=(7.5, 3.5), xytext=(6.4, 4.8), arrowprops=dict(arrowstyle="<->", color="#16A34A", lw=1.8))
# To Node 3
ax.annotate("", xy=(7.5, 1.4), xytext=(6.4, 4.2), arrowprops=dict(arrowstyle="<->", color="#16A34A", lw=1.8))

ax.text(6.85, 4.3, "Replication & Retrieval\nHeartbeat (/health)", ha="center", va="center", fontsize=8, color="#475569", rotation=-15)

# Subtitle / Caption
plt.title("Gambar 1: Arsitektur Sistem Penyimpanan Terdistribusi (Master-Worker Architecture)", 
          fontsize=12, fontweight="bold", color="#0F172A", pad=15)
plt.tight_layout()
plt.savefig("diagrams/arsitektur_sistem.png", bbox_inches='tight')
plt.close()
print("[OK] Created diagrams/arsitektur_sistem.png")


# ----------------- DIAGRAM 2: Replication & Failover Workflow -----------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.5), dpi=300)

for ax in (ax1, ax2):
    ax.set_xlim(0, 6)
    ax.set_ylim(0, 7)
    ax.axis('off')

# === Subplot 1: Upload & 2x Replication ===
ax1.set_title("A. Alur Replikasi Berkas (Upload)", fontsize=11, fontweight="bold", color="#0F172A", pad=10)

ax1.add_patch(patches.FancyBboxPatch((1.8, 5.8), 2.4, 0.8, boxstyle="round,pad=0.08", fc="#EFF6FF", ec="#2563EB", lw=1.5))
ax1.text(3.0, 6.2, "1. Klien Unggah Berkas\n(POST /api/upload)", ha="center", va="center", fontsize=8.5, fontweight="bold", color="#1E293B")

ax1.annotate("", xy=(3.0, 4.8), xytext=(3.0, 5.8), arrowprops=dict(arrowstyle="->", color="#2563EB", lw=1.5))

ax1.add_patch(patches.FancyBboxPatch((1.5, 3.9), 3.0, 0.9, boxstyle="round,pad=0.08", fc="#1E293B", ec="#0F172A", lw=1.5))
ax1.text(3.0, 4.35, "2. Koordinator Seleksi Node\n(Pilih 2 Node Beban Terendah)", ha="center", va="center", fontsize=8.5, fontweight="bold", color="#FFFFFF")

ax1.annotate("", xy=(1.5, 2.7), xytext=(2.4, 3.9), arrowprops=dict(arrowstyle="->", color="#16A34A", lw=1.5))
ax1.annotate("", xy=(4.5, 2.7), xytext=(3.6, 3.9), arrowprops=dict(arrowstyle="->", color="#16A34A", lw=1.5))

# Replika 1
ax1.add_patch(patches.FancyBboxPatch((0.4, 1.9), 2.2, 0.8, boxstyle="round,pad=0.08", fc="#F0FDF4", ec="#16A34A", lw=1.5))
ax1.text(1.5, 2.3, "Storage Node 1\n(Replika Salinan 1)", ha="center", va="center", fontsize=8, fontweight="bold", color="#15803D")

# Replika 2
ax1.add_patch(patches.FancyBboxPatch((3.4, 1.9), 2.2, 0.8, boxstyle="round,pad=0.08", fc="#F0FDF4", ec="#16A34A", lw=1.5))
ax1.text(4.5, 2.3, "Storage Node 2\n(Replika Salinan 2)", ha="center", va="center", fontsize=8, fontweight="bold", color="#15803D")

ax1.annotate("", xy=(3.0, 0.9), xytext=(1.5, 1.9), arrowprops=dict(arrowstyle="->", color="#059669", lw=1.2))
ax1.annotate("", xy=(3.0, 0.9), xytext=(4.5, 1.9), arrowprops=dict(arrowstyle="->", color="#059669", lw=1.2))

ax1.add_patch(patches.FancyBboxPatch((1.5, 0.2), 3.0, 0.7, boxstyle="round,pad=0.08", fc="#FEF3C7", ec="#D97706", lw=1.5))
ax1.text(3.0, 0.55, "3. Konfirmasi & Catat Metadata\n(Actual Replicas = 2, Status 200 OK)", ha="center", va="center", fontsize=8, fontweight="bold", color="#92400E")


# === Subplot 2: Failover Download ===
ax2.set_title("B. Alur Pengalihan Kegagalan (Failover Unduhan)", fontsize=11, fontweight="bold", color="#0F172A", pad=10)

ax2.add_patch(patches.FancyBboxPatch((1.8, 5.8), 2.4, 0.8, boxstyle="round,pad=0.08", fc="#EFF6FF", ec="#2563EB", lw=1.5))
ax2.text(3.0, 6.2, "1. Klien Minta Unduhan\n(GET /api/download/{id})", ha="center", va="center", fontsize=8.5, fontweight="bold", color="#1E293B")

ax2.annotate("", xy=(3.0, 4.8), xytext=(3.0, 5.8), arrowprops=dict(arrowstyle="->", color="#2563EB", lw=1.5))

ax2.add_patch(patches.FancyBboxPatch((1.5, 3.9), 3.0, 0.9, boxstyle="round,pad=0.08", fc="#1E293B", ec="#0F172A", lw=1.5))
ax2.text(3.0, 4.35, "2. Koordinator Hubungi Node 1\n(Penyimpan Primer)", ha="center", va="center", fontsize=8.5, fontweight="bold", color="#FFFFFF")

ax2.annotate("", xy=(1.5, 2.7), xytext=(2.4, 3.9), arrowprops=dict(arrowstyle="->", color="#DC2626", lw=1.5, ls="--"))

# Node 1 Crash (Red)
ax2.add_patch(patches.FancyBboxPatch((0.4, 1.9), 2.2, 0.8, boxstyle="round,pad=0.08", fc="#FEF2F2", ec="#DC2626", lw=1.5))
ax2.text(1.5, 2.3, "Storage Node 1\n[OFFLINE / CRASH]", ha="center", va="center", fontsize=8, fontweight="bold", color="#B91C1C")

# Failover Arrow to Node 2
ax2.annotate("Failover Otomatis\n(Koneksi Gagal)", xy=(4.5, 2.7), xytext=(2.7, 2.3),
             arrowprops=dict(arrowstyle="->", color="#2563EB", lw=1.8),
             fontsize=7.5, color="#1D4ED8", fontweight="bold", ha="center")

# Node 2 OK (Green)
ax2.add_patch(patches.FancyBboxPatch((3.4, 1.9), 2.2, 0.8, boxstyle="round,pad=0.08", fc="#F0FDF4", ec="#16A34A", lw=1.5))
ax2.text(4.5, 2.3, "Storage Node 2\n(Replika Sekunder: AKTIF)", ha="center", va="center", fontsize=8, fontweight="bold", color="#15803D")

ax2.annotate("", xy=(3.0, 0.9), xytext=(4.5, 1.9), arrowprops=dict(arrowstyle="->", color="#16A34A", lw=1.5))

ax2.add_patch(patches.FancyBboxPatch((1.5, 0.2), 3.0, 0.7, boxstyle="round,pad=0.08", fc="#F0FDF4", ec="#16A34A", lw=1.5))
ax2.text(3.0, 0.55, "3. Berkas Berhasil Dialirkan\n(Header: X-Served-By: node2)", ha="center", va="center", fontsize=8, fontweight="bold", color="#166534")

plt.tight_layout()
plt.savefig("diagrams/alur_failover_replikasi.png", bbox_inches='tight')
plt.close()
print("[OK] Created diagrams/alur_failover_replikasi.png")
