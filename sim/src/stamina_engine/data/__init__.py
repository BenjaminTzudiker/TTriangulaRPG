"""Data files: weapon, armor and shield tables, class cores, builds. Loaded with load_toml."""

import tomllib
from functools import lru_cache
from importlib.resources import files
from typing import Any


@lru_cache(maxsize=256)
def _text(parts: tuple[str, ...]) -> str:
    """Data files don't change while the engine runs: read each once per process."""
    return files(__name__).joinpath(*parts).read_text()


def load_toml(*parts: str) -> dict[str, Any]:
    return tomllib.loads(_text(parts))


def list_names(folder: str) -> list[str]:
    return sorted(
        p.name.removesuffix(".toml")
        for p in files(__name__).joinpath(folder).iterdir()
        if p.name.endswith(".toml")
    )
