#!/usr/bin/env python3
"""Single slit with extended observation region

Run directly from any directory. Edit CONFIG below to change the experiment.
All distances are SI unless a parameter explicitly says cells. See --help.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from fdtd import Config1D, Config2D, Layer
from fdtd.runner import main

CONFIG = Config2D(
    name='27_single_slit_far_field',
    title='Single slit with extended observation region',
    thesis='6.1; Figs. 6-5 to 6-7; printed pp. 87-88',
    nx=400,
    ny=500,
    steps=1700,
    geometry='slits',
    source='sine',
    injection='line',
    source_x=200,
    source_y=45,
    source_width=400,
    wall_y=79,
    detector_y=380,
    snapshots=(150, 300, 755, 1700),
    notes='Extended domain with all-side PML to suppress replicas. Chosen L=300 cells gives full-aperture Fresnel number 0.033; exact L is not specified for Fig. 6-7.',
)

if __name__ == "__main__":
    main(CONFIG)
