#!/usr/bin/env python3
"""Diagonal array of equal-phase point sources

Run directly from any directory. Edit CONFIG below to change the experiment.
All distances are SI unless a parameter explicitly says cells. See --help.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from fdtd import Config1D, Config2D, Layer
from fdtd.runner import main

CONFIG = Config2D(
    name='36_diagonal_huygens_array',
    title='Diagonal array of equal-phase point sources',
    thesis='Supplement: refraccionlarry.m and nuevo/Untitled2.m',
    nx=400,
    ny=400,
    steps=1000,
    wavelength=7e-07,
    source='sine',
    injection='diagonal',
    source_x=149,
    source_y=149,
    source_width=20,
    snapshots=(100, 250, 500, 1000),
    notes='Source-only prototype: no refraction interface is active in refraccionlarry.m.',
)

if __name__ == "__main__":
    main(CONFIG)
