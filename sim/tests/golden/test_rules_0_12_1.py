"""Golden tests for packet 0.12.1:
- Baseline promotion (`v0.12.1`, equipment table `v0_12_1`) and Sample Character
- Weapon proficiencies shelved (Ledger H-11): any melee weapon grants +1 MD (unless FIN < 0)
  and +1 per even FIN
- Dual wielding shelved (Ledger H-12): second melee weapon grants +0 MD
- Shields: tiered Strength requirements (+1 RD at STR 1, +1 MD at STR 2, no attribute
  penalties), base-5 equip action and base-1 remove action on your turn only (removing a
  shield frees that hand immediately)
- Armor: Strength-gated even-Agility defense (light: full; medium: capped at even STR;
  heavy: capped at even STR - 1, min 0), action-tax Strength shortfall (+1 stamina on every
  action per point of STR short, zero negative attributes), and heavy-armor dash cost +1
  (base 2)
- Simplified Drawing Weapons: free before attacking/shooting on your turn; post-action and
  off-turn weapon draws are always actions (normal weapons: base + escalation only if you
  haven't attacked/shot since turn start; Quick-draw: 1 + escalation either way)
- Step 4 (Reactions) off-turn drawing (`ReactDrawRequest`), including point-blank OA shot
  cancellation ("drew a weapon"), TacticalAgent, HumanAgent, and wire serialization
"""

from stamina_engine.agents.decisions import (
    Attack,
    BlocksRequest,
    Draw,
    DrawOption,
    EndTurn,
    Move,
    OATake,
    Pass,
    ReactDrawRequest,
    Shoot,
)
from stamina_engine.agents.human import HumanAgent, ScriptedIO
from stamina_engine.agents.listed import Listed
from stamina_engine.agents.scripted import make_agent
from stamina_engine.agents.wire import request as wire_request
from stamina_engine.core.dice import ScriptedDice
from stamina_engine.engine.battle import Battle, Entrant
from stamina_engine.engine.events import Drew, Injured, ShotCancelled, Spent
from stamina_engine.grid.battlefield import parse_map
from stamina_engine.model.build import Attributes, Build, Loadout, load_build
from stamina_engine.model.derive import CombatProfile, derive, equipment_for
from stamina_engine.rules.exchange import Blocks
from stamina_engine.rules.pricing import Pricing, Quote, Track, Trackers
from stamina_engine.rules.ruleset import BASELINE, RuleSet, preset

RULES = preset("v0.12.1")
RULES_12_0 = preset("v0.12.0")
OPEN = parse_map("\n".join(["." * 12] * 12))


class Dice:
    def __init__(self, faces: dict[str, list[int]]) -> None:
        self.sources = {k: ScriptedDice(v) for k, v in faces.items()}

    def dice(self, name: str) -> ScriptedDice:
        return self.sources.setdefault(name, ScriptedDice([6] * 30))


def profile(build: str | Build, rules: RuleSet = RULES) -> CombatProfile:
    b = load_build(build) if isinstance(build, str) else build
    return derive(b, rules)


# --- Baseline, Equipment Table & Sample Character ------------------------------------


def test_baseline_and_sample_character_v0_12_1() -> None:
    assert BASELINE == "v0.12.1"
    assert equipment_for(RULES) == "v0_12_1"
    assert equipment_for(RULES_12_0) == "v0_12"
    p = profile("l1_sample")
    lo = p.main
    assert (p.hp_max, p.stamina_max, p.recovery, p.strain_max) == (10, 16, 4, 0)
    assert (lo.melee_defense, lo.ranged_defense, lo.armor) == (3, 2, 2)
    assert (lo.attributes.STR, lo.attributes.AGI, lo.attributes.FIN) == (2, 1, 1)
    assert lo.oa_cap == 2


# --- Weapon Proficiencies Shelved (Ledger H-11) --------------------------------------


