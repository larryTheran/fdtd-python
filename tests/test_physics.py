"""Physical and numerical checks, independent of the appearance of the plots."""
from dataclasses import replace
import numpy as np
import pytest
from fdtd import Config1D, Config2D, Layer
from fdtd.config import C0
from fdtd.one_d import prepare, simulate, spectrum
from fdtd.two_d import prepare as prepare2, simulate as simulate2
from fdtd.analysis import fresnel, diffraction, diagnostics


def base1(**kwargs):
    return replace(Config1D("test", "test", "", cells=400, steps=1800,
                            source_cell=40, points_per_wavelength=30), **kwargs)


def base2(**kwargs):
    return replace(Config2D("test", "test", "", nx=101, ny=101, steps=500,
                            source_x=50, source_y=50, pml_cells=16), **kwargs)


def test_vacuum_speed_and_one_way_source():
    r = simulate(base1(snapshots=(250, 350), steps=400))
    a, b = r["snapshots"][:2]
    assert abs((np.argmax(b)-np.argmax(a))/100 - .5) < .015
    assert np.max(np.abs(a[:35])) < .002*np.max(np.abs(a))


@pytest.mark.parametrize("boundary", ["delay", "mur"])
def test_absorbing_boundary_removes_outgoing_pulse(boundary):
    c = base1(boundary=boundary)
    absorbed = simulate(c)
    reflected = simulate(replace(c, boundary="pec"))
    assert absorbed["energy"][-1]/absorbed["energy"].max() < 1e-6
    assert reflected["energy"][-1]/reflected["energy"].max() > .8


def test_periodic_pulse_survives_multiple_crossings():
    r = simulate(base1(boundary="periodic"))
    settled = r["energy"][500:]
    assert np.ptp(settled)/np.mean(settled) < .001


def test_fresnel_reflection_amplitude_and_phase():
    c = base1(cells=800, steps=1800, source_cell=60, points_per_wavelength=40,
              boundary="mur", layers=[Layer(300, 800, 4)])
    r, b = simulate(c), simulate(c, reference=True)
    reflected = r["probes"][:, 0]-b["probes"][:, 0]
    coefficient = np.min(reflected)/np.max(b["probes"][:, 0])
    assert abs(coefficient - (1-2)/(1+2)) < .01


def test_lossless_slab_spectrum_and_energy_balance():
    c = base1(layers=[Layer(150, 250, 4)], steps=4500, spectra=True)
    r, b = simulate(c), simulate(c, reference=True)
    sp = spectrum(c, r, b)
    valid = sp["spectral_valid"]
    assert np.max(abs(sp["residual"][valid])) < .005
    # Independent analytic Fabry-Perot reflection, slab thickness 100*dx.
    phase = 2*np.pi*sp["frequency"]*2*(100*r["dx"])/C0
    rr = ((1-2)/(1+2))**2
    analytic = 4*rr*np.sin(phase)**2/((1-rr)**2+4*rr*np.sin(phase)**2)
    valid &= sp["frequency"] < .6*C0/c.wavelength
    assert np.max(abs(sp["reflectance"][valid]-analytic[valid])) < .025


def test_conductivity_attenuates_and_integral_model_agrees():
    c = base1(cells=500, steps=4500, source_cell=30, dx=.001, wavelength=.1,
              layers=[Layer(150, 300, 2, .05)])
    r, b = simulate(c), simulate(replace(c, layers=[Layer(150, 300, 2)]))
    integral = simulate(replace(c, loss_model="integral"))
    assert np.sum(r["probes"][:, 1]**2) < .5*np.sum(b["probes"][:, 1]**2)
    assert np.linalg.norm(integral["probes"]-r["probes"])/np.linalg.norm(r["probes"]) < .004


def test_optical_and_microwave_loss_are_not_confused():
    c = base1(cells=400, steps=4000, source_cell=30, layers=[Layer(150, 300, 4, .04)])
    optical = simulate(c)
    microwave = simulate(replace(c, wavelength=.2, dx=.01))
    # Conductivity is dimensional: a scaled wavelength alone does not preserve loss.
    assert np.max(abs(microwave["probes"][:, 1])) < .05*np.max(abs(optical["probes"][:, 1]))


def test_2d_symmetry_and_pml_absorption():
    c = base2(snapshots=(80,))
    r = simulate2(c)
    assert np.max(abs(r["snapshots"][0]-r["snapshots"][0].T)) < 1e-12
    assert r["energy"][-1]/r["energy"].max() < 1e-7
    pec = simulate2(replace(c, boundary_x="pec", boundary_y="pec"))
    assert pec["energy"][-1]/pec["energy"].max() > .7


