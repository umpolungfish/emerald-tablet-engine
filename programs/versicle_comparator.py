#!/usr/bin/env python3
"""
Versicle Topology Comparator — structural fingerprints across Emerald Tablet versicles.

Computes per-versicle primitive distributions and Jensen-Shannon divergence
between the four corpus sections (proem, cosmogony, praxis, closure).

Usage:
    python programs/versicle_comparator.py data/emerald_tablet_etff.txt [--top-n 10]
"""

from __future__ import annotations
import argparse
import math
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from emerald_tablet_engine import compile_corpus, PRIMITIVES, SECTIONS

ALL_CODES = list(PRIMITIVES.keys())
ALL_MNEMONICS = [PRIMITIVES[c]['mnemonic'] for c in ALL_CODES]


def versicle_dist(v_data: dict) -> dict[str, float]:
    counts: Counter = Counter()
    for instr in v_data['instructions']:
        m = re.search(r'\|\s*(\w+)', instr)
        if m:
            counts[m.group(1)] += 1
    total = sum(counts.values()) or 1
    return {mn: counts.get(mn, 0) / total for mn in ALL_MNEMONICS}


def js_divergence(p: dict[str, float], q: dict[str, float]) -> float:
    keys = set(p) | set(q)
    m = {k: (p.get(k, 0) + q.get(k, 0)) / 2 for k in keys}
    def kl(a, b):
        return sum(a[k] * math.log(a[k] / b[k]) for k in keys
                   if a.get(k, 0) > 1e-12 and b.get(k, 0) > 1e-12)
    return (kl(p, m) + kl(q, m)) / 2


def section_of_versicle(v_name: str) -> str:
    n = int(re.sub(r'\D', '', v_name) or 0)
    for sec_range, sec_name, _ in SECTIONS:
        if n in sec_range:
            return sec_name
    return 'other'


def section_aggregate(versicles: dict, section: str) -> dict[str, float]:
    combined: Counter = Counter()
    total = 0
    for v_name, v_data in versicles.items():
        if section_of_versicle(v_name) != section:
            continue
        for instr in v_data['instructions']:
            m = re.search(r'\|\s*(\w+)', instr)
            if m:
                combined[m.group(1)] += 1
                total += 1
    if total == 0:
        return {mn: 0.0 for mn in ALL_MNEMONICS}
    return {mn: combined.get(mn, 0) / total for mn in ALL_MNEMONICS}


def top_versicles(versicles: dict, n: int) -> list[tuple[str, dict]]:
    scored = []
    for name, data in versicles.items():
        d = versicle_dist(data)
        fsplit = d.get('FSPLIT', 0)
        ffuse  = d.get('FFUSE', 0)
        balance = 1 - abs(fsplit - ffuse)
        scored.append((name, d, balance))
    scored.sort(key=lambda x: -x[2])
    return [(name, d) for name, d, _ in scored[:n]]


def main():
    ap = argparse.ArgumentParser(description='Versicle Topology Comparator — Emerald Tablet')
    ap.add_argument('transcription')
    ap.add_argument('--top-n', type=int, default=10)
    args = ap.parse_args()

    result = compile_corpus(args.transcription)
    versicles = result['versicles']

    print(f"\nEmerald Tablet Versicle Topology Comparator")
    print(f"{'─' * 60}")
    print(f"Versicles: {len(versicles)}  ·  Total instructions: {result['total_instructions']}")

    print(f"\nTop {args.top_n} versicles by Frobenius balance (FSPLIT/FFUSE parity):")
    print(f"  {'Versicle':8s}  {'Section':12s}  {'FSPLIT':7s}  {'FFUSE':7s}  {'CLINK':7s}  {'IMSCRIB':7s}")
    print(f"  {'─' * 60}")
    for v_name, d in top_versicles(versicles, args.top_n):
        sec = section_of_versicle(v_name)
        print(f"  {v_name:8s}  {sec:12s}  "
              f"{d.get('FSPLIT', 0):.3f}    {d.get('FFUSE', 0):.3f}    "
              f"{d.get('CLINK', 0):.3f}    {d.get('IMSCRIB', 0):.3f}")

    SECTION_NAMES = [name for _, name, _ in SECTIONS]
    section_dists = {s: section_aggregate(versicles, s) for s in SECTION_NAMES}

    print(f"\nSection-level primitive distributions (top 6 opcodes):")
    for sec in SECTION_NAMES:
        d = section_dists[sec]
        top = sorted(d.items(), key=lambda x: -x[1])[:6]
        print(f"  {sec:12s}  " + "  ".join(f"{mn}:{pct:.3f}" for mn, pct in top))

    print(f"\nJensen-Shannon divergence between sections:")
    header = f"  {'':12s}" + "".join(f"  {s[:12]:12s}" for s in SECTION_NAMES)
    print(header)
    for a in SECTION_NAMES:
        row = f"  {a:12s}"
        for b in SECTION_NAMES:
            if a == b:
                row += f"  {'0.000':12s}"
            else:
                js = js_divergence(section_dists[a], section_dists[b])
                row += f"  {js:.4f}      "
        print(row)

    print(f"\nNote: Emerald Tablet crystal imscription")
    print(f"  ⟨ Ð_ω  Þ_O  Ř_=  Φ_}}  ƒ_ż  Ç_W  Γ_ʔ  ɢ_ˌ  ⊙_ÿ  Ħ_A  Σ_ï  Ω_z ⟩")
    print(f"  Tier: O_∞  ·  C = 1.0  ·  MEET(ET, OS) = OS imscription")


if __name__ == '__main__':
    main()
