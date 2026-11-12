"""The switches the designer may weigh against 0.10.0's ranged rules (Assumptions register,
pending designer): reaction timing, the reaction purchase cap, the single-purchase swap, the
crit rules C' and C, and the critical bonus inside the aim limit. Each is tested with a
constructed shot; the 0.10.0 defaults are tested in test_rules_0_10_0.py."""

from dataclasses import replace

from stamina_engine.agents.decisions import BlocksRequest, DiveRequest, Move, OATake, Shoot
from stamina_engine.agents.listed import Listed
from stamina_engine.core.dice import ScriptedDice
from stamina_engine.engine.battle import Battle, BattleResult, Entrant
from stamina_engine.grid.battlefield import Cell, parse_map
from stamina_engine.model.build import Build, Loadout, load_build
from stamina_engine.model.derive import CombatProfile, WeaponProfile, derive
from stamina_engine.model.equipment import load_table
from stamina_engine.rules.exchange import Blocks, resolve, roll_attack, roll_shot
from stamina_engine.rules.ruleset import RuleSet, preset

V10 = preset("v0.10.0")
TABLE = load_table("v0_10")
WIDE = parse_map("\n".join(["." * 30] * 5))


class Dice:
    def __init__(self, faces: dict[str, list[int]]) -> None:
        self.sources = {k: ScriptedDice(v) for k, v in faces.items()}

    def dice(self, name: str) -> ScriptedDice:
        return self.sources[name]


def archer(**attrs: int) -> Build:
    """The library archer (STR 1, AGI 1, FIN 2, longbow), with other attributes."""
    b = load_build("l1_archer")
    return replace(b, attributes=replace(b.attributes, **attrs), budget="ignore")


def profile(build: Build) -> CombatProfile:
    return derive(build, V10, TABLE)


def bow(build: Build) -> WeaponProfile:
    w = profile(build).main.weapon
    assert w is not None
    return w


def sample() -> CombatProfile:
    return profile(load_build("l1_sample"))


def of(agent: Listed, kind: type) -> list:
    return [r for r in agent.requests if isinstance(r, kind)]


def ranged(**kw: object) -> RuleSet:
    return V10.with_(ranged=replace(V10.ranged, **kw))


def fight(
    rules: RuleSet,
    roster: list[tuple[str, str, CombatProfile, Cell, Listed]],
    attacks: dict[str, list[int]],
) -> BattleResult:
    faces = {"initiative": [12, 12] + [1, 1] * (len(roster) - 1), "dying": [6] * 10}
    faces.update({f"attack:{k}": v for k, v in attacks.items()})
    entrants = [Entrant(cid, team, p, a, "", pos) for cid, team, p, pos, a in roster]
    return Battle(rules, entrants, Dice(faces), seed=0, round_cap=1, check=True, field=WIDE).run()


def shot_at(
    rules: RuleSet, shooter_at: Cell, target_at: Cell, dive: tuple[Cell, ...] | None
) -> tuple[BlocksRequest, Listed]:
    """The sample fighter (Melee Defense 3, Ranged Defense 2, 2 squares per off-turn
    purchase) is shot by the library archer and reacts along dive, if given."""
    t = Listed(dives=[Move(dive)] if dive else [], oas=[OATake("main", 1)])
    fight(
        rules,
        [
            ("A", "red", profile(archer()), shooter_at, Listed(turns=[Shoot("T")])),
            ("T", "blue", sample(), target_at, t),
        ],
        {"A": [1, 1], "T": [1]},
    )
    (blocks,) = of(t, BlocksRequest)
    return blocks, t


# --- defense_timing --------------------------------------------------------------------


def test_closing_in_keeps_ranged_defense_when_judged_at_declaration() -> None:
    rules = ranged(defense_timing="declaration")
    blocks, _ = shot_at(rules, (0, 2), (3, 2), ((2, 2), (1, 2)))
    assert blocks.defense == 2 + 1  # Ranged Defense, +1 for moving: not Melee Defense
    blocks, _ = shot_at(V10, (0, 2), (3, 2), ((2, 2), (1, 2)))
    assert blocks.defense == 3  # 0.10.0: Melee Defense once in reach


def test_backing_out_of_reach_keeps_melee_defense_when_judged_at_declaration() -> None:
    rules = ranged(defense_timing="declaration")
    blocks, _ = shot_at(rules, (2, 2), (3, 2), ((4, 2), (5, 2)))
    assert blocks.defense == 3
    blocks, _ = shot_at(V10, (2, 2), (3, 2), ((4, 2), (5, 2)))
    assert blocks.defense == 2 + 1


