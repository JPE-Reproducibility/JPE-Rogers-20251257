# manual_figures/

**Supporting reference; `README.md` governs.**

Source assets for the one manuscript figure that is **not** produced by an
estimation script: `Deregulation_May31_23_Paper.png` (manuscript **Figure 2**,
label `pic:DeviceDeregulation`), a hand-drawn conceptual schematic of the FDA
reclassification design. It plots no estimate, so there is nothing to regenerate
from data.

Two files ship here:

- `Deregulation_May31_23_Paper.png` — the image the manuscript includes.
  `run_all.py`'s `copy_manual_figure()` copies it into `output/figures/` as a
  package output, so the figure is restored even after `output/figures/` is
  emptied for a from-scratch run.
- `Deregulation_May31_23_Paper.drawio` — the editable master, plain XML. Open it
  at <https://app.diagrams.net> (or in the draw.io desktop app) and export to PNG
  to regenerate the image. It is a package **source** asset, so it lives here and
  is deliberately **not** copied into `output/`: `output/` holds only what a run
  produces, and the output comparison treats anything else found there as an
  unaccounted extra. Its SHA-256 is pinned in
  `certification/EXPECTED_MODEL_ARTIFACT_HASHES.csv`.

See `certification/FIGURE_PROVENANCE.md` for the figure's provenance and the
REPRODUCIBILITY POLICY block in `run_all.py` for why it is not script-generated.
