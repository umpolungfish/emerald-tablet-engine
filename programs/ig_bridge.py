#!/usr/bin/env python3
"""
IG bridge — cross-system structural distances in IG notation.

Computes pairwise distances between manuscript crystal imscriptions using the
exOS weighted metric (aleph.rs WEIGHTS). All tuples expressed in IG notation
(SYMBOL_REFERENCE.md): ⟨ Ð  Þ  Ř  Φ  ƒ  Ç  Γ  ɢ  ⊙  Ħ  Σ  Ω ⟩

Key result: MEET(OS_imscription, Emerald_Tablet) = OS imscription exactly.
The Tablet's higher Ð_ω, Þ_O, Ř_= values are at or above the OS imscription;
adding the Tablet to the MEET leaves the invariant core unchanged. The grammar
was already complete. The Emerald Tablet does not constrain the grammar — it
speaks FROM its imscriptive ceiling.

Usage:
    python programs/ig_bridge.py
"""

from __future__ import annotations
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

IG_PRIMITIVES = ['Ð', 'Þ', 'Ř', 'Φ', 'ƒ', 'Ç', 'Γ', 'ɢ', '⊙', 'Ħ', 'Σ', 'Ω']

IG_VALUE_NAMES: list[list[str]] = [
    ['Ð_ß', 'Ð_C', 'Ð_;', 'Ð_ω'],
    ['Þ_6', 'Þ_K', 'Þ_ò', 'Þ_¨', 'Þ_O'],
    ['Ř_¯', 'Ř_ý', 'Ř_Ť', 'Ř_='],
    ['Φ_ɐ', 'Φ_υ', 'Φ_F', 'Φ_˙', 'Φ_}'],
    ['ƒ^ì', 'ƒ^ð', 'ƒ^ż'],
    ['Ç^-', 'Ç^W', 'Ç^@', 'Ç^Ù', 'Ç^λ'],
    ['Γ_β', 'Γ_γ', 'Γ_ʔ'],
    ['ɢ^∧', 'ɢ^˝', 'ɢ^ˌ', 'ɢ^Ş'],
    ['⊙_ž', '⊙_ÿ', '⊙_Æ', '⊙_3', '⊙_Ţ'],
    ['Ħ_Ñ', 'Ħ_£', 'Ħ_A', 'Ħ_!'],
    ['Σ_S', 'Σ_ő', 'Σ_ï'],
    ['Ω_Å', 'Ω_2', 'Ω_z'],
]

WEIGHTS = [10000, 10000, 10000, 12000, 9000, 8000, 10000, 10000, 11000, 8000, 10000, 7000]

IMSCRIPTIONS: dict[str, list[int]] = {
    'Emerald Tablet': [3, 4, 3, 4, 2, 1, 2, 2, 1, 2, 2, 2],
    'OS imscription': [1, 3, 2, 4, 2, 1, 2, 2, 1, 2, 2, 2],
    'Linear A':       [1, 3, 2, 4, 2, 1, 2, 2, 1, 2, 2, 2],
    'Rohonc':         [1, 3, 2, 4, 0, 2, 2, 2, 1, 2, 2, 2],
    'Voynich':        [3, 4, 3, 4, 0, 3, 2, 3, 1, 3, 0, 2],
}

