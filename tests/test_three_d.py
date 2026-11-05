"""Independent physical checks and the complete 24-case 3D coverage."""
from dataclasses import replace
import subprocess
import sys
import numpy as np
import pytest
from fdtd.config import Config2D, Layer, C0
from fdtd.three_d import Config3D, prepare, simulate
from fdtd.two_d import simulate as simulate2
from run_all_3d import experiments, ROOT


def base(**changes):
    c=Config3D('test3d','test','',nx=24,ny=100,nz=16,steps=200,
               pml_cells=6,pml_cells_z=4,source_x=12,source_y=20,
               boundary_x='periodic',boundary_z='periodic',
               injection='tfsf',source='gaussian',points_per_wavelength=20,
               source_width=24,energy_stride=1)
    return replace(c,**changes)


def test_native_matches_python_with_material_pml_and_vector_fields():
    c=base(nx=20,ny=28,nz=18,steps=70,source_x=10,source_y=10,
           pml_cells=4,pml_cells_z=4,boundary_x='pml',boundary_z='pml',
           injection='point',source='modulated',geometry='layers',
           layers=[Layer(16,28,2.25,.03)],wavelength=.1,dx=.005)
    a=simulate(replace(c,backend='numpy'))
    b=simulate(replace(c,backend='native'))
    sequential=simulate(replace(c,backend='native',workers=1))
    for key in ('ex','ey','ez','hx','hy','hz'):
        assert np.allclose(a[key],b[key],atol=2e-6,rtol=1e-4)
        assert np.array_equal(b[key],sequential[key])
    assert np.max(abs(b['ex']))>1e-4 and np.max(abs(b['ey']))>1e-4


def test_depth_independent_3d_reduces_to_existing_2d():
    c=base(nx=26,ny=50,nz=8,steps=100,source_x=13,source_y=25,
           boundary_y='periodic',injection='line',source='modulated',source_width=100,
           geometry='layers',layers=[Layer(30,40,4)])
    r=simulate(c)
    values={k:getattr(c,k) for k in Config2D.__dataclass_fields__}
    b=simulate2(Config2D(**values))
    assert np.allclose(r['ez'][:,:,0],b['e'],atol=2e-6,rtol=1e-4)
    assert np.max(np.ptp(r['ez'],axis=2))==0
    for key in ('ex','ey','hz'): assert np.max(abs(r[key]))==0


def test_plane_wave_speed_and_one_way_injection():
    c=base(ny=160,steps=210,snapshots=(120,180))
    r=simulate(c)
    first,second=r['snapshots_xy'][:2]
    assert abs((np.argmax(second[0])-np.argmax(first[0]))/60-.5)<.025
    assert np.max(abs(second[:,:c.source_y-5]))<.006*np.max(abs(second))
    for key in ('ex','ey','hz'): assert np.max(abs(r[key]))==0


def test_plane_pulse_pml_absorption():
    c=base(ny=100,steps=550,pml_cells=12,source_y=25)
    r=simulate(c)
    assert r['energy'][-1]/r['energy'].max()<1e-4
    pec=simulate(replace(c,boundary_y='pec'))
    assert pec['energy'][-1]/pec['energy'].max()>.6


def test_fresnel_amplitude_and_loss_attenuation():
    c=base(ny=280,steps=850,source_y=25,points_per_wavelength=40,
           geometry='layers',layers=[Layer(120,280,4)],spectra=True)
    r=simulate(c); ref=simulate(c,reference=True)
    # Pulse amplitudes at the first probe, before a far-boundary return.
    reflected=r['probes'][:,0]-ref['probes'][:,0]
    coefficient=np.min(reflected)/np.max(ref['probes'][:,0])
    assert abs(coefficient+1/3)<.02
    c=base(ny=160,steps=650,wavelength=.1,dx=.0025,
           geometry='layers',layers=[Layer(65,110,2.25,.1)])
    loss=simulate(c); lossless=simulate(replace(c,layers=[Layer(65,110,2.25)]))
    assert np.sum(loss['detector_trace']**2)<.7*np.sum(lossless['detector_trace']**2)


def test_vector_dipole_rotation_symmetry_and_periodic_translation():
    c=base(nx=25,ny=25,nz=25,source_x=12,source_y=12,injection='point',
           boundary_y='periodic',source='modulated',steps=100)
    r=simulate(c)
    assert np.allclose(r['ez'],r['ez'].transpose(1,0,2),atol=2e-6)
    shifted=simulate(replace(c,source_x=14,source_y=15,source_z=16))
    for name in ('ex','ey','ez','hx','hy','hz'):
        assert np.allclose(np.roll(r[name],(2,3,4),axis=(0,1,2)),shifted[name],atol=2e-6)


