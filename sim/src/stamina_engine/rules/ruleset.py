"""RuleSet: one frozen bundle of rule components, its presets, TOML I/O and digest.

An experiment names a base preset and overrides components; results are stamped with the
digest, which hashes the rules but not the name.
"""

import dataclasses
import hashlib
import json
import tomllib
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path

from stamina_engine.core.errors import ConfigError
from stamina_engine.rules import components as _components  # noqa: F401  (registers variants)
from stamina_engine.rules.components.blocks import BlockRule, PerfectSlope
from stamina_engine.rules.components.crit import CritRule, DoubleOnce, PerDieIfThrough
from stamina_engine.rules.components.defenses import DefenseRule, V09Defenses
from stamina_engine.rules.components.dying import DyingRule, NoShock, SystemShock
from stamina_engine.rules.components.grid import GridRule, V09Grid
from stamina_engine.rules.components.information import InformationRule, V09Information
from stamina_engine.rules.components.movement import MovementRule, V09Movement
from stamina_engine.rules.components.off_turn import Escalation, OffTurnRule
from stamina_engine.rules.components.opportunity import OpportunityRule, V09Opportunity
from stamina_engine.rules.components.ranged import RangedRule, V09Ranged
from stamina_engine.rules.components.resources import ResourceRule, V09Resources
from stamina_engine.rules.components.surcharge import LinearSurcharge, SurchargeRule
from stamina_engine.rules.components.turn_order import TurnOrderRule, V09Initiative
from stamina_engine.rules.components.wounds import NoWounds, WoundRule
from stamina_engine.rules.registry import KINDS, Component, Scalar, from_dict, non_default, to_dict


@dataclass(frozen=True)
class RuleSet:
    name: str
    crit: CritRule
    surcharge: SurchargeRule
    blocks: BlockRule
    defenses: DefenseRule
    resources: ResourceRule
    wounds: WoundRule
    movement: MovementRule
    off_turn: OffTurnRule
    opportunity: OpportunityRule
    ranged: RangedRule
    turn_order: TurnOrderRule
    dying: DyingRule
    information: InformationRule
    grid: GridRule

    def __post_init__(self) -> None:
        for kind in KINDS:
            component = getattr(self, kind)
            if not isinstance(component, Component) or component.kind != kind:
                raise ConfigError(f"RuleSet.{kind} must be a {kind} component")

    def with_(self, name: str | None = None, **changes: Component) -> "RuleSet":
        """A copy with whole components replaced. Without a name, a changed copy is named
        "<base>+modified" so it can't pass for its base preset."""
        unknown = set(changes) - set(KINDS)
        if unknown:
            raise ConfigError(f"unknown component kinds {sorted(unknown)}")
        if name is None:
            name = f"{self.name}+modified" if changes else self.name
        # __post_init__ checks each component is of its slot's kind.
        return dataclasses.replace(self, name=name, **changes)  # type: ignore[arg-type]

    def override(self, overrides: Mapping[str, object], name: str | None = None) -> "RuleSet":
        """Apply TOML-style overrides: {kind: {"kind": variant?, param: value...}}."""
        changes: dict[str, Component] = {}
        for kind, data in overrides.items():
            if kind not in KINDS:
                raise ConfigError(f"unknown component kind {kind!r}")
            if not isinstance(data, Mapping):
                raise ConfigError(f"override for {kind} must be a table")
            changes[kind] = from_dict(kind, data, base=getattr(self, kind))
        return self.with_(name=name, **changes)

    def components(self) -> dict[str, Component]:
        return {kind: getattr(self, kind) for kind in KINDS}

    def to_toml(self) -> str:
        lines = ["[ruleset]", f"name = {_toml_value(self.name)}"]
        for kind, component in self.components().items():
            lines.append("")
            lines.append(f"[ruleset.{kind}]")
            lines.extend(f"{k} = {_toml_value(v)}" for k, v in to_dict(component).items())
        return "\n".join(lines) + "\n"

    def digest(self) -> str:
        """SHA-256 of each component's variant and its parameters that aren't at their
        default; the name is excluded.

        Leaving defaults out means a new switch whose default keeps the current rule leaves
        every existing digest unchanged, the baseline's included. In exchange, a released
        default never changes (tests/golden/test_component_defaults.py pins them): to change
        a rule, set the new value where it applies, in a preset for the baseline, and the
        digest changes with it. to_toml() still writes every parameter.
        """
        lines: list[str] = []
        for kind, component in self.components().items():
            lines.append(f"[ruleset.{kind}]")
            lines.append(f"kind = {_toml_value(component.variant)}")
            lines.extend(f"{k} = {_toml_value(v)}" for k, v in non_default(component).items())
        return hashlib.sha256(("\n".join(lines) + "\n").encode()).hexdigest()

    def short_digest(self) -> str:
        return self.digest()[:12]


