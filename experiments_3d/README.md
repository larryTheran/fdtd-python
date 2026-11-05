# Separate 3D experiments

Each script contains its own editable `CONFIG` and runs directly with Python. See the [3D guide](../docs/THREE_D.md) and [saved results gallery](../results_3d/index.html).

```sh
../.venv/bin/python 29_double_slit_L15_3d.py --gif
```

| Python file | 3D experiment |
|---|---|
| [15_free_space_sine_3d.py](15_free_space_sine_3d.py) | 3D free-space sinusoidal point source — full-vector 3D |
| [16_free_space_modulated_3d.py](16_free_space_modulated_3d.py) | 3D modulated point pulse, reflecting edges — full-vector 3D |
| [17_free_space_gaussian_3d.py](17_free_space_gaussian_3d.py) | 3D Gaussian point pulse — full-vector 3D |
| [18_periodic_xy_3d.py](18_periodic_xy_3d.py) | 3D pulse with periodic x and y boundaries — full-vector 3D |
| [19_pml_xy_3d.py](19_pml_xy_3d.py) | 3D pulse with PML on all four sides — full-vector 3D |
| [20_pml_x_periodic_y_3d.py](20_pml_x_periodic_y_3d.py) | 3D PML in x, periodic in y — full-vector 3D |
| [21_periodic_x_pml_y_3d.py](21_periodic_x_pml_y_3d.py) | 3D periodic in x, PML in y — full-vector 3D |
| [22_huygens_plane_wave_3d.py](22_huygens_plane_wave_3d.py) | 3D plane wave from an aligned source array — full-vector 3D |
| [23_tfsf_plane_wave_3d.py](23_tfsf_plane_wave_3d.py) | 3D one-way plane wave using TF/SF — full-vector 3D |
| [24_plane_wave_lossy_material_3d.py](24_plane_wave_lossy_material_3d.py) | 3D plane wave entering a lossy dielectric — full-vector 3D |
| [25_single_slit_L25_3d.py](25_single_slit_L25_3d.py) | Single slit b=10, detector distance=25 cells — full-vector 3D |
| [26_single_slit_L30_3d.py](26_single_slit_L30_3d.py) | Single slit b=10, detector distance=30 cells — full-vector 3D |
| [27_single_slit_far_field_3d.py](27_single_slit_far_field_3d.py) | Single slit with extended observation region — full-vector 3D |
| [28_double_slit_L5_3d.py](28_double_slit_L5_3d.py) | Double slit b=10, gap=10, detector distance=5 — full-vector 3D |
| [29_double_slit_L15_3d.py](29_double_slit_L15_3d.py) | Double slit b=10, gap=10, detector distance=15 — full-vector 3D |
| [30_double_slit_b5_L100_3d.py](30_double_slit_b5_L100_3d.py) | Double slit b=5 with a distant detector — full-vector 3D |
| [31_refraction_two_media_3d.py](31_refraction_two_media_3d.py) | Refraction from n=1.5 to n=2.1 — full-vector 3D |
| [32_high_index_reflection_3d.py](32_high_index_reflection_3d.py) | Reflection and transmission from n=1.5 to n=4 — full-vector 3D |
| [33_specular_pec_mirror_3d.py](33_specular_pec_mirror_3d.py) | Specular reflection from an ideal PEC mirror — full-vector 3D |
| [34_refraction_three_media_3d.py](34_refraction_three_media_3d.py) | Refraction through n=1.5 / 2.5 / 1.5 — full-vector 3D |
| [35_mur_refraction_3d.py](35_mur_refraction_3d.py) | Glass-air refraction with Mur boundaries — full-vector 3D |
| [36_diagonal_huygens_array_3d.py](36_diagonal_huygens_array_3d.py) | Diagonal array of equal-phase point sources — full-vector 3D |
| [37_root_double_slit_700nm_3d.py](37_root_double_slit_700nm_3d.py) | Double slit from the root FDTD3D.m — full-vector 3D |
| [38_waveguide_bend_3d.py](38_waveguide_bend_3d.py) | Rectangular-core waveguide bend — full-vector 3D |
