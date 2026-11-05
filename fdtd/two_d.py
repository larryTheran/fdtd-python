"""TMz Yee solver: Ez/Z0, Hx, Hy, with Berenger split-field PML.

Arrays have shape (nx, ny). Display Ez.T so x is horizontal and y vertical.
E lives at (i,j), Hx at (i,j+1/2), Hy at (i+1/2,j). The two E parts
are driven by +dHy/dx and -dHx/dy; their sum is the physical Ez field.
"""
import numpy as np
from .config import C0, EPS0, Config2D
from .sources import waveform


def difference(a, axis, forward, periodic):
    """A staggered difference, with a zero ghost only on nonperiodic sides."""
    if forward:
        out = np.roll(a, -1, axis=axis) - a
        if not periodic:
            if axis == 0:
                out[-1, :] = -a[-1, :]
            else:
                out[:, -1] = -a[:, -1]
    else:
        out = a - np.roll(a, 1, axis=axis)
        if not periodic:
            if axis == 0:
                out[0, :] = a[0, :]
            else:
                out[:, 0] = a[:, 0]
    return out


def profile(size, width, offset):
    if not width:
        return np.zeros(size)
    x = np.arange(size) + offset
    depth = np.maximum(width - x, x - (size - 1 - width)) / width
    return np.clip(depth, 0, 1) ** 3


def geometry(c):
    er = np.full((c.nx, c.ny), c.background_index ** 2)
    sigma = np.zeros_like(er)
    pec = np.zeros_like(er, dtype=bool)
    for layer in c.layers:
        if not 0 <= layer.start < layer.stop <= c.ny or layer.epsilon_r < 1 or layer.sigma < 0:
            raise ValueError("Invalid 2D layer")
        er[:, layer.start:layer.stop] = layer.epsilon_r
        sigma[:, layer.start:layer.stop] = layer.sigma
    if c.geometry in {"slits", "mirror"}:
        if not 2 <= c.wall_y < c.ny-c.wall_thickness-2 or c.wall_thickness < 1:
            raise ValueError("Wall must be inside the domain")
        pec[:, c.wall_y:c.wall_y+c.wall_thickness] = True
        if c.geometry == "slits":
            if c.slit_count not in {1, 2} or c.slit_width < 1 or c.slit_gap < 1:
                raise ValueError("Need one or two slits with positive integer dimensions")
            total = c.slit_count * c.slit_width + (c.slit_count-1) * c.slit_gap
            if total >= c.nx - 2*c.pml_cells:
                raise ValueError("Slits do not fit in the interior")
            start = (c.nx-total)//2
            for slit in range(c.slit_count):
                a = start + slit*(c.slit_width+c.slit_gap)
                pec[a:a+c.slit_width, c.wall_y:c.wall_y+c.wall_thickness] = False
    elif c.geometry not in {"free", "layers", "bend"}:
        raise ValueError("Unknown geometry")
    dx = c.dx if c.dx is not None else c.wavelength / (c.points_per_wavelength * np.sqrt(er.max()))
    dy = c.dy if c.dy is not None else dx
    mode = None
    if c.geometry == "bend":
        # Supplemental reconstruction of Untitled8: effective-index 2D bend.
        from scipy.linalg import eigh_tridiagonal
        vertical_dz = c.wavelength / (c.points_per_wavelength*c.bend_core_index)
        z = np.arange(-3*c.bend_width, 4*c.bend_width, vertical_dz)
        vertical_er = np.where(z < 0, 1., 1.52**2)
        vertical_er[(z >= 0) & (z < c.bend_width)] = c.bend_core_index**2
        k0 = 2*np.pi/c.wavelength
        eig = eigh_tridiagonal(-2/vertical_dz**2+k0*k0*vertical_er,
                              np.full(len(z)-1, 1/vertical_dz**2),
                              select="i", select_range=(len(z)-1, len(z)-1), eigvals_only=True)
        ncore = np.sqrt(eig[-1])/k0
        nclad = 0.3*1.0 + 0.7*1.52
        x, y = np.arange(c.nx)[:, None]*dx, np.arange(c.ny)[None, :]*dy
        xc = c.source_x*dx + c.bend_radius
        yc = (c.pml_cells+40)*dy
        r = np.sqrt((x-xc)**2+(y-yc)**2)
        mask = (np.abs(r-c.bend_radius) <= c.bend_width/2) & (x <= xc) & (y >= yc)
        mask |= (np.abs(x-c.source_x*dx) <= c.bend_width/2) & (y < yc)
        mask |= (np.abs(y-yc-c.bend_radius) <= c.bend_width/2) & (x > xc)
        if xc+c.bend_width > (c.nx-c.pml_cells)*dx or yc+c.bend_radius+c.bend_width > (c.ny-c.pml_cells)*dy:
            raise ValueError("Bend does not fit: enlarge nx/ny or reduce bend_radius")
        er[:] = np.where(mask, ncore**2, nclad**2)
        vals, vecs = eigh_tridiagonal(-2/dx**2 + k0*k0*er[:, c.source_y],
                                    np.full(c.nx-1, 1/dx**2), select="i",
                                    select_range=(c.nx-1, c.nx-1))
        mode = vecs[:, -1] / np.max(np.abs(vecs[:, -1]))
    return er, sigma, pec, dx, dy, mode


