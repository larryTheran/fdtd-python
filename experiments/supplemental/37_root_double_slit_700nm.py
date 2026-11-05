#!/usr/bin/env python3
"""Double slit from the root FDTD2D.m

Run directly from any directory. Edit CONFIG below to change the experiment.
All distances are SI unless a parameter explicitly says cells. See --help.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from fdtd import Config1D, Config2D, Layer
from fdtd.runner import main

CONFIG = Config2D(
    name='37_root_double_slit_700nm',
    title='Double slit from the root FDTD2D.m',
    thesis='Supplement: root FDTD2D.m',
    nx=400,
    ny=400,
    steps=1600,
    wavelength=7e-07,
    dx=4.117e-08,
    pml_cells=50,
    geometry='slits',
    background_index=1.4142135623730951,
    source='sine',
    injection='line',
    source_x=200,
    source_y=100,
    source_width=200,
    wall_y=149,
    slit_count=2,
    slit_width=2,
    slit_gap=5,
    detector_y=240,
    snapshots=(300, 600, 900, 1200),
    notes='Rotated to +y propagation. Integer sampled legacy intervals correspond to two 2-cell openings and a 5-cell opaque gap despite Ancho=5/Separacion=5. PEC replaces the 5.7e8 S/m obstacle; tiny background loss omitted.',
)

if __name__ == "__main__":
    main(CONFIG)
