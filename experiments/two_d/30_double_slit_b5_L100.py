#!/usr/bin/env python3
"""Double slit b=5 with a distant detector

Run directly from any directory. Edit CONFIG below to change the experiment.
All distances are SI unless a parameter explicitly says cells. See --help.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from fdtd import Config1D, Config2D, Layer
from fdtd.runner import main

CONFIG = Config2D(
    name='30_double_slit_b5_L100',
    title='Double slit b=5 with a distant detector',
    thesis='6.1; prose following Fig. 6-9; printed pp. 89-90',
    nx=300,
    ny=300,
    steps=1200,
    geometry='slits',
    source='sine',
    injection='line',
    source_x=150,
    source_y=45,
    source_width=300,
    wall_y=79,
    slit_count=2,
    slit_width=5,
    detector_y=180,
    snapshots=(100, 200, 400, 1200),
    notes='Preserves the separate prose case b=5 and L=100; captions specify a different b=10 case.',
)

if __name__ == "__main__":
    main(CONFIG)
