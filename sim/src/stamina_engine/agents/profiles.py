"""NPC profiles (ENGINE_PLAN agent family 4; Ledger H-6): data files that configure the
tactical agent the way a stat block would ("commits 2 steps; 3 against a target below half
stamina"). The packet leaves NPC aggression profiles out of this version, so these are agent
behavior, not rules; sweeping them is how a GM's lethality dial (Review F6) is measured.

A profile is data/profiles/<name>.toml with a [profile] table of tactical agent fields:
commit, commit_vs_low, low_target, target (focus, lowest_stamina, nearest, first),
retreat_engaged, low_stamina, flee_below, surrender_below, w, objective (kill or first, see
agents/objective_play.py), and a description.
"""

import tomllib
from importlib.resources import files

from stamina_engine.core.errors import ConfigError

cites = ("Packet: Running the Game", "Ledger GM-1", "Ledger H-6", "Review F6")


def library_profiles() -> list[str]:
    folder = files("stamina_engine.data").joinpath("profiles")
    return sorted(
        p.name.removesuffix(".toml") for p in folder.iterdir() if p.name.endswith(".toml")
    )


def load_profile(name: str) -> dict[str, object]:
    resource = files("stamina_engine.data").joinpath("profiles", f"{name}.toml")
    if not resource.is_file():
        raise ConfigError(f"no NPC profile {name!r}; known: {library_profiles()}")
    data = tomllib.loads(resource.read_text())
    profile = dict(data.get("profile", {}))
    if not profile:
        raise ConfigError(f"profile {name} has no [profile] table")
    return profile