def test_rectangular_grid_and_swapped_boundary_axes():
    c = base2(nx=90, ny=110, source_x=45, source_y=55, dx=40e-9, dy=55e-9,
              boundary_x="periodic", boundary_y="pml", steps=220)
    a = simulate2(c)["e"]
    b = simulate2(replace(c, nx=110, ny=90, source_x=55, source_y=45,
                          dx=55e-9, dy=40e-9, boundary_x="pml", boundary_y="periodic"))["e"]
    assert np.max(abs(a-b.T)) < 1e-12


def test_periodic_2d_translation_invariance():
    c = base2(boundary_x="periodic", boundary_y="periodic", steps=200)
    a, b = simulate2(c), simulate2(replace(c, source_x=55, source_y=57))
    assert np.max(abs(np.roll(a["e"], (5, 7), axis=(0, 1))-b["e"])) < 1e-12


def test_2d_tfsf_is_uniform_and_one_way():
    r = simulate2(base2(nx=65, ny=180, source_x=32, source_y=40,
                       boundary_x="periodic", injection="tfsf", source="gaussian",
                       steps=220, snapshots=(160,)))
    e = r["snapshots"][0]
    assert np.max(np.std(e, axis=0)) < 1e-12
    assert np.max(abs(e[:, :35])) < .005*np.max(abs(e))


def test_2d_plane_wave_slab_spectral_conservation():
    from fdtd.two_d import spectrum as spectrum2
    c = base2(nx=65, ny=280, source_x=32, source_y=40, pml_cells=20,
              boundary_x="periodic", injection="tfsf", source="gaussian",
              geometry="layers", layers=[Layer(120, 160, 4)],
              spectra=True, steps=2200, points_per_wavelength=20)
    r, b = simulate2(c), simulate2(c, reference=True)
    s = spectrum2(c, r, b)
    valid = s["spectral_valid"]
    assert np.max(abs(s["residual"][valid])) < .01
    assert np.max(s["reflectance"][valid]) > .3


def test_aperture_geometry_and_actual_fresnel_regime():
    c = base2(nx=200, ny=200, geometry="slits", slit_count=2, slit_width=10,
              slit_gap=10, wall_y=80, detector_y=96, source_x=100, source_y=40,
              steps=2, source="sine")
    r = simulate2(c)
    assert np.count_nonzero(~r["pec"][:, 80]) == 20
    d = diagnostics(c, r)
    assert d["fresnel_number_full_aperture"] == pytest.approx(6)
    assert d["fresnel_number_each_slit"] == pytest.approx(2/3)


def test_far_field_diffraction_envelope():
    c = base2(nx=260, ny=400, pml_cells=24, geometry="slits", slit_width=10,
              wall_y=70, detector_y=320, source_x=130, source_y=35,
              injection="line", source_width=260, source="sine", steps=1500)
    r = simulate2(c)
    i = r["detector_mean_square"]/r["detector_mean_square"].max()
    x = (np.arange(c.nx)-(c.nx-1)/2)*r["dx"]
    theory = diffraction(x, c.slit_width*r["dx"], c.wavelength, 249*r["dy"])
    interior = slice(50, -50)
    assert np.max(abs(i[interior]-theory[interior])) < .12
    assert np.max(abs(i-i[::-1])) < .02


def test_refraction_angle_from_field_phase_matches_snell():
    c = base2(nx=250, ny=300, source_x=60, source_y=40, source_width=24,
              dx=532e-9/25, wavelength=532e-9, background_index=1.5,
              geometry="layers", layers=[Layer(150, 300, 2.1**2)],
              injection="beam", source="sine", angle_deg=40, steps=1800, pml_cells=30)
    report = diagnostics(c, simulate2(c))
    ray = report["refraction"][0]
    assert abs(ray["measured_phase_angle_deg"]-ray["snell_angle_deg"]) < 3
    r, t, angle = fresnel(1.5, 4, 40)
    assert 0 < r < 1 and t > 0 and angle < 40
    assert fresnel(1.5, 1, 50)[:2] == (1., 0.)


@pytest.mark.parametrize("change", [{"courant": 1.1}, {"dx": -1}, {"source_cell": 0},
                                  {"layers": [Layer(300, 200, 2)]},
                                  {"layers": [Layer(150, 250, 2, -1)]}])
def test_invalid_1d_inputs_are_rejected(change):
    with pytest.raises(ValueError):
        prepare(base1(**change))


@pytest.mark.parametrize("change", [{"courant": .8}, {"pml_cells": 50},
                                  {"source_y": 5}, {"detector_y": 150}, {"dx": -1}])
def test_invalid_2d_inputs_are_rejected(change):
    with pytest.raises(ValueError):
        prepare2(base2(**change))
