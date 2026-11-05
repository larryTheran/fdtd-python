# From literature review to the first research result

This is an implementation proposal, not a record of completed research. Start one lead project at a time. Keep the existing 38 teaching examples as regression checks and place research models in separate modules.

## Shared first steps

1. Choose a material/sample or a feed/lens geometry whose dimensions and equilibrium properties are accessible. Record the exact paper version and parameter sources.
2. Add calibrated broadband probes and consistent field/flux normalization. Store complex transfer functions, not only squared amplitudes.
3. Add static Drude/Lorentz or other appropriate causal dispersion where the sample requires it. Verify material response separately and slab scattering against independent theory.
4. Establish numerical error in the actual proposed observable. For an optimization study, this error must be smaller than the design improvement; for model discrimination it must be smaller than the differences being interpreted.

## Antenna project milestones

| Milestone | Deliverable | Proceed only when |
|---|---|---|
| A0: baseline physics | Broadband 2D aperture/lens, with and without a cover; field waveforms and gated flux. | Source contamination, boundary reflection and mesh error are quantified. |
| A1: design comparison | Matched-aperture geometric, power-optimized and waveform-aware designs. | All designs use the same physical and loss constraints; ideal TTD is labeled as an upper benchmark. |
| A2: hold-out study | Pulse-family, focal-position and cover-parameter tests excluded from optimization. | Any improvement persists beyond numerical uncertainty and does not merely trade away most received energy. |
| A3: finite antenna | A realizable feed and finite 3D lens/metasurface, independently checked. | 2D conclusions survive finite aperture, polarization and feed effects. |
| A4: publication evidence | Measured transfer functions or pulse data, or a strong independently validated computational result with a general design rule. | The contribution remains distinct from A1/A2/A8 and related newer work. |

The initial experiments can be named `antenna_01_aperture_baseline`, `antenna_02_cover`, `antenna_03_geometric_lens`, `antenna_04_power_objective`, and `antenna_05_waveform_objective`. These names describe proposed future files; they have not been implemented.

## Ultrafast project milestones

| Milestone | Deliverable | Proceed only when |
|---|---|---|
| U0: static dispersion | Material ODE and dispersive slab verification. | Complex amplitude/phase and loss agree with independent calculations. |
| U1: temporal benchmark | Reproduction of selected Dixon et al. coefficients and comparison with their published Python code. | The intended constitutive model and temporal continuity conditions are explicit; numerical convergence is shown. |
| U2: finite-film problem | Finite pulse, finite rise time, damping and interfaces, with a physically motivated modulation history. | Results are not dominated by abrupt-switch artifacts or an inconsistent energy budget. |
| U3: observability | Candidate-model fits including timing, damping, thickness and pump uncertainty. | Equivalently evolving models are grouped, and discrimination thresholds are calibrated rather than assumed. |
| U4: informative probe | A feasible probe/detector protocol compared at fixed energy and resources. | Improvement persists on held-out noise and material conditions; otherwise document a meaningful identifiability limit. |
| U5: oblique extension | TEz p-polarized finite-film study and independent comparison. | Source injection, ENZ interface resolution and angular spectra are validated. |

Proposed future files: `optics_01_static_drude_slab`, `optics_02_temporal_interface`, `optics_03_finite_pump_film`, `optics_04_model_observability`, and `optics_05_probe_design`. The first three establish physical validity; the last two address the proposed new question.

## Computational scope

Benchmark actual runtime before committing to large sweeps. A 1000 × 1000 2D mesh with 10000 steps entails 10^10 cell updates. A 200 × 200 × 200 3D grid contains eight million cells; six float64 field arrays alone occupy about 384 MB, before material states, PML, coefficients and outputs. These are arithmetic sizing examples, not measurements of the current implementation.

Optical nanometer films under wide beams can demand a fine transverse mesh far beyond the present examples. Use 1D studies first, then a carefully bounded 2D domain; validate any subgridding, surface model or domain decomposition before relying on it. For macroscopic antenna apertures or optical-to-THz emission, combine validated local FDTD with suitable propagation or circuit models rather than forcing every length and time scale onto one uniform grid.

## Conditions for writing the paper

Before preparing a manuscript, require a frozen baseline; a reproducible parameter dataset; numerical and model error bounds; an independently verified result; a clear explanation of why the new objective or observable changes the conclusion; and a final forward-citation search of the closest papers. The review is a starting map, not a guarantee of priority or acceptance.

Experimental access will determine the final emphasis. RF fabrication and VNA access favor the antenna route. A pump–probe collaborator with characterized films favors the optical route. For simulation-only work, the optical benchmark and observability study are the first recommendation, provided they yield a useful general result rather than a parameter sweep alone.
