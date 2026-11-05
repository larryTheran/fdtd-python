> Historical local-workspace guide. For a fresh public checkout, follow the [current README](../README.md). Restore release result archives before following links into `results/` or `results_3d/`. Original MATLAB/PDF archives are referenced by provenance records and are not included automatically.

# Python FDTD experiments

38 individually runnable simulations based on **Tesis-larry-FDTD (1).pdf** by Larry Theran Suarez and the MATLAB archive in **Correcciones 2 con nuevas cosas/Codigos terminados**. The original files are preserved.

Each script has an editable `CONFIG` block, a thesis section/figure reference, and its own output folder. Common Yee updates are in `fdtd/` so numerical corrections apply consistently across experiments. These are corrected implementations of the physical experiments, not byte-for-byte reproductions of MATLAB bugs.

## Start here

The archived local workspace had a Python environment and completed results. On a fresh clone, create your own environment below and download release results separately. Open [the experiment catalog](EXPERIMENTS.md) to choose a script, or [the results gallery](../results/README.md) to view the generated plots and GIFs.

From Terminal:

```bash
cd "path/to/fdtd-python"

# Run one experiment and save its plots, data and animation.
.venv/bin/python experiments/one_d/06_lossless_two_layers.py --gif

# Single-slit diffraction.
.venv/bin/python experiments/two_d/25_single_slit_L25.py --gif

# Refraction between two dielectric media.
.venv/bin/python experiments/two_d/31_refraction_two_media.py --gif

# List all experiments, or run all of them.
.venv/bin/python run_all.py --list
.venv/bin/python run_all.py --gif --frames 60

# Select by number; show the available options for one experiment.
.venv/bin/python run_all.py --only 2 6 19 31
.venv/bin/python experiments/two_d/31_refraction_two_media.py --help

# Run the automated physics and integration checks.
.venv/bin/python -m pytest -q
```

`--show` opens the static figures in Matplotlib windows after computing. `--gif` creates an animation that can be opened in a browser or image viewer. Saving figures and GIFs works without a graphical desktop. `--no-plots` saves only the numerical data. `--steps 50` is useful for a quick startup check but is too short for most physical experiments.

To use another Python installation or move this project to another computer, recreate the virtual environment using **Python 3.10 or later**:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
```

The completed runs used Python 3.12. Exact installed package versions are recorded in [requirements-tested.txt](../requirements-tested.txt); use that file with Python 3.12 to reproduce this environment.

In VS Code, PyCharm or another editor, select `python_fdtd/.venv/bin/python` as the interpreter. Run the chosen experiment file directly; the working directory does not matter.

## What is included

| IDs | Experiments |
|---|---|
| 01-05 | 1D free-space propagation, absorbing boundary, TF/SF, periodic boundary, vacuum spectra |
| 06-07 | Two dielectric layers and an editable multilayer stack |
| 08-12 | Ohmic and integral-current losses, with separate optical and centimeter-scale interpretations |
| 13-14 | Alternating dielectric stack and true PEC reflection |
| 15-24 | 2D point sources, periodic/PML boundaries, aligned plane-wave sources and a lossy medium |
| 25-30 | Single and double slits, near detectors and an extended far-field domain |
| 31-34 | Two/three-medium refraction, high-index partial reflection and an ideal PEC mirror |
| 35-38 | Supplemental Mur refraction, diagonal source array, root `FDTD2D.m` slit case and reconstructed waveguide bend |

## Change an experiment

Open its `.py` file and edit `CONFIG`. `Layer(start, stop, epsilon_r, sigma)` uses zero-based cell indices and an **exclusive** stop. In 1D, layers vary along z; in 2D they vary along y. `epsilon_r` is relative permittivity, so use `n**2` for a nonmagnetic dielectric with refractive index `n`. Conductivity `sigma` is in **S/m**.

Spatial increments and wavelength are in meters. If `dx=None`, the grid spacing is computed from wavelength, resolution and the actual largest material index. When `dx` is explicit, changing wavelength does not change it. The time step is always recomputed from the same spatial grid. Source types are `gaussian`, `modulated` and `sine`.

Some common changes are also available on the command line:

```bash
.venv/bin/python experiments/two_d/31_refraction_two_media.py --angle 30 --steps 2200 --gif
.venv/bin/python experiments/two_d/25_single_slit_L25.py --detector-y 120 --gif
.venv/bin/python experiments/one_d/08_ohmic_optical.py --sigma 10000 --gif
```

Use `--output path/to/new/run` when retaining a parameter sweep. Re-running a script with its default output replaces that experiment's existing output files. The code rejects invalid layer bounds, unsupported source/boundary combinations and unstable Courant factors.

## Read the outputs

Every `results/<experiment>/` directory contains:

- `config.json`: the exact inputs used.
- `data.npz`: electric/magnetic fields, material maps, snapshots, time axis, energy proxy and any detector/spectral data. Load using `numpy.load(..., allow_pickle=False)`.
- `diagnostics.json`: numerical measurements and notes.
- `fields.png`: field snapshots at the thesis steps and the final step.
- `energy.png`: a normalized domain-energy diagnostic.
- Material, spectrum or detector plots as appropriate.
- `animation.gif` when requested with `--gif`.

Example:

```python
from pathlib import Path
import numpy as np

