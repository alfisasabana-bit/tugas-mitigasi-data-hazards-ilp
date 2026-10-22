
# ============================================
# WAR (Write After Read) Hazard Simulator
# ============================================

from dataclasses import dataclass
import matplotlib.pyplot as plt
import networkx as nx


@dataclass
class Instruction:
    name: str
    destination: str
    sources: list


# Instruction set untuk menguji WAR
instructions = [
    Instruction("I1", "R1", ["R2", "R3"]),
    Instruction("I2", "R4", ["R5", "R6"]),
    Instruction("I3", "R2", ["R7", "R8"]),
]


def detect_war(inst1, inst2):
    # WAR terjadi ketika instruksi pertama membaca
    # register yang kemudian ditulis instruksi kedua.
    return inst2.destination in inst1.sources


def show_war(instructions):
    print("=" * 45)
    print("WAR DEPENDENCY ANALYSIS")
    print("=" * 45)

    graph = nx.DiGraph()

    for inst in instructions:
        label = (
            f"{inst.name}\n"
            f"{inst.destination} = "
            f"{' + '.join(inst.sources)}"
        )
        graph.add_node(inst.name, label=label)

    found = False

    for i in range(len(instructions)):
        for j in range(i + 1, len(instructions)):
            first = instructions[i]
            second = instructions[j]

            if detect_war(first, second):
                print(
                    f"{first.name} -> {second.name}: "
                    f"WAR on register {second.destination}"
                )

                graph.add_edge(first.name, second.name)
                found = True

    if not found:
        print("No WAR dependency found.")

    # Membuat dependency graph
    positions = nx.spring_layout(graph, seed=42)
    labels = nx.get_node_attributes(graph, "label")

    plt.figure(figsize=(8, 4))
    nx.draw(
        graph,
        positions,
        labels=labels,
        with_labels=True,
        node_size=2800,
        node_color="lightblue",
        arrows=True,
        arrowsize=20,
        font_size=9
    )

    plt.title("WAR Dependency Graph")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig("war_graph.png", dpi=200)
    plt.show()


if __name__ == "__main__":
    show_war(instructions)

