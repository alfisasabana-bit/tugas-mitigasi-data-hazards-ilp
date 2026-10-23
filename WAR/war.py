
# ==============================================================
# TUGAS: MITIGASI DATA HAZARDS PADA INSTRUCTION-LEVEL PARALLELISM
# JENIS HAZARD: WAR (WRITE AFTER READ)
# ==============================================================
#
# Fitur:
# 1. Deteksi dependensi WAR secara otomatis.
# 2. Analisis pasangan instruksi dan register yang terlibat.
# 3. Visualisasi dependency graph.
# 4. Grafik statistik dependensi.
# 5. Simulasi mitigasi menggunakan register renaming.
# 6. Perbandingan sebelum dan sesudah mitigasi.
# 7. Penyimpanan grafik dan laporan hasil analisis.
#
# Instalasi:
# pip install matplotlib networkx
# ==============================================================

from dataclasses import dataclass
from pathlib import Path
import csv
import matplotlib.pyplot as plt
import networkx as nx


# ==============================================================
# 1. KONFIGURASI
# ==============================================================

OUTPUT_DIR = Path(__file__).resolve().parent

plt.rcParams.update({
    "figure.dpi": 120,
    "savefig.dpi": 220,
    "font.size": 10,
    "axes.titlesize": 14,
    "axes.labelsize": 10,
})


# ==============================================================
# 2. DEFINISI INSTRUKSI
# ==============================================================

@dataclass
class Instruction:
    name: str
    destination: str
    sources: list[str]
    operation: str = "ADD"

    def __str__(self):
        return (
            f"{self.name}: {self.destination} = "
            f"{self.operation}({', '.join(self.sources)})"
        )


# Contoh instruction set untuk pengujian WAR.
# I1 membaca R2, kemudian I3 menulis R2.
# Kondisi tersebut menghasilkan dependensi WAR I1 -> I3.

instructions = [
    Instruction("I1", "R1", ["R2", "R3"], "ADD"),
    Instruction("I2", "R4", ["R5", "R6"], "SUB"),
    Instruction("I3", "R2", ["R7", "R8"], "MUL"),
]


# ==============================================================
# 3. DETEKSI DEPENDENSI WAR
# ==============================================================

def detect_war(inst1, inst2):
    """
    WAR terjadi jika:
    - Instruksi pertama membaca suatu register.
    - Instruksi berikutnya menulis register yang sama.

    Pasangan diperiksa berdasarkan urutan instruksi.
    """

    shared_registers = sorted(
        set(inst1.sources) & {inst2.destination}
    )

    return shared_registers


def analyze_war(instruction_list):
    """Menghasilkan daftar seluruh dependensi WAR."""

    dependencies = []

    for i, first in enumerate(instruction_list):
        for second in instruction_list[i + 1:]:
            registers = detect_war(first, second)

            for register in registers:
                dependencies.append({
                    "reader": first.name,
                    "writer": second.name,
                    "register": register,
                    "reader_instruction": str(first),
                    "writer_instruction": str(second),
                })

    return dependencies


# ==============================================================
# 4. MEMBANGUN DEPENDENCY GRAPH
# ==============================================================

def build_graph(instruction_list, dependencies):
    graph = nx.DiGraph()

    for inst in instruction_list:
        graph.add_node(
            inst.name,
            label=(
                f"{inst.name}\n"
                f"{inst.destination} = "
                f"{inst.operation}("
                f"{', '.join(inst.sources)})"
            )
        )

    for dep in dependencies:
        source = dep["reader"]
        target = dep["writer"]

        if graph.has_edge(source, target):
            graph[source][target]["registers"].append(
                dep["register"]
            )
        else:
            graph.add_edge(
                source,
                target,
                registers=[dep["register"]]
            )

    return graph


# ==============================================================
# 5. VISUALISASI DEPENDENCY GRAPH
# ==============================================================

