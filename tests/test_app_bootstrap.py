from __future__ import annotations

import sys
from pathlib import Path

from app.bootstrap import ensure_project_root_on_path


def test_ensure_project_root_on_path_adds_repo_root() -> None:
    project_root = Path(__file__).resolve().parents[1]
    root_str = str(project_root)
    original_path = list(sys.path)

    try:
        sys.path = [entry for entry in sys.path if entry != root_str]
        resolved_root = ensure_project_root_on_path()

        assert resolved_root == project_root
        assert sys.path[0] == root_str
    finally:
        sys.path = original_path