def _toml_value(value: Scalar) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    return json.dumps(value)


def from_toml(text: str) -> RuleSet:
    """Load a RuleSet. With base = "<preset>", unlisted components come from that preset;
    without it, every component must be listed."""
    data = tomllib.loads(text)
    table = data.get("ruleset")
    if not isinstance(table, dict):
        raise ConfigError("missing [ruleset] table")
    name = table.get("name")
    base_name = table.get("base")
    overrides = {k: v for k, v in table.items() if k not in ("name", "base")}
    if base_name is not None:
        if not isinstance(base_name, str):
            raise ConfigError("base must be a preset name")
        base = preset(base_name)
        return base.override(overrides, name=name if isinstance(name, str) else None)
    missing = [k for k in KINDS if k not in overrides]
    if missing:
        raise ConfigError(f"no base preset and no tables for {missing}")
    if not isinstance(name, str):
        raise ConfigError("ruleset needs a name")
    built = {kind: from_dict(kind, overrides[kind]) for kind in KINDS}
    extra = set(overrides) - set(KINDS)
    if extra:
        raise ConfigError(f"unknown component kinds {sorted(extra)}")
    return RuleSet(name=name, **built)  # type: ignore[arg-type]


def v0_9() -> RuleSet:
    """The packet as written, plus the Assumptions register's defaults for silent rules."""
    return RuleSet(
        name="v0.9",
        crit=DoubleOnce(),
        surcharge=LinearSurcharge(),
        blocks=PerfectSlope(),
        defenses=V09Defenses(),
        resources=V09Resources(),
        wounds=NoWounds(),
        movement=V09Movement(),
        off_turn=Escalation(),
        opportunity=V09Opportunity(),
        ranged=V09Ranged(),
        turn_order=V09Initiative(),
        dying=SystemShock(),
        information=V09Information(),
        grid=V09Grid(),
    )


def _resources_0_9_1(hp_base: int) -> V09Resources:
    """0.9.1's HP from even Strength and Intelligence's AP rules, on a base HP."""
    return V09Resources(
        hp_base=hp_base,
        hp_strength="per_even",
        core_discount="odd_intelligence",
        bonus_ap="even_intelligence",
    )


def v0_9_1() -> RuleSet:
    """Packet 0.9.1 (rules/CHANGELOG.md): no opportunity-attack cap; extra on-turn movement
    1 square a purchase; initiative 2d12 + Cunning; maximum HP 6 + 2 per even Strength; the
    dying roll adds Will; Intelligence's core-ability discount and bonus Ability Points."""
    return v0_9().with_(
        name="v0.9.1",
        opportunity=V09Opportunity(cap_rule="none"),
        movement=V09Movement(extra_squares="one"),
        turn_order=V09Initiative(bonus="cunning"),
        resources=_resources_0_9_1(hp_base=6),
        dying=SystemShock(roll_attribute="will"),
    )