def plot_dependency_graph(graph, title, filename):
    fig, ax = plt.subplots(figsize=(11, 6))

    # Posisi berdasarkan urutan instruksi.
    positions = {
        node: (index * 2.5, 0)
        for index, node in enumerate(graph.nodes())
    }

    labels = nx.get_node_attributes(graph, "label")

    nx.draw_networkx_nodes(
        graph,
        positions,
        node_size=4600,
        node_color="#DCEBFA",
        edgecolors="#2563A6",
        linewidths=2,
        ax=ax
    )

    nx.draw_networkx_labels(
        graph,
        positions,
        labels=labels,
        font_size=9,
        font_weight="bold",
        font_color="#16324F",
        ax=ax
    )

    nx.draw_networkx_edges(
        graph,
        positions,
        arrows=True,
        arrowstyle="-|>",
        arrowsize=24,
        width=2.5,
        edge_color="#D9485F",
        connectionstyle="arc3,rad=0.12",
        node_size=4600,
        min_source_margin=15,
        min_target_margin=15,
        ax=ax
    )

    edge_labels = {
        (u, v): "WAR: " + ", ".join(data["registers"])
        for u, v, data in graph.edges(data=True)
    }

    if edge_labels:
        nx.draw_networkx_edge_labels(
            graph,
            positions,
            edge_labels=edge_labels,
            font_size=9,
            font_color="#B42336",
            label_pos=0.5,
            rotate=False,
            ax=ax
        )

    if graph.number_of_edges() == 0:
        ax.text(
            0.5, 0.48,
            "Tidak ditemukan dependensi WAR",
            transform=ax.transAxes,
            ha="center",
            fontsize=12,
            color="#247A55"
        )

    ax.set_title(title, fontweight="bold", pad=22)
    ax.text(
        0.5, -0.12,
        "Panah menunjukkan urutan dependensi: instruksi pembaca → penulis",
        transform=ax.transAxes,
        ha="center",
        fontsize=9,
        color="#555555"
    )
    ax.axis("off")

    fig.tight_layout()
    fig.savefig(
        OUTPUT_DIR / filename,
        bbox_inches="tight",
        facecolor="white"
    )
    plt.show()
    plt.close(fig)


# ==============================================================
# 6. GRAFIK STATISTIK
# ==============================================================

def plot_statistics(instruction_list, dependencies):
    read_registers = {
        register
        for inst in instruction_list
        for register in inst.sources
    }

    written_registers = {
        inst.destination for inst in instruction_list
    }

    unique_war_registers = {
        dep["register"] for dep in dependencies
    }

    categories = [
        "Jumlah instruksi",
        "Register dibaca",
        "Register ditulis",
        "Dependensi WAR",
        "Register terdampak",
    ]

    values = [
        len(instruction_list),
        len(read_registers),
        len(written_registers),
        len(dependencies),
        len(unique_war_registers),
    ]

    fig, ax = plt.subplots(figsize=(10, 5.5))

    bars = ax.barh(
        categories,
        values,
        color=["#4776A8", "#62A6D8", "#78BFA5",
               "#E66B6B", "#E6AD55"],
        edgecolor="white",
        height=0.62
    )

    ax.bar_label(
        bars,
        labels=[str(value) for value in values],
        padding=7,
        fontsize=10,
        fontweight="bold"
    )

    ax.set_title(
        "Statistik Analisis Instruction-Level Parallelism",
        fontweight="bold",
        pad=18
    )
    ax.set_xlabel("Jumlah")
    ax.set_xlim(0, max(values, default=0) + 2)
    ax.grid(axis="x", linestyle="--", alpha=0.3)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.tight_layout()
    fig.savefig(
        OUTPUT_DIR / "war_analysis.png",
        bbox_inches="tight",
        facecolor="white"
    )
    plt.show()
    plt.close(fig)


# ==============================================================
# 7. SIMULASI REGISTER RENAMING
# ==============================================================

def mitigate_war(instruction_list, dependencies):
    """
    Membuat salinan instruction set dan mengganti register
    tujuan instruksi penulis yang terlibat dalam WAR.

    Ini merupakan simulasi mitigasi dependensi WAR.
    Untuk program nyata, seluruh penggunaan register harus
    diperbarui sesuai pemetaan register agar semantik terjaga.
    """

    mitigated = [
        Instruction(
            inst.name,
            inst.destination,
            list(inst.sources),
            inst.operation
        )
        for inst in instruction_list
    ]

    if not dependencies:
        return mitigated, []

    affected_writers = {
        dep["writer"] for dep in dependencies
    }

    used_registers = {
        register
        for inst in mitigated
        for register in (
            inst.sources + [inst.destination]
        )
    }

    rename_log = []
    next_register_number = 1

    for inst in mitigated:
        if inst.name not in affected_writers:
            continue

        old_register = inst.destination

        while f"R{next_register_number}" in used_registers:
            next_register_number += 1

        new_register = f"R{next_register_number}"
        next_register_number += 1

        inst.destination = new_register
        used_registers.add(new_register)

        rename_log.append({
            "instruction": inst.name,
            "old_register": old_register,
            "new_register": new_register,
        })

    return mitigated, rename_log


# ==============================================================
# 8. MENYIMPAN HASIL ANALISIS
# ==============================================================

