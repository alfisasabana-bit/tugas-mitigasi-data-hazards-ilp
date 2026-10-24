
# WAW (WRITE AFTER WRITE) HAZARD SIMULATOR
# Based on the ILP simulator from the lecturer

from dataclasses import dataclass
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx


@dataclass
class Instruction:
    name: str
    destination: str
    sources: list


# -------------------------------------------------
# INSTRUCTION SET BEFORE MITIGATION
# I5 and I6 write to the same register: R11
# -------------------------------------------------

instructions = [
    Instruction("I1", "R1", ["R2", "R3"]),
    Instruction("I2", "R4", ["R5", "R6"]),
    Instruction("I3", "R7", ["R1", "R4"]),
    Instruction("I4", "R8", ["R9", "R10"]),
    Instruction("I5", "R11", ["R7", "R8"]),
    Instruction("I6", "R11", ["R13", "R14"]),
]


# -------------------------------------------------
# CHECK WAW DEPENDENCY
# -------------------------------------------------

def has_dependency(inst1, inst2):
    # WAW: two instructions write to the same destination
    return inst1.destination == inst2.destination


def find_dependencies(instruction_list):
    dependencies = []

    for i in range(len(instruction_list)):
        for j in range(i + 1, len(instruction_list)):
            first = instruction_list[i]
            second = instruction_list[j]

            if has_dependency(first, second):
                dependencies.append(
                    (first.name, second.name, first.destination)
                )

    return dependencies


# -------------------------------------------------
# DRAW DEPENDENCY GRAPH
# -------------------------------------------------

