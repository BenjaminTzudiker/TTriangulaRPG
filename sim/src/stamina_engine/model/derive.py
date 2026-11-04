"""derive(build, ruleset) -> CombatProfile. Armor penalties first, then every formula."""

from dataclasses import dataclass

from stamina_engine.core.dice import Dice
from stamina_engine.model.build import Attributes, Build, Loadout, core_proficiencies, validate
from stamina_engine.model.equipment import DamageExpr, EquipmentTable, Weapon, load_table
from stamina_engine.rules.ruleset import RuleSet

cites = (
    "Packet: Armor",
    "Packet: Defenses",
    "Packet: Stamina",
    "Packet: Weapon Table",
    "Ledger EQ-1",
    "Ledger EQ-2",
    "Ledger DF-1",
)


@dataclass(frozen=True)
class Damage:
    """A weapon's damage resolved against the wielder's attributes."""

    dice: tuple[Dice, ...]
    flat: int
    chosen: tuple[str, ...]  # the attribute taken for each term, in order
    step_floor: int = 0

    @property
    def mean_x2(self) -> int:
        """Twice the mean per step, ignoring the floor (exact when the floor never binds)."""
        return sum(d.mean_x2 for d in self.dice) + 2 * self.flat

    def __str__(self) -> str:
        text = " + ".join(str(d) for d in self.dice)
        return f"{text} + {self.flat}" if self.flat >= 0 else f"{text} - {-self.flat}"


@dataclass(frozen=True)
class WeaponProfile:
    name: str
    grip: str
    base: int
    reach: int
    ranged: bool
    quick_draw: bool
    proficient: bool
    damage: Damage
    crit_widen: int


@dataclass(frozen=True)
class LoadoutProfile:
    name: str
    attributes: Attributes  # after armor penalties
    armor_name: str
    armor: int
    shield: str | None
    weapon: WeaponProfile | None
    off_hand_weapon: WeaponProfile | None
    melee_defense: int
    ranged_defense: int
    dodge_defense: int
    movement: int
    squares_per_purchase: int  # off-turn
    initiative_bonus: int
    oa_cap: int  # with the main weapon (the cap can depend on the weapon: F9 option 1)
    extra_squares_per_purchase: int = 0  # extra on-turn movement


@dataclass(frozen=True)
class CombatProfile:
    build: str
    level: int
    hp_max: int
    stamina_max: int  # at full HP
    recovery: int
    strain_max: int
    start_stamina: int
    start_strain: int
    loadouts: tuple[LoadoutProfile, ...]
    ruleset_digest: str

    @property
    def main(self) -> LoadoutProfile:
        return self.loadouts[0]

    def loadout(self, name: str) -> LoadoutProfile:
        for lo in self.loadouts:
            if lo.name == name:
                return lo
        raise KeyError(name)


def resolve_damage(expr: DamageExpr, attributes: Attributes, step_floor: int) -> Damage:
    """Add the attribute terms; for "X or Y" take the higher, the first listed on a tie."""
    flat = expr.flat
    chosen: list[str] = []
    for term in expr.terms:
        best = max(term.choices, key=attributes.get)  # max() keeps the first on ties
        chosen.append(best)
        flat += term.multiplier * attributes.get(best)
    return Damage(expr.dice, flat, tuple(chosen), step_floor)


def penalized(attributes: Attributes, strength_requirement: int, per_point: int) -> Attributes:
    """Armor's Strength penalties lower Agility and Finesse themselves (Packet: Armor)."""
    deficit = max(0, strength_requirement - attributes.STR) * per_point
    if not deficit:
        return attributes
    return Attributes(
        STR=attributes.STR,
        AGI=attributes.AGI - deficit,
        FIN=attributes.FIN - deficit,
        INT=attributes.INT,
        WIL=attributes.WIL,
        CUN=attributes.CUN,
    )


def _weapon_profile(
    weapon: Weapon,
    grip: str,
    attrs: Attributes,
    proficient: frozenset[str],
    rules: RuleSet,
    table: EquipmentTable,
) -> WeaponProfile:
    return WeaponProfile(
        name=weapon.name,
        grip=grip,
        base=weapon.base,
        reach=weapon.reach,
        ranged=weapon.ranged,
        quick_draw=weapon.quick_draw,
        proficient=weapon.name in proficient,
        damage=resolve_damage(weapon.damage(grip), attrs, table.step_floor),
        crit_widen=rules.crit.widen(attrs.FIN),
    )


def _loadout_profile(
    name: str,
    lo: Loadout,
    build: Build,
    proficient: frozenset[str],
    rules: RuleSet,
    table: EquipmentTable,
) -> LoadoutProfile:
    armor = table.armor_named(lo.armor)
    attrs = penalized(build.attributes, armor.strength_requirement, armor.penalty_per_point)
    main = (
        _weapon_profile(table.weapon(lo.weapon), lo.grip, attrs, proficient, rules, table)
        if lo.weapon is not None
        else None
    )
    shield = table.shield(lo.off_hand) if lo.off_hand and table.is_shield(lo.off_hand) else None
    off = (
        _weapon_profile(table.weapon(lo.off_hand), "one", attrs, proficient, rules, table)
        if lo.off_hand is not None and shield is None
        else None
    )
    proficient_melee = main is not None and main.proficient and not main.ranged
    second = off is not None and off.proficient and not off.ranged
    shield_md = shield.melee if shield else 0
    shield_rd = shield.ranged if shield else 0
    d, mv = rules.defenses, rules.movement
    return LoadoutProfile(
        name=name,
        attributes=attrs,
        armor_name=armor.name,
        armor=armor.value,
        shield=shield.name if shield else None,
        weapon=main,
        off_hand_weapon=off,
        melee_defense=d.melee(
            attrs.AGI, attrs.FIN, armor.agility_step, proficient_melee, second, shield_md
        ),
        ranged_defense=d.ranged(attrs.AGI, shield_rd),
        dodge_defense=d.dodge(attrs.AGI, armor.agility_step),
        movement=mv.free_movement(attrs.AGI),
        squares_per_purchase=mv.squares_per_purchase(attrs.AGI),
        initiative_bonus=rules.turn_order.initiative_bonus(attrs.AGI, attrs.CUN),
        oa_cap=rules.opportunity.cap(attrs.FIN, main.base if main is not None else 0),
        extra_squares_per_purchase=mv.extra_squares_per_purchase(attrs.AGI),
    )


def derive(build: Build, rules: RuleSet, table: EquipmentTable | None = None) -> CombatProfile:
    table = table or load_table()
    validate(build, rules, table)
    res = rules.resources
    proficient = build.proficiencies | core_proficiencies(build.cores)
    hp = res.hp_max(build.attributes.STR)
    stamina_max = res.max_stamina(hp, build.level)
    return CombatProfile(
        build=build.name,
        level=build.level,
        hp_max=hp,
        stamina_max=stamina_max,
        recovery=res.recovery(build.level),
        strain_max=res.strain_max(build.level),
        start_stamina=stamina_max,
        start_strain=0,
        loadouts=tuple(
            _loadout_profile(n, lo, build, proficient, rules, table) for n, lo in build.loadouts
        ),
        ruleset_digest=rules.digest(),
    )
