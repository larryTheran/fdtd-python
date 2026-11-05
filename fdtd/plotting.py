"""Static figures and bounded-size GIF animations; no GUI needed for saving."""
from pathlib import Path
import numpy as np
from .analysis import diffraction


def _style():
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False,
                         "axes.spines.right": False, "figure.dpi": 110,
                         "savefig.dpi": 160, "axes.titleweight": "bold"})
    return plt


def overlay(ax, c, r):
    from matplotlib.patches import Rectangle
    if c.geometry in {"slits", "mirror"}:
        ax.contour(r["pec"].T, levels=[.5], colors=["#242424"], linewidths=.8)
    if np.ptp(r["epsilon_r"]) > 0:
        levels = (np.unique(r["epsilon_r"])[1:]+np.unique(r["epsilon_r"])[:-1])/2
        ax.contour(r["epsilon_r"].T, levels=levels, colors="#273d45", linewidths=.8, linestyles="--")
    for b, axis, size in [(c.boundary_x, 0, c.nx), (c.boundary_y, 1, c.ny)]:
        if b != "pml":
            continue
        for start in [0, size-1-c.pml_cells]:
            xy = (start, 0) if axis == 0 else (0, start)
            w, h = (c.pml_cells, c.ny-1) if axis == 0 else (c.nx-1, c.pml_cells)
            ax.add_patch(Rectangle(xy, w, h, color="#687f8b", alpha=.14, linewidth=0))
    if c.detector_y is not None:
        ax.axhline(c.detector_y, color="#108577", lw=.8, ls=":")
    ax.set(xlabel="x (cell)", ylabel="y (cell)")


