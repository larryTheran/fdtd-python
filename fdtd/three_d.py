"""Full-vector Yee FDTD, E/Z0 and H, with convolutional PML.

E_x=(i+.5,j,k), E_y=(i,j+.5,k), E_z=(i,j,k+.5).
H_x=(i,j+.5,k+.5), H_y=(i+.5,j,k+.5), H_z=(i+.5,j+.5,k).
Fields are not collocated. Material inputs are sampled at integer nodes;
edge permittivities/conductivities use adjacent-node arithmetic averages.
"""
from dataclasses import dataclass, replace
import math
import operator
import time
import numpy as np
from .config import Config2D, C0, EPS0
from .sources import waveform
from .two_d import profile


@dataclass
class Config3D(Config2D):
    nz: int = 64
    dz: float | None = None
    boundary_z: str = 'pml'
    pml_cells_z: int = 12
    source_z: int | None = None
    source_width_z: float = 16.0
    slit_height: int = 24
    bend_height: float = 0.775e-6
    substrate_index: float = 1.52
    cladding_index: float = 1.0
    backend: str = 'auto'  # auto: optional local C accelerator, otherwise numpy
    workers: int = 3  # independent components per Yee phase; NumPy uses one
    energy_stride: int = 10
    origin_2d: str = ''


@dataclass(frozen=True)
class PreviewFrame3D:
    """A bounded observational snapshot, never a view into solver-owned fields.

    Section order is XY at source_z, XZ at detector_y, YZ at source_x.
    Material planes are shared, read-only copies for this preview session.
    Energy is the most recent saved diagnostic, sampled at energy_step.
    """
    step: int
    steps: int
    time_s: float
    spacing: tuple
    fields: tuple
    epsilon_r: tuple
    pec: tuple
    energy: float
    energy_step: int


def _preview_options(callback, stride, interval):
    if callback is not None and not callable(callback):
        raise ValueError('on_frame must be callable or None')
    if isinstance(stride,bool):
        raise ValueError('Preview stride must be an integer >=1 and interval finite >=0')
    try:
        stride = operator.index(stride)
        interval = float(interval)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError('Preview stride must be an integer >=1 and interval finite >=0') from error
    if isinstance(stride, bool) or stride < 1 or not math.isfinite(interval) or interval < 0:
        raise ValueError('Preview stride must be an integer >=1 and interval finite >=0')
    return stride, interval


