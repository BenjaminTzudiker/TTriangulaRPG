"""StateOps: invariants hold under random op sequences, and nothing else writes state."""

import ast
import random
import subprocess
import sys
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from stamina_engine.core.errors import RulesError, Unaffordable
from stamina_engine.engine.events import Event, log_sha256
from stamina_engine.engine.stateops import StateOps
from stamina_engine.model.build import load_build
from stamina_engine.model.derive import derive
from stamina_engine.model.state import BattleState, new_combatant
from stamina_engine.rules.pricing import Pricing, Quote, Trackers
from stamina_engine.rules.ruleset import RuleSet, review_sim, v0_9

SRC = Path(__file__).resolve().parents[2] / "src" / "stamina_engine"


def battle(rules: RuleSet, *builds: str) -> tuple[BattleState, StateOps, list[Event]]:
    cs = tuple(
        new_combatant(f"c{i}", f"t{i}", derive(load_build(b), rules)) for i, b in enumerate(builds)
    )
    state = BattleState(cs)
    log: list[Event] = []
    return state, StateOps(state, rules, log, check=True), log


@settings(max_examples=150)
@given(
    st.sampled_from([v0_9(), review_sim()]),
    st.sampled_from(["l1_sample", "l1_duelist", "l30_sample", "l99_sample"]),
    st.lists(
        st.tuples(
            st.sampled_from(["attack", "block", "recover", "injure", "turn"]), st.integers(0, 12)
        ),
        max_size=40,
    ),
)
def test_invariants_under_random_ops(
    rules: RuleSet, build: str, ops: list[tuple[str, int]]
) -> None:
    state, so, _ = battle(rules, build)
    c = state.combatants[0]
    pricing = Pricing(rules)
    for op, n in ops:
        before_max = so.max_stamina(c)
        if op == "attack" and c.active:
            k = min(n % 4, pricing.max_steps(2, c.stamina, c.trackers))
            quote = pricing.melee_attack(2, k, c.trackers)
            before = c.stamina
            so.spend(c, quote, "attack")
            assert c.stamina == before - quote.total  # every charge equals its quote
        elif op == "block" and c.active and c.stamina >= n % 3:
            so.spend(c, pricing.blocks(0, n % 3), "block")
        elif op == "recover" and c.active:
            so.recover(c, c.profile.recovery)
        elif op == "injure":
            so.injure(c, n)
            assert so.max_stamina(c) <= before_max  # max follows HP down
        elif op == "turn":
            so.start_turn(c)
            assert c.trackers == Trackers(0, 0, c.strain)
        assert 0 <= c.stamina <= so.max_stamina(c)
        assert so.max_stamina(c) == rules.resources.max_stamina(c.hp, c.profile.level)


def test_refusals() -> None:
    state, so, _ = battle(v0_9(), "l1_sample")
    c = state.combatants[0]
    p = Pricing(v0_9())
    with pytest.raises(Unaffordable):
        so.spend(c, Quote((20,)), "attack")
    so.injure(c, 8)
    assert not c.active
    with pytest.raises(RulesError):
        so.spend(c, p.blocks(1, 0), "block")


def test_clamp_and_waste() -> None:
    state, so, log = battle(v0_9(), "l1_sample")
    c = state.combatants[0]
    so.spend(c, Pricing(v0_9()).melee_attack(2, 2), "attack")  # 14 -> 9
    so.injure(c, 6)  # HP 2: max stamina 6 + 2 = 8
    assert (c.hp, c.stamina) == (2, 8)
    so.recover(c, 4)  # already at the new max: all 4 wasted
    assert (c.stamina, log[-1].wasted) == (8, 4)  # type: ignore[attr-defined]


def test_system_shock_through_stateops() -> None:
    """Packet: Dying and Death, Example: System Shock, applied as state changes."""
    state, so, _ = battle(v0_9(), "l1_sample")
    c = state.combatants[0]
    so.injure(c, 5)  # 8 -> 3 HP
    so.injure(c, 5)  # -2 HP
    assert (c.hp, c.dying.shock) == (-2, 2)
    assert c.stamina <= so.max_stamina(c) == 6  # the HP term floors at 0
    so.dying_roll(c, 5)
    so.injure(c, 3)
    assert (c.hp, c.dying.shock) == (-5, 6)


def test_review_sim_has_no_shock() -> None:
    state, so, _ = battle(review_sim(), "l1_sample")
    c = state.combatants[0]
    so.injure(c, 11)
    assert (c.hp, c.dying.shock, c.dying.in_shock, c.status.value) == (
        -3,
        0,
        False,
        "incapacitated",
    )


def test_log_hash_stable_across_processes() -> None:
    state, so, log = battle(v0_9(), "l1_sample", "l1_duelist")
    rng = random.Random(3)
    for _ in range(20):
        c = state.combatants[rng.randint(0, 1)]
        if c.active:
            so.recover(c, rng.randint(0, 5))
            so.injure(c, rng.randint(0, 2))
    code = (
        "import json,hashlib,sys; lines=sys.stdin.read().split('\\n');"
        "print(hashlib.sha256('\\n'.join(lines).encode()).hexdigest())"
    )
    text = "\n".join(e.to_json() for e in log)
    out = subprocess.run([sys.executable, "-c", code], input=text, capture_output=True, text=True)
    assert out.stdout.strip() == log_sha256(log)


STATE_FIELDS = {
    "stamina",
    "dying",
    "trackers",
    "strain",
    "damage_taken",
    "perfect_blocks",
    "round",
    "order",
    "turn_of",
    "version",
    "loadout",
    "pos",
    "free_move_left",
    "banked",
    "moving",
    "debt",
    "used_weapon",
    "bow_hands",
}
ALLOWED = {"engine/stateops.py", "model/state.py"}


def test_only_stateops_writes_state() -> None:
    """Ground rule 3: no module but StateOps assigns to battle-state fields."""
    offenders = []
    for path in SRC.rglob("*.py"):
        rel = path.relative_to(SRC).as_posix()
        if rel in ALLOWED:
            continue
        for node in ast.walk(ast.parse(path.read_text())):
            targets: list[ast.expr] = []
            if isinstance(node, ast.Assign):
                targets = node.targets
            elif isinstance(node, ast.AugAssign | ast.AnnAssign):
                targets = [node.target]
            for t in targets:
                if isinstance(t, ast.Subscript):
                    t = t.value
                if (
                    isinstance(t, ast.Attribute)
                    and t.attr in STATE_FIELDS
                    and not (isinstance(t.value, ast.Name) and t.value.id == "self")
                ):
                    offenders.append(f"{rel}:{node.lineno} .{t.attr}")
    assert not offenders, offenders
