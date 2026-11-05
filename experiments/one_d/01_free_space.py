#!/usr/bin/env python3
"""1D free-space pulse with zero exterior ghosts

Run directly from any directory. Edit CONFIG below to change the experiment.
All distances are SI unless a parameter explicitly says cells. See --help.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from fdtd import Config1D, Config2D, Layer
from fdtd.runner import main

CONFIG = Config1D(
    name='01_free_space',
    title='1D free-space pulse with zero exterior ghosts',
    thesis='4.1.4; Fig. 4-5; printed p. 42',
    wavelength=5.32e-07,
    dx=5.3200000000000007e-08,
    boundary='zero',
    injection='soft',
    notes='Corrected last-cell index from sin_nada_modi. Zero ghosts reflect; they are not an absorbing boundary. Uses 532 nm and dx=lambda/10 from the thesis prose (printed p. 43), rather than the MATLAB draft wavelength.',
)

if __name__ == "__main__":
    main(CONFIG)
