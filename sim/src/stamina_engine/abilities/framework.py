"""The ability framework (Packet: Class Trees, Core Abilities, Candidate Abilities, Strain).

An ability declares the windows it can fire in, its strain and base stamina, when it's
usable, and its effect. Its price comes from Pricing.strain_ability: the base stamina plus
1 per point of strain over the maximum, counted after adding this use's strain (Packet:
Going Over Your Maximum Strain). Windows:

- turn: on your own turn, between actions (a TurnCommand option);
- off_turn: in an off-turn window, beside moving and drawing;
- before_blocks: after an attack on you is rolled, before you declare blocks;
- between_turns: before the next creature's turn (the Rogue core);
- turn_start: as your turn would begin (the Rogue core's delay);
- declare_attack: as you declare a melee attack, before its steps (Heavy Swing);
- reactions: the attack procedure's reactions step, against a melee attack (Tactical
  Withdrawal).

Which creatures have which abilities: each core in a build brings "<core>_core", and a
build lists candidate abilities. Engine-side only: agents decide whether to use them.
"""

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from stamina_engine.agents.decisions import AbilityOption, AbilityRequest, UseAbility
from stamina_engine.core.errors import ConfigError

if TYPE_CHECKING:
    from stamina_engine.engine.battle import Battle
    from stamina_engine.model.state import CombatantState

cites = (
    "Packet: Class Trees",
    "Packet: Core Abilities",
    "Packet: Candidate Abilities",
    "Packet: Strain",
    "Packet: Going Over Your Maximum Strain",
)

WINDOWS = frozenset(
    {
        "turn",
        "off_turn",
        "before_blocks",
        "between_turns",
        "turn_start",
        "declare_attack",
        "reactions",
    }
)

Facts = Mapping[str, int | str]


@dataclass(frozen=True)
class Ability:
    name: str
    windows: frozenset[str]
    strain: int
    stamina: int
    usable: Callable[["Battle", "CombatantState", str, Facts], bool]
    apply: Callable[["Battle", "CombatantState", str, Facts], None]
    cites: tuple[str, ...] = field(default=())

    def __post_init__(self) -> None:
        if not self.windows <= WINDOWS:
            raise ConfigError(f"{self.name}: unknown windows {sorted(self.windows - WINDOWS)}")


REGISTRY: dict[str, Ability] = {}


def register(ability: Ability) -> Ability:
    if ability.name in REGISTRY:
        raise ConfigError(f"ability {ability.name} registered twice")
    REGISTRY[ability.name] = ability
    return ability


def known(name: str) -> Ability:
    _load()
    try:
        return REGISTRY[name]
    except KeyError:
        raise ConfigError(f"no ability {name!r}; known: {sorted(REGISTRY)}") from None


def _load() -> None:
    from stamina_engine.abilities import candidates, cores  # noqa: F401  (registers them)


def options(
    b: "Battle", c: "CombatantState", window: str, facts: Facts | None = None
) -> tuple[AbilityOption, ...]:
    """The creature's abilities usable in this window now, priced, if affordable."""
    _load()
    facts = facts or {}
    out = []
    if not c.active:
        return ()
    for name in c.profile.abilities:
        a = REGISTRY.get(name)
        if a is None or window not in a.windows or not a.usable(b, c, window, facts):
            continue
        strain = _strain(b, c, a)
        quote = b.pricing.strain_ability(a.stamina, strain, c.trackers, c.profile.strain_max)
        if quote.total <= c.stamina:
            out.append(AbilityOption(a.name, quote, strain))
    return tuple(out)


def _strain(b: "Battle", c: "CombatantState", a: Ability) -> int:
    """A Rogue that already paid to wait chooses when to come back for free."""
    if a.name == "rogue_core" and c.id in b.state.delayed:
        return 0
    return a.strain


def use(
    b: "Battle", c: "CombatantState", name: str, window: str, facts: Facts | None = None
) -> None:
    """Pay for and apply an ability the broker has already allowed."""
    a = known(name)
    strain = _strain(b, c, a)
    quote = b.pricing.strain_ability(a.stamina, strain, c.trackers, c.profile.strain_max)
    with b.context.frame(f"ability {c.id} {name}"):
        if quote.total:
            b.ops.spend(c, quote, f"ability:{name}")
        b.ops.ability_used(c, name, window, strain)
        a.apply(b, c, window, facts or {})


def window(b: "Battle", c: "CombatantState", where: str, facts: Facts | None = None) -> str | None:
    """Ask the creature whether to use an ability here (if it has any usable); apply it.
    Returns the ability used, if any."""
    offered = options(b, c, where, facts)
    if not offered:
        return None
    answer = b.broker.ability(
        AbilityRequest(c.id, b.observe(c.id), b.context.path(), where, offered, dict(facts or {}))
    )
    if not isinstance(answer, UseAbility):
        return None
    use(b, c, answer.name, where, facts)
    return answer.name
