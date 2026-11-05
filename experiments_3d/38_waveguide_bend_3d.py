#!/usr/bin/env python3
"""Rectangular-core waveguide bend — full-vector 3D

Independent 3D counterpart; edit CONFIG or see --help.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from fdtd.config import Layer
from fdtd.three_d import Config3D
from fdtd.three_d_runner import main

CONFIG = Config3D(
    name='38_waveguide_bend_3d',
    title='Rectangular-core waveguide bend — full-vector 3D',
    thesis='Supplement: unfinished 2D/FDTD_2D_3/Untitled8.m',
    nx=430,
    ny=430,
    steps=4200,
    wavelength=1.55e-06,
    points_per_wavelength=10.0,
    dx=8.157894736842106e-08,
    dy=None,
    courant=0.5,
    boundary_x='pml',
    boundary_y='pml',
    pml_cells=40,
    pml_reflection=1e-08,
    geometry='bend',
    background_index=1.0,
    layers=[],
    source='sine',
    injection='mode',
    source_x=65,
    source_y=45,
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
    snapshots=(400, 1200, 2400, 4200),
    bend_radius=2e-05,
    bend_width=7.75e-07,
    bend_core_index=1.9,
    notes='Reconstruction of intended 20 um-radius, 0.775 um-width bend. Includes a scalar eigenmode solver to replace missing ezmode; no claim of exact agreement with the incomplete 3D effective-index prototype. Added z depth is 64 cells, dz=dx, with 12-cell z PML. The x-y geometry, grid spacing and time-step count are preserved. Full rectangular dielectric core (n=1.9), height=0.775 μm, air above and n=1.52 substrate below. Scalar transverse eigenfunction seeds Ez; this is not a calibrated vector port mode.',
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
    origin_2d='experiments/supplemental/38_waveguide_bend.py',
)

if __name__ == "__main__":
    main(CONFIG)
