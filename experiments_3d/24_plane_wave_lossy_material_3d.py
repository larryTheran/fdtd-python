#!/usr/bin/env python3
"""3D plane wave entering a lossy dielectric — full-vector 3D

Independent 3D counterpart; edit CONFIG or see --help.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from fdtd.config import Layer
from fdtd.three_d import Config3D
from fdtd.three_d_runner import main

CONFIG = Config3D(
    name='24_plane_wave_lossy_material_3d',
    title='3D plane wave entering a lossy dielectric — full-vector 3D',
    thesis='2D/FDTD_2D_2 material_onda_plana.m',
    nx=200,
    ny=400,
    steps=1800,
    wavelength=0.00599584916,
    points_per_wavelength=10.0,
    dx=0.0003461705126546392,
    dy=None,
    courant=0.5,
    boundary_x='periodic',
    boundary_y='pml',
    pml_cells=30,
    pml_reflection=1e-08,
    geometry='layers',
    background_index=1.0,
    layers=[Layer(start=200, stop=400, epsilon_r=1.5, sigma=0.1)],
    source='sine',
    injection='line',
    source_x=100,
    source_y=50,
    source_width=200,
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
    snapshots=(200, 500, 1000, 1800),
    bend_radius=2e-05,
    bend_width=7.75e-07,
    bend_core_index=1.9,
    notes=' Uniform x-z source sheet; periodic z with eight cells gives the depth-independent plane-wave calibration limit of the six-component solver.',
    nz=8,
    dz=None,
    boundary_z='periodic',
    pml_cells_z=12,
    source_z=None,
    source_width_z=16,
    slit_height=24,
    bend_height=7.75e-07,
    substrate_index=1.52,
    cladding_index=1.0,
    backend='auto',
    energy_stride=10,
    origin_2d='experiments/two_d/24_plane_wave_lossy_material.py',
)

if __name__ == "__main__":
    main(CONFIG)
