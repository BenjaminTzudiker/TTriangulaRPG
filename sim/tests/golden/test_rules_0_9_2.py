"""Packet 0.9.1 and 0.9.2 (rules/CHANGELOG.md), from the notes' own numbers: HP, the Sample
Character, the critical-hit example, opportunity attacks without a cap, initiative,
Intelligence's costs, and the presets that select them."""

from dataclasses import replace
from pathlib import Path

import pytest

from stamina_engine.core.errors import ConfigError
from stamina_engine.engine.events import OpportunityDeclared
from stamina_engine.experiments.runner import run_trial
from stamina_engine.experiments.scenario import load_scenario
from stamina_engine.model.build import Attributes, Build, Loadout, ability_cost, load_build
from stamina_engine.model.derive import derive
from stamina_engine.rules.components.dying import SystemShock
from stamina_engine.rules.components.opportunity import V09Opportunity
from stamina_engine.rules.components.turn_order import V09Initiative
from stamina_engine.rules.exchange import Blocks, resolve
from stamina_engine.rules.pricing import Pricing, Trackers
from stamina_engine.rules.ruleset import preset, v0_9, v0_9_1, v0_9_2

SCENARIOS = Path(__file__).resolve().parents[2] / "src/stamina_engine/data/scenarios"


def hp(rules_name: str, strength: int) -> int:
    return preset(rules_name).resources.hp_max(strength)


def test_hp_from_even_strength() -> None:
    """Packet: HP. 0.9.2: 8 + 2 per even Strength; 0.9.1 had base 6; v0.9 was 6 + Strength."""
    assert [hp("v0.9.2", s) for s in range(7)] == [8, 8, 10, 10, 12, 12, 14]
    assert [hp("v0.9.1", s) for s in range(7)] == [6, 6, 8, 8, 10, 10, 12]
    assert [hp("v0.9", s) for s in range(7)] == [6, 7, 8, 9, 10, 11, 12]


def test_sample_character() -> None:
    """Packet: Quick Reference, Sample Character (0.9.2): HP 10, stamina 16, recovers 4,
    strain 6; MD 4, RD 3, DD 1; movement 6, 2 squares per off-turn purchase; initiative 2d12
    (CUN 0); a d8 crits on 7-8."""
    rules = v0_9_2()
    p = derive(load_build("l1_sample"), rules)
    lo = p.main
    assert (p.hp_max, p.stamina_max, p.recovery, p.strain_max) == (10, 16, 4, 6)
    assert (lo.melee_defense, lo.ranged_defense, lo.dodge_defense) == (4, 3, 1)
    assert (lo.movement, lo.squares_per_purchase, lo.extra_squares_per_purchase) == (6, 2, 1)
    assert lo.initiative_bonus == 0
    assert lo.oa_cap is None
    w = lo.weapon
    assert w is not None
    assert [f for f in range(1, 9) if rules.crit.is_crit(f, 8, w.crit_widen)] == [7, 8]
    one = derive(load_build("l1_sample"), v0_9_1())
    assert (one.hp_max, one.stamina_max) == (8, 14)  # 0.9.1: HP 8 unchanged


def test_melee_example_with_a_critical_die() -> None:
    """Packet: Critical Hits, Example: Melee Attack. The orc has Melee Defense 4, armor 1."""
    rules = v0_9_2()
    no_crit = {
        Blocks(4, 0): 0,
        Blocks(3, 1): 0,
        Blocks(2, 2): 1,
        Blocks(2, 1): 3,
    }
    for blocks, injury in no_crit.items():
        assert resolve(15, 0, 4, 1, blocks, rules).injury == injury, blocks
    # 16 damage with one critical die: armor counts as 0.
    full = resolve(16, 1, 4, 1, Blocks(4, 0), rules)
    assert (full.armor_applied, full.after_armor, full.injury) == (0, 0, 0)  # adds nothing
    leaks = resolve(16, 1, 4, 1, Blocks(2, 2), rules)
    assert (leaks.after_armor, leaks.injury) == (2, 3)  # the 2 leaks + 1


def test_each_critical_die_adds_one_only_if_damage_gets_through() -> None:
    rules = v0_9_2()
    assert resolve(12, 2, 4, 3, Blocks(1, 0), rules).injury == 7 + 2  # 8 - 1 armor, +1 each
    assert resolve(12, 2, 4, 3, Blocks(3, 0), rules).injury == 0  # all stopped: nothing
    assert resolve(5, 1, 4, 3, Blocks(0, 0), rules).injury == 3 + 1  # armor 3 - 1 ignored
    # v0.9 doubled instead: (5 - 2) x 2.
    assert resolve(5, 1, 4, 3, Blocks(0, 0), v0_9()).injury == 6


