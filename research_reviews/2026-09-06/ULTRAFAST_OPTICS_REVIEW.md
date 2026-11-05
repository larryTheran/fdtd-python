# Ultrafast optics: recent research and a publication route using FDTD

Prepared 6 September 2026. This focused review selects 2024–2026 primary research relevant to ultrafast pulse control, time-dependent optical materials and the existing Python FDTD code. It separates published findings, access limitations, and proposed research. A proposed gap is not proof that the problem has never been studied.

**Recommendation:** begin with a computational study of the observability of time-varying material dynamics in finite-film pump–probe experiments. The aim is to determine which predictions survive realistic pulse duration, loss, interfaces and measurement uncertainty, and which measurements could distinguish the surviving model classes. This offers a 1D entry point, a recent independent FDTD benchmark, and a meaningful route into 2D ultrafast experiments.

For a device-oriented paper, the next choices are pulse-quality-aware all-optical switching or broadband THz emission with an explicitly optimized collected waveform. These require substantially more physics and computational development.

## 1. What recent papers establish

| ID | Recent paper and evidence | What it contributes | Consequence for our proposal |
|---|---|---|---|
| U1 | Tanaka et al., **2025**, Advanced Optical Materials. [Femtosecond shaping with silicon Huygens metasurfaces](https://advanced.onlinelibrary.wiley.com/doi/10.1002/adom.202500135). Main text inspected. | A metasurface placed in a spectrally dispersed Fourier-plane setup reshapes pulses. Measured examples stretch 229 fs pulses to 489 fs and split them by 524 fs. | Static amplitude/phase pulse shaping is an excellent benchmark, but splitting or stretching a pulse is established. The system includes a Fourier optical arrangement; it is not just a uniform slab traversed by a pulse. |
| U2 | Harwood et al., **2025**, Nature Communications. [Space-time diffraction from synthetic motion](https://www.nature.com/articles/s41467-025-60159-9). Main text and methods inspected. | Demonstrates angle–frequency diffraction using optically modulated ITO. Methods include a 40 nm ITO film with gold, oblique beams, a time-dependent effective-mass Drude description and a finite temporal response kernel. | Material memory, finite response and space-time beam geometry are already present in relevant experimental modeling. We must quantify a further observable or failure regime, not simply add a rise time. |
| U3 | Jaffray et al., **2025**, Nature Photonics. [Spatio-spectral optical fission](https://www.nature.com/articles/s41566-025-01640-1). Abstract and indexed main-text sections inspected. | Reports spatial and spectral separation of an ultrafast pulse in a pumped AZO film; representative pulses are 93 fs at 1300 nm in a 900 nm film. | A scalar transmitted spectrum alone can miss where the converted light goes. This motivates joint spatial, spectral and temporal detection in later stages. |
| U4 | Deng et al., **2025**, Advanced Optical Materials. [THz amplification at a Huygens time boundary](https://advanced.onlinelibrary.wiley.com/doi/abs/10.1002/adom.202402052). Publisher abstract inspected. | Uses photoexcited carrier dynamics to alter resonances and reports frequency-selective transmitted intensity enhancement up to about 20%. | Spectral enhancement is already demonstrated. It must not be equated automatically with integrated pulse-energy gain, and the pump/material energy exchange must be accounted for. |
| U5 | Garg et al., **2025**, Advanced Optical Materials. [Inverse-designed dispersive time-varying nanostructures](https://advanced.onlinelibrary.wiley.com/doi/10.1002/adom.202402444). Methods inspected. | Develops a differentiable T-matrix approach optimizing periodic carrier-density modulation for dispersive structures, with dipole-decay and asymmetric-transmission examples. | Inverse design plus time modulation plus dispersion is already prior art. Realistic pump constraints and a new measurable function are needed. |
| U6 | Dixon et al., **2026**, Journal of Optics. [Time-varying Drude–Lorentz scattering](https://doi.org/10.1088/2040-8986/ae4bf2). [Author manuscript](https://arxiv.org/html/2511.19322v1) inspected; publication confirmed by the institutional code record. | Compares four material-dynamics models using analytical temporal scattering and custom FDTD. Their differing predictions show that specifying initial/final permittivities is insufficient. | This is the closest theoretical prior art and our first benchmark. A new paper must extend the physical question, not reproduce its model comparison under another name. |
| U7 | Tonkaev et al., **2025**, Nature Communications. [High-harmonic generation in resonant membranes](https://www.nature.com/articles/s41467-025-67871-6). Main-text sections inspected. | Finds unconventional nonlinear intensity dependencies in resonant membranes and explicitly studies coupling between pulse duration and resonant lifetime. | “Find the optimal Q for a short pulse” is too broad to claim as new. Strong-field HHG also cannot be established by adding only a simple Kerr coefficient to our solver. |
| U8 | Hail, Michaeli & Atwater, **2026**, Nature Nanotechnology. [Ultrafast all-optical beam steering](https://www.nature.com/articles/s41565-026-02199-w). Publisher abstract and publication metadata inspected. | Reports pulse-limited steering with a 74 fs response and angles up to ±13°, using resonantly enhanced Kerr effects with a slower free-carrier contribution. | A fast steering demonstration alone would duplicate the main concept. Pulse quality, residual carrier memory and practical pump shaping are more specific candidate questions. Full text remains to be inspected before selecting a close device adaptation. |
| U9 | Segal et al., **2026**, Physical Review Research. [Subcycle time refraction](https://journals.aps.org/prresearch/abstract/10.1103/zvs7-9vgn). Publisher abstract/indexed sections inspected. | Reports enhanced time-refraction frequency shifts as modulation is shortened into the subcycle regime. | Switching time must be compared with the probe optical period, not labeled ultrafast solely because it is measured in femtoseconds. Time refraction is not evidence of an observed optical time-reflected wave. |
| U10 | Peters et al., **2024**, Advanced Optical Materials. [All-dielectric metasurfaces for THz pulse generation](https://advanced.onlinelibrary.wiley.com/doi/10.1002/adom.202303148). Results and methods inspected. | Fabricated AlGaAs resonators exploit optical rectification, with reported emission enhancement and control of amplitude and phase through geometry and pump wavelength. | THz generation and geometric waveform control are already established; optimize a specified collected THz waveform and bandwidth if pursuing an emitter paper. |
| U11 | Akturk et al., **2026 preprint**, submitted 31 July. [Spatiotemporal metasurface for all-optical wavefront shaping](https://arxiv.org/abs/2608.00308). Abstract inspected. | Reports subpicosecond transient defocusing from a spatially nonuniform optical excitation of a semiconductor nanowire metasurface. | An additional close novelty check for pumped spatial gradients. It remains preprint evidence in this review; no journal publication was verified. |

The relevant frontier is not just faster switching. It is predicting and controlling a broadband field when the optical response changes during the pulse. The reviewed literature already includes dispersion, finite response and inverse design in different settings. The remaining opportunity must therefore be stated as a specific physical or measurement question.

## 2. Recommended problem: which material dynamics can a pulse measurement identify?

**Working title:** *Observability of time-varying dispersive dynamics in finite-film pump–probe scattering.*

**Research question:** when candidate dynamical models agree with the same equilibrium optical data, do their predicted differences remain distinguishable after finite pump rise time, film interfaces, damping, probe bandwidth, detector averaging and uncertain pump calibration are included?

**Hypothesis:** some large differences in ideal temporal-boundary calculations disappear after realistic averaging or can be mimicked by changes in film thickness, damping or pump delay. Other differences may survive in a complex reflected/transmitted waveform or an angle-resolved spectrum. The result would identify where a measurement can constrain dynamics and where it cannot.

Our proposed contribution is an **observability map and measurement-design procedure with quantified uncertainty**, rather than the existence of model-dependent scattering. U6 already raises experimental distinguishability. The extension would need to show, quantitatively, how finite geometry and nuisance parameters determine discrimination and how a feasible measurement improves it. No claim of firstness is justified by this search alone.

There is a crucial identifiability limit: U6's current-density and effective-mass models coincide in the pure Drude limit under the same parameter histories. They must be treated as one observable class there. Electromagnetic data cannot identify a microscopic mechanism when competing models give identical dynamics. [Model equations and equivalence](https://arxiv.org/html/2511.19322v1).

### Stage 1: independent 1D benchmark

Reproduce selected analytical temporal-boundary coefficients, then compare with the authors' [public Python FDTD and plotting code](https://doi.org/10.24378/exe.31399617). The repository lists separate implementations of the four models and a plotting notebook. This review verified its availability, not its execution. Preserve attribution and the repository license when using it.

Use periodic bulk tests to validate the temporal-scattering mathematics separately from spatially bounded-film tests. Add static dispersive slabs and compare their complex reflection/transmission against a transfer-matrix calculation. Check material-only ODE solutions against a separate numerical integrator.

A normal-incidence 1D film is a tractable test of dispersive dynamics and interfaces. It is **not** a reproduction of the oblique, p-polarized ENZ enhancement used in many pump–probe measurements.

### Stage 2: a finite, experimentally motivated film

Select one sample family rather than treating ITO, AZO, silicon and AlGaAs as interchangeable. A provisional near-infrared TCO study can use an equilibrium Drude–Lorentz fit consistent with that sample's measured complex permittivity. Film thickness and pump range must come from the chosen paper or collaborator; the 40 nm ITO and 900 nm AZO examples in U2/U3 are distinct samples, not endpoints of a universal material model.

Replace ideal discontinuities with causal pump-driven histories. Separate changes in carrier population, effective mass, damping and bound-electron response according to the mechanism being tested. Bound pump amplitudes and relaxation times to experimental evidence. Do not optimize an arbitrary permittivity waveform and call it a realizable pump.

Use dimensionless controls to organize the study: rise time divided by optical period, probe duration divided by optical period, film thickness divided by wavelength, damping divided by optical frequency, and normalized modulation strength. A two-femtosecond change near 1300 nm is a very different regime from a hundred-femtosecond change; the shortest cases should be treated as stress tests unless a measured mechanism supports them.

### Stage 3: design an informative measurement

Compare progressively richer observables: spectral intensity; both reflection and transmission; retrieved complex temporal fields; and, after the 2D extension, angle-resolved spectra. Propagate detector bandwidth, finite collection angle and a specified noise model through the simulated measurement. Treat timing zero, film thickness and calibrated pump strength as nuisance parameters rather than assuming them perfectly known.

A useful comparison is the minimum noise-weighted distance between competing model predictions after refitting nuisance parameters:

\[
D_{ab}=\min_{\eta_a,\eta_b}\left\|C_n^{-1/2}\left[y_a(\eta_a)-y_b(\eta_b)\right]\right\|_2.
\]

Here the parameter ranges must be restricted by independent calibration; unconstrained refitting could erase meaningful distinctions or invent unrealistic fits. This distance is a screening metric, not automatically a statistical confidence level. Establish decision thresholds using simulated noise and held-out data, with a clearly specified inference method.

Optimize a small set of controllable probe parameters—duration, chirp, delay and, later, angle—to improve discrimination at fixed incident energy and detector resources. Compare against a conventional transform-limited single-probe protocol. If using two pulses, fix total probe energy and account for coherence and timing uncertainty. This is the proposed measurement-design step; it is not a published result.

### What would constitute a publishable result?

The strongest outcome would combine independent benchmarks, a realistic film model, a quantitative region of model distinguishability, and a practicable probe design that improves robustness. A carefully established non-identifiability result can also be valuable if it shows why a commonly used observable cannot determine the claimed dynamics and identifies what additional measurement is required.

The study should stop or change direction if every apparent distinction is smaller than numerical or calibration uncertainty, or if it merely reproduces U6's ideal coefficients. A noisy parameter sweep without a clear physical explanation would not be enough.

**Proposed figures:** benchmark coefficients and convergence; finite-film pulse evolution; effects of rise time and loss; nuisance-parameter degeneracy; observability maps for different detectors; optimized versus baseline probe protocols; and an independent experimental or solver comparison.

## 3. Device-oriented alternatives

| Direction | Concrete candidate problem | Relation to recent work | Necessary development |
|---|---|---|---|
| Pulse-quality-aware all-optical deflector | At fixed pump energy and required deflection, minimize the temporal pedestal and waveform error of the selected output beam while accounting for Kerr response, carrier memory and finite illumination. | U8/U11 establish very fast spatial control; U7 already treats lifetime/pulse coupling. A new result needs a joint speed–energy–fidelity constraint and realistic carrier dynamics. | Dispersive nonlinear polarization, carrier rate equations, finite-beam pumping, mode/angle-resolved pulse extraction, and eventual 3D metasurface validation. |
| Broadband THz emitter optimized for collected waveform | Can joint pump-resonance and THz outcoupling design improve the energy collected within a specified numerical aperture and usable bandwidth without lengthening the emitted pulse excessively? | U10 already controls emission via geometry; U4 already demonstrates time-boundary THz enhancement. A local-field or peak-spectrum improvement alone is insufficient. | Tensor second-order nonlinearity, realistic optical and THz dispersion/loss, pump normalization, 3D radiation and a validated multiscale calculation. |

The THz direction directly joins antenna radiation concepts with ultrafast excitation. In the weak-conversion regime, an efficient route is to calculate the optical pump field locally, derive its nonlinear polarization source, then propagate the THz field on an appropriate grid. Validate that separation against a smaller coupled calculation. One enormous grid resolving optical nanostructures over a macroscopic THz radiation volume is usually a poor starting strategy.

Static pulse shaping based on U1 is a useful training and verification project. It can validate spectral phase, pulse reconstruction and later fabrication tolerances, but the cited pulse-splitting/stretcher functions are not new publication objectives by themselves.

## 4. Essential changes to our FDTD implementation

The present code models static relative permittivity and Ohmic conductivity. It does not contain Drude/Lorentz polarization memory, pump-driven material changes, nonlinear susceptibilities, calibrated pump fluence or a carrier model. A Gaussian optical source alone does not provide those capabilities.

| Change | Requirement for credible results |
|---|---|
| Auxiliary differential equations for material polarization/current | Fit causal equilibrium dispersion and integrate the specific time-dependent microscopic model, with its own continuity and energy relations. |
| Displacement-field formulation | Update Maxwell's equations consistently while material parameters change; do not substitute a time-dependent index into the existing static coefficients without deriving the update. |
| TEz polarization in 2D: Ex, Ey, Hz | With the incidence plane in x–y and a film normal along y, p-polarized ENZ excitation needs an in-plane electric field, including its normal component. The current Ez, Hx, Hy solver supplies the other polarization. |
| Validated oblique pulse injection and general scattering monitors | The existing normal plane-wave spectrum routine cannot measure general angle/frequency conversion. |
| Physical units and energy accounting | Convert normalized field amplitudes consistently to SI for pump intensity, nonlinear polarization and carrier excitation. Include dispersive material energy, dissipation and modulation work. |
| Nonlinear and carrier dynamics, for the device branches | Distinguish prescribed weak-probe modulation from a self-consistent pump–probe calculation; add thermal accumulation only where the experimental repetition rate warrants it. |

For a time-varying medium, output frequencies mix and energy can be exchanged with the modulator. The current stationary `1-R-T` residual cannot be used unchanged as absorptance or gain. Compare integrated fluxes and material/modulation energy budgets. Benchmark the pump-off case first, then the temporal modulation, then spatial complexity.

Published strong-field HHG, exciton coherence or quantum-light generation requires additional constitutive or quantum dynamics beyond this classical teaching solver. These can be long-term applications, but they are not the most direct first paper from the current code.

**Recommended next action:** establish static dispersive slab tests and reproduce one U6 benchmark in 1D. Then determine whether finite-film observables retain enough model sensitivity to justify the 2D p-polarized extension. This provides a concrete early decision before attempting a complex metasurface device.

See [STARTER_PLAN.md](STARTER_PLAN.md) for milestones and [paper_catalog.csv](paper_catalog.csv) for all publication/access details.
