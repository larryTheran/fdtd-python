# Search scope and evidence notes

Search date: **6 September 2026**. Coverage: recent antenna and ultrafast-optics applications in which broadband, transient or time-varying electromagnetic modeling could be useful. The working corpus contains **22 records: 11 per field**, including one metadata-only antenna watch item. Reading depth varies and is explicitly listed for every record in the catalog.

## Method

The search began with wideband antennas, pulse fidelity, near-field focusing, time-modulated metasurfaces, femtosecond pulse shaping, nonlinear resonances and time-varying transparent conducting oxides. Promising results were followed through exact-title searches, DOI/publisher pages, institutional repositories and author manuscripts. Version-of-record and preprint duplicates were treated as one study where the relationship was verified.

Primary evidence was preferred: the research article, its authors' manuscript, publisher metadata or the authors' institutional publication/code repository. Secondary search results helped locate papers but were not used as the scientific basis of the reviews. Search snippets were checked against primary records when possible. Some publisher pages were unavailable directly, so accessible indexed article sections or institutional abstracts were used and labeled.

This was not an exhaustive database export, a PRISMA review, a citation-count ranking or a systematic appraisal of every paper published in either field. It deliberately emphasizes work close to the current FDTD capabilities and promising extensions. Topics such as quantum emission, strong-field electron dynamics and fully vectorial topological fields were not promoted as immediate applications of the present solver.

## Representative query families

- `2025 2026 time varying metasurface antenna pulse distortion transient beamforming`
- `2024 2025 ultrawideband antenna pulse fidelity near field metasurface FDTD`
- `2025 antenna metasurface true time delay wideband pulse distortion`
- `antenna near field focusing pulse fidelity metasurface robust group delay 2024 2025 2026`
- `2025 2026 ultrafast optics time varying metasurface pulse shaping quasi bound state continuum`
- `2024 2025 time refraction optics single cycle modulation epsilon near zero pulse FDTD`
- `time-varying Drude energy causality 2024 2025`
- `quasi BIC metasurface ultrashort pulse optimal Q pulse duration finite beam 2025 2026`
- Exact-title searches for every selected paper and publication-version checks.
- Final overlap searches for `time-varying Drude identifiability`, `pump-probe model discrimination`, and `metasurface near-field pulse fidelity optimization`.

The final overlap searches did not establish an exact-match solution to either recommended proposal in the accessible results. **That absence is not evidence of novelty.** The closest overlaps, particularly antenna A1/A2/A8/A11 and optical U2/U5/U6/U7/U8, are explicitly discussed in the reviews.

## Publication and access checks that changed the interpretation

- **A7:** the publisher says 16 October 2025. A search result included a July 2026 date belonging to a related article. The review uses the actual publication date.
- **A4:** the 2025 author manuscript was read. An associated IEEE TWC DOI was found, but the publisher version/final issue metadata were not independently accessed, so the review does not present the manuscript and journal article as separate evidence.
- **U4:** the 2024 preprint corresponds to a 2025 Advanced Optical Materials article. It is counted once, using the journal title and DOI.
- **U6:** the 2025 arXiv manuscript was read; the authors' [Exeter software repository](https://doi.org/10.24378/exe.31399617) confirms a 2026 Journal of Optics publication and supplies its DOI and FDTD code. Exact March publication days conflict across accessible records; only the year/month relationship is used. No code from that repository was executed in this review.
- **U8:** the publisher abstract and [publisher-supplied Crossmark record](https://crossmark.crossref.org/dialog/?doi=10.1038%2Fs41565-026-02199-w) support the result and 22 June 2026 online date. The full main text was not accessed.
- **U11:** the arXiv record is a preprint first submitted 31 July 2026. No journal version was verified.
- **A10:** institutional metadata confirm the publication, but its full content was not read. It is included only as a nearby item to check before a reconfiguration project.

## Distinguishing findings from proposals

The paper tables summarize reported work; linked sources support those summaries. Research questions, suggested comparisons, metrics and implementation milestones are our proposed synthesis. No improvement percentages, successful optimizations, new experimental observations or publication acceptance are asserted for the proposed projects.

The code assessment is based on the local `fdtd/config.py`, `fdtd/two_d.py` and project README: the present 2D solver evolves Ez, Hx and Hy with static materials. The existing normal-incidence spectrum and teaching energy proxy must be extended before general time-varying or antenna-power claims can be made.
