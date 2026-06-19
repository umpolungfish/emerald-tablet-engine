"""
Animated decompressed-token CFG — Emerald Tablet.

Register-level graph (preserving full trace structure) with semantic
edge decompression.  Split traces are visible as diverging coloured arcs:

  ENGAGR node → ∅ arc (grey-dashed) + W arc (gold) diverge simultaneously
  IMSCRIB node → src arc (orange) + ← backpop arc (violet) diverge

Phase 1 — BUILD
  Nodes appear in instruction order.  When an ENGAGR node is revealed,
  both its ∅ and W out-edges materialise together (the split is visible
  from the moment the token enters).

Phase 2 — FLOW WAVE
  Gaussian pulse travels instruction-order through the graph.
  When pulse hits ENGAGR: ∅ edge dims to grey-dashed, W edge blazes gold.
  When pulse hits IMSCRIB: src edge dims, ← backpop arc blazes violet.
  When pulse hits IFIX: arriving backpop arc pulses violet (receiving end).

Output: docs/animated_cfg_tokens.gif
"""

from __future__ import annotations
import io
import re
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
import networkx as nx

from emerald_tablet_engine.compiler import compile_corpus
from emerald_tablet_engine.callgraph_tokens import (
    build_graph, largest_component, EDGE_STYLE, summary,
)

TRANSCRIPTION = root / "data" / "emerald_tablet_etff.txt"
OUT = root / "docs" / "animated_cfg_tokens.gif"
BG  = "#0d0d1a"

_INSTR_RE = re.compile(r'\s*0x[0-9a-fA-F]+\s*\|\s*(\w+)\s+%r(\d+)')

_PULSE_WHITE  = np.array(mcolors.to_rgba("#ffffff"))
_PULSE_GOLD   = np.array(mcolors.to_rgba("#ffd700"))
_PULSE_VIOLET = np.array(mcolors.to_rgba("#cc44ff"))
_PULSE_GREY   = np.array(mcolors.to_rgba("#888888"))


def parse_instruction_order(sections: dict) -> list[tuple[int, str]]:
    """Return (reg_id, mnemonic) in compiled order across all versicles."""
    order: list[tuple[int, str]] = []
    for data in sections.values():
        for line in data["instructions"]:
            m = _INSTR_RE.match(line)
            if m:
                order.append((int(m.group(2)), m.group(1)))
    return order


def render_frame(
    ax, C, pos, node_order, base_colors, base_sizes,
    revealed, pulse_reg, title_str,
):
    ax.clear()
    ax.set_facecolor(BG)
    ax.set_axis_off()
    ax.set_xlim(-1.15, 1.15)
    ax.set_ylim(-1.10, 1.10)
    ax.set_title(title_str, color="white", fontsize=7.5, pad=5, linespacing=1.35)

    pulse_mnem = C.nodes[pulse_reg].get("mnemonic", "") if pulse_reg in C.nodes else ""

    # ── Edges ─────────────────────────────────────────────────────────────
    for u, v, d in C.edges(data=True):
        if u not in pos or v not in pos:
            continue
        if revealed is not None and (u not in revealed or v not in revealed):
            continue

        etype  = d.get("etype", "flow")
        style  = EDGE_STYLE.get(etype, EDGE_STYLE["flow"])
        near   = pulse_reg in (u, v)

        lw = style["lw"] * (2.0 if near else 0.6)
        al = min(0.98, style["alpha"] * (1.7 if near else 0.5))

        # Extra highlight logic for split traces
        if near and pulse_mnem == "ENGAGR":
            if etype == "weighted":
                lw, al = style["lw"] * 2.8, 0.98  # W arc blazes gold
            elif etype == "empty":
                lw, al = style["lw"] * 1.4, 0.85  # ∅ arc shows grey-dashed

        if near and pulse_mnem == "IMSCRIB":
            if etype == "backpop":
                lw, al = style["lw"] * 2.8, 0.98  # ← arc blazes violet
            elif etype == "source":
                lw, al = style["lw"] * 1.8, 0.88

        if pulse_mnem == "IFIX" and v == pulse_reg and etype == "backpop":
            lw, al = style["lw"] * 2.5, 0.96  # receiving end of backpop

        rad = 0.12 if etype in ("weighted", "backpop") else 0.06
        ax.annotate(
            "", xy=pos[v], xytext=pos[u],
            arrowprops=dict(
                arrowstyle="-|>",
                color=style["color"],
                lw=lw, alpha=al,
                linestyle=style["style"],
                connectionstyle=f"arc3,rad={rad}",
            ),
            zorder=2 if near else 1,
        )

    # ── Nodes ─────────────────────────────────────────────────────────────
    vis_idx = (
        [i for i, n in enumerate(node_order) if n in revealed]
        if revealed is not None
        else list(range(len(node_order)))
    )
    if not vis_idx:
        return

    node_colors = base_colors.copy()
    node_sizes  = base_sizes.copy()

    if pulse_reg is not None:
        try:
            pi = node_order.index(pulse_reg)
            mnem = C.nodes[pulse_reg].get("mnemonic", "")
            if mnem == "ENGAGR":
                node_colors[pi] = _PULSE_GOLD
            elif mnem == "IMSCRIB":
                node_colors[pi] = _PULSE_VIOLET
            elif mnem == "IFIX":
                node_colors[pi] = _PULSE_VIOLET * 0.7 + _PULSE_WHITE * 0.3
            else:
                node_colors[pi] = _PULSE_WHITE
            node_sizes[pi] *= 3.0
        except ValueError:
            pass

    xs = np.array([pos[node_order[i]][0] for i in vis_idx])
    ys = np.array([pos[node_order[i]][1] for i in vis_idx])
    ax.scatter(
        xs, ys,
        c=node_colors[vis_idx],
        s=node_sizes[vis_idx],
        zorder=4, linewidths=0.4, edgecolors="#ffffff22",
    )


