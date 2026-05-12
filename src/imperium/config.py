"""Configuration resolution for IMPERIUM verification spine."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import tomllib
from typing import Any


VALID_MODES = {"dev", "operator"}


class ConfigError(RuntimeError):
    """Raised when configuration cannot be resolved safely."""


@dataclass(frozen=True)
class ImperiumConfig:
    schema_version: str
    root_path: Path
    runtime_path: Path
    mode: str
    allow_subprocess: bool
    allow_write: bool
    config_source: str



def _as_bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "on"}:
        return True
    if text in {"0", "false", "no", "off"}:
        return False
    return default



def detect_repo_root(start_path: Path | None = None) -> Path:
    """Find repo root by walking upwards until .git is found."""
    current = (start_path or Path.cwd()).resolve()
    if current.is_file():
        current = current.parent

    for candidate in [current, *current.parents]:
        if (candidate / ".git").exists():
            return candidate
    raise ConfigError("Could not detect repository root from current location.")



def _load_toml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("rb") as handle:
        data = tomllib.load(handle)
    if not isinstance(data, dict):
        raise ConfigError(f"Configuration file must contain a TOML table: {path}")
    return data



def _resolve_mode(explicit_mode: str | None, config_data: dict[str, Any]) -> str:
    raw = (
        explicit_mode
        or os.getenv("IMPERIUM_MODE")
        or config_data.get("mode")
        or "dev"
    )
    mode = str(raw).strip().lower()
    if mode not in VALID_MODES:
        raise ConfigError(f"Invalid mode '{raw}'. Expected one of {sorted(VALID_MODES)}.")
    return mode



def load_config(
    explicit_root: str | Path | None = None,
    *,
    config_path: str | Path | None = None,
    mode: str | None = None,
) -> ImperiumConfig:
    """Resolve effective runtime configuration.

    Root resolution order:
    1) explicit argument
    2) IMPERIUM_ROOT environment variable
    3) root_path in imperium.toml
    4) detected repository root fallback in dev mode only
    """
    repo_root = None
    try:
        repo_root = detect_repo_root()
    except ConfigError:
        repo_root = None

    if config_path:
        effective_config_path = Path(config_path).expanduser().resolve()
    elif repo_root is not None:
        effective_config_path = repo_root / "imperium.toml"
    else:
        effective_config_path = Path.cwd() / "imperium.toml"
    file_config = _load_toml(effective_config_path)

    resolved_mode = _resolve_mode(mode, file_config)

    root_candidate: str | Path | None = None
    source = ""

    if explicit_root is not None:
        root_candidate = explicit_root
        source = "explicit_arg"
    elif os.getenv("IMPERIUM_ROOT"):
        root_candidate = os.getenv("IMPERIUM_ROOT")
        source = "env:IMPERIUM_ROOT"
    elif file_config.get("root_path"):
        root_candidate = file_config.get("root_path")
        source = f"file:{effective_config_path.name}"
    elif resolved_mode == "dev" and repo_root is not None:
        root_candidate = repo_root
        source = "repo_root_fallback_dev"
    else:
        raise ConfigError("Root path unresolved: operator mode requires explicit/env/file root_path.")

    root_path = Path(root_candidate).expanduser().resolve()

    runtime_candidate = os.getenv("IMPERIUM_RUNTIME") or file_config.get("runtime_path")
    runtime_path = (
        Path(runtime_candidate).expanduser().resolve()
        if runtime_candidate
        else (root_path / ".imperium_runtime")
    )

    allow_subprocess = _as_bool(os.getenv("IMPERIUM_ALLOW_SUBPROCESS"), _as_bool(file_config.get("allow_subprocess"), False))
    allow_write = _as_bool(os.getenv("IMPERIUM_ALLOW_WRITE"), _as_bool(file_config.get("allow_write"), False))

    return ImperiumConfig(
        schema_version="imperium.config.v0_1",
        root_path=root_path,
        runtime_path=runtime_path,
        mode=resolved_mode,
        allow_subprocess=allow_subprocess,
        allow_write=allow_write,
        config_source=source,
    )

