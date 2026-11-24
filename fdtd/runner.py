"""Shared command line and reproducible outputs for individually runnable scripts."""
import argparse
from dataclasses import asdict, replace
import json
import math
import os
from pathlib import Path
import time
import numpy as np
from .cli import parse_arguments
from .config import Config1D
from .analysis import diagnostics

ROOT = Path(__file__).resolve().parents[1]


def run(config, output=None, show=False, gif=False, frames=80, plots=True):
    # Keep the font cache inside this project; avoid changing global Python settings.
    os.environ.setdefault("MPLCONFIGDIR", str(ROOT/".cache"/"matplotlib"))
    if not show:
        os.environ.setdefault("MPLBACKEND", "Agg")
    output = Path(output) if output is not None else ROOT/"results"/config.name
    output.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter()
    stride = max(1, math.ceil(config.steps/max(2, frames))) if gif else 0
    if isinstance(config, Config1D):
        from .one_d import simulate, spectrum
        result = simulate(config, stride)
        if config.spectra:
            baseline = simulate(config, reference=True)
            result.update(spectrum(config, result, baseline))
            result["reference_probes"] = baseline["probes"]
    else:
        from .two_d import simulate, spectrum
        result = simulate(config, stride)
        if config.spectra:
            baseline = simulate(config, reference=True)
            result.update(spectrum(config, result, baseline))
            result["reference_probes"] = baseline["probes"]
    report = diagnostics(config, result)
    report["simulation_seconds"] = time.perf_counter()-start
    report["numpy_version"] = np.__version__
    report["notes"] = config.notes
    np.savez_compressed(output/"data.npz", **result)
    (output/"config.json").write_text(json.dumps(asdict(config), indent=2)+"\n")
    (output/"diagnostics.json").write_text(json.dumps(report, indent=2, allow_nan=False)+"\n")
    if plots:
        from .plotting import figures
        figures(config, result, output, show)
    if gif:
        from .plotting import animation
        animation(config, result, output)
    print(f"{config.name}: {config.steps} steps; results in {output}", flush=True)
    return result, report


def main(config, argv=None):
    parser = argparse.ArgumentParser(description=f"{config.title}. {config.thesis}. {config.notes}")
    parser.add_argument("--steps", type=int, help="Override the number of time steps")
    parser.add_argument("--output", type=Path, help="Output directory for this experiment")
    parser.add_argument("--wavelength-nm", type=float, help="Set vacuum wavelength in nm; automatic dx is recomputed")
    parser.add_argument("--sigma", type=float, help="Set conductivity of all existing layers, S/m")
    parser.add_argument("--show", action="store_true", help="Display static figures in a GUI window")
    parser.add_argument("--gif", action="store_true", help="Save an animation.gif")
    parser.add_argument("--frames", type=int, default=80, help="Approximate GIF frame budget (default 80)")
    parser.add_argument("--no-plots", action="store_true", help="Save numerical data only")
    parser.add_argument("--describe", action="store_true", help="Print inputs without simulating")
    if not isinstance(config, Config1D):
        parser.add_argument("--angle", type=float, help="Beam angle in degrees from the +y normal")
        parser.add_argument("--detector-y", type=int, help="Detector row, zero based")
    args = parse_arguments(parser, argv)
    if args.steps is not None:
        config = replace(config, steps=args.steps)
    if args.wavelength_nm is not None:
        config = replace(config, wavelength=args.wavelength_nm*1e-9)
    if args.sigma is not None:
        if not config.layers:
            parser.error("--sigma requires a material experiment")
        config = replace(config, layers=[replace(l, sigma=args.sigma) for l in config.layers])
    for arg, field in [("angle", "angle_deg"), ("detector_y", "detector_y")]:
        if getattr(args, arg, None) is not None:
            config = replace(config, **{field: getattr(args, arg)})
    if args.describe:
        print(json.dumps(asdict(config), indent=2))
        return
    run(config, args.output, args.show, args.gif, args.frames, not args.no_plots)
