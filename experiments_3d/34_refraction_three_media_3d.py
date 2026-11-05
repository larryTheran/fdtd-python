#!/usr/bin/env python3
"""Refraction through n=1.5 / 2.5 / 1.5 — full-vector 3D

Independent 3D counterpart; edit CONFIG or see --help.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from fdtd.config import Layer
from fdtd.three_d import Config3D
from fdtd.three_d_runner import main

CONFIG = Config3D(
    name='34_refraction_three_media_3d',
    title='Refraction through n=1.5 / 2.5 / 1.5 — full-vector 3D',
    thesis='6.2; Fig. 6-16; printed p. 96',
    nx=250,
    ny=300,
    steps=2200,
    wavelength=5.32e-07,
    points_per_wavelength=10.0,
    dx=2.1280000000000003e-08,
    dy=None,
    courant=0.5,
    boundary_x='pml',
    boundary_y='pml',
    pml_cells=30,
    pml_reflection=1e-08,
    geometry='layers',
    background_index=1.5,
    layers=[Layer(start=100, stop=200, epsilon_r=6.25, sigma=0.0), Layer(start=200, stop=300, epsilon_r=2.25, sigma=0.0)],
    source='sine',
    injection='beam',
    source_x=60,
    source_y=40,
    source_width=24,
    angle_deg=40,
    tau_periods=0.5,
    wall_y=80,
    wall_thickness=2,
    slit_count=1,
    slit_width=10,
    slit_gap=10,
    detector_y=None,
    average_cycles=8,
    spectra=False,
    snapshots=(200, 700, 1000, 1500),
    bend_radius=2e-05,
    bend_width=7.75e-07,
    bend_core_index=1.9,
    notes='Three dielectric regions with parallel interfaces; first and last index are equal. Run extended to sample the final region. Added z depth is 64 cells, dz=dx, with 12-cell z PML. The x-y geometry, grid spacing and time-step count are preserved. Gaussian beam in both transverse dimensions; x phase delay preserves the original incidence angle.',
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
    origin_2d='experiments/two_d/34_refraction_three_media.py',
)

if __name__ == "__main__":
    main(CONFIG)
