"""Plugins: rule variants in a file outside the package, registered at run time.

A plugin is a Python file whose classes use @register, exactly like the built-in components.
It is how a design chat tries a new mechanism without touching the baseline: the experiment
gets its own variant name, and the plugin's hash goes into every result's provenance. A
variant name that's already registered is refused, so a plugin can't shadow a rule.
"""

import hashlib
import importlib.util
import sys
from dataclasses import dataclass
from pathlib import Path

from stamina_engine.core.errors import ConfigError
from stamina_engine.rules import components as _components  # noqa: F401  (built-ins first)
from stamina_engine.rules.registry import forget, registered


@dataclass(frozen=True)
class PluginInfo:
    name: str  # file name
    sha256: str
    components: tuple[tuple[str, str], ...]  # (kind, variant) it registered


_LOADED: dict[Path, PluginInfo] = {}


def load_plugin(path: str | Path) -> PluginInfo:
    """Import a plugin file and return what it registered. Loading the same unchanged file
    again is a no-op; loading it again after it changed is an error (restart instead)."""
    resolved = Path(path).resolve()
    try:
        source = resolved.read_bytes()
    except OSError as exc:
        raise ConfigError(f"can't read plugin {path}: {exc}") from exc
    sha = hashlib.sha256(source).hexdigest()
    if resolved in _LOADED:
        if _LOADED[resolved].sha256 != sha:
            raise ConfigError(f"plugin {resolved.name} changed since it was loaded; restart")
        return _LOADED[resolved]

    before = set(registered())
    module_name = f"stamina_plugin_{sha[:16]}"
    spec = importlib.util.spec_from_file_location(module_name, resolved)
    if spec is None or spec.loader is None:
        raise ConfigError(f"can't import plugin {resolved}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module  # dataclasses and type hints look the module up
    try:
        spec.loader.exec_module(module)
    except Exception as exc:
        _roll_back(before, module_name)
        raise ConfigError(f"plugin {resolved.name} failed to load: {exc}") from exc

    added = tuple(sorted(set(registered()) - before))
    if not added:
        _roll_back(before, module_name)
        raise ConfigError(f"plugin {resolved.name} registered no components (use @register)")
    info = PluginInfo(resolved.name, sha, added)
    _LOADED[resolved] = info
    return info


def _roll_back(before: set[tuple[str, str]], module_name: str) -> None:
    for kind, variant in set(registered()) - before:
        forget(kind, variant)
    sys.modules.pop(module_name, None)
