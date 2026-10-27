import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

os.makedirs("diagrams", exist_ok=True)

plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["Arial", "DejaVu Sans", "Segoe UI"]


def draw_stick_actor(ax, x, y, label, scale=1.0):
    head_r = 0.22 * scale
    ax.add_patch(patches.Circle((x, y + 0.55 * scale), head_r, facecolor="#FFFFFF", edgecolor="#000000", lw=1.6, zorder=6))
    ax.plot([x, x], [y + 0.33 * scale, y - 0.25 * scale], color="#000000", lw=1.6, zorder=6)
    ax.plot([x - 0.32 * scale, x + 0.32 * scale], [y + 0.15 * scale, y + 0.15 * scale], color="#000000", lw=1.6, zorder=6)
    ax.plot([x, x - 0.28 * scale], [y - 0.25 * scale, y - 0.72 * scale], color="#000000", lw=1.6, zorder=6)
    ax.plot([x, x + 0.28 * scale], [y - 0.25 * scale, y - 0.72 * scale], color="#000000", lw=1.6, zorder=6)
    if label:
        ax.text(x, y - 0.90 * scale, label, ha="center", va="top", fontsize=10, fontweight="bold", color="#000000", zorder=6)


def draw_oval(ax, x, y, w, h, text, fill="#FFFFFF", lw=1.4, fontsize=8.8, subtext=None):
    ellipse = patches.Ellipse((x, y), width=w, height=h, facecolor=fill, edgecolor="#000000", lw=lw, zorder=4)
    ax.add_patch(ellipse)
    if subtext:
        ax.text(x, y + 0.11, text, ha="center", va="center", fontsize=fontsize, fontweight="bold", color="#000000", zorder=5)
        ax.text(x, y - 0.13, subtext, ha="center", va="center", fontsize=fontsize - 0.8, style="italic", color="#222222", zorder=5)
    else:
        ax.text(x, y, text, ha="center", va="center", fontsize=fontsize, fontweight="bold", color="#000000", linespacing=1.2, zorder=5)


def draw_generalization_arrow(ax, x1, y1, x2, y2):
    """Draw a line with a hollow triangle head at (x2, y2) per UML Generalization standard."""
    ax.annotate(
        "", xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(arrowstyle="-|>,head_length=0.7,head_width=0.45", facecolor="#FFFFFF", edgecolor="#000000", lw=1.4),
        zorder=5
    )


