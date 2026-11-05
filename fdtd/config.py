"""SI inputs. Array positions are zero based; layer stop indices are exclusive."""
from dataclasses import dataclass, field
import math

C0 = 299792458.0
EPS0 = 8.8541878176e-12
MU0 = 1.2566370614e-6
Z0 = math.sqrt(MU0 / EPS0)


@dataclass(frozen=True)
class Layer:
    start: int
    stop: int
    epsilon_r: float
    sigma: float = 0.0  # S/m, never a dimensionless loss parameter


@dataclass
class Config1D:
    name: str
    title: str
    thesis: str
    cells: int = 200
    steps: int = 300
    wavelength: float = 500e-9
    points_per_wavelength: float = 10.0  # in the highest-index material
    dx: float | None = None
    courant: float = 0.5  # c0 dt / dx
    boundary: str = "delay"  # delay, mur, periodic, zero, pec
    source: str = "gaussian"  # gaussian, sine, modulated
    injection: str = "tfsf"  # soft or tfsf
    source_cell: int = 99
    tau_periods: float = 0.5
    layers: list[Layer] = field(default_factory=list)
    loss_model: str = "ohmic"  # centered Ohm update or integral D/E/I
    spectra: bool = False
    snapshots: tuple[int, ...] = (100, 150, 200, 250, 300)
    notes: str = ""


@dataclass
class Config2D:
    name: str
    title: str
    thesis: str
    nx: int = 200
    ny: int = 200
    steps: int = 600
    wavelength: float = 532e-9
    points_per_wavelength: float = 10.0
    dx: float | None = None
    dy: float | None = None
    courant: float = 0.5  # c0 dt / min(dx,dy)
    boundary_x: str = "pml"
    boundary_y: str = "pml"  # pml, periodic, pec, mur
    pml_cells: int = 30
    pml_reflection: float = 1e-8  # continuous-profile design target, not a guarantee
    geometry: str = "free"  # free, layers, slits, mirror, bend
    background_index: float = 1.0
    layers: list[Layer] = field(default_factory=list)  # along y
    source: str = "modulated"
    injection: str = "point"  # point, line, tfsf, beam, diagonal, mode
    source_x: int = 100
    source_y: int = 50
    source_width: float = 60.0  # beam Gaussian radius or finite line length, cells
    angle_deg: float = 0.0  # from +y towards +x
    tau_periods: float = 0.5
    wall_y: int = 80
    wall_thickness: int = 2
    slit_count: int = 1
    slit_width: int = 10  # width of EACH opening, unlike ambiguous MATLAB Ancho
    slit_gap: int = 10  # opaque gap; center separation = slit_width + slit_gap
    detector_y: int | None = None
    average_cycles: int = 8
    spectra: bool = False  # normal plane-wave calibration; periodic transverse x
    snapshots: tuple[int, ...] = (100, 180, 300, 401)
    bend_radius: float = 20e-6
    bend_width: float = 0.775e-6
    bend_core_index: float = 1.9
    notes: str = ""