def figures(c, r, output, show=False):
    plt = _style()
    paths = []
    def save(fig, name):
        path = output/name
        fig.savefig(path, bbox_inches="tight")
        paths.append(path)
        if not show:
            plt.close(fig)
    one = r["e"].ndim == 1
    count = len(r["snapshots"])
    if one:
        fig, axes = plt.subplots(count, 1, figsize=(10, 2*count), sharex=True, layout="constrained", squeeze=False)
        limit = max(1.1, np.max(np.abs(r["snapshots"]))*1.1)
        for ax, e, h, step in zip(axes[:, 0], r["snapshots"], r["magnetic_snapshots"], r["snapshot_steps"]):
            for k, layer in enumerate(c.layers):
                ax.axvspan(layer.start, layer.stop, color=["#87c9aa", "#f0d488"][k % 2], alpha=.4)
            ax.plot(e, color="#c84452", lw=1.25, label="E / Z0")
            ax.plot(np.arange(c.cells)+.5, h, color="#2875ae", lw=1.1, label="H (half step)")
            ax.set(ylabel="Normalized field", title=f"Step {step}", ylim=(-limit, limit), xlim=(0, c.cells-1))
            ax.grid(alpha=.12)
        axes[0, 0].legend(loc="upper right", ncol=2)
        axes[-1, 0].set_xlabel("z (cell)")
        fig.suptitle(f"{c.title}\n{c.thesis}", fontsize=13)
        save(fig, "fields.png")
        fig, axes = plt.subplots(1, 2, figsize=(11, 3.5), layout="constrained")
        axes[0].plot(r["epsilon_r"], color="#147c6b")
        axes[0].set(xlabel="z (cell)", ylabel="Relative permittivity", title="Material profile")
        axes[1].plot(1/np.sqrt(r["epsilon_r"]), color="#2866a1")
        axes[1].set(xlabel="z (cell)", ylabel="v / c0", title="Lossless phase-speed reference")
        save(fig, "materials.png")
    else:
        cols = min(3, count)
        rows = (count+cols-1)//cols
        fig, axes = plt.subplots(rows, cols, figsize=(4*cols, 4*rows), squeeze=False, layout="constrained")
        lim = max(np.max(np.abs(r["snapshots"])), 1e-12)
        for ax, e, step in zip(axes.flat, r["snapshots"], r["snapshot_steps"]):
            im = ax.imshow(e.T, origin="lower", cmap="RdBu_r", vmin=-lim, vmax=lim, interpolation="nearest")
            overlay(ax, c, r)
            ax.set_title(f"Step {step}")
        for ax in list(axes.flat)[count:]:
            ax.set_visible(False)
        fig.colorbar(im, ax=list(axes.flat)[:count], shrink=.7, label="Ez / Z0")
        fig.suptitle(f"{c.title}\n{c.thesis}", fontsize=13)
        save(fig, "fields.png")
        fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), layout="constrained")
        im = axes[0].imshow(r["epsilon_r"].T, origin="lower", cmap="viridis", interpolation="nearest")
        overlay(axes[0], c, r)
        axes[0].set_title("Relative permittivity / PEC walls")
        fig.colorbar(im, ax=axes[0], shrink=.7)
        im = axes[1].imshow(r["mean_square"].T, origin="lower", cmap="magma", interpolation="nearest")
        overlay(axes[1], c, r)
        axes[1].set_title(f"Mean squared field, last {r['average_steps']} steps")
        fig.colorbar(im, ax=axes[1], shrink=.7, label="Mean (Ez / Z0)^2")
        save(fig, "materials_and_intensity.png")
        if "detector" in r:
            fig, axes = plt.subplots(1, 2, figsize=(11, 3.7), layout="constrained")
            intensity = r["detector_mean_square"]
            x = np.arange(c.nx)-(c.nx-1)/2
            interior = slice(c.pml_cells+1, -c.pml_cells-1) if c.boundary_x == "pml" else slice(None)
            axes[0].plot(x[interior], intensity[interior], color="#2875ae", label="Time averaged")
            axes[0].plot(x[interior], r["detector"][-1, interior]**2, color="#a1adb8", alpha=.7, label="Last-step square")
            axes[0].set(xlabel="x offset (cell)", ylabel="Squared normalized field", title="Detector signal")
            axes[0].legend()
            axes[1].plot(x[interior], intensity[interior]/max(intensity.max(), 1e-300), label="FDTD", color="#2875ae")
            if c.geometry == "slits":
                distance = (c.detector_y-c.wall_y-c.wall_thickness+1)*r["dy"]
                curve = diffraction(x*r["dx"], c.slit_width*r["dx"], c.wavelength/c.background_index,
                                    distance, c.slit_count, (c.slit_width+c.slit_gap)*r["dx"])
                axes[1].plot(x[interior], curve[interior], "--", label="Fraunhofer aperture approximation", color="#c57a26")
            axes[1].set(xlabel="x offset (cell)", ylabel="Peak-normalized intensity", title="Pattern comparison")
            axes[1].legend(fontsize=8)
            save(fig, "detector.png")
    if "frequency" in r:
        fig, ax = plt.subplots(figsize=(9, 4), layout="constrained")
        scale = 1e12 if r["frequency"].max() > 1e12 else 1e9
        valid = r["spectral_valid"]
        f = r["frequency"][valid]/scale
        for key, label, color, ls in [("reflectance", "R", "#c84452", "-"),
            ("transmittance", "T", "#2875ae", "-"), ("residual", "1 - R - T", "#18816b", "-")]:
            ax.plot(f, r[key][valid], label=label, color=color, ls=ls)
        ax.plot(f, (r["reflectance"]+r["transmittance"])[valid], "k:", label="R + T")
        ax.set(xlabel=f"Frequency ({'THz' if scale == 1e12 else 'GHz'})", ylabel="Power ratio",
               title="Reference-normalized spectra (finite time record)")
        ax.legend(ncol=4)
        ax.grid(alpha=.2)
        save(fig, "spectra.png")
    fig, ax = plt.subplots(figsize=(8, 3.5), layout="constrained")
    ax.plot(np.arange(1, c.steps+1), r["energy"]/max(r["energy"].max(), 1e-300), color="#18816b")
    ax.set(xlabel="Time step", ylabel="Energy proxy / peak", title="Domain field energy (includes PML cells)")
    ax.grid(alpha=.2)
    save(fig, "energy.png")
    if show:
        plt.show()
    return paths


def animation(c, r, output):
    plt = _style()
    from matplotlib.animation import FuncAnimation, PillowWriter
    fig, ax = plt.subplots(figsize=(7, 4.5), layout="constrained")
    lim = max(np.max(np.abs(r["frames"])), 1e-12)
    if r["e"].ndim == 1:
        artist, = ax.plot(r["frames"][0], color="#c84452")
        ax.set(xlim=(0, c.cells-1), ylim=(-1.05*lim, 1.05*lim), xlabel="z (cell)", ylabel="E / Z0")
        for layer in c.layers:
            ax.axvspan(layer.start, layer.stop, color="#87c9aa", alpha=.3)
    else:
        artist = ax.imshow(r["frames"][0].T, origin="lower", cmap="RdBu_r", vmin=-lim, vmax=lim)
        overlay(ax, c, r)
        fig.colorbar(artist, ax=ax, label="Ez / Z0")
    def update(k):
        if r["e"].ndim == 1:
            artist.set_ydata(r["frames"][k])
        else:
            artist.set_data(r["frames"][k].T)
        ax.set_title(f"{c.title}\nStep {r['frame_steps'][k]}")
        return artist,
    anim = FuncAnimation(fig, update, frames=len(r["frames"]), interval=60)
    path = Path(output)/"animation.gif"
    anim.save(path, writer=PillowWriter(fps=16), dpi=95)
    plt.close(fig)
    return path
