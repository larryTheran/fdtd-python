# Numerical methods and interpretation

## Source priority and reproduction policy

The primary source is `Tesis-larry-FDTD (1).pdf` (118 PDF pages). Printed thesis page numbers are 11 lower than PDF page numbers in the experiment chapters: printed p. 42 is PDF p. 53. Chapters 4-6 and their captions define the main experiments. MATLAB files supply otherwise unspecified positions, source shapes and draft variants. Conflicts are recorded in each script's `notes` and in the source audit.

The 532 nm wavelength in the thesis takes precedence for the main optical examples. Explicitly supplemental MATLAB cases retain their stated wavelengths (including 50 GHz, 5 GHz, 700 nm, 10 µm and 1.55 µm). A Gaussian without a carrier is broadband: its `wavelength` parameter sets `fmax=c0/wavelength` and pulse width, not a unique monochromatic wavelength. A `modulated` source adds a carrier at that frequency. Sinusoidal sources use a four-cycle smooth turn-on to reduce abrupt-start transients; the original MATLAB often starts immediately.

Each experiment's final configuration is saved with its results. These implementations reproduce the intended experiments while correcting implementation errors. Exact pixel agreement with the thesis is not claimed. No executable MATLAB/Octave comparison was performed; validation uses the documented equations, analytical solutions and numerical invariants.

## 1D Yee update

The stored fields are `e=Ey/Z0` and `h=Hx`, with relative permeability one. E is sampled at integer z and integer time, H at z+1/2 and time+1/2. With `S=c0*dt/dz`, the lossless update is

```text
h[j] += S * (e[j+1] - e[j])
e[j] += S / epsilon_r[j] * (h[j] - h[j-1])
```

The electric source plane is corrected together with the neighboring staggered magnetic sample for one-way TF/SF injection. A right-moving wave has `h=-sqrt(epsilon_r)*e` in this polarization. Analytical injection is subject to numerical dispersion; reference subtraction removes the source leakage from reflection measurements.

Boundary options are explicit:

- `zero`: the thesis's zero exterior electric/magnetic ghosts. This reflects waves; the two ends impose different staggered field conditions.
- `delay`: the historical three-entry history buffer, used as a two-step propagation delay. Restricted to vacuum endpoints and `S=0.5`. It approximates absorption for resolved pulses; it is not a universally perfect boundary.
- `periodic`: wrap both electric and magnetic differences consistently.
- `pec`: set E=0 at both endpoints.
- `mur`: first-order one-way outgoing E update using the local boundary speed. The unused H plotting ghost is extrapolated, avoiding accumulation of an artificial boundary field.

For Ohmic conductivity, `q=sigma*dt/(2*epsilon0*epsilon_r)`, and

```text
ca = (1-q)/(1+q)
cb = S / (epsilon_r*(1+q))
e_new = ca*e_old + cb*(h[j]-h[j-1])
```

The thesis's printed positive-feedback coefficient in eqs. 4-32/4-34 and Listing 4.5 would amplify a passive material. The numerator must be `1-q`, as already used in some MATLAB revisions. This is the centered, passive conductivity update.

The alternative integral-current update is

```text
D_new = D_old + S*curl(H)
g = sigma*dt/epsilon0
E_new = (D_new - I_old)/(epsilon_r + g)
I_new = I_old + g*E_new
```

TF/SF forcing enters D before computing E. This discretizes the thesis's conductive constitutive relation `epsilon_r*(omega)=epsilon_r + sigma/(i*omega*epsilon0)` using a backward rectangular integral. The positive denominator corrects eqs. 4-42/4-44. It is not a Debye, Drude or Lorentz dispersion model; no such material parameters are provided in the thesis. The rectangular integral differs slightly from the centered Ohmic update and converges toward the same continuum equation as dt decreases.

## Loss units

