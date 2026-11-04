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
    penalty: int = 0  # subtracted from the total, floored at 0 (range-band variant)

    @property
    def total(self) -> int:
        return max(0, sum(s.total for s in self.steps) - self.penalty)

    @property
    def crit_dice(self) -> int:
        return sum(s.crit_dice for s in self.steps)


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
    """A ranged attack's roll (Packet: Ranged Attacks step 4, Aim, Range Bands): the weapon's
    damage, then each aim step (aim_die + Finesse; at medium and long range the first one or
    two add only Finesse and roll no die). Under precision aim, aim steps add nothing and
    widen the shot's critical range instead. Shots that need more aims than were bought
    miss: callers check required_aims before rolling."""
    r = rules.ranged
    precision = r.precision_aim()
    widen = weapon.crit_widen + (aims if precision else 0)
    steps = [roll_step(weapon.damage, widen, rules.crit, source)]
    if not precision:
        dropped = r.dropped_aim_dice(band)
        aim_widen = weapon.crit_widen if rules.crit.aim_dice_can_crit else -1
        for i in range(aims):
            if i < dropped:
                steps.append(StepRoll((), max(0, finesse), 0))
                continue
            (face,) = roll(Dice(1, r.aim_dice()), source)
            crit = int(aim_widen >= 0 and rules.crit.is_crit(face, r.aim_dice(), aim_widen))
            steps.append(StepRoll((face,), max(0, face + finesse), crit))
    penalty = sum(roll(Dice(r.penalty_dice(band), 6), source)) if r.penalty_dice(band) else 0
    return AttackRoll(tuple(steps), penalty)


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
    damage: int, crit_dice: int, defense: int, armor: int, blocks: Blocks, rules: RuleSet
) -> Outcome:
    """Steps 5-8. Each block subtracts the defense; each graze leaks. Armor, less 1 per crit
    die, soaks what got through and the leaks together; the crit effect applies to what
    remains (Assumptions register: what armor soaks)."""
    through = max(0, damage - blocks.count * defense)
    leaked = blocks.grazing * rules.blocks.graze_leak
    armor_applied = max(0, armor - rules.crit.armor_ignored(crit_dice))
    after_armor = max(0, through + leaked - armor_applied)
    injury = rules.crit.finalize(after_armor, crit_dice)
    return Outcome(damage, crit_dice, blocks, through, leaked, armor_applied, after_armor, injury)