def test_weapon_proficiencies_shelved() -> None:
    """Any melee weapon grants +1 MD (unless FIN < 0) and +1 per even FIN without needing
    proficiency under v0.12.1; v0.12.0 still requires proficiency."""
    unproficient = Build(
        "unprof",
        1,
        Attributes(FIN=2),
        (("main", Loadout(weapon="longsword", grip="one", armor="none")),),
        (),  # no cores, no proficiencies
        frozenset(),
    )
    p121 = profile(unproficient, RULES)
    p120 = profile(unproficient, RULES_12_0)
    assert p121.main.melee_defense == 3  # 1 base + 1 weapon + 1 even FIN
    assert p120.main.melee_defense == 1  # v0.12.0 requires proficiency

    # Under v0.12.1 armor never pushes attributes negative (shortfall is +1 stamina/action),
    # so FIN stays 0 and keeps the +1 melee weapon bonus; v0.12.0 still drops FIN to -1.
    short_med = Build(
        "short_med",
        1,
        Attributes(STR=0, AGI=1, FIN=0),
        (("main", Loadout(weapon="longsword", grip="one", armor="medium")),),
        (),
        frozenset({"longsword"}),
    )
    p121_short = profile(short_med, RULES)
    assert (p121_short.main.attributes.AGI, p121_short.main.attributes.FIN) == (1, 0)
    assert p121_short.main.armor_action_extra == 1
    assert p121_short.main.melee_defense == 2  # 1 base + 1 weapon (FIN stays 0)
    p120_short = profile(short_med, RULES_12_0)
    assert (p120_short.main.attributes.AGI, p120_short.main.attributes.FIN) == (0, -1)
    assert p120_short.main.melee_defense == 1  # base 1 kept (AGI 0), +1 weapon lost (FIN -1)


# --- Dual Wielding Shelved (Ledger H-12) ---------------------------------------------


def test_dual_wielding_shelved() -> None:
    """Second melee weapon grants +0 MD under v0.12.1 (v0.12.0 keeps +1 MD)."""
    dual = Build(
        "dual",
        1,
        Attributes(FIN=2),
        (
            (
                "main",
                Loadout(weapon="shortsword", grip="one", off_hand="dagger", armor="none"),
            ),
        ),
        ("rogue",),
        frozenset({"shortsword", "dagger"}),
    )
    assert profile(dual, RULES).main.melee_defense == 3  # 1 + 1 weapon + 1 even FIN
    assert profile(dual, RULES_12_0).main.melee_defense == 4  # +1 for second weapon


# --- Shields: Tiered Strength Requirements & Equip / Remove Actions ------------------


def test_shield_tiered_strength_requirements() -> None:
    """Shield gives +1 RD (requires STR 1) and +1 MD (requires STR 2) with no attribute
    penalties under v0.12.1."""
    str2 = Build(
        "str2",
        12,
        Attributes(STR=2, AGI=2, FIN=2),
        (("main", Loadout(weapon="longsword", grip="one", off_hand="shield", armor="none")),),
        ("fighter",),
    )
    str1 = Build(
        "str1",
        12,
        Attributes(STR=1, AGI=2, FIN=2),
        (("main", Loadout(weapon="longsword", grip="one", off_hand="shield", armor="none")),),
        ("fighter",),
    )
    str0 = Build(
        "str0",
        12,
        Attributes(STR=0, AGI=2, FIN=2),
        (("main", Loadout(weapon="longsword", grip="one", off_hand="shield", armor="none")),),
        ("fighter",),
    )
    p2, p1, p0 = profile(str2, RULES), profile(str1, RULES), profile(str0, RULES)
    # Attributes are never penalized by a shield.
    assert (p2.main.attributes.AGI, p2.main.attributes.FIN) == (2, 2)
    assert (p1.main.attributes.AGI, p1.main.attributes.FIN) == (2, 2)
    assert (p0.main.attributes.AGI, p0.main.attributes.FIN) == (2, 2)
    # Base 1 + weapon 1 + even AGI 1 + even FIN 1 = 4 MD; base 1 + even AGI 1 = 2 RD.
    assert (p2.main.melee_defense, p2.main.ranged_defense) == (5, 3)  # +1 MD, +1 RD
    assert (p1.main.melee_defense, p1.main.ranged_defense) == (4, 3)  # +0 MD, +1 RD
    assert (p0.main.melee_defense, p0.main.ranged_defense) == (4, 2)  # +0 MD, +0 RD
    # Under v0.12.0, shields had no Strength requirement (+1/+1 even at STR 0).
    p0_120 = profile(str0, RULES_12_0)
    assert (p0_120.main.melee_defense, p0_120.main.ranged_defense) == (5, 3)

    # Armor Strength shortfall adds +1 stamina/action (no negative attribute penalties),
    # medium armor caps even-AGI defense at even STR (0 at STR 0), and shield gives +0/+0 at STR 0.
    str0_med = Build(
        "str0_med",
        10,
        Attributes(STR=0, AGI=2, FIN=2),
        (("main", Loadout(weapon="longsword", grip="one", off_hand="shield", armor="medium")),),
        ("fighter",),
    )
    pm = profile(str0_med, RULES)
    assert (pm.main.attributes.AGI, pm.main.attributes.FIN) == (2, 2)
    assert pm.main.armor_action_extra == 1
    assert (pm.main.melee_defense, pm.main.ranged_defense) == (3, 1)  # 1 + weapon + even FIN; 1 RD

    # Unarmed STR 1 caster holding a shield gets +0 MD and +1 RD (not a free weapon MD bonus).
    caster_sh = Build(
        "caster_sh",
        1,
        Attributes(STR=1, AGI=0, FIN=0),
        (("main", Loadout(weapon=None, off_hand="shield", armor="none")),),
        (),
    )
    pc = profile(caster_sh, RULES)
    assert (pc.main.melee_defense, pc.main.ranged_defense) == (1, 2)


