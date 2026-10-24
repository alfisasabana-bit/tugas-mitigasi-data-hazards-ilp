
# ============================================================
# WAW (WRITE AFTER WRITE) HAZARD SIMULATOR
# Simulasi Dependensi WAW pada Instruction-Level Parallelism
# ============================================================

from dataclasses import dataclass
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import networkx as nx
import os


# 1. DEFINISI INSTRUKSI
@dataclass
class Instruction:
    name: str
    destination: str
    sources: list


# 2. INSTRUCTION SET
instructions = [
    Instruction("I1", "R1", ["R2", "R3"]),
    Instruction("I2", "R4", ["R5", "R6"]),
    Instruction("I3", "R1", ["R7", "R8"]),
    Instruction("I4", "R4", ["R9", "R10"]),
]


# 3. PEMERIKSAAN DEPENDENSI WAW
def has_waw_dependency(inst1, inst2):
    return inst1.destination == inst2.destination


# 4. ANALISIS DEPENDENSI WAW
def show_waw_dependencies(instructions):
    print("=" * 55)
    print("WAW (WRITE AFTER WRITE) DEPENDENCY ANALYSIS")
    print("=" * 55)

    graph = nx.DiGraph()
    dependencies = []

    # Membuat node instruksi
    for inst in instructions:
        label = (
            f"{inst.name}\n"
            f"{inst.destination} = {' + '.join(inst.sources)}"
        )
        graph.add_node(inst.name, label=label)

    # Mencari dependensi WAW
    for i in range(len(instructions)):
        for j in range(i + 1, len(instructions)):
            first = instructions[i]
            second = instructions[j]

            if has_waw_dependency(first, second):
                dependencies.append(
                    (first.name, second.name, first.destination)
                )
                graph.add_edge(first.name, second.name)

                print(
                    f"{first.name} -> {second.name}: "
                    f"WAW pada register {first.destination}"
                )

    if not dependencies:
        print("Tidak ditemukan dependensi WAW.")

    print("\nDaftar instruksi:")
    for inst in instructions:
        print(
            f"{inst.name}: {inst.destination} = "
            f"{' + '.join(inst.sources)}"
        )

    print(f"\nTotal dependensi WAW: {len(dependencies)}")

    # 5. MEMBUAT DEPENDENCY GRAPH
    pos = {
        "I1": (0, 1),
        "I2": (0, -1),
        "I3": (3, 1),
        "I4": (3, -1),
    }

    labels = nx.get_node_attributes(graph, "label")

    edge_labels = {
        (first, second): f"WAW ({register})"
        for first, second, register in dependencies
    }

    plt.figure(figsize=(12, 6))

    nx.draw_networkx_nodes(
        graph,
        pos,
        node_size=3500,
        node_color="lightblue",
        node_shape="s",
        edgecolors="black",
    )

    nx.draw_networkx_labels(
        graph,
        pos,
        labels=labels,
        font_size=9,
        font_weight="bold",
    )

    nx.draw_networkx_edges(
        graph,
        pos,
        arrows=True,
        arrowstyle="-|>",
        arrowsize=20,
        node_size=3500,
        edge_color="black",
    )

    nx.draw_networkx_edge_labels(
        graph,
        pos,
        edge_labels=edge_labels,
        font_size=9,
    )

    plt.title("WAW Dependency Graph", fontsize=14)
    plt.axis("off")
    plt.tight_layout()

    # 6. MENYIMPAN GRAFIK KE FOLDER WAW
    output_dir = "WAW"
    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(output_dir, "grafik_waw.png")
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"\nGrafik berhasil disimpan: {output_file}")


# 7. MENJALANKAN PROGRAM
if __name__ == "__main__":
    show_waw_dependencies(instructions)
