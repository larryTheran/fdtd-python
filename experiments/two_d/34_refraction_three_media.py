#!/usr/bin/env python3
"""Refraction through n=1.5 / 2.5 / 1.5

Run directly from any directory. Edit CONFIG below to change the experiment.
All distances are SI unless a parameter explicitly says cells. See --help.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from fdtd import Config1D, Config2D, Layer
from fdtd.runner import main

CONFIG = Config2D(
    name='34_refraction_three_media',
    title='Refraction through n=1.5 / 2.5 / 1.5',
    thesis='6.2; Fig. 6-16; printed p. 96',
    nx=250,
    ny=300,
    steps=2200,
    dx=2.1280000000000003e-08,
    geometry='layers',
    background_index=1.5,
    layers=[Layer(start=100, stop=200, epsilon_r=6.25, sigma=0.0), Layer(start=200, stop=300, epsilon_r=2.25, sigma=0.0)],
    source='sine',
    injection='beam',
    source_x=60,
    source_y=40,
    source_width=24,
    angle_deg=40,
    snapshots=(200, 700, 1000, 1500),
    notes='Three dielectric regions with parallel interfaces; first and last index are equal. Run extended to sample the final region.',
)

if __name__ == "__main__":
    main(CONFIG)
