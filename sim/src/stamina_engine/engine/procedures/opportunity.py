"""Opportunity attacks (Packet: Making Opportunity Attacks).

An opportunity attack is a normal melee attack whose steps go on the attacker's off-turn
escalation instead of its on-turn surcharge, and whose whole cost must fit its cap, if it
has one. After the steps are paid it runs the same steps as any melee attack: roll,
reactions, blocks, armor and crits, injury.

The cap was 1 + odd FIN in v0.9 (opportunity.cap_rule picks F9's weapon-based cap); from
0.9.1 there is none, and the off-turn escalation is the only limit (cap_rule = none). Under
the packet's optional per-square rule (opportunity.per_square_cap) the cap is pooled for one
move: each square the mover leaves within your reach without paying you off adds a cap's
worth, and an OA can spend what has built up minus what you already spent on that mover
during the move.
"""

from collections.abc import Iterable
from dataclasses import dataclass, field

from stamina_engine.agents.decisions import OAOption, TakeOA
from stamina_engine.core.errors import Unaffordable
from stamina_engine.engine.battle import Battle
from stamina_engine.engine.events import OpportunityDeclared
from stamina_engine.engine.procedures.melee import (
    armor_and_crits,
    declare_blocks,
    lose_hp,
    reactions,
    roll,
)
from stamina_engine.grid.battlefield import Cell
from stamina_engine.grid.geometry import reach_cells
from stamina_engine.grid.threat import melee_weapons
from stamina_engine.model.derive import WeaponProfile
from stamina_engine.model.state import CombatantState

cites = (
    "Packet: Making Opportunity Attacks",
    "Packet: Off-Turn Escalation",
    "Packet: Attack Procedure",
    "Ledger MV-4",
    "Ledger MV-5",
    "Review F9",
)


@dataclass
class OAContext:
    """Per-move bookkeeping for the per-square cap. Local to one move, so not battle state."""

    accrued: dict[str, int] = field(default_factory=dict)
    spent: dict[str, int] = field(default_factory=dict)

    def left_within(self, enemy: str, cap: int | None, paid: bool) -> None:
        if not paid and cap is not None:
            self.accrued[enemy] = self.accrued.get(enemy, 0) + cap

    def available(self, enemy: str, cap: int | None, per_square: bool) -> int | None:
        if not per_square or cap is None:  # the per-square rule needs a cap (config check)
            return cap
        return self.accrued.get(enemy, 0) - self.spent.get(enemy, 0)

    def spend(self, enemy: str, amount: int) -> None:
        self.spent[enemy] = self.spent.get(enemy, 0) + amount


def _weapons(attacker: CombatantState) -> list[tuple[str, WeaponProfile]]:
    gear = attacker.gear
    out = []
    for slot, w in (("main", gear.weapon), ("off_hand", gear.off_hand_weapon)):
        if w is not None and w in melee_weapons(gear):
            out.append((slot, w))
    return out


def _reaching(b: Battle, attacker: CombatantState, square: Cell) -> list[tuple[str, WeaponProfile]]:
    if b.field is None:
        return _weapons(attacker)  # all-adjacent: everyone is in reach (only Riposte gets here)
    if attacker.pos is None:
        return []
    return [
        (slot, w)
        for slot, w in _weapons(attacker)
        if square in reach_cells(b.field, attacker.pos, w.reach, b.rules.grid)
    ]


def reach_cap(b: Battle, attacker: CombatantState, square: Cell) -> int | None:
    """The attacker's cap for one OA on a mover leaving `square`: the best of its weapons
    that reach it (the weapon matters only under F9's weapon-based cap)."""
    fin = attacker.gear.attributes.FIN
    if b.rules.opportunity.cap(fin) is None:
        return None
    caps = [b.pricing.oa_cap(fin, w.base) for _, w in _reaching(b, attacker, square)]
    return max((c for c in caps if c is not None), default=0)


def _largest(caps: Iterable[int | None]) -> int | None:
    """The biggest cap among the weapons, or None if they have none."""
    values = list(caps)
    return None if None in values else max(c for c in values if c is not None)


def opportunity_attack(
    b: Battle, attacker: CombatantState, target: CombatantState, square: Cell, oa: OAContext
) -> None:
    per_square = b.rules.opportunity.per_square()
    fin = attacker.gear.attributes.FIN
    options = []
    caps = {}
    for slot, w in _reaching(b, attacker, square):
        cap = oa.available(attacker.id, b.pricing.oa_cap(fin, w.base), per_square)
        quotes = []
        k = 1
        while True:
            try:
                quote = b.pricing.opportunity_attack(
                    w.base, k, attacker.trackers, cap, stamina=attacker.stamina
                )
            except Unaffordable:
                break
            quotes.append(quote)
            k += 1
        if quotes:
            options.append(OAOption(slot, w.name, tuple(quotes)))
            caps[slot] = cap
    if not options:
        return  # nothing fits the cap and stamina: no request (Assumptions register)
    with b.context.frame(f"OA {attacker.id}->{target.id}"):
        request = TakeOA(
            attacker.id,
            b.observe(attacker.id),
            b.context.path(),
            target.id,
            square,
            _largest(caps.values()),
            tuple(options),
        )
        answer = b.broker.take_oa(request)
        if answer.steps == 0:
            return
        option = next(o for o in options if o.weapon == answer.weapon)
        weapon = dict(_reaching(b, attacker, square))[answer.weapon]
        quote = option.quotes[answer.steps - 1]
        b.ops.emit(OpportunityDeclared(attacker.id, target.id, answer.weapon, answer.steps))
        b.ops.spend(attacker, quote, "opportunity")
        oa.spend(attacker.id, quote.total)
        attack = roll(b, attacker, weapon, answer.steps)
        reactions(b, attacker, target)
        blocks = declare_blocks(b, attacker, target, attack)
        outcome = armor_and_crits(b, attacker, target, attack, blocks)
        lose_hp(b, target, outcome)
