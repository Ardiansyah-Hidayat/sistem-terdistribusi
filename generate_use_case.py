import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

os.makedirs("diagrams", exist_ok=True)

plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["Arial", "DejaVu Sans", "Segoe UI"]


def draw_stick_actor(ax, x, y, label, scale=1.0):
    """Draw a standard UML stick figure actor centered at (x, y)."""
    head_r = 0.22 * scale
    ax.add_patch(patches.Circle((x, y + 0.55 * scale), head_r, facecolor="#FFFFFF", edgecolor="#000000", lw=1.6, zorder=6))
    ax.plot([x, x], [y + 0.33 * scale, y - 0.25 * scale], color="#000000", lw=1.6, zorder=6)
    ax.plot([x - 0.32 * scale, x + 0.32 * scale], [y + 0.15 * scale, y + 0.15 * scale], color="#000000", lw=1.6, zorder=6)
    ax.plot([x, x - 0.28 * scale], [y - 0.25 * scale, y - 0.72 * scale], color="#000000", lw=1.6, zorder=6)
    ax.plot([x, x + 0.28 * scale], [y - 0.25 * scale, y - 0.72 * scale], color="#000000", lw=1.6, zorder=6)
    if label:
        ax.text(x, y - 0.92 * scale, label, ha="center", va="top", fontsize=9.2, fontweight="bold", color="#000000", linespacing=1.2, zorder=6)


def draw_use_case_oval(ax, x, y, w, h, text, fill="#FFFFFF", lw=1.4, fontsize=8.2, bold=False):
    """Draw a standard UML Use Case ellipse centered at (x, y)."""
    ellipse = patches.Ellipse((x, y), width=w, height=h, facecolor=fill, edgecolor="#000000", lw=lw, zorder=4)
    ax.add_patch(ellipse)
    ax.text(
        x, y, text, ha="center", va="center", fontsize=fontsize,
        fontweight="bold" if bold else "normal",
        color="#000000", linespacing=1.2, zorder=5
    )


def draw_assoc(ax, x1, y1, x2, y2, lw=1.15):
    ax.plot([x1, x2], [y1, y2], color="#000000", lw=lw, zorder=2)


def draw_dashed_rel(ax, x1, y1, x2, y2, stereotype="«include»", label_offset=(0, 0.14)):
    ax.annotate(
        "", xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(arrowstyle="->", color="#000000", lw=1.25, ls="--", shrinkA=2, shrinkB=2),
        zorder=4
    )
    mx = (x1 + x2) / 2 + label_offset[0]
    my = (y1 + y2) / 2 + label_offset[1]
    ax.text(
        mx, my, stereotype, ha="center", va="center", fontsize=7.8, style="italic", color="#000000",
        bbox=dict(boxstyle="square,pad=0.08", fc="#FFFFFF", ec="none"), zorder=6
    )


