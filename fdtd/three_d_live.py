"""Notebook-only, bounded live rendering of the three FDTD field sections."""
import base64
from io import BytesIO
import math
import operator


def in_notebook():
    try:
        from IPython import get_ipython
    except ImportError:
        return False
    shell = get_ipython()
    return shell is not None and getattr(shell, 'kernel', None) is not None


def validate_options(stride, fps):
    try:
        checked_stride = operator.index(stride)
        checked_fps = float(fps)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError('Live stride must be an integer >=1 and fps finite in (0, 10]') from error
    if isinstance(stride, bool) or checked_stride < 1 or not math.isfinite(checked_fps) or not 0 < checked_fps <= 10:
        raise ValueError('Live stride must be an integer >=1 and fps finite in (0, 10]')
    return checked_stride, checked_fps


class LiveFieldPreview:
    """One figure and display handle per run; frames replace the same output.

    The figure is not registered with pyplot, so inline's post-cell hook cannot
    duplicate it. Only the current PNG and three current field planes are kept.
    """
    def __init__(self, config):
        self.config = config
        self.figure = None
        self.images = []
        self.axes = None
        self.handle = None
        self.peak = 1e-15
        self.closed = False

    def __enter__(self):
        return self

    def _initialize(self, frame):
        import numpy as np
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_agg import FigureCanvasAgg
        self.figure = Figure(figsize=(12,6.4),dpi=90,layout='constrained')
        FigureCanvasAgg(self.figure)
        self.axes = self.figure.subplots(2,3)
        dx,dy,dz = (value*1e6 for value in frame.spacing)
        for col,(field,er,pec,(a,b),(x,y)) in enumerate(zip(frame.fields,frame.epsilon_r,frame.pec,
                ((dx,dy),(dx,dz),(dy,dz)),(('x','y'),('x','z'),('y','z')))):
            extent = (0,(field.shape[0]-1)*a,0,(field.shape[1]-1)*b)
            image = self.axes[0,col].imshow(field.T,origin='lower',extent=extent,
                cmap='RdBu_r',vmin=-self.peak,vmax=self.peak,aspect='auto')
            self.images.append(image)
            self.figure.colorbar(image,ax=self.axes[0,col],shrink=.75)
            material = self.axes[1,col].imshow(np.ma.masked_where(pec,er).T,origin='lower',
                extent=extent,cmap='viridis',aspect='auto')
            if pec.any():
                self.axes[1,col].imshow(np.ma.masked_where(~pec,pec).T,origin='lower',
                    extent=extent,cmap='gray_r',vmin=0,vmax=1,aspect='auto')
            self.axes[1,col].set_title('Relative permittivity; black = PEC',fontsize=10)
            self.figure.colorbar(material,ax=self.axes[1,col],shrink=.75)
            for row in range(2):
                self.axes[row,col].set(xlabel=f'{x} (μm)',ylabel=f'{y} (μm)')
        self.heading = self.figure.suptitle(self.config.title,fontsize=13)

    def __call__(self, frame):
        if self.closed:
            raise RuntimeError('The live preview is closed')
        import numpy as np
        from IPython.display import display
        if self.figure is None:
            self._initialize(frame)
        self.peak = max(self.peak,*(float(np.max(np.abs(field))) for field in frame.fields))
        for key,ax,image,field in zip(('XY','XZ','YZ'),self.axes[0],self.images,frame.fields):
            image.set_data(field.T)
            image.set_clim(-self.peak,self.peak)
            ax.set_title(f'{key} section — Ez/Z0',fontsize=11)
        state = 'Complete' if frame.step == frame.steps else 'Live'
        self.heading.set_text(f'{self.config.title}\n{state} · step {frame.step:,} / {frame.steps:,} '
            f'({100*frame.step/frame.steps:.1f}%) · t = {frame.time_s*1e15:.2f} fs')
        # The latest energy proxy is labelled by its own sampling step.
        self.figure.supxlabel(f'Field color scale: peak across displayed sections · '
            f'Energy proxy at step {frame.energy_step:,}: {frame.energy:.4g}',fontsize=9)
        buffer = BytesIO()
        self.figure.savefig(buffer,format='png',dpi=90)
        data = {'image/png': base64.b64encode(buffer.getvalue()).decode('ascii'),
                'text/plain': f'{self.config.name}: step {frame.step}/{frame.steps}'}
        if self.handle is None:
            self.handle = display(data,raw=True,display_id=True)
        else:
            self.handle.update(data,raw=True)

    def close(self):
        if self.figure is not None:
            self.figure.clear()
        self.images.clear()
        self.figure = None
        self.axes = None
        self.handle = None
        self.heading = None
        self.closed = True

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        return False
