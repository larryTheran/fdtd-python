"""Standalone real-Jupyter smoke check for distinct live FDTD frames."""
import argparse
import base64
import hashlib
import os
from pathlib import Path
import queue
import sys
import tempfile
import time
from jupyter_client import KernelManager
from jupyter_client.kernelspec import KernelSpec


def main(frames_dir=None):
    if frames_dir is not None:
        frames_dir=Path(frames_dir)
        frames_dir.mkdir(parents=True,exist_ok=True)
    root=Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory(prefix='pylab-fdtd-jupyter-') as directory:
        environment=os.environ.copy()
        for key in ('IPYTHONDIR','JUPYTER_CONFIG_DIR','JUPYTER_DATA_DIR','JUPYTER_RUNTIME_DIR','MPLCONFIGDIR'):
            target=Path(directory)/key; target.mkdir()
            environment[key]=str(target)
        environment['PYTHONDONTWRITEBYTECODE']='1'
        kernel=KernelManager(kernel_name='python3',autorestart=False)
        kernel._kernel_spec=KernelSpec(argv=[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}'],display_name='Preview check',language='python')
        kernel.start_kernel(cwd=directory,env=environment)
        client=kernel.client(); client.start_channels()
        try:
            client.wait_for_ready(timeout=30)
            source="""
import sys
sys.path.insert(0, ROOT)
from fdtd.three_d import Config3D,simulate
from fdtd.three_d_live import LiveFieldPreview,in_notebook
import matplotlib.pyplot as plt
assert in_notebook()
before=plt.get_fignums()
config=Config3D('live-smoke','Live FDTD smoke','',nx=12,ny=14,nz=10,steps=8,
    source_x=6,source_y=6,source_z=5,geometry='free',injection='point',source='sine',
    boundary_x='periodic',boundary_y='periodic',boundary_z='periodic',backend='numpy',energy_stride=1)
with LiveFieldPreview(config) as preview:
    result=simulate(config,on_frame=preview,preview_stride=2,preview_interval=0)
assert preview.closed and preview.figure is None and plt.get_fignums()==before
print('LIVE_FDTD_COMPLETE', result['ez'].shape)
""".replace('ROOT',repr(str(root)))
            request=client.execute(source)
            images=[]; complete=False
            deadline=time.monotonic()+45
            while time.monotonic()<deadline:
                try: message=client.get_iopub_msg(timeout=.5)
                except queue.Empty: continue
                if message.get('parent_header',{}).get('msg_id')!=request: continue
                kind=message['msg_type']; content=message['content']
                if kind=='error': raise AssertionError('\n'.join(content.get('traceback',[])))
                if kind in ('display_data','update_display_data') and 'image/png' in content.get('data',{}):
                    raw=base64.b64decode(content['data']['image/png'])
                    assert raw.startswith(b'\x89PNG')
                    if frames_dir is not None:
                        if not images: (frames_dir/'first.png').write_bytes(raw)
                        (frames_dir/'last.png').write_bytes(raw)
                    images.append((kind,content.get('transient',{}).get('display_id'),hashlib.sha256(raw).hexdigest(),content['data'].get('text/plain','')))
                if kind=='stream' and 'LIVE_FDTD_COMPLETE' in content.get('text',''): complete=True
                if kind=='status' and content.get('execution_state')=='idle': break
            else: raise AssertionError('Live FDTD execution timed out')
            assert complete and len(images)==5,images
            assert images[0][0]=='display_data' and all(image[0]=='update_display_data' for image in images[1:])
            assert images[0][1] and len({image[1] for image in images})==1
            assert len({image[2] for image in images})>=3
            assert images[-1][3]=='live-smoke: step 8/8'
            print('PASS: 5 PNG frames emitted during actual Jupyter execution, one stable display_id, distinct evolving fields, complete state and no pyplot figure leak')
        finally:
            client.stop_channels(); kernel.shutdown_kernel(now=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--frames-dir',type=Path,help='Optional folder for first/last preview PNGs')
    main(parser.parse_args().frames_dir)