def build_white_paper_version():
    fig, ax = plt.subplots(figsize=(12.5, 8.8), dpi=300)
    ax.set_xlim(0, 12.5)
    ax.set_ylim(0, 9.0)
    ax.axis("off")

    # System Boundary (Sharp Rectangle, Monochrome)
    bx, by, bw, bh = 2.15, 0.65, 7.65, 7.95
    ax.add_patch(patches.Rectangle((bx, by), bw, bh, facecolor="#FFFFFF", edgecolor="#000000", lw=1.6, zorder=1))
    ax.text(bx + bw / 2, by + bh - 0.32, "Sistem: Master Coordinator", ha="center", va="center", fontsize=11.5, fontweight="bold", color="#000000")

    # Left Human Actors
    admin_x, admin_y = 1.05, 6.25
    guest_x, guest_y = 1.05, 2.35
    draw_stick_actor(ax, admin_x, admin_y, "Administrator", scale=0.88)
    draw_stick_actor(ax, guest_x, guest_y, "Pengguna Tamu", scale=0.88)

    # Generalization arrow from Administrator to Pengguna Tamu
    draw_generalization_arrow(ax, admin_x, admin_y - 1.25, guest_x, guest_y + 0.82)

    # Left Column Use Cases (Triggered by Actors)
    c1_x = 3.95
    c1_w, c1_h = 2.85, 0.68

    uc_login_admin = (c1_x, 7.65, "Masuk sebagai\nadministrator")
    uc_kelola_tamu = (c1_x, 6.80, "Kelola akses tamu")
    uc_simulasi = (c1_x, 5.95, "Simulasi matikan /\nnyalakan node")
    uc_hapus = (c1_x, 5.10, "Hapus berkas")

    uc_lihat_node = (c1_x, 4.20, "Lihat status node")
    uc_lihat_berkas = (c1_x, 3.30, "Lihat daftar berkas\n& lokasi replika")
    uc_unggah = (c1_x, 2.40, "Unggah berkas")
    uc_unduh = (c1_x, 1.55, "Unduh berkas")
    uc_masuk_tamu = (c1_x, 0.92 + 0.05, "Masuk sebagai tamu")

    # Adjust y slightly so all 9 ovals fit with generous margin inside [0.65, 8.60]
    left_ucs = [
        ("login_admin", c1_x, 7.72, "Masuk sebagai\nadministrator"),
        ("kelola_tamu", c1_x, 6.92, "Kelola akses tamu"),
        ("simulasi", c1_x, 6.12, "Simulasi matikan /\nnyalakan node"),
        ("hapus", c1_x, 5.32, "Hapus berkas"),
        ("lihat_node", c1_x, 4.42, "Lihat status node"),
        ("lihat_berkas", c1_x, 3.56, "Lihat daftar berkas\n& lokasi replika"),
        ("unggah", c1_x, 2.70, "Unggah berkas"),
        ("unduh", c1_x, 1.90, "Unduh berkas"),
        ("masuk_tamu", c1_x, 1.10, "Masuk sebagai tamu"),
    ]
    uc_map = {}
    for k, x, y, txt in left_ucs:
        draw_oval(ax, x, y, c1_w, 0.64, txt, fill="#FFFFFF", fontsize=8.8)
        uc_map[k] = (x, y)

    # Right Column Use Cases (Internal System Processes - Shaded Light Gray for Monochrome)
    c2_x = 8.05
    c2_w = 2.75
    right_ucs = [
        ("hapus_salinan", c2_x, 5.32, "Hapus salinan\npada node", None),
        ("heartbeat", c2_x, 4.42, "Pantau heartbeat\nnode", None),
        ("pilih_node", c2_x, 3.56, "Pilih 2 dari 3 node", "(least-loaded)"),
        ("replikasi", c2_x, 2.70, "Replikasi berkas", None),
        ("failover", c2_x, 1.90, "Failover unduhan", "[node utama mati]"),
    ]
    for k, x, y, txt, sub in right_ucs:
        draw_oval(ax, x, y, c2_w, 0.66, txt, fill="#EAEAEA", fontsize=8.6, subtext=sub)
        uc_map[k] = (x, y)

    # Associations from Administrator
    for k in ["login_admin", "kelola_tamu", "simulasi", "hapus"]:
        ux, uy = uc_map[k]
        ax.plot([admin_x + 0.30, ux - c1_w / 2], [admin_y + 0.15, uy], color="#000000", lw=1.2, zorder=2)

    # Associations from Pengguna Tamu
    for k in ["lihat_node", "lihat_berkas", "unggah", "unduh", "masuk_tamu"]:
        ux, uy = uc_map[k]
        ax.plot([guest_x + 0.30, ux - c1_w / 2], [guest_y + 0.10, uy], color="#000000", lw=1.2, zorder=2)

    # Dashed Include / Extend Arrows
    def dashed_arrow(x1, y1, x2, y2, label, lx, ly):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", color="#000000", lw=1.25, ls="--"), zorder=5)
        ax.text(lx, ly, label, ha="center", va="center", fontsize=8.0, style="italic", color="#000000")

    # Hapus berkas --<<include>>--> Hapus salinan pada node
    dashed_arrow(c1_x + c1_w / 2, 5.32, c2_x - c2_w / 2, 5.32, "«include»", (c1_x + c2_x) / 2, 5.50)
    # Lihat status node --<<include>>--> Pantau heartbeat node
    dashed_arrow(c1_x + c1_w / 2, 4.42, c2_x - c2_w / 2, 4.42, "«include»", (c1_x + c2_x) / 2, 4.60)
    # Unggah berkas --<<include>>--> Replikasi berkas
    dashed_arrow(c1_x + c1_w / 2, 2.70, c2_x - c2_w / 2, 2.70, "«include»", (c1_x + c2_x) / 2, 2.88)
    # Replikasi berkas --<<include>>--> Pilih 2 dari 3 node (least-loaded)
    dashed_arrow(c2_x, 2.70 + 0.33, c2_x, 3.56 - 0.33, "«include»", c2_x + 0.52, 3.13)
    # Failover unduhan --<<extend>>--> Unduh berkas
    dashed_arrow(c2_x - c2_w / 2, 1.90, c1_x + c1_w / 2, 1.90, "«extend»", (c1_x + c2_x) / 2, 2.08)

    # Right Side: «system» Storage Node (Sharp Rectangle) + Node 1, Node 2, Node 3
    sn_x, sn_y, sn_w, sn_h = 10.45, 3.00, 1.75, 1.15
    ax.add_patch(patches.Rectangle((sn_x, sn_y), sn_w, sn_h, facecolor="#E5E5E5", edgecolor="#000000", lw=1.5, zorder=4))
    ax.text(sn_x + sn_w / 2, sn_y + 0.72, "«system»", ha="center", va="center", fontsize=8.5, style="italic", color="#222222", zorder=5)
    ax.text(sn_x + sn_w / 2, sn_y + 0.38, "Storage Node", ha="center", va="center", fontsize=9.8, fontweight="bold", color="#000000", zorder=5)

    # Connect internal use cases (plus Simulasi matikan/nyalakan node) to «system» Storage Node
    for k in ["hapus_salinan", "heartbeat", "pilih_node", "replikasi", "failover"]:
        ux, uy = uc_map[k]
        ax.plot([ux + c2_w / 2, sn_x], [uy, sn_y + sn_h / 2], color="#000000", lw=1.15, zorder=2)

    # Node 1, Node 2, Node 3 specialization boxes below «system» Storage Node
    child_nodes = [
        (10.45, 1.95, 1.75, 0.45, "Node 1"),
        (10.45, 1.35, 1.75, 0.45, "Node 2"),
        (10.45, 0.75, 1.75, 0.45, "Node 3"),
    ]
    for nx, ny, nw, nh, ntxt in child_nodes:
        ax.add_patch(patches.Rectangle((nx, ny), nw, nh, facecolor="#F5F5F5", edgecolor="#000000", lw=1.3, zorder=4))
        ax.text(nx + nw / 2, ny + nh / 2, ntxt, ha="center", va="center", fontsize=9.2, fontweight="bold", color="#000000", zorder=5)
        # Branch line to vertical spine at x = 10.22
        ax.plot([10.22, nx], [ny + nh / 2, ny + nh / 2], color="#000000", lw=1.2, zorder=3)

    # Vertical spine from Node 3 up to y = 2.62, then right to x = 11.32, then generalization arrow up to Storage Node bottom
    ax.plot([10.22, 10.22], [0.75 + 0.225, 2.62], color="#000000", lw=1.2, zorder=3)
    ax.plot([10.22, sn_x + sn_w / 2], [2.62, 2.62], color="#000000", lw=1.2, zorder=3)
    draw_generalization_arrow(ax, sn_x + sn_w / 2, 2.62, sn_x + sn_w / 2, sn_y)

    # Bottom Legend Strip
    ax.add_patch(patches.Ellipse((1.65, 0.25), 0.45, 0.24, facecolor="#FFFFFF", edgecolor="#000000", lw=1.2))
    ax.text(2.00, 0.25, "Dipicu aktor", ha="left", va="center", fontsize=8.8)

    ax.add_patch(patches.Ellipse((3.95, 0.25), 0.45, 0.24, facecolor="#EAEAEA", edgecolor="#000000", lw=1.2))
    ax.text(4.30, 0.25, "Internal sistem", ha="left", va="center", fontsize=8.8)

    ax.annotate("", xy=(7.15, 0.25), xytext=(6.55, 0.25), arrowprops=dict(arrowstyle="->", color="#000000", lw=1.2, ls="--"))
    ax.text(7.25, 0.25, "include / extend", ha="left", va="center", fontsize=8.8)

    draw_generalization_arrow(ax, 9.55, 0.25, 10.05, 0.25)
    ax.text(10.15, 0.25, "generalisasi", ha="left", va="center", fontsize=8.8)

    plt.tight_layout()
    plt.savefig("diagrams/use_case_diagram_monochrome.png", bbox_inches="tight", facecolor="#FFFFFF")
    plt.close()
    print("[OK] Saved diagrams/use_case_diagram_monochrome.png")


if __name__ == "__main__":
    build_white_paper_version()
