#!/usr/bin/env python3
"""1D integral-current loss at optical SI scales

Run directly from any directory. Edit CONFIG below to change the experiment.
All distances are SI unless a parameter explicitly says cells. See --help.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from fdtd import Config1D, Config2D, Layer
from fdtd.runner import main

CONFIG = Config1D(
    name='12_integral_loss_optical',
    title='1D integral-current loss at optical SI scales',
    thesis='4.1.10; optical interpretation of Figs. 4-19 and 4-20',
    cells=400,
    steps=3000,
    source_cell=19,
    layers=[Layer(start=149, stop=300, epsilon_r=1.5, sigma=0.01)],
    loss_model='integral',
    spectra=True,
    snapshots=(250, 350, 550, 1300),
    notes='Same SI conductivity as Fig. 4-19, with a consistently optical time grid; not a Debye, Drude or Lorentz dispersive model.',
)

if __name__ == "__main__":
    main(CONFIG)
