# Public-repository preparation checks

Checked on 4 November 2026 against the clean staged source, before initial publication.

- 14 one-dimensional, 24 two-dimensional (20 primary plus four supplemental), and 24 three-dimensional independently runnable experiment scripts were retained.
- The solver, experiment, tool, and test files match the supplied source byte-for-byte. Environment/cache files and generated numerical result trees are excluded from Git; complete archived result files are distributed separately with hashes.
- The complete automated suite passed: **125 tests**, no failures, in 20.68 seconds on Apple Silicon using Python 3.12, NumPy 1.26.4, SciPy 1.16.1, and Matplotlib 3.8.4. A dateutil deprecation warning did not affect execution. A temporary pure-Python pytest driver was used without changing installed scientific packages.
- `python run_all.py --list` and `python run_all_3d.py --list` identified all 38 original cases and 24 3D counterparts.
- `python tools/check_live_fdtd.py` passed in a separate real Jupyter kernel: five distinct evolving PNG frames, one stable display ID, completed state, and no pyplot figure leak. The tiny test uses temporary output and does not run a full default experiment.
- GitHub Actions configuration targets Python 3.12 on Linux/macOS, uses the stable scientific constraints, runs the automated suite and real-Jupyter smoke, and lists both catalogs. The remote workflow status is separate from these completed local checks and becomes available after publication.

The numerical-method definitions, provenance, historical run reports, and limitations remain in the source documentation. Passing these checks does not establish mesh/depth/time convergence or calibrated physical observables for every experiment.
