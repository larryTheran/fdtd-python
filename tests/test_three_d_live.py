"""Bounded live preview checks; no default experiment or saved results are run."""
from dataclasses import replace
import base64
import numpy as np
import pytest
from fdtd.three_d import Config3D,simulate
from fdtd.three_d_live import LiveFieldPreview,validate_options


def tiny(**changes):
    config=Config3D('live-test','Live field test','',nx=14,ny=16,nz=12,steps=16,
        source_x=7,source_y=7,source_z=6,geometry='free',injection='point',source='sine',
        boundary_x='periodic',boundary_y='periodic',boundary_z='periodic',
        backend='numpy',energy_stride=3,snapshots=(4,12))
    return replace(config,**changes)


def test_preview_does_not_change_numerical_results_and_is_bounded():
    config=tiny()
    baseline=simulate(config)
    frames=[]
    observed=simulate(config,on_frame=frames.append,preview_stride=3,preview_interval=0)
    assert [frame.step for frame in frames]==[0,3,6,9,12,15,16]
    assert frames[0].time_s==0 and frames[-1].time_s==config.steps*float(observed['dt'])
    for key in baseline:
        assert np.array_equal(baseline[key],observed[key]),key
    for frame in frames:
        assert [a.shape for a in frame.fields]==[(14,16),(14,12),(16,12)]
        assert all(a.ndim==2 and not a.flags.writeable for a in (*frame.fields,*frame.epsilon_r,*frame.pec))
        assert all(not np.shares_memory(a,observed['ez']) for a in frame.fields)
        assert frame.epsilon_r is frames[0].epsilon_r and frame.pec is frames[0].pec
        assert 0 <= frame.energy_step <= frame.step
    assert np.array_equal(frames[-1].fields[0],observed['ez'][:,:,6])
    assert np.array_equal(frames[-1].fields[1],observed['ez'][:,int(observed['detector_y']),:])
    assert np.array_equal(frames[-1].fields[2],observed['ez'][7,:,:])
    # Even a malicious observer only gets detached section arrays.
    def mutate_copy(frame):
        frame.fields[0].flags.writeable=True
        frame.fields[0][:]=99
    mutated=simulate(config,on_frame=mutate_copy,preview_interval=0)
    assert np.array_equal(mutated['ez'],baseline['ez'])


def test_preview_time_throttle_keeps_initial_and_final():
    steps=[]
    simulate(tiny(),on_frame=lambda frame: steps.append(frame.step),preview_interval=3600)
    assert steps==[0,16]


@pytest.mark.parametrize('options',[{'preview_stride':0},{'preview_stride':True},{'preview_stride':1.5},
    {'preview_interval':-1},{'preview_interval':float('nan')},{'on_frame':'not callable'}])
def test_bad_preview_options_fail_before_callback(options):
    with pytest.raises(ValueError): simulate(tiny(),**options)


def test_invalid_physics_does_not_publish_preview():
    calls=[]
    with pytest.raises(ValueError): simulate(tiny(courant=2),on_frame=calls.append)
    assert not calls


def test_preview_failure_and_interrupt_do_not_get_swallowed():
    class DisplayFailure(Exception): pass
    def fail(frame):
        if frame.step: raise DisplayFailure('display is unavailable')
    with pytest.raises(DisplayFailure): simulate(tiny(),on_frame=fail,preview_interval=0)
    with pytest.raises(KeyboardInterrupt):
        with LiveFieldPreview(tiny()) as preview:
            raise KeyboardInterrupt()
    assert preview.closed and preview.figure is None


