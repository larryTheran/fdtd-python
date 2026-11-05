# Publication opportunities from the Python FDTD project

Literature checked on **6 September 2026**, emphasizing 2024–2026 primary research. Prepared for a researcher with experience in antenna design and ultrafast optics. Experimental facilities, preferred bands and computing resources were not specified, so the recommendations favor a staged computational start and identify where collaborators or measurement equipment become necessary.

The two reviews are separate and can be read independently:

- [Antenna design review](ANTENNA_REVIEW.md): 11 paper records, three candidate directions, a recommended pulse-preserving focusing study, baselines, metrics and required code extensions.
- [Ultrafast optics review](ULTRAFAST_OPTICS_REVIEW.md): 11 paper records, three candidate directions, a recommended study of observable material dynamics, benchmarks and required constitutive physics.
- [Starter plan](STARTER_PLAN.md): the first independent benchmarks, decision gates and paths toward a publication.
- [Paper catalog — CSV](paper_catalog.csv), [JSON](paper_catalog.json), and [BibTeX](references.bib): titles, identifiers, access levels and publication-status notes. Some BibTeX author lists are deliberately abbreviated with `others`; expand from publisher metadata before manuscript submission.
- [Search and evidence notes](SEARCH_NOTES.md): review scope, query families, corrections to misleading search metadata and limitations.

## Recommended choices

| Field | Lead question | First useful calculation | What must be new |
|---|---|---|---|
| Antennas | Can a realizable focusing structure preserve a broadband waveform through an imperfect dielectric cover over a useful focal region? | 2D feed/lens/cover comparison using pulse fidelity and gated energy. | A demonstrated design tradeoff or design rule beyond existing pulse antennas and robust wideband metasurfaces. |
| Ultrafast optics | Which time-varying material models remain distinguishable in finite-film pulse measurements with uncertain experimental parameters? | 1D causal dispersive slab and temporal-interface benchmarks. | A quantitative observability limit or feasible measurement protocol beyond existing ideal model comparisons. |

**Assessment:** the optical proposal has the shortest route to a meaningful independent numerical benchmark. The antenna proposal has a more direct path to a conventional fabricated prototype if RF facilities are available. Both still require a new result; neither is publication-ready because the teaching simulations run correctly.

These reviews contain proposed studies, not new simulation results. The 38 completed thesis experiments and their validation are unchanged. The new hypotheses have not been run, optimized or experimentally tested.
