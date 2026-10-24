
from dataclasses import dataclass
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch


# ============================================================
# 1. KONFIGURASI DAN STRUKTUR DATA
# ============================================================

OUTPUT_DIR = Path("WAR")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class Instruction:
    name: str
    destination: str
    sources: list[str]
    operation: str


# Instruksi sebelum mitigasi
instructions_before = [
    Instruction("I1", "R1", ["R2", "R3"], "ADD"),
    Instruction("I2", "R4", ["R5", "R6"], "SUB"),
    Instruction("I3", "R2", ["R7", "R8"], "MUL"),
]


# ============================================================
# 2. DETEKSI DEPENDENSI WAR
# ============================================================

def detect_war(inst1, inst2):
    """
    WAR terjadi ketika instruksi lebih awal membaca register
    yang kemudian ditulis oleh instruksi berikutnya.
    """
    return inst2.destination in inst1.sources


def find_war_dependencies(instruction_list):
    dependencies = []

    for i, inst1 in enumerate(instruction_list):
        for inst2 in instruction_list[i + 1:]:
            if detect_war(inst1, inst2):
                dependencies.append(
                    (inst1.name, inst2.name, inst2.destination)
                )

    return dependencies


# ============================================================
# 3. MITIGASI REGISTER RENAMING
# ============================================================

def apply_register_renaming(instruction_list):
    """
    Contoh mitigasi:
    Tujuan penulisan I3 diubah dari R2 menjadi R9.

    Pada program nyata, pastikan register baru tersedia dan
    perubahan tidak mengubah hasil perhitungan program.
    """
    mitigated = []

    for inst in instruction_list:
        if inst.name == "I3":
            mitigated.append(
                Instruction(
                    name=inst.name,
                    destination="R9",
                    sources=inst.sources.copy(),
                    operation=inst.operation,
                )
            )
        else:
            mitigated.append(
                Instruction(
                    name=inst.name,
                    destination=inst.destination,
                    sources=inst.sources.copy(),
                    operation=inst.operation,
                )
            )

    return mitigated


# ============================================================
# 4. GRAPH DEPENDENSI WAR
# ============================================================

def draw_war_graph(instruction_list, title, filename):
    fig, ax = plt.subplots(figsize=(14, 7.5), dpi=180)

    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 8)
    ax.axis("off")

    fig.suptitle(
        title,
        fontsize=22,
        fontweight="bold",
        color="#142B52",
        y=0.95,
    )

    positions = {
        "I1": (2.5, 5.0),
        "I2": (7.5, 5.0),
        "I3": (12.5, 5.0),
    }

    box_width = 3.5
    box_height = 1.65

    dependencies = find_war_dependencies(instruction_list)

    # Menggambar kotak instruksi
    for inst in instruction_list:
        x, y = positions[inst.name]

        box = FancyBboxPatch(
            (x - box_width / 2, y - box_height / 2),
            box_width,
            box_height,
            boxstyle="round,pad=0.12,rounding_size=0.25",
            linewidth=2.2,
            edgecolor="#3976B9",
            facecolor="#EAF3FF",
            zorder=3,
        )
        ax.add_patch(box)

        ax.text(
            x,
            y + 0.35,
            inst.name,
            ha="center",
            va="center",
            fontsize=19,
            fontweight="bold",
            color="#16345C",
            zorder=4,
        )

        ax.text(
            x,
            y - 0.22,
            f"{inst.destination} = "
            f"{inst.operation}({', '.join(inst.sources)})",
            ha="center",
            va="center",
            fontsize=11.5,
            color="#16345C",
            zorder=4,
        )

    # Menggambar panah untuk setiap dependensi WAR
    for source_name, target_name, register in dependencies:
        x1, y1 = positions[source_name]
        x2, y2 = positions[target_name]

        arrow = FancyArrowPatch(
            (x1 + 0.85, y1 - 0.9),
            (x2 - 0.85, y2 - 0.9),
            connectionstyle="arc3,rad=0.28",
            arrowstyle="-|>",
            mutation_scale=25,
            linewidth=3,
            color="#B94752",
            zorder=2,
        )
        ax.add_patch(arrow)

        ax.text(
            (x1 + x2) / 2,
            2.85,
            f"WAR: {source_name} → {target_name}\n"
            f"Register {register}",
            ha="center",
            va="center",
            fontsize=11,
            fontweight="bold",
            color="#983844",
            bbox={
                "boxstyle": "round,pad=0.4",
                "facecolor": "#FFF1F2",
                "edgecolor": "#E4A6AC",
                "linewidth": 1.2,
            },
            zorder=5,
        )

    if dependencies:
        summary = f"Ditemukan {len(dependencies)} dependensi WAR."
        summary_color = "#983844"
    else:
        summary = "Tidak ditemukan dependensi WAR."
        summary_color = "#24764B"

    ax.text(
        7.5,
        1.55,
        summary,
        ha="center",
        va="center",
        fontsize=14,
        fontweight="bold",
        color=summary_color,
    )

    ax.text(
        7.5,
        0.85,
        "Panah menunjukkan instruksi pembaca → instruksi penulis",
        ha="center",
        va="center",
        fontsize=11,
        color="#555F6D",
    )

    fig.subplots_adjust(
        left=0.035,
        right=0.965,
        top=0.84,
        bottom=0.08,
    )

    # Simpan di folder WAR dan root repository
    fig.savefig(
        OUTPUT_DIR / filename,
        dpi=220,
        bbox_inches="tight",
        facecolor="white",
    )

    fig.savefig(
        filename,
        dpi=220,
        bbox_inches="tight",
        facecolor="white",
    )

    plt.close(fig)
    print(f"Graph berhasil dibuat: {filename}")


