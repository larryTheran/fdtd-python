# 3D validation and full-run audit

Audit date: 12 September 2026.

**24/24 full default 3D experiments completed and verified.** Every run used the original 2D x/y grid, wavelength, materials, and default time-step count, plus the documented depth configuration. None of the audited results is a shortened smoke run.

Test suite result: **106 passed in 12.67s**. This includes the original 65 tests and the new 3D tests. The physical benchmarks cover vector propagation, absorbing and reflecting boundaries, loss, Fresnel reflection, plane-wave spectral balance, and reduction to the existing 2D method.

The audit opens every numerical archive with pickle disabled, checks all six field shapes and finite values, confirms the final step and full time history, compares saved configurations with the independent scripts, verifies solver-source hashes, checks output images, and inspects every GIF for multiple frames. Machine-readable evidence: `results_3d/verified_runs.json`; full-run execution log: `results_3d/execution.log`; test output: `results_3d/test_execution.log`.

Summed simulation runtime: 17.4 minutes on this computer, excluding archive compression and plotting. Runtime depends on hardware and backend. This is execution and benchmark validation, not a mesh-convergence certificate for every geometry. See `THREE_D.md` for limits of the finite-depth aperture, Mur, waveguide excitation, and detector models.

| Experiment | Grid | Full steps | Simulation seconds | GIF frames |
|---|---|---:|---:|---:|
| 15_free_space_sine_3d | 200 × 200 × 64 | 350 | 4.3 | 31 |
| 16_free_space_modulated_3d | 200 × 200 × 64 | 350 | 4.2 | 31 |
| 17_free_space_gaussian_3d | 200 × 200 × 64 | 350 | 4.2 | 31 |
| 18_periodic_xy_3d | 200 × 200 × 64 | 500 | 5.4 | 31 |
| 19_pml_xy_3d | 200 × 200 × 64 | 700 | 11.8 | 31 |
| 20_pml_x_periodic_y_3d | 200 × 200 × 64 | 700 | 11.7 | 31 |
| 21_periodic_x_pml_y_3d | 200 × 200 × 64 | 700 | 11.8 | 31 |
| 22_huygens_plane_wave_3d | 200 × 200 × 8 | 700 | 1.4 | 31 |
| 23_tfsf_plane_wave_3d | 200 × 200 × 8 | 700 | 2.8 | 31 |
| 24_plane_wave_lossy_material_3d | 200 × 400 × 8 | 1800 | 6.7 | 31 |
| 25_single_slit_L25_3d | 200 × 200 × 64 | 900 | 15.2 | 31 |
| 26_single_slit_L30_3d | 200 × 200 × 64 | 900 | 15.2 | 31 |
| 27_single_slit_far_field_3d | 400 × 500 × 64 | 1700 | 134.3 | 31 |
| 28_double_slit_L5_3d | 200 × 200 × 64 | 900 | 15.2 | 31 |
| 29_double_slit_L15_3d | 200 × 200 × 64 | 900 | 15.2 | 31 |
| 30_double_slit_b5_L100_3d | 300 × 300 × 64 | 1200 | 43.7 | 31 |
| 31_refraction_two_media_3d | 250 × 300 × 64 | 1800 | 55.3 | 31 |
| 32_high_index_reflection_3d | 250 × 300 × 64 | 1800 | 55.3 | 31 |
| 33_specular_pec_mirror_3d | 250 × 300 × 64 | 1800 | 53.8 | 31 |
| 34_refraction_three_media_3d | 250 × 300 × 64 | 2200 | 65.4 | 31 |
| 35_mur_refraction_3d | 400 × 240 × 64 | 1600 | 49.5 | 31 |
| 36_diagonal_huygens_array_3d | 400 × 400 × 64 | 1000 | 61.2 | 31 |
| 37_root_double_slit_700nm_3d | 400 × 400 × 64 | 1600 | 101.3 | 31 |
| 38_waveguide_bend_3d | 430 × 430 × 64 | 4200 | 301.9 | 31 |


## Live notebook field previews — 4 November 2026

The optional observer path was checked against the unobserved solver with exact
array equality for every returned result key in both NumPy and threaded native
runs. Preview snapshots contain only three detached 2D field planes, static
read-only material planes, and scalar metadata; they do not share writable memory
with the final volume arrays. Initial/final publishing, stride and wall-clock
limits, invalid inputs, callback errors, interrupted cleanup, and automatic
notebook/disabled/terminal runner choices were exercised.

The 19 focused checks in `tests/test_three_d_live.py` passed in the selected
`/opt/miniconda3/bin/python3.12` environment. The entire existing
`tests/test_three_d.py` suite also passed there: **41 tests**, including native vs
NumPy agreement, six-face absorption, modal/geometry configuration validation,
spectral and Fresnel checks, and standalone CLI/GIF/result-bundle integration.
The selected environment's scientific libraries were retained; the test driver
used temporary links to the project's already-installed pytest dependencies,
without package installation or environment changes.

`tools/check_live_fdtd.py` passed against its own real IPython kernel: five PNG
frames arrived during the eight-step test, all with one stable display ID and
multiple distinct field images. The last frame reported step 8/8, render resources
closed, and no extra pyplot figure was registered. First/last smoke images and a
six-panel preview rendered from the existing experiment-38 data were inspected.
The latter only read the saved archive; the 430×430×64, 4,200-step experiment was
not rerun and its source configuration, saved results, and open PyLab session were
not changed. CLI help/description retained the same experiment configuration;
a tiny `--no-live --no-plots` check saved only the normal numerical bundle.

An earlier full-suite attempt in the project's separate local virtual environment
passed 40 numerical/configuration checks but encountered that environment's
Matplotlib 3.11 `system_profiler` font-discovery `KeyError('_items')` in the CLI
plot test. That test and all 41 existing tests passed in the actual selected
Miniconda/Matplotlib 3.8 environment. No application or simulation code workaround
was added for the unrelated font-discovery issue.
