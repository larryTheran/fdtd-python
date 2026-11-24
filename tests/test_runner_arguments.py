"""Launch options for standalone, notebook and batch experiments."""
import sys
from types import SimpleNamespace

import pytest
import run_all
import run_all_3d
from fdtd import cli, runner, three_d_runner
from fdtd.config import Config1D, Config2D
from fdtd.three_d import Config3D


@pytest.fixture
def kernel_launcher(monkeypatch):
    arguments = ['-f', '/tmp/example-connection.json', '--debug']
    kernel = SimpleNamespace(parent=SimpleNamespace(argv=arguments.copy()))
    monkeypatch.setattr(cli, 'notebook_kernel', lambda: kernel)
    monkeypatch.setattr(sys, 'argv', ['ipykernel_launcher.py', *arguments])


@pytest.mark.parametrize('entry,config_type', [(runner, Config1D), (runner, Config2D), (three_d_runner, Config3D)])
def test_experiment_arguments_in_notebooks(kernel_launcher, monkeypatch, entry, config_type):
    config = config_type('trial', 'Test', '', steps=9)
    steps = []
    monkeypatch.setattr(entry, 'run', lambda config, *args, **kwargs: steps.append(config.steps))

    entry.main(config)
    entry.main(config, ['--steps', '5'])
    monkeypatch.setattr(sys, 'argv', ['experiment.py', '--steps', '7'])  # IPython %run
    entry.main(config)
    assert steps == [9, 5, 7]

    monkeypatch.setattr(sys, 'argv', ['experiment.py', '--unknown-option'])
    with pytest.raises(SystemExit) as error:
        entry.main(config)
    assert error.value.code == 2


@pytest.mark.parametrize('batch,config_type', [(run_all, Config1D), (run_all_3d, Config3D)])
def test_batch_arguments_in_notebooks(kernel_launcher, monkeypatch, tmp_path, batch, config_type):
    config = config_type('trial', 'Test', '', steps=2)
    monkeypatch.setattr(batch, 'ROOT', tmp_path)
    monkeypatch.setattr(batch, 'experiments', lambda: [(tmp_path/'trial.py', config)])
    steps = []
    def record(config, *args, **kwargs):
        steps.append(config.steps)
        return {}, {}
    monkeypatch.setattr(batch, 'run', record)

    batch.main()
    batch.main(['--steps', '3'])
    monkeypatch.setattr(sys, 'argv', ['run_all.py', '--list'])
    batch.main()
    assert steps == [2, 3]
