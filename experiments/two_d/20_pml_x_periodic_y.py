#!/usr/bin/env python3
"""2D PML in x, periodic in y

Run directly from any directory. Edit CONFIG below to change the experiment.
All distances are SI unless a parameter explicitly says cells. See --help.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from fdtd import Config1D, Config2D, Layer
from fdtd.runner import main

CONFIG = Config2D(
    name='20_pml_x_periodic_y',
    title='2D PML in x, periodic in y',
    thesis='5.1.6; Fig. 5-11; printed p. 80',
    steps=700,
    dx=5.3200000000000007e-08,
    boundary_y='periodic',
    source_x=99,
    source_y=99,
    snapshots=(100, 180, 300, 401, 700),
    notes=' Uses the 532 nm wavelength from thesis printed p. 72, rather than 50 GHz in the exploratory MATLAB files.',
)

if __name__ == "__main__":
    main(CONFIG)
