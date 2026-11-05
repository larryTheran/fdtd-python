#!/usr/bin/env python3
"""3D one-way plane wave using TF/SF — full-vector 3D

Independent 3D counterpart; edit CONFIG or see --help.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from fdtd.config import Layer
from fdtd.three_d import Config3D
from fdtd.three_d_runner import main

CONFIG = Config3D(
    name='23_tfsf_plane_wave_3d',
    title='3D one-way plane wave using TF/SF — full-vector 3D',
    thesis='2D/FDTD_2D_2 TF/SF draft and Untitled7.m',
    nx=200,
    ny=200,
    steps=700,
    wavelength=0.00599584916,
    points_per_wavelength=10.0,
    dx=0.0003461705126546392,
    dy=None,
    courant=0.5,
    boundary_x='periodic',
    boundary_y='pml',
    pml_cells=30,
    pml_reflection=1e-08,
    geometry='free',
    background_index=1.0,
    layers=[],
    source='gaussian',
    injection='tfsf',
    source_x=100,
    source_y=50,
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
    spectra=True,
    snapshots=(100, 200, 400, 700),
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
    origin_2d='experiments/two_d/23_tfsf_plane_wave.py',
)

if __name__ == "__main__":
    main(CONFIG)