def draw_legend(ax, leg_x, leg_y, leg_w=1.85, leg_h=3.60):
    ax.add_patch(patches.Rectangle((leg_x, leg_y), leg_w, leg_h, facecolor="#FFFFFF", edgecolor="#000000", lw=1.1, ls="--", zorder=3))
    ax.text(leg_x + 0.14, leg_y + leg_h - 0.28, "Keterangan:", ha="left", va="center", fontsize=9.0, fontweight="bold", zorder=6)

    # 1. Actor symbol
    draw_stick_actor(ax, leg_x + 0.38, leg_y + leg_h - 0.90, "", scale=0.45)
    ax.text(leg_x + 0.72, leg_y + leg_h - 0.90, ": Aktor", ha="left", va="center", fontsize=8.0, zorder=6)

    # 2. Use Case symbol
    ax.add_patch(patches.Ellipse((leg_x + 0.38, leg_y + leg_h - 1.68), 0.50, 0.28, facecolor="#FFFFFF", edgecolor="#000000", lw=1.2, zorder=6))
    ax.text(leg_x + 0.72, leg_y + leg_h - 1.68, ": Use Case", ha="left", va="center", fontsize=8.0, zorder=6)

    # 3. Association symbol
    ax.plot([leg_x + 0.15, leg_x + 0.60], [leg_y + leg_h - 2.25, leg_y + leg_h - 2.25], color="#000000", lw=1.2, zorder=6)
    ax.text(leg_x + 0.72, leg_y + leg_h - 2.25, ": Asosiasi", ha="left", va="center", fontsize=8.0, zorder=6)

    # 4. Include symbol
    ax.annotate("", xy=(leg_x + 0.62, leg_y + leg_h - 2.78), xytext=(leg_x + 0.14, leg_y + leg_h - 2.78),
                arrowprops=dict(arrowstyle="->", color="#000000", lw=1.1, ls="--"), zorder=6)
    ax.text(leg_x + 0.38, leg_y + leg_h - 2.95, "«include»", ha="center", va="center", fontsize=7.2, style="italic", zorder=6)
    ax.text(leg_x + 0.72, leg_y + leg_h - 2.78, ": Relasi Include", ha="left", va="center", fontsize=7.8, zorder=6)

    # 5. Extend symbol
    ax.annotate("", xy=(leg_x + 0.62, leg_y + leg_h - 3.30), xytext=(leg_x + 0.14, leg_y + leg_h - 3.30),
                arrowprops=dict(arrowstyle="->", color="#000000", lw=1.1, ls="--"), zorder=6)
    ax.text(leg_x + 0.38, leg_y + leg_h - 3.47, "«extend»", ha="center", va="center", fontsize=7.2, style="italic", zorder=6)
    ax.text(leg_x + 0.72, leg_y + leg_h - 3.30, ": Relasi Extend", ha="left", va="center", fontsize=7.8, zorder=6)


