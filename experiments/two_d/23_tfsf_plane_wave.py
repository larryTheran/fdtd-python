#!/usr/bin/env python3
"""2D one-way plane wave using TF/SF

Run directly from any directory. Edit CONFIG below to change the experiment.
All distances are SI unless a parameter explicitly says cells. See --help.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from fdtd import Config1D, Config2D, Layer
from fdtd.runner import main

CONFIG = Config2D(
    name='23_tfsf_plane_wave',
    title='2D one-way plane wave using TF/SF',
    thesis='2D/FDTD_2D_2 TF/SF draft and Untitled7.m',
    steps=700,
    wavelength=0.00599584916,
    dx=0.0003461705126546392,
    boundary_x='periodic',
    source='gaussian',
    injection='tfsf',
    spectra=True,
    snapshots=(100, 200, 400, 700),
)

if __name__ == "__main__":
    main(CONFIG)
