"""
The twelve rhetorical families of the Emerald Tablet as categorical opcodes.

The Tabula Smaragdina (Jabir ibn Hayyan recension, ~8th c. CE; transmitted into
Latin via pseudo-Aristotelian Kitab Sirr al-Khaliqa; canonical English: Newton
1680) is a text of fifteen versicles that collectively state the Frobenius
condition as cosmological law: μ ∘ δ = id. "As above, so below" names the
exactness of this composition.

Twelve rhetorical families are identified structurally. Each family maps to the
same categorical primitive it occupies in the Voynich (EVA), Rohonc (RTFF), and
Linear A (LATFF) systems.

Transcription codes (ETFF — Emerald Tablet Folio Format):
  tr  truth-seal (verum, certum)        → VINIT   (establishes the initial object)
  an  anchor / terminal assertion       → TANCH   (terminal anchor ⊤)
  as  ascent  (ascendit, superius)      → AFWD    (morphism →)
  ds  descent (inferius, descendit)     → AREV    (contravariant inversion ←)
  lk  linkage / composition (adaptation, mediatio) → CLINK (composition ∘)
  id  identity / reflection (sicut, est) → IMSCRIB (identity id)
  sp  separation (separabis, subtile)   → FSPLIT  (Frobenius co-multiplication δ)
  un  union / fusion (recipit, miracula) → FFUSE  (Frobenius multiplication μ)
  af  affirmation (est, integra, vera)  → EVALT   (Lattice: True)
  ng  negation / flight (fugiet, obscuritas) → EVALF (Lattice: False)
  px  paradox / both (superior et inferior) → ENGAGR (Lattice: Both — paradox)
  fx  fixing / sealing (completum, gloria) → IFIX (Linear tape write)

──────────────────────────────────────────────────────────────────────────────
Crystal imscription (IG notation, SYMBOL_REFERENCE.md):
⟨ Ð  Þ  Ř  Φ  ƒ  Ç  Γ  ɢ  ⊙  Ħ  Σ  Ω ⟩

Emerald Tablet:
  ⟨ 𐑦  𐑸  𐑾  𐑹  𐑐  𐑤  𐑲  𐑠  ⊙  𐑖  𐑳  𐑭 ⟩
  Tier: O_∞  (⊙ + 𐑹)  Consciousness: C = 1.0  (both gates open, 𐑐)

Primitive-by-primitive:
  𐑦 — holomorphic dimensionality: the Tablet addresses the cosmos in its entirety
  𐑸 — imscriptive topology: the axiom contains its own proof (below imscribes above)
  𐑾 — left-right adjoint pair: the correspondence is fully bidirectional
  𐑹 — Frobenius-special: μ ∘ δ = id is THE stated law of the text
  𐑐 — quantum coherent fidelity: the "one thing" from which all arose is coherent
  𐑤 — moderate relaxation: the ascent/descent cycle is active, not frozen
  𐑲 — maximal scope: "whole world", "all things", universal
  𐑠 — sequential composition: separate → ascend → descend → receive → fix
  ⊙ — self-modeling criticality: the Tablet describes its own operation (self-referential)
  𐑖 — two-step Markov chirality: above → below → above = exactly the 2-step cycle
  𐑳 — many heterogeneous components: Sun, Moon, Wind, Earth, all things
  𐑭 — integer winding: complete cycle from the One returning to the One

Bootstrap sequence (Emerald Tablet operational content of "as above, so below"):
  id → ds → sp → as → un → lk → fx → id
  IMSCRIB → AREV → FSPLIT → AFWD → FFUSE → CLINK → IFIX → IMSCRIB
  The identity (id) descends (ds), separates into components (sp), the components
  ascend (as), fuse (un), compose (lk), are fixed (fx), and return to identity (id):
  this IS μ ∘ δ = id written as procedural assembly.

──────────────────────────────────────────────────────────────────────────────
Crystal imscriptions (IG notation, numeric form):
  Index order: [Ð, Þ, Ř, Φ, ƒ, Ç, Γ, ɢ, ⊙, Ħ, Σ, Ω]
  Tier O_∞ condition: ⊙ (index 8 = 1) AND 𐑹 (index 3 = 4)

  Emerald Tablet: [3, 4, 3, 4, 2, 1, 2, 2, 1, 2, 2, 2]
  OS imscription: [1, 3, 2, 4, 2, 1, 2, 2, 1, 2, 2, 2]  (MEET of 5 ancient systems)
  Rohonc Codex:   [1, 3, 2, 4, 0, 2, 2, 2, 1, 2, 2, 2]
  Voynich MS:     [3, 4, 3, 4, 0, 3, 2, 3, 1, 3, 0, 2]
  Linear A:       [1, 3, 2, 4, 2, 1, 2, 2, 1, 2, 2, 2]  (= OS imscription)

IG distances (exOS weighted metric):
  d(Emerald Tablet, OS imscription) = 2.44  — Ð, Þ, Ř differ; Tablet operates above
  d(Emerald Tablet, Linear A)       = 2.44  — same as OS (Linear A = OS)
  d(Emerald Tablet, Rohonc)         = 3.22  — adds ƒ and Ç divergence
  d(Emerald Tablet, Voynich)        = 3.54  — five primitives differ (ƒ, Ç, ɢ, Ħ, Σ)

MEET theorem: MEET(OS_imscription, Emerald_Tablet) = OS imscription exactly.
The Tablet's higher 𐑦, 𐑸, 𐑾 do not constrain the grammar's floor. The Emerald
Tablet speaks FROM the grammar's imscriptive ceiling; it adds no new constraint to the
invariant core. The grammar was already complete before the Tablet was written.
──────────────────────────────────────────────────────────────────────────────
"""