def test_shield_equip_and_remove_actions_free_hand_immediately() -> None:
    """Equipping a shield is a base-5 action, removing is a base-1 action, on your turn only;
    removing a shield frees that hand immediately so a Fighter can switch to a 2H grip."""
    b = Build(
        "shield_sw",
        1,
        Attributes(STR=2, AGI=1, FIN=1),
        (
            ("sp_sh", Loadout(weapon="spear", grip="one", off_hand="shield", armor="medium")),
            ("sp_1h", Loadout(weapon="spear", grip="one", armor="medium")),
            ("sp_2h", Loadout(weapon="spear", grip="two", armor="medium")),
            ("bow", Loadout(weapon="shortbow", grip="two", armor="medium")),
        ),
        ("fighter",),
    )
    p = profile(b, RULES)
    pricing = Pricing(RULES)
    sp_sh, sp_1h, sp_2h, bow = (
        p.loadout("sp_sh"),
        p.loadout("sp_1h"),
        p.loadout("sp_2h"),
        p.loadout("bow"),
    )
    # On turn: remove costs base 1 + escalation (action); equip costs base 5 + escalation (action).
    assert pricing.draw(sp_sh, sp_1h, on_turn=True, used_weapon=False, bow_hands=False) == Quote(
        (1,), Track.ON_TURN
    )
    assert pricing.draw(sp_1h, sp_sh, on_turn=True, used_weapon=False, bow_hands=False) == Quote(
        (5,), Track.ON_TURN
    )
    assert pricing.draw(
        sp_1h, sp_sh, on_turn=True, used_weapon=False, bow_hands=False, trackers=Trackers(2)
    ) == Quote((7,), Track.ON_TURN)
    # Off turn: neither equip nor remove is allowed.
    assert pricing.draw(sp_sh, sp_1h, on_turn=False, used_weapon=False, bow_hands=False) is None
    assert pricing.draw(sp_1h, sp_sh, on_turn=False, used_weapon=False, bow_hands=False) is None
    # Removing a shield and switching a spear to 2H grip (in one step or two) is allowed before
    # attacking/shooting/casting on your turn, costing base 1 + escalation for the removal.
    assert pricing.draw(sp_sh, sp_2h, on_turn=True, used_weapon=False, bow_hands=False) == Quote(
        (1,), Track.ON_TURN
    )
    assert pricing.draw(
        sp_1h, sp_2h, on_turn=True, used_weapon=False, bow_hands=False, trackers=Trackers(1)
    ) == Quote(())
    # After attacking/shooting on your turn: equipping a shield and changing grip are disallowed.
    assert (
        pricing.draw(
            bow, sp_sh, on_turn=True, used_weapon=True, bow_hands=True, trackers=Trackers(1)
        )
        is None
    )
    assert (
        pricing.draw(
            sp_1h, sp_2h, on_turn=True, used_weapon=True, bow_hands=False, trackers=Trackers(1)
        )
        is None
    )

    # In a battle: removing a shield on turn 1 frees the hand immediately (sp_2h is offered for
    # 0 stamina right away), and escalation (+1) carries into the 2H spear attack on the same turn.
    mover = Listed(
        turns=[Draw("sp_1h"), Draw("sp_2h"), Attack("B"), EndTurn()],
        commit=[1],
    )
    entrants = [
        Entrant("A", "red", p, mover, "sp_sh", (2, 2)),
        Entrant("B", "blue", profile("l1_sample"), Listed(), "", (4, 2)),  # distance 2 (reach 2!)
    ]
    res = Battle(
        RULES,
        entrants,
        Dice({"initiative": [12, 12, 1, 1], "attack:A": [5]}),
        seed=0,
        round_cap=1,
        check=True,
        field=OPEN,
    ).run()
    turn_cmds = [r for r in mover.requests if type(r).__name__ == "TurnCommand"]
    # Second TurnCommand of round 1 (right after removing shield): sp_2h IS offered for 0 stamina.
    r1_after_remove = {d.loadout: d.quote for d in turn_cmds[1].draws}
    assert r1_after_remove["sp_2h"] == Quote(())
    drew = [e for e in res.log if isinstance(e, Drew) and e.who == "A"]
    assert [(d.loadout, d.cost) for d in drew] == [("sp_1h", 1), ("sp_2h", 0)]
    # 2H spear attack pays base 2 + 1 escalation carried from removing the shield = 3 stamina!
    atk_spent = [
        e for e in res.log if isinstance(e, Spent) and e.who == "A" and e.category == "attack"
    ]
    assert len(atk_spent) == 1 and atk_spent[0].parts == (3,)