def v0_9_2() -> RuleSet:
    """Packet 0.9.2: 0.9.1, with +1 per critical die only if damage gets past blocks and
    armor (no doubling), and maximum HP 8 + 2 per even Strength."""
    return v0_9_1().with_(
        name="v0.9.2",
        crit=PerDieIfThrough(),
        resources=_resources_0_9_1(hp_base=8),
    )


def v0_9_3() -> RuleSet:
    """Packet 0.9.3: the same fight rules as 0.9.2. Its changes are all after a fight
    (healing below 0 HP, dying rolls once a fight ends), which the engine doesn't play yet,
    so this preset has 0.9.2's components and digest. The campaign layer's rest rules will
    extend it (sim/docs/CAMPAIGN_PLAN.md)."""
    return v0_9_2().with_(name="v0.9.3")


def v0_10_0() -> RuleSet:
    """Packet 0.10.0, the ranged package: 0.9.3 with band widths and -2 per further band
    measured after the target's reaction; shots as actions with one free aim die; aim steps
    1d6 with no Finesse; the aim limit; aim dice never critical; cover +1 / +2; +1 Ranged
    Defense for moving in reaction to a shot and +1 per even Agility (armor-adjusted, the
    dodge_folded mode); point-blank OAs only from enemies in reach both when the shot is
    declared and when they happen. The bows, Piercing, Precise and the +1 / +1 shield are
    equipment: run it with the v0_10 equipment table (derive refuses v0.9's bows)."""
    base = v0_9_3()
    return base.with_(
        name="v0.10.0",
        crit=PerDieIfThrough(aim_dice_can_crit=False),
        defenses=V09Defenses(ranged_mode="dodge_folded"),
        ranged=V09Ranged(
            bands="linear",
            shot_action=True,
            aim_finesse=False,
            free_aim_dice=1,
            aim_limit="damage_roll",
            half_cover=1,
            three_quarter_cover=2,
            range_measured="after_reaction",
            reaction_bonus=1,
        ),
        opportunity=V09Opportunity(cap_rule="none", point_blank_eligible="declared_and_resolution"),
    )


def v0_10_1() -> RuleSet:
    """Packet 0.10.1: 0.10.0 with one rule changed. A grazing block leaks 1 of the damage
    it stopped, so one with nothing left to stop leaks nothing (perfect blocks count
    first). The packet's other 0.10.1 entries (paying to avoid an opportunity attack before
    the enemy decides; Melee Defense against a shot when the shooter is within the target's
    reach) are already how every preset plays."""
    base = v0_10_0()
    blocks = dataclasses.replace(base.blocks, graze_needs_stop=True)
    return base.with_(name="v0.10.1", blocks=blocks)


def v0_10_0_cover_only() -> RuleSet:
    """Not a packet version: the designer's "reaction changes cover only" package on 0.10.0.
    The range penalty and Melee vs Ranged Defense are judged where the target was when the
    shot was declared; a reaction still earns cover and the +1 Ranged Defense for moving."""
    base = v0_10_0()
    assert isinstance(base.ranged, V09Ranged)
    ranged = dataclasses.replace(
        base.ranged, range_measured="declaration", defense_timing="declaration"
    )
    return base.with_(name="v0.10.0-cover-only", ranged=ranged)


def v0_10_0_crit_c_prime() -> RuleSet:
    """Not a packet version: 0.10.0 with the solver study's crit rule C': aim dice can be
    critical, but only on a 6, and a shot counts at most one critical die."""
    base = v0_10_0()
    crit = dataclasses.replace(
        base.crit, aim_dice_can_crit=True, aim_dice_widen=False, per_shot_cap=1
    )
    return base.with_(name="v0.10.0-crit-c-prime", crit=crit)


