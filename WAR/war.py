
# ============================================================
# TUGAS: MITIGASI DATA HAZARDS PADA INSTRUCTION-LEVEL
# PARALLELISM (ILP)
# ============================================================
# JENIS HAZARD: WAR (Write After Read)
#
# WAR terjadi ketika instruksi berikutnya menulis register
# yang sebelumnya telah dibaca oleh instruksi terdahulu.
#
# Tujuan:
# 1. Mendeteksi dependensi WAR antar-instruksi.
# 2. Menampilkan hasil analisis dependensi.
# 3. Membuat dependency graph yang mudah dibaca.
#
# Mitigasi:
# Register renaming dapat menghilangkan dependensi WAR
# dengan memisahkan register yang digunakan.
# ============================================================

from dataclasses import dataclass
import matplotlib.pyplot as plt
import networkx as nx


# ------------------------------------------------------------
# 1. DEFINISI INSTRUKSI
# ------------------------------------------------------------

@dataclass
class Instruction:
    name: str
    destination: str
    sources: list


# ------------------------------------------------------------
# 2. INSTRUCTION SET
# ------------------------------------------------------------

instructions = [
    Instruction("I1", "R1", ["R2", "R3"]),
    Instruction("I2", "R4", ["R5", "R6"]),
    Instruction("I3", "R2", ["R7", "R8"]),
]


# ------------------------------------------------------------
# 3. DETEKSI WAR
# ------------------------------------------------------------

def detect_war(inst1, inst2):
    """
    WAR terjadi jika instruksi pertama membaca register
    yang ditulis oleh instruksi kedua.
    """
    return inst2.destination in inst1.sources


# ------------------------------------------------------------
# 4. ANALISIS DEPENDENSI WAR
# ------------------------------------------------------------

def show_war(instructions):
    print("=" * 55)
    print("WAR (WRITE AFTER READ) DEPENDENCY ANALYSIS")
    print("=" * 55)

    graph = nx.DiGraph()

    # Tambahkan instruksi ke graph
    for inst in instructions:
        label = (
            f"{inst.name}\n"
            f"{inst.destination} = "
            f"{' + '.join(inst.sources)}"
        )
        graph.add_node(inst.name, label=label)

    found = False

    # Periksa setiap pasangan instruksi sesuai urutan
    for i in range(len(instructions)):
        for j in range(i + 1, len(instructions)):
            first = instructions[i]
            second = instructions[j]

            if detect_war(first, second):
                register = second.destination

                print(
                    f"{first.name} -> {second.name}: "
                    f"WAR pada register {register}"
                )

                graph.add_edge(first.name, second.name)
                found = True

    if not found:
        print("Tidak ditemukan dependensi WAR.")

    print("\nDaftar instruksi:")
    for inst in instructions:
        print(
            f"{inst.name}: {inst.destination} = "
            f"{' + '.join(inst.sources)}"
        )

    # --------------------------------------------------------
    # 5. VISUALISASI GRAPH
    # --------------------------------------------------------

    # Posisi tetap agar node tidak terpotong dan mudah dibaca
    positions = {
        "I1": (0, 1),
        "I2": (2, 1),
        "I3": (0, 0),
    }

    labels = nx.get_node_attributes(graph, "label")

    fig, ax = plt.subplots(figsize=(10, 6))

    nx.draw_networkx_nodes(
        graph,
        positions,
        node_size=4200,
        node_color="lightblue",
        edgecolors="black",
        linewidths=1.5,
        ax=ax
    )

    nx.draw_networkx_labels(
        graph,
        positions,
        labels=labels,
        font_size=10,
        font_weight="normal",
        ax=ax
    )

    nx.draw_networkx_edges(
        graph,
        positions,
        arrows=True,
        arrowstyle="-|>",
        arrowsize=22,
        width=1.8,
        edge_color="black",
        node_size=4200,
        ax=ax
    )

    ax.set_title("WAR Dependency Graph", fontsize=14, pad=20)

    # Ruang ekstra di sekeliling node
    ax.set_xlim(-1.2, 3.2)
    ax.set_ylim(-0.8, 2.0)
    ax.axis("off")

    fig.tight_layout()
    fig.savefig(
        "war_graph.png",
        dpi=200,
        bbox_inches="tight"
    )

    plt.show()
    plt.close(fig)


# ------------------------------------------------------------
# 6. PROGRAM UTAMA
# ------------------------------------------------------------

if __name__ == "__main__":
    show_war(instructions)
