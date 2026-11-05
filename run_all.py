#!/usr/bin/env python3
"""Run separate experiments, sequentially, and collect their result locations."""
import argparse
import importlib.util
import json
from pathlib import Path
from fdtd.runner import run
from dataclasses import replace

ROOT = Path(__file__).resolve().parent


def experiments():
    result = []
    for path in sorted((ROOT/"experiments").glob("*/*.py"), key=lambda p: p.name):
        spec = importlib.util.spec_from_file_location(path.stem, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result.append((path, module.CONFIG))
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--list", action="store_true")
    p.add_argument("--only", nargs="+", help="Numeric experiment IDs or name prefixes")
    p.add_argument("--group", choices=["one_d", "two_d", "supplemental"])
    p.add_argument("--steps", type=int, help="Override for smoke tests; truncates physical propagation")
    p.add_argument("--gif", action="store_true")
    p.add_argument("--frames", type=int, default=60)
    p.add_argument("--no-plots", action="store_true")
    p.add_argument("--output", type=Path, default=ROOT/"results")
    args = p.parse_args()
    selected = [(path, c) for path, c in experiments()
                if (not args.group or path.parent.name == args.group)
                and (not args.only or any(c.name.startswith(k.zfill(2) if k.isdigit() else k) for k in args.only))]
    if not selected:
        p.error("No matching experiments")
    if args.list:
        for path, c in selected:
            print(f"{c.name:36} {c.thesis}")
        return
    args.output.mkdir(parents=True, exist_ok=True)
    summary, failures = [], []
    for path, c in selected:
        if args.steps is not None:
            c = replace(c, steps=args.steps)
        try:
            _, metrics = run(c, args.output/c.name, gif=args.gif, frames=args.frames, plots=not args.no_plots)
            summary.append({"experiment": c.name, "status": "passed", **metrics})
        except Exception as exc:
            print(f"FAILED {c.name}: {exc}", flush=True)
            summary.append({"experiment": c.name, "status": "failed", "error": str(exc)})
            failures.append(c.name)
    (args.output/"run_summary.json").write_text(json.dumps(summary, indent=2)+"\n")
    print(f"Completed {len(selected)-len(failures)}/{len(selected)} experiments", flush=True)
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