def v0_10_0_crit_c() -> RuleSet:
    """Not a packet version: 0.10.0 with the solver study's crit rule C: every die can be
    critical (Finesse widens aim dice too), and a shot counts at most one critical die."""
    base = v0_10_0()
    crit = dataclasses.replace(base.crit, aim_dice_can_crit=True, per_shot_cap=1)
    return base.with_(name="v0.10.0-crit-c", crit=crit)


def review_candidate() -> RuleSet:
    """The review's candidate: +2 surcharge per prior action, v0.9 crits."""
    return v0_9().with_(name="review-candidate", surcharge=LinearSurcharge(slope=2))


def review_sim() -> RuleSet:
    """The review simulator's quirks, for parity runs only (see CLAUDE.md, The oracle).

    Initiative ties go to the first-listed combatant, duels have no off-turn movement or
    opportunity attacks, and there is no System Shock: a creature at 0 HP or below is out and
    rolls nothing. Its crit modes are selected per run with crit overrides.
    """
    base = v0_9()
    return base.with_(
        name="review-sim",
        turn_order=V09Initiative(tiebreak="list_order"),
        off_turn=Escalation(enabled=False),
        opportunity=V09Opportunity(enabled=False),
        dying=NoShock(),
    )


def exp_0_11_0() -> RuleSet:
    """Not a baseline preset: an experiment's reading of packet 0.11.0's movement on 0.10.1
    (exp/holds). One dash (an action on the one escalation, 1 square + 1 per odd Agility,
    on or off your turn), the escalation reset when your turn ends, a dash phase before
    every turn with the highest in initiative first, and the placeholder opportunity
    attack: one step at the weapon's base cost, not an action, no cap."""
    base = v0_10_1()
    assert isinstance(base.movement, V09Movement)
    assert isinstance(base.off_turn, Escalation)
    assert isinstance(base.opportunity, V09Opportunity)
    return base.with_(
        name="exp-0.11.0",
        movement=dataclasses.replace(
            base.movement, extra_squares="agility", leftover="move", extra_action=True
        ),
        off_turn=dataclasses.replace(
            base.off_turn,
            order="descending_initiative",
            track="unified",
            restart=True,
            opening=True,
        ),
        opportunity=dataclasses.replace(
            base.opportunity, cap_rule="none", pricing="fresh", max_steps=1
        ),
    )


def exp_holds() -> RuleSet:
    """Not a baseline preset: exp-0.11.0 with the designer's hold rule of 2026-11-17. An
    opportunity attack's steps cost base + 1 per earlier step of that attack, within a cap
    of 1 + 1 per odd Finesse plus the tokens of a hold on that target; leaving costs 1 + a
    hold's tokens for the first square."""
    base = exp_0_11_0()
    assert isinstance(base.opportunity, V09Opportunity)
    return base.with_(
        name="exp-holds",
        opportunity=dataclasses.replace(
            base.opportunity, cap_rule="flat", max_steps=0, holds=True
        ),
    )


def exp_holds_per_square() -> RuleSet:
    """exp-holds with the cap added again for each square the mover leaves within your
    reach without paying you, pooled for one move."""
    base = exp_holds()
    assert isinstance(base.opportunity, V09Opportunity)
    return base.with_(
        name="exp-holds-per-square",
        opportunity=dataclasses.replace(base.opportunity, per_square_cap=True),
    )


def exp_holds_next_turn() -> RuleSet:
    """exp-holds with the designer's second timing (2026-11-17): holds are set at the end
    of your turn before you recover, and the tokens stay out through your next turn, coming
    back at its end right before you recover (when you may set new ones)."""
    base = exp_holds()
    assert isinstance(base.opportunity, V09Opportunity)
    return base.with_(
        name="exp-holds-next-turn",
        opportunity=dataclasses.replace(
            base.opportunity, hold_return="turn_end", hold_set="before_recovery"
        ),
    )


