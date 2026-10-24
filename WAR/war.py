
from dataclasses import dataclass
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch


# ============================================================
# 1. STRUKTUR DATA INSTRUKSI
# ============================================================

@dataclass
class Instruction:
    name: str
    destination: str
    sources: list[str]
    operation: str


# Instruksi awal sebelum mitigasi
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
    WAR (Write After Read) terjadi apabila:
    - Instruksi lebih awal membaca suatu register.
    - Instruksi berikutnya menulis register yang sama.
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
# 3. MITIGASI MENGGUNAKAN REGISTER RENAMING
# ============================================================

def apply_register_renaming(instruction_list):
    """
    Contoh mitigasi:
    Tujuan penulisan I3 diubah dari R2 menjadi R9.

    Catatan:
    Register baru harus tersedia dan perubahan harus konsisten
    dengan penggunaan register pada program sebenarnya.
    """
    mitigated = []

    for inst in instruction_list:
        if inst.name == "I3":
            mitigated.append(
                Instruction(
                    inst.name,
                    "R9",
                    inst.sources.copy(),
                    inst.operation,
                )
            )
        else:
            mitigated.append(
                Instruction(
                    inst.name,
                    inst.destination,
                    inst.sources.copy(),
                    inst.operation,
                )
            )

    return mitigated


# ============================================================
# 4. VISUALISASI GRAPH WAR
# ============================================================

def draw_war_graph(instruction_list, title, output_filename):
    fig, ax = plt.subplots(figsize=(15, 8), dpi=180)

    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor("#FFFFFF")
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 8)
    ax.axis("off")

    fig.suptitle(
        title,
        fontsize=23,
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

    # --------------------------------------------------------
    # Kotak instruksi
    # --------------------------------------------------------
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
            fontsize=20,
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
            fontsize=12,
            color="#16345C",
            zorder=4,
        )

    # --------------------------------------------------------
    # Panah dependensi WAR
    # --------------------------------------------------------
    for source_name, target_name, register in dependencies:
        x1, y1 = positions[source_name]
        x2, y2 = positions[target_name]

        arrow = FancyArrowPatch(
            (x1 + 0.85, y1 - 0.9),
            (x2 - 0.85, y2 - 0.9),
            connectionstyle="arc3,rad=0.28",
            arrowstyle="-|>",
            mutation_scale=26,
            linewidth=3.2,
            color="#B94752",
            zorder=2,
        )
        ax.add_patch(arrow)

        label_x = (x1 + x2) / 2
        label_y = 2.85

        ax.text(
            label_x,
            label_y,
            f"WAR: {source_name} → {target_name}\n"
            f"Register {register}",
            ha="center",
            va="center",
            fontsize=12,
            fontweight="bold",
            color="#983844",
            bbox={
                "boxstyle": "round,pad=0.45",
                "facecolor": "#FFF1F2",
                "edgecolor": "#E4A6AC",
                "linewidth": 1.3,
            },
            zorder=5,
        )

    # --------------------------------------------------------
    # Keterangan di bawah graph
    # --------------------------------------------------------
    if dependencies:
        description = (
            f"Ditemukan {len(dependencies)} dependensi WAR."
        )
        description_color = "#983844"
    else:
        description = "Tidak ditemukan dependensi WAR."
        description_color = "#24764B"

    ax.text(
        7.5,
        1.55,
        description,
        ha="center",
        va="center",
        fontsize=14,
        fontweight="bold",
        color=description_color,
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

    # Simpan gambar di folder WAR dan root repository.
    output_dir = Path("WAR")
    output_dir.mkdir(parents=True, exist_ok=True)

    fig.savefig(
        output_dir / output_filename,
        dpi=220,
        bbox_inches="tight",
        facecolor="white",
    )

    fig.savefig(
        output_filename,
        dpi=220,
        bbox_inches="tight",
        facecolor="white",
    )

    plt.close(fig)

    print(f"Grafik berhasil dibuat: {output_filename}")


# ============================================================
# 5. LAPORAN ANALISIS
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
# 6. PROGRAM UTAMA
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

    # Ringkasan perbandingan
    print("\n" + "=" * 55)
    print("RINGKASAN PERBANDINGAN")
    print("=" * 55)
    print(f"Dependensi sebelum mitigasi: {len(before_dependencies)}")
    print(f"Dependensi sesudah mitigasi: {len(after_dependencies)}")

    if len(before_dependencies) > len(after_dependencies):
        print("Mitigasi mengurangi jumlah dependensi WAR.")
    elif len(before_dependencies) == len(after_dependencies):
        print("Jumlah dependensi WAR tidak berubah.")
    else:
        print("Jumlah dependensi WAR meningkat.")

    print("\nSemua proses analisis selesai.")


if __name__ == "__main__":
    main()
