"""Tactical agents at range: exact aim choice, diving, the archer's blade, kiting and
approaching through cover (agents/tactical.py)."""

from fractions import Fraction

from stamina_engine.agents.decisions import DiveRequest, Move, Pass
from stamina_engine.agents.grid_view import shot_value
from stamina_engine.agents.listed import Listed
from stamina_engine.agents.scripted import make_agent
from stamina_engine.agents.tactical import TacticalAgent
from stamina_engine.core.rng import Streams
from stamina_engine.engine.battle import Battle, BattleResult, Entrant
from stamina_engine.engine.events import Dived, Drew, Moved, ShotDeclared
from stamina_engine.engine.procedures.movement import move_options
from stamina_engine.engine.procedures.ranged import cover_from
from stamina_engine.engine.timeline import place_everyone
from stamina_engine.grid.battlefield import Battlefield, Cell, parse_map
from stamina_engine.model.build import load_build
from stamina_engine.model.derive import CombatProfile, derive
from stamina_engine.rules.ruleset import preset

RULES = preset("v0.9")


def archer() -> CombatProfile:
    return derive(load_build("l1_archer"), RULES)


def sample() -> CombatProfile:
    return derive(load_build("l1_sample"), RULES)


class Initiative:
    def __init__(self, first: str, ids: list[str], seed: int = 1) -> None:
        self.streams = Streams(seed)
        self.order = [12, 12] if ids[0] == first else [1, 1]
        self.faces = [f for cid in ids for f in ((12, 12) if cid == first else (1, 1))]

    def dice(self, name: str):  # type: ignore[no-untyped-def]
        from stamina_engine.core.dice import ScriptedDice

        if name == "initiative":
            return ScriptedDice(self.faces)
        return self.streams.dice(name)


def battle(
    field: Battlefield,
    roster: list[tuple[str, str, CombatProfile, Cell, object]],
    first: str,
    rounds: int = 1,
) -> BattleResult:
    entrants = [Entrant(cid, team, p, a, "", pos) for cid, team, p, pos, a in roster]  # type: ignore[arg-type]
    dice = Initiative(first, [r[0] for r in roster])
    return Battle(RULES, entrants, dice, seed=1, round_cap=rounds, check=True, field=field).run()


OPEN = parse_map("\n".join(["." * 24] * 5))


def test_aim_choice_is_the_exact_best_when_nothing_can_reach_it() -> None:
    a = make_agent("tactical", RULES)
    t = Listed()
    result = battle(
        OPEN, [("A", "red", archer(), (0, 2), a), ("T", "blue", sample(), (14, 2), t)], "A"
    )
    (shot,) = [e for e in result.log if isinstance(e, ShotDeclared)]
    assert shot.band == "medium"
    gear = archer().loadout("bow")
    assert gear.weapon is not None
    target = sample()
    best, best_k = None, None
    for k in range(0, 4):
        cost = 5 + sum(1 + i for i in range(k))
        if cost > archer().stamina_max:
            break
        value = Fraction(-cost)
        if k >= 1:
            inj, drained, down = shot_value(
                gear.weapon,
                k,
                gear.attributes.FIN,
                "medium",
                target.main.ranged_defense,
                target.main.armor,
                target.stamina_max,
                target.hp_max,
                RULES,
                Fraction(3),
            )
            value += 3 * inj + drained + 30 * down
        if best is None or value > best:
            best, best_k = value, k
    assert shot.aims == best_k


def test_aiming_holds_back_when_the_enemy_can_reach_it() -> None:
    def aims(distance: int) -> int:
        a = make_agent("tactical", RULES)
        r = battle(
            OPEN,
            [("A", "red", archer(), (0, 2), a), ("T", "blue", sample(), (distance, 2), Listed())],
            "A",
        )
        return next(e.aims for e in r.log if isinstance(e, ShotDeclared))

    assert aims(5) <= aims(8)  # 5 apart, the fighter's 6 free squares reach it


def test_dive_only_when_it_pays() -> None:
    """Behind the wall a big roll is blocked at +5; a small one isn't worth the move."""
    walled = parse_map("\n".join([".....#..", ".....#..", ".....#..", "........", "........"]))
    agent = make_agent("tactical", RULES)
    assert isinstance(agent, TacticalAgent)
    b = Battle(
        RULES,
        [
            Entrant("S", "red", archer(), Listed(), "", (0, 1)),
            Entrant("T", "blue", sample(), agent, "", (6, 4)),
        ],
        Streams(1),
        seed=1,
        field=walled,
    )
    place_everyone(b)
    b.ops.set_order(("S", "T"))
    t = b.state.get("T")
    moves = move_options(b, t, on_turn=False)
    assert moves is not None
    shooter = b.state.get("S")
    after = {
        d: RULES.ranged.dive_cover(int(cover_from(b, shooter, t, d))) for d in moves.destinations
    }
    for damage, expect_dive in ((30, True), (2, False)):
        answer = agent.dive(DiveRequest("T", b.observe("T"), (), "S", damage, 0, 0, moves, after))
        assert isinstance(answer, Move) is expect_dive, damage
        if isinstance(answer, Move):
            assert after[answer.path[-1]] >= 1


def test_archer_readies_its_blade_and_draws_the_bow_again() -> None:
    a = make_agent("tactical", RULES)
    f = make_agent("never", RULES)  # blocks well, never moves or attacks
    result = battle(
        OPEN,
        [("A", "red", archer(), (0, 2), a), ("F", "blue", sample(), (7, 2), f)],
        "A",
        rounds=2,
    )
    drew = [e.loadout for e in result.log if isinstance(e, Drew)]
    assert drew[:2] == ["blade", "bow"]  # the window after its shot, then its next turn


def test_archer_steps_out_of_reach_before_shooting() -> None:
    a = make_agent("tactical", RULES)
    result = battle(
        OPEN, [("A", "red", archer(), (3, 2), a), ("F", "blue", sample(), (4, 2), Listed())], "A"
    )
    first_shot = next(i for i, e in enumerate(result.log) if isinstance(e, ShotDeclared))
    moved = [e for e in result.log[:first_shot] if isinstance(e, Moved) and e.who == "A"]
    assert moved and max(abs(moved[-1].to[0] - 4), abs(moved[-1].to[1] - 2)) > 1


def test_approach_prefers_cover_from_a_shooter() -> None:
    """Two squares equally close to the archer: one behind a pillar."""
    field = parse_map(
        "\n".join(["............", "............", "..o.........", "............", "............"])
    )
    f = make_agent({"kind": "tactical", "commit": "chipkill"}, RULES)
    result = battle(
        field, [("F", "red", sample(), (11, 2), f), ("A", "blue", archer(), (0, 2), Listed())], "F"
    )
    end = [e for e in result.log if isinstance(e, Moved) and e.who == "F"][-1].to
    from stamina_engine.grid.los import Cover, cover

    assert cover(field, RULES.grid, (0, 2), end) >= Cover.HALF or end[0] <= 1
    assert not any(isinstance(e, Dived) for e in result.log)
    assert isinstance(Pass(), Pass)
