#!/usr/bin/env python3
"""Double slit from the root FDTD3D.m — full-vector 3D

Independent 3D counterpart; edit CONFIG or see --help.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from fdtd.config import Layer
from fdtd.three_d import Config3D
from fdtd.three_d_runner import main

CONFIG = Config3D(
    name='37_root_double_slit_700nm_3d',
    title='Double slit from the root FDTD3D.m — full-vector 3D',
    thesis='Supplement: root FDTD2D.m',
    nx=400,
    ny=400,
    steps=1600,
    wavelength=7e-07,
    points_per_wavelength=10.0,
    dx=4.117e-08,
    dy=None,
    courant=0.5,
    boundary_x='pml',
    boundary_y='pml',
    pml_cells=50,
    pml_reflection=1e-08,
    geometry='slits',
    background_index=1.4142135623730951,
    layers=[],
    source='sine',
    injection='line',
    source_x=200,
    source_y=100,
    source_width=200,
    angle_deg=0.0,
    tau_periods=0.5,
    wall_y=149,
    wall_thickness=2,
    slit_count=2,
    slit_width=2,
    slit_gap=5,
    detector_y=240,
    average_cycles=8,
    spectra=False,
    snapshots=(300, 600, 900, 1200),
    bend_radius=2e-05,
    bend_width=7.75e-07,
    bend_core_index=1.9,
    notes='Rotated to +y propagation. Integer sampled legacy intervals correspond to two 2-cell openings and a 5-cell opaque gap despite Ancho=5/Separacion=5. PEC replaces the 5.7e8 S/m obstacle; tiny background loss omitted. Added z depth is 64 cells, dz=dx, with 12-cell z PML. The x-y geometry, grid spacing and time-step count are preserved. Each former slit is now a finite rectangular aperture 24 cells high. Illumination has a 16-cell Gaussian radius in z.',
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
    origin_2d='experiments/supplemental/37_root_double_slit_700nm.py',
)

if __name__ == "__main__":
    main(CONFIG)
