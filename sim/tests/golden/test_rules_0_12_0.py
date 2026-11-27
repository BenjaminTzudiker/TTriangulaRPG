"""Golden tests for packets 0.11.0 through 0.12.0:
- Sample Character (0.12.0)
- Spear reach only in two hands (0.11.1)
- Skipping OA avoidance when an enemy can't make even 1 step (0.11.1)
- Initiative tiebreak by Agility + Cunning then d12 roll-off (0.11.2)
- Helping the Dying (0.11.2)
- Ending a hold when all held stamina is spent, and Forced Movement (0.11.6)
- Strain shelved and the four martial class cores (0.12.0):
  Second Wind, Opportunist, Press the Wound, Poised Guard
- Unified-escalation agent regression, tactical hold heuristic, and HumanAgent CLI prompts
"""

import pytest

from stamina_engine.agents.decisions import (
    AbilityRequest,
    Attack,
    Avoid,
    EndTurn,
    HelpDying,
    Holds,
    Move,
    OATake,
    Pass,
    Shoot,
    UseAbility,
)
from stamina_engine.agents.human import HumanAgent, ScriptedIO
from stamina_engine.agents.listed import Listed
from stamina_engine.agents.scripted import make_agent
from stamina_engine.core.dice import ScriptedDice
from stamina_engine.core.errors import RulesError
from stamina_engine.engine.battle import Battle, Entrant
from stamina_engine.engine.events import (
    AbilityUsed,
    AttackDeclared,
    BlocksDeclared,
    DyingHelped,
    ForcedMoved,
    HoldEnded,
    HoldSet,
    HoldSpent,
    InitiativeRolled,
    OpportunityAvoided,
    OpportunityProvoked,
    Recovered,
    RecoverySkipped,
    ShotDeclared,
    Spent,
)
from stamina_engine.grid.battlefield import parse_map
from stamina_engine.grid.geometry import forced_move_squares
from stamina_engine.model.build import Attributes, Build, Loadout, load_build
from stamina_engine.model.derive import CombatProfile, derive
from stamina_engine.rules.exchange import Blocks
from stamina_engine.rules.ruleset import BASELINE, RuleSet, preset

RULES = preset("v0.12.0")
OPEN = parse_map("\n".join(["." * 12] * 12))


class Dice:
    def __init__(self, faces: dict[str, list[int]]) -> None:
        self.sources = {k: ScriptedDice(v) for k, v in faces.items()}

    def dice(self, name: str) -> ScriptedDice:
        return self.sources.setdefault(name, ScriptedDice([6] * 30))


def profile(build: str | Build, rules: RuleSet = RULES) -> CombatProfile:
    b = load_build(build) if isinstance(build, str) else build
    return derive(b, rules)


# --- Sample Character & Equipment (0.11.1, 0.12.0) -----------------------------------


def test_sample_character_v0_12_0() -> None:
    """Matches Packet 0.12.0: Sample Character."""
    assert BASELINE == "v0.12.1"
    p = profile("l1_sample")
    lo = p.main
    assert (p.hp_max, p.stamina_max, p.recovery, p.strain_max) == (10, 16, 4, 0)
    assert (lo.melee_defense, lo.ranged_defense) == (3, 2)
    assert (lo.armor, lo.movement, lo.squares_per_purchase) == (2, 6, 2)
    assert lo.initiative_bonus == 0
    assert lo.oa_cap == 2
    assert not RULES.resources.uses_strain()
    w = lo.weapon
    assert w is not None
    assert (w.name, w.grip, w.base, str(w.damage)) == ("longsword", "one", 2, "1d8 + 3")
    assert [f for f in range(1, 9) if RULES.crit.is_crit(f, 8, w.crit_widen)] == [7, 8]


def test_spear_reach_only_in_two_hands() -> None:
    """Packet 0.11.1: spear reaches 2 only in two hands; 1H spear with shield reaches 1."""
    one_h = profile("l1_spear")
    two_h = profile("l1_spear_2h")
    assert one_h.main.weapon is not None and one_h.main.weapon.reach == 1
    assert two_h.main.weapon is not None and two_h.main.weapon.reach == 2
    assert two_h.main.shield is None
    # Earlier presets (v0.10.1) keep 1H spear at reach 2 for backwards reproducibility.
    old_one_h = derive(load_build("l1_spear"), preset("v0.10.1"))
    assert old_one_h.main.weapon is not None and old_one_h.main.weapon.reach == 2


