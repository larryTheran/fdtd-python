"""Small snapshot fixtures for the result release packer."""
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

import pytest

from scripts.pack_results import create_packages


def result_tree(tmp_path):
    source = tmp_path / "simulation"
    experiment = source / "results" / "pulse"
    experiment.mkdir(parents=True)
    (experiment / "config.json").write_text('{"cells": 8, "steps": 3}')
    (source / "results_3d").mkdir()
    return source


def pack(source, assets, catalog):
    create_packages(source, assets, catalog, "example/fdtd", "sample", 1024 * 1024, False)


@pytest.mark.parametrize("link", [
    "results_3d", "results/linked_experiment", "results/report.txt",
    "results/pulse/linked_frames", "results/pulse/missing",
])
def test_symlinks_rejected_before_creating_output(tmp_path, link):
    source = result_tree(tmp_path)
    outside = tmp_path / "external"
    outside.mkdir()
    (outside / "config.json").write_text('{"cells": 8, "steps": 3}')
    path = source / link
    if path.is_dir():
        path.rmdir()
    target = outside
    if path.suffix:
        target = outside / "config.json"
    elif path.name == "missing":
        target = outside / "missing"
    path.symlink_to(target)
    with pytest.raises(ValueError, match="(?i)symlink"):
        pack(source, tmp_path / "assets", tmp_path / "catalog")
    assert not (tmp_path / "assets").exists()
    assert not (tmp_path / "catalog").exists()


@pytest.mark.parametrize(("assets_path", "catalog_path"), [
    ("assets", "simulation"),
    ("assets", "simulation/results"),
    ("assets", "simulation/results_3d/nested"),
    ("assets", "assets"),
    ("assets", "assets/nested"),
    ("catalog/assets", "catalog"),
])
def test_overlapping_output_directories_rejected(tmp_path, assets_path, catalog_path):
    source = result_tree(tmp_path)
    readme = source / "README.md"
    readme.write_text("original instructions")
    with pytest.raises(ValueError, match="catalog"):
        pack(source, tmp_path / assets_path, tmp_path / catalog_path)
    assert readme.read_text() == "original instructions"
    assert not (tmp_path / assets_path).exists()


def test_snapshot_catalog_and_checksums_match_generated_files(tmp_path):
    source = result_tree(tmp_path)
    experiment = source / "results/pulse"
    files = {"config.json": (experiment / "config.json").read_bytes()}
    for frame in ("initial", "final"):
        (experiment / frame).mkdir()
        for name in ("fields.png", "diagnostics.json"):
            path = f"{frame}/{name}"
            files[path] = json.dumps(frame).encode()
            (experiment / path).write_bytes(files[path])
    assets = tmp_path / "assets"
    assets.mkdir()
    (assets / "personal-notes.txt").write_text("unrelated")
    catalog = source / "results-catalog"
    pack(source, assets, catalog)

    [record] = json.loads((assets / "results-experiments.json").read_text())
    for key, directory, suffix in [("previews", "previews", ".png"), ("metadata", "metadata", ".json")]:
        expected = {f"{directory}/1d/pulse/{name}" for name in files if name.endswith(suffix)}
        assert set(record[key]) == expected
        for relative in expected:
            name = Path(relative).relative_to(Path(directory) / "1d" / "pulse").as_posix()
            assert (catalog / relative).read_bytes() == files[name]

    with ZipFile(assets / record["archive"]) as archive:
        for name, data in files.items():
            assert archive.read(f"results/pulse/{name}") == data
    lines = (assets / "SHA256SUMS").read_text().splitlines()
    checksums = {name: checksum for checksum, name in (line.split("  ", 1) for line in lines)}
    assert set(checksums) == {
        "fdtd-results-1d.zip", "fdtd-results-2d.zip",
        "results-archives.json", "results-experiments.json", "results-manifest.json",
    }
    for name, checksum in checksums.items():
        assert hashlib.sha256((assets / name).read_bytes()).hexdigest() == checksum
