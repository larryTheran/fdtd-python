#!/usr/bin/env python3
"""Run the 24 separate 3D counterparts without changing the 1D/2D results."""
import argparse
import importlib.util
import json
import hashlib
import zipfile
from dataclasses import asdict
from pathlib import Path
import numpy as np
from fdtd.cli import parse_arguments
from fdtd.three_d_runner import run,add_arguments,overrides

ROOT=Path(__file__).resolve().parent


def experiments():
    result=[]
    for path in sorted((ROOT/'experiments_3d').glob('[0-9]*.py')):
        spec=importlib.util.spec_from_file_location(path.stem,path)
        module=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result.append((path,module.CONFIG))
    return result


def completed(c,directory,gif,plots):
    """Reuse only complete outputs matching the exact settings and solver."""
    try:
        report=json.loads((directory/'diagnostics.json').read_text())
        config=json.loads((directory/'config.json').read_text())
        expected={name:hashlib.sha256((ROOT/'fdtd'/name).read_bytes()).hexdigest() for name in ('three_d.py','three_d_backend.py','three_d_kernel.c')}
        if config!=json.loads(json.dumps(asdict(c))) or report['solver_sha256']!=expected:
            return None
        required=['data.npz']
        if plots: required+=['fields.png','snapshots.png','volume_sections.png','diagnostics.png']
        if gif: required+=['animation.gif']
        if not all((directory/name).is_file() for name in required): return None
        with np.load(directory/'data.npz',allow_pickle=False) as data:
            if int(data['snapshot_steps'][-1])!=c.steps or len(data['time'])!=c.steps: return None
            for key in ('ex','ey','ez','hx','hy','hz'):
                field=data[key]
                if field.shape!=(c.nx,c.ny,c.nz) or not np.isfinite(field).all(): return None
        return report
    except (OSError,ValueError,KeyError,EOFError,zipfile.BadZipFile):
        return None


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    add_arguments(p)
    p.add_argument('--list',action='store_true')
    p.add_argument('--resume',action='store_true',help='Reuse complete outputs only when configuration and solver hashes match')
    p.add_argument('--only',nargs='+',help='Experiment IDs or name prefixes')
    p.add_argument('--output',type=Path,default=ROOT/'results_3d')
    args=parse_arguments(p, argv)
    selected=[(path,overrides(c,args)) for path,c in experiments() if not args.only or any(c.name.startswith(k.zfill(2) if k.isdigit() else k) for k in args.only)]
    if not selected: p.error('No matching 3D experiments')
    if args.list:
        for path,c in selected: print(f'{c.name:42} {c.nx}×{c.ny}×{c.nz} | {c.steps} steps')
        return
    args.output.mkdir(parents=True,exist_ok=True)
    summary=[]
    for path,c in selected:
        try:
            report=completed(c,args.output/c.name,args.gif,not args.no_plots) if args.resume else None
            if report is None:
                result,report=run(c,args.output/c.name,args.gif,args.frames,not args.no_plots,
                                  live=args.live,live_stride=args.live_stride,live_fps=args.live_fps)
                del result
            else:
                print(f'{c.name}: verified existing full run; reused',flush=True)
            summary.append(dict(status='completed',**report))
        except Exception as exc:
            print(f'FAILED {c.name}: {exc}',flush=True)
            summary.append(dict(name=c.name,status='failed',error=str(exc)))
        # Checkpoint after every experiment, including interrupted long batches.
        (args.output/'run_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    passed=sum(r['status']=='completed' for r in summary)
    print(f'Completed {passed}/{len(selected)} 3D experiments',flush=True)
    if passed != len(selected): raise SystemExit(1)


if __name__=='__main__': main()
