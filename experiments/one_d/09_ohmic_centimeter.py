#!/usr/bin/env python3
"""1D Ohmic attenuation on the legacy cm grid

Run directly from any directory. Edit CONFIG below to change the experiment.
All distances are SI unless a parameter explicitly says cells. See --help.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from fdtd import Config1D, Config2D, Layer
from fdtd.runner import main

CONFIG = Config1D(
    name='09_ohmic_centimeter',
    title='1D Ohmic attenuation on the legacy cm grid',
    thesis='4.1.9; Fig. 4-18 visual reconstruction',
    cells=400,
    steps=2000,
    wavelength=0.2,
    dx=0.01,
    source_cell=9,
    layers=[Layer(start=149, stop=300, epsilon_r=4, sigma=0.04)],
    spectra=True,
    snapshots=(200, 350, 400, 550),
    notes='Consistent microwave reinterpretation: dx=1 cm, lambda=20 cm, sigma=0.04 S/m. This is not an optical simulation.',
)

if __name__ == "__main__":
    main(CONFIG)
