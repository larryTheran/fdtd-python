#!/usr/bin/env python3
"""1D two lossless dielectric layers

Run directly from any directory. Edit CONFIG below to change the experiment.
All distances are SI unless a parameter explicitly says cells. See --help.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from fdtd import Config1D, Config2D, Layer
from fdtd.runner import main

CONFIG = Config1D(
    name='06_lossless_two_layers',
    title='1D two lossless dielectric layers',
    thesis='4.1.8; Figs. 4-14 to 4-17; printed pp. 53-55',
    cells=400,
    steps=4000,
    wavelength=5.32e-07,
    source_cell=9,
    layers=[Layer(start=149, stop=249, epsilon_r=2, sigma=0.0), Layer(start=249, stop=300, epsilon_r=4, sigma=0.0)],
    spectra=True,
    snapshots=(300, 900, 2000, 4000),
    notes='Uses the thesis 532 nm rather than the draft 500 nm. 1-R-T is a finite-record spectral residual, not instantaneous stored energy.',
)

if __name__ == "__main__":
    main(CONFIG)