The 1D loss drafts initially construct an optical time axis, then overwrite `dz=0.01` and `dt=dz/(2*c0)`. Some retain the old Fourier kernel, while others recalculate it against an incompatible frequency axis. Literal translation would label a centimeter-grid microwave waveform as optical.

Experiments 09-11 explicitly use `dx=0.01 m` and rescale the wavelength so the sampled pulse width remains comparable to the intended original waveform. The Ohmic example uses lambda=0.2 m and epsilon_r=4; the integral examples use lambda=`0.01*10*sqrt(1.5)` m and epsilon_r=1.5. Sigma remains in S/m. Experiments 08/12 use consistent optical grids instead and consequently show much less attenuation at the same small conductivity.

## Reflection and transmission

Each spectral run includes a homogeneous reference simulation on the same mesh and time grid. The left monitor lies after the source but before the device; subtracting its complex reference spectrum isolates the reflected field. The transmission monitor uses its own reference spectrum. In homogeneous nonmagnetic lossless exterior media, the power correction is `n_out/n_in`.

The 2D spectrum in experiment 23 uses the spatially uniform, normally incident plane-wave component in a domain periodic along x. This monitor is supported only for x-uniform media with that source; it is not a general diffraction-order or oblique-incidence power decomposition.

Spectra use a real FFT of the complete time records. Fourfold power-of-two padding interpolates frequency samples; it does not improve physical frequency resolution. Frequencies are accepted only where both reference monitor powers exceed 1e-4 of their peaks, and only up to the source frequency parameter. DC and unilluminated bins are marked invalid/NaN. No negative residuals are clipped.

`1-R-T` is a **finite-record spectral residual**. Only after sufficiently long propagation, with well-resolved sources and negligible boundary reflections, can it approximate absorptance. It is not the instantaneous energy stored inside the device. The separate domain-energy curve measures a field-energy proxy. Thin dielectric resonances require long records; experiment 13 runs 64000 steps to bring its maximum lossless spectral residual below about 0.5% over the illuminated band.

## 2D Yee update and PML

The solver uses TMz (`Ez`, `Hx`, `Hy`) on arrays shaped `(nx,ny)`. Displaying `Ez.T` gives conventional x-horizontal/y-vertical figures. This also resolves several swapped x/y labels in the original figures and MATLAB filenames.

Berenger split-field PML is used throughout, with separate E components driven by `+dHy/dx` and `-dHx/dy`. Hx is driven by `-dEz/dy`, Hy by `+dEz/dx`. Directional electric and magnetic damping rates are matched and evaluated at their respective Yee positions. The loss profile is cubic, with a continuous-profile target reflection of 1e-8 by default; that target is not a measured guarantee. The reference Ohner PDF, section 4.3 (printed pp. 23-25), also describes split-field PML; its opposite polarization is related by electromagnetic duality.

The general stability check is `c0*dt*sqrt(dx^-2+dy^-2)/n_min <= 1`. Both grid spacings enter the derivatives. Axis-specific periodic boundaries wrap both staggered curls. PML lies inside the stated grid dimensions and ends at PEC outer edges. Beam and finite-line sources are tapered outside the x PML. The plane TF/SF source requires uniform lossless material at the source plane and periodic transverse x boundaries.

The refraction supplement uses first-order Mur, not an exact translation of the incomplete higher-order ABC draft. PML is preferable for the main oblique-incidence experiments. Split-field PML performance depends on resolution, incidence and material geometry; the bend supplement is not an independently converged PML/mode-transmission benchmark.

## Slit diffraction

An exact E=0 PEC mask models the opaque screen, avoiding an enormous numerical permittivity or conductivity. Each opening's cell count is explicit; `slit_gap` is the opaque gap, so center separation is `slit_width + slit_gap`. The screen is two cells thick by default. `detector_y` is an absolute row, and reported L is measured from the screen's exit face.

The default small-domain examples use periodic transverse boundaries, matching the thesis setup. This represents repeated apertures, and late-time fields can include neighboring-period contributions. The extended single-slit example uses PML on all four sides to reduce this effect. PML cells are excluded from plotted detector comparisons.

