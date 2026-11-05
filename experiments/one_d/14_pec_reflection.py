#!/usr/bin/env python3
"""1D reflection from actual PEC endpoints

Run directly from any directory. Edit CONFIG below to change the experiment.
All distances are SI unless a parameter explicitly says cells. See --help.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from fdtd import Config1D, Config2D, Layer
from fdtd.runner import main

CONFIG = Config1D(
    name='14_pec_reflection',
    title='1D reflection from actual PEC endpoints',
    thesis='Supplement: clarify boundary terminology in 4.1.5',
    steps=600,
    boundary='pec',
    injection='soft',
    snapshots=(100, 200, 300, 450, 600),
)

if __name__ == "__main__":
    main(CONFIG)