# --- Simplified Drawing Weapons ------------------------------------------------------


def test_drawing_weapons_pricing_matrix() -> None:
    """Verify every drawing case under v0.12.1: free before acting on your turn; after acting
    or off-turn, every weapon draw is an action (normal requires not having attacked/shot since
    turn start; Quick-draw is 1 + escalation either way)."""
    b = Build(
        "arsenal",
        1,
        Attributes(STR=2, AGI=1, FIN=1),
        (
            ("bow", Loadout(weapon="shortbow", grip="two", armor="none")),
            ("sword", Loadout(weapon="longsword", grip="one", armor="none")),
            ("dagger", Loadout(weapon="dagger", grip="one", armor="none")),
            ("shortsword", Loadout(weapon="shortsword", grip="one", armor="none")),
            ("greatsword", Loadout(weapon="greatsword", grip="two", armor="none")),
            ("spear", Loadout(weapon="spear", grip="one", armor="none")),
        ),
        ("fighter",),
    )
    p = profile(b, RULES)
    pricing = Pricing(RULES)
    bow, sword, dagger, ss, gs, spear = (
        p.loadout(n) for n in ("bow", "sword", "dagger", "shortsword", "greatsword", "spear")
    )
    # 1. On turn, before attacking/shooting: free.
    assert pricing.draw(bow, gs, on_turn=True, used_weapon=False, bow_hands=False) == Quote(())
    assert pricing.draw(bow, dagger, on_turn=True, used_weapon=False, bow_hands=False) == Quote(())

    # 2. On turn, after shooting bow or attacking with a 1H sword (escalation 1):
    #    no normal weapons; Quick-draw is always an action (1 + escalation = 2).
    for cur, bow_flag in ((bow, True), (sword, False)):
        assert (
            pricing.draw(
                cur, spear, on_turn=True, used_weapon=True, bow_hands=bow_flag, trackers=Trackers(1)
            )
            is None
        )
        assert (
            pricing.draw(
                cur, gs, on_turn=True, used_weapon=True, bow_hands=bow_flag, trackers=Trackers(1)
            )
            is None
        )
        assert pricing.draw(
            cur, dagger, on_turn=True, used_weapon=True, bow_hands=bow_flag, trackers=Trackers(1)
        ) == Quote((2,), Track.ON_TURN)
        assert pricing.draw(
            cur, ss, on_turn=True, used_weapon=True, bow_hands=bow_flag, trackers=Trackers(1)
        ) == Quote((2,), Track.ON_TURN)

    # 3. Off turn (escalation 0), before attacking/shooting since turn start:
    #    every weapon draw (including Quick-draw) is an action costing base + escalation!
    assert pricing.draw(
        bow, dagger, on_turn=False, used_weapon=False, bow_hands=False
    ) == Quote((1,), Track.ON_TURN)
    assert pricing.draw(
        bow, sword, on_turn=False, used_weapon=False, bow_hands=False
    ) == Quote((2,), Track.ON_TURN)
    assert pricing.draw(
        bow, gs, on_turn=False, used_weapon=False, bow_hands=False
    ) == Quote((3,), Track.ON_TURN)
    # With prior off-turn dash (escalation 1): Quick-draw pays 1 + 1 = 2!
    assert pricing.draw(
        bow, dagger, on_turn=False, used_weapon=False, bow_hands=False, trackers=Trackers(1)
    ) == Quote((2,), Track.ON_TURN)

    # 4. Off turn (escalation 0), after attacking/shooting since turn start:
    #    normal weapons disallowed; Quick-draw is 1 + escalation (action).
    assert (
        pricing.draw(bow, sword, on_turn=False, used_weapon=True, bow_hands=True) is None
    )
    assert pricing.draw(
        bow, dagger, on_turn=False, used_weapon=True, bow_hands=True
    ) == Quote((1,), Track.ON_TURN)