# --- Skipping OA Avoidance When Enemy Can't Make 1 Step (0.11.1) ---------------------


def test_avoid_skips_enemy_that_cannot_make_one_step() -> None:
    """Packet 0.11.1: a greatsword (base 3) at FIN 1 (cap 2) has no OA without a hold, so
    a mover leaving its reach owes it nothing and isn't asked AvoidOA."""
    gs = Build(
        "gs",
        1,
        Attributes(STR=2, AGI=1, FIN=1),
        (("main", Loadout(weapon="greatsword", grip="two", armor="medium")),),
        ("fighter",),
    )
    mover = Listed(turns=[Move(((4, 4), (5, 4)))], avoids=[Avoid(("G",))])
    guard = Listed(oas=[OATake("main", 1)])
    entrants = [
        Entrant("M", "red", profile("l1_sample"), mover, "", (3, 4)),
        Entrant("G", "blue", profile(gs), guard, "", (3, 3)),
    ]
    faces = {"initiative": [12, 12, 1, 1]}
    result = Battle(RULES, entrants, Dice(faces), seed=0, round_cap=1, check=True, field=OPEN).run()
    assert not [e for e in result.log if isinstance(e, OpportunityAvoided)]
    assert not [r for r in mover.requests if type(r).__name__ == "AvoidOA"]

    # With a 1-stamina hold on M, G's cap becomes 2 + 1 = 3 >= base 3, so M IS asked AvoidOA.
    mover2 = Listed(turns=[Move(((4, 4),))], avoids=[Avoid(("G",))])
    guard2 = Listed(hold_answers=[Holds({"M": 1})], oas=[OATake("main", 1)])
    entrants2 = [
        Entrant("G", "blue", profile(gs), guard2, "", (3, 3)),
        Entrant("M", "red", profile("l1_sample"), mover2, "", (3, 4)),
    ]
    res2 = Battle(RULES, entrants2, Dice(faces), seed=0, round_cap=1, check=True, field=OPEN).run()
    avoided = [e for e in res2.log if isinstance(e, OpportunityAvoided)]
    assert avoided and avoided[0].enemies == ("G",)
    spent = [e for e in res2.log if isinstance(e, Spent) and e.category == "avoid"]
    assert spent and spent[0].amount == 2  # 1 base + 1 held


# --- Initiative Tiebreaker (0.11.2) --------------------------------------------------


def test_initiative_tiebreak_agility_plus_cunning_then_d12() -> None:
    """Packet 0.11.2: ties break by higher Agility + Cunning, then a d12 roll-off."""
    high_ac = Build(
        "hi", 1, Attributes(AGI=2, CUN=1), (("m", Loadout(weapon="dagger")),), ("fighter",)
    )
    low_ac = Build(
        "lo", 1, Attributes(AGI=1, CUN=1), (("m", Loadout(weapon="dagger")),), ("fighter",)
    )
    # Same initiative roll total (both CUN 1 -> +1 bonus; both roll 6+6+1 = 13).
    entrants = [
        Entrant("L", "red", profile(low_ac), Listed()),
        Entrant("H", "blue", profile(high_ac), Listed()),
    ]
    res = Battle(
        RULES, entrants, Dice({"initiative": [6, 6, 6, 6]}), seed=0, round_cap=1, check=True
    ).run()
    init = next(e for e in res.log if isinstance(e, InitiativeRolled))
    assert init.order == ("H", "L")
    assert len(init.rolls) == 2  # no roll-off needed when AGI + CUN separates them

    # Equal AGI + CUN: breaks by d12 roll-off (first roll-off ties 5-5, second separates 3 vs 9).
    entrants2 = [
        Entrant("A", "red", profile(high_ac), Listed()),
        Entrant("B", "blue", profile(high_ac), Listed()),
    ]
    res2 = Battle(
        RULES,
        entrants2,
        Dice({"initiative": [6, 6, 6, 6, 5, 5, 3, 9]}),
        seed=0,
        round_cap=1,
        check=True,
    ).run()
    init2 = next(e for e in res2.log if isinstance(e, InitiativeRolled))
    assert init2.order == ("B", "A")
    assert init2.rolls == (("A", 13), ("B", 13), ("A", 5), ("B", 5), ("A", 3), ("B", 9))


# --- Helping the Dying (0.11.2) ------------------------------------------------------


