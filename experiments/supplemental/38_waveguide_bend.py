#!/usr/bin/env python3
"""Effective-index waveguide bend

Run directly from any directory. Edit CONFIG below to change the experiment.
All distances are SI unless a parameter explicitly says cells. See --help.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from fdtd import Config1D, Config2D, Layer
from fdtd.runner import main

CONFIG = Config2D(
    name='38_waveguide_bend',
    title='Effective-index waveguide bend',
    thesis='Supplement: unfinished 2D/FDTD_2D_3/Untitled8.m',
    nx=430,
    ny=430,
    steps=4200,
    wavelength=1.55e-06,
    dx=8.157894736842106e-08,
    pml_cells=40,
    geometry='bend',
    source='sine',
    injection='mode',
    source_x=65,
    source_y=45,
    snapshots=(400, 1200, 2400, 4200),
    notes='Reconstruction of intended 20 um-radius, 0.775 um-width bend. Includes a scalar eigenmode solver to replace missing ezmode; no claim of exact agreement with the incomplete 3D effective-index prototype.',
)

if __name__ == "__main__":
    main(CONFIG)
