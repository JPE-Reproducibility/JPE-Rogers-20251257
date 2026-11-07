"""Shared output-path overrides for clean-room synthetic-data generation.

Normal author-side generation uses the package's ``_synthetic_source_internal``
and ``simulated_data`` directories. ``build_simulation.py`` sets both environment
variables below so every Stage-B generator writes into an isolated temporary tree
instead of reading or mutating an existing simulated payload.
"""

from __future__ import annotations

import os
from pathlib import Path


HERE = Path(__file__).resolve().parent
PACKAGE_ROOT = HERE.parents[1]
SYNTHETIC_PIPELINE = PACKAGE_ROOT / "synthetic_pipeline"


def internal_dir() -> Path:
    return Path(
        os.environ.get(
            "FDA_SYNTHETIC_INTERNAL",
            str(SYNTHETIC_PIPELINE / "_synthetic_source_internal"),
        )
    ).resolve()


def simulated_data_dir() -> Path:
    return Path(
        os.environ.get(
            "FDA_SIMULATED_DATA_OUT",
            str(SYNTHETIC_PIPELINE / "simulated_data"),
        )
    ).resolve()