def prepare(c: Config2D):
    if min(c.nx, c.ny) < 8 or c.steps < 1 or c.wavelength <= 0 or c.background_index < 1:
        raise ValueError("Invalid grid, steps, wavelength or background index")
    if c.points_per_wavelength < 4 or c.tau_periods <= 0:
        raise ValueError("Invalid source resolution or duration")
    if any(b not in {"pml", "periodic", "pec", "mur"} for b in [c.boundary_x, c.boundary_y]):
        raise ValueError("Invalid 2D boundary")
    if "pml" in {c.boundary_x, c.boundary_y}:
        if not 3 <= c.pml_cells < min(c.nx, c.ny)//2-3 or not 0 < c.pml_reflection < 1:
            raise ValueError("PML must leave a nonempty interior and have 0<R<1")
    if not 1 <= c.source_x < c.nx-1 or not 1 <= c.source_y < c.ny-1:
        raise ValueError("Source is outside the interior")
    if c.injection not in {"point", "line", "tfsf", "beam", "diagonal", "mode"}:
        raise ValueError("Unknown source injection")
    if c.source_width <= 0 or abs(c.angle_deg) >= 90:
        raise ValueError("Source width must be positive and incidence angle within (-90,90)")
    if c.detector_y is not None and not 1 <= c.detector_y < c.ny-1:
        raise ValueError("Detector is outside the domain")
    er, sigma, pec, dx, dy, mode = geometry(c)
    if min(dx, dy) <= 0 or not np.isfinite([dx, dy]).all():
        raise ValueError("Spatial steps must be finite and positive")
    dt = c.courant * min(dx, dy) / C0
    stability = C0*dt*np.sqrt(1/dx**2+1/dy**2)/np.sqrt(er.min())
    if dt <= 0 or stability > 1:
        raise ValueError(f"Unstable 2D Courant factor: {stability:g} > 1")
    if c.boundary_y == "pml" and not c.pml_cells+1 <= c.source_y < c.ny-c.pml_cells-1:
        raise ValueError("Source must be outside the y PML")
    if c.injection == "tfsf" and (c.boundary_x != "periodic" or np.ptp(er[:, c.source_y]) or np.any(sigma[:, c.source_y])):
        raise ValueError("This plane TF/SF injection needs periodic x and a uniform lossless source plane")
    if c.spectra:
        if c.injection != "tfsf" or c.geometry not in {"free", "layers"}:
            raise ValueError("2D spectra require normal TF/SF incidence on an x-uniform geometry")
        if c.layers and min(layer.start for layer in c.layers) <= c.source_y+10:
            raise ValueError("Leave 11 cells between source and slab for the incident monitor")
    if np.any(pec[c.source_x, c.source_y]):
        raise ValueError("Source overlaps the PEC wall")
    return er, sigma, pec, dx, dy, dt, mode


