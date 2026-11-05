"""Optional standard-C accelerator. NumPy remains a complete supported backend."""
import ctypes
import hashlib
from pathlib import Path
import shutil
import subprocess
import sys
import warnings
import numpy as np

_CACHE = None


def get_update(backend, fallback):
    global _CACHE
    if backend not in {'auto','numpy','native'}:
        raise ValueError('backend must be auto, numpy or native')
    if backend == 'numpy':
        return fallback,'numpy'
    if _CACHE is not None:
        return _CACHE,'native'
    try:
        compiler = shutil.which('cc') or shutil.which('clang') or shutil.which('gcc')
        if compiler is None:
            raise RuntimeError('No local C compiler available')
        source = Path(__file__).with_name('three_d_kernel.c')
        digest = hashlib.sha256(source.read_bytes()+sys.platform.encode()).hexdigest()[:16]
        directory = source.parents[1]/'.cache'/'fdtd3d'
        directory.mkdir(parents=True,exist_ok=True)
        library = directory/f'curl_{digest}.so'
        if not library.exists():
            import os
            temporary = library.with_name(f'{library.stem}_{os.getpid()}.so')
            try:
                subprocess.run([compiler,'-O3','-std=c99','-fPIC','-shared',str(source),'-o',str(temporary)],check=True,capture_output=True)
                temporary.replace(library)
            finally:
                temporary.unlink(missing_ok=True)
        handle = ctypes.CDLL(str(library))
        pointer = np.ctypeslib.ndpointer(dtype=np.float32,flags='C_CONTIGUOUS')
        handle.update.argtypes = [pointer]*9+[ctypes.c_int]*12+[ctypes.c_float]*2
        handle.update.restype = None
        def update(out,fa,fb,pa,pb,ca,cb,aa,bb,forward,axes,periodic,scales):
            handle.update(out,fa,fb,pa,pb,ca,cb,aa,bb,*out.shape,int(forward),*axes,*map(int,periodic),pa.shape[axes[0]]//2 if pa.size>1 else 0,pb.shape[axes[1]]//2 if pb.size>1 else 0,int(aa.size==1),int(bb.size==1),*scales)
        _CACHE = update
        return update,'native'
    except (OSError,RuntimeError,subprocess.CalledProcessError) as exc:
        if backend == 'native':
            raise RuntimeError('Unable to build native accelerator; use --backend numpy') from exc
        warnings.warn(f'Using NumPy 3D backend: {exc}',RuntimeWarning)
        return fallback,'numpy'
