
# ============================================================
# RAW (READ AFTER WRITE) HAZARD SIMULATOR
# Simulasi Dependensi RAW pada Instruction-Level Parallelism
# ============================================================

from dataclasses import dataclass
import matplotlib.pyplot as plt
import networkx as nx


# ============================================================
# 1. DEFINISI INSTRUKSI
# ============================================================

@dataclass
class Instruction:
    name: str
    destination: str
    sources: list


# ============================================================
# 2. INSTRUCTION SET
# ============================================================

instructions = [
    Instruction("I1", "R1", ["R2", "R3"]),
    Instruction("I2", "R4", ["R1", "R5"]),
    Instruction("I3", "R6", ["R4", "R7"]),
    Instruction("I4", "R8", ["R9", "R10"]),
]


# ============================================================
# 3. PEMERIKSAAN DEPENDENSI RAW
# ============================================================

def has_raw_dependency(inst1, inst2):
    """
    RAW terjadi jika instruksi kedua membaca
    register yang ditulis instruksi pertama.
    """
    return inst1.destination in inst2.sources


# ============================================================
# 4. ANALISIS DEPENDENSI
# ============================================================

def show_raw(instructions):

    print("=" * 60)
    print("RAW (READ AFTER WRITE) DEPENDENCY ANALYSIS")
    print("=" * 60)

    graph = nx.DiGraph()
    dependencies = []

    # Menambahkan node untuk setiap instruksi
    for inst in instructions:
        label = (
            f"{inst.name}\n"
            f"{inst.destination} = "
            f"{' + '.join(inst.sources)}"
        )
        graph.add_node(inst.name, label=label)

    # Memeriksa dependensi antar-instruksi
    for i in range(len(instructions)):
        for j in range(i + 1, len(instructions)):

            first = instructions[i]
            second = instructions[j]

            if has_raw_dependency(first, second):

                dependencies.append(
                    (first.name, second.name, first.destination)
                )

                graph.add_edge(
                    first.name,
                    second.name,
                    register=first.destination
                )

                print(
                    f"{first.name} -> {second.name}: "
                    f"RAW pada register {first.destination}"
                )

    if not dependencies:
        print("Tidak ditemukan dependensi RAW.")

    # Menampilkan daftar instruksi
    print("\nDaftar Instruksi:")

    for inst in instructions:
        print(
            f"{inst.name}: {inst.destination} = "
            f"{' + '.join(inst.sources)}"
        )

    print(f"\nTotal dependensi RAW: {len(dependencies)}")

    # ========================================================
    # 5. VISUALISASI DEPENDENCY GRAPH
    # ========================================================

    # Posisi node dibuat manual agar rapi
    pos = {
        "I1": (0, 1),
        "I2": (2, 1),
        "I3": (4, 1),
        "I4": (2, -1)
    }

    labels = nx.get_node_attributes(graph, "label")

    plt.figure(figsize=(12, 5))

    # Menggambar node berbentuk kotak
    nx.draw_networkx_nodes(
        graph,
        pos,
        node_color="lightblue",
        node_shape="s",
        node_size=5000,
        edgecolors="black",
        linewidths=1.5
    )

    # Menampilkan label instruksi
    nx.draw_networkx_labels(
        graph,
        pos,
        labels=labels,
        font_size=9,
        font_weight="bold"
    )

    # Menggambar panah dependensi
    nx.draw_networkx_edges(
        graph,
        pos,
        edgelist=list(graph.edges()),
        arrows=True,
        arrowstyle="-|>",
        arrowsize=25,
        edge_color="black",
        width=1.8,
        node_size=5000,
        connectionstyle="arc3,rad=0.0"
    )

    plt.title(
        "RAW (Read After Write) Dependency Graph",
        fontsize=14,
        fontweight="bold",
        pad=20
    )

    plt.xlim(-1.5, 5.5)
    plt.ylim(-2, 2)
    plt.axis("off")
    plt.tight_layout()
    plt.show()


# ============================================================
# 6. MENJALANKAN PROGRAM
# ============================================================

if __name__ == "__main__":
    show_raw(instructions)
