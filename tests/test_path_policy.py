from __future__ import annotations

from pathlib import Path
import sys

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from imperium.security.path_policy import PathPolicyError, require_inside_root



def test_path_inside_root_passes(tmp_path: Path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    child = root / "nested" / "file.txt"

    resolved = require_inside_root(child, root)

    assert resolved == child.resolve(strict=False)



def test_path_outside_root_fails(tmp_path: Path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    outside = tmp_path / "outside.txt"

    with pytest.raises(PathPolicyError):
        require_inside_root(outside, root)
