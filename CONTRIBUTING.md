# Contributing

Keep contributions small enough to review and provide a runnable reproducer. Include the experiment name, configuration/CLI overrides, Python and dependency versions, operating system, backend/workers, and observed/expected behavior in bug reports.

## Numerical changes

Preserve experiment IDs and explicit source/thesis mappings. Explain the numerical equations, staggering, boundary/source assumptions, SI units, and any changed interpretation. Add an analytical or invariance check that can fail independently of the implementation; a reference output alone is insufficient. Run `python -m pytest -q`. For native changes, compare all six components against NumPy and sequential/threaded native execution. For a 3D preview change, verify that callbacks do not change solution arrays and run `python tools/check_live_fdtd.py` with the optional notebook dependencies.

Do not replace archived reference results with truncated smoke runs. Use a separate `--output runs/<study>` directory and record convergence in space, depth, absorbing layers, and time before making quantitative claims.

## Environment

Use Python 3.12 and an isolated environment. Install `requirements-dev.txt` and, for live notebook tests, `requirements-notebook.txt`. `constraints-ci.txt` constrains NumPy, SciPy, and Matplotlib to the stable scientific stack used for current publication checks. GitHub Actions runs small automated cases on Linux and macOS; it does not rerun the full default batch or download multi-gigabyte result archives.

## Documentation and provenance

`docs/EXPERIMENTS.md`, `docs/experiments.json`, source audit files, and historical validation reports are published evidence. `tools/build_reports.py` and `tools/build_3d_reports.py` regenerate reports from complete local results and test logs, so restore the corresponding release first and review the resulting diff. `tools/audit_sources.py` was written for the original archive layout, with the source collection in the project parent directory and the project directory named `python_fdtd`; it should not be run blindly from a clone with unrelated sibling folders. Its existing audit records remain usable without the original private/local collection.

Literature reviews under `research_reviews/` describe proposals rather than completed simulation results. Keep primary references and the distinction between completed validation and future work.

## Generated data

Source, small metadata, and selected browsable previews belong in Git. Full arrays/GIF collections belong in the release result archives, accompanied by file hashes and restore instructions. Remove environment folders, caches, compiled local accelerators, machine-specific paths, credentials, and unrelated personal material before submission. Do not attach tokens or passwords to an issue.

The repository currently has no newly granted open-source license; see `LICENSING.md` before submitting material whose redistribution rights differ from the current collection.
