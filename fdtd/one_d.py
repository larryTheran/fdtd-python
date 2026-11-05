"""Vectorized Ey/Hx Yee scheme, using E/Z0 and H (thesis chapter 4).

E is at integer cells/times; H is half a cell/step ahead. Both spatial
derivatives have positive signs in this polarization. For a +z wave H=-nE.
The historical 'perfect' boundary is a delay ABC, NOT a PEC conductor.
"""
import numpy as np
from .config import C0, EPS0, Config1D
from .sources import waveform


def prepare(config: Config1D):
    c = config
    if c.cells < 8 or c.steps < 1 or c.wavelength <= 0 or c.points_per_wavelength < 4:
        raise ValueError("Need >=8 cells, positive steps/wavelength and >=4 points/wavelength")
    if not 1 <= c.source_cell < c.cells - 2:
        raise ValueError("Source must lie inside the grid")
    if c.boundary not in {"delay", "mur", "periodic", "zero", "pec"}:
        raise ValueError("Invalid 1D boundary")
    if c.injection not in {"soft", "tfsf"} or c.loss_model not in {"ohmic", "integral"}:
        raise ValueError("Invalid injection or material update")
    er, sigma = np.ones(c.cells), np.zeros(c.cells)
    for layer in c.layers:
        if not 0 <= layer.start < layer.stop <= c.cells or layer.epsilon_r < 1 or layer.sigma < 0:
            raise ValueError("Layer bounds, permittivity or conductivity are invalid")
        er[layer.start:layer.stop] = layer.epsilon_r
        sigma[layer.start:layer.stop] = layer.sigma
    dx = c.dx if c.dx is not None else c.wavelength / (c.points_per_wavelength * np.sqrt(er.max()))
    if not np.isfinite(dx) or dx <= 0 or not 0 < c.courant <= np.sqrt(er.min()):
        raise ValueError("Invalid spacing or unstable Courant number")
    if c.boundary == "delay" and (c.courant != 0.5 or np.any(er[[0, -1]] != 1) or np.any(sigma[[0, -1]])):
        raise ValueError("The two-step delay ABC requires vacuum endpoints and Courant=0.5; use mur")
    if c.injection == "tfsf" and (er[c.source_cell-1] != er[c.source_cell] or sigma[c.source_cell]):
        raise ValueError("TF/SF source must be in a homogeneous lossless material")
    return er, sigma, dx, c.courant * dx / C0


