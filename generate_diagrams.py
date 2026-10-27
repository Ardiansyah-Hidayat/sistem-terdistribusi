import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

os.makedirs("diagrams", exist_ok=True)

plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["Arial", "DejaVu Sans", "Segoe UI"]


def draw_sharp_box(ax, x, y, w, h, title, subtitle_lines=None, header_fill="#E5E5E5", body_fill="#FFFFFF", lw=1.6, ls="-", fontsize=8.8):
    """Draw a strict monochrome sharp-cornered rectangle with an optional header band."""
    if subtitle_lines:
        header_h = min(0.48, h * 0.36)
        body_h = h - header_h
        ax.add_patch(patches.Rectangle((x, y), w, body_h, facecolor=body_fill, edgecolor="#000000", linewidth=lw, linestyle=ls))
        ax.add_patch(patches.Rectangle((x, y + body_h), w, header_h, facecolor=header_fill, edgecolor="#000000", linewidth=lw, linestyle=ls))
        ax.text(x + w / 2, y + body_h + header_h / 2, title, ha="center", va="center", fontsize=9.5, fontweight="bold", color="#000000")
        body_text = "\n".join(subtitle_lines)
        ax.text(x + w / 2, y + body_h / 2, body_text, ha="center", va="center", fontsize=8.5, color="#111111", linespacing=1.35)
    else:
        ax.add_patch(patches.Rectangle((x, y), w, h, facecolor=body_fill, edgecolor="#000000", linewidth=lw, linestyle=ls))
        ax.text(x + w / 2, y + h / 2, title, ha="center", va="center", fontsize=fontsize, fontweight="bold", color="#000000", linespacing=1.28)


# ==============================================================================
# DIAGRAM 1: Arsitektur Sistem (Monochrome, Sharp Rectangles, 3 Nodes)
# ==============================================================================
fig, ax = plt.subplots(figsize=(10.5, 5.8), dpi=300)
ax.set_xlim(0, 10.5)
ax.set_ylim(0, 6.6)
ax.axis("off")

ax.add_patch(patches.Rectangle((3.45, 0.35), 6.75, 5.85, facecolor="none", edgecolor="#444444", linewidth=1.2, linestyle="--"))
ax.text(6.82, 6.0, "Klaster Penyimpanan Terdistribusi (Master-Worker 3 Node)", ha="center", va="center", fontsize=9, fontweight="bold", color="#222222")

draw_sharp_box(
    ax, x=0.2, y=2.45, w=2.2, h=1.6,
    title="KLIEN / PENGGUNA",
    subtitle_lines=[
        "Konsol Web Browser",
        "Protokol: HTTP / REST",
        "Peran: Admin / Tamu"
    ],
    header_fill="#E5E5E5", body_fill="#FFFFFF"
)

draw_sharp_box(
    ax, x=3.75, y=1.65, w=2.70, h=3.2,
    title="MASTER COORDINATOR",
    subtitle_lines=[
        "Endpoint: Port 8000 (FastAPI)",
        "────────────────────",
        "• Katalog Metadata (JSON)",
        "• Seleksi Node (Least-Loaded)",
        "• Pemantau Heartbeat (3 dtk)",
        "• Kontrol Akses RBAC & Token",
        "• Pengalih Unduhan (Failover)"
    ],
    header_fill="#CCCCCC", body_fill="#FAFAFA", lw=1.8
)

nodes_spec = [
    ("STORAGE NODE 1", 4.35, "Port: 8001 (FastAPI Worker)", "Lokal: 127.0.0.1:8001", "VM: 192.168.56.102:8001"),
    ("STORAGE NODE 2", 2.50, "Port: 8002 (FastAPI Worker)", "Lokal: 127.0.0.1:8002", "VM: 192.168.56.103:8002"),
    ("STORAGE NODE 3", 0.65, "Port: 8003 (FastAPI Worker)", "Lokal: 127.0.0.1:8003", "VM: 192.168.56.104:8003"),
]

for title, y_pos, l1, l2, l3 in nodes_spec:
    draw_sharp_box(
        ax, x=7.65, y=y_pos, w=2.3, h=1.4,
        title=title,
        subtitle_lines=[l1, l2, l3],
        header_fill="#E5E5E5", body_fill="#FFFFFF"
    )

