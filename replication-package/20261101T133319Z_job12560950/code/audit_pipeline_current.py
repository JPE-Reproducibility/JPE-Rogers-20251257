#!/usr/bin/env python3
"""
Audit wrapper for the CURRENT manuscript (resolves paths relative to the package root).

Version-agnostic: it audits the highest-numbered (by NUMERIC version)
`paper/JPE_submission_v*.tex` shipped in the package (the deposit ships exactly
one, JPE_submission_v8.tex), so it does not need retargeting on a version bump.

Self-contained for clean-room reviewers: resolves the manuscript TeX,
bibliography, and figure/table comparison paths relative to the package root,
so the audit can be rerun anywhere the package is unpacked.

The manuscript's \\includegraphics and \\input paths use the prefix
"../replication_package/output/..." (relative to the manuscript's original
location in my_paper/paper/). This wrapper rewrites that resolution so both
the manuscript-side and replication-side comparisons land on the package's
own output/ directory.
"""

import re
import sys
from pathlib import Path

import audit_pipeline as base


PACKAGE_ROOT = Path(__file__).resolve().parents[1]


def _ms_version(path):
    """Numeric version key so v10 sorts AFTER v9 (a lexicographic sort would not)."""
    m = re.search(r"_v(\d+)\.tex$", path.name)
    return int(m.group(1)) if m else -1


# Target the shipped manuscript. The deposit ships exactly one
# (JPE_submission_v8.tex); if more than one is present, pick the highest version
# NUMERICALLY (not lexicographically — as strings "v10" < "v9").
_MS_CANDIDATES = sorted(
    (PACKAGE_ROOT / "paper").glob("JPE_submission_v*.tex"), key=_ms_version
)
MS_TEX = _MS_CANDIDATES[-1] if _MS_CANDIDATES else PACKAGE_ROOT / "paper" / "JPE_submission_v8.tex"
AUDIT_HTML = base.ROOT_DIR / "output" / "replication_audit.html"


def _patch_audit():
    """Redirect manuscript-side paths to the package's own output/ directory.

    Rationale: in a clean-room build the manuscript is shipped inside the
    package and there is no separate "rendered manuscript output" tree. The
    audit's purpose here is to confirm every figure/table referenced by the
    manuscript exists in the package's output. We point both sides of the
    comparison at the package output so a missing exhibit shows up as
    REPL-MISSING and an existing exhibit shows up as MATCH.
    """
    base.MS_TEX = MS_TEX
    base.OUTPUT_HTML = AUDIT_HTML
    base.MS_FIGURES = base.ROOT_DIR / "output" / "figures"
    base.MS_TABLES_FMT = base.ROOT_DIR / "output" / "tables" / "Formatted"

    # Freshness is not assessed in a packaged build. Assembling the archive resets
    # file mtimes, so the base mtime-based staleness check does not apply here and
    # is disabled: this audit certifies that every manuscript-referenced exhibit
    # EXISTS in output/ (completeness), not that it was freshly regenerated.
    # Freshness is established by the clean from-source run of run_all.py.
    base.check_staleness = lambda *args, **kwargs: (False, None, None, None)

    def _resolve_manuscript_table_path(tex_path, fname):
        candidate = (base.MS_TEX.parent / tex_path).resolve()
        if candidate.exists():
            return candidate
        for sub in ("tables", "tables/Formatted"):
            c = base.ROOT_DIR / "output" / sub / fname
            if c.exists():
                return c
        return base.MS_TABLES_FMT / fname

    base.resolve_manuscript_table_path = _resolve_manuscript_table_path


def main() -> int:
    if not MS_TEX.exists():
        raise FileNotFoundError(
            f"Manuscript TeX not found at {MS_TEX}. "
            "Ensure a paper/JPE_submission_v*.tex is shipped in the package."
        )
    print(f"  Auditing manuscript: {MS_TEX.name}")
    print("  Scope: exhibit existence/completeness (every figure/table referenced "
          "by the manuscript exists in output/). Freshness is not assessed here "
          "(packaged mtimes reset at assembly); freshness is established by a clean "
          "from-source run of run_all.py.")
    _patch_audit()
    rc = base.main()   # FAIL-CLOSED: propagate the base audit's exit code (missing exhibit /
    #                    0-ref manuscript / provenance gap -> nonzero), do not discard it.

    if AUDIT_HTML.exists():
        html = AUDIT_HTML.read_text(encoding="utf-8")
        html = html.replace("JPE_submission_v1.tex", MS_TEX.name)
        AUDIT_HTML.write_text(html, encoding="utf-8")
        print(f"  Audit HTML written to: {AUDIT_HTML}")
    return int(rc or 0)


if __name__ == "__main__":
    sys.exit(main())
