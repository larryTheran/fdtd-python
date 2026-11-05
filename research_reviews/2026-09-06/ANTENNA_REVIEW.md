# Antenna design: recent research and a publication route using FDTD

Prepared 6 September 2026. Focused review of 2024–2026 primary research, selected for relevance to antenna design and the existing Python solver. This is a research-planning review, not an exhaustive systematic review. Proposed gaps are inferences from the inspected literature, not certified claims of priority. Access limitations are recorded in [paper_catalog.csv](paper_catalog.csv).

**Recommendation:** investigate pulse-preserving near-field focusing through a dielectric cover, with a physically realizable antenna–lens or antenna–metasurface design. The central question should be whether optimizing the complete received waveform over a focal region changes the design selected by conventional frequency-domain gain criteria. This has a manageable 2D starting point and a clear path to an antenna experiment. A second, more demanding direction is transient beam switching with realistic device dynamics.

## 1. What recent papers establish

The selected work spans three connected areas: ultrawideband pulse radiation, wideband near-field focusing, and reconfigurable metasurface antennas. These are particularly relevant because they involve spatially dependent spectral phase, resonant memory, and radiation into finite observation regions.

| ID | Recent paper and evidence | What it contributes | Consequence for our proposal |
|---|---|---|---|
| A1 | Lee, Raman & Augustine, **2024**, IEEE Access. [Pulse-oriented antipodal Vivaldi design](https://doi.org/10.1109/ACCESS.2024.3432853). Institutional abstract inspected. | Optimizes a short-pulse radiation metric and assesses transfer functions, group delay, received pulses and imaging. The reported matched range extends from 1.8 to beyond 10 GHz. | Pulse-based antenna optimization is already established. A new Vivaldi shape with an extra fidelity plot is a weak novelty claim. |
| A2 | S. Lee et al., **2025**, IEEE Sensors Journal. [Wideband fan-beam lens antenna for IR-UWB radar](https://ksp.etri.re.kr/ksp/article/read?id=70679). Institutional abstract inspected. | Combines a Vivaldi radiator with dielectric/air lens layers over 1–8 GHz; reports fidelity above 0.93 and experimental radar evaluation. | A lens that increases directivity while preserving pulses is also prior art. We need a different question and matched baselines. |
| A3 | Wu et al., **2024**, Nature Communications. [Synthetic moving-envelope metasurface antenna](https://www.nature.com/articles/s41467-024-51587-0). Main text inspected. | Demonstrates programmable harmonic generation and radiation using switched waveguide slots. A representative experiment uses a 22.5 GHz carrier and 10 kHz envelope modulation. | Harmonic synthesis itself is not new. The huge carrier/modulation timescale separation also makes a brute-force full-device FDTD reproduction unattractive. |
| A4 | Carlson et al., **2025 author manuscript**. [Wideband DMA performance with practical design characteristics](https://arxiv.org/html/2510.07827v1). Main text inspected. | Includes waveguide attenuation, frequency-selective resonators and restricted tuning in a communication model and proposes a configuration algorithm. | We cannot claim to be first to include practical DMA dispersion or loss. A potential extension is an independently verified finite-aperture waveform model and a different design objective. Final journal metadata were not independently accessed. |
| A5 | M. Wang et al., **2025**, Nature Communications. [Frequency-comb-steered quasi-TTD beamformer](https://www.nature.com/articles/s41467-025-62854-z). Main text inspected. | Demonstrates 12–18 GHz LFM beamforming with linear and planar arrays. The authors explicitly explain that the quasi-TTD construction depends on LFM properties and does not apply to arbitrary waveforms. | This motivates testing waveform dependence, but genuine true time delay already handles arbitrary waveforms in principle. Our contribution must concern realizable hardware and its tradeoffs. |
| A6 | M. Wang et al., **2025**, Laser & Photonics Reviews. [Space-time modulation for near-field focusing](https://onlinelibrary.wiley.com/doi/10.1002/lpor.202500406). Publisher abstract inspected. | An 8 × 8 prototype uses harmonic phase control at a 24.5 GHz carrier and 100 kHz modulation to improve focusing relative to 1-bit operation. | Merely demonstrating a moving near-field focus or finer harmonic phase control is not a new problem. Short-pulse performance would need direct study; it cannot be inferred from this abstract. |
| A7 | Bilgin et al., **2025**, Communications Engineering. [Programmable low-coherence wavefronts](https://www.nature.com/articles/s44172-025-00502-6). Main text and methods inspected. | Uses programmable broadband wavefronts with spatial and inter-frequency decorrelation for localization, supported by THz measurements. | Frequency diversity and low-coherence coding are already useful design objectives. A new study should address a specific unmodeled operating condition or calibration constraint. |
| A8 | Li et al., **2026**, Communications Engineering. [Wideband wavefront manipulation across asymmetric media](https://www.nature.com/articles/s44172-026-00645-0). Indexed main-text sections inspected. | Combines resonant and spacer propagation phase for X-band transmission, steering and focusing. Reports about 13% relative bandwidth, with sensitivity analyses covering material, alignment and fabrication changes. | This is the closest hardware comparison for our first proposal. Robustness and asymmetric interfaces alone are already covered; the differentiator must be a waveform-level design result. |
| A9 | **2026**, IEEE INFOCOM. [WiFocus](https://ieeexplore.ieee.org/document/11571374). Publisher abstract/metadata inspected. | Uses phase manipulation to redistribute near-field received power across frequency, supported by D-band measurements. | Compare against bandwidth-aware focusing, not only a single-frequency phase law. Its abstract supports the capacity objective, not a conclusion about every possible pulse metric. |
| A10 | Vellucci et al., **2026**, IEEE JSTEAP. [Pulse-driven transmissive Huygens metasurface](https://pure.nitech.ac.jp/en/publications/pulse-driven-reconfigurable-transmissive-huygens-metasurface-for-/). **Metadata only.** | The institutional record confirms an additional closely related publication. | A novelty watch item requiring full-text inspection before committing to any pulse-driven reconfiguration claim. No performance figures are inferred from its title. |
| A11 | Yazdnian & Ghasempour, **August 2026**, npj Wireless Technology. [Few-shot near-field localization](https://www.nature.com/articles/s44459-026-00058-7). Main text inspected. | Demonstrates D-band localization using angle-dependent spectra and controllable Bessel-beam depth without phase-coherent detection. Optimizes spectral-signature separation and includes robustness analyses. | For the localization branch, neither noncoherent operation nor signature-separation optimization is new. A cover/calibration study must establish a distinct physical failure mode and remedy. |

The evidence points to a distinction worth investigating: broad matching bandwidth, a stable beam direction, and high pulse fidelity are different properties. Existing studies already address several of them. Our proposed contribution is their constrained co-design for a finite focal region and a specified propagation environment, rather than another demonstration of any one property.

## 2. Recommended problem: preserve the pulse at the useful focus

**Working title:** *Pulse-preserving near-field focusing through dielectric covers: joint waveform and aperture design with causal FDTD models.*

**Research question:** for a fixed aperture, feed and material budget, can a lens/metasurface designed for waveform fidelity and useful focal energy outperform designs optimized for peak intensity or band-averaged received power, particularly when the dielectric cover differs from its nominal specification?

**Testable hypothesis:** two designs with similar matching and band-averaged focal power can have significantly different pulse broadening, late-time ringing and timing bias. A design that controls the relative group delays of the aperture contributions may retain useful energy in a short time gate over a larger focal region. This is a hypothesis to test, not a result obtained here.

The potential novelty is a **measured or independently validated tradeoff between pulse fidelity, focal concentration, efficiency and uncertainty**, plus a design rule explaining that tradeoff. A1/A2 already study pulse radiation; A8 already studies wideband asymmetric focusing and tolerances. The combination must yield a demonstrably different design or a useful limit. Simply adding Monte Carlo plots to an existing geometry would be insufficient.

### Initial physical scope

Start with a passive dielectric or multilayer lens fed by a broadband aperture. Use a 2D extruded geometry to isolate the mechanism, then a finite 3D radiator and lens for an antenna paper. A provisional X-band range of 8–12 GHz is a design assumption, chosen for manageable dimensions and proximity to A8; it is not a requirement from the user. A lower-frequency UWB version can be selected if that better matches available hardware.

A dielectric cover can represent a radome or an engineered inspection interface. Specify its thickness, dielectric dispersion and loss from measured or published material data. Do not present an arbitrary dielectric slab as validated biological tissue or infer diagnostic performance.

Use at least two excitation families: a band-limited Gaussian-modulated pulse and a chirped pulse with a comparable occupied band. This tests whether a design improvement is waveform-specific. Choose a small, fixed set of focal ranges and off-axis positions before optimization.

### Baselines that make the result credible

1. The same feed and cover without a focusing structure.
2. A conventional geometric lens or single-frequency phase focusing design.
3. A design optimized for band-averaged focal power using the same parameterization and loss constraints.
4. An ideal true-time-delay aperture as a clearly labeled upper benchmark, with no claim that it is fabricable at the same cost.
5. The proposed waveform-aware design, evaluated on cover parameters and waveforms held out from optimization.

An adaptation of A8 should be identified as such and compared within its actual usable band. A bandwidth-aware phase baseline inspired by A9 is useful, but reproducing its algorithm requires its full paper; an invented approximation must not be labeled a reproduction.

### Measurements and objective

Define pulse fidelity at each observation position using the normalized field correlation

\[
F(\mathbf r)=\max_\tau\frac{\left|\int e(\mathbf r,t)e_{\rm ref}^{*}(\mathbf r,t-\tau)\,dt\right|}
{\sqrt{\int |e(\mathbf r,t)|^2dt\int |e_{\rm ref}(\mathbf r,t)|^2dt}}.
\]

The reference is a prescribed desired pulse, including the expected geometric delay. Report the maximizing delay separately: maximizing correlation alone can hide a timing error. Also report received amplitude/energy, because this normalized metric can be high for a severely attenuated signal.

Collect pulse-width ratio, late-time energy fraction, peak-arrival bias, focal position versus frequency, focal width, sidelobes, and energy delivered to a predefined receiver surface and time gate. Use Poynting flux for physical energy; the current squared-field plots are not calibrated power measurements. A genuine antenna implementation additionally requires feed return loss, accepted power, radiation efficiency and realized gain.

Use a Pareto comparison rather than arbitrary weighted scores: maximize useful gated energy subject to a minimum fidelity and limits on ringing, total thickness and passive loss. Sweep the fidelity threshold. Every numerical target is a proposed design criterion, not an anticipated experimental result.

### First study and decision gate

Begin with 16–32 aperture segments in a 2D model, then implement a small family of physically realizable dielectric profiles. Delays must come from propagation or causal resonant elements; do not assign independently adjustable, lossless phase at every frequency. Test three spatial resolutions, two PML thicknesses and longer records until the relevant waveform metrics converge.

Proceed to 3D when the optimized and baseline designs show a difference larger than their numerical uncertainty over held-out conditions. If an ordinary geometric lens achieves the same Pareto curve, the proposed metasurface contribution fails. That finding should redirect the project toward a useful scaling limit or a different operating regime rather than a more decorative geometry.

**Proposed paper figures:** geometry and delay budget; baseline spectra and waveforms; focal position across the band; fidelity–energy Pareto curves; uncertainty/held-out performance; 3D and measurement comparison. A VNA transfer-function measurement can support pulse reconstruction for a linear time-invariant prototype, provided frequency sampling, reference planes and windowing are controlled. Direct pulse measurements would be an additional check.

## 3. Other candidate publication problems

| Direction | Specific question beyond the reviewed demonstrations | FDTD role | Main difficulty | Priority |
|---|---|---|---|---|
| Transient switching of a metasurface antenna | How do switch rise time, resonator ring-down and unequal aperture timing determine the interval during which neither the old nor new beam carries a usable waveform? Can the switching schedule reduce that interval under the same energy and component constraints? | Coupled field/circuit transient response and radiated waveform; reduced models for long modulation periods. | Device models, bias-network parasitics, full-vector radiation, and overlap with A3/A6/A10. | Second; attractive with RF hardware collaborators. |
| Calibration-robust waveform coding for localization | Which aperture codes remain distinguishable when dielectric cover, coupling or element calibration changes between training and use? | Generate transfer functions including physical coupling and cover changes, then evaluate held-out localization data. | A7/A11 already establish decorrelation and signature-separation approaches; needs a specific failure mode beyond their robustness analyses and strong calibration baselines. | Third; good if sensing is a central interest. |

For the switching topic, distinguish reconfiguration between static states from modulation during an RF signal. Simulating a full 10 kHz modulation period with a picosecond-scale RF time step can require around 10^8 updates in time alone. Use short FDTD switching windows or extracted causal element models combined with envelope/circuit simulation. Increasing the modulation frequency merely to accelerate the solver would change the experiment.

## 4. What our present implementation can support

The existing solver has 1D propagation and a 2D **Ez, Hx, Hy** system, with static dielectric layers, conductivity, PEC geometries, PML and pulse sources. These are useful for an extruded lens mechanism study. It currently has neither a full 3D antenna model nor calibrated feed ports, general near-to-far-field radiation, lumped-device circuits or dynamic materials.

| Required development | Why it matters |
|---|---|
| General geometry/material maps and causal dispersive models | Implement real lens/radome profiles and measured frequency dependence. |
| Broadband field probes and aligned E/H flux monitors | Quantify transfer phase, pulse distortion and energy consistently on the Yee grid. |
| A validated aperture/feed excitation | Separate the focusing structure from source artifacts; later include the actual antenna feed. |
| 3D solver or independent established 3D tool | Finite PCB antennas, cross-polarization, finite apertures and dBi claims cannot be established by a 2D extruded model. |
| Optimization plus held-out evaluations | Produce a design result rather than an illustration; use simple parameter searches before an adjoint implementation. |
| Circuit coupling, only for the switching branch | Model actual reactive loads and switching dynamics, rather than arbitrary changes in dielectric constant. |

For passive linear structures, frequency-domain solutions followed by an inverse Fourier transform can also predict pulses. FDTD is valuable here because it gives broadband transient fields and local interactions directly, but using it is not itself novelty. For a publication, preserve the validated teaching cases and introduce the research features in separate modules with independent benchmarks.

**Recommended next action:** reproduce the waveform behavior of a simple lens/feed baseline, then perform a small fidelity–energy comparison with and without a cover. This is the fastest way to learn whether the proposed antenna problem contains a useful effect before investing in full 3D design.

Full titles, identifiers, access notes and publication status are in [the paper catalog](paper_catalog.csv). The implementation sequence and evidence gates are in [STARTER_PLAN.md](STARTER_PLAN.md).
