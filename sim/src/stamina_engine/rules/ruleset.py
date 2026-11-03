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

from stamina_engine.core.errors import ConfigError
from stamina_engine.rules import components as _components  # noqa: F401  (registers variants)
from stamina_engine.rules.components.blocks import BlockRule, PerfectSlope
from stamina_engine.rules.components.crit import CritRule, DoubleOnce
from stamina_engine.rules.components.defenses import DefenseRule, V09Defenses
from stamina_engine.rules.components.dying import DyingRule, SystemShock
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
from stamina_engine.rules.registry import KINDS, Component, Scalar, from_dict, to_dict


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
        """A copy with whole components replaced."""
        unknown = set(changes) - set(KINDS)
        if unknown:
            raise ConfigError(f"unknown component kinds {sorted(unknown)}")
        # __post_init__ checks each component is of its slot's kind.
        return dataclasses.replace(self, name=name or self.name, **changes)  # type: ignore[arg-type]

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
        """SHA-256 of the canonical TOML of every component (the name is excluded)."""
        body = self.to_toml().split("\n", 2)[2]
        return hashlib.sha256(body.encode()).hexdigest()

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
        return base.override(overrides, name=name if isinstance(name, str) else base.name)
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


def review_candidate() -> RuleSet:
    """The review's candidate: +2 surcharge per prior action, v0.9 crits."""
    return v0_9().with_(name="review-candidate", surcharge=LinearSurcharge(slope=2))


def review_sim() -> RuleSet:
    """The review simulator's quirks, for parity runs only (see CLAUDE.md, The oracle).

    Initiative ties go to the first-listed combatant, and duels have no off-turn movement or
    opportunity attacks. Its crit modes are selected per run with crit overrides.
    """
    base = v0_9()
    return base.with_(
        name="review-sim",
        turn_order=V09Initiative(tiebreak="list_order"),
        off_turn=Escalation(enabled=False),
        opportunity=V09Opportunity(enabled=False),
    )


PRESETS: dict[str, Callable[[], RuleSet]] = {
    "v0.9": v0_9,
    "review-candidate": review_candidate,
    "review-sim": review_sim,
}


def preset(name: str) -> RuleSet:
    try:
        return PRESETS[name]()
    except KeyError:
        raise ConfigError(f"no preset {name!r}; known: {sorted(PRESETS)}") from None
