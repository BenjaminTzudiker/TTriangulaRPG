"""Weapons, armor and shields as data (Packet: Weapon Table, Armor, Shields)."""

import re
from dataclasses import dataclass
from typing import Any

from stamina_engine.core.dice import Dice
from stamina_engine.core.errors import ConfigError
from stamina_engine.data import load_toml

ATTRIBUTES = ("STR", "AGI", "FIN", "INT", "WIL", "CUN")

_DICE = re.compile(r"^(\d+)d(\d+)$")
_FLAT = re.compile(r"^-?\d+$")
_ATTR = re.compile(r"^(?:(\d+)\s*[*×]\s*)?(?:max\(([^)]*)\)|([A-Z]{3}))$")


@dataclass(frozen=True)
class AttrTerm:
    """multiplier x one attribute, or the best of several ("STR or AGI")."""

    multiplier: int
    choices: tuple[str, ...]

    def __str__(self) -> str:
        inner = self.choices[0] if len(self.choices) == 1 else f"max({', '.join(self.choices)})"
        return inner if self.multiplier == 1 else f"{self.multiplier}*{inner}"


@dataclass(frozen=True)
class DamageExpr:
    """Damage per step or shot, such as 1d10 + max(STR, AGI) + FIN."""

    dice: tuple[Dice, ...]
    terms: tuple[AttrTerm, ...]
    flat: int = 0

    @staticmethod
    def parse(text: str) -> "DamageExpr":
        dice: list[Dice] = []
        terms: list[AttrTerm] = []
        flat = 0
        for raw in text.split("+"):
            part = raw.strip()
            if m := _DICE.match(part):
                dice.append(Dice(int(m.group(1)), int(m.group(2))))
            elif _FLAT.match(part):
                flat += int(part)
            elif m := _ATTR.match(part):
                mult = int(m.group(1)) if m.group(1) else 1
                names = m.group(2).split(",") if m.group(2) else [m.group(3)]
                choices = tuple(n.strip() for n in names)
                if not choices or any(c not in ATTRIBUTES for c in choices):
                    raise ConfigError(f"bad attribute term {part!r} in {text!r}")
                terms.append(AttrTerm(mult, choices))
            else:
                raise ConfigError(f"can't parse {part!r} in damage {text!r}")
        return DamageExpr(tuple(dice), tuple(terms), flat)

    def __str__(self) -> str:
        parts = [str(d) for d in self.dice] + [str(t) for t in self.terms]
        if self.flat:
            parts.append(str(self.flat))
        return " + ".join(parts)


@dataclass(frozen=True)
class Weapon:
    name: str
    base: int
    reach: int
    ranged: bool
    ranges: tuple[int, ...]
    properties: frozenset[str]
    grips: tuple[tuple[str, DamageExpr], ...]  # ("one" | "two", damage)

    def damage(self, grip: str) -> DamageExpr:
        for name, expr in self.grips:
            if name == grip:
                return expr
        raise ConfigError(f"{self.name} has no {grip!r} grip; it has {[g for g, _ in self.grips]}")

    @property
    def quick_draw(self) -> bool:
        return "quick-draw" in self.properties


@dataclass(frozen=True)
class Armor:
    name: str
    value: int
    agility_step: int
    strength_requirement: int
    penalty_per_point: int = 1


@dataclass(frozen=True)
class Shield:
    name: str
    melee: int
    ranged: int


@dataclass(frozen=True)
class EquipmentTable:
    name: str
    weapons: tuple[Weapon, ...]
    armor: tuple[Armor, ...]
    shields: tuple[Shield, ...]
    step_floor: int

    def weapon(self, name: str) -> Weapon:
        return _find(self.weapons, name, "weapon")

    def armor_named(self, name: str) -> Armor:
        return _find(self.armor, name, "armor")

    def shield(self, name: str) -> Shield:
        return _find(self.shields, name, "shield")

    def is_shield(self, name: str) -> bool:
        return any(s.name == name for s in self.shields)


def _find[T: (Weapon, Armor, Shield)](items: tuple[T, ...], name: str, what: str) -> T:
    for item in items:
        if item.name == name:
            return item
    raise ConfigError(f"no {what} {name!r}")


def _weapon(name: str, data: dict[str, Any]) -> Weapon:
    grips = data.get("grips", {})
    if not grips:
        raise ConfigError(f"weapon {name} has no grips")
    return Weapon(
        name=name,
        base=int(data["base"]),
        reach=int(data.get("reach", 0 if data.get("ranged") else 1)),
        ranged=bool(data.get("ranged", False)),
        ranges=tuple(int(r) for r in data.get("ranges", ())),
        properties=frozenset(data.get("properties", ())),
        grips=tuple((g, DamageExpr.parse(text)) for g, text in grips.items()),
    )


def load_table(weapons: str = "v0_9", armor: str = "armor") -> EquipmentTable:
    """Load a weapon table from data/weapons/<weapons>.toml and armor and shields."""
    w = load_toml("weapons", f"{weapons}.toml")
    a = load_toml(f"{armor}.toml")
    return EquipmentTable(
        name=weapons,
        weapons=tuple(_weapon(n, d) for n, d in w["weapons"].items()),
        armor=tuple(Armor(name=n, **d) for n, d in a["armor"].items()),
        shields=tuple(Shield(name=n, **d) for n, d in a["shields"].items()),
        step_floor=int(w.get("rules", {}).get("step_floor", 0)),
    )
