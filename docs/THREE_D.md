# Three-dimensional versions of the 2D experiments

Created 12 September 2026. There are **24 independently runnable Python experiments**, one for every existing 2D case, including the four supplemental cases. The original 1D/2D scripts, MATLAB sources, thesis, and result directories are preserved.

## Run an experiment

From `python_fdtd`:

```sh
.venv/bin/python experiments_3d/29_double_slit_L15_3d.py --gif
.venv/bin/python experiments_3d/31_refraction_two_media_3d.py --describe
.venv/bin/python run_all_3d.py --list
.venv/bin/python run_all_3d.py --only 25 26 28 29 --gif
.venv/bin/python run_all_3d.py --gif --frames 30
.venv/bin/python run_all_3d.py --resume --gif --frames 30
```

Scripts also run from another working directory. For a new environment, install `requirements.txt`; use `requirements-dev.txt` for tests. No commercial solver is needed.

The default `auto` backend compiles a small local C accelerator when a C compiler is available. The complete reference solver is NumPy; select it explicitly with `--backend numpy`. The accelerator implements only the same curl/absorbing-memory update and is checked against NumPy for all six components in a lossy, three-dimensional geometry. Native execution uses three workers for the independent components within each H or E phase, with synchronization between phases; use `--workers 1` for sequential execution. The threaded and sequential native results are checked for exact equality. NumPy runs sequentially. All experiment configuration, geometry, sources, orchestration, analysis, and plots are Python. Compiler output stays under `.cache/fdtd3d/`. There are no downloads or GPU requirements.

```sh
.venv/bin/python experiments_3d/19_pml_xy_3d.py --backend numpy --steps 100 --output results_3d_trial/pulse
.venv/bin/python experiments_3d/29_double_slit_L15_3d.py --nz 96 --pml-z 16 --slit-height 32 --source-width-z 24 --gif --output results_3d_trial/slits
.venv/bin/python -m pytest tests -q
```

`--steps` changes the physical duration. A short run is useful for checking execution but may end before a wave reaches its detector. Changing `--nz` enlarges the depth at fixed cell spacing and recenters the source. It does **not** refine the mesh. Output overrides prevent exploratory runs from replacing the default result bundle. `--resume` checks configurations, solver hashes, complete field arrays, and required output files before reusing a result; missing, stale, or interrupted runs are recomputed.

## Live field evolution in PyLab and Jupyter

When a 3D experiment runs inside an IPython notebook kernel, its runner automatically
publishes one live figure with XY, XZ, and YZ `Ez/Z0` sections above the corresponding
material maps. The figure updates in place as the solver advances, with the current
step, simulated time, and latest sampled energy proxy. The final PNG/data files are
still saved normally. Experiment 38's existing `main(CONFIG)` call uses this behavior;
its physical configuration does not need changing.

After updating these modules, restart the notebook's Python kernel once so Python
loads the new runner rather than a cached import. Rerun the experiment afterward.
Updates cannot be added retroactively to a completed run or injected into an already
executing solver. PyLab needs the version with Jupyter display-ID update support to
replace frames instead of accumulating separate images.

The default limit is four intermediate preview frames per second, checking every
solver step. Actual updates depend on calculation and PNG-rendering time. Initial
and final states are always sent. Rendering adds some wall-clock overhead; it does
not change the numerical time step or retained solution arrays. The solver copies
only three 2D sections for each preview, shares static material-section copies, and
does not retain a movie of live frames. Field color limits use the peak observed in
the displayed sections; they are not calibrated source power. The energy label
explicitly identifies its sampling step and remains an energy proxy.

Optional notebook runner arguments:

```python
main(CONFIG, ["--live-fps", "2", "--live-stride", "5"])
# Or disable live previews while keeping normal final plots:
main(CONFIG, ["--no-live"])
```

Use `main(CONFIG)` for defaults in an ordinary Jupyter cell. In IPython,
`%run experiments_3d/38_waveguide_bend_3d.py --live-fps 2` accepts the same
experiment flags as a terminal command. The batch runner also applies
`--live`, `--no-live`, `--live-stride`, and `--live-fps` to each simulation it runs.

`--live-fps` accepts values greater than zero and at most 10. `--live-stride` is a
positive number of solver steps. Both limits apply. `--no-plots` disables automatic
live previews as well; an explicit `--live` can request previews separately.
Terminal runs remain noninteractive by default. `--live` requires an IPython/Jupyter
kernel; use `--gif` for a saved animation from Terminal. Canceling a run closes the
preview's render resources while preserving the last image already displayed.

For a custom observer, `simulate(config, on_frame=callback, preview_stride=1,
preview_interval=0.25)` supplies a `PreviewFrame3D` containing detached read-only
field sections, static material sections, step/time, and the latest scalar energy
sample. The callback runs after a complete Yee step, between solver updates. A
callback exception propagates normally.

The optional real-Jupyter smoke check is `python tools/check_live_fdtd.py` in an
environment with `ipykernel`, `jupyter_client`, Matplotlib, and NumPy. It runs a tiny
temporary experiment and verifies five evolving PNG frames with one display ID;
it does not run experiment 38 or overwrite saved results.

