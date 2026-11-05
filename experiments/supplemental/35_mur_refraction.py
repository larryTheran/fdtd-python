#!/usr/bin/env python3
"""Glass-air refraction with Mur boundaries

Run directly from any directory. Edit CONFIG below to change the experiment.
All distances are SI unless a parameter explicitly says cells. See --help.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from fdtd import Config1D, Config2D, Layer
from fdtd.runner import main

CONFIG = Config2D(
    name='35_mur_refraction',
    title='Glass-air refraction with Mur boundaries',
    thesis='Supplement: refraccionmur.m / Program31',
    nx=400,
    ny=240,
    steps=1600,
    wavelength=1e-05,
    dx=5e-07,
    boundary_x='mur',
    boundary_y='mur',
    geometry='layers',
    background_index=1.5,
    layers=[Layer(start=120, stop=240, epsilon_r=1, sigma=0.0)],
    source='sine',
    injection='beam',
    source_y=20,
    source_width=25,
    angle_deg=35,
    snapshots=(200, 400, 700, 1000),
    notes='First-order Mur replacement for the draft second-order ABC; no artificial magnetic bulk loss. Positive-index conventional dielectric.',
)

if __name__ == "__main__":
    main(CONFIG)
