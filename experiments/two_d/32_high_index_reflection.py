#!/usr/bin/env python3
"""Reflection and transmission from n=1.5 to n=4

Run directly from any directory. Edit CONFIG below to change the experiment.
All distances are SI unless a parameter explicitly says cells. See --help.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from fdtd import Config1D, Config2D, Layer
from fdtd.runner import main

CONFIG = Config2D(
    name='32_high_index_reflection',
    title='Reflection and transmission from n=1.5 to n=4',
    thesis='6.2; Fig. 6-15; printed p. 95',
    nx=250,
    ny=300,
    steps=1800,
    dx=1.3300000000000002e-08,
    geometry='layers',
    background_index=1.5,
    layers=[Layer(start=150, stop=300, epsilon_r=16, sigma=0.0)],
    source='sine',
    injection='beam',
    source_x=60,
    source_y=40,
    source_width=24,
    angle_deg=40,
    snapshots=(200, 400, 700, 1000),
    notes='The specified n=1.5 to n=4 interface only partially reflects. It cannot produce total internal reflection. A separate PEC example supplies the ideal specular mirror.',
)

if __name__ == "__main__":
    main(CONFIG)
