
# ============================================================
# TUGAS: MITIGASI DATA HAZARDS PADA INSTRUCTION-LEVEL
# PARALLELISM (ILP)
# ============================================================
# JENIS HAZARD: WAR (Write After Read)
#
# Pengertian:
# WAR adalah data hazard yang terjadi ketika sebuah instruksi
# menulis register yang sebelumnya dibaca oleh instruksi lain.
#
# Tujuan:
# 1. Mengidentifikasi dependensi WAR antar-instruksi.
# 2. Menampilkan hasil analisis dependensi.
# 3. Memvisualisasikan dependensi dalam bentuk grafik.
#
# Mitigasi:
# Register renaming dapat digunakan untuk menghindari WAR
# dengan memisahkan register yang digunakan oleh instruksi.
#
# Catatan:
# Program ini merupakan simulasi sederhana dependensi WAR.
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
# 2. CONTOH INSTRUCTION SET
# ------------------------------------------------------------

instructions = [
    Instruction("I1", "R1", ["R2", "R3"]),
    Instruction("I2", "R4", ["R5", "R6"]),
    Instruction("I3", "R2", ["R7", "R8"]),
]


# ------------------------------------------------------------
# 3. DETEKSI WAR HAZARD
# ------------------------------------------------------------

def detect_war(inst1, inst2):
    """
    WAR terjadi ketika instruksi pertama membaca register
    yang kemudian ditulis oleh instruksi kedua.
    """
    return inst2.destination in inst1.sources


# ------------------------------------------------------------
# 4. ANALISIS DEPENDENSI DAN VISUALISASI
# ------------------------------------------------------------

def show_war(instructions):
    print("=" * 55)
    print("WAR (WRITE AFTER READ) DEPENDENCY ANALYSIS")
    print("=" * 55)

    graph = nx.DiGraph()

    # Menambahkan seluruh instruksi ke grafik
    for inst in instructions:
        label = (
            f"{inst.name}\n"
            f"{inst.destination} = "
            f"{' + '.join(inst.sources)}"
        )
        graph.add_node(inst.name, label=label)

    found = False

    # Memeriksa dependensi antar-instruksi
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

    # Menampilkan keterangan instruksi
    print("\nDaftar instruksi:")
    for inst in instructions:
        print(
            f"{inst.name}: {inst.destination} = "
            f"{' + '.join(inst.sources)}"
        )

    # Mengatur posisi node agar grafik mudah dibaca
    positions = nx.spring_layout(
        graph,
        seed=42,
        k=1.5
    )

    labels = nx.get_node_attributes(graph, "label")

    # Membuat grafik
    fig, ax = plt.subplots(figsize=(10, 6))

    nx.draw_networkx_nodes(
        graph,
        positions,
        node_size=3500,
        node_color="lightblue",
        edgecolors="black",
        ax=ax
    )

    nx.draw_networkx_labels(
        graph,
        positions,
        labels=labels,
        font_size=9,
        ax=ax
    )

    nx.draw_networkx_edges(
        graph,
        positions,
        arrows=True,
        arrowsize=22,
        edge_color="black",
        connectionstyle="arc3,rad=0.05",
        ax=ax
    )

    ax.set_title("WAR Dependency Graph", fontsize=14)
    ax.axis("off")

    fig.savefig(
        "war_graph.png",
        dpi=200,
        bbox_inches="tight"
    )

    plt.show()
    plt.close(fig)


# ------------------------------------------------------------
# 5. PROGRAM UTAMA
# ------------------------------------------------------------

if __name__ == "__main__":
    show_war(instructions)
