#!/usr/bin/env python3
"""Glass-air refraction with Mur boundaries — full-vector 3D

Independent 3D counterpart; edit CONFIG or see --help.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from fdtd.config import Layer
from fdtd.three_d import Config3D
from fdtd.three_d_runner import main

CONFIG = Config3D(
    name='35_mur_refraction_3d',
    title='Glass-air refraction with Mur boundaries — full-vector 3D',
    thesis='Supplement: refraccionmur.m / Program31',
    nx=400,
    ny=240,
    steps=1600,
    wavelength=1e-05,
    points_per_wavelength=10.0,
    dx=5e-07,
    dy=None,
    courant=0.5,
    boundary_x='mur',
    boundary_y='mur',
    pml_cells=30,
    pml_reflection=1e-08,
    geometry='layers',
    background_index=1.5,
    layers=[Layer(start=120, stop=240, epsilon_r=1, sigma=0.0)],
    source='sine',
    injection='beam',
    source_x=100,
    source_y=20,
    source_width=25,
    angle_deg=35,
    tau_periods=0.5,
    wall_y=80,
    wall_thickness=2,
    slit_count=1,
    slit_width=10,
    slit_gap=10,
    detector_y=None,
    average_cycles=8,
    spectra=False,
    snapshots=(200, 400, 700, 1000),
    bend_radius=2e-05,
    bend_width=7.75e-07,
    bend_core_index=1.9,
    notes='First-order Mur replacement for the draft second-order ABC; no artificial magnetic bulk loss. Positive-index conventional dielectric. First-order Mur on all six faces; finite Gaussian beam in x-z. Depth is 64 cells.',
    nz=64,
    dz=None,
    boundary_z='mur',
    pml_cells_z=12,
    source_z=None,
    source_width_z=16,
    slit_height=24,
    bend_height=7.75e-07,
    substrate_index=1.52,
    cladding_index=1.0,
    backend='auto',
    energy_stride=10,
    origin_2d='experiments/supplemental/35_mur_refraction.py',
)

if __name__ == "__main__":
    main(CONFIG)
