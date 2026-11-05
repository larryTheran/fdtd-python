# Saved simulation results

Complete archived result files are published as GitHub release downloads. The code repository retains browsable preview images, configuration/diagnostic metadata, experiment indexes, and checksums under [`results-catalog/`](../results-catalog/). The solver's original `results/` and `results_3d/` trees are restored from those archives, without committing multi-gigabyte numerical volumes into Git history.

## Browse

- [Result catalog](../results-catalog/README.md)
- [All release downloads](https://github.com/larryTheran/fdtd-python/releases)
- [1D/2D script catalog](EXPERIMENTS.md)
- [3D experiment guide](THREE_D.md)

The publication contains the available result folders supplied with the project, including their PNG/GIF images, numerical arrays, exact configurations, diagnostics, and historical reports. Availability of an archived result is distinct from independent physical convergence or agreement with a thesis figure.

## Release downloads

The snapshot release is [`results-2026-11-04`](https://github.com/larryTheran/fdtd-python/releases/tag/results-2026-11-04). It covers **491 files totaling 2,889,417,070 uncompressed bytes**, with results for 14 one-dimensional, 24 two-dimensional, and 24 three-dimensional experiments. Download every 3D part to restore all 3D cases; each part is an independent ZIP containing complete experiment folders.

| Download | Compressed size | Contents and restored location |
|---|---:|---|
| [1D results](https://github.com/larryTheran/fdtd-python/releases/download/results-2026-11-04/fdtd-results-1d.zip) | 14.2 MiB | 14 experiment folders under `results/` |
| [2D results](https://github.com/larryTheran/fdtd-python/releases/download/results-2026-11-04/fdtd-results-2d.zip) | 431.0 MiB | 24 experiment folders under `results/` |
| [3D results, part 1](https://github.com/larryTheran/fdtd-python/releases/download/results-2026-11-04/fdtd-results-3d-part-01.zip) | 849.6 MiB | Complete experiment folders under `results_3d/` |
| [3D results, part 2](https://github.com/larryTheran/fdtd-python/releases/download/results-2026-11-04/fdtd-results-3d-part-02.zip) | 741.7 MiB | Complete experiment folders under `results_3d/` |
| [3D results, part 3](https://github.com/larryTheran/fdtd-python/releases/download/results-2026-11-04/fdtd-results-3d-part-03.zip) | 719.0 MiB | Complete experiment folders under `results_3d/` |
| [Report/support files](https://github.com/larryTheran/fdtd-python/releases/download/results-2026-11-04/fdtd-results-support.zip) | 0.15 MiB | Original gallery/index, run summaries, logs, and support metadata |

[Archive sizes and SHA-256](../results-catalog/archives.json) · [Per-file JSON manifest](../results-catalog/manifest.json) · [CSV manifest](../results-catalog/manifest.csv) · [Per-experiment records](../results-catalog/experiments.json)

The release link is stable for this recorded snapshot; publication status and release assets can be checked on its release page. Compare each downloaded archive against `archives.json`, then verify extracted paths and hashes against `manifest.json` if auditing the full snapshot.

## Restore

Download the release assets listed in the result catalog, verify their SHA-256 values, and extract them at the repository root. The archives preserve original relative paths so the original report galleries and analysis tools can locate `results/<experiment>/` and `results_3d/<experiment>/`.

Use an empty checkout or restore into a separate temporary folder before copying results if local output folders already contain your own parameter studies. The result catalog records each file's original relative path, byte count, and hash; retain the supplied `config.json` and `diagnostics.json` with its data.

## Read and compare

```python
from pathlib import Path
import numpy as np

folder = Path("results/06_lossless_two_layers")
with np.load(folder / "data.npz", allow_pickle=False) as data:
    fields = data["e"]
    time_seconds = data["time"]
```

3D files store six staggered field components in `(x, y, z)` order. They can be large: inspect metadata and select the needed arrays rather than loading every volume at once. The [3D output definitions](THREE_D.md#saved-outputs) describe the sections, detector maps, energy proxy, and units.

A new solver revision can differ from the solver hashes stored in historical diagnostics. Archived files preserve that history. To compare changes, rerun the matching script/configuration into a separate `--output` folder and record the current commit/environment, instead of overwriting the archive.

Exact release archive names, byte counts, and per-file manifests are maintained by the result publication catalog.
