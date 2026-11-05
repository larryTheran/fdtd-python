"""Analytical comparisons and measured phase-gradient diagnostics."""
import numpy as np


def fresnel(n1, n2, angle_deg=0):
    """s-polarized electric-field power R,T at a nonmagnetic interface."""
    theta = np.deg2rad(angle_deg)
    q = n1*np.sin(theta)/n2
    if abs(q) >= 1:
        return 1., 0., None
    transmitted = np.arcsin(q)
    a, b = n1*np.cos(theta), n2*np.cos(transmitted)
    r = (a-b)/(a+b)
    return float(r*r), float(4*a*b/(a+b)**2), float(np.rad2deg(transmitted))


def diffraction(x, width, wavelength, distance, count=1, separation=0):
    """Fraunhofer aperture approximation, including the sinc denominator."""
    theta = np.arctan2(x, distance)
    pattern = np.sinc(width*np.sin(theta)/wavelength)**2
    if count == 2:
        pattern *= np.cos(np.pi*separation*np.sin(theta)/wavelength)**2
    return pattern


def phase_angle(phasor, dx, dy):
    """Estimate local wavevector direction; standing waves invalidate this diagnostic.

    Neighbor phasor products avoid unwrap branch cuts. Low-amplitude points
    are excluded; weights suppress noise near beam edges.
    """
    amplitude = np.abs(phasor)
    if not amplitude.size or amplitude.max() < 1e-12:
        return None
    def component(axis, delta):
        a = np.take(phasor, range(phasor.shape[axis]-1), axis=axis)
        b = np.take(phasor, range(1, phasor.shape[axis]), axis=axis)
        weight = np.abs(a*b)
        good = weight > .1*weight.max()
        if not np.any(good):
            return 0.
        return np.sum(np.angle(b[good]*np.conj(a[good]))*weight[good])/np.sum(weight[good])/delta
    kx, ky = component(0, dx), component(1, dy)
    # DFT uses exp(-i wt); +y propagation has a negative spatial phase gradient.
    return float(np.rad2deg(np.arctan2(-kx, -ky)))


def diagnostics(c, r):
    data = dict(final_peak_field=float(np.max(np.abs(r["e"]))),
                final_energy_proxy=float(r["energy"][-1]),
                peak_energy_proxy=float(r["energy"].max()),
                remaining_energy_fraction=float(r["energy"][-1]/max(r["energy"].max(), 1e-300)),
                dt_seconds=float(r["dt"]), dx_meters=float(r["dx"]), steps=c.steps)
    if "spectral_valid" in r:
        ok = r["spectral_valid"]
        data["valid_frequency_bins"] = int(ok.sum())
        if ok.any():
            data.update(max_abs_spectral_residual=float(np.max(np.abs(r["residual"][ok]))),
                        median_reflectance=float(np.median(r["reflectance"][ok])),
                        median_transmittance=float(np.median(r["transmittance"][ok])))
    if hasattr(c, "nx"):
        data["dy_meters"] = r["dy"]
        data["average_steps"] = int(r["average_steps"])
        if c.geometry == "slits" and c.detector_y is not None:
            distance = (c.detector_y-(c.wall_y+c.wall_thickness-1))*r["dy"]
            width = c.slit_width*r["dx"]
            wavelength = c.wavelength/c.background_index
            total = (c.slit_count*c.slit_width+(c.slit_count-1)*c.slit_gap)*r["dx"]
            data.update(detector_distance_m=distance, slit_width_m=width,
                        fresnel_number_each_slit=width**2/(wavelength*distance),
                        fresnel_number_full_aperture=total**2/(wavelength*distance))
        if c.geometry == "layers" and c.layers and c.injection == "beam":
            n1 = np.sqrt(r["epsilon_r"][c.source_x, c.source_y])
            interfaces = sorted(set(l.start for l in c.layers if l.start > c.source_y))
            prediction = []
            for y in interfaces:
                n2 = np.sqrt(r["epsilon_r"][c.source_x, y])
                _, _, angle = fresnel(n1, n2, c.angle_deg)
                stop = min(y+35, c.ny-c.pml_cells-2)
                xcenter = int(c.source_x+(y-c.source_y)*np.tan(np.deg2rad(c.angle_deg)))
                xcenter = np.clip(xcenter, c.pml_cells+15, c.nx-c.pml_cells-15)
                patch = r["phasor"][max(c.pml_cells+2, xcenter-35):min(c.nx-c.pml_cells-2, xcenter+35), y+8:stop]
                measured = phase_angle(patch, r["dx"], r["dy"])
                prediction.append(dict(interface_y=y, index=n2, snell_angle_deg=angle,
                                       measured_phase_angle_deg=measured,
                                       note="Local diagnostic; finite beams and standing waves affect phase gradients"))
            data["refraction"] = prediction
    return data
