"""Standalone 3D execution and self-contained numerical result bundles."""
import argparse
from contextlib import nullcontext
from dataclasses import asdict,replace
import hashlib
import json
import math
import os
from pathlib import Path
import time
import numpy as np
from .cli import parse_arguments
from .config import C0
from .three_d import simulate,spectrum

ROOT=Path(__file__).resolve().parents[1]


def run(c,output=None,gif=False,frames=40,plots=True,*,live=None,live_stride=1,live_fps=4.):
    os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.cache'/'matplotlib'))
    os.environ.setdefault('MPLBACKEND','Agg')
    from .three_d_live import LiveFieldPreview,in_notebook,validate_options
    live_stride,live_fps=validate_options(live_stride,live_fps)
    if live is not None and not isinstance(live,bool):
        raise ValueError('live must be True, False or None (automatic)')
    notebook=in_notebook()
    if live is True and not notebook:
        raise ValueError('Live plots require an IPython/Jupyter notebook kernel; use --gif for terminal runs')
    live_enabled=notebook if live is None else live
    # Explicit --live may accompany --no-plots; automatic mode follows plots.
    if live is None and not plots: live_enabled=False
    output=Path(output) if output is not None else ROOT/'results_3d'/c.name
    output.mkdir(parents=True,exist_ok=True)
    start=time.perf_counter()
    with LiveFieldPreview(c) if live_enabled else nullcontext() as preview:
        r=simulate(c,max(1,math.ceil(c.steps/max(2,frames))) if gif else 0,
            on_frame=preview,preview_stride=live_stride,preview_interval=1/live_fps)
    if c.spectra:
        baseline=simulate(c,reference=True)
        r.update(spectrum(c,r,baseline))
        r['reference_probes']=baseline['probes']
        del baseline
    dt=float(r['dt']); spacing=[float(r[k]) for k in ('dx','dy','dz')]
    field_names=('ex','ey','ez','hx','hy','hz')
    finite=all(np.isfinite(r[k]).all() for k in field_names)
    if not finite: raise FloatingPointError('Non-finite saved fields')
    energy=r['energy']
    manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__).with_name(k) for k in ('three_d.py','three_d_backend.py','three_d_kernel.c')]}
    report=dict(name=c.name,origin_2d=c.origin_2d,grid=[c.nx,c.ny,c.nz],steps=c.steps,
                finite_fields=finite,backend=str(r['backend']),workers=int(r['workers']),simulation_seconds=time.perf_counter()-start,
                dt_s=dt,spacing_m=spacing,duration_s=c.steps*dt,
                cfl_ratio=C0*dt*np.sqrt(sum(1/d**2 for d in spacing))/np.sqrt(float(r['epsilon_r'].min())),
                minimum_cells_per_material_wavelength=c.wavelength/(max(spacing)*np.sqrt(float(r['epsilon_r'].max()))),
                field_component_max={k:float(np.max(abs(r[k]))) for k in field_names},
                energy_final_over_peak=float(energy[-1]/max(energy.max(),np.finfo(float).tiny)),
                energy_note='Staggered-field proxy; includes PML and is not an exact discrete invariant or calibrated joules.',
                detector_note='Mean sum of squared staggered electric components; not calibrated Poynting flux or antenna gain.',
                average_steps=int(r['average_steps']),numpy_version=np.__version__,solver_sha256=manifest,notes=c.notes)
    if 'scalar_seed_neff' in r: report['scalar_seed_neff']=float(r['scalar_seed_neff'])
    np.savez_compressed(output/'data.npz',**r)
    (output/'config.json').write_text(json.dumps(asdict(c),indent=2)+'\n')
    (output/'diagnostics.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    if plots:
        from .three_d_plotting import figures
        figures(c,r,output)
    if gif:
        from .three_d_plotting import animation
        animation(c,r,output)
    print(f'{c.name}: {c.steps} steps on {c.nx}×{c.ny}×{c.nz}; {report["simulation_seconds"]:.1f}s; {output}',flush=True)
    return r,report


def add_arguments(parser):
    parser.add_argument('--steps',type=int,help='Override time steps (short runs do not establish physical convergence)')
    parser.add_argument('--nz',type=int,help='Change depth cells; preserve dz and center the source')
    parser.add_argument('--pml-z',type=int,help='PML thickness on each z face')
    parser.add_argument('--slit-height',type=int,help='Aperture height in z cells')
    parser.add_argument('--source-width-z',type=float,help='Gaussian source radius in z cells')
    parser.add_argument('--backend',choices=['auto','native','numpy'])
    parser.add_argument('--workers',type=int,choices=[1,2,3],help='Concurrent native field components (default 3; NumPy uses one)')
    parser.add_argument('--gif',action='store_true')
    parser.add_argument('--frames',type=int,default=40)
    parser.add_argument('--no-plots',action='store_true')
    live=parser.add_mutually_exclusive_group()
    live.add_argument('--live',dest='live',action='store_true',help='Live field sections in an IPython notebook (automatic there)')
    live.add_argument('--no-live',dest='live',action='store_false',help='Disable notebook live plotting')
    parser.set_defaults(live=None)
    parser.add_argument('--live-stride',type=int,default=1,help='Minimum solver steps between live frames (default 1)')
    parser.add_argument('--live-fps',type=float,default=4.,help='Maximum intermediate preview frames per second, >0 and <=10 (default 4)')


def overrides(c,args):
    changes={field:getattr(args,arg) for arg,field in [('steps','steps'),('nz','nz'),('pml_z','pml_cells_z'),('slit_height','slit_height'),('source_width_z','source_width_z'),('backend','backend'),('workers','workers')] if getattr(args,arg,None) is not None}
    if 'nz' in changes: changes['source_z']=None
    return replace(c,**changes)


def main(config,argv=None):
    parser=argparse.ArgumentParser(description=config.title+' — '+config.notes)
    add_arguments(parser)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--describe',action='store_true')
    args=parse_arguments(parser, argv)
    config=overrides(config,args)
    if args.describe:
        print(json.dumps(asdict(config),indent=2)); return
    run(config,args.output,args.gif,args.frames,not args.no_plots,live=args.live,live_stride=args.live_stride,live_fps=args.live_fps)
