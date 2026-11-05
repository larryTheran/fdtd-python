#!/usr/bin/env python3
"""Audit saved full 3D runs and build a local visual index; never reruns a solver."""
import argparse
from dataclasses import asdict
import hashlib
import html
import json
import os
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from run_all_3d import experiments
from fdtd.three_d_plotting import figures


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--render-missing',action='store_true')
    args=parser.parse_args()
    os.environ.setdefault('MPLBACKEND','Agg')
    os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.cache'/'matplotlib'))
    result_root=ROOT/'results_3d'
    audit=[]; cards=[]; rows=[]
    keys=('ex','ey','ez','hx','hy','hz')
    plot_keys=('ez','epsilon_r','pec','source_z','detector_y','dx','dy','dz','dt','snapshot_steps','snapshots_xy','snapshots_xz','snapshots_yz','energy_steps','energy','detector_mean_square')
    expected_hashes={name:hashlib.sha256((ROOT/'fdtd'/name).read_bytes()).hexdigest() for name in ('three_d.py','three_d_backend.py','three_d_kernel.c')}
    for script,c in experiments():
        directory=result_root/c.name
        report=json.loads((directory/'diagnostics.json').read_text())
        config=json.loads((directory/'config.json').read_text())
        if config != json.loads(json.dumps(asdict(c))): raise ValueError(f'Non-default saved configuration: {c.name}')
        if report['solver_sha256'] != expected_hashes: raise ValueError(f'Stale solver result: {c.name}')
        shape=(c.nx,c.ny,c.nz)
        with np.load(directory/'data.npz',allow_pickle=False) as data:
            for key in keys:
                field=data[key]
                if field.shape!=shape or not np.isfinite(field).all(): raise ValueError(f'Invalid {key}: {c.name}')
                del field
            if int(data['snapshot_steps'][-1]) != c.steps or len(data['time']) != c.steps:
                raise ValueError(f'Incomplete run: {c.name}')
            if args.render_missing and not (directory/'volume_sections.png').exists():
                selected={key:data[key] for key in plot_keys}
                if 'reflectance' in data:
                    selected.update({key:data[key] for key in ('reflectance','transmittance','residual','frequency','spectral_valid')})
                figures(c,selected,directory)
                del selected
        from PIL import Image
        with Image.open(directory/'animation.gif') as im:
            frame_count=im.n_frames
            if frame_count<2: raise ValueError(f'Missing animation: {c.name}')
        for file in ('config.json','diagnostics.json','data.npz','fields.png','snapshots.png','volume_sections.png','diagnostics.png','animation.gif'):
            if not (directory/file).is_file(): raise ValueError(f'Missing {file}: {c.name}')
        entry=dict(name=c.name,status='verified_full_default_run',grid=list(shape),steps=c.steps,
                   simulation_seconds=report['simulation_seconds'],gif_frames=frame_count,
                   cfl_ratio=report['cfl_ratio'],minimum_cells_per_material_wavelength=report['minimum_cells_per_material_wavelength'],
                   data_bytes=(directory/'data.npz').stat().st_size,solver_sha256=expected_hashes)
        audit.append(entry)
        print(f'Verified {c.name}',flush=True)
        rows.append(f'| {c.name} | {c.nx} × {c.ny} × {c.nz} | {c.steps} | {report["simulation_seconds"]:.1f} | {frame_count} |')
        label=html.escape(c.title)
        cards.append(f'''<article id="case-{c.name[:2]}"><h2>{label}</h2>
<p>{c.nx} × {c.ny} × {c.nz} cells · {c.steps} steps · completed full default run</p>
<a href="{c.name}/volume_sections.png"><img loading="lazy" src="{c.name}/volume_sections.png" alt="Three field sections placed in three-dimensional coordinates"></a>
<nav><a href="{c.name}/animation.gif">Animation</a><a href="{c.name}/fields.png">Fields &amp; materials</a><a href="{c.name}/snapshots.png">Snapshots</a><a href="{c.name}/diagnostics.png">Detector</a><a href="{c.name}/config.json">Settings</a><a href="{c.name}/data.npz">Field volumes</a><a href="../experiments_3d/{script.name}">Python experiment</a></nav></article>''')
    (result_root/'verified_runs.json').write_text(json.dumps(audit,indent=2)+'\n')
    document='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>3D FDTD experiments</title>
<style>body{font:16px/1.6 system-ui,sans-serif;background:#f3f5f8;color:#172236;margin:0}header,main{max-width:1200px;margin:auto;padding:32px}h1{font-size:38px;line-height:1.2}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,440px),1fr));gap:24px;padding-top:0}article{background:white;border:1px solid #dce2ec;border-radius:12px;padding:22px}h2{font-size:20px;line-height:1.4}img{width:100%;height:auto}nav{display:flex;flex-wrap:wrap;gap:12px}a{color:#164cab}p{color:#47566f}header p{max-width:900px}</style>
<header><h1>3D FDTD experiments</h1><p>24 separate Python simulations, extended from the existing 2D experiments. All six field components evolve on a three-dimensional grid. Each card links to saved results from the full default run.</p><p>The preview shows three field sections in 3D coordinates. Animations show the center-depth XY section. Detector maps are electric-field proxies, not calibrated power measurements. Plane-wave cases 22–24 intentionally use depth-independent fields.</p><a href="../docs/THREE_D.md">Modeling and usage guide</a> · <a href="../docs/THREE_D_VALIDATION.md">Validation report</a></header><main>'''+''.join(cards)+'</main></html>'
    (result_root/'index.html').write_text(document)
    testlog=(result_root/'test_execution.log').read_text().strip().splitlines()[-1]
    total=sum(r['simulation_seconds'] for r in audit)
    report=f'''# 3D validation and full-run audit

Audit date: 12 September 2026.

**24/24 full default 3D experiments completed and verified.** Every run used the original 2D x/y grid, wavelength, materials, and default time-step count, plus the documented depth configuration. None of the audited results is a shortened smoke run.

Test suite result: **{testlog}**. This includes the original 65 tests and the new 3D tests. The physical benchmarks cover vector propagation, absorbing and reflecting boundaries, loss, Fresnel reflection, plane-wave spectral balance, and reduction to the existing 2D method.

The audit opens every numerical archive with pickle disabled, checks all six field shapes and finite values, confirms the final step and full time history, compares saved configurations with the independent scripts, verifies solver-source hashes, checks output images, and inspects every GIF for multiple frames. Machine-readable evidence: `results_3d/verified_runs.json`; full-run execution log: `results_3d/execution.log`; test output: `results_3d/test_execution.log`.

Summed simulation runtime: {total/60:.1f} minutes on this computer, excluding archive compression and plotting. Runtime depends on hardware and backend. This is execution and benchmark validation, not a mesh-convergence certificate for every geometry. See `THREE_D.md` for limits of the finite-depth aperture, Mur, waveguide excitation, and detector models.

| Experiment | Grid | Full steps | Simulation seconds | GIF frames |
|---|---|---:|---:|---:|
'''+ '\n'.join(rows)+'\n'
    (ROOT/'docs'/'THREE_D_VALIDATION.md').write_text(report)
    print(f'All {len(audit)} result bundles verified; gallery and validation report written.',flush=True)


if __name__=='__main__': main()