# ==============================================================================
# VERSI 1: Use Case Diagram Lengkap dengan Aktor Node 1, Node 2, & Node 3
# ==============================================================================
def build_use_case_v1():
    fig, ax = plt.subplots(figsize=(15.0, 8.6), dpi=300)
    ax.set_xlim(0, 15.0)
    ax.set_ylim(0, 8.8)
    ax.axis("off")

    ax.text(6.45, 8.42, "Use Case Diagram", ha="center", va="center", fontsize=15.5, fontweight="bold", color="#000000")
    ax.text(6.45, 8.05, "Sistem Klaster Penyimpanan Berkas Terdistribusi (Arsitektur Master-Worker 3 Node)",
            ha="center", va="center", fontsize=11.2, color="#222222")

    bx, by, bw, bh = 2.05, 0.35, 8.80, 7.40
    ax.add_patch(patches.Rectangle((bx, by), bw, bh, facecolor="#FFFFFF", edgecolor="#000000", lw=1.6, zorder=1))
    ax.text(bx + bw / 2, by + bh - 0.26, "Sistem Klaster Penyimpanan Berkas Terdistribusi (Master Coordinator)",
            ha="center", va="center", fontsize=10.2, fontweight="bold", color="#000000")

    admin_x, admin_y = 0.90, 5.75
    guest_x, guest_y = 0.90, 2.05
    draw_stick_actor(ax, admin_x, admin_y, "Administrator", scale=0.92)
    draw_stick_actor(ax, guest_x, guest_y, "Pengguna Tamu\n(Guest)", scale=0.92)

    node_actors = [
        (11.95, 6.05, "Storage Node 1\n(Port 8001 / VM 1)"),
        (11.95, 3.85, "Storage Node 2\n(Port 8002 / VM 2)"),
        (11.95, 1.65, "Storage Node 3\n(Port 8003 / VM 3)"),
    ]
    for nx, ny, nlabel in node_actors:
        draw_stick_actor(ax, nx, ny, nlabel, scale=0.85)

    col1_x = 3.85
    col1_w = 2.75
    col1_h = 0.56

    uc_login_admin = (col1_x, 6.95, col1_w, col1_h, "Login Administrator")
    uc_kelola_tamu = (col1_x, 6.18, col1_w, 0.60, "Mengelola Akses &\nMode Eksperimen Tamu")
    uc_simulasi_node = (col1_x, 5.38, col1_w, 0.62, "Simulasi Matikan / Nyalakan\nNode (Node 1, Node 2, Node 3)")
    uc_hapus_berkas = (col1_x, 4.58, col1_w, col1_h, "Menghapus Berkas")
    uc_lihat_node = (col1_x, 3.78, col1_w, 0.62, "Melihat Status Kesehatan\nNode 1, Node 2, dan Node 3")
    uc_lihat_berkas = (col1_x, 2.98, col1_w, 0.58, "Melihat Daftar Berkas\n& Lokasi Replika")
    uc_unggah = (col1_x, 2.18, col1_w, col1_h, "Mengunggah Berkas")
    uc_unduh = (col1_x, 1.38, col1_w, col1_h, "Mengunduh Berkas")
    uc_login_tamu = (col1_x, 0.68, col1_w, col1_h, "Masuk sebagai Tamu")

    for x, y, w, h, txt in [
        uc_login_admin, uc_kelola_tamu, uc_simulasi_node, uc_hapus_berkas,
        uc_lihat_node, uc_lihat_berkas, uc_unggah, uc_unduh, uc_login_tamu
    ]:
        draw_use_case_oval(ax, x, y, w, h, txt, fill="#FFFFFF", fontsize=8.1)

    col2_x = 8.45
    col2_w = 3.25

    uc_kontrol_node = (col2_x, 5.38, col2_w, 0.66, "Kontrol Status Aktif / Mati\npada Node 1, Node 2, atau Node 3")
    uc_hapus_replika = (col2_x, 4.58, col2_w, 0.64, "Hapus Salinan Berkas pada\nNode 1, Node 2, dan Node 3")
    uc_heartbeat = (col2_x, 3.78, col2_w, 0.66, "Pemantauan Heartbeat (/health)\nke Node 1, Node 2, dan Node 3")
    uc_replikasi = (col2_x, 2.18, col2_w, 0.74, "Replikasi Least-Loaded (RF = 2)\nke 2 dari 3 Storage Node Aktif\n(Node 1, Node 2, Node 3)")
    uc_failover = (col2_x, 1.18, col2_w, 0.74, "Pengalihan Unduhan Otomatis\n(Failover ke Node Cadangan:\nNode 1 / Node 2 / Node 3)")

    col2_list = [uc_kontrol_node, uc_hapus_replika, uc_heartbeat, uc_replikasi, uc_failover]
    for x, y, w, h, txt in col2_list:
        draw_use_case_oval(ax, x, y, w, h, txt, fill="#F2F2F2", fontsize=8.0)

    for ux, uy, uw, uh, _ in [
        uc_login_admin, uc_kelola_tamu, uc_simulasi_node, uc_hapus_berkas,
        uc_lihat_node, uc_lihat_berkas, uc_unggah, uc_unduh
    ]:
        draw_assoc(ax, admin_x + 0.35, admin_y + 0.05, ux - uw / 2, uy)

    for ux, uy, uw, uh, _ in [
        uc_lihat_node, uc_lihat_berkas, uc_unggah, uc_unduh, uc_login_tamu
    ]:
        draw_assoc(ax, guest_x + 0.35, guest_y + 0.05, ux - uw / 2, uy)

    draw_dashed_rel(ax, uc_simulasi_node[0] + col1_w / 2, uc_simulasi_node[1],
                    uc_kontrol_node[0] - col2_w / 2, uc_kontrol_node[1], "«include»", (0, 0.15))
    draw_dashed_rel(ax, uc_hapus_berkas[0] + col1_w / 2, uc_hapus_berkas[1],
                    uc_hapus_replika[0] - col2_w / 2, uc_hapus_replika[1], "«include»", (0, 0.15))
    draw_dashed_rel(ax, uc_lihat_node[0] + col1_w / 2, uc_lihat_node[1],
                    uc_heartbeat[0] - col2_w / 2, uc_heartbeat[1], "«include»", (0, 0.15))
    draw_dashed_rel(ax, uc_unggah[0] + col1_w / 2, uc_unggah[1],
                    uc_replikasi[0] - col2_w / 2, uc_replikasi[1], "«include»", (0, 0.15))
    draw_dashed_rel(ax, uc_failover[0] - col2_w / 2, uc_failover[1] + 0.06,
                    uc_unduh[0] + col1_w / 2, uc_unduh[1] - 0.04, "«extend»", (0, 0.16))

    for ux, uy, uw, uh, _ in col2_list:
        for nx, ny, _ in node_actors:
            draw_assoc(ax, ux + uw / 2, uy, nx - 0.35, ny + 0.10, lw=1.05)

    draw_legend(ax, 13.00, 2.35, 1.85, 3.60)

    plt.tight_layout()
    plt.savefig("diagrams/use_case_diagram.png", bbox_inches="tight", facecolor="#FFFFFF")
    plt.close()
    print("[OK] Saved diagrams/use_case_diagram.png")


