#!/usr/bin/env python3
"""3D PML in x, periodic in y — full-vector 3D

Independent 3D counterpart; edit CONFIG or see --help.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from fdtd.config import Layer
from fdtd.three_d import Config3D
from fdtd.three_d_runner import main

CONFIG = Config3D(
    name='20_pml_x_periodic_y_3d',
    title='3D PML in x, periodic in y — full-vector 3D',
    thesis='5.1.6; Fig. 5-11; printed p. 80',
    nx=200,
    ny=200,
    steps=700,
    wavelength=5.32e-07,
    points_per_wavelength=10.0,
    dx=5.3200000000000007e-08,
    dy=None,
    courant=0.5,
    boundary_x='pml',
    boundary_y='periodic',
    pml_cells=30,
    pml_reflection=1e-08,
    geometry='free',
    background_index=1.0,
    layers=[],
    source='modulated',
    injection='point',
    source_x=99,
    source_y=99,
    source_width=60.0,
    angle_deg=0.0,
    tau_periods=0.5,
    wall_y=80,
    wall_thickness=2,
    slit_count=1,
    slit_width=10,
    slit_gap=10,
    detector_y=None,
    average_cycles=8,
    spectra=False,
    snapshots=(100, 180, 300, 401, 700),
    bend_radius=2e-05,
    bend_width=7.75e-07,
    bend_core_index=1.9,
    notes=' Uses the 532 nm wavelength from thesis printed p. 72, rather than 50 GHz in the exploratory MATLAB files. Added z depth is 64 cells, dz=dx, with 12-cell z PML. The x-y geometry, grid spacing and time-step count are preserved.',
    nz=64,
    dz=None,
    boundary_z='pml',
    pml_cells_z=12,
    source_z=None,
    source_width_z=16,
    slit_height=24,
    bend_height=7.75e-07,
    substrate_index=1.52,
    cladding_index=1.0,
    backend='auto',
    energy_stride=10,
    origin_2d='experiments/two_d/20_pml_x_periodic_y.py',
)

if __name__ == "__main__":
    main(CONFIG)
