#!/usr/bin/env python3
"""1D reflection and transmission in vacuum

Run directly from any directory. Edit CONFIG below to change the experiment.
All distances are SI unless a parameter explicitly says cells. See --help.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from fdtd import Config1D, Config2D, Layer
from fdtd.runner import main

CONFIG = Config1D(
    name='05_free_space_spectra',
    title='1D reflection and transmission in vacuum',
    thesis='4.1.7; Figs. 4-12, 4-13; printed pp. 51-52',
    steps=800,
    wavelength=5.32e-07,
    dx=5.3200000000000007e-08,
    source_cell=40,
    spectra=True,
    notes='Run extended to let the reference pulse leave; left monitor is inside the total-field region and baseline-subtracted. Uses 532 nm and dx=lambda/10 from the thesis prose (printed p. 43), rather than the MATLAB draft wavelength.',
)

if __name__ == "__main__":
    main(CONFIG)