# ==============================================================================
# VERSI 2: Tata Letak Mirip Gambar 5 Temanmu (Admin di Kiri, Tamu di Kanan,
#          dan Ketiga Storage Node: Node 1, Node 2, Node 3 di dalam Boundary)
# ==============================================================================
def build_use_case_v2():
    fig, ax = plt.subplots(figsize=(14.5, 8.4), dpi=300)
    ax.set_xlim(0, 14.5)
    ax.set_ylim(0, 8.6)
    ax.axis("off")

    ax.text(6.15, 8.22, "Use Case Diagram", ha="center", va="center", fontsize=15.5, fontweight="bold", color="#000000")
    ax.text(6.15, 7.85, "Sistem Klaster Penyimpanan Berkas Terdistribusi", ha="center", va="center", fontsize=11.5, color="#222222")

    bx, by, bw, bh = 1.95, 0.35, 8.45, 7.20
    ax.add_patch(patches.Rectangle((bx, by), bw, bh, facecolor="#FFFFFF", edgecolor="#000000", lw=1.6, zorder=1))
    ax.text(bx + bw / 2, by + bh - 0.26, "Sistem Klaster Penyimpanan Berkas Terdistribusi",
            ha="center", va="center", fontsize=10.5, fontweight="bold", color="#000000")

    # Left Actor: Administrator
    admin_x, admin_y = 0.85, 4.35
    draw_stick_actor(ax, admin_x, admin_y, "Administrator", scale=0.95)

    # Right Actor: Pengguna Tamu
    guest_x, guest_y = 11.45, 4.35
    draw_stick_actor(ax, guest_x, guest_y, "Pengguna Tamu", scale=0.95)

    # Left Column (Admin-specific Use Cases)
    uc_login_admin = (3.40, 6.55, 2.35, 0.56, "Login Administrator")
    uc_kelola_tamu = (3.40, 5.75, 2.45, 0.60, "Mengelola Akses &\nMode Eksperimen Tamu")
    uc_simulasi = (3.40, 4.90, 2.55, 0.64, "Simulasi Matikan / Nyalakan\nNode 1, Node 2, & Node 3")
    uc_hapus = (3.40, 4.05, 2.35, 0.56, "Menghapus Berkas")

    # Center-Right Column (Shared + Guest Use Cases)
    uc_masuk_tamu = (7.25, 6.55, 2.45, 0.56, "Masuk sebagai Tamu")
    uc_lihat_node = (7.25, 5.75, 2.65, 0.60, "Melihat Status Kesehatan\nNode 1, Node 2, & Node 3")
    uc_lihat_berkas = (7.25, 4.95, 2.55, 0.58, "Melihat Daftar Berkas\n& Lokasi Replika")
    uc_unggah = (7.25, 4.15, 2.45, 0.56, "Mengunggah Berkas")
    uc_unduh = (7.25, 3.35, 2.45, 0.56, "Mengunduh Berkas")

    # Middle Tier (Replication & Failover Orchestration)
    uc_replikasi = (4.45, 2.15, 3.10, 0.68, "Replikasi Least-Loaded (RF = 2)\nke 2 dari 3 Storage Node")
    uc_failover = (8.15, 2.15, 3.05, 0.68, "Pengalihan Unduhan Otomatis\n(Failover ke Node Aktif)")

    # Bottom Tier: Explicit 3 Storage Nodes (Node 1, Node 2, Node 3)
    uc_node1 = (3.35, 0.85, 2.35, 0.62, "Penyimpanan & Akses\nStorage Node 1 (8001)")
    uc_node2 = (6.15, 0.85, 2.35, 0.62, "Penyimpanan & Akses\nStorage Node 2 (8002)")
    uc_node3 = (8.95, 0.85, 2.35, 0.62, "Penyimpanan & Akses\nStorage Node 3 (8003)")

    for x, y, w, h, txt in [
        uc_login_admin, uc_kelola_tamu, uc_simulasi, uc_hapus,
        uc_masuk_tamu, uc_lihat_node, uc_lihat_berkas, uc_unggah, uc_unduh
    ]:
        draw_use_case_oval(ax, x, y, w, h, txt, fill="#FFFFFF", fontsize=8.1)

    for x, y, w, h, txt in [uc_replikasi, uc_failover, uc_node1, uc_node2, uc_node3]:
        draw_use_case_oval(ax, x, y, w, h, txt, fill="#F2F2F2", fontsize=8.0)

    # Admin associations
    for ux, uy, uw, uh, _ in [uc_login_admin, uc_kelola_tamu, uc_simulasi, uc_hapus]:
        draw_assoc(ax, admin_x + 0.35, admin_y + 0.10, ux - uw / 2, uy)

    # Admin also accesses shared use cases (routed cleanly)
    for ux, uy, uw, uh, _ in [uc_lihat_node, uc_lihat_berkas, uc_unggah, uc_unduh]:
        draw_assoc(ax, admin_x + 0.35, admin_y - 0.15, ux - uw / 2, uy, lw=0.95)

    # Guest associations
    for ux, uy, uw, uh, _ in [uc_masuk_tamu, uc_lihat_node, uc_lihat_berkas, uc_unggah, uc_unduh]:
        draw_assoc(ax, guest_x - 0.35, guest_y + 0.10, ux + uw / 2, uy)

    # Correct Include / Extend relations
    # Mengunggah Berkas --<<include>>--> Replikasi Least-Loaded (RF=2)
    draw_dashed_rel(ax, uc_unggah[0] - 0.5, uc_unggah[1] - uc_unggah[3] / 2,
                    uc_replikasi[0] + 0.3, uc_replikasi[1] + uc_replikasi[3] / 2,
                    "«include»", (-0.35, 0.08))

    # Pengalihan Unduhan Otomatis (Failover) --<<extend>>--> Mengunduh Berkas
    draw_dashed_rel(ax, uc_failover[0], uc_failover[1] + uc_failover[3] / 2,
                    uc_unduh[0] + 0.3, uc_unduh[1] - uc_unduh[3] / 2,
                    "«extend»", (0.42, 0.02))

    # Replikasi & Failover involve Storage Node 1, Storage Node 2, and Storage Node 3
    rel_offsets_rep = [(-0.22, 0.06), (-0.42, 0.14), (0.10, 0.14)]
    rel_offsets_fail = [(-0.10, -0.14), (0.42, 0.14), (0.25, 0.06)]
    for idx, n_uc in enumerate([uc_node1, uc_node2, uc_node3]):
        draw_dashed_rel(ax, uc_replikasi[0], uc_replikasi[1] - uc_replikasi[3] / 2,
                        n_uc[0] - 0.18, n_uc[1] + n_uc[3] / 2, "«include»", rel_offsets_rep[idx])
        draw_dashed_rel(ax, uc_failover[0], uc_failover[1] - uc_failover[3] / 2,
                        n_uc[0] + 0.18, n_uc[1] + n_uc[3] / 2, "«include»", rel_offsets_fail[idx])

    draw_legend(ax, 12.40, 2.35, 1.85, 3.60)

    plt.tight_layout()
    plt.savefig("diagrams/use_case_diagram_opsi2.png", bbox_inches="tight", facecolor="#FFFFFF")
    plt.close()
    print("[OK] Saved diagrams/use_case_diagram_opsi2.png")


if __name__ == "__main__":
    build_use_case_v1()
    build_use_case_v2()