def test_six_face_absorption_and_closed_cavity_retention():
    c=base(nx=41,ny=41,nz=41,steps=600,source_x=20,source_y=20,
           pml_cells=8,pml_cells_z=8,injection='point',source='modulated',
           points_per_wavelength=12,energy_stride=5)
    for boundary in ('pml','mur'):
        r=simulate(replace(c,boundary_x=boundary,boundary_y=boundary,boundary_z=boundary))
        assert r['energy'][-1]/r['energy'].max()<1e-6
    r=simulate(replace(c,boundary_x='pec',boundary_y='pec',boundary_z='pec'))
    settled=r['energy'][r['energy_steps']>120]
    # A driven dipole stores then returns near-field energy during the pulse;
    # compare AFTER the source turns off, not against the driven peak.
    assert .9<settled[-1]/settled[0]<1.1
    assert np.ptp(settled)/np.mean(settled)<.15


def test_lossless_plane_slab_spectral_conservation():
    from fdtd.three_d import spectrum
    c=base(nx=8,nz=8,source_x=4,ny=260,steps=2000,pml_cells=16,
           source_y=30,geometry='layers',layers=[Layer(100,140,4)],spectra=True)
    r=simulate(c); ref=simulate(c,reference=True); s=spectrum(c,r,ref)
    valid=s['spectral_valid']
    assert valid.any()
    assert np.max(abs(s['residual'][valid]))<.015
    assert np.max(s['reflectance'][valid])>.3


def test_finite_aperture_and_pec_tangential_fields():
    c=base(nx=40,ny=50,nz=32,source_x=20,source_y=12,steps=100,
           injection='line',geometry='slits',wall_y=25,slit_count=2,
           slit_width=4,slit_gap=4,slit_height=10,boundary_z='pml',pml_cells_z=6)
    er,sg,pec,*_=prepare(c)
    assert np.count_nonzero(~pec[:,25,:])==2*4*10
    r=simulate(c)
    assert np.max(abs(r['ex'][pec]))==0 and np.max(abs(r['ez'][pec]))==0
    assert np.max(abs(r['ey']))>0


@pytest.mark.parametrize('changes',[{'courant':.7},{'dz':-1},{'source_z':0},{'nz':8,'boundary_z':'pml'},
                                  {'injection':'tfsf','boundary_z':'pec'},{'layers':[Layer(30,50,2,-.1)]}])
def test_invalid_inputs(changes):
    with pytest.raises(ValueError): prepare(base(**changes))


@pytest.mark.parametrize('path,c',experiments(),ids=lambda v:getattr(v,'name',str(v)))
def test_each_3d_configuration_is_valid(path,c):
    er,sigma,pec,spacing,dt,source,widths=prepare(c)
    assert er.shape==(c.nx,c.ny,c.nz)
    assert np.isfinite(er).all() and not pec[source]


def test_exact_2d_coverage_and_preserved_parameters():
    from run_all import experiments as old
    pairs={c.name:c for _,c in old() if isinstance(c,Config2D)}
    new=experiments()
    assert len(new)==len(pairs)==24
    for _,c in new:
        source=pairs[c.name.removesuffix('_3d')]
        for name in ('nx','ny','dx','dy','wavelength','steps','layers','slit_width','slit_gap','wall_y','detector_y','bend_radius'):
            assert getattr(c,name)==getattr(source,name)


def test_independent_script_and_saved_vector_volumes(tmp_path):
    path=ROOT/'experiments_3d/23_tfsf_plane_wave_3d.py'
    subprocess.run([sys.executable,str(path),'--steps','80','--gif','--frames','4','--output',str(tmp_path)],cwd=tmp_path,check=True,capture_output=True)
    for file in ('config.json','diagnostics.json','data.npz','fields.png','snapshots.png','animation.gif'):
        assert (tmp_path/file).is_file()
    with np.load(tmp_path/'data.npz',allow_pickle=False) as r:
        assert all(r[k].shape==(200,200,8) for k in ('ex','ey','ez','hx','hy','hz'))
    from run_all_3d import completed
    c=replace(next(c for _,c in experiments() if c.name.startswith('23')),steps=80)
    assert completed(c,tmp_path,True,True) is not None
    assert completed(replace(c,steps=81),tmp_path,True,True) is None
    (tmp_path/'data.npz').write_bytes(b'interrupted archive')
    assert completed(c,tmp_path,True,True) is None
