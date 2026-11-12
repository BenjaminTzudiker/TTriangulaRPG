"""Decision requests as JSON, for a chat that plays one decision at a time (`se play --step`).

A request goes out as its fields, with the observation cut down to what a player reads off
the table (positions, HP, stamina, defenses, armor, weapon, movement, and the observer's own
counters), squares as [x, y], maps keyed by square as "x,y", and quotes as their parts and
total. Every request type uses the same encoder, so a field added to a request reaches the
wire without changes here.
"""

import dataclasses
from collections.abc import Mapping
from enum import Enum
from fractions import Fraction
from typing import Any

from stamina_engine.agents.decisions import CombatantView, Observation
from stamina_engine.grid.battlefield import Battlefield
from stamina_engine.rules.pricing import Quote, Trackers

cites = ("Review F11",)

KINDS = {
    "TurnCommand": "turn",
    "Commitment": "steps",
    "BlocksRequest": "blocks",
    "OffTurnMove": "off_turn",
    "AvoidOA": "avoid",
    "TakeOA": "take_oa",
    "AimRequest": "aim",
    "DiveRequest": "react",
    "AbilityRequest": "ability",
}


def _key(k: object) -> str:
    if isinstance(k, tuple) and len(k) == 2 and all(isinstance(v, int) for v in k):
        return f"{k[0]},{k[1]}"
    return str(k)


def to_wire(x: object) -> Any:
    """Plain JSON values for a request's fields."""
    if x is None or isinstance(x, bool | int | float | str):
        return x
    if isinstance(x, Enum):
        return to_wire(x.value)
    if isinstance(x, Fraction):
        return float(x)
    if isinstance(x, Quote):
        return {"parts": list(x.parts), "total": x.total}
    if isinstance(x, Trackers):
        return {
            "actions_this_turn": x.actions_this_turn,
            "off_turn_costs": x.off_turn_costs,
            "strain": x.strain,
            "extra_purchases": x.extra_purchases,
        }
    if isinstance(x, Observation):
        return observation(x)
    if isinstance(x, Battlefield):
        return None  # the map is sent once, drawn
    if isinstance(x, Mapping):
        return {_key(k): to_wire(v) for k, v in x.items()}
    if isinstance(x, frozenset | set):
        return sorted((to_wire(v) for v in x), key=str)
    if isinstance(x, tuple | list):
        return [to_wire(v) for v in x]
    if dataclasses.is_dataclass(x) and not isinstance(x, type):
        return {f.name: to_wire(getattr(x, f.name)) for f in dataclasses.fields(x)}
    return str(x)


def view(v: CombatantView) -> dict[str, Any]:
    g = v.gear
    weapon = g.weapon
    out: dict[str, Any] = {
        "id": v.id,
        "team": v.team,
        "status": v.status,
        "pos": to_wire(v.pos),
        "hp": v.hp,
        "hp_max": v.profile.hp_max,
        "stamina": v.stamina,
        "stamina_max": v.max_stamina,
        "stamina_exact": v.stamina_exact,
        "melee_defense": g.melee_defense,
        "ranged_defense": g.ranged_defense,
        "armor": g.armor,
        "weapon": weapon.name if weapon is not None else None,
        "movement": g.movement,
        "squares_per_off_turn_purchase": g.squares_per_purchase,
    }
    if weapon is not None and weapon.ranged:
        out["band_width"] = weapon.band_width
        out["piercing"] = weapon.piercing
    if v.trackers is not None:
        out["counters"] = to_wire(v.trackers)
        out["free_move_left"] = v.free_move_left
        out["banked"] = v.banked
    return out


def observation(obs: Observation) -> dict[str, Any]:
    return {
        "round": obs.round,
        "order": list(obs.order),
        "me": view(obs.me),
        "others": [view(v) for v in obs.others],
        "objectives": [to_wire(o) for o in obs.objectives],
    }


def request(req: object) -> dict[str, Any]:
    """A request as JSON: its kind, who decides, the timing context, and every field."""
    name = type(req).__name__
    fields = to_wire(req)
    assert isinstance(fields, dict)
    return {
        "kind": KINDS.get(name, name),
        "who": fields.pop("who", None),
        "context": fields.pop("context", []),
        "observation": fields.pop("observation", None),
        "fields": fields,
    }
