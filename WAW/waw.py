
# ============================================================
# WAW (WRITE AFTER WRITE) HAZARD SIMULATOR
# Analisis dan Mitigasi WAW dengan Register Renaming
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


# 2. INSTRUCTION SET SEBELUM MITIGASI
instructions_before = [
    Instruction("I1", "R1", ["R2", "R3"]),
    Instruction("I2", "R4", ["R5", "R6"]),
    Instruction("I3", "R1", ["R7", "R8"]),
    Instruction("I4", "R4", ["R9", "R10"]),
]


# 3. PEMERIKSAAN DEPENDENSI WAW
def has_waw_dependency(inst1, inst2):
    return inst1.destination == inst2.destination


def find_waw_dependencies(instructions):
    dependencies = []

    for i in range(len(instructions)):
        for j in range(i + 1, len(instructions)):
            first = instructions[i]
            second = instructions[j]

            if has_waw_dependency(first, second):
                dependencies.append(
                    (first.name, second.name, first.destination)
                )

    return dependencies


# 4. FUNGSI MEMBUAT GRAFIK DEPENDENSI
def draw_dependency_graph(instructions, dependencies,
                          title, output_file):
    graph = nx.DiGraph()

    for inst in instructions:
        label = (
            f"{inst.name}\n"
            f"{inst.destination} = {' + '.join(inst.sources)}"
        )
        graph.add_node(inst.name, label=label)

    for first, second, register in dependencies:
        graph.add_edge(first, second, register=register)

    # Mengatur posisi agar setiap pasangan mudah dibaca
    pos = {}
    for index, inst in enumerate(instructions):
        row = index // 2
        col = index % 2
        pos[inst.name] = (col * 3, -row * 2)

    labels = nx.get_node_attributes(graph, "label")
    edge_labels = {
        (first, second): f"WAW ({register})"
        for first, second, register in dependencies
    }

    plt.figure(figsize=(11, 6))

    nx.draw_networkx_nodes(
        graph, pos,
        node_size=3200,
        node_color="lightblue",
        node_shape="s",
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
        arrowsize=20,
        node_size=3200,
        edge_color="black"
    )

    if edge_labels:
        nx.draw_networkx_edge_labels(
            graph, pos,
            edge_labels=edge_labels,
            font_size=9
        )

    plt.title(title, fontsize=14)
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"Grafik disimpan: {output_file}")


# 5. ANALISIS SEBELUM MITIGASI
dependencies_before = find_waw_dependencies(instructions_before)

print("=" * 55)
print("ANALISIS WAW SEBELUM MITIGASI")
print("=" * 55)

for first, second, register in dependencies_before:
    print(f"{first} -> {second}: WAW pada register {register}")

print(f"Total dependensi sebelum mitigasi: {len(dependencies_before)}")


# 6. INSTRUCTION SET SETELAH REGISTER RENAMING
# I3 dan I4 memakai register tujuan baru agar tidak
# menulis ke register tujuan yang sama dengan instruksi sebelumnya.

instructions_after = [
    Instruction("I1", "R1", ["R2", "R3"]),
    Instruction("I2", "R4", ["R5", "R6"]),
    Instruction("I3", "R11", ["R7", "R8"]),
    Instruction("I4", "R12", ["R9", "R10"]),
]

dependencies_after = find_waw_dependencies(instructions_after)

print("\n" + "=" * 55)
print("ANALISIS WAW SETELAH REGISTER RENAMING")
print("=" * 55)

if dependencies_after:
    for first, second, register in dependencies_after:
        print(f"{first} -> {second}: WAW pada register {register}")
else:
    print("Tidak ditemukan dependensi WAW.")

print(f"Total dependensi setelah mitigasi: {len(dependencies_after)}")


# 7. SIMPAN SEMUA GRAFIK
output_dir = "WAW"
os.makedirs(output_dir, exist_ok=True)

draw_dependency_graph(
    instructions_before,
    dependencies_before,
    "WAW Dependency Graph",
    os.path.join(output_dir, "grafik_waw.png")
)

draw_dependency_graph(
    instructions_before,
    dependencies_before,
    "WAW Before Mitigation",
    os.path.join(output_dir, "waw_sebelum_mitigasi.png")
)

draw_dependency_graph(
    instructions_after,
    dependencies_after,
    "WAW After Register Renaming",
    os.path.join(output_dir, "waw_setelah_mitigasi.png")
)


# 8. GRAFIK PERBANDINGAN JUMLAH DEPENDENSI
labels = ["Sebelum Mitigasi", "Setelah Mitigasi"]
values = [len(dependencies_before), len(dependencies_after)]

plt.figure(figsize=(8, 5))
bars = plt.bar(labels, values)

plt.title("Perbandingan Dependensi WAW")
plt.ylabel("Jumlah Dependensi")
plt.ylim(0, max(values + [1]) + 1)
plt.bar_label(bars, padding=3)
plt.tight_layout()

comparison_file = os.path.join(
    output_dir, "grafik_efektivitas_waw.png"
)
plt.savefig(comparison_file, dpi=300, bbox_inches="tight")
plt.close()

print(f"Grafik disimpan: {comparison_file}")
print("\nAnalisis WAW selesai.")
