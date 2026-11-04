"""Data files: weapon, armor and shield tables, class cores, builds. Loaded with load_toml."""

import tomllib
from importlib.resources import files
from typing import Any


def load_toml(*parts: str) -> dict[str, Any]:
    resource = files(__name__).joinpath(*parts)
    return tomllib.loads(resource.read_text())


def list_names(folder: str) -> list[str]:
    return sorted(
        p.name.removesuffix(".toml")
        for p in files(__name__).joinpath(folder).iterdir()
        if p.name.endswith(".toml")
    )