# --- Step 4 Reactions Drawing, Escalation Carryover & Point-Blank OA -----------------


def test_reaction_draw_on_melee_attack_raises_md_and_taxes_next_turn() -> None:
    """Archer shoots turn 1 (both hands used), then draws its quick-draw shortsword in step 4
    of an incoming melee attack: blocks with the blade's MD (3 instead of 1) and pays +1
    escalation on its turn 2."""
    archer = Listed(
        turns=[Shoot("F"), EndTurn(), Draw("bow"), Shoot("F"), EndTurn()],
        aims=[0, 0],
        react_draws=[Draw("blade")],
        block_answers=[Blocks(2, 0)],
    )
    fighter = Listed(
        turns=[Attack("A"), EndTurn(), EndTurn()],
        commit=[1],
        block_answers=[Blocks(2, 0), Blocks(2, 0)],
    )
    entrants = [
        Entrant("A", "red", profile("l1_archer"), archer, "bow", (3, 3)),
        Entrant("F", "blue", profile("l1_sample"), fighter, "", (4, 3)),
    ]
    faces = {
        "initiative": [12, 12, 1, 1],
        "attack:A": [2, 2, 2, 2],
        "attack:F": [5],  # 5 + 3 = 8 damage
    }
    res = Battle(RULES, entrants, Dice(faces), seed=0, round_cap=2, check=True, field=OPEN).run()
    # Archer received a ReactDrawRequest during F's attack, and blocked with blade's MD (3 vs 1).
    rd_reqs = [r for r in archer.requests if isinstance(r, ReactDrawRequest)]
    assert len(rd_reqs) == 1
    assert [d.loadout for d in rd_reqs[0].draws] == ["blade"]
    assert rd_reqs[0].draws[0].quote == Quote((1,), Track.ON_TURN)
    blk_reqs = [r for r in archer.requests if isinstance(r, BlocksRequest)]
    assert blk_reqs[0].defense == 3  # blade MD (1 base + 1 weapon + 1 even FIN 2)
    assert profile("l1_archer").loadout("bow").melee_defense == 1
    # Because the reaction draw used a used hand (action), A's turn 2 shot pays +1 escalation!
    a_shots = [
        e for e in res.log if isinstance(e, Spent) and e.who == "A" and e.category == "shot"
    ]
    assert a_shots[0].parts == (4,)  # turn 1: longbow base 4 + 0
    assert a_shots[1].parts == (5,)  # turn 2: longbow base 4 + 1 carried from reaction draw!

    # Under v0.12.0, no ReactDrawRequest is ever sent.
    archer120 = Listed(turns=[Shoot("F"), EndTurn()], aims=[0], block_answers=[Blocks(2, 0)])
    fighter120 = Listed(turns=[Attack("A"), EndTurn()], commit=[1], block_answers=[Blocks(2, 0)])
    entrants120 = [
        Entrant("A", "red", profile("l1_archer", RULES_12_0), archer120, "bow", (3, 3)),
        Entrant("F", "blue", profile("l1_sample", RULES_12_0), fighter120, "", (4, 3)),
    ]
    Battle(
        RULES_12_0, entrants120, Dice(faces), seed=0, round_cap=1, check=True, field=OPEN
    ).run()
    assert not [r for r in archer120.requests if isinstance(r, ReactDrawRequest)]


