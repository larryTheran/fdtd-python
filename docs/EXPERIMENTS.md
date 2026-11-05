# Experiment catalog

Each file runs independently. Edit its CONFIG block or use `--help`. The main thesis is the 118-page root PDF; references below use printed page numbers.

| ID / script | Experiment | Thesis / original source | Grid | Steps |
|---|---|---|---|---|
| [01_free_space](../experiments/one_d/01_free_space.py) | 1D free-space pulse with zero exterior ghosts | 4.1.4; Fig. 4-5; printed p. 42 | 200 | 300 |
| [02_absorbing_boundary](../experiments/one_d/02_absorbing_boundary.py) | 1D pulse with the thesis delay ABC | 4.1.5; Fig. 4-7; printed p. 45 | 200 | 300 |
| [03_tfsf_pulse](../experiments/one_d/03_tfsf_pulse.py) | 1D one-way TF/SF pulse | 4.1.6; Fig. 4-9; printed p. 48 | 200 | 300 |
| [04_periodic_boundary](../experiments/one_d/04_periodic_boundary.py) | 1D pulse with periodic boundaries | 4.1.6; Fig. 4-10; printed p. 49 | 200 | 650 |
| [05_free_space_spectra](../experiments/one_d/05_free_space_spectra.py) | 1D reflection and transmission in vacuum | 4.1.7; Figs. 4-12, 4-13; printed pp. 51-52 | 200 | 800 |
| [06_lossless_two_layers](../experiments/one_d/06_lossless_two_layers.py) | 1D two lossless dielectric layers | 4.1.8; Figs. 4-14 to 4-17; printed pp. 53-55 | 400 | 4000 |
| [07_configurable_layers](../experiments/one_d/07_configurable_layers.py) | 1D configurable dielectric stack | 1D/FDTD_1D_5 MATLAB extension of 4.1.8 | 400 | 4000 |
| [08_ohmic_optical](../experiments/one_d/08_ohmic_optical.py) | 1D Ohmic loss at optical SI scales | 4.1.9; Fig. 4-18 parameters; printed p. 58 | 400 | 4000 |
| [09_ohmic_centimeter](../experiments/one_d/09_ohmic_centimeter.py) | 1D Ohmic attenuation on the legacy cm grid | 4.1.9; Fig. 4-18 visual reconstruction | 400 | 2000 |
| [10_integral_loss_0p01](../experiments/one_d/10_integral_loss_0p01.py) | 1D integral-current loss, sigma=0.01 S/m | 4.1.10; Fig. 4-19; printed p. 62 | 400 | 3000 |
| [11_integral_loss_0p004](../experiments/one_d/11_integral_loss_0p004.py) | 1D integral-current loss, sigma=0.004 S/m | 4.1.10; Fig. 4-20; printed p. 63 | 400 | 3000 |
| [12_integral_loss_optical](../experiments/one_d/12_integral_loss_optical.py) | 1D integral-current loss at optical SI scales | 4.1.10; optical interpretation of Figs. 4-19 and 4-20 | 400 | 3000 |
| [13_periodic_dielectric_stack](../experiments/one_d/13_periodic_dielectric_stack.py) | 1D alternating dielectric stack at 5 GHz | 1D/FDTD_1D_8/FDTD_1D_Dielectrico_periodico.m | 1000 | 64000 |
| [14_pec_reflection](../experiments/one_d/14_pec_reflection.py) | 1D reflection from actual PEC endpoints | Supplement: clarify boundary terminology in 4.1.5 | 200 | 600 |
| [15_free_space_sine](../experiments/two_d/15_free_space_sine.py) | 2D free-space sinusoidal point source | 5.1.4; Fig. 5-6; printed p. 71 | 200 x 200 | 350 |
| [16_free_space_modulated](../experiments/two_d/16_free_space_modulated.py) | 2D modulated point pulse, reflecting edges | 5.1.4; Fig. 5-7; printed p. 72 | 200 x 200 | 350 |
| [17_free_space_gaussian](../experiments/two_d/17_free_space_gaussian.py) | 2D Gaussian point pulse | 2D/FDTD_2D_1/FDTD_2D_libre.m | 200 x 200 | 350 |
| [18_periodic_xy](../experiments/two_d/18_periodic_xy.py) | 2D pulse with periodic x and y boundaries | 5.1.5; Fig. 5-8; printed p. 73 | 200 x 200 | 500 |
| [19_pml_xy](../experiments/two_d/19_pml_xy.py) | 2D pulse with PML on all four sides | 5.1.6; Fig. 5-10; printed p. 79 | 200 x 200 | 700 |
| [20_pml_x_periodic_y](../experiments/two_d/20_pml_x_periodic_y.py) | 2D PML in x, periodic in y | 5.1.6; Fig. 5-11; printed p. 80 | 200 x 200 | 700 |
| [21_periodic_x_pml_y](../experiments/two_d/21_periodic_x_pml_y.py) | 2D periodic in x, PML in y | 5.1.6; Fig. 5-12; printed p. 80 | 200 x 200 | 700 |
| [22_huygens_plane_wave](../experiments/two_d/22_huygens_plane_wave.py) | 2D plane wave from an aligned source array | 5.2; Fig. 5-13; printed p. 81 | 200 x 200 | 700 |
| [23_tfsf_plane_wave](../experiments/two_d/23_tfsf_plane_wave.py) | 2D one-way plane wave using TF/SF | 2D/FDTD_2D_2 TF/SF draft and Untitled7.m | 200 x 200 | 700 |
| [24_plane_wave_lossy_material](../experiments/two_d/24_plane_wave_lossy_material.py) | 2D plane wave entering a lossy dielectric | 2D/FDTD_2D_2 material_onda_plana.m | 200 x 400 | 1800 |
| [25_single_slit_L25](../experiments/two_d/25_single_slit_L25.py) | Single slit b=10, detector distance=25 cells | 6.1; Figs. 6-2 to 6-4; printed pp. 84-86 | 200 x 200 | 900 |
| [26_single_slit_L30](../experiments/two_d/26_single_slit_L30.py) | Single slit b=10, detector distance=30 cells | 6.1; Figs. 6-2 to 6-4; printed pp. 84-86 | 200 x 200 | 900 |
| [27_single_slit_far_field](../experiments/two_d/27_single_slit_far_field.py) | Single slit with extended observation region | 6.1; Figs. 6-5 to 6-7; printed pp. 87-88 | 400 x 500 | 1700 |
| [28_double_slit_L5](../experiments/two_d/28_double_slit_L5.py) | Double slit b=10, gap=10, detector distance=5 | 6.1; Figs. 6-10 and 6-11 captions; printed pp. 90-91 | 200 x 200 | 900 |
| [29_double_slit_L15](../experiments/two_d/29_double_slit_L15.py) | Double slit b=10, gap=10, detector distance=15 | 6.1; Figs. 6-10 and 6-11 captions; printed pp. 90-91 | 200 x 200 | 900 |
| [30_double_slit_b5_L100](../experiments/two_d/30_double_slit_b5_L100.py) | Double slit b=5 with a distant detector | 6.1; prose following Fig. 6-9; printed pp. 89-90 | 300 x 300 | 1200 |
| [31_refraction_two_media](../experiments/two_d/31_refraction_two_media.py) | Refraction from n=1.5 to n=2.1 | 6.2; Fig. 6-14; printed p. 94 | 250 x 300 | 1800 |
| [32_high_index_reflection](../experiments/two_d/32_high_index_reflection.py) | Reflection and transmission from n=1.5 to n=4 | 6.2; Fig. 6-15; printed p. 95 | 250 x 300 | 1800 |
| [33_specular_pec_mirror](../experiments/two_d/33_specular_pec_mirror.py) | Specular reflection from an ideal PEC mirror | 6.2; intended ideal reflector in Fig. 6-15 | 250 x 300 | 1800 |
| [34_refraction_three_media](../experiments/two_d/34_refraction_three_media.py) | Refraction through n=1.5 / 2.5 / 1.5 | 6.2; Fig. 6-16; printed p. 96 | 250 x 300 | 2200 |
| [35_mur_refraction](../experiments/supplemental/35_mur_refraction.py) | Glass-air refraction with Mur boundaries | Supplement: refraccionmur.m / Program31 | 400 x 240 | 1600 |
| [36_diagonal_huygens_array](../experiments/supplemental/36_diagonal_huygens_array.py) | Diagonal array of equal-phase point sources | Supplement: refraccionlarry.m and nuevo/Untitled2.m | 400 x 400 | 1000 |
| [37_root_double_slit_700nm](../experiments/supplemental/37_root_double_slit_700nm.py) | Double slit from the root FDTD2D.m | Supplement: root FDTD2D.m | 400 x 400 | 1600 |
| [38_waveguide_bend](../experiments/supplemental/38_waveguide_bend.py) | Effective-index waveguide bend | Supplement: unfinished 2D/FDTD_2D_3/Untitled8.m | 430 x 430 | 4200 |
