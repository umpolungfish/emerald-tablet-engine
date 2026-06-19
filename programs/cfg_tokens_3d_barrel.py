"""
Interactive 3D decompressed-token CFG — Emerald Tablet (barrel view).

Same graph and traces as cfg_tokens_3d.py; camera starts directly overhead
looking down the Z axis ("down the barrel").  The full XY spread of the
decompressed token graph is immediately visible; depth (Z) separates layers
you rotate into view.

Camera: eye at (0.05, 0.05, 2.4) — nearly straight down.
        up  = (0, 1, 0) so the graph reads with Y going away from you.

Output: docs/cfg_tokens_3d_barrel.html
"""

from __future__ import annotations
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))

import numpy as np
import networkx as nx
import plotly.graph_objects as go

from emerald_tablet_engine.compiler import compile_corpus
from emerald_tablet_engine.callgraph_tokens import (
    build_graph, largest_component, EDGE_STYLE, TOKEN_FAMILY, summary,
)

DATA = root / "data" / "emerald_tablet_etff.txt"
OUT  = root / "docs" / "cfg_tokens_3d_barrel.html"

_ETYPE_PLOTLY: dict[str, dict] = {
    "empty":     {"color": "rgba(136,136,136,0.85)", "width": 3,   "dash": "dot"},
    "weighted":  {"color": "rgba(255,215,  0,0.95)", "width": 5,   "dash": "solid"},
    "backpop":   {"color": "rgba(204, 68,255,0.95)", "width": 5,   "dash": "solid"},
    "source":    {"color": "rgba(242,142, 43,0.80)", "width": 3.5, "dash": "solid"},
    "frobenius": {"color": "rgba( 78,121,167,0.90)", "width": 4,   "dash": "solid"},
    "seq_clink": {"color": "rgba( 85,136,170,0.70)", "width": 2.5, "dash": "solid"},
    "flow":      {"color": "rgba( 58, 95,128,0.30)", "width": 1.2, "dash": "solid"},
}

_FAMILY_PLOTLY: dict[str, str] = {
    "identity":   "rgb( 89,161, 79)",
    "morphism":   "rgb(242,142, 43)",
    "frobenius":  "rgb( 78,121,167)",
    "dialetheia": "rgb(225, 87, 89)",
    "bootstrap":  "rgb(156,156,156)",
}

_SEMANTIC_LABEL: dict[str, str] = {
    "empty":    "∅  empty — ENGAGR→next",
    "weighted": "W  weighted — ENGAGR→IMSCRIB split",
    "backpop":  "←  backpop — IMSCRIB→IFIX",
    "source":   "src — IMSCRIB source",
    "frobenius":"δ — FSPLIT co-multiplication",
    "seq_clink":"∘→id — CLINK (never IFIX)",
    "flow":     "flow — sequential",
}


