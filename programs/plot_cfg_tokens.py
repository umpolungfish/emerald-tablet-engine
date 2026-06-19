"""
Document-quality decompressed-token CFG — Emerald Tablet.

Register-level graph (one node per compiled instruction) with semantic
edge decompression:

  FSPLIT  → δ-split to next two regs          (blue, existing behaviour)
  ENGAGR  → ∅ to next reg + W to next IMSCRIB  (grey-dashed + gold — the split trace)
  IMSCRIB  → src to next reg + ← to next IFIX  (orange + violet — backpopulation arc)
  CLINK   → ∘→id to next reg                  (steel, never to IFIX)
  others  → flow to next reg                  (dim)

Node colour = token family.  Node size ∝ in-degree (hub prominence).

Output: docs/cfg_tokens_document.png  (300 dpi)
"""

from __future__ import annotations
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.lines  as mlines
import matplotlib.patches as mpatches
import networkx as nx
import numpy as np

from emerald_tablet_engine.compiler import compile_corpus
from emerald_tablet_engine.callgraph_tokens import (
    build_graph, largest_component, EDGE_STYLE, summary,
)

DATA = root / "data" / "emerald_tablet_etff.txt"
OUT  = root / "docs" / "cfg_tokens_document.png"
BG   = "#0d0d1a"


def main() -> None:
    print("Compiling Emerald Tablet corpus …")
    result   = compile_corpus(DATA)
    all_instr: list[str] = []
    for data in result["versicles"].values():
        all_instr.extend(data["instructions"])
    print(f"  {result['versicle_count']} versicles · {result['total_instructions']} instructions")

    G = build_graph(all_instr)
    C = largest_component(G)
    print(f"  {summary(C)}")

    print("Computing layout …")
    pos = nx.spring_layout(C, k=0.06, iterations=300, seed=42)

    # Node colour and size
    node_list   = list(C.nodes())
    node_colors = [C.nodes[n].get("color", "#cccccc") for n in node_list]
    indeg       = dict(C.in_degree())
    max_deg     = max(indeg.values()) if indeg else 1
    node_sizes  = [
        30 + 160 * (np.log1p(indeg.get(n, 0)) / np.log1p(max_deg)) ** 1.4
        for n in node_list
    ]

    fig, ax = plt.subplots(figsize=(16, 16), facecolor=BG)
    ax.set_facecolor(BG)
    ax.set_axis_off()

    # Draw edges grouped by etype
    for etype, style in EDGE_STYLE.items():
        edgelist = [(u, v) for u, v, d in C.edges(data=True) if d.get("etype") == etype]
        if not edgelist:
            continue
        nx.draw_networkx_edges(
            C, pos, edgelist=edgelist, ax=ax,
            edge_color=style["color"],
            alpha=style["alpha"],
            width=style["lw"],
            style=style["style"],
            arrows=True, arrowsize=7, arrowstyle="-|>",
            connectionstyle="arc3,rad=0.08",
            min_source_margin=3, min_target_margin=3,
        )

    # Draw nodes
    pc = nx.draw_networkx_nodes(
        C, pos, nodelist=node_list,
        node_color=node_colors, node_size=node_sizes,
        linewidths=0.4, edgecolors="#ffffff33", ax=ax,
    )
    if pc is not None:
        pc.set_zorder(4)

    ax.set_title(
        f"Emerald Tablet — Decompressed Token CFG\n"
        f"{C.number_of_nodes()} nodes · {C.number_of_edges()} edges · "
        f"{result['versicle_count']} versicles\n"
        f"ENGAGR splits: ∅→next  W→IMSCRIB  ·  IMSCRIB backpop: ←→IFIX",
        color="white", fontsize=11, pad=14, linespacing=1.6,
    )

    legend_handles = [
        mlines.Line2D([], [], color="#ffd700", lw=2.5,  label="W  ENGAGR→IMSCRIB (weighted split)"),
        mlines.Line2D([], [], color="#888888", lw=1.6, linestyle="--", label="∅  ENGAGR→IFIX (empty split)"),
        mlines.Line2D([], [], color="#cc44ff", lw=2.5,  label="←  IMSCRIB→IFIX (backpopulation)"),
        mlines.Line2D([], [], color="#f28e2b", lw=1.8,  label="src  IMSCRIB sequential source"),
        mlines.Line2D([], [], color="#4e79a7", lw=2.2,  label="δ  FSPLIT co-multiplication"),
        mlines.Line2D([], [], color="#5588aa", lw=1.4,  label="∘→id  CLINK (never to IFIX)"),
        mlines.Line2D([], [], color="#3a5f80", lw=0.8,  alpha=0.5, label="flow  sequential"),
        mpatches.Patch(color="#59a14f", label="Identity (IMSCRIB / IFIX)"),
        mpatches.Patch(color="#f28e2b", label="Morphism (AFWD / AREV / CLINK)"),
        mpatches.Patch(color="#4e79a7", label="Frobenius (FSPLIT / FFUSE)"),
        mpatches.Patch(color="#e15759", label="Dialetheia (ENGAGR / EVALT / EVALF)"),
        mpatches.Patch(color="#9c9c9c", label="Bootstrap (VINIT / TANCH)"),
    ]
    ax.legend(
        handles=legend_handles, loc="lower left",
        framealpha=0.35, facecolor="#1a1a2e",
        edgecolor="#444466", labelcolor="white", fontsize=8,
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(OUT), dpi=300, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"Saved: {OUT}")


if __name__ == "__main__":
    main()
