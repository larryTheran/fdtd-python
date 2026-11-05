#!/usr/bin/env python3
"""1D Ohmic loss at optical SI scales

Run directly from any directory. Edit CONFIG below to change the experiment.
All distances are SI unless a parameter explicitly says cells. See --help.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from fdtd import Config1D, Config2D, Layer
from fdtd.runner import main

CONFIG = Config1D(
    name='08_ohmic_optical',
    title='1D Ohmic loss at optical SI scales',
    thesis='4.1.9; Fig. 4-18 parameters; printed p. 58',
    cells=400,
    steps=4000,
    source_cell=9,
    layers=[Layer(start=149, stop=300, epsilon_r=4, sigma=0.04)],
    spectra=True,
    snapshots=(200, 350, 400, 550),
    notes='Literal sigma=0.04 S/m at 500 nm gives very weak loss. The original visible attenuation used a later dx=0.01 m override; see experiment 09.',
)

if __name__ == "__main__":
    main(CONFIG)