def build_traces(C: nx.DiGraph, pos3d: dict) -> list:
    from collections import defaultdict
    traces = []

    etype_edges: dict[str, list] = defaultdict(list)
    for u, v, d in C.edges(data=True):
        etype_edges[d.get("etype", "flow")].append((u, v, d))

    for etype, edge_list in etype_edges.items():
        style = _ETYPE_PLOTLY.get(etype, _ETYPE_PLOTLY["flow"])
        xs, ys, zs = [], [], []
        for u, v, _ in edge_list:
            if u not in pos3d or v not in pos3d:
                continue
            p0, p1 = pos3d[u], pos3d[v]
            xs += [p0[0], p1[0], None]
            ys += [p0[1], p1[1], None]
            zs += [p0[2], p1[2], None]
        if not xs:
            continue
        traces.append(go.Scatter3d(
            x=xs, y=ys, z=zs,
            mode="lines",
            line=dict(color=style["color"], width=style["width"], dash=style["dash"]),
            name=_SEMANTIC_LABEL.get(etype, etype),
            legendgroup=etype,
            hoverinfo="name",
        ))

    # Arrow cones for semantic edges
    for etype in ("weighted", "backpop", "empty", "frobenius", "source"):
        edge_list = etype_edges.get(etype, [])
        if not edge_list:
            continue
        style = _ETYPE_PLOTLY[etype]
        cx, cy, cz, ux, uy, uz = [], [], [], [], [], []
        for u, v, _ in edge_list:
            if u not in pos3d or v not in pos3d:
                continue
            p0, p1 = np.array(pos3d[u]), np.array(pos3d[v])
            mid  = p0 * 0.55 + p1 * 0.45
            dirv = p1 - p0
            norm = np.linalg.norm(dirv)
            if norm < 1e-9:
                continue
            dirv /= norm
            cx.append(float(mid[0])); cy.append(float(mid[1])); cz.append(float(mid[2]))
            ux.append(float(dirv[0])); uy.append(float(dirv[1])); uz.append(float(dirv[2]))
        if not cx:
            continue
        col = style["color"].replace("rgba(","").replace("rgb(","").replace(")","")
        parts = col.split(",")
        r, g, b = int(parts[0]), int(parts[1]), int(parts[2])
        traces.append(go.Cone(
            x=cx, y=cy, z=cz, u=ux, v=uy, w=uz,
            sizemode="absolute", sizeref=0.06,
            colorscale=[[0, f"rgb({r},{g},{b})"], [1, f"rgb({r},{g},{b})"]],
            showscale=False, opacity=0.85,
            name=f"{etype} dir", legendgroup=etype, showlegend=False,
            hoverinfo="skip",
        ))

    # Nodes
    indeg   = dict(C.in_degree())
    max_deg = max(indeg.values()) if indeg else 1
    node_list = [n for n in C.nodes() if n in pos3d]
    xs = [pos3d[n][0] for n in node_list]
    ys = [pos3d[n][1] for n in node_list]
    zs = [pos3d[n][2] for n in node_list]
    node_colors = [
        _FAMILY_PLOTLY.get(C.nodes[n].get("family", "bootstrap"), "rgb(156,156,156)")
        for n in node_list
    ]
    node_sizes = [
        8 + 28 * (np.log1p(indeg.get(n, 0)) / np.log1p(max_deg)) ** 1.3
        for n in node_list
    ]
    hover_texts = []
    for n in node_list:
        mnem = C.nodes[n].get("mnemonic", "?")
        fam  = C.nodes[n].get("family", "?")
        out_e = [(d.get("etype",""), d.get("label",""), v)
                 for _, v, d in C.out_edges(n, data=True)]
        in_e  = [(d.get("etype",""), d.get("label",""), u)
                 for u, _, d in C.in_edges(n, data=True)]
        out_str = "  ".join(f"{lbl}→%r{v}" for _, lbl, v in out_e) or "—"
        in_str  = "  ".join(f"%r{u}→{lbl}" for _, lbl, u in in_e[:4]) or "—"
        hover_texts.append(
            f"<b>%r{n}  {mnem}</b><br>family: {fam}<br>"
            f"in-degree: {indeg.get(n,0)}<br>"
            f"out: {out_str}<br>in (≤4): {in_str}"
        )
    traces.append(go.Scatter3d(
        x=xs, y=ys, z=zs,
        mode="markers+text",
        marker=dict(size=node_sizes, color=node_colors,
                    line=dict(color="rgba(255,255,255,0.25)", width=0.5)),
        text=[C.nodes[n].get("mnemonic","") for n in node_list],
        textposition="top center",
        textfont=dict(size=8, color="white"),
        hovertext=hover_texts, hoverinfo="text",
        name="tokens", legendgroup="nodes",
    ))
    return traces


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

    print("  3D spring layout …")
    pos3d_raw = nx.spring_layout(C, dim=3, k=0.55, iterations=300, seed=42)
    pos3d     = {n: (float(v[0]), float(v[1]), float(v[2])) for n, v in pos3d_raw.items()}

    print("  Building traces …")
    traces = build_traces(C, pos3d)

    fig = go.Figure(data=traces)
    fig.update_layout(
        title=dict(
            text=(
                f"Emerald Tablet — Decompressed Token CFG (barrel view)<br>"
                f"<sup>{C.number_of_nodes()} nodes · {C.number_of_edges()} edges · "
                f"drag to rotate · scroll to zoom</sup>"
            ),
            font=dict(color="white", size=14), x=0.5,
        ),
        paper_bgcolor="#0d0d1a",
        scene=dict(
            bgcolor="#0d0d1a",
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False,
                       title="", backgroundcolor="#0d0d1a"),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False,
                       title="", backgroundcolor="#0d0d1a"),
            zaxis=dict(showgrid=False, zeroline=False, showticklabels=False,
                       title="", backgroundcolor="#0d0d1a"),
            # ── barrel view: camera overhead, looking straight down Z ──────
            camera=dict(
                eye=dict(x=0.05, y=0.05, z=2.4),
                up=dict(x=0, y=1, z=0),
                center=dict(x=0, y=0, z=0),
            ),
            aspectmode="cube",
        ),
        legend=dict(
            bgcolor="rgba(26,26,46,0.7)", bordercolor="#444466",
            font=dict(color="white", size=10), x=0.01, y=0.99,
        ),
        margin=dict(l=0, r=0, t=80, b=0),
        font=dict(color="white"),
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(str(OUT), include_plotlyjs="cdn", full_html=True,
                   config={"displayModeBar": True, "scrollZoom": True})
    sz = OUT.stat().st_size / 1024
    print(f"Saved: {OUT}  ({sz:.0f} KB)")


if __name__ == "__main__":
    main()
