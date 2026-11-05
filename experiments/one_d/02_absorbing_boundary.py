#!/usr/bin/env python3
"""1D pulse with the thesis delay ABC

Run directly from any directory. Edit CONFIG below to change the experiment.
All distances are SI unless a parameter explicitly says cells. See --help.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from fdtd import Config1D, Config2D, Layer
from fdtd.runner import main

CONFIG = Config1D(
    name='02_absorbing_boundary',
    title='1D pulse with the thesis delay ABC',
    thesis='4.1.5; Fig. 4-7; printed p. 45',
    wavelength=5.32e-07,
    dx=5.3200000000000007e-08,
    injection='soft',
    notes='The thesis calls this PEC. It is a two-step delay absorbing boundary at S=0.5. Uses 532 nm and dx=lambda/10 from the thesis prose (printed p. 43), rather than the MATLAB draft wavelength.',
)

if __name__ == "__main__":
    main(CONFIG)
