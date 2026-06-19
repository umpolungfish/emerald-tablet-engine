"""
Animated barrel-view decompressed-token CFG — Emerald Tablet.

3D matplotlib animation looking nearly straight down the Z axis, slowly
rotating azimuth to reveal depth.  Same graph and edge semantics as
animated_cfg_tokens.py; the barrel perspective makes the ENGAGR split
traces (∅ + W diverging) and IMSCRIB backpop arcs (←) pop out of the
plane as the rotation sweeps past them.

Camera: elev=78° (near-overhead), azim sweeps 0→360°.

Output: docs/animated_cfg_tokens_barrel.gif
"""

from __future__ import annotations
import io
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))

import numpy as np
from PIL import Image
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from mpl_toolkits.mplot3d import Axes3D   # noqa: F401 — registers 3d projection
import networkx as nx

from emerald_tablet_engine.compiler import compile_corpus
from emerald_tablet_engine.callgraph_tokens import (
    build_graph, largest_component, EDGE_STYLE, summary,
)

TRANSCRIPTION = root / "data" / "emerald_tablet_etff.txt"
OUT = root / "docs" / "animated_cfg_tokens_barrel.gif"
BG  = "#0d0d1a"

_ETYPE_COLOR = {
    "empty":     "#888888",
    "weighted":  "#ffd700",
    "backpop":   "#cc44ff",
    "source":    "#f28e2b",
    "frobenius": "#4e79a7",
    "seq_clink": "#5588aa",
    "flow":      "#3a5f80",
}
_ETYPE_LW = {
    "empty":     1.4,
    "weighted":  2.6,
    "backpop":   2.6,
    "source":    1.8,
    "frobenius": 2.2,
    "seq_clink": 1.4,
    "flow":      0.7,
}
_ETYPE_ALPHA = {
    "empty":     0.75,
    "weighted":  0.95,
    "backpop":   0.95,
    "source":    0.80,
    "frobenius": 0.85,
    "seq_clink": 0.65,
    "flow":      0.25,
}


def fig_to_pil(fig, dpi):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, facecolor=BG, bbox_inches="tight")
    buf.seek(0)
    return Image.open(buf).copy()


def main(n_frames=90, elev=78, fps=20, dpi=120):
    print("Compiling Emerald Tablet corpus …")
    result   = compile_corpus(TRANSCRIPTION)
    all_instr: list[str] = []
    for data in result["versicles"].values():
        all_instr.extend(data["instructions"])
    print(f"  {result['versicle_count']} versicles · {result['total_instructions']} instructions")

    G = build_graph(all_instr)
    C = largest_component(G)
    print(f"  {summary(C)}")

    print("  3D spring layout …")
    pos3d_raw = nx.spring_layout(C, dim=3, k=0.55, iterations=300, seed=42)
    pos3d     = {n: np.array(v) for n, v in pos3d_raw.items()}

    node_list = list(C.nodes())
    indeg     = dict(C.in_degree())
    max_deg   = max(indeg.values()) if indeg else 1

    node_colors = [
        mcolors.to_rgba(
            {"identity":"#59a14f","morphism":"#f28e2b","frobenius":"#4e79a7",
             "dialetheia":"#e15759","bootstrap":"#9c9c9c"}
            .get(C.nodes[n].get("family","bootstrap"), "#cccccc")
        ) for n in node_list
    ]
    node_sizes = [
        30 + 180 * (np.log1p(indeg.get(n,0)) / np.log1p(max_deg)) ** 1.3
        for n in node_list
    ]

    xs = np.array([pos3d[n][0] for n in node_list])
    ys = np.array([pos3d[n][1] for n in node_list])
    zs = np.array([pos3d[n][2] for n in node_list])

    # Group edges by type for batch drawing
    from collections import defaultdict
    etype_edges: dict[str, list[tuple]] = defaultdict(list)
    for u, v, d in C.edges(data=True):
        if u in pos3d and v in pos3d:
            etype_edges[d.get("etype","flow")].append((u, v))

    azim_angles = np.linspace(0, 360, n_frames, endpoint=False)

    print(f"  Rendering {n_frames} frames (elev={elev}°, full rotation) …")
    fig = plt.figure(figsize=(8, 8), facecolor=BG)
    frames_pil: list[Image.Image] = []

    for f, azim in enumerate(azim_angles):
        print(f"\r  {(f+1)/n_frames*100:5.1f}%  frame {f+1}/{n_frames}", end="", flush=True)

        ax = fig.add_subplot(111, projection="3d", facecolor=BG)
        ax.set_facecolor(BG)
        fig.patch.set_facecolor(BG)

        # Hide all default axes chrome
        ax.set_axis_off()
        ax.grid(False)
        for pane in (ax.xaxis.pane, ax.yaxis.pane, ax.zaxis.pane):
            pane.fill = False
            pane.set_edgecolor("none")

        # Draw edges
        for etype, edge_list in etype_edges.items():
            col   = _ETYPE_COLOR.get(etype, "#3a5f80")
            lw    = _ETYPE_LW.get(etype, 0.7)
            al    = _ETYPE_ALPHA.get(etype, 0.25)
            ls    = "dashed" if etype == "empty" else "solid"
            for u, v in edge_list:
                p0, p1 = pos3d[u], pos3d[v]
                ax.plot(
                    [p0[0], p1[0]], [p0[1], p1[1]], [p0[2], p1[2]],
                    color=col, lw=lw, alpha=al, linestyle=ls, zorder=1,
                )

        # Draw nodes
        ax.scatter(
            xs, ys, zs,
            c=node_colors, s=node_sizes,
            depthshade=True, zorder=4,
            edgecolors="none",
        )

        ax.view_init(elev=elev, azim=azim)

        # Title
        ax.set_title(
            f"Emerald Tablet — Decompressed Token CFG\n"
            f"barrel view  elev={elev}°  azim={azim:.0f}°",
            color="white", fontsize=8, pad=4,
        )

        frames_pil.append(fig_to_pil(fig, dpi))
        fig.clf()

    print()
    plt.close(fig)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    print(f"Assembling GIF → {OUT} …")
    frames_rgb = [fr.convert("RGB") for fr in frames_pil]
    frames_rgb[0].save(
        str(OUT), save_all=True, append_images=frames_rgb[1:],
        duration=1000 // fps, loop=0, optimize=False,
    )
    sz = OUT.stat().st_size / (1024 * 1024)
    print(f"Done: {OUT}  ({sz:.1f} MB)")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", type=int, default=90)
    ap.add_argument("--elev",   type=int, default=78)
    ap.add_argument("--fps",    type=int, default=20)
    ap.add_argument("--dpi",    type=int, default=120)
    args = ap.parse_args()
    main(n_frames=args.frames, elev=args.elev, fps=args.fps, dpi=args.dpi)
