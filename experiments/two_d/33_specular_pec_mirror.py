#!/usr/bin/env python3
"""Specular reflection from an ideal PEC mirror

Run directly from any directory. Edit CONFIG below to change the experiment.
All distances are SI unless a parameter explicitly says cells. See --help.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from fdtd import Config1D, Config2D, Layer
from fdtd.runner import main

CONFIG = Config2D(
    name='33_specular_pec_mirror',
    title='Specular reflection from an ideal PEC mirror',
    thesis='6.2; intended ideal reflector in Fig. 6-15',
    nx=250,
    ny=300,
    steps=1800,
    dx=2.1280000000000003e-08,
    geometry='mirror',
    background_index=1.5,
    source='sine',
    injection='beam',
    source_x=60,
    source_y=40,
    source_width=24,
    angle_deg=40,
    wall_y=150,
    snapshots=(200, 400, 700, 1000),
    notes='Ideal PEC produces full reflection. This is a correction of the intended ideal-mirror experiment, not a claim that n=4 is a perfect conductor.',
)

if __name__ == "__main__":
    main(CONFIG)