def fig_to_pil(fig, dpi):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, facecolor=BG, bbox_inches="tight")
    buf.seek(0)
    return Image.open(buf).copy()


def main(build_frames=60, flow_frames=100, fps=18, dpi=110):
    print("Compiling Emerald Tablet corpus …")
    result = compile_corpus(TRANSCRIPTION)
    all_instr: list[str] = []
    for data in result["versicles"].values():
        all_instr.extend(data["instructions"])

    print(f"  {result['versicle_count']} versicles · {result['total_instructions']} instructions")

    G = build_graph(all_instr)
    C = largest_component(G)
    print(f"  {summary(C)}")

    instr_order = parse_instruction_order(result["versicles"])
    node_order_raw = [r for r, _ in instr_order if r in C.nodes]
    seen: set[int] = set()
    node_order: list[int] = []
    for r in node_order_raw:
        if r not in seen:
            seen.add(r)
            node_order.append(r)
    # append any component nodes not in instruction stream
    for n in C.nodes():
        if n not in seen:
            node_order.append(n)

    N = len(node_order)
    print(f"  Layout ({N} nodes) …")
    pos = nx.spring_layout(C, k=0.06, iterations=300, seed=42)

    indeg      = dict(C.in_degree())
    max_deg    = max(indeg.values()) if indeg else 1
    base_colors = np.array([
        mcolors.to_rgba(C.nodes[n].get("color", "#cccccc")) for n in node_order
    ])
    base_sizes = np.array([
        25 + 140 * (np.log1p(indeg.get(n, 0)) / np.log1p(max_deg)) ** 1.4
        for n in node_order
    ])

    # Flow phase: pulse follows instruction order (wrapping)
    pulse_seq = [node_order_raw[i % len(node_order_raw)]
                 for i in np.linspace(0, len(node_order_raw) - 1, flow_frames).astype(int)]

    total_frames = build_frames + flow_frames
    print(f"  Rendering {total_frames} frames …")

    fig, ax = plt.subplots(figsize=(9, 9), facecolor=BG)
    frames_pil: list[Image.Image] = []

    for f in range(total_frames):
        print(f"\r  {(f+1)/total_frames*100:5.1f}%  frame {f+1}/{total_frames}", end="", flush=True)

        if f < build_frames:
            frac     = (f + 1) / build_frames
            k        = max(1, int(frac * N))
            revealed = set(node_order[:k])
            pulse    = node_order[k - 1]
            mnem     = C.nodes[pulse].get("mnemonic", "")
            if mnem == "ENGAGR":
                hint = "⚡ split: ∅→IFIX  W→IMSCRIB"
            elif mnem == "IMSCRIB":
                hint = "⚡ backpop: ←→IFIX  src→next"
            else:
                hint = mnem
            title = f"Emerald Tablet — Decompressed Token CFG | build: {hint} | μ∘δ=id"
            render_frame(ax, C, pos, node_order, base_colors, base_sizes,
                         revealed, pulse, title)
        else:
            fi    = f - build_frames
            pulse = pulse_seq[fi]
            mnem  = C.nodes[pulse].get("mnemonic", "") if pulse in C.nodes else ""
            out_etypes = [d.get("etype","") for _, _, d in C.out_edges(pulse, data=True)]
            splits = " + ".join(sorted(set(out_etypes))) if out_etypes else ""
            title = (
                f"Emerald Tablet — Decompressed Token CFG | "
                f"%r{pulse} {mnem}  →  [{splits}]"
            )
            render_frame(ax, C, pos, node_order, base_colors, base_sizes,
                         None, pulse, title)

        frames_pil.append(fig_to_pil(fig, dpi))

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
    ap.add_argument("--build-frames", type=int, default=60)
    ap.add_argument("--flow-frames",  type=int, default=100)
    ap.add_argument("--fps",          type=int, default=18)
    ap.add_argument("--dpi",          type=int, default=110)
    args = ap.parse_args()
    main(
        build_frames=args.build_frames,
        flow_frames=args.flow_frames,
        fps=args.fps,
        dpi=args.dpi,
    )