def exp_holds_next_turn_break() -> RuleSet:
    """exp-holds-next-turn, and a holder that loses HP drops its holds (tokens stay out)."""
    base = exp_holds_next_turn()
    assert isinstance(base.opportunity, V09Opportunity)
    return base.with_(
        name="exp-holds-next-turn-break",
        opportunity=dataclasses.replace(base.opportunity, hold_breaks_on_injury=True),
    )


def exp_holds_placeholder() -> RuleSet:
    """The designer's placeholder hold rules (2026-11-17): exp-holds-next-turn-break, and a
    wound that lowers maximum stamina takes tokens before ready stamina."""
    base = exp_holds_next_turn_break()
    assert isinstance(base.opportunity, V09Opportunity)
    return base.with_(
        name="exp-holds-placeholder",
        opportunity=dataclasses.replace(base.opportunity, hold_wound_clamp="tokens_first"),
    )


def exp_0_11_1() -> RuleSet:
    """Not a baseline preset: an experiment's reading of packet 0.11.1 on 0.10.1. The
    movement of exp-0.11.0 and the hold rules of exp-holds-placeholder, with holds allowed on
    any enemy, in reach or not. Where the packet lets a creature choose what to lose when it
    would go over its maximum stamina, the engine takes tokens first after a wound (always the
    better choice once the wound has ended the holds) and keeps them when recovery would go
    over. The spear's reach only in two hands isn't modelled: the equipment is v0.10.1's,
    and its spear builds hold the spear one-handed with a shield and still reach 2."""
    base = exp_holds_placeholder()
    assert isinstance(base.opportunity, V09Opportunity)
    return base.with_(
        name="exp-0.11.1",
        opportunity=dataclasses.replace(base.opportunity, hold_targets="any"),
    )


def exp_holds_next_turn_half() -> RuleSet:
    """exp-holds-next-turn with holds set after recovering, at most half your ready stamina."""
    base = exp_holds_next_turn()
    assert isinstance(base.opportunity, V09Opportunity)
    return base.with_(
        name="exp-holds-next-turn-half",
        opportunity=dataclasses.replace(
            base.opportunity, hold_set="after_recovery", hold_max_percent=50
        ),
    )


BASELINE = "v0.10.1"
"""The preset the engine's scenarios, suites and defaults use: the current packet. Moving the
baseline to a new packet version is this one line (and the pinned hashes it moves)."""

PRESETS: dict[str, Callable[[], RuleSet]] = {
    "v0.9": v0_9,
    "v0.9.1": v0_9_1,
    "v0.9.2": v0_9_2,
    "v0.9.3": v0_9_3,
    "v0.10.0": v0_10_0,
    "v0.10.1": v0_10_1,
    "v0.10.0-cover-only": v0_10_0_cover_only,
    "v0.10.0-crit-c-prime": v0_10_0_crit_c_prime,
    "v0.10.0-crit-c": v0_10_0_crit_c,
    "review-candidate": review_candidate,
    "review-sim": review_sim,
    "exp-0.11.0": exp_0_11_0,
    "exp-holds": exp_holds,
    "exp-holds-per-square": exp_holds_per_square,
    "exp-holds-next-turn": exp_holds_next_turn,
    "exp-holds-next-turn-break": exp_holds_next_turn_break,
    "exp-holds-next-turn-half": exp_holds_next_turn_half,
    "exp-holds-placeholder": exp_holds_placeholder,
    "exp-0.11.1": exp_0_11_1,
}


def load_ruleset(spec: str) -> RuleSet:
    """A preset name, or a path to a RuleSet TOML file."""
    if spec.endswith(".toml"):
        try:
            text = Path(spec).read_text()
        except OSError as exc:
            raise ConfigError(f"can't read RuleSet file {spec}: {exc}") from exc
        return from_toml(text)
    return preset(spec)


def preset(name: str) -> RuleSet:
    try:
        return PRESETS[name]()
    except KeyError:
        raise ConfigError(f"no preset {name!r}; known: {sorted(PRESETS)}") from None
