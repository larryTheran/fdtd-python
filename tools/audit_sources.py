#!/usr/bin/env python3
"""Read and hash the original archive without modifying it; regenerate provenance."""
from pathlib import Path
import csv
import hashlib
import json
import zipfile
from collections import Counter

PROJECT = Path(__file__).resolve().parents[1]
SOURCE = PROJECT.parent

# IDs refer to the individually runnable Python experiments, not original filenames.
MAPPING = {
    "FDTD_1D_sin_nada.m": ("01", "Last H index corrected using the _modi version."),
    "FDTD_1D_sin_nada_modi.m": ("01", "Zero-exterior update used; thesis optical settings take precedence."),
    "FDTD_1D_Frontera_Perfecta.m": ("02,14", "Two-step delay ABC retained; true PEC supplied separately."),
    "FDTD_1D_TS_FS.m": ("03,04", "Active MATLAB code uses periodic ghosts; both open and periodic cases supplied."),
    "FDTD_1D_TF.m": ("05", "Reference-normalized spectra replace division by the bare source at noisy frequencies."),
    "FDTD_1D_Dielectrico_sin_perdidas.m": ("06", "Two-layer reflection/transmission and material-speed diagrams."),
    "FDTD_1D_Dielectrico_sin_perdidas_2.m": ("06", "Snapshot variant; same physical geometry."),
    "FDTD_1D_Dielectrico_sin_perdidas_vectorial.m": ("07", "Interactive layer inputs replaced by an editable Layer list."),
    "FDTD_1D_Dielectrico_con_perdidas.m": ("10,11,12", "Integral-current formulation; cm/optical units separated."),
    "FDTD_1D_Dielectrico_con_perdidas1.m": ("08,09", "Centered Ohmic update; unrelated highly conductive endpoint removed."),
    "FDTD_1D_Dielectrico_con_perdidas_densidad_de_corriente.m": ("08,09", "Prototype resizes the grid to 200; canonical thesis slab is 400 cells."),
    "FDTD_1D_Dielectrico_con_perdidas_densidad_de_corriente1.m": ("08,09", "Undefined f0, freq_in and KE; corrected source/time-grid implementation replaces this draft."),
    "FDTD_1D_Dielectrico_con_perdidas_densidad_de_corriente2.m": ("09", "Fig. 4-18 snapshot source; fixes cm override and stale source coefficient/index."),
    "FDTD_1D_Dielectrico_con_perdidas_densidad.m": ("08,10,11,12", "Broken matrix division/scalar coefficients and inconsistent 1/epsilon0 normalization; covered by validated lossy solvers."),
    "FDTD_1D_Dielectrico_periodico.m": ("13", "Alternating epsilon=5/2 slabs at 5 GHz; source length bug and insufficient duration corrected."),
    "FDTD_2D_libre.m": ("15,16,17,18", "Several incompatible point/line and boundary variants; separated into explicit experiments."),
    "FDTD_2D_PML.m": ("19", "Asymmetric fi3=(1-xn)/(1-xn), stale indices and missing cross terms replaced by split-field PML."),
    "FDTD_2D_PML_TF_SF.m": ("23", "Correct staggered electric/magnetic plane-source injection."),
    "FDTD_2D_PML_solo_en_X.m": ("20,21", "Filename and active damping axes disagree; axes are explicit in Python."),
    "FDTD_2D_PML_solo_en_X_frontera_periodica_en_Y.m": ("20,21,24", "Contains dielectric loss and undefined Ez_src; boundary and material cases separated."),
    "FDTD_2D_PML_solo_en_X_material_onda_plana.m": ("22,24", "Plane source with lossy half-space; physical sigma retained at 50 GHz in 24."),
    "Untitled7.m": ("23", "Normal-incidence TF/SF/DFT prototype; declared er2 slab is never inserted."),
    "Untitled7modi.m": ("23", "Incomplete coefficients, undefined source/steps/draw2d; runnable plane-wave reconstruction."),
    "Untitled8.m": ("38", "Incomplete effective-index bend: missing ezmode, coordinates and ramp. Reconstructed as a clearly labeled supplement."),
    "FDTD_2D_1_2_Rendijas.m": ("25,26,27,28,29,30", "Single/double slit branches; explicit aperture widths, PEC, detector averaging and far-field guide."),
    "FDTD_2D_1_2_Rendijas_modi.m": ("25,26,27,28,29,30", "Plot/parameter variants include 532/700 nm and ambiguous slit half-width; thesis figure cases kept separately."),
    "FDTD_2D_refraccion.m": ("31,32,34", "Draft assigns ER linearly and never uses it in ga; interfaces reconstructed from thesis chapter 6."),
    "FDTD_2D_Libre.m": ("18", "Periodic prototype with corner/index errors."),
    "FDTD_2D_Libre2.m": ("19,20,21,23", "PML/DFT prototype with undefined Sx and mode-array size mismatch."),
    "Untitled2.m": ("19,36", "PML/three-point diagonal source experiment; explicit array source geometry supplied."),
    "refraccionmodi.m": ("31,35", "ABC/PML hybrid draft; clean PML and first-order Mur variants supplied."),
    "refraccionmur.m": ("35", "Mur prototype; documented first-order replacement and consistent source frequency."),
    "refraccionpml.m": ("34", "Outer folder has 1.5/2.5/1.5. Nested draft has index1=0 and divides by zero; thesis values take precedence."),
    "refraccionpml1.m": ("31,32,33", "Nested draft n2=2, outer n2=4; thesis n2=2.1 plus stated n2=4 and true PEC cases supplied."),
    "refraccionlarry.m": ("36", "Diagonal source is active; no material interface is actually built."),
    "interfaz1D.m": ("01-14", "GUIDE callback scaffold; Simular_Callback is empty. Replaced by independent scripts/CLI, not a GUI port."),
    "Program31_refraction_at_interface_of_two_media.m": ("35", "Reference code copied in four thesis folders; negative index is squared into positive epsilon and is not a negative-index material model."),
    "FDTD2D.m": ("37", "Root 700 nm double slit, dx=41.17 nm, 400x400. Sampled aperture dimensions documented explicitly."),
}


