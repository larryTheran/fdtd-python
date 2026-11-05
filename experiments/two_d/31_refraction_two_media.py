#!/usr/bin/env python3
"""Refraction from n=1.5 to n=2.1

Run directly from any directory. Edit CONFIG below to change the experiment.
All distances are SI unless a parameter explicitly says cells. See --help.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from fdtd import Config1D, Config2D, Layer
from fdtd.runner import main

CONFIG = Config2D(
    name='31_refraction_two_media',
    title='Refraction from n=1.5 to n=2.1',
    thesis='6.2; Fig. 6-14; printed p. 94',
    nx=250,
    ny=300,
    steps=1800,
    dx=2.1280000000000003e-08,
    geometry='layers',
    background_index=1.5,
    layers=[Layer(start=150, stop=300, epsilon_r=4.41, sigma=0.0)],
    source='sine',
    injection='beam',
    source_x=60,
    source_y=40,
    source_width=24,
    angle_deg=40,
    snapshots=(200, 400, 700, 1000),
    notes='532 nm from thesis; 25 vacuum cells/wavelength. Finite phased beam replaces the under-resolved draft source. Angles are measured from +y; epsilon_r=n^2.',
)

if __name__ == "__main__":
    main(CONFIG)
