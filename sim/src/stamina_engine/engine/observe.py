"""Build what a creature observes, filtered by the information rule."""

from stamina_engine.agents.decisions import CombatantView, Observation
from stamina_engine.core.errors import ConfigError
from stamina_engine.model.state import BattleState, CombatantState
from stamina_engine.rules.ruleset import RuleSet

cites = ("Packet: Commitment", "Review F6")


def _view(c: CombatantState, rules: RuleSet, own: bool) -> CombatantView:
    return CombatantView(
        id=c.id,
        team=c.team,
        profile=c.profile,
        gear=c.gear,
        hp=c.hp,
        max_stamina=rules.resources.max_stamina(c.hp, c.profile.level),
        stamina=c.stamina,
        stamina_exact=True,
        status=c.status.value,
        trackers=c.trackers if own else None,
    )


def observe(state: BattleState, rules: RuleSet, who: str) -> Observation:
    if rules.information.stamina != "public":  # type: ignore[attr-defined]
        raise ConfigError("hidden stamina observations arrive in M1 slice 8")
    me = state.get(who)
    return Observation(
        me=_view(me, rules, own=True),
        others=tuple(_view(c, rules, own=False) for c in state.combatants if c.id != who),
        round=state.round,
    )