def test_live_artists_and_display_id_reused_then_cleaned(monkeypatch):
    IPython_display=pytest.importorskip('IPython.display')
    calls=[]
    class Handle:
        def update(self,data,**kwargs): calls.append(('update',data,kwargs))
    handle=Handle()
    def publish(data,**kwargs):
        calls.append(('display',data,kwargs)); return handle
    monkeypatch.setattr(IPython_display,'display',publish)
    config=tiny(steps=4)
    frames=[]
    simulate(config,on_frame=frames.append,preview_interval=0)
    with LiveFieldPreview(config) as preview:
        preview(frames[0]); figure=preview.figure; images=list(preview.images)
        for frame in frames[1:]:
            preview(frame)
            assert preview.figure is figure and preview.images==images
        assert len(figure.axes)==12 # six plots, six colorbars, never per-frame growth
        assert preview.handle is handle
        assert len(calls)==5 and calls[0][0]=='display' and all(c[0]=='update' for c in calls[1:])
        assert calls[0][2]=={'raw':True,'display_id':True}
        assert all(c[2]=={'raw':True} for c in calls[1:])
        pngs=[base64.b64decode(c[1]['image/png']) for c in calls]
        assert all(p.startswith(b'\x89PNG') for p in pngs) and len(set(pngs))>2
        assert 'step 4/4' in calls[-1][1]['text/plain']
    assert preview.closed and preview.figure is None and preview.images==[] and preview.handle is None


def test_runner_auto_notebook_and_cli_options_are_observational(tmp_path,monkeypatch):
    import fdtd.three_d_live as live_module
    import fdtd.three_d_runner as runner
    calls=[]
    class Preview:
        def __init__(self,config): pass
        def __enter__(self): return self
        def __exit__(self,*args): calls.append('closed')
        def __call__(self,frame): calls.append(frame.step)
    monkeypatch.setattr(live_module,'LiveFieldPreview',Preview)
    monkeypatch.setattr(live_module,'in_notebook',lambda: True)
    runner.run(tiny(steps=2),tmp_path/'notebook',plots=False,live=True,live_fps=10)
    assert calls==[0,2,'closed']
    calls.clear()
    import fdtd.three_d_plotting as plotting
    monkeypatch.setattr(plotting,'figures',lambda *args: calls.append('saved final plots'))
    runner.run(tiny(steps=2),tmp_path/'automatic',plots=True)
    assert calls==[0,2,'closed','saved final plots']
    calls.clear()
    runner.run(tiny(steps=2),tmp_path/'disabled',plots=False,live=False)
    assert calls==[]
    monkeypatch.setattr(live_module,'in_notebook',lambda: False)
    runner.run(tiny(steps=2),tmp_path/'terminal',plots=False)
    assert calls==[]
    with pytest.raises(ValueError): runner.run(tiny(),tmp_path/'invalid',live=True)
    assert not (tmp_path/'invalid').exists()
    with pytest.raises(ValueError): runner.run(tiny(),tmp_path/'bad-fps',live_fps=float('nan'))
    assert not (tmp_path/'bad-fps').exists()
    import argparse
    parser=argparse.ArgumentParser(); runner.add_arguments(parser)
    args=parser.parse_args(['--no-live','--live-stride','8','--live-fps','2'])
    assert args.live is False and args.live_stride==8 and args.live_fps==2
    assert parser.parse_args([]).live is None


@pytest.mark.parametrize('flag,expected', [('--live', True), ('--no-live', False)])
def test_batch_forwards_live_controls_for_each_simulation(tmp_path, monkeypatch, flag, expected):
    import run_all_3d as batch

    configs = [tiny(name='first'), tiny(name='second')]
    monkeypatch.setattr(batch, 'experiments', lambda: [(None, config) for config in configs])
    calls = []
    def fake_run(config, output, gif, frames, plots, **kwargs):
        calls.append((config.name, output, plots, kwargs))
        return {}, {'name': config.name}
    monkeypatch.setattr(batch, 'run', fake_run)

    batch.main(['--output', str(tmp_path), '--no-plots', flag, '--live-stride', '7', '--live-fps', '1.5'])
    assert calls == [
        (c.name, tmp_path / c.name, False, dict(live=expected, live_stride=7, live_fps=1.5))
        for c in configs
    ]


@pytest.mark.parametrize('stride,fps',[(0,4),(True,4),(1.5,4),(1,0),(1,float('inf')),(1,11)])
def test_live_option_validation(stride,fps):
    with pytest.raises(ValueError): validate_options(stride,fps)


def test_native_preview_observer_leaves_threaded_fields_identical():
    config=tiny(backend='native',workers=3,steps=6)
    baseline=simulate(config)
    frames=[]
    observed=simulate(config,on_frame=frames.append,preview_interval=0)
    assert len(frames)==7
    for key in baseline:
        assert np.array_equal(baseline[key],observed[key]),key