## How each 2D case becomes 3D

The original `nx`, `ny`, `dx`, `dy`, wavelength, materials, source x/y location, incidence angle, obstacle x/y geometry, detector row, and number of time steps are retained. Default `dz=dx`. The Courant choice remains `c0 dt / min(dx,dy,dz)=0.5`, with an explicit three-dimensional stability check.

Most experiments add **64 depth cells**, with a 12-cell PML on each z face. These depth dimensions are new modeling choices, not values attributed to the thesis. They keep the examples practical on a computer while resolving finite-depth fields. Increase depth and absorbing-layer clearance before drawing quantitative conclusions about wide beams or long-distance diffraction.

| IDs | Separate 3D experiments | Added dimension and interpretation |
|---|---|---|
| 15–17 | Sine, modulated, and Gaussian free-space sources | A localized z-directed electric dipole in a PEC cavity. Radiation has vector dipole structure; the 2D cylindrical-wave pattern is not expected to survive. |
| 18 | Periodic boundaries | A localized dipole with periodic x, y, and z; this models periodic images in all three directions. |
| 19 | PML boundaries | A localized dipole with PML on all six faces. |
| 20 | PML x, periodic y | Original x/y conditions plus PML z. |
| 21 | Periodic x, PML y | Original x/y conditions plus PML z. |
| 22 | Aligned Huygens array | A uniform electric-current sheet over x/z, periodic in x/z, absorbing in y. It radiates in both y directions. |
| 23 | TF/SF plane pulse | Normal +y plane wave, uniform x/z with periodic x/z. Eight depth cells suffice for this intentionally depth-independent calibration case. |
| 24 | Lossy material plane wave | Uniform x/z sheet and layered medium, periodic x/z, eight depth cells. Conductivity retains its SI value. |
| 25–26 | Single slit, L=25 and L=30 | One finite rectangular aperture, 24 cells high in z. The detector is now an x/z plane. |
| 27 | Single slit, distant observation | Same x/y extended observation region, finite aperture in z. The saved detector is a finite near-field plane, not a near-to-far transform. |
| 28–29 | Double slit, L=5 and L=15 | Two finite rectangular apertures, 24 cells high; the original x widths, separation, and detector distances remain. |
| 30 | Double slit, b=5 and L=100 | Two finite rectangles with original narrow x widths and distant detector. |
| 31 | n=1.5 → 2.1 | Oblique beam with Gaussian envelopes in x and z, at the original x/y phase angle. |
| 32 | n=1.5 → 4 | Partial reflection and transmission of the finite 3D beam. This is not total internal reflection. |
| 33 | PEC mirror | Finite 3D beam reflected from a PEC plane spanning x/z. |
| 34 | n=1.5 / 2.5 / 1.5 | Finite 3D beam passing through two parallel interfaces. |
| 35 | Glass–air with Mur | Finite beam with first-order Mur boundaries on all six faces. |
| 36 | Diagonal Huygens array | Twenty equal-phase, z-directed electric dipoles on the original x/y diagonal, at the center depth. |
| 37 | Root 700 nm double slit | Two 2-cell-wide openings with the original 5-cell opaque gap, extended to finite 24-cell height. The coarse x aperture needs refinement for quantitative work. |
| 38 | Waveguide bend | A real rectangular dielectric core, rather than an effective-index plane: radius 20 μm, width and height 0.775 μm, core n=1.9, substrate n=1.52 below and air above. |

For finite-aperture sheet sources, the z amplitude has a Gaussian radius of 16 cells and tapers to zero before the z PML. Finite beams use the same added z radius. The original x source profile is retained and tapered before any x PML. A source labeled `line` in configuration is the 3D counterpart of the original line: a finite or periodic x/z electric-current sheet. Only `tfsf` supplies the paired electric/magnetic corrections for one-way incidence.

Case 38 uses a scalar x/z eigenfunction to seed `Ez`, then evolves the complete vector Maxwell system. The excitation includes both propagation directions and can include radiation and other modes. The scalar seed index is saved for inspection; it is not a full-vector modal propagation constant. The electric detector map does not establish bend insertion loss. A vector port solver, forward/backward mode decomposition, straight-waveguide calibration, and mesh/depth convergence are needed for that quantity.

## Numerical implementation

`fdtd/three_d.py` evolves all six fields on a Yee grid, with array order `(x,y,z)`:

| Component | Spatial sample, in cell indices |
|---|---|
| Ex | (i+1/2, j, k) |
| Ey | (i, j+1/2, k) |
| Ez | (i, j, k+1/2) |
| Hx | (i, j+1/2, k+1/2) |
| Hy | (i+1/2, j, k+1/2) |
| Hz | (i+1/2, j+1/2, k) |

Electric fields in the arrays are `E/Z0`; magnetic fields use the corresponding normalized amplitude convention. Source amplitudes are arbitrary, with no watt or joule calibration. E and H are also offset by half a time step. Do not multiply raw E/H arrays to claim calibrated power without spatial and temporal interpolation and a source normalization.