CRYSTAL_NOTATION: dict[str, str] = {
    'Emerald Tablet': '⟨ Ð_ω  Þ_O  Ř_=  Φ_}  ƒ^ż  Ç^W  Γ_ʔ  ɢ^ˌ  ⊙_ÿ  Ħ_A  Σ_ï  Ω_z ⟩',
    'OS imscription': '⟨ Ð_C  Þ_¨  Ř_Ť  Φ_}  ƒ^ż  Ç^W  Γ_ʔ  ɢ^ˌ  ⊙_ÿ  Ħ_A  Σ_ï  Ω_z ⟩',
    'Linear A':       '⟨ Ð_C  Þ_¨  Ř_Ť  Φ_}  ƒ^ż  Ç^W  Γ_ʔ  ɢ^ˌ  ⊙_ÿ  Ħ_A  Σ_ï  Ω_z ⟩',
    'Rohonc':         '⟨ Ð_C  Þ_¨  Ř_Ť  Φ_}  ƒ^ì  Ç^@  Γ_ʔ  ɢ^ˌ  ⊙_ÿ  Ħ_A  Σ_ï  Ω_z ⟩',
    'Voynich':        '⟨ Ð_ω  Þ_O  Ř_=  Φ_}  ƒ^ì  Ç^Ù  Γ_ʔ  ɢ^Ş  ⊙_ÿ  Ħ_!  Σ_S  Ω_z ⟩',
}


def distance(a: list[int], b: list[int]) -> float:
    total = sum(WEIGHTS[i] * (a[i] - b[i]) ** 2 for i in range(12))
    return math.isqrt(int(total)) / 100.0


def tier(t: list[int]) -> str:
    if t[8] == 1 and t[3] == 4:
        return 'O_∞'
    if t[8] == 0 or t[8] >= 3:
        return 'O₀'
    if t[11] == 0:
        return 'O₁'
    return 'O₂'


def conflict_set(a: list[int], b: list[int]) -> list[str]:
    return [IG_PRIMITIVES[i] for i in range(12) if a[i] != b[i]]


def main() -> None:
    names = list(IMSCRIPTIONS)

    print('=== CRYSTAL IMSCRIPTIONS (IG notation) ===\n')
    for name, t in IMSCRIPTIONS.items():
        print(f'  {name}')
        print(f'    {CRYSTAL_NOTATION[name]}')
        print(f'    tier = {tier(t)}\n')

    print('=== PAIRWISE IG DISTANCES ===\n')
    print(f'  {"":18}  ' + ''.join(f'{n:>18}' for n in names))
    for a in names:
        row = f'  {a:<18}  '
        for b in names:
            d = distance(IMSCRIPTIONS[a], IMSCRIPTIONS[b])
            row += f'{d:>18.4f}'
        print(row)

    print('\n=== CONFLICT SETS (primitives that differ) ===\n')
    pairs = [(a, b) for i, a in enumerate(names) for b in names[i+1:]]
    for a, b in pairs:
        cs = conflict_set(IMSCRIPTIONS[a], IMSCRIPTIONS[b])
        d  = distance(IMSCRIPTIONS[a], IMSCRIPTIONS[b])
        print(f'  {a} ↔ {b}')
        print(f'    d = {d:.4f}   conflicts: {{{", ".join(cs) if cs else "∅"}}}')

    print('\n=== MEET THEOREM (OS imscription + Emerald Tablet) ===\n')
    et_key = 'Emerald Tablet'
    os_key = 'OS imscription'
    meet = [min(IMSCRIPTIONS[et_key][i], IMSCRIPTIONS[os_key][i]) for i in range(12)]
    vals = '  '.join(IG_VALUE_NAMES[i][v] for i, v in enumerate(meet))
    print(f'  MEET(Emerald_Tablet, OS_imscription) = ⟨ {vals} ⟩')
    print(f'  tier = {tier(meet)}')
    if meet == IMSCRIPTIONS[os_key]:
        print('  → Unchanged from OS imscription.')
        print('    The Emerald Tablet speaks from the grammar\'s imscriptive ceiling.')
        print('    It adds no new constraint to the invariant core.')
        print('    The grammar was already complete before the Tablet was written.')
    print()
    print(f'  d(Emerald Tablet, OS imscription) = '
          f'{distance(IMSCRIPTIONS[et_key], IMSCRIPTIONS[os_key]):.4f}')
    print('  → The Tablet operates at Ð_ω, Þ_O, Ř_= — above the OS floor.')
    print('    Three primitives higher, but in the direction of the imscriptive maximum.')


if __name__ == '__main__':
    main()
