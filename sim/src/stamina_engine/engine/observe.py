"""Build what a creature observes, filtered by the information rule."""

from stamina_engine.agents.decisions import CombatantView, Observation
from stamina_engine.core.errors import ConfigError
from stamina_engine.engine.ledger import PublicLedger
from stamina_engine.grid.battlefield import Battlefield
from stamina_engine.model.state import BattleState, CombatantState
from stamina_engine.rules.ruleset import RuleSet

cites = ("Packet: Commitment", "Review F6")


def _view(
    c: CombatantState, rules: RuleSet, own: bool, ledger: PublicLedger | None
) -> CombatantView:
    hidden = ledger is not None and not own
    return CombatantView(
        id=c.id,
        team=c.team,
        profile=c.profile,
        gear=c.gear,
        hp=c.hp,
        max_stamina=rules.resources.max_stamina(c.hp, c.profile.level),
        stamina=ledger.estimate[c.id] if hidden and ledger is not None else c.stamina,
        stamina_exact=not hidden,
        status=c.status.value,
        trackers=c.trackers if own else None,
        pos=c.pos,
        free_move_left=c.free_move_left if own else None,
        banked=c.banked if own else None,
    )


def observe(
    state: BattleState,
    rules: RuleSet,
    who: str,
    ledger: PublicLedger | None = None,
    field: Battlefield | None = None,
) -> Observation:
    """Everything a creature sees. With hidden stamina, others' stamina is the public ledger's
    reconstruction; its own is exact."""
    hidden = rules.information.stamina_visibility() == "hidden"
    if hidden and ledger is None:
        raise ConfigError("hidden stamina needs the battle's public ledger")
    me = state.get(who)
    use = ledger if hidden else None
    return Observation(
        me=_view(me, rules, True, use),
        others=tuple(_view(c, rules, False, use) for c in state.combatants if c.id != who),
        round=state.round,
        field=field,
        order=state.order,
    )
