
# =====================================================
# RAW (Read After Write) Hazard Simulator
# Simulasi dependensi RAW pada Instruction-Level Parallelism
# =====================================================

from dataclasses import dataclass
import matplotlib.pyplot as plt
import networkx as nx


@dataclass
class Instruction:
    name: str
    destination: str
    sources: list


# Instruksi untuk menguji dependensi RAW
instructions = [
    Instruction("I1", "R1", ["R2", "R3"]),
    Instruction("I2", "R4", ["R1", "R5"]),
    Instruction("I3", "R6", ["R4", "R7"]),
    Instruction("I4", "R8", ["R9", "R10"]),
]


def has_raw_dependency(inst1, inst2):
    """True jika inst2 membaca register yang ditulis inst1."""
    return inst1.destination in inst2.sources


def show_raw(instructions):
    print("=" * 55)
    print("RAW (READ AFTER WRITE) DEPENDENCY ANALYSIS")
    print("=" * 55)

    graph = nx.DiGraph()
    dependencies = []

    for inst in instructions:
        graph.add_node(
            inst.name,
            label=f"{inst.name}\n{inst.destination} = "
                  f"{' + '.join(inst.sources)}"
        )

    for i in range(len(instructions)):
        for j in range(i + 1, len(instructions)):
            first = instructions[i]
            second = instructions[j]

            if has_raw_dependency(first, second):
                dependencies.append(
                    (first.name, second.name, first.destination)
                )
                graph.add_edge(first.name, second.name)

                print(
                    f"{first.name} -> {second.name}: "
                    f"RAW pada register {first.destination}"
                )

    if not dependencies:
        print("Tidak ditemukan dependensi RAW.")

    print("\nDaftar instruksi:")
    for inst in instructions:
        print(
            f"{inst.name}: {inst.destination} = "
            f"{' + '.join(inst.sources)}"
        )

    # Membuat dependency graph
    pos = nx.spring_layout(graph, seed=42)

    labels = nx.get_node_attributes(graph, "label")

    plt.figure(figsize=(10, 6))
    nx.draw_networkx(
        graph,
        pos,
        labels=labels,
        node_color="lightblue",
        node_size=3000,
        font_size=9,
        arrows=True,
        arrowsize=20,
        edge_color="black",
        connectionstyle="arc3,rad=0.05"
    )

    plt.title("RAW Dependency Graph")
    plt.axis("off")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    show_raw(instructions)

