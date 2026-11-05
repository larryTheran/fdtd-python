#!/usr/bin/env python3
"""2D plane wave from an aligned source array

Run directly from any directory. Edit CONFIG below to change the experiment.
All distances are SI unless a parameter explicitly says cells. See --help.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from fdtd import Config1D, Config2D, Layer
from fdtd.runner import main

CONFIG = Config2D(
    name='22_huygens_plane_wave',
    title='2D plane wave from an aligned source array',
    thesis='5.2; Fig. 5-13; printed p. 81',
    steps=700,
    dx=5.3200000000000007e-08,
    boundary_x='periodic',
    source='sine',
    injection='line',
    source_x=99,
    source_y=149,
    source_width=200,
    snapshots=(100, 200, 400, 700),
    notes='Sources span x and propagate along y, so x is periodic and y is PML. The thesis caption swaps these axes. Uses the 532 nm wavelength from thesis printed p. 72, rather than 50 GHz in the exploratory MATLAB files.',
)

if __name__ == "__main__":
    main(CONFIG)