ax.annotate("", xy=(3.75, 3.25), xytext=(2.4, 3.25), arrowprops=dict(arrowstyle="<->", color="#000000", lw=1.6))
ax.text(2.92, 3.42, "REST API\n(Unggah / Unduh)", ha="center", va="bottom", fontsize=8, color="#000000")

ax.annotate("", xy=(7.65, 5.05), xytext=(6.45, 4.1), arrowprops=dict(arrowstyle="<->", color="#000000", lw=1.4))
ax.annotate("", xy=(7.65, 3.20), xytext=(6.45, 3.20), arrowprops=dict(arrowstyle="<->", color="#000000", lw=1.4))
ax.annotate("", xy=(7.65, 1.35), xytext=(6.45, 2.3), arrowprops=dict(arrowstyle="<->", color="#000000", lw=1.4))

ax.text(7.05, 3.42, "Replikasi (/store)\nUnduh (/retrieve)\nHeartbeat (/health)", ha="center", va="bottom", fontsize=7.8, color="#111111")

plt.tight_layout()
plt.savefig("diagrams/arsitektur_sistem.png", bbox_inches="tight", facecolor="#FFFFFF")
plt.close()
print("[OK] Created diagrams/arsitektur_sistem.png")


# ==============================================================================
# DIAGRAM 2: Alur Replikasi & Failover pada 3 Node (Node 1, Node 2, Node 3)
# ==============================================================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.2, 6.0), dpi=300)

for ax in (ax1, ax2):
    ax.set_xlim(0, 6.4)
    ax.set_ylim(0, 7.2)
    ax.axis("off")

# Outer border for Panel A & Panel B
ax1.add_patch(patches.Rectangle((0.12, 0.1), 6.16, 6.9, facecolor="none", edgecolor="#000000", linewidth=1.2))
ax1.add_patch(patches.Rectangle((0.12, 6.45), 6.16, 0.55, facecolor="#E5E5E5", edgecolor="#000000", linewidth=1.2))
ax1.text(3.2, 6.72, "A. Alur Replikasi Berkas ke Klaster 3 Node (RF = 2)", ha="center", va="center", fontsize=9.8, fontweight="bold", color="#000000")

ax2.add_patch(patches.Rectangle((0.12, 0.1), 6.16, 6.9, facecolor="none", edgecolor="#000000", linewidth=1.2))
ax2.add_patch(patches.Rectangle((0.12, 6.45), 6.16, 0.55, facecolor="#E5E5E5", edgecolor="#000000", linewidth=1.2))
ax2.text(3.2, 6.72, "B. Alur Failover Otomatis pada Klaster 3 Node", ha="center", va="center", fontsize=9.8, fontweight="bold", color="#000000")

# --- Panel A: Upload & Least-Loaded across Node 1, Node 2, Node 3 ---
draw_sharp_box(ax1, 1.5, 5.35, 3.4, 0.8, "1. Klien Unggah Berkas\nPOST /api/upload", body_fill="#FFFFFF")
ax1.annotate("", xy=(3.2, 4.55), xytext=(3.2, 5.35), arrowprops=dict(arrowstyle="->", color="#000000", lw=1.5))

draw_sharp_box(ax1, 0.9, 3.65, 4.6, 0.9, "2. Koordinator Evaluasi Beban 3 Node Aktif\n(Pilih 2 Node Beban Terendah dari Node 1, 2, 3)", body_fill="#F2F2F2")

# Arrows to Node 1, Node 2 (selected), and Node 3 (standby for next upload)
ax1.annotate("", xy=(1.15, 2.80), xytext=(2.2, 3.65), arrowprops=dict(arrowstyle="->", color="#000000", lw=1.5))
ax1.annotate("", xy=(3.20, 2.80), xytext=(3.2, 3.65), arrowprops=dict(arrowstyle="->", color="#000000", lw=1.5))
ax1.annotate("", xy=(5.25, 2.80), xytext=(4.2, 3.65), arrowprops=dict(arrowstyle="->", color="#555555", lw=1.1, ls=":"))

