"""derive(build, ruleset) -> CombatProfile. Armor penalties first, then every formula."""

from dataclasses import dataclass

from stamina_engine.core.dice import Dice
from stamina_engine.core.errors import ConfigError
from stamina_engine.model.build import Attributes, Build, Loadout, core_proficiencies, validate
from stamina_engine.model.equipment import DamageExpr, EquipmentTable, Weapon, load_table
from stamina_engine.rules.ruleset import RuleSet

cites = (
    "Packet: Armor",
    "Packet: Defenses",
    "Packet: Stamina",
    "Packet: Weapon Table",
    "Packet: Weapon Properties",
    "Packet: Range Bands",
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
    # The part of flat that counts toward a shot's damage roll for the aim limit (Packet:
    # Aim): Strength terms and constants. Other attributes (the shortbow's Finesse) count
    # like aim.
    limit_flat: int = 0

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
    ranges: tuple[int, ...] = ()  # short, medium, long (squares), for ranged weapons
    light: bool = False  # tagged light in the table (Review F8 option 2's surcharge discount)
    band_width: int = 0  # the wielder's band width (linear bands); 0 or less can't shoot
    piercing: int = 0  # armor the weapon ignores (Piercing N)
    precise: bool = False  # Precise: the aim limit is at least the wielder's Finesse


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
    oa_cap: int | None  # with the main weapon (F9 option 1 ties it to the weapon); None: no cap
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
    abilities: tuple[str, ...] = ()  # each core's ability ("fighter_core"...) and candidates

    @property
    def main(self) -> LoadoutProfile:
        return self.loadouts[0]

    def loadout(self, name: str) -> LoadoutProfile:
        for lo in self.loadouts:
            if lo.name == name:
                return lo
        raise KeyError(name)


def resolve_damage(
    expr: DamageExpr, attributes: Attributes, step_floor: int, str_cap: str = "none"
) -> Damage:
    """Add the attribute terms; for "X or Y" take the higher, the first listed on a tie.
    With str_cap = "die" (Review F8 option 3) a Strength term adds at most the weapon's
    largest die size."""
    flat = expr.flat
    limit_flat = expr.flat
    chosen: list[str] = []
    cap = max((d.size for d in expr.dice), default=0)
    for term in expr.terms:
        best = max(term.choices, key=attributes.get)  # max() keeps the first on ties
        chosen.append(best)
        value = term.multiplier * attributes.get(best)
        if str_cap == "die" and best == "STR":
            value = min(value, cap)
        flat += value
        if best == "STR":
            limit_flat += value
    return Damage(expr.dice, flat, tuple(chosen), step_floor, limit_flat)


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
    r = rules.ranged
    if weapon.ranged and r.uses_band_width() and weapon.band_width <= 0:
        raise ConfigError(
            f"{weapon.name} has no band width, which {rules.name}'s range bands need; "
            "use an equipment table with 0.10.0's bows (v0_10)"
        )
    if weapon.ranged and not r.uses_band_width() and not weapon.ranges:
        raise ConfigError(
            f"{weapon.name} has no short / medium / long ranges, which {rules.name}'s range "
            "bands need; use an equipment table with v0.9's bows (v0_9)"
        )
    return WeaponProfile(
        name=weapon.name,
        grip=grip,
        base=weapon.base,
        reach=weapon.reach,
        ranged=weapon.ranged,
        quick_draw=weapon.quick_draw,
        proficient=weapon.name in proficient,
        damage=resolve_damage(weapon.damage(grip), attrs, table.step_floor, table.str_cap),
        crit_widen=rules.crit.widen(attrs.FIN),
        ranges=weapon.ranges,
        light="light" in weapon.properties,
        band_width=(
            r.band_width(weapon.band_width, attrs.FIN, attrs.STR, weapon.strength)
            if weapon.ranged
            else 0
        ),
        piercing=weapon.piercing,
        precise=weapon.precise,
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
    held = table.shield(lo.off_hand) if lo.off_hand and table.is_shield(lo.off_hand) else None
    if held is not None and held.strength_requirement:
        # A heavy shield's Strength requirement penalizes separately from armor's.
        attrs = penalized(attrs, held.strength_requirement, held.penalty_per_point)
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
            attrs.AGI,
            attrs.FIN,
            armor.agility_step,
            proficient_melee,
            second,
            shield_md,
            proficient_melee and main is not None and main.grip == "two",
        ),
        ranged_defense=d.ranged(attrs.AGI, shield_rd, armor.agility_step),
        dodge_defense=d.dodge(attrs.AGI, armor.agility_step),
        movement=mv.free_movement(attrs.AGI),
        squares_per_purchase=mv.squares_per_purchase(attrs.AGI),
        initiative_bonus=rules.turn_order.initiative_bonus(attrs.AGI, attrs.CUN),
        oa_cap=rules.opportunity.cap(attrs.FIN, main.base if main is not None else 0),
        extra_squares_per_purchase=mv.extra_squares_per_purchase(attrs.AGI),
    )


def equipment_for(rules: RuleSet) -> str:
    """The packet's equipment table for a RuleSet's range bands: 0.10.0's bows (with band
    widths, and the +1 / +1 shield) under linear bands, v0.9's (three ranges) otherwise.
    What a scenario or table uses when it names none."""
    return "v0_10" if rules.ranged.uses_band_width() else "v0_9"


def derive(build: Build, rules: RuleSet, table: EquipmentTable | None = None) -> CombatProfile:
    table = table or load_table(equipment_for(rules))
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
        abilities=tuple(f"{core}_core" for core in build.cores) + build.abilities,
    )