def save_results(instruction_list, dependencies, rename_log):
    csv_path = OUTPUT_DIR / "war_results.csv"

    with csv_path.open(
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:
        writer = csv.writer(file)

        writer.writerow([
            "Instruksi Pembaca",
            "Instruksi Penulis",
            "Register WAR",
            "Mitigasi"
        ])

        for dep in dependencies:
            rename = next(
                (
                    item for item in rename_log
                    if item["instruction"] == dep["writer"]
                    and item["old_register"] == dep["register"]
                ),
                None
            )

            mitigation = (
                f"Renaming {rename['old_register']} ke "
                f"{rename['new_register']}"
                if rename else "Tidak diperlukan"
            )

            writer.writerow([
                dep["reader"],
                dep["writer"],
                dep["register"],
                mitigation
            ])

    report_path = OUTPUT_DIR / "war_report.txt"

    with report_path.open("w", encoding="utf-8") as file:
        file.write("LAPORAN ANALISIS WAR\n")
        file.write("=" * 55 + "\n\n")

        file.write("DAFTAR INSTRUKSI\n")
        for inst in instruction_list:
            file.write(str(inst) + "\n")

        file.write("\nHASIL DETEKSI DEPENDENSI\n")
        if dependencies:
            for dep in dependencies:
                file.write(
                    f"{dep['reader']} -> {dep['writer']} | "
                    f"Register {dep['register']}\n"
                )
        else:
            file.write("Tidak ditemukan dependensi WAR.\n")

        file.write(f"\nTotal instruksi: {len(instruction_list)}\n")
        file.write(f"Total dependensi WAR: {len(dependencies)}\n")
        file.write(f"Total mitigasi renaming: {len(rename_log)}\n")

        file.write("\nCATATAN\n")
        file.write(
            "Register renaming pada simulasi ini mengganti "
            "register tujuan. Untuk implementasi nyata, "
            "pemetaan penggunaan register perlu dijaga.\n"
        )


# ==============================================================
# 9. PROGRAM UTAMA
# ==============================================================

def main():
    print("=" * 65)
    print(" ANALISIS WAR (WRITE AFTER READ)")
    print(" INSTRUCTION-LEVEL PARALLELISM (ILP)")
    print("=" * 65)

    print("\n[1] DAFTAR INSTRUKSI")
    for inst in instructions:
        print("  ", inst)

    dependencies = analyze_war(instructions)

    print("\n[2] HASIL DETEKSI WAR")
    if dependencies:
        for index, dep in enumerate(dependencies, start=1):
            print(
                f"  {index}. {dep['reader']} -> "
                f"{dep['writer']} | Register {dep['register']}"
            )
    else:
        print("  Tidak ditemukan dependensi WAR.")

    original_graph = build_graph(instructions, dependencies)

    print("\n[3] SIMULASI REGISTER RENAMING")
    mitigated_instructions, rename_log = mitigate_war(
        instructions, dependencies
    )

    if rename_log:
        for item in rename_log:
            print(
                f"  {item['instruction']}: "
                f"{item['old_register']} -> "
                f"{item['new_register']}"
            )
    else:
        print("  Tidak ada register yang perlu diubah.")

    remaining_dependencies = analyze_war(mitigated_instructions)

    print("\n[4] PERBANDINGAN HASIL")
    print(f"  Sebelum mitigasi : {len(dependencies)} dependensi WAR")
    print(
        f"  Setelah mitigasi : "
        f"{len(remaining_dependencies)} dependensi WAR"
    )

    if dependencies:
        reduction = (
            (len(dependencies) - len(remaining_dependencies))
            / len(dependencies)
        ) * 100

        print(f"  Pengurangan      : {reduction:.1f}%")

    print("\n[5] MEMBUAT VISUALISASI")
    plot_dependency_graph(
        original_graph,
        "WAR Dependency Graph — Sebelum Mitigasi",
        "war_dependency_graph.png"
    )

    mitigated_graph = build_graph(
        mitigated_instructions,
        remaining_dependencies
    )

    plot_dependency_graph(
        mitigated_graph,
        "WAR Dependency Graph — Setelah Mitigasi",
        "war_mitigation_graph.png"
    )

    plot_statistics(instructions, dependencies)

    save_results(instructions, dependencies, rename_log)

    print("\n[6] FILE HASIL")
    for filename in [
        "war_dependency_graph.png",
        "war_mitigation_graph.png",
        "war_analysis.png",
        "war_results.csv",
        "war_report.txt",
    ]:
        print(f"  - {OUTPUT_DIR / filename}")

    print("\nAnalisis WAR selesai.")
    print("=" * 65)


if __name__ == "__main__":
    main()