def test_point_blank_oa_reaction_draw_cancels_shot() -> None:
    """Shooting in melee: drawing a blade in step 4 of the point-blank OA blocks with the
    blade's MD (1 + escalation action) and cancels the shot."""
    archer = Listed(
        turns=[Shoot("F"), EndTurn()],
        aims=[0],
        react_draws=[Draw("blade")],
        block_answers=[Blocks(2, 0)],
    )
    fighter = Listed(oas=[OATake("main", 1)])
    entrants = [
        Entrant("A", "red", profile("l1_archer"), archer, "bow", (3, 3)),
        Entrant("F", "blue", profile("l1_sample"), fighter, "", (4, 3)),
    ]
    faces = {"initiative": [12, 12, 1, 1], "attack:F": [5]}
    res = Battle(RULES, entrants, Dice(faces), seed=0, round_cap=1, check=True, field=OPEN).run()
    cancelled = [e for e in res.log if isinstance(e, ShotCancelled)]
    assert len(cancelled) == 1
    assert (cancelled[0].shooter, cancelled[0].reason) == ("A", "drew a weapon")
    # Every reaction draw (including Quick-draw) is an action (1 + escalation).
    draw_spent = [
        e for e in res.log if isinstance(e, Spent) and e.who == "A" and e.category == "draw"
    ]
    assert len(draw_spent) == 1
    assert draw_spent[0].amount == 1 and draw_spent[0].track == "on_turn"
    blk_reqs = [r for r in archer.requests if isinstance(r, BlocksRequest)]
    assert blk_reqs[0].defense == 3


# --- TacticalAgent, HumanAgent & Wire Support ----------------------------------------


def test_tactical_human_and_wire_react_draw() -> None:
    """TacticalAgent draws a blade on a heavy melee roll and passes on a tiny roll; HumanAgent
    displays the action flag and parses `d blade`; wire encodes `kind = 'react_draw'`."""
    archer_p = profile("l1_archer")
    tactical = make_agent({"kind": "tactical", "commit": "fixed:2"}, RULES)
    entrants = [
        Entrant("A", "red", archer_p, tactical, "bow", (3, 3)),
        Entrant("F", "blue", profile("l1_sample"), Listed(), "", (4, 3)),
    ]
    b = Battle(RULES, entrants, Dice({}), seed=0, round_cap=1, check=True, field=OPEN)
    a, f = b.state.get("A"), b.state.get("F")
    b.ops.place(a, (3, 3))
    b.ops.place(f, (4, 3))
    obs = b.observe("A")

    draws = (DrawOption("blade", Quote((1,), Track.ON_TURN)),)
    heavy_req = ReactDrawRequest(
        "A", obs, ("round 1",), "F", damage=12, crit_dice=0, ranged=False, draws=draws
    )
    tiny_req = ReactDrawRequest(
        "A", obs, ("round 1",), "F", damage=2, crit_dice=0, ranged=False, draws=draws
    )
    assert tactical.react_draw(heavy_req) == Draw("blade")
    assert tactical.react_draw(tiny_req) == Pass()

    # HumanAgent parses `d blade` and prints "(1 stamina, action)".
    io = ScriptedIO(["d blade"])
    human = HumanAgent(RULES, io)
    assert human.react_draw(heavy_req) == Draw("blade")
    assert "1 stamina, action" in "\n".join(io.shown)

    # Wire serialization for `se play --step`.
    w = wire_request(heavy_req)
    assert w["kind"] == "react_draw" and w["who"] == "A"
    assert w["fields"]["draws"][0]["loadout"] == "blade"


# --- Armor: Strength-Gated Agility, Action-Tax Shortfall & Heavy Dash Cost -----------