def test_helping_the_dying_packet_example() -> None:
    """Packet 0.11.2 example: ally at 3 Shock within 1 square, helper with INT 1. First tend
    costs 5, rolls 2d12 + 1 = 15 >= 13 -> Shock drops to 2. Second tend costs 6."""
    medic_build = Build(
        "medic",
        1,
        Attributes(STR=1, AGI=1, INT=1),
        (("m", Loadout(weapon="longsword", grip="one")),),
        ("fighter",),
    )
    medic = Listed(turns=[HelpDying("D"), HelpDying("D"), EndTurn()])
    # Put D in 3 Shock before M's turn: E hits for 15 (0 blocks, armor 2 -> 13 injury -> -3 HP).
    enemy = Listed(turns=[Attack("D")], commit=[2])
    entrants = [
        Entrant("E", "blue", profile("l1_sample"), enemy, "", (5, 4)),
        Entrant("M", "red", profile(medic_build), medic, "", (4, 5)),
        Entrant("D", "red", profile("l1_sample"), Listed(), "", (4, 4)),
    ]
    faces = {
        "initiative": [12, 12, 8, 8, 1, 1],
        "attack:E": [5, 4],  # (5+3)+(4+3) = 15, armor 2 -> 13 injury -> -3 HP, 3 Shock
        # M's tends: 7+7+1=15 >= 13 (ok -> 2 Shock), then 1+2+1=4 < 12 (fail); D's dying roll: 6+6
        "dying": [7, 7, 1, 2, 6, 6],
    }
    res = Battle(RULES, entrants, Dice(faces), seed=0, round_cap=1, check=True, field=OPEN).run()
    helped = [e for e in res.log if isinstance(e, DyingHelped)]
    assert len(helped) == 2
    assert (helped[0].helper, helped[0].target, helped[0].total, helped[0].succeeded) == (
        "M",
        "D",
        15,
        True,
    )
    assert helped[0].shock_after == 2
    assert (helped[1].total, helped[1].succeeded, helped[1].shock_after) == (4, False, 2)
    spent = [e.amount for e in res.log if isinstance(e, Spent) and e.category == "help_dying"]
    assert spent == [5, 6]  # base 5, then 5 + 1 escalation


# --- Forced Movement & Ending 0-Stamina Holds (0.11.6) -------------------------------


def test_forced_movement_rules_and_no_oa_or_hold_end() -> None:
    """Packet 0.11.6: 1 square, empty, wall corners apply, not closer to mover, doesn't
    provoke OAs or trigger/end holds."""
    corner_map = parse_map(".....\n..#..\n.....\n.....\n.....")
    # Mover at (1, 2), target at (2, 2); wall at (2, 1) blocks (3, 1) and (1, 1) under no_cut.
    valid = forced_move_squares(
        corner_map, RULES.grid, mover=(1, 2), target=(2, 2), occupied=frozenset({(1, 2), (2, 2)})
    )
    assert (3, 1) not in valid  # blocked by wall corner at (2, 1)
    assert (1, 1) not in valid  # blocked by wall corner at (2, 1)
    assert (1, 2) not in valid  # occupied by mover
    assert (3, 2) in valid and (3, 3) in valid and (2, 3) in valid and (1, 3) in valid

    entrants = [
        Entrant("A", "red", profile("l1_sample"), Listed(), "", (1, 2)),
        Entrant("B", "blue", profile("l1_sample"), Listed(), "", (2, 2)),
    ]
    b = Battle(RULES, entrants, Dice({}), seed=0, round_cap=1, check=True, field=corner_map)
    a, target = b.state.get("A"), b.state.get("B")
    b.ops.place(a, (1, 2))
    b.ops.place(target, (2, 2))
    b.ops.set_hold(a, "B", 3)
    # Closer square or corner-cut square is rejected.
    with pytest.raises(RulesError):
        b.ops.force_move(target, (3, 1), by="A")
    # Valid square succeeds without provoking OA or ending A's hold on B.
    b.ops.force_move(target, (3, 2), by="A")
    assert target.pos == (3, 2)
    assert a.holds == {"B": 3}  # hold still active!
    assert any(isinstance(e, ForcedMoved) and e.to == (3, 2) for e in b.log)
    assert not any(isinstance(e, OpportunityProvoked) for e in b.log)