def test_opportunity_attacks_have_no_cap() -> None:
    """Packet: Off-Turn Escalation's example: move, move, a dagger OA at 3, move: 10. With no
    cap, a Finesse 0 creature can make that OA (v0.9 needed a cap of 3)."""
    rules = v0_9_1()
    assert rules.opportunity.cap(0) is None
    pricing = Pricing(rules)
    oa = pricing.opportunity_attack(1, 1, Trackers(off_turn_costs=2), cap=None)
    assert oa.total == 3
    assert pricing.opportunity_attack(2, 3, Trackers(), cap=None).total == 2 + 3 + 4
    assert pricing.oa_cap(0, 2) is None
    with pytest.raises(ConfigError):
        V09Opportunity(cap_rule="none", per_square_cap=True)
    with pytest.raises(ConfigError):
        V09Opportunity(cap_rule="none", avoid_price="attacker_cap")


def test_engine_agents_size_uncapped_opportunity_attacks_by_commitment() -> None:
    """With no cap, a fixed:2 agent's OAs take 2 steps, not its whole pool (Assumptions
    register: engine agents and uncapped opportunity attacks). Under v0.9's cap of 2 stamina
    it could take only 1."""
    s = replace(load_scenario(SCENARIOS / "retreat_economics.toml"), rules=v0_9_2())
    steps = [
        e.steps
        for trial in range(40)
        for e in run_trial(s, trial).log
        if isinstance(e, OpportunityDeclared) and e.attacker == "A"  # A is fixed:2
    ]
    assert steps and max(steps) == 2


def test_initiative_is_2d12_plus_cunning() -> None:
    """Packet: Starting Combat and Turn Structure, Cunning: + every point of Cunning; Agility
    no longer counts."""
    rule = v0_9_1().turn_order
    assert [rule.initiative_bonus(agility=5, cunning=c) for c in range(7)] == list(range(7))
    assert V09Initiative().initiative_bonus(agility=5, cunning=3) == 3 + 2  # v0.9: odd + odd


def test_dying_roll_adds_will() -> None:
    """Packet: Dying and Death, Will: 2d12 + Will from 0.9.1 (2d12 + Strength in v0.9)."""
    assert v0_9_1().dying.roll_bonus(strength=4, will=1) == 1
    assert SystemShock().roll_bonus(strength=4, will=1) == 4


def test_extra_on_turn_movement_is_one_square() -> None:
    """Packet: On-Turn Movement: each purchase moves 1 square; Agility doesn't change it."""
    build = Build("quick", 1, Attributes(AGI=5), (("m", Loadout()),), budget="ignore")
    assert derive(build, v0_9_1()).main.extra_squares_per_purchase == 1
    assert derive(build, v0_9()).main.extra_squares_per_purchase == 4


def test_intelligence_core_costs_and_bonus_ability_points() -> None:
    """Packet: Intelligence's two tables."""
    res = v0_9_1().resources
    table = {0: [1, 2, 3, 4], 1: [1, 1, 2, 3], 2: [1, 1, 2, 3], 3: [1, 1, 1, 2], 5: [1, 1, 1, 1]}
    for intelligence, costs in table.items():
        assert [res.core_cost(owned, intelligence) for owned in range(4)] == costs
    assert [v0_9().resources.core_cost(owned, 5) for owned in range(4)] == [1, 2, 3, 4]
    plain = res.ability_budget(99, 0)
    extra = {i: res.ability_budget(99, i) - plain for i in range(7)}
    assert extra == {0: 0, 1: 0, 2: 3, 3: 3, 4: 6, 5: 6, 6: 9}
    assert res.ability_budget(9, 2) == res.ability_budget(9, 0)
    assert res.ability_budget(10, 2) == res.ability_budget(10, 0) + 1
    assert res.ability_budget(40, 4) - res.ability_budget(40, 0) == 3  # 10, 20 and 40
    cores = ("fighter", "barbarian", "rogue")
    assert ability_cost(cores, v0_9_1(), intelligence=3) == 3
    assert ability_cost(cores, v0_9(), intelligence=3) == 6


def test_presets_differ_where_intended() -> None:
    base, one, two = v0_9(), v0_9_1(), v0_9_2()
    kinds = ("opportunity", "movement", "turn_order", "resources", "dying")
    assert {k for k, c in one.components().items() if c != base.components()[k]} == set(kinds)
    assert {k for k, c in two.components().items() if c != one.components()[k]} == {
        "crit",
        "resources",
    }
    assert two.crit.variant == "per_die_if_through"