# ============================================================
# 5. GRAFIK BATANG PERBANDINGAN
# ============================================================

def draw_comparison_chart(before_count, after_count):
    labels = ["Sebelum Mitigasi", "Sesudah Mitigasi"]
    values = [before_count, after_count]
    colors = ["#B94752", "#39856B"]

    fig, ax = plt.subplots(figsize=(10, 6), dpi=180)

    bars = ax.bar(
        labels,
        values,
        color=colors,
        width=0.55,
        edgecolor="white",
        linewidth=1.5,
    )

    ax.set_title(
        "Perbandingan Jumlah Dependensi WAR",
        fontsize=18,
        fontweight="bold",
        color="#142B52",
        pad=20,
    )

    ax.set_ylabel("Jumlah Dependensi WAR", fontsize=12)
    ax.set_ylim(0, max(values + [1]) + 0.8)
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    ax.set_axisbelow(True)

    for bar, value in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.08,
            str(value),
            ha="center",
            va="bottom",
            fontsize=14,
            fontweight="bold",
            color="#142B52",
        )

    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)

    fig.tight_layout()

    fig.savefig(
        OUTPUT_DIR / "grafik_perbandingan_war.png",
        dpi=220,
        bbox_inches="tight",
        facecolor="white",
    )

    fig.savefig(
        "grafik_perbandingan_war.png",
        dpi=220,
        bbox_inches="tight",
        facecolor="white",
    )

    plt.close(fig)
    print("Grafik perbandingan WAR berhasil dibuat.")


# ============================================================
# 6. GRAFIK EFEKTIVITAS MITIGASI
# ============================================================

def draw_effectiveness_chart(before_count, after_count):
    if before_count > 0:
        reduction = (
            (before_count - after_count) / before_count
        ) * 100
    else:
        reduction = 0

    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=180)

    bar_color = "#39856B" if reduction >= 0 else "#B94752"

    ax.barh(
        ["Penurunan Dependensi WAR"],
        [reduction],
        color=bar_color,
        height=0.45,
    )

    ax.set_xlim(0, max(100, reduction + 10))
    ax.set_xlabel("Penurunan (%)", fontsize=12)

    ax.set_title(
        "Efektivitas Mitigasi WAR",
        fontsize=18,
        fontweight="bold",
        color="#142B52",
        pad=18,
    )

    ax.text(
        reduction + 2,
        0,
        f"{reduction:.1f}%",
        va="center",
        fontweight="bold",
        fontsize=13,
        color="#142B52",
    )

    ax.grid(axis="x", linestyle="--", alpha=0.3)
    ax.set_axisbelow(True)

    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)

    fig.tight_layout()

    fig.savefig(
        OUTPUT_DIR / "grafik_efektivitas_war.png",
        dpi=220,
        bbox_inches="tight",
        facecolor="white",
    )

    fig.savefig(
        "grafik_efektivitas_war.png",
        dpi=220,
        bbox_inches="tight",
        facecolor="white",
    )

    plt.close(fig)
    print("Grafik efektivitas WAR berhasil dibuat.")


# ============================================================
# 7. LAPORAN ANALISIS
# ============================================================

def print_analysis(title, instruction_list):
    dependencies = find_war_dependencies(instruction_list)

    print("\n" + "=" * 55)
    print(title)
    print("=" * 55)

    print("\nDaftar instruksi:")

    for inst in instruction_list:
        print(
            f"{inst.name}: {inst.destination} = "
            f"{inst.operation}({', '.join(inst.sources)})"
        )

    print("\nHasil deteksi WAR:")

    if dependencies:
        for source, target, register in dependencies:
            print(
                f"- {source} -> {target} "
                f"(register {register})"
            )
    else:
        print("- Tidak ditemukan dependensi WAR.")

    print(f"\nJumlah dependensi WAR: {len(dependencies)}")

    return dependencies


# ============================================================
# 8. PROGRAM UTAMA
# ============================================================

def main():
    print("ANALISIS WRITE AFTER READ (WAR)")

    # Analisis sebelum mitigasi
    before_dependencies = print_analysis(
        "SEBELUM MITIGASI",
        instructions_before,
    )

    draw_war_graph(
        instructions_before,
        "WAR Dependency Graph — Sebelum Mitigasi",
        "war_sebelum_mitigasi.png",
    )

    # Terapkan contoh mitigasi register renaming
    instructions_after = apply_register_renaming(
        instructions_before
    )

    # Analisis sesudah mitigasi
    after_dependencies = print_analysis(
        "SESUDAH MITIGASI (REGISTER RENAMING)",
        instructions_after,
    )

    draw_war_graph(
        instructions_after,
        "WAR Dependency Graph — Sesudah Mitigasi",
        "war_setelah_mitigasi.png",
    )

    # Buat dua grafik tambahan
    draw_comparison_chart(
        len(before_dependencies),
        len(after_dependencies),
    )

    draw_effectiveness_chart(
        len(before_dependencies),
        len(after_dependencies),
    )

    # Ringkasan akhir
    print("\n" + "=" * 55)
    print("RINGKASAN PERBANDINGAN")
    print("=" * 55)

    print(
        f"Dependensi sebelum mitigasi: "
        f"{len(before_dependencies)}"
    )
    print(
        f"Dependensi sesudah mitigasi: "
        f"{len(after_dependencies)}"
    )

    print("\nFile grafik yang dihasilkan:")

    files = [
        "war_sebelum_mitigasi.png",
        "war_setelah_mitigasi.png",
        "grafik_perbandingan_war.png",
        "grafik_efektivitas_war.png",
    ]

    for filename in files:
        print(f"- WAR/{filename}")

    print("\nSemua proses analisis selesai.")


if __name__ == "__main__":
    main()
