#!/usr/bin/env python3
"""2D Gaussian point pulse

Run directly from any directory. Edit CONFIG below to change the experiment.
All distances are SI unless a parameter explicitly says cells. See --help.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from fdtd import Config1D, Config2D, Layer
from fdtd.runner import main

CONFIG = Config2D(
    name='17_free_space_gaussian',
    title='2D Gaussian point pulse',
    thesis='2D/FDTD_2D_1/FDTD_2D_libre.m',
    steps=350,
    wavelength=0.00599584916,
    dx=0.0003461705126546392,
    boundary_x='pec',
    boundary_y='pec',
    source='gaussian',
    snapshots=(100, 150, 250, 350),
)

if __name__ == "__main__":
    main(CONFIG)