def test_armor_strength_gated_even_agility() -> None:
    """Light/unarmored grants full even Agility; medium caps even Agility at even Strength;
    heavy caps even Agility at max(0, even Strength - 1), for both MD and RD. v0.12.0 keeps
    legacy every-3rd / every-4th Agility steps."""

    def defs(armor: str, str_: int, agi: int, rules: RuleSet = RULES) -> tuple[int, int]:
        b = Build(
            "t",
            99,
            Attributes(STR=str_, AGI=agi, FIN=0),
            (("main", Loadout(weapon="longsword", grip="one", armor=armor)),),
            (),
            frozenset({"longsword"}),
        )
        lo = profile(b, rules).main
        return lo.melee_defense, lo.ranged_defense

    # Unarmored / Light: full even Agility regardless of Strength (base MD 2, RD 1).
    for armor in ("none", "light"):
        assert defs(armor, 0, 0) == (2, 1)
        assert defs(armor, 0, 2) == (3, 2)
        assert defs(armor, 0, 4) == (4, 3)
        assert defs(armor, 0, 6) == (5, 4)

    # Medium (Armor 2): even Agility capped at even Strength.
    assert defs("medium", 0, 4) == (2, 1)  # even STR 0 -> +0
    assert defs("medium", 1, 2) == (2, 1)  # even STR 0 -> +0
    assert defs("medium", 2, 2) == (3, 2)  # min(1, 1) -> +1
    assert defs("medium", 2, 4) == (3, 2)  # min(2, 1) -> +1
    assert defs("medium", 4, 2) == (3, 2)  # min(1, 2) -> +1
    assert defs("medium", 4, 4) == (4, 3)  # min(2, 2) -> +2
    assert defs("medium", 6, 6) == (5, 4)  # min(3, 3) -> +3

    # Heavy (Armor 3): even Agility capped at max(0, even Strength - 1).
    assert defs("heavy", 2, 4) == (2, 1)  # even STR 1 - 1 = 0 -> +0
    assert defs("heavy", 3, 4) == (2, 1)  # even STR 1 - 1 = 0 -> +0
    assert defs("heavy", 4, 2) == (3, 2)  # min(1, 1) -> +1
    assert defs("heavy", 4, 4) == (3, 2)  # min(2, 1) -> +1
    assert defs("heavy", 6, 4) == (4, 3)  # min(2, 2) -> +2
    assert defs("heavy", 6, 6) == (4, 3)  # min(3, 2) -> +2

    # Earlier preset (v0.12.0) keeps legacy every-3rd (medium) and every-4th (heavy) steps.
    assert defs("medium", 1, 3, RULES_12_0) == (3, 2)
    assert defs("medium", 1, 3, RULES) == (2, 1)
    assert defs("heavy", 3, 4, RULES_12_0) == (3, 2)
    assert defs("heavy", 3, 4, RULES) == (2, 1)


def test_armor_shortfall_action_tax_and_heavy_dash_pricing() -> None:
    """Being below armor's Strength requirement adds +1 stamina to every action per point short
    (no attribute penalties), and heavy armor adds +1 to dash base cost (base 2); blocks, OAs
    and free pre-action weapon draws are unaffected."""
    b = Build(
        "str2_heavy",
        12,
        Attributes(STR=2, AGI=2, FIN=2),
        (
            ("sword", Loadout(weapon="longsword", grip="one", armor="heavy")),
            ("sword_sh", Loadout(weapon="longsword", grip="one", off_hand="shield", armor="heavy")),
            ("dagger", Loadout(weapon="dagger", grip="one", armor="heavy")),
        ),
        ("fighter",),
    )
    p = profile(b, RULES)
    sword, sword_sh, dagger = p.loadout("sword"), p.loadout("sword_sh"), p.loadout("dagger")
    pricing = Pricing(RULES)

    # No attribute mutation; 1 short of heavy STR 3 -> +1 action tax, +1 heavy dash cost.
    assert sword.attributes == Attributes(STR=2, AGI=2, FIN=2)
    assert (sword.armor, sword.armor_action_extra, sword.armor_dash_extra) == (3, 1, 1)
    assert (p.hp_max, p.stamina_max) == (10, 18)  # L12: 6 + 10 HP + 2 level stamina

    # Melee attack & max_steps include armor_action_extra.
    assert pricing.melee_attack(2, 2, extra=sword.armor_action_extra) == Quote(
        (3, 4), Track.ON_TURN
    )
    assert pricing.max_steps(2, 7, extra=sword.armor_action_extra) == 2
    assert pricing.max_steps(2, 6, extra=sword.armor_action_extra) == 1

    # Dashes: heavy (+1) + 1 STR short (+1) -> base 3 on 1st dash; STR 3 heavy -> base 2.
    q_short_dash = pricing.move(
        3,
        on_turn=True,
        trackers=Trackers(),
        free_left=2,
        movement=2,
        extra_squares=2,
        dash_extra=sword.armor_action_extra + sword.armor_dash_extra,
    )
    assert q_short_dash.total == 3
    str3_heavy = Build(
        "str3_heavy",
        10,
        Attributes(STR=3, AGI=0, FIN=1),
        (("main", Loadout(weapon="longsword", grip="one", armor="heavy")),),
        ("fighter",),
    )
    h3 = profile(str3_heavy, RULES).main
    assert (h3.armor_action_extra, h3.armor_dash_extra) == (0, 1)
    assert (
        pricing.move(
            3,
            on_turn=True,
            trackers=Trackers(),
            free_left=2,
            movement=2,
            extra_squares=2,
            dash_extra=h3.armor_action_extra + h3.armor_dash_extra,
        ).total
        == 2
    )
    assert pricing.off_turn_purchase(Trackers(), extra=1) == Quote((2,), Track.ON_TURN)

    # Paid draws and shield equip/remove include armor_action_extra; free pre-action draw does not.
    assert pricing.draw(sword, dagger, on_turn=True, used_weapon=False, bow_hands=False) == Quote(
        ()
    )
    assert pricing.draw(
        sword_sh, sword, on_turn=True, used_weapon=False, bow_hands=False
    ) == Quote((2,), Track.ON_TURN)
    assert pricing.draw(
        sword, sword_sh, on_turn=True, used_weapon=False, bow_hands=False
    ) == Quote((6,), Track.ON_TURN)
    assert pricing.draw(
        sword, dagger, on_turn=False, used_weapon=True, bow_hands=False
    ) == Quote((2,), Track.ON_TURN)
    assert pricing.draw(
        dagger, sword, on_turn=False, used_weapon=False, bow_hands=False
    ) == Quote((3,), Track.ON_TURN)

    # Ranged shots, aim steps, and Helping the Dying include armor_action_extra (STR 0 heavy = +3).
    assert pricing.ranged_attack(3, 1, extra=3) == Quote((6, 5), Track.ON_TURN)
    assert pricing.help_dying(extra=3) == Quote((8,), Track.ON_TURN)

    # Blocks and opportunity attacks are never taxed by armor shortfall.
    assert pricing.blocks(2, 0) == Quote((1, 2))
    assert pricing.opportunity_attack(2, 1, Trackers(), cap=2) == Quote((2,))


