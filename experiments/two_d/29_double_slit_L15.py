#!/usr/bin/env python3
"""Double slit b=10, gap=10, detector distance=15

Run directly from any directory. Edit CONFIG below to change the experiment.
All distances are SI unless a parameter explicitly says cells. See --help.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from fdtd import Config1D, Config2D, Layer
from fdtd.runner import main

CONFIG = Config2D(
    name='29_double_slit_L15',
    title='Double slit b=10, gap=10, detector distance=15',
    thesis='6.1; Figs. 6-10 and 6-11 captions; printed pp. 90-91',
    steps=900,
    boundary_x='periodic',
    geometry='slits',
    source='sine',
    injection='line',
    source_y=45,
    source_width=200,
    wall_y=79,
    slit_count=2,
    detector_y=95,
    snapshots=(100, 150, 220, 300),
    notes='Uses caption dimensions. L=15 is not Fraunhofer for the full 30-cell aperture; report full-aperture Fresnel number. Periodic x represents an aperture array.',
)

if __name__ == "__main__":
    main(CONFIG)
