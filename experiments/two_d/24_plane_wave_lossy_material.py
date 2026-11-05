#!/usr/bin/env python3
"""2D plane wave entering a lossy dielectric

Run directly from any directory. Edit CONFIG below to change the experiment.
All distances are SI unless a parameter explicitly says cells. See --help.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from fdtd import Config1D, Config2D, Layer
from fdtd.runner import main

CONFIG = Config2D(
    name='24_plane_wave_lossy_material',
    title='2D plane wave entering a lossy dielectric',
    thesis='2D/FDTD_2D_2 material_onda_plana.m',
    ny=400,
    steps=1800,
    wavelength=0.00599584916,
    dx=0.0003461705126546392,
    boundary_x='periodic',
    geometry='layers',
    layers=[Layer(start=200, stop=400, epsilon_r=1.5, sigma=0.1)],
    source='sine',
    injection='line',
    source_width=200,
    snapshots=(200, 500, 1000, 1800),
)

if __name__ == "__main__":
    main(CONFIG)