def simulate(config: Config2D, frame_stride=0, reference=False):
    c = config
    er, sigma, pec, dx, dy, dt, mode = prepare(c)
    if reference:
        er = np.full_like(er, er[c.source_x, c.source_y])
        sigma = np.zeros_like(sigma)
    px, py = c.boundary_x == "periodic", c.boundary_y == "periodic"
    wx = c.pml_cells if c.boundary_x == "pml" else 0
    wy = c.pml_cells if c.boundary_y == "pml" else 0
    # Matched electric/magnetic damping rates evaluated on their own Yee sites.
    speed = C0 / np.sqrt(er)
    speed_hx = C0 / np.sqrt((er + np.roll(er, -1, axis=1))/2)
    speed_hy = C0 / np.sqrt((er + np.roll(er, -1, axis=0))/2)
    strength = -4*np.log(c.pml_reflection)/2
    rx = strength*speed*profile(c.nx, wx, 0)[:, None]/(max(wx, 1)*dx)
    ry = strength*speed*profile(c.ny, wy, 0)[None, :]/(max(wy, 1)*dy)
    rhx = strength*speed_hx*profile(c.ny, wy, .5)[None, :]/(max(wy, 1)*dy)
    rhy = strength*speed_hy*profile(c.nx, wx, .5)[:, None]/(max(wx, 1)*dx)
    def coeff(rate, scale):
        q = .5*dt*rate
        return (1-q)/(1+q), scale/(1+q)
    ax, bx = coeff(rx+sigma/(EPS0*er), C0*dt/(er*dx))
    ay, by = coeff(ry+sigma/(EPS0*er), C0*dt/(er*dy))
    ahx, bhx = coeff(rhx, C0*dt/dy)
    ahy, bhy = coeff(rhy, C0*dt/dx)
    e, ex, ey, hx, hy = (np.zeros_like(er) for _ in range(5))
    energy = np.zeros(c.steps)
    snapshots, frames, frame_steps = [], [], []
    snapshot_steps = sorted({n for n in c.snapshots if 0 < n <= c.steps} | {c.steps})
    detector = np.zeros((c.steps, c.nx)) if c.detector_y is not None else None
    probe_cells = np.array([c.source_y+10, c.ny-(c.pml_cells if c.boundary_y == "pml" else 0)-5])
    probes = np.zeros((c.steps, 2)) if c.spectra else None
    if c.spectra and (probe_cells[1] <= probe_cells[0] or np.any(sigma[:, probe_cells])):
        raise ValueError("Spectral monitors must be ordered and inside lossless exterior regions")
    avg_steps = min(c.steps, max(1, round(c.average_cycles*c.wavelength/C0/dt)))
    phasor = np.zeros_like(e, dtype=complex)
    mean_square = np.zeros_like(e)
    f = C0/c.wavelength
    nsrc = np.sqrt(er[c.source_x, c.source_y])
    theta = np.deg2rad(c.angle_deg)
    xp = np.arange(c.nx) - c.source_x
    delay = nsrc*np.sin(theta)*xp*dx/C0
    beam = np.exp(-(xp/c.source_width)**2)
    # A line source spans the whole transverse periodic domain when width>=nx.
    line = (np.abs(xp) <= c.source_width/2).astype(float)
    if c.source_width >= c.nx:
        line[:] = 1
    if wx:
        taper = np.sin(.5*np.pi*np.clip(np.minimum(np.arange(c.nx)-wx,
                                   c.nx-1-wx-np.arange(c.nx))/8, 0, 1))**2
        beam *= taper
        line *= taper
    for k in range(c.steps):
        old = e.copy() if "mur" in {c.boundary_x, c.boundary_y} else None
        hx = ahx*hx - bhx*difference(e, 1, True, py)
        hy = ahy*hy + bhy*difference(e, 0, True, px)
        if c.injection == "tfsf":
            hx[:, c.source_y-1] += bhx[:, c.source_y-1]*waveform(k*dt, f, c.source, c.tau_periods)
        ex = ax*ex + bx*difference(hy, 0, False, px)
        ey = ay*ey - by*difference(hx, 1, False, py)
        if c.injection == "tfsf":
            shift = nsrc*dy/(2*C0)+dt/2
            ey[:, c.source_y] += by[:, c.source_y]*nsrc*waveform(k*dt+shift, f, c.source, c.tau_periods)
        elif c.injection == "point":
            value = waveform(k*dt, f, c.source, c.tau_periods)
            ex[c.source_x, c.source_y] += .5*value
            ey[c.source_x, c.source_y] += .5*value
        elif c.injection == "diagonal":
            offsets = np.arange(round(c.source_width))
            ix, iy = c.source_x+offsets, c.source_y-offsets
            if ix[-1] >= c.nx-wx-1 or iy[-1] < wy+1:
                raise ValueError("Diagonal source does not fit outside the PML")
            value = waveform(k*dt, f, c.source, c.tau_periods)
            ex[ix, iy] += .5*value
            ey[ix, iy] += .5*value
        else:
            amp = beam if c.injection == "beam" else (mode if c.injection == "mode" else line)
            if amp is None:
                raise ValueError("Mode injection requires bend geometry")
            value = amp*waveform(k*dt-delay, f, c.source, c.tau_periods)
            ex[:, c.source_y] += .5*value
            ey[:, c.source_y] += .5*value
        ex[pec], ey[pec] = 0., 0.
        if c.boundary_x in {"pml", "pec"}:
            ex[[0, -1], :], ey[[0, -1], :] = 0., 0.
        if c.boundary_y in {"pml", "pec"}:
            ex[:, [0, -1]], ey[:, [0, -1]] = 0., 0.
        e = ex + ey
        if old is not None:
            # First-order Mur; deliberately distinct from the second-order draft.
            if c.boundary_x == "mur":
                r = (speed[[0, -1], :]*dt/dx-1)/(speed[[0, -1], :]*dt/dx+1)
                e[0] = old[1]+r[0]*(e[1]-old[0])
                e[-1] = old[-2]+r[1]*(e[-2]-old[-1])
                ex[[0, -1], :], ey[[0, -1], :] = e[[0, -1], :]/2, e[[0, -1], :]/2
            if c.boundary_y == "mur":
                r = (speed[:, [0, -1]]*dt/dy-1)/(speed[:, [0, -1]]*dt/dy+1)
                e[:, 0] = old[:, 1]+r[:, 0]*(e[:, 1]-old[:, 0])
                e[:, -1] = old[:, -2]+r[:, 1]*(e[:, -2]-old[:, -1])
                ex[:, [0, -1]], ey[:, [0, -1]] = e[:, [0, -1]]/2, e[:, [0, -1]]/2
        energy[k] = .5*dx*dy*np.sum(er*e*e+hx*hx+hy*hy)
        if detector is not None:
            detector[k] = e[:, c.detector_y]
        if probes is not None:
            probes[k] = np.mean(e[:, probe_cells], axis=0)
        if k >= c.steps-avg_steps:
            phasor += e*np.exp(-2j*np.pi*f*(k+1)*dt)*2/avg_steps
            mean_square += e*e/avg_steps
        if k+1 in snapshot_steps:
            snapshots.append(e.copy())
        if frame_stride and (k % frame_stride == 0 or k == c.steps-1):
            frames.append(e.astype(np.float32))
            frame_steps.append(k+1)
    if not np.isfinite(e).all() or not np.isfinite(energy).all():
        raise FloatingPointError("Non-finite 2D fields")
    result = dict(e=e, hx=hx, hy=hy, epsilon_r=er, sigma=sigma, pec=pec,
                  dx=dx, dy=dy, dt=dt, energy=energy,
                  snapshots=np.asarray(snapshots), snapshot_steps=np.array(snapshot_steps),
                  frames=np.asarray(frames), frame_steps=np.array(frame_steps),
                  phasor=phasor, mean_square=mean_square,
                  average_steps=avg_steps, time=(np.arange(c.steps)+1)*dt)
    if detector is not None:
        result.update(detector=detector, detector_mean_square=np.mean(detector[-avg_steps:]**2, axis=0))
    if probes is not None:
        result.update(probes=probes, probe_cells=probe_cells)
    return result


def spectrum(config, result, baseline):
    """Zeroth spatial-order spectrum for an x-uniform, normally incident plane wave.

    This is the active homogeneous case in Untitled7. It is not a general
    diffraction-order decomposition for patterned or oblique structures.
    """
    from .one_d import spectrum as plane_spectrum
    line_result = dict(result, epsilon_r=result["epsilon_r"][0], sigma=result["sigma"][0])
    return plane_spectrum(config, line_result, baseline)
