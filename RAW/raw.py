
# RAW (READ AFTER WRITE) HAZARD SIMULATOR

from dataclasses import dataclass
import matplotlib.pyplot as plt
import networkx as nx


@dataclass
class Instruction:
    name: str
    destination: str
    sources: list


instructions = [
    Instruction("I1", "R1", ["R2", "R3"]),
    Instruction("I2", "R4", ["R1", "R5"]),
    Instruction("I3", "R6", ["R4", "R7"]),
    Instruction("I4", "R8", ["R9", "R10"]),
]


def has_raw_dependency(inst1, inst2):
    return inst1.destination in inst2.sources


def show_raw(instructions):
    print("=" * 50)
    print("RAW DEPENDENCY ANALYSIS")
    print("=" * 50)

    graph = nx.DiGraph()
    dependencies = []

    for inst in instructions:
        label = (
            f"{inst.name}\n"
            f"{inst.destination} = {' + '.join(inst.sources)}"
        )
        graph.add_node(inst.name, label=label)

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

    print(f"\nTotal dependensi RAW: {len(dependencies)}")

    pos = {
        "I1": (0, 1),
        "I2": (2, 1),
        "I3": (4, 1),
        "I4": (2, -1)
    }

    labels = nx.get_node_attributes(graph, "label")

    plt.figure(figsize=(12, 5))

    nx.draw_networkx_nodes(
        graph, pos,
        node_color="lightblue",
        node_shape="s",
        node_size=5000,
        edgecolors="black"
    )

    nx.draw_networkx_labels(
        graph, pos,
        labels=labels,
        font_size=9,
        font_weight="bold"
    )

    nx.draw_networkx_edges(
        graph, pos,
        arrows=True,
        arrowstyle="-|>",
        arrowsize=25,
        node_size=5000
    )

    edge_labels = {
        (source, target): data["register"]
        for source, target, data in graph.edges(data=True)
    }

    nx.draw_networkx_edge_labels(
        graph, pos,
        edge_labels=edge_labels,
        font_color="red"
    )

    plt.title("RAW Dependency Graph")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(
        "raw_dependency_graph.png",
        dpi=300,
        bbox_inches="tight"
    )
    plt.show()

    print("\nGrafik disimpan sebagai raw_dependency_graph.png")


if __name__ == "__main__":
    show_raw(instructions)
