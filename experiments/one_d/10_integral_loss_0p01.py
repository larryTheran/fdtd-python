#!/usr/bin/env python3
"""1D integral-current loss, sigma=0.01 S/m

Run directly from any directory. Edit CONFIG below to change the experiment.
All distances are SI unless a parameter explicitly says cells. See --help.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from fdtd import Config1D, Config2D, Layer
from fdtd.runner import main

CONFIG = Config1D(
    name='10_integral_loss_0p01',
    title='1D integral-current loss, sigma=0.01 S/m',
    thesis='4.1.10; Fig. 4-19; printed p. 62',
    cells=400,
    steps=3000,
    wavelength=0.1224744871391589,
    dx=0.01,
    source_cell=19,
    layers=[Layer(start=149, stop=300, epsilon_r=1.5, sigma=0.01)],
    loss_model='integral',
    spectra=True,
    snapshots=(250, 350, 550, 1300),
    notes='D/E/I conductive model with corrected positive denominator. Consistent cm-grid reinterpretation; original optical labels conflicted with the actual time step. No fitted 70% or 90% loss target.',
)

if __name__ == "__main__":
    main(CONFIG)
