"""Thin backend wrapper over mlend.query_parser."""

from __future__ import annotations

from pathlib import Path
import sys

# Ensure project root is importable so `mlend` package can be used from backend.
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from mlend.query_parser import (  # noqa: E402
    ALLOWED_COLUMNS,
    apply_filter_spec,
    filter_spec_to_dict,
    parse_query_with_openai,
)

__all__ = [
    "ALLOWED_COLUMNS",
    "apply_filter_spec",
    "filter_spec_to_dict",
    "parse_query_with_openai",
]
