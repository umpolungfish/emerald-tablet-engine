"""Emerald Tablet Engine — Universal Imscriptive Grammar compilation of the Tabula Smaragdina."""

from .compiler import compile_corpus, peak_versicles, write_log
from .runtime import UniversalEngine
from .callgraph import generate_call_graph
from .sectional import generate_sectional_graphs, classify_versicle
from .primitives import (
    PRIMITIVES, FLUX, BOOTSTRAP_SEQUENCE, SECTIONS,
    EMERALD_TABLET_IMSCRIPTION, OS_IMSCRIPTION, IG_WEIGHTS,
)

__all__ = [
    'compile_corpus',
    'peak_versicles',
    'write_log',
    'UniversalEngine',
    'generate_call_graph',
    'generate_sectional_graphs',
    'classify_versicle',
    'PRIMITIVES',
    'FLUX',
    'BOOTSTRAP_SEQUENCE',
    'SECTIONS',
    'EMERALD_TABLET_IMSCRIPTION',
    'OS_IMSCRIPTION',
    'IG_WEIGHTS',
]