The detector saves its full time record, final-step squared field, and mean squared field over the final eight source cycles. Instantaneous E² can have phase-dependent oscillations that are not stationary irradiance fringes. The analytical guide is

```text
single: sinc(b*sin(theta)/lambda)^2
double: sinc(b*sin(theta)/lambda)^2 * cos(pi*d*sin(theta)/lambda)^2
theta = atan(x/L)
```

Here NumPy's sinc includes pi, and d is center separation. The thesis eq. 6-2 omits the sinc denominator. This guide assumes far-field uniform aperture illumination; a wavelength-sized, finite-thickness PEC slit and near-field detector need not reproduce it exactly.

Fresnel numbers are reported for both an individual slit and the entire illuminated aperture. For b=10, gap=10, lambda=10 cells and L=15, the complete aperture has F=6, despite the thesis caption calling it Fraunhofer. The b=5/L=100 prose case and b=10/L=5 or 15 caption cases are separate scripts. The far single-slit domain uses a documented L=300-cell choice because the thesis does not state an exact L for that final figure.

The root `FDTD2D.m` is included separately at 700 nm and dx=41.17 nm, with epsilon_r=2 outside the obstacle. Its half-integer MATLAB thresholds are translated to the actual integer-sampled openings. This case is rotated into the same +y propagation convention as the others.

## Refraction and reflection

Material indices become `epsilon_r=n^2`. A finite Gaussian-weighted phased source produces a beam with a requested incidence angle measured from the +y interface normal. Source frequency is `c0/lambda0`; it does not acquire an extra index/Courant factor as in the drafts. Main optical cases use a finer grid to resolve the highest-index material.

Snell predictions use `n1*sin(theta1)=n2*sin(theta2)`. Increasing the second index bends the ray **toward** the normal; the inequalities in the prose on printed p. 93 are reversed. Local phasor gradients provide measured-angle diagnostics, affected by finite beam width, reflections and discretization. No angle is fitted to the thesis's reported values.

For n1=1.5, n2=2.1 and theta1=40 degrees, Snell predicts 27.331 degrees. For n2=4 it predicts about 13.948 degrees and nonzero transmitted power, not total reflection. A separate PEC wall supplies the intended ideal specular reflector. Three parallel regions n=1.5/2.5/1.5 restore the outgoing angle to the incoming angle in the geometrical-optics limit.

## Unfinished supplemental code

`Untitled8.m` requires an absent `ezmode` function and references undefined spatial/time coordinates. Experiment 38 reconstructs its intended 20 µm-radius bend using a 1D scalar eigenvalue calculation for the effective index, followed by a 2D guided-mode source. It retains the 1.55 µm wavelength, 0.775 µm width and stated core/substrate indices. It is a supplemental approximation, not a full 3D waveguide solution or a validated coupling-efficiency calculation.

`interfaz1D.m` is an empty GUIDE callback scaffold. The independent scripts expose simulation controls through Python configuration and CLI arguments; the original GUI itself is not recreated.

## Supporting references

- Larry Theran Suarez, local `Tesis-larry-FDTD (1).pdf`, chapters 4-6.
- Gernot Ohner, local `Ohner_FDTD_Bachelorarbeit_final.pdf`, chapter 4 (split-field PML and grading).
- John B. Schneider, [Understanding the FDTD Method](https://eecs.wsu.edu/~schneidj/ufdtd/ufdtd.pdf), loss terms, numerical dispersion, sources and absorbing boundaries.
- Richard Fitzpatrick, [Single-Slit Diffraction](https://farside.ph.utexas.edu/teaching/315/Waveshtml/node96.html), sinc-squared far-field aperture pattern.
- OpenStax, [Total Internal Reflection](https://openstax.org/books/university-physics-volume-3/pages/1-4-total-internal-reflection), index ordering and critical angle.
