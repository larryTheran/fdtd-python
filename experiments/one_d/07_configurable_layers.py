#!/usr/bin/env python3
"""1D configurable dielectric stack

Run directly from any directory. Edit CONFIG below to change the experiment.
All distances are SI unless a parameter explicitly says cells. See --help.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from fdtd import Config1D, Config2D, Layer
from fdtd.runner import main

CONFIG = Config1D(
    name='07_configurable_layers',
    title='1D configurable dielectric stack',
    thesis='1D/FDTD_1D_5 MATLAB extension of 4.1.8',
    cells=400,
    steps=4000,
    wavelength=5.3e-07,
    source_cell=9,
    layers=[Layer(start=149, stop=199, epsilon_r=2, sigma=0.0), Layer(start=199, stop=249, epsilon_r=4, sigma=0.0), Layer(start=249, stop=300, epsilon_r=2, sigma=0.0)],
    spectra=True,
    snapshots=(300, 900, 2000, 4000),
    notes='Edit the Layer list to set any number of slabs; replaces interactive MATLAB input prompts.',
)

if __name__ == "__main__":
    main(CONFIG)