folder = Path("results/06_lossless_two_layers")
with np.load(folder / "data.npz", allow_pickle=False) as result:
    electric = result["e"]
    times_seconds = result["time"]
    valid = result["spectral_valid"]
    frequencies_hz = result["frequency"][valid]
    reflected_power = result["reflectance"][valid]
```

The electric field is represented as `E/Z0`, alongside H. Plots use arbitrary source amplitude; detector curves are squared-field quantities, not calibrated W/m². Magnetic fields are staggered by half a cell and half a time step. The energy curve is a diagnostic proxy; it is not an exact discrete conservation invariant.

## Important interpretation notes

The thesis and MATLAB drafts contain conflicting settings and numerical errors. Those differences are recorded rather than hidden:

- The 1D boundary called “PEC” in the thesis is actually a delay absorbing boundary. A true PEC example is separate.
- Several loss files replace an optical cell size with **1 cm** after building the pulse. Experiments 08/12 retain consistent optical units; 09-11 reproduce the intended visible attenuation on a consistent microwave grid. The stated 70%/90% losses are not fitted targets.
- A dielectric transition from `n=1.5` to `n=4` partially reflects. It is not total internal reflection. Experiments 32 and 33 distinguish that material case from an ideal mirror.
- Diffraction plots include time averaging and a sinc-squared far-field guide. The captioned double-slit distance of 15 cells does not meet a far-field criterion for the complete aperture.
- The unfinished waveguide code is supplied as a documented reconstruction, not an exact reproduction of missing dependencies. The empty MATLAB GUIDE interface is replaced by these separate runnable scripts, rather than ported as a GUI.

See [numerical methods and corrections](NUMERICS.md), [the complete source audit](SOURCE_AUDIT.md), and [validation results](VALIDATION.md) for details.

The [verified run manifest](../results/verified_runs.json) covers all 38 saved default experiments. `run_summary.json` records only the most recent `run_all.py` invocation. After changing experiments, rerun them and the tests before regenerating reports with `tools/build_reports.py`.

## Research and publication planning

[Separate antenna-design and ultrafast-optics literature reviews](../research_reviews/2026-09-06/README.md) examine recent 2024–2026 papers, candidate research problems, and the solver extensions needed to investigate them. These are proposed future studies; their results are not part of the completed thesis experiments.

## Full-vector 3D counterparts

All **24 existing 2D experiments (15–38)** now have separate scripts in [`experiments_3d`](../experiments_3d). They retain the original x/y geometry, wavelengths, materials, and time-step counts, with explicitly defined depth geometry. The solver evolves all six electromagnetic components, including finite apertures, finite beams, six-face absorbing boundaries, and a rectangular-core waveguide bend.

```sh
.venv/bin/python experiments_3d/29_double_slit_L15_3d.py --gif
.venv/bin/python run_all_3d.py --list
.venv/bin/python run_all_3d.py --gif --frames 30
```

Inside PyLab or Jupyter, 3D experiments now show a live six-panel field/material figure during the run, with step and simulated time. Updates replace the same figure and are capped at four intermediate frames per second. Restart the notebook kernel once after updating these modules, then rerun the experiment. Terminal defaults and saved numerical results are unchanged; `--no-live` disables notebook preview updates.

Read the [3D guide](THREE_D.md) for geometry choices, outputs, performance, and numerical limitations; the [3D validation report](THREE_D_VALIDATION.md) records the completed checks. Results are separate under [`results_3d`](../results_3d). The [results gallery](../results_3d/index.html) presents the saved experiments.