def main():
    files = sorted(p for p in SOURCE.rglob("*") if p.is_file()
                   and p.relative_to(SOURCE).parts[0] not in {"python_fdtd", "tmp", ".git"})
    records, seen, types, archive_info, matlab = [], {}, Counter(), [], []
    for p in files:
        raw = p.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        rel = str(p.relative_to(SOURCE))
        duplicate = seen.get(digest, "")
        seen.setdefault(digest, rel)
        suffix = p.suffix.lower()
        types[suffix or "(none)"] += 1
        records.append(dict(path=rel, bytes=len(raw), suffix=suffix, sha256=digest, duplicate_of=duplicate))
        if suffix == ".m":
            ids, comment = MAPPING.get(p.name, ("UNMAPPED", "Needs manual review"))
            matlab.append(dict(path=rel, sha256=digest, duplicate_of=duplicate,
                               experiment_ids=ids, review=comment))
        if suffix == ".zip":
            with zipfile.ZipFile(p) as z:
                archive_info.append(dict(path=rel, member_count=len(z.namelist()),
                                         source_members=[n for n in z.namelist() if n.lower().endswith((".m", ".py"))]))
    with (PROJECT/"docs/source_inventory.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)
    summary = dict(original_files=len(files), file_types=dict(types), matlab_files=len(matlab),
                   unique_matlab_contents=len({r["sha256"] for r in matlab}), archives=archive_info)
    (PROJECT/"docs/source_audit.json").write_text(json.dumps(dict(summary=summary, matlab=matlab), indent=2)+"\n")
    lines = ["# Original file audit", "", f"Indexed and SHA-256 hashed **{len(files)} original files**. "
             f"Reviewed **{len(matlab)} MATLAB files ({summary['unique_matlab_contents']} distinct byte contents)**, "
             "plus the MATLAB autosave. Source files were not edited.", "",
             "The inventory covers every original file, including images, PDFs, LaTeX source, compiled "
             "artifacts and archives. It is an inventory, not a claim of visual review of every duplicate image. "
             "The main 118-page thesis was text-extracted; chapters 4-6, equations, captions and representative "
             "rendered pages were used to define the experiments. The alternate thesis folders and the Ohner "
             "reference were inspected for context. Four ZIP files contain LaTeX tcolorbox resources and no MATLAB/Python code.", "",
             "Protected MATLAB `.p` plotting helpers cannot be read as source; Python uses Matplotlib. "
             "The `.fig`, `.bin`, EPS/PNG/PDF outputs and compiled LaTeX files are preserved as references, "
             "not executed. The GUIDE file has empty simulation callbacks and no corresponding runnable GUI layout here.", "",
             "`source_inventory.csv` lists every path, size, hash and exact duplicate. "
             "`source_audit.json` contains the machine-readable source-to-experiment map.", "",
             "## MATLAB source-to-experiment map", "", "Paths are relative to the original FDTD folder. "
             "Experiment IDs refer to the numbered Python scripts in `experiments/`.", "",
             "| Original MATLAB file | Python IDs | Findings |", "|---|---|---|"]
    for r in matlab:
        note = r["review"] + (" Exact duplicate of another inventoried source." if r["duplicate_of"] else "")
        lines.append(f"| {r['path']} | {r['experiment_ids']} | {note} |")
    lines.extend(["", "The `.asv` file repeats the incomplete current-density draft (undefined `f0`, "
                  "`freq_in`, `KE`) and maps to the corrected loss cases 08-12. "
                  "Both `fdtd1dpercon.txt` files are empty (zero bytes).", ""])
    (PROJECT/"docs/SOURCE_AUDIT.md").write_text("\n".join(lines))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
