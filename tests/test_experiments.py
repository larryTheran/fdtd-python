"""Every separate script must import and produce finite, correctly shaped fields."""
from dataclasses import replace
import subprocess
import sys
import numpy as np
import pytest
from run_all import experiments, ROOT
from fdtd import Config1D
from fdtd.one_d import simulate
from fdtd.two_d import simulate as simulate2


@pytest.mark.parametrize("path,config", experiments(), ids=lambda v: getattr(v, "name", str(v)))
def test_every_experiment_runs(path, config):
    c = replace(config, steps=8)
    r = simulate(c) if isinstance(c, Config1D) else simulate2(c)
    assert np.isfinite(r["e"]).all()
    assert len(r["energy"]) == 8
    assert r["snapshot_steps"][-1] == 8


def test_standalone_cli_and_saved_outputs(tmp_path):
    script = ROOT/"experiments/one_d/03_tfsf_pulse.py"
    subprocess.run([sys.executable, str(script), "--steps", "180", "--output", str(tmp_path),
                    "--gif", "--frames", "8"], cwd=tmp_path, check=True, capture_output=True)
    assert all((tmp_path/f).exists() for f in ["data.npz", "config.json", "diagnostics.json",
                                               "fields.png", "animation.gif"])
    from PIL import Image
    with Image.open(tmp_path/"animation.gif") as im:
        assert im.n_frames > 1
    with np.load(tmp_path/"data.npz", allow_pickle=False) as r:
        assert r["e"].shape == (200,)