def test_spending_all_held_stamina_ends_the_hold() -> None:
    """Packet 0.11.6: spending all of a hold's held stamina emits HoldEnded(reason='spent')."""
    entrants = [
        Entrant("A", "red", profile("l1_sample"), Listed(), "", (2, 2)),
        Entrant("B", "blue", profile("l1_sample"), Listed(), "", (3, 2)),
    ]
    b = Battle(RULES, entrants, Dice({}), seed=0, round_cap=1, check=True, field=OPEN)
    a = b.state.get("A")
    b.ops.set_hold(a, "B", 2)
    b.ops.spend_hold(a, "B", 2)
    assert "B" not in a.holds and a.parked == 0
    assert any(
        isinstance(e, HoldEnded) and e.who == "A" and e.target == "B" and e.reason == "spent"
        for e in b.log
    )


# --- 0.12.0 Class Cores: Second Wind, Opportunist, Press the Wound, Poised Guard -----


def test_fighter_second_wind() -> None:
    """0.12.0 Fighter core: off-turn / before-blocks recovery, 0 stamina, +1 escalation until
    next turn ends, skips next end-of-turn recovery, can't reuse until skipped."""
    # Round 1: F spends 9 (3 steps: 2+3+4=9 -> 7, recovers 4 -> 11). Then A attacks F: before
    # blocks, F uses Second Wind (+4 -> 15, escalation -> 1). On round 2, F's 1st step costs
    # 2 + 1 = 3, and F's end-of-turn recovery is skipped (RecoverySkipped).
    f = Listed(
        turns=[Attack("A"), EndTurn(), Attack("A"), EndTurn()],
        commit=[3, 1],
        uses=[UseAbility("second_wind")],
        block_answers=[Blocks(2, 0)],
    )
    a = Listed(
        turns=[Attack("F"), EndTurn(), EndTurn()],
        commit=[2],
        block_answers=[Blocks(3, 0), Blocks(2, 0)],
    )
    entrants = [
        Entrant("F", "red", profile("l1_sample"), f),
        Entrant("A", "blue", profile("l1_heavy"), a),
    ]
    faces = {
        "initiative": [12, 12, 1, 1],
        "attack:F": [1, 1, 1, 1],
        "attack:A": [4, 4],
    }
    res = Battle(RULES, entrants, Dice(faces), seed=0, round_cap=2, check=True).run()
    used = [e for e in res.log if isinstance(e, AbilityUsed) and e.who == "F"]
    assert [(u.ability, u.window, u.strain_after) for u in used] == [
        ("second_wind", "before_blocks", 0)
    ]
    # Second Wind raised escalation to 1, so F's round 2 first attack step costs 2 + 1 = 3!
    f_attacks = [
        e for e in res.log if isinstance(e, Spent) and e.who == "F" and e.category == "attack"
    ]
    assert f_attacks[0].parts == (2, 3, 4)
    assert f_attacks[1].parts == (3,)
    # F's round 2 end-of-turn recovery was skipped.
    skipped = [e for e in res.log if isinstance(e, RecoverySkipped) and e.who == "F"]
    assert len(skipped) == 1
    # Verify Second Wind was NOT offered on F's own turn.
    turn_cmds = [r for r in f.requests if type(r).__name__ == "TurnCommand"]
    assert all(not r.abilities for r in turn_cmds)


def test_rogue_opportunist_opening_and_escalation() -> None:
    """0.12.0 Rogue core: act in opening dash phase before turn 1 within 1 + CUN stamina;
    counts toward escalation until Rogue's turn ends; once between turns, resets after turn."""
    # l1_rogue_opportunist has CUN 1 (budget 2) and shortsword (base 1).
    # Opening dash phase: R makes 1-step shortsword attack (cost 1 <= budget 2; escalation -> 1).
    # Then on R's own turn 1: 1-step shortsword attack costs 1 + 1 = 2!
    r = Listed(
        off_turn=[Attack("B"), Pass(), Pass()],
        turns=[Attack("B"), EndTurn()],
        commit=[1, 1],
    )
    b = Listed(block_answers=[Blocks(2, 0), Blocks(2, 0)])
    entrants = [
        Entrant("B", "blue", profile("l1_sample"), b, "", (3, 3)),
        Entrant("R", "red", profile("l1_rogue_opportunist"), r, "", (3, 4)),
    ]
    faces = {"initiative": [12, 12, 1, 1], "attack:R": [2, 2]}
    res = Battle(RULES, entrants, Dice(faces), seed=0, round_cap=1, check=True, field=OPEN).run()
    # Opening dash phase attack happens BEFORE B's turn!
    opp_used = [e for e in res.log if isinstance(e, AbilityUsed) and e.ability == "opportunist"]
    assert len(opp_used) == 1
    r_attacks = [
        e for e in res.log if isinstance(e, Spent) and e.who == "R" and e.category == "attack"
    ]
    assert r_attacks[0].parts == (1,)  # opening dash phase
    assert r_attacks[1].parts == (2,)  # on R's turn 1, carrying escalation = 1!
    # Check budget enforcement: shortsword 2 steps = 1 + 2 = 3 > budget 2, so max_steps was 1.
    commits = [req for req in r.requests if type(req).__name__ == "Commitment"]
    assert commits[0].max_steps == 1  # capped by 1 + CUN = 2