def prepare(c):
    shape = (c.nx, c.ny, c.nz)
    bounds = (c.boundary_x, c.boundary_y, c.boundary_z)
    widths = tuple(w if b == 'pml' else 0 for b, w in zip(bounds, (c.pml_cells, c.pml_cells, c.pml_cells_z)))
    if min(shape) < 4 or c.steps < 1 or c.energy_stride < 1:
        raise ValueError('Grid dimensions >=4, steps and energy_stride >=1 required')
    if any(b not in {'pml', 'pec', 'periodic', 'mur'} for b in bounds):
        raise ValueError('Unknown boundary')
    if any(b == 'pml' and not 3 <= w < n/2-2 for n, b, w in zip(shape, bounds, widths)):
        raise ValueError('PML must leave at least five interior cells on each axis')
    if not 0 < c.pml_reflection < 1:
        raise ValueError('PML reflection design target must be between zero and one')
    if not np.isfinite([c.wavelength, c.background_index, c.points_per_wavelength, c.tau_periods]).all() or c.wavelength <= 0 or c.background_index < 1 or c.points_per_wavelength < 4 or c.tau_periods <= 0:
        raise ValueError('Invalid wavelength, index, resolution or pulse duration')
    er = np.full(shape, c.background_index**2, dtype=np.float32)
    sigma = np.zeros(shape, dtype=np.float32)
    pec = np.zeros(shape, dtype=bool)
    for layer in c.layers:
        if not 0 <= layer.start < layer.stop <= c.ny or not np.isfinite([layer.epsilon_r, layer.sigma]).all() or layer.epsilon_r < 1 or layer.sigma < 0:
            raise ValueError('Invalid dielectric layer')
        er[:, layer.start:layer.stop, :] = layer.epsilon_r
        sigma[:, layer.start:layer.stop, :] = layer.sigma
    dx = c.dx if c.dx is not None else c.wavelength/(c.points_per_wavelength*np.sqrt(float(er.max())))
    spacing = tuple(float(d) for d in (dx, c.dy if c.dy is not None else dx, c.dz if c.dz is not None else dx))
    if not np.isfinite(spacing).all() or min(spacing) <= 0:
        raise ValueError('Grid spacings must be finite and positive')
    sz = c.nz//2 if c.source_z is None else c.source_z
    source = (c.source_x, c.source_y, sz)
    if any(not max(1,w+1) <= s < n-max(1,w+1) for s,n,w in zip(source, shape, widths)):
        raise ValueError('Source center must be inside the grid and outside PML')
    if c.injection not in {'point','line','tfsf','beam','diagonal','mode'} or c.source not in {'sine','gaussian','modulated'}:
        raise ValueError('Invalid source')
    if not np.isfinite([c.source_width,c.source_width_z,c.angle_deg]).all() or min(c.source_width,c.source_width_z) <= 0 or abs(c.angle_deg) >= 90:
        raise ValueError('Invalid source width or angle')
    if c.geometry in {'slits','mirror'}:
        if c.wall_thickness < 1 or not widths[1]+2 <= c.wall_y < c.ny-widths[1]-c.wall_thickness-2:
            raise ValueError('Wall must lie outside the longitudinal PML')
        pec[:, c.wall_y:c.wall_y+c.wall_thickness, :] = True
        if c.geometry == 'slits':
            if c.slit_count not in (1,2) or min(c.slit_width,c.slit_gap,c.slit_height) < 1:
                raise ValueError('Invalid aperture dimensions')
            total = c.slit_count*c.slit_width+(c.slit_count-1)*c.slit_gap
            if total >= c.nx-2*widths[0]-2 or c.slit_height >= c.nz-2*widths[2]-2:
                raise ValueError('Apertures must fit outside PML')
            left, bottom = (c.nx-total)//2, (c.nz-c.slit_height)//2
            for slit in range(c.slit_count):
                x = left+slit*(c.slit_width+c.slit_gap)
                pec[x:x+c.slit_width,c.wall_y:c.wall_y+c.wall_thickness,bottom:bottom+c.slit_height] = False
    elif c.geometry == 'bend':
        if min(c.bend_width,c.bend_height,c.bend_radius) <= 0 or min(c.substrate_index,c.cladding_index) < 1 or c.bend_core_index <= max(c.substrate_index,c.cladding_index):
            raise ValueError('Invalid guiding core or cladding parameters')
        x = np.arange(c.nx)[:,None]*spacing[0]
        y = np.arange(c.ny)[None,:]*spacing[1]
        xc, yc = c.source_x*spacing[0]+c.bend_radius, (c.pml_cells+40)*spacing[1]
        if xc+c.bend_width >= (c.nx-widths[0])*spacing[0] or yc+c.bend_radius+c.bend_width >= (c.ny-widths[1])*spacing[1]:
            raise ValueError('Bend does not fit in the x-y interior')
        mask = (abs(np.hypot(x-xc,y-yc)-c.bend_radius) <= c.bend_width/2) & (x <= xc) & (y >= yc)
        mask |= (abs(x-c.source_x*spacing[0]) <= c.bend_width/2) & (y < yc)
        mask |= (abs(y-yc-c.bend_radius) <= c.bend_width/2) & (x > xc)
        z = (np.arange(c.nz)-sz)*spacing[2]
        if c.bend_height/2 >= min(sz-widths[2]-2,c.nz-sz-widths[2]-2)*spacing[2]:
            raise ValueError('Core height does not fit outside z PML')
        er[:] = np.where(z < -c.bend_height/2,c.substrate_index**2,c.cladding_index**2)
        er[mask[:,:,None] & (abs(z)[None,None,:] <= c.bend_height/2)] = c.bend_core_index**2
    elif c.geometry not in {'free','layers'}:
        raise ValueError('Unknown geometry')
    if pec[source]:
        raise ValueError('Source overlaps PEC')
    if c.detector_y is not None and not widths[1]+1 <= c.detector_y < c.ny-widths[1]-1:
        raise ValueError('Detector must be inside the non-PML interior')
    dt = c.courant*min(spacing)/C0
    stability = C0*dt*np.sqrt(sum(1/d**2 for d in spacing))/np.sqrt(float(er.min()))
    if not np.isfinite(dt) or dt <= 0 or stability > 1:
        raise ValueError(f'Unstable 3D CFL ratio {stability:g}; must be <=1')
    if c.injection == 'tfsf':
        if bounds[0] != 'periodic' or bounds[2] != 'periodic' or c.angle_deg != 0 or np.ptp(er[:,c.source_y,:]) or np.any(sigma[:,c.source_y,:]):
            raise ValueError('Normal TF/SF requires periodic x/z and a uniform lossless source plane')
    if c.injection == 'mode' and c.geometry != 'bend':
        raise ValueError('Mode source requires a waveguide bend')
    if c.injection == 'diagonal':
        n = round(c.source_width)
        if n < 1 or c.source_x+n >= c.nx-widths[0]-1 or c.source_y-n < widths[1]+1:
            raise ValueError('Diagonal dipole array does not fit')
    if c.spectra and (c.injection != 'tfsf' or c.geometry not in {'free','layers'}):
        raise ValueError('Spectra require normal TF/SF and a uniform layered geometry')
    return er,sigma,pec,spacing,dt,source,widths


