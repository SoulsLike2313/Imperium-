"""Path policy helpers for root-constrained file access."""

from __future__ import annotations

from pathlib import Path
import re


class PathPolicyError(ValueError):
    """Raised when a path escapes the configured root boundary."""


ABSOLUTE_LOCAL_PATH_PATTERNS = [
    re.compile(r"\b[A-Za-z]:\\\\[^\s\"']+"),
    re.compile(r"/home/[^\s\"']+"),
    re.compile(r"/Users/[^\s\"']+"),
]



def _resolved(path: str | Path, root: Path | None = None) -> Path:
    candidate = Path(path).expanduser()
    if not candidate.is_absolute():
        if root is None:
            raise PathPolicyError(f"Relative path '{candidate}' requires root context.")
        candidate = root / candidate
    return candidate.resolve(strict=False)



def require_inside_root(path: str | Path, root: str | Path) -> Path:
    """Return resolved path only if it stays within the resolved root."""
    root_resolved = Path(root).expanduser().resolve(strict=False)
    path_resolved = _resolved(path, root_resolved)

    try:
        path_resolved.relative_to(root_resolved)
    except ValueError as exc:
        raise PathPolicyError(
            f"Path escapes root boundary: path={path_resolved} root={root_resolved}"
        ) from exc

    return path_resolved



def safe_relative_path(path: str | Path, root: str | Path) -> str:
    """Return normalized root-relative path after boundary check."""
    safe_path = require_inside_root(path, root)
    root_resolved = Path(root).expanduser().resolve(strict=False)
    return safe_path.relative_to(root_resolved).as_posix()



def looks_like_absolute_local_path(value: str) -> bool:
    """True when a string contains a local absolute path token."""
    return any(pattern.search(value) for pattern in ABSOLUTE_LOCAL_PATH_PATTERNS)



def find_absolute_local_paths(text: str) -> list[str]:
    """Extract local absolute path tokens from text."""
    matches: list[str] = []
    for pattern in ABSOLUTE_LOCAL_PATH_PATTERNS:
        matches.extend(pattern.findall(text))
    # Preserve order while deduplicating.
    deduped = list(dict.fromkeys(matches))
    return deduped