def test_rogue_opportunist_ranged_shot() -> None:
    """0.12.0 Rogue core: Opportunist also allows a ranged shot (with aims) within 1 + CUN."""
    archer_rogue = Build(
        "ar",
        1,
        Attributes(FIN=1, CUN=2),  # 1+3 = 4 EP; budget = 1 + 2 = 3 -> shortbow (base 3, 0 aims)
        (("main", Loadout(weapon="shortbow", grip="two", armor="none")),),
        ("rogue",),
        frozenset({"shortbow"}),
    )
    r = Listed(off_turn=[Shoot("B")], aims=[0])
    b = Listed(block_answers=[Blocks(2, 0)])
    entrants = [
        Entrant("B", "blue", profile("l1_sample"), b, "", (8, 4)),
        Entrant("R", "red", profile(archer_rogue), r, "", (4, 4)),
    ]
    faces = {"initiative": [12, 12, 1, 1], "attack:R": [2, 3]}
    res = Battle(RULES, entrants, Dice(faces), seed=0, round_cap=1, check=True, field=OPEN).run()
    assert any(isinstance(e, ShotDeclared) and e.shooter == "R" for e in res.log)
    assert any(isinstance(e, AbilityUsed) and e.ability == "opportunist" for e in res.log)


def test_barbarian_press_the_wound() -> None:
    """0.12.0 Barbarian core: once on your turn, when a melee attack deals >= 1 HP damage,
    recover weapon base cost (longsword base 2). Doesn't trigger on 0 HP damage."""
    # First attack: B blocks all -> 0 injury -> no Press the Wound offered.
    # Second attack on same turn: B doesn't block -> >= 1 injury -> Press the Wound recovers 2!
    # Third attack on same turn: already used this turn -> not offered again.
    barb = Listed(
        turns=[Attack("T"), Attack("T"), Attack("T"), EndTurn()],
        commit=[1, 1, 1],
        uses=[UseAbility("press_the_wound")],
    )
    target = Listed(block_answers=[Blocks(3, 0), Blocks(0, 0), Blocks(0, 0)])
    entrants = [
        Entrant("B", "red", profile("l1_barbarian"), barb),
        Entrant("T", "blue", profile("l1_sample"), target),
    ]
    faces = {"initiative": [12, 12, 1, 1], "attack:B": [1, 4, 4]}
    res = Battle(RULES, entrants, Dice(faces), seed=0, round_cap=1, check=True).run()
    asked = [r for r in barb.requests if isinstance(r, AbilityRequest)]
    assert len(asked) == 1 and asked[0].window == "on_melee_wound"
    used = [e for e in res.log if isinstance(e, AbilityUsed) and e.ability == "press_the_wound"]
    assert len(used) == 1
    i = res.log.index(used[0])
    rec = res.log[i + 1]
    assert isinstance(rec, Recovered) and rec.who == "B" and rec.amount == 2  # longsword base 2


