#!/usr/bin/env python3
"""
Run all Emerald Tablet programs sequentially.

Usage:
    python programs/run_all.py data/emerald_tablet_etff.txt
"""

import subprocess
import sys
from pathlib import Path

DATA = sys.argv[1] if len(sys.argv) > 1 else 'data/emerald_tablet_etff.txt'
BASE = Path(__file__).resolve().parent

programs = [
    ('IG Bridge',             BASE / 'ig_bridge.py',           []),
    ('Bootstrap Explorer',    BASE / 'bootstrap_explorer.py',   [DATA]),
    ('Versicle Comparator',   BASE / 'versicle_comparator.py',  [DATA]),
]

for name, script, extra_args in programs:
    print(f'\n{"═" * 60}')
    print(f'  {name}')
    print(f'{"═" * 60}')
    subprocess.run([sys.executable, str(script)] + extra_args, check=True)

print(f'\n{"═" * 60}')
print('  All programs complete.')
print(f'{"═" * 60}')