Faraday updates use forward differences, and Ampère updates use backward differences. Materials are positive, isotropic, nondispersive relative permittivity and optional nonnegative conductivity. Relative permeability is one. Node-sampled permittivity and conductivity are averaged to each electric edge. This is a basic staircased material representation, not a conformal or subpixel interface method.

Ohmic conduction is time-centered: with `q = σ dt/(2 ε0 εr)`, the old electric field is multiplied by `(1-q)/(1+q)`, and the curl increment is divided by `εr(1+q)`. The CFL ratio is

```text
c0 dt sqrt(dx^-2 + dy^-2 + dz^-2) / sqrt(min εr) <= 1.
```

The convolutional PML stretches each derivative independently with a cubic depth profile. Its recurrence is `ψ_new = b ψ_old + (b-1) ΔF`, and the stretched difference is `ΔF + ψ_new`, with `b=exp(-rate dt)`. Profiles are evaluated on the appropriate electric/magnetic integer or half-integer sites. This implementation uses stretch κ=1 and frequency shift α=0. The configured reflection value controls the continuous-profile design; it is not a measured reflection guarantee. Interfaces reaching PML and strongly evanescent or grazing fields require their own convergence checks.

PEC walls use staircased excluded electric edges; an edge touching a PEC node is suppressed. At external PEC faces only tangential electric components are constrained. Thus the sampled opening mask and the exact effective electromagnetic aperture differ by component-dependent edge placement. Mur is first order for each tangential component, with sequential edge/corner treatment; it is an approximate alternative to PML.

The normal TF/SF source is a planar boundary at `source_y`, with electric and magnetic time/space staggering. It requires uniform, lossless incident material and periodic x/z. Spectrum extraction is restricted to uniform normal-incidence layered media and uses a reference run. There is no general oblique TF/SF box or diffraction-order power extraction.

## Saved outputs

Each `results_3d/<experiment>/` contains:

- `config.json`: complete settings and the originating 2D script.
- `diagnostics.json`: grid, spacing, time step, CFL ratio, resolution in the highest-index material, runtime, solver hashes, finite-field check, and diagnostic definitions.
- `data.npz`: all six final field volumes; material/conductor volumes; XY, XZ, and YZ field snapshots; sampled energy history; electric detector phasors and mean-square map; detector trace; animation sections and their time steps. Case 23 also contains calibrated normal-incidence spectra and reference probes.
- `fields.png`: final field and material sections.
- `snapshots.png`: propagation in the center-z XY plane.
- `volume_sections.png`: three spatially placed field sections in 3D perspective.
- `diagnostics.png`: field-energy proxy and x/z detector map.
- `animation.gif`: time evolution of the center-z XY section, when requested.

The whole-grid energy proxy includes PML. It uses staggered fields and is not an exact discrete conservation invariant. Its default sampling interval is ten steps; the final sample can have a different carrier phase from previous samples. Set `energy_stride=1` when studying its within-cycle variation. The detector mean-square map sums squared staggered electric components and is **not** calibrated irradiance, Poynting flux, antenna gain, or mode power. Detector arrays cover the full stored x/z plane; exclude x/z PML strips from physical measurements, since their fading edges are absorption rather than diffraction zeros. In a dipole pulse, the source can store and return near-field energy: cavity conservation is therefore checked after the source turns off rather than against the driven peak. An unmodulated Gaussian current pulse can leave a static electric field associated with deposited charge; a nonzero final field alone is not evidence of a boundary failure.

Volumes use float32 to control memory; scalar energy accumulation uses float64. PML derivative histories are stored only in compact boundary slabs, and uniform, lossless material coefficients are represented by scalars. Frames retain sections rather than hundreds of full volumes. The final native implementation completed a 50-step, 12.8-million-cell homogeneous benchmark in about 4.1 seconds with about 712 MB of process peak memory on this computer; heterogeneous materials and longer frame histories require more. Full-duration runs are appreciably heavier than the 2D examples; the batch runner executes experiments sequentially and checkpoints its summary after each case.

## Validation and research use

`tests/test_three_d.py` checks the native/NumPy agreement; reduction to the existing 2D solver in a depth-independent layered problem; wave speed; one-way injection; plane-wave and full-vector six-face absorption; Fresnel amplitude and conductivity attenuation; slab spectral conservation; rotational/translation behavior of a vector dipole; finite apertures and PEC constraints; invalid inputs; exact 24-case coverage; preserved 2D parameters; and standalone outputs.

See `THREE_D_VALIDATION.md` for the actual completed run audit. A successful run and these benchmark tests validate the implementation within their coverage. They do not establish publication-level convergence for every application.

For a quantitative study, first enlarge the depth and check the detector and absorbing boundaries independently. Then refine **all three** spacings while scaling cell-based dimensions, PML widths, source locations, layers, detector indices, and time-step count to preserve physical geometry and duration. Keep beam/aperture physical dimensions fixed during this mesh study. Compare calibrated observables, not arbitrary source amplitudes. Thin apertures, high-index interfaces, curved waveguide walls, and oblique beams are especially sensitive to discretization. The current optical materials remain nondispersive; ultrafast nonlinear or dispersive media need additional constitutive equations.
