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
        ax.text(x, y - 0.92 * scale, label, ha="center", va="top", fontsize=9.8, fontweight="bold", color="#000000", linespacing=1.2, zorder=6)


def draw_use_case_oval(ax, x, y, w, h, text, fill="#FFFFFF", lw=1.4, fontsize=8.3, bold=False):
    """Draw a standard UML Use Case ellipse centered at (x, y)."""
    ellipse = patches.Ellipse((x, y), width=w, height=h, facecolor=fill, edgecolor="#000000", lw=lw, zorder=4)
    ax.add_patch(ellipse)
    ax.text(
        x, y, text, ha="center", va="center", fontsize=fontsize,
        fontweight="bold" if bold else "normal",
        color="#000000", linespacing=1.2, zorder=5
    )


def draw_assoc(ax, x1, y1, x2, y2, lw=1.2):
    ax.plot([x1, x2], [y1, y2], color="#000000", lw=lw, zorder=2)


def draw_dashed_rel(ax, x1, y1, x2, y2, stereotype="«include»", label_offset=(0, 0.14)):
    ax.annotate(
        "", xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(arrowstyle="->", color="#000000", lw=1.2, ls="--", shrinkA=2, shrinkB=2),
        zorder=4
    )
    mx = (x1 + x2) / 2 + label_offset[0]
    my = (y1 + y2) / 2 + label_offset[1]
    ax.text(
        mx, my, stereotype, ha="center", va="center", fontsize=7.6, style="italic", color="#000000",
        bbox=dict(boxstyle="square,pad=0.06", fc="#FFFFFF", ec="none"), zorder=6
    )


def draw_legend(ax, leg_x, leg_y, leg_w=1.85, leg_h=3.60):
    ax.add_patch(patches.Rectangle((leg_x, leg_y), leg_w, leg_h, facecolor="#FFFFFF", edgecolor="#000000", lw=1.1, ls="--", zorder=3))
    ax.text(leg_x + 0.14, leg_y + leg_h - 0.28, "Keterangan:", ha="left", va="center", fontsize=9.0, fontweight="bold", zorder=6)

    # 1. Actor symbol
    draw_stick_actor(ax, leg_x + 0.38, leg_y + leg_h - 0.90, "", scale=0.45)
    ax.text(leg_x + 0.72, leg_y + leg_h - 0.90, ": Aktor", ha="left", va="center", fontsize=8.2, zorder=6)

    # 2. Use Case symbol
    ax.add_patch(patches.Ellipse((leg_x + 0.38, leg_y + leg_h - 1.68), 0.50, 0.28, facecolor="#FFFFFF", edgecolor="#000000", lw=1.2, zorder=6))
    ax.text(leg_x + 0.72, leg_y + leg_h - 1.68, ": Use Case", ha="left", va="center", fontsize=8.2, zorder=6)

    # 3. Association symbol
    ax.plot([leg_x + 0.15, leg_x + 0.60], [leg_y + leg_h - 2.25, leg_y + leg_h - 2.25], color="#000000", lw=1.2, zorder=6)
    ax.text(leg_x + 0.72, leg_y + leg_h - 2.25, ": Asosiasi", ha="left", va="center", fontsize=8.2, zorder=6)

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