def _edge_average(a, axis, periodic):
    b = np.roll(a,-1,axis=axis)
    if not periodic:
        edge = [slice(None)]*3
        edge[axis] = -1
        b[tuple(edge)] = a[tuple(edge)]
    return (a+b)*np.float32(.5)


def _numpy_update(out, fa, fb, pa, pb, ca, cb, aa, bb, forward, axes, periodic, scales):
    """Reference implementation of one signed curl component and CPML memory."""
    curls = []
    for f,p,coef,axis,per,scale in zip((fa,fb),(pa,pb),(ca,cb),axes,periodic,scales):
        d = np.roll(f,-1 if forward else 1,axis=axis)
        d = d-f if forward else f-d
        if not per:
            edge = [slice(None)]*3
            edge[axis] = -1 if forward else 0
            d[tuple(edge)] = (-1 if forward else 1)*f[tuple(edge)]
        if p.size > 1:
            width=p.shape[axis]//2
            for side in (0,1):
                full=[slice(None)]*3; compact=[slice(None)]*3
                full[axis]=slice(0,width) if side==0 else slice(-width,None)
                compact[axis]=slice(side*width,(side+1)*width)
                shape=[1,1,1]; shape[axis]=width
                b=(coef[:width] if side==0 else coef[-width:]).reshape(shape)
                memory=p[tuple(compact)]; derivative=d[tuple(full)]
                memory *= b
                memory += (b-1)*derivative
                derivative += memory
        curls.append(d*scale)
    out *= aa
    out += bb*(curls[0]-curls[1])


def _mode(c, er, spacing):
    """Scalar transverse seed; deliberately not a full-vector port eigenmode."""
    from scipy.sparse import diags, eye, kron
    from scipy.sparse.linalg import eigsh
    nx,nz = c.nx,c.nz
    k0 = 2*np.pi/c.wavelength
    # Dimensionless operator improves eigenvalue conditioning.
    dx,dz = spacing[0],spacing[2]
    lx = diags([np.ones(nx-1),-2*np.ones(nx),np.ones(nx-1)],[-1,0,1])/(k0*dx)**2
    lz = diags([np.ones(nz-1),-2*np.ones(nz),np.ones(nz-1)],[-1,0,1])/(k0*dz)**2
    op = kron(lx,eye(nz))+kron(eye(nx),lz)+diags(er[:,c.source_y,:].ravel().astype(float))
    vals,vecs = eigsh(op,k=1,which='LA',tol=1e-7,v0=np.ones(nx*nz))
    mode = vecs[:,0].reshape(nx,nz)
    return (mode/np.max(abs(mode))).astype(np.float32),float(np.sqrt(max(0,vals[0])))


