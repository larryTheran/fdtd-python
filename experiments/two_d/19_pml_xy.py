#!/usr/bin/env python3
"""2D pulse with PML on all four sides

Run directly from any directory. Edit CONFIG below to change the experiment.
All distances are SI unless a parameter explicitly says cells. See --help.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from fdtd import Config1D, Config2D, Layer
from fdtd.runner import main

CONFIG = Config2D(
    name='19_pml_xy',
    title='2D pulse with PML on all four sides',
    thesis='5.1.6; Fig. 5-10; printed p. 79',
    steps=700,
    dx=5.3200000000000007e-08,
    source_x=99,
    source_y=99,
    snapshots=(100, 180, 300, 401, 700),
    notes=' Uses the 532 nm wavelength from thesis printed p. 72, rather than 50 GHz in the exploratory MATLAB files.',
)

if __name__ == "__main__":
    main(CONFIG)
