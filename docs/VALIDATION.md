# Validation results

The checks below refer to saved runs produced in this workspace. The code was verified against analytical physics and numerical invariants; MATLAB/Octave was not executed.

**65 automated tests passed, with no failures.** The suite covers all independent scripts plus the numerical and CLI/GIF checks. See `results/tests.log` and `results/tests.xml`.

## Physics checks

- Vacuum pulse speed and TF/SF directionality.
- Absorbing versus reflecting 1D boundaries and periodic propagation.
- Fresnel amplitude/sign at an index step and analytical Fabry-Perot slab spectra.
- 1D and 2D lossless spectral power balance.
- Ohmic attenuation and agreement with the integral-current update.
- Dimensional distinction between optical and centimeter-grid loss.
- 2D PML pulse decay, x/y symmetry, rectangular meshes and periodic translation.
- Plane TF/SF uniformity, aperture cell counts, Fresnel regime and far-field envelope.
- Refraction angle from the simulated phasor versus Snell's law.
- Invalid-input rejection, direct script launch from another directory, saved arrays and animated GIF frames.

## Saved full runs

A successful run here means finite fields and valid output artifacts. It does not imply every geometry is independently converged in grid spacing, boundary thickness and run duration.

| Experiment | Steps | Final / peak domain energy proxy | Maximum abs(1-R-T), if spectral |
|---|---:|---:|---:|
| 01_free_space | 300 | 0.99167 | — |
| 02_absorbing_boundary | 300 | 1.3429e-06 | — |
| 03_tfsf_pulse | 300 | 1.2857e-06 | — |
| 04_periodic_boundary | 650 | 0.99999 | — |
| 05_free_space_spectra | 800 | 1.2031e-07 | 2.2204e-16 |
| 06_lossless_two_layers | 4000 | 4.254e-08 | 0.0031779 |
| 07_configurable_layers | 4000 | 2.9824e-09 | 0.0029791 |
| 08_ohmic_optical | 4000 | 1.5807e-05 | 0.0053966 |
| 09_ohmic_centimeter | 2000 | 0.00023227 | 0.88044 |
| 10_integral_loss_0p01 | 3000 | 4.8376e-10 | 0.98062 |
| 11_integral_loss_0p004 | 3000 | 2.6579e-16 | 0.85028 |
| 12_integral_loss_optical | 3000 | 3.7691e-12 | 0.0030912 |
| 13_periodic_dielectric_stack | 64000 | 4.1519e-15 | 0.0043607 |
| 14_pec_reflection | 600 | 0.85105 | — |
| 15_free_space_sine | 350 | 0.99223 | — |
| 16_free_space_modulated | 350 | 0.94371 | — |
| 17_free_space_gaussian | 350 | 0.57748 | — |
| 18_periodic_xy | 500 | 0.94047 | — |
| 19_pml_xy | 700 | 1.3142e-10 | — |
| 20_pml_x_periodic_y | 700 | 0.16074 | — |
| 21_periodic_x_pml_y | 700 | 0.16074 | — |
| 22_huygens_plane_wave | 700 | 0.99523 | — |
| 23_tfsf_plane_wave | 700 | 2.2653e-16 | 2.2204e-16 |
| 24_plane_wave_lossy_material | 1800 | 0.99976 | — |
| 25_single_slit_L25 | 900 | 0.88045 | — |
| 26_single_slit_L30 | 900 | 0.88045 | — |
| 27_single_slit_far_field | 1700 | 0.89046 | — |
| 28_double_slit_L5 | 900 | 0.89595 | — |
| 29_double_slit_L15 | 900 | 0.89595 | — |
| 30_double_slit_b5_L100 | 1200 | 0.89588 | — |
| 31_refraction_two_media | 1800 | 0.99997 | — |
| 32_high_index_reflection | 1800 | 1 | — |
| 33_specular_pec_mirror | 1800 | 0.99995 | — |
| 34_refraction_three_media | 2200 | 1 | — |
| 35_mur_refraction | 1600 | 0.9983 | — |
| 36_diagonal_huygens_array | 1000 | 0.99807 | — |
| 37_root_double_slit_700nm | 1600 | 0.99156 | — |
| 38_waveguide_bend | 4200 | 0.99479 | — |

**38 full default experiments verified**, including PNG decoding, multi-frame GIF decoding, finite numerical fields and saved parameter consistency.

Large energy fractions are expected for continuous sources, reflecting or periodic domains. For lossy materials, a nonzero spectral residual is physically expected; the residual column is not a numerical-error score for such cases. Pulse energy in a mixed PML/periodic domain can persist in modes traveling along the periodic direction.

## Refraction measurements

These are local phase-gradient diagnostics from finite beams, not fits to the thesis figures. Their window is specified in `fdtd/analysis.py`.

| Experiment | Interface row | Snell angle | Measured phase angle |
|---|---:|---:|---:|
| 31_refraction_two_media | 150 | 27.331° | 25.501° |
| 32_high_index_reflection | 150 | 13.948° | 12.719° |
| 34_refraction_three_media | 100 | 22.686° | 21.991° |
| 34_refraction_three_media | 200 | 40.000° | 42.779° |
| 35_mur_refraction | 120 | 59.358° | 52.536° |

## Practical limits

The main free-space, boundary, dielectric and diffraction implementations have independent physics tests. The supplemental waveguide is verified to run and guide a mode around the bend, but no quantitative coupling-efficiency or 3D effective-index convergence result is claimed. The supplementary first-order Mur source is not a port of the draft's higher-order boundary. Periodic slit examples represent aperture arrays. Optical losses below numerical residuals cannot be estimated reliably from 1-R-T on these demonstration grids.

The periodic material stack was checked at 16000, 32000 and 64000 steps; its maximum spectral residual fell from approximately 8.75% to 0.522% and 0.436%. The final saved run uses 64000 steps. This is time-record convergence, not a complete mesh-convergence study.
