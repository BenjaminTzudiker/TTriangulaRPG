"""The engine agents' ability policies (agents/ability_policy.py): off by default, and each
heuristic firing where its docstring says. Agent conventions, not rules."""

from dataclasses import replace

import pytest

from stamina_engine.agents.decisions import Attack
from stamina_engine.agents.listed import Listed
from stamina_engine.agents.scripted import make_agent
from stamina_engine.core.dice import ScriptedDice
from stamina_engine.core.errors import ConfigError
from stamina_engine.engine.battle import Battle, BattleResult, Entrant
from stamina_engine.engine.events import (
    AbilityUsed,
    AttackAvoided,
    AttackResolved,
    Spent,
    TurnStarted,
)
from stamina_engine.grid.battlefield import parse_map
from stamina_engine.model.build import load_build
from stamina_engine.model.derive import CombatProfile, derive
from stamina_engine.rules.ruleset import preset

RULES = preset("v0.9")


class Dice:
    def __init__(self, faces: dict[str, list[int]]) -> None:
        self.sources = {k: ScriptedDice(v) for k, v in faces.items()}

    def dice(self, name: str) -> ScriptedDice:
        return self.sources[name]


def profile(build: str, *abilities: str) -> CombatProfile:
    b = load_build(build)
    return derive(replace(b, abilities=abilities) if abilities else b, RULES)


def agent(commit: str = "alpha", uses: str = "use") -> object:
    return make_agent({"commit": commit, "abilities": uses}, RULES)


def battle(
    entrants: list[Entrant], faces: dict[str, list[int]], rounds: int = 1, field: object = None
) -> BattleResult:
    faces = {"dying": [6] * 30, "attack:A": [1] * 30, "attack:B": [1] * 30, **faces}
    return Battle(
        RULES, entrants, Dice(faces), seed=0, round_cap=rounds, check=True, field=field
    ).run()  # type: ignore[arg-type]


def used(result: BattleResult) -> list[tuple[str, str, str]]:
    return [(e.who, e.ability, e.window) for e in result.log if isinstance(e, AbilityUsed)]


def test_abilities_are_off_by_default_and_checked() -> None:
    entrants = [
        Entrant("A", "A", profile("l1_barbarian"), make_agent("alpha", RULES)),  # type: ignore[arg-type]
        Entrant("B", "B", profile("l1_heavy"), make_agent("alpha", RULES)),  # type: ignore[arg-type]
    ]
    result = battle(entrants, {"initiative": [12, 12, 1, 1], "attack:A": [1] * 9})
    assert used(result) == []
    with pytest.raises(ConfigError, match="abilities"):
        make_agent({"commit": "alpha", "abilities": "sometimes"}, RULES)


def test_barbarian_refunds_each_step_after_attacking() -> None:
    entrants = [
        Entrant("A", "A", profile("l1_barbarian"), agent()),  # type: ignore[arg-type]
        Entrant("B", "B", profile("l1_heavy"), agent("never", "none")),  # type: ignore[arg-type]
    ]
    result = battle(entrants, {"initiative": [12, 12, 1, 1], "attack:A": [1] * 9})
    steps = [e for e in result.log if isinstance(e, Spent) and e.category == "attack"]
    refunds = used(result)
    assert refunds and all(u == ("A", "barbarian_core", "turn") for u in refunds)
    assert len(refunds) == min(len(steps[0].parts), 6)  # one per step, within max strain 6


def test_fighter_recovers_before_blocking_a_big_roll() -> None:
    """B (a fighter) spends everything on its own attack; A's big roll then comes in, and
    recovering first is worth more than one HP."""
    entrants = [
        Entrant("B", "B", profile("l1_sample"), agent()),  # type: ignore[arg-type]
        Entrant("A", "A", profile("l1_heavy"), agent("fixed:3", "none")),  # type: ignore[arg-type]
    ]
    faces = {"initiative": [12, 12, 1, 1], "attack:B": [1] * 9, "attack:A": [6, 6, 6]}
    result = battle(entrants, faces)
    assert ("B", "fighter_core", "before_blocks") in used(result)


def test_fighter_recovers_on_its_turn_when_short_of_two_steps() -> None:
    """All in on round 1 (14 stamina, 4 steps); round 2 starts at its recovery of 4, short of
    two steps (5), so it recovers before attacking."""
    entrants = [
        Entrant("B", "B", profile("l1_sample"), agent("alpha")),  # type: ignore[arg-type]
        Entrant("A", "A", profile("l1_heavy"), agent("never", "none")),  # type: ignore[arg-type]
    ]
    faces = {"initiative": [12, 12, 1, 1], "attack:B": [1] * 20}
    result = battle(entrants, faces, rounds=2)
    turn_uses = [u for u in used(result) if u[2] == "turn"]
    assert turn_uses and turn_uses[0] == ("B", "fighter_core", "turn")


def test_rogue_jumps_ahead_of_an_enemy_once() -> None:
    entrants = [
        Entrant("A", "A", profile("l1_sample"), Listed()),
        Entrant("R", "R", profile("l1_rogue"), agent("never")),  # type: ignore[arg-type]
    ]
    result = battle(entrants, {"initiative": [12, 12, 1, 1]}, rounds=2)
    assert [e.who for e in result.log if isinstance(e, TurnStarted)] == ["R", "A", "R", "A"]
    assert used(result) == [("R", "rogue_core", "between_turns")]


@pytest.mark.parametrize(("target", "swings"), [("l1_heavy", True), ("l1_duelist", False)])
def test_heavy_swing_only_against_armor(target: str, swings: bool) -> None:
    entrants = [
        Entrant("A", "A", profile("l1_sample", "heavy_swing"), agent("fixed:2")),  # type: ignore[arg-type]
        Entrant("B", "B", profile(target), Listed()),
    ]
    result = battle(entrants, {"initiative": [12, 12, 1, 1], "attack:A": [1] * 9})
    assert (("A", "heavy_swing", "declare_attack") in used(result)) is swings


def test_tactical_withdrawal_steps_out_of_reach() -> None:
    field = parse_map("\n".join(["......"] * 3))
    a = Listed(turns=[Attack("B")], commit=[2])
    b = agent("never")
    entrants = [
        Entrant("A", "A", profile("l1_sample"), a, "", (2, 1)),
        Entrant("B", "B", profile("l1_sample", "tactical_withdrawal"), b, "", (3, 1)),  # type: ignore[arg-type]
    ]
    result = battle(entrants, {"initiative": [12, 12, 1, 1], "attack:A": [8, 8]}, field=field)
    assert ("B", "tactical_withdrawal", "reactions") in used(result)
    assert any(isinstance(e, AttackAvoided) for e in result.log)
    assert not any(isinstance(e, AttackResolved) for e in result.log)


def test_monk_blocks_flat_against_a_big_roll() -> None:
    entrants = [
        Entrant("A", "A", profile("l1_sample"), agent("fixed:3", "none")),  # type: ignore[arg-type]
        Entrant("M", "M", profile("l1_monk"), agent("never")),  # type: ignore[arg-type]
    ]
    result = battle(entrants, {"initiative": [12, 12, 1, 1], "attack:A": [8, 8, 8]})
    assert used(result) == [("M", "monk_core", "before_blocks")]
    flat = [e for e in result.log if isinstance(e, Spent) and e.category == "block"]
    assert flat and all(p <= 1 for p in flat[0].parts if p)  # perfect blocks at 1 each