def simulate(config: Config1D, frame_stride=0, reference=False):
    er, sigma, dx, dt = prepare(config)
    c = config
    if reference:
        er = np.full_like(er, er[c.source_cell])
        sigma = np.zeros_like(sigma)
    s = C0 * dt / dx
    e, h, d, current = (np.zeros(c.cells) for _ in range(4))
    q = sigma * dt / (2 * EPS0 * er)
    ca, cb = (1 - q) / (1 + q), s / (er * (1 + q))
    gb = sigma * dt / EPS0
    ga = 1 / (er + gb)
    e_hist, h_hist = [0., 0., 0.], [0., 0., 0.]
    left = min(c.source_cell + 10, c.cells - 4)
    right = c.cells - 5
    if c.spectra and c.layers and min(layer.start for layer in c.layers) <= left:
        raise ValueError("Leave at least 11 cells between the source and first material for the incident monitor")
    probes = np.zeros((c.steps, 2))
    energy = np.zeros(c.steps)
    snapshots, magnetic, frames, frame_steps = [], [], [], []
    snapshot_steps = sorted({v for v in c.snapshots if 0 < v <= c.steps} | {c.steps})
    frequency = C0 / c.wavelength
    nsrc = np.sqrt(er[c.source_cell])
    shift = nsrc * dx / (2 * C0) + dt / 2
    for k in range(c.steps):
        old = e.copy() if c.boundary == "mur" else None
        # H^(n+1/2) from E^n. Right ghost is stored E, periodic E, or zero.
        h[:-1] += s * np.diff(e)
        ghost_e = e[0] if c.boundary == "periodic" else (e_hist[2] if c.boundary == "delay" else 0.)
        if c.boundary in {"mur", "pec"}:
            # These boundaries prescribe E at the last node. There is no Yee H
            # sample to its right; extrapolate the unused plotting ghost instead
            # of integrating a fictitious field against E=0 outside the grid.
            h[-1] = h[-2]
        else:
            h[-1] += s * (ghost_e - e[-1])
        src_e = waveform(k * dt, frequency, c.source, c.tau_periods)
        if c.injection == "tfsf":
            h[c.source_cell-1] -= s * src_e
        h_hist = [h[0], h_hist[0], h_hist[1]]
        ghost_h = h[-1] if c.boundary == "periodic" else (h_hist[2] if c.boundary == "delay" else 0.)
        curl = np.empty_like(e)
        curl[0], curl[1:] = h[0] - ghost_h, np.diff(h)
        src_h = -nsrc * waveform(k * dt + shift, frequency, c.source, c.tau_periods)
        if c.loss_model == "ohmic":
            e = ca * e + cb * curl
            if c.injection == "tfsf":
                e[c.source_cell] -= cb[c.source_cell] * src_h
        else:
            # D = eps_r E + integral(sigma E/eps0 dt), backward rectangular rule.
            d += s * curl
            if c.injection == "tfsf":
                d[c.source_cell] -= s * src_h
            e = ga * (d - current)
            current += gb * e
        if c.injection == "soft":
            e[c.source_cell] += src_e
            if c.loss_model == "integral":
                d[c.source_cell] += src_e / ga[c.source_cell]
        if c.boundary == "mur":
            edge_s = s / np.sqrt(er[[0, -1]])
            r = (edge_s - 1) / (edge_s + 1)
            e[0] = old[1] + r[0] * (e[1] - old[0])
            e[-1] = old[-2] + r[1] * (e[-2] - old[-1])
        elif c.boundary == "pec":
            e[[0, -1]] = 0
        if c.loss_model == "integral" and c.boundary in {"mur", "pec"}:
            d[[0, -1]] = e[[0, -1]] / ga[[0, -1]] + current[[0, -1]] - gb[[0, -1]] * e[[0, -1]]
        e_hist = [e[-1], e_hist[0], e_hist[1]]
        probes[k] = e[[left, right]]
        energy[k] = 0.5 * dx * np.sum(er * e * e + h * h)
        if k + 1 in snapshot_steps and not reference:
            snapshots.append(e.copy())
            magnetic.append(h.copy())
        if frame_stride and (k % frame_stride == 0 or k == c.steps-1) and not reference:
            frames.append(e.astype(np.float32))
            frame_steps.append(k+1)
    if not np.isfinite(e).all() or not np.isfinite(energy).all():
        raise FloatingPointError("Non-finite 1D fields")
    return dict(e=e, h=h, epsilon_r=er, sigma=sigma, dx=dx, dt=dt,
                probes=probes, probe_cells=np.array([left, right]), energy=energy,
                snapshots=np.asarray(snapshots), magnetic_snapshots=np.asarray(magnetic),
                snapshot_steps=np.array(snapshot_steps), frames=np.asarray(frames),
                frame_steps=np.array(frame_steps), time=(np.arange(c.steps)+1)*dt)


def spectrum(config, result, baseline):
    """Reference-subtracted field spectra in homogeneous, lossless exterior media.

    The two monitors have separate reference normalization. A source-power mask
    avoids division by noise; padding interpolates the finite record, not resolution.
    """
    if np.any(result["sigma"][result["probe_cells"]]):
        raise ValueError("Power spectra require lossless monitor regions")
    nfft = 1 << (max(1024, 4 * config.steps) - 1).bit_length()
    f = np.fft.rfftfreq(nfft, result["dt"])
    ref = np.fft.rfft(baseline["probes"], n=nfft, axis=0)
    total = np.fft.rfft(result["probes"], n=nfft, axis=0)
    valid = (np.abs(ref[:, 0]) ** 2 > 1e-4 * np.max(np.abs(ref[:, 0]) ** 2))
    valid &= np.abs(ref[:, 1]) ** 2 > 1e-4 * np.max(np.abs(ref[:, 1]) ** 2)
    valid &= (f > 0) & (f <= C0 / config.wavelength)
    r, t = np.full(len(f), np.nan), np.full(len(f), np.nan)
    r[valid] = np.abs((total[valid, 0] - ref[valid, 0]) / ref[valid, 0]) ** 2
    n1, n2 = np.sqrt(result["epsilon_r"][result["probe_cells"]])
    t[valid] = n2 / n1 * np.abs(total[valid, 1] / ref[valid, 1]) ** 2
    return dict(frequency=f, reflectance=r, transmittance=t, residual=1-r-t, spectral_valid=valid)