draw_sharp_box(ax1, 0.25, 1.85, 1.80, 0.95, "Storage Node 1\nPOST /store/{id}\n[Replika 1]", body_fill="#FFFFFF", lw=1.6, fontsize=7.8)
draw_sharp_box(ax1, 2.30, 1.85, 1.80, 0.95, "Storage Node 2\nPOST /store/{id}\n[Replika 2]", body_fill="#FFFFFF", lw=1.6, fontsize=7.8)
draw_sharp_box(ax1, 4.35, 1.85, 1.80, 0.95, "Storage Node 3\n[Aktif / Siaga]\nTarget Giliran Berikut", body_fill="#F8F8F8", lw=1.2, ls="--", fontsize=7.5)

ax1.annotate("", xy=(2.6, 1.1), xytext=(1.15, 1.85), arrowprops=dict(arrowstyle="->", color="#000000", lw=1.4))
ax1.annotate("", xy=(3.4, 1.1), xytext=(3.20, 1.85), arrowprops=dict(arrowstyle="->", color="#000000", lw=1.4))

draw_sharp_box(ax1, 0.9, 0.3, 4.6, 0.8, "3. Catat Katalog Metadata JSON\n(Status 200 OK · Distribusi Merata di Node 1, 2, 3)", body_fill="#E5E5E5")

# --- Panel B: Failover across Node 1, Node 2, Node 3 ---
draw_sharp_box(ax2, 1.5, 5.35, 3.4, 0.8, "1. Klien Minta Unduhan\nGET /api/download/{id}", body_fill="#FFFFFF")
ax2.annotate("", xy=(3.2, 4.55), xytext=(3.2, 5.35), arrowprops=dict(arrowstyle="->", color="#000000", lw=1.5))

draw_sharp_box(ax2, 0.9, 3.65, 4.6, 0.9, "2. Koordinator Cek Lokasi Replika pada 3 Node\n(Replika Berkas Tersedia di: node1, node2 / node3)", body_fill="#F2F2F2")

# Dashed arrow to failed Node 1
ax2.annotate("", xy=(1.15, 2.80), xytext=(2.2, 3.65), arrowprops=dict(arrowstyle="->", color="#000000", lw=1.4, ls="--"))
ax2.text(1.12, 3.25, "Gagal", ha="center", va="center", fontsize=7.5, style="italic", color="#000000")

# Failover arrows to Node 2 / Node 3
ax2.annotate("", xy=(3.20, 2.80), xytext=(3.2, 3.65), arrowprops=dict(arrowstyle="->", color="#000000", lw=1.6))
ax2.text(3.72, 3.25, "Failover", ha="center", va="center", fontsize=7.5, fontweight="bold", color="#000000")
ax2.annotate("", xy=(5.25, 2.80), xytext=(4.2, 3.65), arrowprops=dict(arrowstyle="->", color="#333333", lw=1.2, ls=":"))

draw_sharp_box(ax2, 0.25, 1.85, 1.80, 0.95, "Storage Node 1\n[STATUS: MATI]\nKoneksi Ditolak", body_fill="#F2F2F2", lw=1.5, ls="--", fontsize=7.8)
draw_sharp_box(ax2, 2.30, 1.85, 1.80, 0.95, "Storage Node 2\nGET /retrieve/{id}\n[FAILOVER AKTIF]", body_fill="#FFFFFF", lw=1.8, fontsize=7.8)
draw_sharp_box(ax2, 4.35, 1.85, 1.80, 0.95, "Storage Node 3\nGET /retrieve/{id}\n[REPLIKA AKTIF]", body_fill="#FFFFFF", lw=1.4, fontsize=7.8)

ax2.annotate("", xy=(3.2, 1.1), xytext=(3.20, 1.85), arrowprops=dict(arrowstyle="->", color="#000000", lw=1.5))
ax2.annotate("", xy=(3.8, 1.1), xytext=(5.25, 1.85), arrowprops=dict(arrowstyle="->", color="#444444", lw=1.1, ls=":"))

draw_sharp_box(ax2, 0.9, 0.3, 4.6, 0.8, "3. Berkas Berhasil Dikirim ke Klien\n(Header HTTP: X-Served-By: node2 / node3)", body_fill="#E5E5E5")

plt.tight_layout()
plt.savefig("diagrams/alur_failover_replikasi.png", bbox_inches="tight", facecolor="#FFFFFF")
plt.close()
print("[OK] Created diagrams/alur_failover_replikasi.png with all 3 nodes")