def test_armor_shortfall_and_heavy_dash_in_battle() -> None:
    """End-to-end battle check: a STR 2 fighter in heavy armor (1 short) pays 3 stamina for its
    first dash (1 base + 1 heavy + 1 shortfall) and 4 for a following 1-step longsword attack
    (2 base + 1 shortfall + 1 escalation) with zero phantom Heavy Swing piercing, while its
    block (1) and opportunity attack (2) remain unaffected."""
    short_heavy = Build(
        "str2_heavy",
        1,
        Attributes(STR=2, AGI=0, FIN=1),
        (("main", Loadout(weapon="longsword", grip="one", armor="heavy")),),
        ("fighter",),
    )
    a_prof = profile(short_heavy, RULES)
    assert a_prof.main.movement == 5  # AGI 0 -> 5 free squares; 6th square triggers 1st dash
    a_agent = Listed(
        turns=[Move(((2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (7, 2))), Attack("B"), EndTurn()],
        commit=[1],
        block_answers=[Blocks(1, 0)],
        oas=[OATake("main", 1)],
    )
    b_agent = Listed(
        turns=[Attack("A"), Move(((9, 2),)), EndTurn()],
        commit=[1],
        block_answers=[Blocks(0, 0), Blocks(0, 0)],
    )
    entrants = [
        Entrant("A", "red", a_prof, a_agent, "main", (1, 2)),
        Entrant("B", "blue", profile("l1_sample", RULES), b_agent, "", (8, 2)),
    ]
    faces = {
        "initiative": [12, 12, 1, 1],
        "attack:A": [5, 5],  # 5 + 2 (longsword) + 1 (odd STR) = 8 raw; vs B's Armor 2 -> 6 HP
        "attack:B": [5],
    }
    res = Battle(RULES, entrants, Dice(faces), seed=0, round_cap=1, check=True, field=OPEN).run()
    a_spent = [e for e in res.log if isinstance(e, Spent) and e.who == "A"]
    by_cat = {e.category: e for e in a_spent}
    assert by_cat["extra_move"].parts == (3,)  # 1 base + 1 heavy + 1 STR shortfall
    assert by_cat["attack"].parts == (4,)  # 2 base + 1 STR shortfall + 1 escalation from dash
    assert by_cat["block"].parts == (1,)  # unaffected by STR shortfall
    assert by_cat["opportunity"].parts == (2,)  # weapon base 2, unaffected by STR shortfall
    b_inj = [e for e in res.log if isinstance(e, Injured) and e.who == "B"]
    assert b_inj[0].damage == 6  # 8 raw - 2 armor = 6 (armor_action_extra adds 0 piercing)