def test_monk_poised_guard_blocks_and_ends_hold() -> None:
    """0.12.0 Monk core: unarmored with no shield, spends up to 2 held stamina on attacker for
    non-escalating perfect blocks that don't raise remaining perfect block costs."""
    # Round 1: M ends turn holding 2 on A.
    # A attacks M for 2 steps: 2*(5+3)=16 damage, 0 crits. M has MD 2, armor 0.
    # M uses poised_guard_2 (spends 2 held stamina -> HoldEnded 'spent') and declares 4 perfect
    # blocks total: 2 prepaid + 2 paid from ready stamina at cost 1 + 2 = 3 (instead of 1+2+3+4=10)!
    monk = Listed(
        turns=[EndTurn()],
        hold_answers=[Holds({"A": 2})],
        uses=[UseAbility("poised_guard_2")],
        block_answers=[Blocks(4, 0)],
    )
    attacker = Listed(turns=[Attack("M"), EndTurn()], commit=[2])
    entrants = [
        Entrant("M", "red", profile("l1_monk_unarmored"), monk),
        Entrant("A", "blue", profile("l1_sample"), attacker),
    ]
    faces = {"initiative": [12, 12, 1, 1], "attack:A": [5, 5]}
    res = Battle(RULES, entrants, Dice(faces), seed=0, round_cap=1, check=True).run()
    assert any(isinstance(e, HoldSpent) and e.who == "M" and e.tokens == 2 for e in res.log)
    assert any(
        isinstance(e, HoldEnded) and e.who == "M" and e.target == "A" and e.reason == "spent"
        for e in res.log
    )
    block_spent = [
        e for e in res.log if isinstance(e, Spent) and e.who == "M" and e.category == "block"
    ]
    assert block_spent and block_spent[0].parts == (1, 2) and block_spent[0].amount == 3
    decl = next(e for e in res.log if isinstance(e, BlocksDeclared) and e.defender == "M")
    assert (decl.perfect, decl.grazing) == (4, 0)

    # Wearing armor or shield disables Poised Guard.
    armored_monk = Listed(turns=[EndTurn()], hold_answers=[Holds({"A": 2})])
    entrants2 = [
        Entrant("M", "red", profile("l1_monk"), armored_monk),
        Entrant("A", "blue", profile("l1_sample"), Listed(turns=[Attack("M")], commit=[1])),
    ]
    Battle(RULES, entrants2, Dice(faces), seed=0, round_cap=1, check=True).run()
    assert not [r for r in armored_monk.requests if isinstance(r, AbilityRequest)]


# --- Agent & CLI Integration Under 0.12.0 --------------------------------------------


def test_tactical_agent_attacks_after_pre_turn_dash_and_sets_holds() -> None:
    """Regression: under unified escalation (0.11.0+), a tactical agent that dashed before its
    turn (or on its turn) still attacks rather than mistaking actions_this_turn > 0 for having
    already attacked; and sets holds on a pressured enemy in reach."""
    # Place A and B 7 squares apart: A (Movement 6) must dash 1 square on its turn to reach B,
    # raising actions_this_turn to 1 before attacking. A must still attack B!
    entrants = [
        Entrant(
            "A",
            "red",
            profile("l1_sample"),
            make_agent({"kind": "tactical", "commit": "fixed:2"}, RULES),
            "",
            (1, 5),
        ),
        Entrant(
            "B",
            "blue",
            profile("l1_sample"),
            make_agent({"kind": "tactical", "commit": "fixed:2"}, RULES),
            "",
            (8, 5),
        ),
    ]
    faces = {"initiative": [12, 12, 1, 1], "attack:A": [5] * 10, "attack:B": [4] * 10}
    res = Battle(RULES, entrants, Dice(faces), seed=0, round_cap=2, check=True, field=OPEN).run()
    assert any(isinstance(e, AttackDeclared) and e.attacker == "A" for e in res.log)
    assert any(isinstance(e, HoldSet) for e in res.log)


def test_human_agent_handles_holds_and_no_strain_display() -> None:
    """HumanAgent parses holds (ID:N and none) and omits strain under v0.12.0."""
    # Opening dash phase (p), A's turn (e), A's holds (B:2), post-A dash (p), post-B dash (p).
    io = ScriptedIO(["p", "e", "B:2", "p", "p"])
    human = HumanAgent(RULES, io)
    entrants = [
        Entrant("A", "red", profile("l1_sample"), human, "", (2, 2)),
        Entrant("B", "blue", profile("l1_sample"), Listed(), "", (4, 2)),
    ]
    res = Battle(
        RULES,
        entrants,
        Dice({"initiative": [12, 12, 1, 1]}),
        seed=0,
        round_cap=1,
        check=True,
        field=OPEN,
    ).run()
    assert any(
        isinstance(e, HoldSet) and e.who == "A" and e.target == "B" and e.tokens == 2
        for e in res.log
    )
    shown = "\n".join(io.shown)
    assert "strain" not in shown.lower()
    assert "Set holds" in shown
