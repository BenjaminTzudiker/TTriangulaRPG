"""Builds: only what a player chooses. Every number is derived (see derive.py)."""

import tomllib
from dataclasses import dataclass, field
from typing import Any

from stamina_engine.core.errors import BudgetError, ConfigError
from stamina_engine.core.mathx import tri
from stamina_engine.data import load_toml
from stamina_engine.model.equipment import ATTRIBUTES, EquipmentTable
from stamina_engine.rules.ruleset import RuleSet

cites = ("Packet: Character Creation", "Packet: Costs", "Ledger CP-4", "Ledger CP-5")


@dataclass(frozen=True)
class Attributes:
    STR: int = 0
    AGI: int = 0
    FIN: int = 0
    INT: int = 0
    WIL: int = 0
    CUN: int = 0

    def get(self, name: str) -> int:
        if name not in ATTRIBUTES:
            raise ConfigError(f"no attribute {name!r}")
        value: int = getattr(self, name)
        return value

    def as_dict(self) -> dict[str, int]:
        return {a: self.get(a) for a in ATTRIBUTES}


@dataclass(frozen=True)
class Loadout:
    """What's in each hand and what's worn. off_hand is a shield or a weapon name."""

    armor: str = "none"
    weapon: str | None = None
    grip: str = "one"
    off_hand: str | None = None


@dataclass(frozen=True)
class Build:
    name: str
    level: int
    attributes: Attributes
    loadouts: tuple[tuple[str, Loadout], ...]
    cores: tuple[str, ...] = ()
    proficiencies: frozenset[str] = field(default_factory=frozenset)

    @staticmethod
    def from_dict(name: str, data: dict[str, Any]) -> "Build":
        try:
            loadouts = tuple((n, Loadout(**d)) for n, d in data["loadouts"].items())
            return Build(
                name=name,
                level=int(data["level"]),
                attributes=Attributes(**data.get("attributes", {})),
                loadouts=loadouts,
                cores=tuple(data.get("cores", ())),
                proficiencies=frozenset(data.get("proficiencies", ())),
            )
        except (KeyError, TypeError) as exc:
            raise ConfigError(f"build {name}: {exc}") from exc

    @staticmethod
    def from_toml(name: str, text: str) -> "Build":
        return Build.from_dict(name, tomllib.loads(text))


def load_build(name: str) -> Build:
    """A library build from data/builds/<name>.toml."""
    return Build.from_dict(name, load_toml("builds", f"{name}.toml"))


def core_proficiencies(cores: tuple[str, ...]) -> frozenset[str]:
    table = load_toml("cores.toml")["cores"]
    granted: set[str] = set()
    for core in cores:
        if core not in table:
            raise ConfigError(f"no core ability {core!r}")
        granted.update(table[core]["proficiencies"])
    return frozenset(granted)


def expertise_cost(attributes: Attributes) -> int:
    """The Nth attribute point costs N (Packet: Costs)."""
    return sum(tri(v) for v in attributes.as_dict().values())


def ability_cost(cores: tuple[str, ...]) -> int:
    """A core ability costs 1, +1 per core ability already owned."""
    return tri(len(cores))


def validate(build: Build, rules: RuleSet, table: EquipmentTable) -> None:
    """Check budgets against the level and that each loadout is wieldable."""
    res = rules.resources
    for attr, value in build.attributes.as_dict().items():
        if not 0 <= value <= 6:
            raise BudgetError(f"{build.name}: {attr} {value} outside 0..6")
    spent, budget = expertise_cost(build.attributes), res.expertise_budget(build.level)
    if spent > budget:
        raise BudgetError(f"{build.name}: {spent} Expertise spent, {budget} available")
    spent, budget = ability_cost(build.cores), res.ability_budget(build.level)
    if spent > budget:
        raise BudgetError(f"{build.name}: {spent} AP spent, {budget} available")
    if len(set(build.cores)) != len(build.cores):
        raise ConfigError(f"{build.name}: a core ability is listed twice")
    core_proficiencies(build.cores)
    if not build.loadouts:
        raise ConfigError(f"{build.name}: no loadouts")
    for name, lo in build.loadouts:
        table.armor_named(lo.armor)
        if lo.weapon is not None:
            table.weapon(lo.weapon).damage(lo.grip)
        if lo.off_hand is not None:
            if lo.weapon is not None and lo.grip == "two":
                raise ConfigError(f"{build.name}/{name}: two-handed grip with an off hand")
            if not table.is_shield(lo.off_hand):
                table.weapon(lo.off_hand).damage("one")
