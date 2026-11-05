#!/usr/bin/env python3
"""Single slit b=10, detector distance=25 cells — full-vector 3D

Independent 3D counterpart; edit CONFIG or see --help.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from fdtd.config import Layer
from fdtd.three_d import Config3D
from fdtd.three_d_runner import main

CONFIG = Config3D(
    name='25_single_slit_L25_3d',
    title='Single slit b=10, detector distance=25 cells — full-vector 3D',
    thesis='6.1; Figs. 6-2 to 6-4; printed pp. 84-86',
    nx=200,
    ny=200,
    steps=900,
    wavelength=5.32e-07,
    points_per_wavelength=10.0,
    dx=None,
    dy=None,
    courant=0.5,
    boundary_x='periodic',
    boundary_y='pml',
    pml_cells=30,
    pml_reflection=1e-08,
    geometry='slits',
    background_index=1.0,
    layers=[],
    source='sine',
    injection='line',
    source_x=100,
    source_y=45,
    source_width=200,
    angle_deg=0.0,
    tau_periods=0.5,
    wall_y=79,
    wall_thickness=2,
    slit_count=1,
    slit_width=10,
    slit_gap=10,
    detector_y=105,
    average_cycles=8,
    spectra=False,
    snapshots=(100, 150, 220, 300),
    bend_radius=2e-05,
    bend_width=7.75e-07,
    bend_core_index=1.9,
    notes='10 cells per vacuum wavelength; exact PEC obstacle; detector distance measured from the exit face. Periodic x represents repeated apertures and can affect late-time patterns. Added z depth is 64 cells, dz=dx, with 12-cell z PML. The x-y geometry, grid spacing and time-step count are preserved. Each former slit is now a finite rectangular aperture 24 cells high. Illumination has a 16-cell Gaussian radius in z.',
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
    origin_2d='experiments/two_d/25_single_slit_L25.py',
)

if __name__ == "__main__":
    main(CONFIG)
