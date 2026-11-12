"""Weapons, armor and shields as data (Packet: Weapon Table, Weapon Properties, Armor,
Shields)."""

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
    band_width: int = 0  # squares per range band (0.10.0 bows); v0.9 bows use ranges
    strength: int = 0  # Strength N: the bow's Strength requirement (shortens its bands)
    piercing: int = 0  # Piercing N: ignores N armor (Hammer is Piercing 1)

    def damage(self, grip: str) -> DamageExpr:
        for name, expr in self.grips:
            if name == grip:
                return expr
        raise ConfigError(f"{self.name} has no {grip!r} grip; it has {[g for g, _ in self.grips]}")

    @property
    def quick_draw(self) -> bool:
        return "quick-draw" in self.properties

    @property
    def precise(self) -> bool:
        """Precise (shortbows): Finesse counts like aim, and the aim limit is the higher of
        the damage roll and Finesse."""
        return "precise" in self.properties


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
    strength_requirement: int = 0  # Review F4 option 1's variant; -1 AGI and FIN per point below
    penalty_per_point: int = 1


@dataclass(frozen=True)
class EquipmentTable:
    name: str
    weapons: tuple[Weapon, ...]
    armor: tuple[Armor, ...]
    shields: tuple[Shield, ...]
    step_floor: int
    str_cap: str = "none"  # Review F8 option 3: "die" caps a step's STR term at its die size

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
    properties = frozenset(data.get("properties", ()))
    unknown = set(data) - {
        "base", "reach", "ranged", "ranges", "properties", "grips", "band_width", "strength",
        "piercing",
    }  # fmt: skip
    if unknown:
        raise ConfigError(f"weapon {name}: unknown fields {sorted(unknown)}")
    return Weapon(
        name=name,
        base=int(data["base"]),
        reach=int(data.get("reach", 0 if data.get("ranged") else 1)),
        ranged=bool(data.get("ranged", False)),
        ranges=tuple(int(r) for r in data.get("ranges", ())),
        properties=properties,
        grips=tuple((g, DamageExpr.parse(text)) for g, text in grips.items()),
        band_width=int(data.get("band_width", 0)),
        strength=int(data.get("strength", 0)),
        # Packet: Weapon Properties: Hammer is Piercing 1.
        piercing=int(data.get("piercing", 1 if "hammer" in properties else 0)),
    )


def library_tables() -> list[str]:
    from importlib.resources import files

    folder = files("stamina_engine.data").joinpath("equipment")
    names = {"v0_9"}
    names |= {p.name.removesuffix(".toml") for p in folder.iterdir() if p.name.endswith(".toml")}
    return sorted(names)


def load_table(weapons: str = "v0_9", armor: str = "armor") -> EquipmentTable:
    """An equipment table by name. "v0_9" is the packet's (data/weapons/v0_9.toml with
    data/armor.toml). A variant is data/equipment/<name>.toml: it names its base tables and
    replaces or adds weapons, armor and shields entry by entry, and may set rules."""
    from importlib.resources import files

    overlay: dict[str, Any] = {}
    variant = files("stamina_engine.data").joinpath("equipment", f"{weapons}.toml")
    if weapons != "v0_9" and variant.is_file():
        overlay = load_toml("equipment", f"{weapons}.toml")
        table = overlay.get("table", {})
        base = load_table(str(table.get("weapons", "v0_9")), str(table.get("armor", armor)))
        name = weapons
    else:
        if not files("stamina_engine.data").joinpath("weapons", f"{weapons}.toml").is_file():
            raise ConfigError(f"no equipment table {weapons!r}; known: {library_tables()}")
        w = load_toml("weapons", f"{weapons}.toml")
        a = load_toml(f"{armor}.toml")
        base = EquipmentTable(
            name=weapons,
            weapons=tuple(_weapon(n, d) for n, d in w["weapons"].items()),
            armor=tuple(Armor(name=n, **d) for n, d in a["armor"].items()),
            shields=tuple(Shield(name=n, **d) for n, d in a["shields"].items()),
            step_floor=int(w.get("rules", {}).get("step_floor", 0)),
        )
        if not overlay:
            return base
        name = weapons

    def merge[T: (Weapon, Armor, Shield)](items: tuple[T, ...], new: dict[str, T]) -> tuple[T, ...]:
        kept = [new.pop(i.name, i) for i in items]
        return tuple(kept + list(new.values()))

    rules = overlay.get("rules", {})
    unknown = set(rules) - {"step_floor", "str_cap"}
    if unknown:
        raise ConfigError(f"equipment {weapons}: unknown rules {sorted(unknown)}")
    if rules.get("str_cap", "none") not in ("none", "die"):
        raise ConfigError(f"equipment {weapons}: str_cap is none or die")
    return EquipmentTable(
        name=name,
        weapons=merge(
            base.weapons, {n: _weapon(n, d) for n, d in overlay.get("weapons", {}).items()}
        ),
        armor=merge(
            base.armor, {n: Armor(name=n, **d) for n, d in overlay.get("armor", {}).items()}
        ),
        shields=merge(
            base.shields, {n: Shield(name=n, **d) for n, d in overlay.get("shields", {}).items()}
        ),
        step_floor=int(rules.get("step_floor", base.step_floor)),
        str_cap=str(rules.get("str_cap", base.str_cap)),
    )
