#!/usr/bin/env python3
"""1D alternating dielectric stack at 5 GHz

Run directly from any directory. Edit CONFIG below to change the experiment.
All distances are SI unless a parameter explicitly says cells. See --help.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from fdtd import Config1D, Config2D, Layer
from fdtd.runner import main

CONFIG = Config1D(
    name='13_periodic_dielectric_stack',
    title='1D alternating dielectric stack at 5 GHz',
    thesis='1D/FDTD_1D_8/FDTD_1D_Dielectrico_periodico.m',
    cells=1000,
    steps=64000,
    wavelength=0.0599584916,
    dx=0.002631578947368421,
    source_cell=9,
    layers=[Layer(start=99, stop=199, epsilon_r=5, sigma=0.0), Layer(start=199, stop=299, epsilon_r=2, sigma=0.0), Layer(start=299, stop=399, epsilon_r=5, sigma=0.0), Layer(start=399, stop=499, epsilon_r=2, sigma=0.0), Layer(start=499, stop=599, epsilon_r=5, sigma=0.0), Layer(start=599, stop=699, epsilon_r=2, sigma=0.0), Layer(start=699, stop=799, epsilon_r=5, sigma=0.0), Layer(start=799, stop=900, epsilon_r=2, sigma=0.0)],
    spectra=True,
    snapshots=(250, 600, 1200, 3000, 64000),
    notes='Periodic MATERIAL stack, open boundaries. Extended beyond the broken MATLAB 1000-sample source buffer and 3000-step loop to 64000 steps to capture high-Q resonances and delayed transmission; finite-record conservation checked.',
)

if __name__ == "__main__":
    main(CONFIG)