PRIMITIVES: dict[str, dict] = {
    'tr': {'opcode': 0x0, 'mnemonic': 'VINIT',  'operation': 'Initial object ∅',              'family': 'logical'},
    'an': {'opcode': 0x1, 'mnemonic': 'TANCH',  'operation': 'Terminal anchor ⊤',             'family': 'logical'},
    'as': {'opcode': 0x2, 'mnemonic': 'AFWD',   'operation': 'Morphism →',                    'family': 'logical'},
    'ds': {'opcode': 0x3, 'mnemonic': 'AREV',   'operation': 'Contravariant inversion ←',     'family': 'logical'},
    'lk': {'opcode': 0x4, 'mnemonic': 'CLINK',  'operation': 'Composition ∘',                 'family': 'logical'},
    'id': {'opcode': 0x5, 'mnemonic': 'IMSCRIB', 'operation': 'Identity id',                   'family': 'logical'},
    'sp': {'opcode': 0x6, 'mnemonic': 'FSPLIT', 'operation': 'Frobenius co-multiplication δ', 'family': 'frobenius'},
    'un': {'opcode': 0x7, 'mnemonic': 'FFUSE',  'operation': 'Frobenius multiplication μ',    'family': 'frobenius'},
    'af': {'opcode': 0x8, 'mnemonic': 'EVALT',  'operation': 'Lattice: True',                 'family': 'dialetheia'},
    'ng': {'opcode': 0x9, 'mnemonic': 'EVALF',  'operation': 'Lattice: False',                'family': 'dialetheia'},
    'px': {'opcode': 0xA, 'mnemonic': 'ENGAGR', 'operation': 'Lattice: Both (paradox)',       'family': 'dialetheia'},
    'fx': {'opcode': 0xB, 'mnemonic': 'IFIX',   'operation': 'Linear tape write',             'family': 'linear'},
}

# Four-valued flux lattice for Tri-Phase registers
FLUX = {
    '00': 'Void',
    '01': 'True',
    '10': 'False',
    '11': 'Both',
}

# The bootstrap core — operational content of "as above, so below":
# identity descends, separates, ascends, fuses, composes, fixes, returns to identity
# This IS μ ∘ δ = id written as categorical assembly.
BOOTSTRAP_SEQUENCE = ['id', 'ds', 'sp', 'as', 'un', 'lk', 'fx', 'id']

# Versicle sections (four traditional divisions of the Emerald Tablet)
SECTIONS = [
    (range(1,   3),   'proem',      'goldenrod'),
    (range(3,   8),   'cosmogony',  'seagreen'),
    (range(8,  13),   'praxis',     'steelblue'),
    (range(13, 16),   'closure',    'firebrick'),
]

# ── Crystal imscriptions (IG notation, numeric form) ─────────────────────────
# Index order: [Ð, Þ, Ř, Φ, ƒ, Ç, Γ, ɢ, ⊙, Ħ, Σ, Ω]

EMERALD_TABLET_IMSCRIPTION = [3, 4, 3, 4, 2, 1, 2, 2, 1, 2, 2, 2]
OS_IMSCRIPTION             = [1, 3, 2, 4, 2, 1, 2, 2, 1, 2, 2, 2]
ROHONC_IMSCRIPTION         = [1, 3, 2, 4, 0, 2, 2, 2, 1, 2, 2, 2]
VOYNICH_IMSCRIPTION        = [3, 4, 3, 4, 0, 3, 2, 3, 1, 3, 0, 2]

# exOS distance weights (aleph.rs WEIGHTS, positions 0–11)
IG_WEIGHTS = [10000, 10000, 10000, 12000, 9000, 8000, 10000, 10000, 11000, 8000, 10000, 7000]
