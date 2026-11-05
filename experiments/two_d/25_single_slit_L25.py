#!/usr/bin/env python3
"""Single slit b=10, detector distance=25 cells

Run directly from any directory. Edit CONFIG below to change the experiment.
All distances are SI unless a parameter explicitly says cells. See --help.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from fdtd import Config1D, Config2D, Layer
from fdtd.runner import main

CONFIG = Config2D(
    name='25_single_slit_L25',
    title='Single slit b=10, detector distance=25 cells',
    thesis='6.1; Figs. 6-2 to 6-4; printed pp. 84-86',
    steps=900,
    boundary_x='periodic',
    geometry='slits',
    source='sine',
    injection='line',
    source_y=45,
    source_width=200,
    wall_y=79,
    detector_y=105,
    snapshots=(100, 150, 220, 300),
    notes='10 cells per vacuum wavelength; exact PEC obstacle; detector distance measured from the exit face. Periodic x represents repeated apertures and can affect late-time patterns.',
)

if __name__ == "__main__":
    main(CONFIG)