def build_standard_2actor_use_case():
    fig, ax = plt.subplots(figsize=(14.6, 8.8), dpi=300)
    ax.set_xlim(0, 14.6)
    ax.set_ylim(0, 9.0)
    ax.axis("off")

    # Title
    ax.text(6.20, 8.62, "Use Case Diagram", ha="center", va="center", fontsize=15.5, fontweight="bold", color="#000000")
    ax.text(6.20, 8.24, "Sistem Klaster Penyimpanan Berkas Terdistribusi", ha="center", va="center", fontsize=11.5, color="#222222")

    # System Boundary Box (Sharp Rectangle)
    bx, by, bw, bh = 1.95, 0.35, 8.50, 7.60
    ax.add_patch(patches.Rectangle((bx, by), bw, bh, facecolor="#FFFFFF", edgecolor="#000000", lw=1.6, zorder=1))
    ax.text(bx + bw / 2, by + bh - 0.26, "Sistem Klaster Penyimpanan Berkas Terdistribusi",
            ha="center", va="center", fontsize=10.5, fontweight="bold", color="#000000")

    # ==========================================================================
    # ONLY 2 HUMAN ACTORS: Administrator (Left) & Pengguna Tamu (Right)
    # ==========================================================================
    admin_x, admin_y = 0.85, 4.85
    guest_x, guest_y = 11.50, 4.85
    draw_stick_actor(ax, admin_x, admin_y, "Administrator", scale=0.95)
    draw_stick_actor(ax, guest_x, guest_y, "Pengguna Tamu", scale=0.95)

    # ==========================================================================
    # TOP SECTION: Admin-Only Use Cases (Left) & Guest Login (Right)
    # ==========================================================================
    uc_login_admin = (3.55, 7.12, 2.50, 0.54, "Login Administrator")
    uc_kelola_tamu = (3.55, 6.40, 2.60, 0.56, "Mengelola Akses &\nMode Eksperimen Tamu")
    uc_simulasi = (3.55, 5.65, 2.75, 0.60, "Simulasi Matikan / Nyalakan\nNode 1, Node 2, & Node 3")
    uc_hapus = (3.55, 4.92, 2.50, 0.54, "Menghapus Berkas")

    uc_masuk_tamu = (8.75, 6.65, 2.45, 0.56, "Masuk sebagai Tamu")

    # ==========================================================================
    # MIDDLE SECTION: Shared Use Cases (Centered so BOTH Admin & Tamu connect
    #                 cleanly without crossing any oval!)
    # ==========================================================================
    mid_x = 6.20
    uc_lihat_node = (mid_x, 4.55, 2.80, 0.56, "Melihat Status Kesehatan\nNode 1, Node 2, dan Node 3")
    uc_lihat_berkas = (mid_x, 3.86, 2.70, 0.54, "Melihat Daftar Berkas\n& Lokasi Replika")
    uc_unggah = (mid_x, 3.18, 2.55, 0.52, "Mengunggah Berkas")
    uc_unduh = (mid_x, 2.50, 2.55, 0.52, "Mengunduh Berkas")

    # ==========================================================================
    # LOWER SECTION: Replikasi & Failover + 3 Storage Nodes (Node 1, Node 2, Node 3)
    # ==========================================================================
    uc_replikasi = (4.20, 1.68, 3.05, 0.58, "Replikasi Least-Loaded (RF = 2)\nke 2 dari 3 Storage Node")
    uc_failover = (8.20, 1.68, 3.05, 0.58, "Pengalihan Unduhan Otomatis\n(Failover ke Node Aktif)")

    # Explicit 3 Storage Nodes at the bottom
    uc_node1 = (3.30, 0.70, 2.35, 0.54, "Penyimpanan Replika\nStorage Node 1")
    uc_node2 = (6.20, 0.70, 2.35, 0.54, "Penyimpanan Replika\nStorage Node 2")
    uc_node3 = (9.10, 0.70, 2.35, 0.54, "Penyimpanan Replika\nStorage Node 3")

    # Draw Ovals
    for x, y, w, h, txt in [
        uc_login_admin, uc_kelola_tamu, uc_simulasi, uc_hapus,
        uc_masuk_tamu, uc_lihat_node, uc_lihat_berkas, uc_unggah, uc_unduh
    ]:
        draw_use_case_oval(ax, x, y, w, h, txt, fill="#FFFFFF", fontsize=8.1)

    for x, y, w, h, txt in [uc_replikasi, uc_failover, uc_node1, uc_node2, uc_node3]:
        draw_use_case_oval(ax, x, y, w, h, txt, fill="#F2F2F2", fontsize=7.9)

    # ==========================================================================
    # ASSOCIATIONS FROM ADMINISTRATOR (Left) - ZERO OVAL CROSSINGS!
    # ==========================================================================
    for ux, uy, uw, uh, _ in [
        uc_login_admin, uc_kelola_tamu, uc_simulasi, uc_hapus,
        uc_lihat_node, uc_lihat_berkas, uc_unggah, uc_unduh
    ]:
        draw_assoc(ax, admin_x + 0.35, admin_y + 0.05, ux - uw / 2, uy)

    # ==========================================================================
    # ASSOCIATIONS FROM PENGGUNA TAMU (Right) - ZERO OVAL CROSSINGS!
    # ==========================================================================
    for ux, uy, uw, uh, _ in [
        uc_masuk_tamu, uc_lihat_node, uc_lihat_berkas, uc_unggah, uc_unduh
    ]:
        draw_assoc(ax, guest_x - 0.35, guest_y + 0.05, ux + uw / 2, uy)

    # ==========================================================================
    # INCLUDE / EXTEND RELATIONS
    # ==========================================================================
    # 1. Mengunggah Berkas --<<include>>--> Replikasi Least-Loaded (RF = 2)
    draw_dashed_rel(
        ax, uc_unggah[0] - 0.65, uc_unggah[1] - uc_unggah[3] / 2,
        uc_replikasi[0] + 0.35, uc_replikasi[1] + uc_replikasi[3] / 2,
        stereotype="«include»", label_offset=(-0.38, 0.05)
    )

    # 2. Pengalihan Unduhan Otomatis (Failover) --<<extend>>--> Mengunduh Berkas
    draw_dashed_rel(
        ax, uc_failover[0] - 0.35, uc_failover[1] + uc_failover[3] / 2,
        uc_unduh[0] + 0.65, uc_unduh[1] - uc_unduh[3] / 2,
        stereotype="«extend»", label_offset=(0.38, 0.03)
    )

    # 3. Replikasi & Failover -> Storage Node 1, Storage Node 2, Storage Node 3
    draw_dashed_rel(ax, uc_replikasi[0] - 0.50, uc_replikasi[1] - uc_replikasi[3] / 2,
                    uc_node1[0], uc_node1[1] + uc_node1[3] / 2, "«include»", (-0.34, 0.03))
    draw_dashed_rel(ax, uc_replikasi[0] + 0.30, uc_replikasi[1] - uc_replikasi[3] / 2,
                    uc_node2[0] - 0.35, uc_node2[1] + uc_node2[3] / 2, "«include»", (-0.34, -0.04))
    draw_dashed_rel(ax, uc_replikasi[0] + 1.05, uc_replikasi[1] - uc_replikasi[3] / 2 + 0.04,
                    uc_node3[0] - 0.65, uc_node3[1] + uc_node3[3] / 2, "«include»", (-0.95, 0.14))

    draw_dashed_rel(ax, uc_failover[0] - 1.05, uc_failover[1] - uc_failover[3] / 2 + 0.04,
                    uc_node1[0] + 0.65, uc_node1[1] + uc_node1[3] / 2, "«include»", (0.95, 0.14))
    draw_dashed_rel(ax, uc_failover[0] - 0.30, uc_failover[1] - uc_failover[3] / 2,
                    uc_node2[0] + 0.35, uc_node2[1] + uc_node2[3] / 2, "«include»", (0.34, -0.04))
    draw_dashed_rel(ax, uc_failover[0] + 0.50, uc_failover[1] - uc_failover[3] / 2,
                    uc_node3[0], uc_node3[1] + uc_node3[3] / 2, "«include»", (0.34, 0.03))

    # Legend Box
    draw_legend(ax, 12.45, 2.70, 1.90, 3.60)

    plt.tight_layout()
    plt.savefig("diagrams/use_case_diagram.png", bbox_inches="tight", facecolor="#FFFFFF")
    plt.close()
    print("[OK] Saved standard 2-actor diagrams/use_case_diagram.png")


if __name__ == "__main__":
    build_standard_2actor_use_case()
