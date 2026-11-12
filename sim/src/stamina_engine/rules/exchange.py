"""One melee attack's roll and resolution (Packet: Attack Procedure, steps 3 and 5-8).

Pure functions: M1's melee procedure calls them and applies the result through StateOps.
"""

from dataclasses import dataclass

from stamina_engine.core.dice import Dice, DiceSource, roll
from stamina_engine.model.derive import Damage, WeaponProfile
from stamina_engine.rules.components.crit import CritRule
from stamina_engine.rules.ruleset import RuleSet

cites = (
    "Packet: Attack Procedure",
    "Packet: Blocking",
    "Packet: Armor",
    "Packet: Critical Hits",
    "Ledger CB-1",
    "Ledger CB-3",
    "Ledger CB-4",
    "Ledger CB-6",
    "Ledger CB-7",
    "Ledger EQ-1",
    "Packet: Ranged Attacks",
    "Packet: Aim",
    "Packet: Range Bands",
    "Packet: Weapon Properties",
    "Ledger RG-1",
    "Ledger RG-2",
    "Ledger RG-3",
)


@dataclass(frozen=True)
class StepRoll:
    faces: tuple[int, ...]
    total: int
    crit_dice: int


@dataclass(frozen=True)
class AttackRoll:
    steps: tuple[StepRoll, ...]
    penalty: int = 0  # subtracted from the total, floored at 0 (range bands)
    limit: int | None = None  # a shot's aim limit: the most HP it can take before crits
    crit_cap: int = 0  # the most critical dice it counts (0: no cap); shots only

    @property
    def total(self) -> int:
        return max(0, sum(s.total for s in self.steps) - self.penalty)

    @property
    def crit_dice(self) -> int:
        n = sum(s.crit_dice for s in self.steps)
        return min(n, self.crit_cap) if self.crit_cap else n


def roll_step(damage: Damage, widen: int, crit: CritRule, source: DiceSource) -> StepRoll:
    """One weapon damage roll. Every die is checked for a crit separately (a greataxe's 2d6
    can give two). The step's total floors at the table's step floor."""
    faces: list[int] = []
    crits = 0
    for dice in damage.dice:
        rolled = roll(dice, source)
        faces.extend(rolled)
        crits += sum(1 for f in rolled if crit.is_crit(f, dice.size, widen))
    total = max(damage.step_floor, sum(faces) + damage.flat)
    return StepRoll(tuple(faces), total, crits)


def roll_attack(
    weapon: WeaponProfile, steps: int, crit: CritRule, source: DiceSource
) -> AttackRoll:
    """Step 3: roll every declared step and note the critical dice."""
    return AttackRoll(
        tuple(roll_step(weapon.damage, weapon.crit_widen, crit, source) for _ in range(steps))
    )


def roll_shot(
    weapon: WeaponProfile,
    aims: int,
    finesse: int,
    band: str,
    rules: RuleSet,
    source: DiceSource,
) -> AttackRoll:
    """A ranged attack's roll (Packet: Ranged Attacks step 3, Aim, Range Bands): the weapon's
    damage, then any free aim dice, then each aim step. An aim die adds its face, plus
    Finesse where ranged.aim_finesse says so (v0.9); at v0.9's medium and long range the
    first one or two aim steps add only Finesse and roll no die. Under precision aim, aim
    steps add nothing and widen the shot's critical range instead. Shots that need more aims
    than were bought miss: callers check required_aims before rolling.

    Linear bands' penalty depends on where the target ends its reaction, so the caller sets
    it afterwards (dataclasses.replace); minus_d6's dice are rolled here. With the aim limit
    on, limit is the weapon's damage roll: its dice and Strength terms (Precise weapons: at
    least Finesse). The range penalty doesn't lower it (Assumptions register). The crit
    switches say which aim dice can be critical and how many critical dice a shot counts."""
    r = rules.ranged
    precision = r.precision_aim()
    widen = weapon.crit_widen + (aims if precision else 0)
    first = roll_step(weapon.damage, widen, rules.crit, source)
    steps = [first]
    if not precision:
        dropped = r.dropped_aim_dice(band)
        aim_widen = rules.crit.aim_widen(weapon.crit_widen)
        fin = finesse if r.aim_adds_finesse() else 0
        free = r.free_aims()
        for i in range(free + aims):
            if i >= free and i - free < dropped:
                steps.append(StepRoll((), max(0, fin), 0))
                continue
            (face,) = roll(Dice(1, r.aim_dice()), source)
            crit = int(aim_widen >= 0 and rules.crit.is_crit(face, r.aim_dice(), aim_widen))
            steps.append(StepRoll((face,), max(0, face + fin), crit))
    penalty = sum(roll(Dice(r.penalty_dice(band), 6), source)) if r.penalty_dice(band) else 0
    limit = shot_limit(weapon, first.faces, finesse, rules)
    return AttackRoll(tuple(steps), penalty, limit, rules.crit.per_shot_cap)


def shot_limit(
    weapon: WeaponProfile, faces: tuple[int, ...], finesse: int, rules: RuleSet
) -> int | None:
    """The aim limit for a shot whose weapon dice rolled faces, or None if off (Packet: Aim;
    Weapon Properties, Precise)."""
    if not rules.ranged.limits_wounds():
        return None
    limit = max(0, sum(faces) + weapon.damage.limit_flat)
    return max(limit, finesse) if weapon.precise else limit


@dataclass(frozen=True)
class Blocks:
    perfect: int = 0
    grazing: int = 0

    @property
    def count(self) -> int:
        return self.perfect + self.grazing


@dataclass(frozen=True)
class Outcome:
    damage: int
    crit_dice: int
    blocks: Blocks
    through_blocks: int  # what the blocks didn't stop, before leaks
    leaked: int
    armor_applied: int  # armor after crit dice ignore some
    after_armor: int
    injury: int


def resolve(
    damage: int,
    crit_dice: int,
    defense: int,
    armor: int,
    blocks: Blocks,
    rules: RuleSet,
    limit: int | None = None,
) -> Outcome:
    """Steps 5-9. Each block subtracts the defense; each graze leaks. Armor (already less
    any Piercing), less 1 per crit die, soaks what got through and the leaks together; a
    shot's aim limit then caps what's left, and the crit effect applies to the result
    (Assumptions register: what armor soaks), capped again by the limit if
    ranged.crit_in_limit says the critical bonus counts toward it."""
    through = max(0, damage - blocks.count * defense)
    leaked = blocks.grazing * rules.blocks.graze_leak
    armor_applied = max(0, armor - rules.crit.armor_ignored(crit_dice))
    after_armor = max(0, through + leaked - armor_applied)
    capped = after_armor if limit is None else min(after_armor, limit)
    injury = rules.crit.finalize(capped, crit_dice)
    if limit is not None and rules.ranged.crit_inside_limit():
        injury = min(injury, limit)
    return Outcome(damage, crit_dice, blocks, through, leaked, armor_applied, after_armor, injury)
