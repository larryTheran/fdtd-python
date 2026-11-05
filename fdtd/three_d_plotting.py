"""Three orthogonal field sections and detector maps, with physical axes."""
import numpy as np


def figures(c,r,output):
    import matplotlib.pyplot as plt
    dx,dy,dz = (float(r[k])*1e6 for k in ('dx','dy','dz'))
    sz,det = int(r['source_z']),int(r['detector_y'])
    sections = [('xy',r['ez'][:,:,sz],r['epsilon_r'][:,:,sz],r['pec'][:,:,sz],dx,dy,'x','y'),
                ('xz',r['ez'][:,det,:],r['epsilon_r'][:,det,:],r['pec'][:,det,:],dx,dz,'x','z'),
                ('yz',r['ez'][c.source_x,:,:],r['epsilon_r'][c.source_x,:,:],r['pec'][c.source_x,:,:],dy,dz,'y','z')]
    fig,axs = plt.subplots(2,3,figsize=(15,8),layout='constrained')
    lim = max(float(np.max(abs(r['ez']))),1e-15)
    for col,(key,e,er,pec,a,b,x,y) in enumerate(sections):
        extent = (0,(e.shape[0]-1)*a,0,(e.shape[1]-1)*b)
        im = axs[0,col].imshow(e.T,origin='lower',extent=extent,cmap='RdBu_r',vmin=-lim,vmax=lim,aspect='auto')
        axs[0,col].set_title(f'{key.upper()} section — final Ez/Z0')
        fig.colorbar(im,ax=axs[0,col],shrink=.75)
        material = np.ma.masked_where(pec,er)
        im = axs[1,col].imshow(material.T,origin='lower',extent=extent,cmap='viridis',aspect='auto')
        if pec.any():
            axs[1,col].imshow(np.ma.masked_where(~pec,pec).T,origin='lower',extent=extent,cmap='gray_r',vmin=0,vmax=1,aspect='auto')
        axs[1,col].set_title('Relative permittivity; black = PEC')
        fig.colorbar(im,ax=axs[1,col],shrink=.75)
        for row in range(2): axs[row,col].set(xlabel=f'{x} (μm)',ylabel=f'{y} (μm)')
    fig.suptitle(c.title)
    fig.savefig(output/'fields.png',dpi=140); plt.close(fig)
    fig,axs = plt.subplots(1,2,figsize=(12,4),layout='constrained')
    axs[0].plot(r['energy_steps']*r['dt']*1e15,r['energy'])
    axs[0].set(xlabel='Time (fs)',ylabel='Normalized field energy proxy',title='Whole grid, including absorbing layers')
    im=axs[1].imshow(r['detector_mean_square'].T,origin='lower',aspect='auto',extent=(0,(c.nx-1)*dx,0,(c.nz-1)*dz),cmap='inferno')
    axs[1].set(xlabel='x (μm)',ylabel='z (μm)',title=f'Mean Σ(Ei/Z0)² at y={det*dy:.3g} μm')
    fig.colorbar(im,ax=axs[1])
    fig.savefig(output/'diagnostics.png',dpi=140); plt.close(fig)
    # Snapshots retain the propagating pulse even when final fields have decayed.
    count=len(r['snapshot_steps'])
    fig,axs=plt.subplots(1,count,figsize=(4*count,4),squeeze=False,layout='constrained')
    lim=max(float(np.max(abs(r['snapshots_xy']))),1e-15)
    for ax,n,e in zip(axs[0],r['snapshot_steps'],r['snapshots_xy']):
        ax.imshow(e.T,origin='lower',extent=(0,(c.nx-1)*dx,0,(c.ny-1)*dy),cmap='RdBu_r',vmin=-lim,vmax=lim,aspect='auto')
        ax.set(title=f'Step {n}',xlabel='x (μm)',ylabel='y (μm)')
    fig.savefig(output/'snapshots.png',dpi=120); plt.close(fig)
    # Three spatially placed planes from the strongest saved snapshot show
    # depth variation without pretending a 2D image is a volume rendering.
    selected=int(np.argmax(np.max(abs(r['snapshots_xy']),axis=(1,2))))
    views=[r['snapshots_xy'][selected],r['snapshots_xz'][selected],r['snapshots_yz'][selected]]
    scale=max(max(float(np.max(abs(v))) for v in views),1e-15)
    norm=plt.Normalize(-scale,scale)
    fig=plt.figure(figsize=(9,7),layout='constrained'); ax=fig.add_subplot(projection='3d')
    for plane,values in enumerate(views):
        a=np.arange(0,values.shape[0],max(1,values.shape[0]//100))
        b=np.arange(0,values.shape[1],max(1,values.shape[1]//100))
        aa,bb=np.meshgrid(a,b,indexing='ij')
        if plane==0: x,y,z=aa*dx,bb*dy,np.full_like(aa,sz*dz,dtype=float)
        elif plane==1: x,y,z=aa*dx,np.full_like(aa,det*dy,dtype=float),bb*dz
        else: x,y,z=np.full_like(aa,c.source_x*dx,dtype=float),aa*dy,bb*dz
        colors=plt.get_cmap('RdBu_r')(norm(values[np.ix_(a,b)]))
        ax.plot_surface(x,y,z,facecolors=colors,shade=False,rcount=len(a),ccount=len(b),alpha=.9)
    ax.set(xlabel='x (μm)',ylabel='y (μm)',zlabel='z (μm)',
           title=f'{c.name}\nEz/Z0 on three sections at step {r["snapshot_steps"][selected]}')
    ax.set_box_aspect((c.nx*dx,c.ny*dy,c.nz*dz))
    fig.colorbar(plt.cm.ScalarMappable(norm=norm,cmap='RdBu_r'),ax=ax,shrink=.65,pad=.1)
    fig.savefig(output/'volume_sections.png',dpi=140); plt.close(fig)
    if 'reflectance' in r:
        valid=r['spectral_valid']; fig,ax=plt.subplots(layout='constrained')
        for name in ('reflectance','transmittance','residual'): ax.plot(r['frequency'][valid]/1e9,r[name][valid],label=name)
        ax.set(xlabel='Frequency (GHz)',ylabel='Fraction'); ax.legend()
        fig.savefig(output/'spectra.png',dpi=140); plt.close(fig)


def animation(c,r,output):
    from PIL import Image,ImageDraw
    import matplotlib as mpl
    frames=r['frames']
    if not len(frames): return
    lim=max(float(np.max(abs(frames))),1e-15)
    images=[]
    for frame,step in zip(frames,r['frame_steps']):
        pixels=(mpl.colormaps['RdBu_r'](.5+.5*frame.T[::-1]/lim)[:,:,:3]*255).astype(np.uint8)
        im=Image.fromarray(pixels).resize((600,600))
        ImageDraw.Draw(im).text((8,8),f'{c.name} | XY section | step {step}',fill='black',stroke_width=1,stroke_fill='white')
        images.append(im)
    images[0].save(output/'animation.gif',save_all=True,append_images=images[1:],duration=90,loop=0)