def simulate(c: Config3D, frame_stride=0, reference=False, *, on_frame=None,
             preview_stride=1, preview_interval=.25):
    """Parallelize independent components, with a barrier between H and E.

    Optional on_frame receives only three copied Ez sections and diagnostic
    scalars. Initial/final states always publish; intermediate states satisfy
    both stride and wall-clock limits. Observers do not change field updates.
    """
    preview_stride,preview_interval = _preview_options(on_frame,preview_stride,preview_interval)
    from concurrent.futures import ThreadPoolExecutor
    from .three_d_backend import get_update
    if c.workers not in (1,2,3):
        raise ValueError('workers must be 1, 2 or 3')
    _,backend=get_update(c.backend,_numpy_update)
    if backend=='native' and c.workers>1:
        with ThreadPoolExecutor(max_workers=c.workers) as executor:
            return _simulate(c,frame_stride,reference,executor,on_frame,preview_stride,preview_interval)
    return _simulate(c,frame_stride,reference,on_frame=on_frame,preview_stride=preview_stride,preview_interval=preview_interval)


def _simulate(c,frame_stride,reference,executor=None,on_frame=None,preview_stride=1,preview_interval=.25):
    er,sigma,pec,spacing,dt,src,widths = prepare(c)
    if reference:
        er.fill(er[src]); sigma.fill(0); pec.fill(False)
    shape = er.shape
    bounds = (c.boundary_x,c.boundary_y,c.boundary_z)
    periodic = tuple(b == 'periodic' for b in bounds)
    fields = [np.zeros(shape,dtype=np.float32) for _ in range(6)]
    one = np.ones(1,dtype=np.float32)
    uniform = float(er.min()) == float(er.max())
    ee = [np.array([er.flat[0]],dtype=np.float32)]*3 if uniform else [_edge_average(er,a,periodic[a]) for a in range(3)]
    lossless = not np.any(sigma)
    electric = []
    masks = []
    for axis in range(3):
        if lossless:
            electric.append((one,1/ee[axis]))
        else:
            q = (_edge_average(sigma,axis,periodic[axis])*float(dt/(2*EPS0))/ee[axis]).astype(np.float32)
            electric.append(((1-q)/(1+q),1/(ee[axis]*(1+q))))
        mask = pec | np.roll(pec,-1,axis=axis)
        # PEC/PML termination constrains tangential E only. Normal E can carry surface charge.
        for face,b in enumerate(bounds):
            if face != axis and b in {'pec','pml'}:
                sl = [slice(None)]*3
                sl[face] = [0,-1]
                mask[tuple(sl)] = True
        masks.append(mask)
    coeff = {}
    for forward in (False,True):
        coeff[forward] = []
        for n,w,d in zip(shape,widths,spacing):
            rate = -2*np.log(c.pml_reflection)*C0*profile(n,w,.5 if forward else 0)/(max(w,1)*d)
            coeff[forward].append(np.exp(-rate*dt).astype(np.float32))
    memories = {}
    for component in range(6):
        axes = ((component+1)%3,(component+2)%3)
        # Derivative memory is identically zero outside PML. Store two compact
        # boundary slabs per derivative, including the staggered transition site.
        memories[component] = [np.zeros(tuple(2*(widths[a]+1) if j==a else n for j,n in enumerate(shape)) if widths[a] else (1,),dtype=np.float32) for a in axes]
    from .three_d_backend import get_update
    update,backend = get_update(c.backend,_numpy_update)
    # Positive curl E update: dH_c/d_b - dH_b/d_c. H update reverses the signs.
    # A single primitive handles both via signed scales.
    scales = tuple(C0*dt/d for d in spacing)
    f = C0/c.wavelength
    sx,sy,sz = src
    xp,zp = np.arange(c.nx)-sx,np.arange(c.nz)-sz
    nsrc = np.sqrt(float(er[src]))
    delay = (nsrc*np.sin(np.deg2rad(c.angle_deg))*xp*spacing[0]/C0)[:,None]
    transverse = np.exp(-(zp/c.source_width_z)**2)
    if periodic[2]:
        transverse[:] = 1
    line = (abs(xp) <= c.source_width/2).astype(float)
    if c.source_width >= c.nx:
        line[:] = 1
    beam = np.exp(-(xp/c.source_width)**2)
    taper = []
    for n,w in [(c.nx,widths[0]),(c.nz,widths[2])]:
        j = np.arange(n)
        taper.append(np.sin(.5*np.pi*np.clip(np.minimum(j-w,n-1-w-j)/8,0,1))**2 if w else np.ones(n))
    seed_neff = None
    if c.injection == 'mode':
        amp,seed_neff = _mode(c,er,spacing)
    else:
        amp = (beam if c.injection == 'beam' else line)[:,None]*transverse[None,:]
    amp = (amp*taper[0][:,None]*taper[1][None,:]).astype(np.float32)
    if c.injection == 'tfsf':
        amp[:] = 1
    energy,energy_steps = [],[]
    frames,frame_steps = [],[]
    snapshot_steps = sorted({n for n in c.snapshots if 0 < n <= c.steps}|{c.steps})
    snapshots = {key:[] for key in ('xy','xz','yz')}
    detector_y = c.detector_y if c.detector_y is not None else min(c.ny-widths[1]-5,max(sy+5,c.ny*3//4))
    avg_steps = min(c.steps,max(1,round(c.average_cycles/f/dt)))
    detector_phasor = np.zeros((3,c.nx,c.nz),dtype=np.complex64)
    detector_mean = np.zeros((c.nx,c.nz),dtype=np.float64)
    detector_trace = np.zeros(c.steps)
    plane_probes = np.array([sy+10,c.ny-widths[1]-5])
    probes = np.zeros((c.steps,2))
    if c.spectra and (plane_probes[1] <= plane_probes[0] or np.any(sigma[:,plane_probes,:]) or (c.layers and min(l.start for l in c.layers) <= plane_probes[0])):
        raise ValueError('Spectral probes require separated lossless exterior regions')
    mur_faces = [(component,axis,side) for component in range(3) for axis,b in enumerate(bounds) if b == 'mur' and axis != component for side in (0,-1)]
    def face(axis,index):
        s = [slice(None)]*3; s[axis]=index
        return tuple(s)
    def advance_h(a):
        b,d = (a+1)%3,(a+2)%3
        update(fields[a+3],fields[d],fields[b],*memories[a+3],coeff[True][b],coeff[True][d],one,one,True,(b,d),(periodic[b],periodic[d]),(-scales[b],-scales[d]))
    def advance_e(a):
        b,d = (a+1)%3,(a+2)%3
        update(fields[a],fields[d+3],fields[b+3],*memories[a],coeff[False][b],coeff[False][d],*electric[a],False,(b,d),(periodic[b],periodic[d]),(scales[b],scales[d]))
    if on_frame is not None:
        def section_copies(values):
            planes = (values[:,:,sz].copy(), values[:,detector_y,:].copy(), values[sx,:,:].copy())
            for plane in planes: plane.flags.writeable = False
            return planes
        preview_material,preview_pec = section_copies(er),section_copies(pec)
        def publish_preview(step):
            on_frame(PreviewFrame3D(step,c.steps,step*dt,spacing,section_copies(fields[2]),
                preview_material,preview_pec,float(energy[-1]) if energy else 0.,
                int(energy_steps[-1]) if energy_steps else 0))
        publish_preview(0)
        last_preview = time.perf_counter()
    for k in range(c.steps):
        old = [(fields[a][face(b,s)].copy(),fields[a][face(b,1 if s == 0 else -2)].copy()) for a,b,s in mur_faces]
        if executor is None:
            for a in range(3): advance_h(a)
        else:
            list(executor.map(advance_h,range(3)))
        if c.injection == 'tfsf':
            fields[3][:,sy-1,:] += scales[1]*waveform(k*dt,f,c.source,c.tau_periods)
        if executor is None:
            for a in range(3): advance_e(a)
        else:
            list(executor.map(advance_e,range(3)))
        if c.injection == 'point':
            fields[2][src] += waveform(k*dt,f,c.source,c.tau_periods)
        elif c.injection == 'diagonal':
            offsets = np.arange(round(c.source_width))
            fields[2][sx+offsets,sy-offsets,sz] += waveform(k*dt,f,c.source,c.tau_periods)
        elif c.injection == 'tfsf':
            shift = nsrc*spacing[1]/(2*C0)+dt/2
            b = electric[2][1]
            fields[2][:,sy,:] += (b[0] if b.size==1 else b[:,sy,:])*scales[1]*nsrc*waveform(k*dt+shift,f,c.source,c.tau_periods)
        else:
            fields[2][:,sy,:] += amp*waveform(k*dt-delay,f,c.source,c.tau_periods)
        for a in range(3):
            fields[a][masks[a]] = 0
        for (a,b,s),(oldface,oldadj) in zip(mur_faces,old):
            j = 1 if s == 0 else -2
            v = C0/np.sqrt(ee[a][0] if ee[a].size==1 else ee[a][face(b,s)])
            ratio = (v*dt/spacing[b]-1)/(v*dt/spacing[b]+1)
            fields[a][face(b,s)] = oldadj+ratio*(fields[a][face(b,j)]-oldface)
        if mur_faces:
            for a in range(3): fields[a][masks[a]]=0
        if k % c.energy_stride == 0 or k == c.steps-1:
            value = sum(np.sum(ee[a]*fields[a]**2,dtype=np.float64)+np.sum(fields[a+3]**2,dtype=np.float64) for a in range(3))
            energy.append(.5*np.prod(spacing)*value); energy_steps.append(k+1)
            if not np.isfinite(value):
                raise FloatingPointError(f'Non-finite 3D fields at step {k+1}')
        detector_trace[k] = fields[2][sx,detector_y,sz]
        if c.spectra:
            probes[k] = fields[2][:,plane_probes,:].mean(axis=(0,2))
        if k >= c.steps-avg_steps:
            for a in range(3):
                plane = fields[a][:,detector_y,:]
                detector_phasor[a] += plane*np.exp(-2j*np.pi*f*(k+1)*dt)*(2/avg_steps)
                detector_mean += plane.astype(float)**2/avg_steps
        if k+1 in snapshot_steps:
            snapshots['xy'].append(fields[2][:,:,sz].copy())
            snapshots['xz'].append(fields[2][:,detector_y,:].copy())
            snapshots['yz'].append(fields[2][sx,:,:].copy())
        if frame_stride and (k % frame_stride == 0 or k == c.steps-1):
            frames.append(fields[2][:,:,sz].copy()); frame_steps.append(k+1)
        if on_frame is not None and (k == c.steps-1 or
                ((k+1) % preview_stride == 0 and time.perf_counter()-last_preview >= preview_interval)):
            publish_preview(k+1)
            last_preview = time.perf_counter()
    result = {name:field for name,field in zip(('ex','ey','ez','hx','hy','hz'),fields)}
    result.update(epsilon_r=er,sigma=sigma,pec=pec,dx=spacing[0],dy=spacing[1],dz=spacing[2],dt=dt,
                  energy=np.array(energy),energy_steps=np.array(energy_steps),
                  snapshot_steps=np.array(snapshot_steps),frames=np.array(frames),frame_steps=np.array(frame_steps),
                  detector_mean_square=detector_mean,detector_phasor=detector_phasor,detector_trace=detector_trace,
                  detector_y=detector_y,source_z=sz,average_steps=avg_steps,time=(np.arange(c.steps)+1)*dt,
                  backend=np.array(backend),workers=c.workers if executor is not None else 1,probe_cells=plane_probes,probes=probes)
    for key,values in snapshots.items(): result['snapshots_'+key]=np.asarray(values)
    if seed_neff is not None: result['scalar_seed_neff']=seed_neff
    return result


def spectrum(c,result,baseline):
    from .one_d import spectrum as plane_spectrum
    line = dict(result,epsilon_r=result['epsilon_r'][0,:,0],sigma=result['sigma'][0,:,0])
    return plane_spectrum(c,line,baseline)