def draw_dependency_graph(instruction_list, dependencies, filename, title):
    graph = nx.DiGraph()

    for inst in instruction_list:
        label = (
            f"{inst.name}\n"
            f"{inst.destination} = {' + '.join(inst.sources)}"
        )
        graph.add_node(inst.name, label=label)

    for first, second, register in dependencies:
        graph.add_edge(first, second, register=register)

    positions = {
        inst.name: (index % 3, -(index // 3))
        for index, inst in enumerate(instruction_list)
    }

    labels = nx.get_node_attributes(graph, "label")
    edge_labels = {
        (first, second): f"WAW ({register})"
        for first, second, register in dependencies
    }

    plt.figure(figsize=(11, 6))
    nx.draw_networkx_nodes(
        graph, positions,
        node_size=3000,
        node_color="lightblue",
        edgecolors="black"
    )
    nx.draw_networkx_labels(
        graph, positions, labels=labels, font_size=9
    )
    nx.draw_networkx_edges(
        graph, positions,
        arrows=True,
        arrowstyle="-|>",
        arrowsize=20
    )

    if edge_labels:
        nx.draw_networkx_edge_labels(
            graph, positions,
            edge_labels=edge_labels,
            font_size=9
        )

    plt.title(title)
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"Dependency graph saved: {filename}")


# -------------------------------------------------
# SEQUENTIAL EXECUTION
# -------------------------------------------------

def sequential_execution(instruction_list):
    print("\n" + "=" * 50)
    print("SEQUENTIAL EXECUTION")
    print("=" * 50)

    for cycle, inst in enumerate(instruction_list, start=1):
        print(
            f"Cycle {cycle}: Executing {inst.name} "
            f"({inst.destination} = {' + '.join(inst.sources)})"
        )

    print(f"\nTotal Sequential Cycles: {len(instruction_list)}")
    return len(instruction_list)


# -------------------------------------------------
# PARALLEL EXECUTION BASED ON WAW
# -------------------------------------------------

def parallel_execution(instruction_list):
    print("\n" + "=" * 50)
    print("INSTRUCTION-LEVEL PARALLEL EXECUTION (WAW)")
    print("=" * 50)

    completed = set()
    remaining = instruction_list.copy()
    cycle = 0

    while remaining:
        cycle += 1
        current_cycle = []

        for inst in remaining:
            dependencies_satisfied = True

            for previous in instruction_list:
                if previous.name == inst.name:
                    break

                if has_dependency(previous, inst):
                    if previous.name not in completed:
                        dependencies_satisfied = False
                        break

            if dependencies_satisfied:
                current_cycle.append(inst)

        if not current_cycle:
            raise RuntimeError("No instruction can be executed.")

        print(f"\nCycle {cycle}:")

        for inst in current_cycle:
            print(
                f"  -> {inst.name}: "
                f"{inst.destination} = {' + '.join(inst.sources)}"
            )

        for inst in current_cycle:
            completed.add(inst.name)
            remaining.remove(inst)

    print(f"\nTotal ILP Cycles: {cycle}")
    return cycle


# -------------------------------------------------
# DEPENDENCY ANALYSIS
# -------------------------------------------------

def show_dependencies(instruction_list):
    print("\n" + "=" * 50)
    print("WAW DEPENDENCY ANALYSIS")
    print("=" * 50)

    dependencies = find_dependencies(instruction_list)

    if dependencies:
        for first, second, register in dependencies:
            print(
                f"{first} -> {second}: "
                f"WAW on register {register}"
            )
    else:
        print("No WAW dependencies found.")

    print(f"Total WAW dependencies: {len(dependencies)}")
    return dependencies


# -------------------------------------------------
# MAIN PROGRAM
# -------------------------------------------------

def main():
    os.makedirs("WAW", exist_ok=True)

    print("\n" + "*" * 60)
    print("      INSTRUCTION-LEVEL PARALLELISM SIMULATOR")
    print("                   WAW HAZARD")
    print("*" * 60)

    print("\nInstruction Set:")

    for inst in instructions:
        print(
            f"{inst.name}: {inst.destination} = "
            f"{' + '.join(inst.sources)}"
        )

    # Before mitigation
    dependencies_before = show_dependencies(instructions)

    draw_dependency_graph(
        instructions,
        dependencies_before,
        "WAW/waw_sebelum_mitigasi.png",
        "WAW Dependency Graph Before Mitigation"
    )

    sequential_cycles = sequential_execution(instructions)
    parallel_cycles = parallel_execution(instructions)

    speedup = sequential_cycles / parallel_cycles
    efficiency = speedup / len(instructions) * 100

    print("\n" + "=" * 50)
    print("PERFORMANCE COMPARISON")
    print("=" * 50)
    print(f"Sequential Cycles : {sequential_cycles}")
    print(f"ILP Cycles        : {parallel_cycles}")
    print(f"Speedup           : {speedup:.2f}x")
    print(f"ILP Efficiency    : {efficiency:.2f}%")

    # After mitigation: rename I6 destination from R11 to R12
    instructions_after = [
        Instruction(inst.name, inst.destination, inst.sources.copy())
        for inst in instructions
    ]
    instructions_after[-1].destination = "R12"

    print("\n" + "=" * 50)
    print("AFTER REGISTER RENAMING")
    print("=" * 50)

    dependencies_after = show_dependencies(instructions_after)

    draw_dependency_graph(
        instructions_after,
        dependencies_after,
        "WAW/waw_setelah_mitigasi.png",
        "WAW Dependency Graph After Register Renaming"
    )

    # Compare the number of WAW dependencies
    labels = ["Before Mitigation", "After Mitigation"]
    values = [len(dependencies_before), len(dependencies_after)]

    plt.figure(figsize=(8, 5))
    bars = plt.bar(labels, values)
    plt.title("WAW Dependency Comparison")
    plt.ylabel("Number of WAW Dependencies")
    plt.ylim(0, max(values + [1]) + 1)
    plt.bar_label(bars, padding=3)
    plt.tight_layout()
    plt.savefig(
        "WAW/grafik_perbandingan_waw.png",
        dpi=300,
        bbox_inches="tight"
    )
    plt.close()

    print("\nWAW analysis completed.")


if __name__ == "__main__":
    main()
