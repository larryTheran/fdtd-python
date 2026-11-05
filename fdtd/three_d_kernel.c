/* Optional acceleration of the Python reference curl/CPML update.
 * No fast-math: reference comparisons depend on IEEE finite arithmetic.
 * Array storage is contiguous float32 in x,y,z order; no shared mutable globals.
 */
#include <stddef.h>
static inline size_t compact_index(int i,int j,int k,int nx,int ny,int nz,int axis,int width) {
    if (axis==0) {if(i>=width) i-=nx-2*width;}
    if (axis==1) {if(j>=width) j-=ny-2*width; ny=2*width;}
    if (axis==2) {if(k>=width) k-=nz-2*width; nz=2*width;}
    return ((size_t)i*ny+j)*nz+k;
}
void update(float *out, const float *fa, const float *fb,
            float *pa, float *pb, const float *ca, const float *cb,
            const float *aa, const float *bb,
            int nx, int ny, int nz, int forward, int axis_a, int axis_b,
            int periodic_a, int periodic_b, int memory_a, int memory_b,
            int scalar_a, int scalar_b, float scale_a, float scale_b) {
    const size_t size = (size_t)nx*ny*nz;
    const size_t strides[3] = {(size_t)ny*nz,(size_t)nz,1};
    const int dims[3] = {nx,ny,nz};
    for (int i=0;i<nx;i++) for (int j=0;j<ny;j++) for (int k=0;k<nz;k++) {
        const int coord[3] = {i,j,k};
        size_t p = ((size_t)i*ny+j)*nz+k;
        const int axes[2]={axis_a,axis_b}, periods[2]={periodic_a,periodic_b};
        const float *fs[2]={fa,fb};
        float d[2];
        for (int t=0;t<2;t++) {
            int axis=axes[t], at=coord[axis];
            float neighbor=0;
            if (forward) {
                if (at+1 < dims[axis]) neighbor=fs[t][p+strides[axis]];
                else if (periods[t]) neighbor=fs[t][p-(dims[axis]-1)*strides[axis]];
                d[t]=neighbor-fs[t][p];
            } else {
                if (at>0) neighbor=fs[t][p-strides[axis]];
                else if (periods[t]) neighbor=fs[t][p+(dims[axis]-1)*strides[axis]];
                d[t]=fs[t][p]-neighbor;
            }
        }
        if (memory_a && (coord[axis_a]<memory_a || coord[axis_a]>=dims[axis_a]-memory_a)) {
            size_t q=compact_index(i,j,k,nx,ny,nz,axis_a,memory_a);
            float b=ca[coord[axis_a]]; pa[q]=b*pa[q]+(b-1)*d[0]; d[0]+=pa[q];
        }
        if (memory_b && (coord[axis_b]<memory_b || coord[axis_b]>=dims[axis_b]-memory_b)) {
            size_t q=compact_index(i,j,k,nx,ny,nz,axis_b,memory_b);
            float b=cb[coord[axis_b]]; pb[q]=b*pb[q]+(b-1)*d[1]; d[1]+=pb[q];
        }
        out[p]=aa[scalar_a?0:p]*out[p]+bb[scalar_b?0:p]*(scale_a*d[0]-scale_b*d[1]);
    }
}
