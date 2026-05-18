"""
Ra and Apep — the Egyptian solar myth encoded in the Emerald Tablet IMASM graph.

The spring layout of the full-corpus register-flow graph settles into the ouroboros:

  Node 0  (Ra's barque)  : leftmost — origin and terminus of the solar circuit
  Nodes 1–8              : outer serpent coil, winding down the lower arc
  Nodes 9–28             : inner coil converging on the head, the dense cluster
  Node 29 (Apep's head)  : the hub — the highest-degree node, center of mass
  Edges 29→0, 29→30      : THE SPEAR — Set's lance left-to-right through the skull
  Node 30 (dawn horizon) : eastern terminus where the sun re-emerges
  Nodes 31–39            : Ra's barque ascending the sky arc back west
  Return edge →0         : ouroboros closes, the sun rises again

Phase 1 — the serpent uncoils:
  Body nodes appear one by one in teal (scales). At node 29 the head blazes red.
  SPEAR FLASH: when node 30 first appears, hold for several frames with the two
  white spear edges drawn at full brightness across the entire frame.

Phase 2 — Ra's journey:
  Gaussian pulse travels the myth circuit. When the pulse peaks at node 29 (the
  head), BOTH spear edges flash white at maximum width — the lance lands. Pulse
  continues to node 30 (east), arcs over the upper nodes, and closes at node 0.

Output: docs/ra_apep.gif
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
import networkx as nx

from emerald_tablet_engine.compiler import compile_corpus
from emerald_tablet_engine.callgraph import build_graph, largest_component

TRANSCRIPTION = root / "data" / "emerald_tablet_etff.txt"
OUT           = root / "docs" / "ra_apep.gif"
BG            = "#060610"

# ── Mythological node roles ───────────────────────────────────────────────────

RA_NODE   = 0   # Ra / origin — leftmost, the sun
HEAD_NODE = 29  # Apep's head — the hub, where the spear lands
DAWN_NODE = 30  # Eastern horizon — right terminus of the spear

# Color by role
_RA_COLOR   = np.array(mcolors.to_rgba("#ffd700"))   # gold — Ra
_HEAD_COLOR = np.array(mcolors.to_rgba("#c1121f"))   # crimson — Apep's head
_DAWN_COLOR = np.array(mcolors.to_rgba("#ffffff"))   # white  — dawn horizon
_BODY_COLOR = np.array(mcolors.to_rgba("#2a9d8f"))   # teal   — serpent scales
_ARC_COLOR  = np.array(mcolors.to_rgba("#f4a261"))   # amber  — solar arc
_DIM_BODY   = np.array(mcolors.to_rgba("#1a5276"))   # dark edge — body
_SPEAR_COL  = np.array(mcolors.to_rgba("#ffffff"))   # white — spear
_PULSE_GOLD = np.array(mcolors.to_rgba("#ffd700"))
_PULSE_WHT  = np.array(mcolors.to_rgba("#ffffff"))
_PULSE_RED  = np.array(mcolors.to_rgba("#ff4444"))

SPEAR_HOLD  = 10   # extra frames frozen on the spear strike


def _node_base_color(n: int) -> np.ndarray:
    if n == RA_NODE:   return _RA_COLOR
    if n == HEAD_NODE: return _HEAD_COLOR
    if n == DAWN_NODE: return _DAWN_COLOR
    if n > DAWN_NODE:  return _ARC_COLOR
    return _BODY_COLOR


def _node_base_size(n: int, deg: int, max_deg: int) -> float:
    if n == HEAD_NODE: return 120.0
    if n == RA_NODE:   return 90.0
    if n == DAWN_NODE: return 70.0
    base = 20 if n > DAWN_NODE else 14
    return base + 50 * (np.log1p(deg) / np.log1p(max_deg)) ** 1.5


def _edge_base_style(u: int, v: int) -> tuple[str, float, float]:
    """(color_hex, linewidth, alpha) for a resting edge."""
    is_spear = (u == HEAD_NODE or v == HEAD_NODE) and (
        (u in (RA_NODE, DAWN_NODE)) or (v in (RA_NODE, DAWN_NODE))
    )
    if is_spear:
        return "#ffffff", 2.2, 0.70
    if u > DAWN_NODE or v > DAWN_NODE:
        return "#d4a017", 1.0, 0.45   # solar arc edges — amber
    return "#1a5276", 0.7, 0.25       # body edges — dark teal


# ── Rendering ─────────────────────────────────────────────────────────────────

def _draw_spear_flash(ax: plt.Axes, pos: dict, alpha: float = 1.0, lw_mul: float = 1.0) -> None:
    """Draw the full spear line: Ra ← head → dawn, with glow."""
    x0, y0 = pos[RA_NODE]
    xh, yh = pos[HEAD_NODE]
    xd, yd = pos[DAWN_NODE]

    # Glow halo
    ax.plot([x0, xd], [y0, yd], color="#ffffff",
            lw=14 * lw_mul, alpha=0.12 * alpha, zorder=4, solid_capstyle="round")
    # Shaft left segment (Ra → head)
    ax.plot([x0, xh], [y0, yh], color="#ffffff",
            lw=4.5 * lw_mul, alpha=0.90 * alpha, zorder=5, solid_capstyle="round")
    # Shaft right segment (head → dawn)
    ax.plot([xh, xd], [yh, yd], color="#ffffff",
            lw=4.5 * lw_mul, alpha=0.90 * alpha, zorder=5, solid_capstyle="round")
    # Tip flash at head — a burst dot
    ax.scatter([xh], [yh], c=[[1, 1, 1, alpha]], s=280 * lw_mul, zorder=6)


def render_frame(
    ax: plt.Axes,
    all_nodes: list[int],
    pos: dict,
    edges: list,
    base_colors: np.ndarray,
    base_sizes: np.ndarray,
    spear_edges: set[tuple[int, int]],
    revealed: set[int] | None,
    spear_flash: float,       # 0.0–1.0 intensity for spear flash
    pulse_center: int | None,
    pulse_sigma: int,
    N: int,
    title_str: str,
) -> None:
    ax.clear()
    ax.set_facecolor(BG)
    ax.set_axis_off()
    ax.set_xlim(-1.25, 1.25)
    ax.set_ylim(-1.25, 1.25)
    ax.set_title(title_str, color="#cccccc", fontsize=8.5, pad=6)

    nidx = {n: i for i, n in enumerate(all_nodes)}
    xs   = np.array([pos[n][0] for n in all_nodes])
    ys   = np.array([pos[n][1] for n in all_nodes])

    if revealed is not None:
        # Phase 1: build
        for u, v, _ in edges:
            if u not in revealed or v not in revealed:
                continue
            is_sp = (u, v) in spear_edges or (v, u) in spear_edges
            if is_sp:
                continue  # drawn separately below
            col, lw, al = _edge_base_style(u, v)
            ax.plot([pos[u][0], pos[v][0]], [pos[u][1], pos[v][1]],
                    color=col, lw=lw, alpha=al, zorder=1)

        # Spear — draw if both endpoints revealed
        if HEAD_NODE in revealed:
            if RA_NODE in revealed:
                ax.plot([pos[RA_NODE][0], pos[HEAD_NODE][0]],
                        [pos[RA_NODE][1], pos[HEAD_NODE][1]],
                        color="#ffffff", lw=2.2, alpha=0.60 + 0.40 * spear_flash, zorder=3)
            if DAWN_NODE in revealed:
                ax.plot([pos[HEAD_NODE][0], pos[DAWN_NODE][0]],
                        [pos[HEAD_NODE][1], pos[DAWN_NODE][1]],
                        color="#ffffff", lw=2.2, alpha=0.60 + 0.40 * spear_flash, zorder=3)

        if spear_flash > 0.05 and HEAD_NODE in revealed and DAWN_NODE in revealed:
            _draw_spear_flash(ax, pos, alpha=spear_flash, lw_mul=spear_flash)

        vis_idx = [nidx[n] for n in all_nodes if n in revealed]
        if not vis_idx:
            return
        colors = base_colors[vis_idx].copy()
        sizes  = base_sizes[vis_idx].copy()
        # Brighten the most recently revealed node
        # (boost head when it appears)
        ax.scatter(xs[vis_idx], ys[vis_idx],
                   c=colors, s=sizes, zorder=4, linewidths=0)

    else:
        # Phase 2: flow wave
        dists   = np.abs(np.arange(N) - pulse_center)
        dists   = np.minimum(dists, N - dists)
        weights = np.exp(-0.5 * (dists / pulse_sigma) ** 2)
        active  = {all_nodes[i] for i in range(N) if weights[i] > 0.25}
        is_spear_pulse = weights[nidx[HEAD_NODE]] > 0.45 if HEAD_NODE in nidx else False

        for u, v, _ in edges:
            is_sp  = (u, v) in spear_edges or (v, u) in spear_edges
            near   = u in active or v in active
            if is_sp:
                continue  # spear drawn separately
            col, lw, al = _edge_base_style(u, v)
            if near:
                lw *= 2.5; al = min(1.0, al * 3.0)
            ax.plot([pos[u][0], pos[v][0]], [pos[u][1], pos[v][1]],
                    color=col, lw=lw, alpha=al, zorder=1)

        # Spear — always visible, brighten on pulse at head
        sp_alpha = 0.55 + 0.45 * weights[nidx[HEAD_NODE]]
        ax.plot([pos[RA_NODE][0], pos[HEAD_NODE][0]],
                [pos[RA_NODE][1], pos[HEAD_NODE][1]],
                color="#ffffff", lw=2.5, alpha=sp_alpha, zorder=3)
        ax.plot([pos[HEAD_NODE][0], pos[DAWN_NODE][0]],
                [pos[HEAD_NODE][1], pos[DAWN_NODE][1]],
                color="#ffffff", lw=2.5, alpha=sp_alpha, zorder=3)

        if is_spear_pulse:
            intensity = weights[nidx[HEAD_NODE]]
            _draw_spear_flash(ax, pos, alpha=intensity, lw_mul=intensity * 1.4)

        # Node colors with pulse blend
        blended = np.empty_like(base_colors)
        for i, n in enumerate(all_nodes):
            w = weights[i]
            if n == HEAD_NODE:
                target = _PULSE_RED
            elif n == RA_NODE or n > DAWN_NODE:
                target = _PULSE_GOLD
            else:
                target = _PULSE_WHT
            blended[i] = np.clip(base_colors[i] * (1 - w) + target * w, 0, 1)
        sizes_w = base_sizes * (1 + 2.0 * weights)

        ax.scatter(xs, ys, c=blended, s=sizes_w, zorder=4, linewidths=0)


def fig_to_pil(fig: plt.Figure, dpi: int) -> Image.Image:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, facecolor=BG, bbox_inches="tight")
    buf.seek(0)
    return Image.open(buf).copy()


# ── Main ──────────────────────────────────────────────────────────────────────

def main(
    build_frames: int = 80,
    flow_frames:  int = 120,
    fps:          int = 15,
    dpi:          int = 120,
    figsize: tuple[float, float] = (9, 9),
) -> None:
    print("Compiling corpus …")
    result = compile_corpus(TRANSCRIPTION)
    all_instr: list[str] = []
    for data in result["versicles"].values():
        all_instr.extend(data["instructions"])

    print("Building graph …")
    G = build_graph(all_instr)
    C = largest_component(G)
    print(f"  {C.number_of_nodes()} nodes  {C.number_of_edges()} edges")

    # Execution order (first appearance)
    import re
    _REG = re.compile(r"%r(\d+)")
    seen_nodes: set[int] = set()
    node_order: list[int] = []
    for line in all_instr:
        for m in _REG.finditer(line):
            n = int(m.group(1))
            if n in C.nodes() and n not in seen_nodes:
                seen_nodes.add(n)
                node_order.append(n)
    N = len(node_order)
    nidx = {n: i for i, n in enumerate(node_order)}

    print(f"  Execution order: {N} unique nodes")
    print(f"  Ra (origin) = node {RA_NODE}   "
          f"head = node {HEAD_NODE}   dawn = node {DAWN_NODE}")

    edges = list(C.edges(data=True))
    degrees = dict(C.degree())
    max_deg = max(degrees.values()) if degrees else 1

    spear_edges: set[tuple[int, int]] = {
        (HEAD_NODE, RA_NODE), (RA_NODE, HEAD_NODE),
        (HEAD_NODE, DAWN_NODE), (DAWN_NODE, HEAD_NODE),
    }

    print("Computing layout …")
    pos = nx.spring_layout(C, k=0.04, iterations=300, seed=42)

    base_colors = np.array([_node_base_color(n) for n in node_order])
    base_sizes  = np.array([_node_base_size(n, degrees.get(n, 1), max_deg) for n in node_order])

    # ── build frame sequence with spear hold ──────────────────────────────────
    # Each entry: (nodes_revealed_count, spear_flash_intensity)
    build_seq: list[tuple[int, float]] = []
    spear_reveal_k = nidx.get(DAWN_NODE, N - 1) + 1  # k when dawn node first appears
    for k in range(1, N + 1):
        build_seq.append((k, 0.0))
        if k == spear_reveal_k:
            # Spear flash: ramp up, hold, ramp down
            ramp = 5
            hold = SPEAR_HOLD - ramp * 2
            for i in range(ramp):
                build_seq.append((k, (i + 1) / ramp))
            for _ in range(max(0, hold)):
                build_seq.append((k, 1.0))
            for i in range(ramp - 1, -1, -1):
                build_seq.append((k, (i + 1) / ramp))

    # ── flow phase: insert extra frames at head pulse ─────────────────────────
    head_idx   = nidx.get(HEAD_NODE, N // 2)
    pulse_sigma = max(5, N // 10)
    base_centers = np.linspace(0, N - 1, flow_frames).astype(int)
    flow_seq: list[int] = []
    SPEAR_PULSE_HOLD = 8
    for c in base_centers:
        flow_seq.append(c)
        if abs(c - head_idx) <= 1:
            for _ in range(SPEAR_PULSE_HOLD):
                flow_seq.append(head_idx)

    total_frames = len(build_seq) + len(flow_seq)
    print(f"  Build frames: {len(build_seq)}  (incl. {SPEAR_HOLD} spear hold)")
    print(f"  Flow frames:  {len(flow_seq)}  (incl. {SPEAR_PULSE_HOLD}× head pulse hold)")
    print(f"  Total:        {total_frames}")

    fig, ax = plt.subplots(figsize=figsize, facecolor=BG)
    frames_pil: list[Image.Image] = []

    print(f"  Rendering …")
    for f, (k, flash) in enumerate(build_seq):
        print(f"\r  build {f+1}/{len(build_seq)}", end="", flush=True)
        revealed = set(node_order[:k])
        n_cur    = node_order[k - 1]

        if flash > 0.05:
            title = (
                f"Ra and Apep  |  the spear strikes — Set pierces Apep's skull  |  "
                f"edges 29→0 · 29→30"
            )
        elif n_cur == HEAD_NODE:
            title = "Ra and Apep  |  Apep's head rises — the serpent's coils complete"
        elif n_cur == RA_NODE:
            title = "Ra and Apep  |  Ra enters the underworld — the solar barque descends"
        elif n_cur > DAWN_NODE:
            title = f"Ra and Apep  |  Ra ascends — solar arc node {n_cur} | dawn nears"
        else:
            title = (
                f"Ra and Apep  |  the serpent uncoils — node {n_cur} | "
                f"{k}/{N} nodes  ·  {C.number_of_edges()} edges"
            )
        render_frame(
            ax, node_order, pos, edges, base_colors, base_sizes, spear_edges,
            revealed=revealed, spear_flash=flash,
            pulse_center=None, pulse_sigma=pulse_sigma, N=N, title_str=title,
        )
        frames_pil.append(fig_to_pil(fig, dpi))

    print()
    for f, center in enumerate(flow_seq):
        print(f"\r  flow  {f+1}/{len(flow_seq)}", end="", flush=True)
        n_at = node_order[center]
        if n_at == HEAD_NODE:
            title = "Ra and Apep  |  THE SPEAR LANDS — Set pierces Apep  |  μ∘δ = id"
        elif n_at == RA_NODE:
            title = "Ra and Apep  |  Ra returns — the ouroboros closes  |  dawn"
        elif n_at > DAWN_NODE:
            title = f"Ra and Apep  |  Ra rises — solar arc  |  μ∘δ = id"
        else:
            title = f"Ra and Apep  |  the serpent's coil  |  node {n_at}  |  μ∘δ = id"
        render_frame(
            ax, node_order, pos, edges, base_colors, base_sizes, spear_edges,
            revealed=None, spear_flash=0.0,
            pulse_center=center, pulse_sigma=pulse_sigma, N=N, title_str=title,
        )
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
    print(f"Done: {OUT}  ({OUT.stat().st_size / 1_048_576:.1f} MB)")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Ra and Apep — Emerald Tablet IMASM myth animation")
    ap.add_argument("--build-frames", type=int, default=80)
    ap.add_argument("--flow-frames",  type=int, default=120)
    ap.add_argument("--fps",          type=int, default=15)
    ap.add_argument("--dpi",          type=int, default=120)
    args = ap.parse_args()
    main(build_frames=args.build_frames, flow_frames=args.flow_frames,
         fps=args.fps, dpi=args.dpi)