def test_the_dive_request_says_the_declaration_defense() -> None:
    _, t = shot_at(ranged(defense_timing="declaration"), (0, 2), (3, 2), None)
    (dive,) = of(t, DiveRequest)
    assert dive.defense_after[(1, 2)] == 2 + 1
    _, t = shot_at(V10, (0, 2), (3, 2), None)
    (dive,) = of(t, DiveRequest)
    assert dive.defense_after[(1, 2)] == 3


def test_cover_only_package() -> None:
    """v0.10.0-cover-only: range and defense at declaration; cover and +1 still count."""
    r = preset("v0.10.0-cover-only").ranged
    assert not r.measures_after_reaction() and not r.defense_after_reaction()
    assert r.reaction_defense() == 1 and r.cover_bonus(2) == 2


# --- reaction_purchases and swap_single_purchase -----------------------------------------


def test_reaction_purchase_cap() -> None:
    """Capped at one purchase, the sample fighter (2 squares a purchase) can react 2 squares."""
    _, t = shot_at(ranged(reaction_purchases=1), (0, 2), (8, 2), None)
    (dive,) = of(t, DiveRequest)
    assert dive.moves.max_squares == 2
    assert max(dive.moves.destinations.values()) == 2
    _, t = shot_at(V10, (0, 2), (8, 2), None)
    (dive,) = of(t, DiveRequest)
    assert dive.moves.max_squares > 2


def test_swap_needs_a_single_purchase() -> None:
    rules = ranged(swap_single_purchase=True)
    one, _ = shot_at(rules, (0, 2), (3, 2), ((2, 2), (1, 2)))  # 2 squares: one purchase
    assert one.defense == 3
    two, t = shot_at(rules, (0, 2), (5, 2), ((4, 2), (3, 2), (2, 2), (1, 2)))  # two purchases
    assert two.defense == 2 + 1
    (dive,) = of(t, DiveRequest)
    assert dive.defense_after[(1, 2)] == 2 + 1 and dive.defense_after[(3, 2)] == 2 + 1
    plain, _ = shot_at(V10, (0, 2), (5, 2), ((4, 2), (3, 2), (2, 2), (1, 2)))
    assert plain.defense == 3


# --- the crit rules ------------------------------------------------------------------


def test_crit_c_prime() -> None:
    """C': aim dice crit only on a 6, whatever the Finesse; a shot counts one critical die."""
    rules = preset("v0.10.0-crit-c-prime")
    w = bow(archer(FIN=3))  # d8 crits on 6-8
    a = roll_shot(w, 2, 3, "band 1", rules, ScriptedDice([8, 5, 6, 6]))
    assert sum(s.crit_dice for s in a.steps) == 3 and a.crit_dice == 1
    b = roll_shot(w, 1, 3, "band 1", rules, ScriptedDice([1, 5, 4]))
    assert b.crit_dice == 0  # a 5 on an aim die isn't critical, even at Finesse 3


def test_crit_c() -> None:
    """C: aim dice crit on the weapon's widened range; one critical die a shot."""
    rules = preset("v0.10.0-crit-c")
    w = bow(archer(FIN=3))
    a = roll_shot(w, 1, 3, "band 1", rules, ScriptedDice([1, 5, 4]))
    assert a.crit_dice == 1  # the 5 crits at Finesse 3 (4-6)
    b = roll_shot(w, 1, 3, "band 1", rules, ScriptedDice([8, 6, 6]))
    assert b.crit_dice == 1


def test_per_shot_cap_leaves_melee_alone() -> None:
    """A greataxe's 2d6 can still crit twice under C."""
    rules = preset("v0.10.0-crit-c")
    axe = replace(
        load_build("l1_archer"),
        name="axe",
        loadouts=(("axe", Loadout(armor="light", weapon="greataxe", grip="two")),),
        budget="ignore",
    )
    w = derive(axe, rules, TABLE).main.weapon
    assert w is not None
    a = roll_attack(w, 1, rules.crit, ScriptedDice([6, 6]))
    assert a.crit_dice == 2


def test_crit_inside_the_limit() -> None:
    """ranged.crit_in_limit: the critical bonus counts toward the aim limit."""
    inside = ranged(crit_in_limit=True)
    assert resolve(20, 1, 2, 0, Blocks(1, 0), inside, limit=8).injury == 8
    assert resolve(20, 1, 2, 0, Blocks(1, 0), V10, limit=8).injury == 9
    assert resolve(9, 1, 2, 0, Blocks(1, 0), inside, limit=8).injury == 7 + 1
    assert resolve(20, 1, 2, 0, Blocks(1, 0), inside).injury == 19  # melee: no limit
