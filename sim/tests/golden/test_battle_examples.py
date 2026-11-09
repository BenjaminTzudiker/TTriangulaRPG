"""Packet examples run as battles: Melee Attack (with attacking again), recovery at the end
of your turn, System Shock across turns, and initiative tiebreaks."""

from collections.abc import Callable
from dataclasses import dataclass, field

from stamina_engine.agents.decisions import (
    Attack,
    BlocksRequest,
    Commitment,
    EndTurn,
    TurnAnswer,
    TurnCommand,
)
from stamina_engine.core.dice import ScriptedDice
from stamina_engine.engine.battle import Battle, Entrant
from stamina_engine.engine.events import (
    AttackRolled,
    BlocksDeclared,
    DyingRolled,
    Event,
    InitiativeRolled,
    Recovered,
    Spent,
    TurnStarted,
)
from stamina_engine.model.build import Attributes, Build, Loadout, load_build
from stamina_engine.model.derive import CombatProfile, derive
from stamina_engine.rules.exchange import Blocks
from stamina_engine.rules.ruleset import RuleSet, review_sim, v0_9

RULES = v0_9()


class Dice:
    """A scripted face list per purpose."""

    def __init__(self, **faces: list[int]) -> None:
        self.sources = {k.replace("_", ":"): ScriptedDice(v) for k, v in faces.items()}

    def dice(self, name: str) -> ScriptedDice:
        return self.sources[name]


@dataclass
class Script:
    """Answers from lists: the attacks to make on each of its turns, then blocks in order."""

    turns: list[list[tuple[str, int]]] = field(default_factory=list)
    block_answers: list[Blocks] = field(default_factory=list)
    _round: int = -1
    _now: list[tuple[str, int]] = field(default_factory=list)
    _steps: int = 0

    def turn_command(self, request: TurnCommand) -> TurnAnswer:
        if request.observation.round != self._round:
            self._round = request.observation.round
            self._now = self.turns.pop(0) if self.turns else []
        if not self._now:
            return EndTurn()
        target, self._steps = self._now.pop(0)
        return Attack(target)

    def commitment(self, request: Commitment) -> int:
        return self._steps

    def blocks(self, request: BlocksRequest) -> Blocks:
        return self.block_answers.pop(0) if self.block_answers else Blocks()

    def ability(self, request: object) -> object:
        from stamina_engine.agents.decisions import Pass

        return Pass()


def orc() -> CombatProfile:
    """Melee Defense 4 (base, proficient weapon, shield) and armor 1."""
    b = Build(
        "orc",
        1,
        Attributes(STR=2, AGI=1, FIN=1),
        (("m", Loadout(armor="light", weapon="longsword", off_hand="shield")),),
        ("fighter",),
    )
    p = derive(b, RULES)
    assert (p.main.melee_defense, p.main.armor) == (4, 1)
    return p


def of(
    log: list[Event] | tuple[Event, ...], kind: type, pred: Callable[[Event], bool] = lambda e: True
) -> list:
    return [e for e in log if isinstance(e, kind) and pred(e)]


def test_melee_attack_example_as_a_battle() -> None:
    fighter = Script(turns=[[("orc", 2), ("orc", 2)]])
    orc_agent = Script(block_answers=[Blocks(2, 2), Blocks(1, 0)])
    battle = Battle(
        RULES,
        [
            Entrant("fighter", "pc", derive(load_build("l1_sample"), RULES), fighter),
            Entrant("orc", "npc", orc(), orc_agent),
        ],
        Dice(initiative=[12, 12, 1, 1], attack_fighter=[6, 3, 1, 1]),
        seed=0,
        round_cap=1,
        check=True,
    )
    result = battle.run()
    log = result.log
    spent = of(log, Spent)
    assert [(e.who, e.parts) for e in spent] == [
        ("fighter", (2, 3)),  # two steps: 5 stamina
        ("orc", (1, 2, 1, 1)),  # 2 perfect + 2 grazing: 5
        ("fighter", (4, 5)),  # attacking again: the surcharge carries on
        ("orc", (1,)),  # the orc's perfect blocks start at 1 again
    ]
    rolls = of(log, AttackRolled)
    assert (rolls[0].total, rolls[0].crit_dice) == (15, 0)
    # 2p+2g against 15 leaves 1 HP after armor 1; then 8 vs 1 perfect leaves 4 - 1 = 3.
    assert result.state.get("orc").damage_taken == [1, 3]
    assert [b.prior_perfect for b in of(log, BlocksDeclared)] == [0, 0]
    # Recovery at the end of your own turn, capped at maximum: the orc, at 4 HP, has a
    # maximum of 6 + 4 = 10, so of its 4 recovery from 8 stamina, 2 are wasted.
    rec = {e.who: (e.amount, e.wasted, e.stamina_after) for e in of(log, Recovered)}
    assert rec["fighter"] == (4, 0, 4)
    assert rec["orc"] == (2, 2, 10)
    assert result.reason == "round_cap" and result.winner is None


def test_system_shock_across_turns() -> None:
    """A downed creature makes its dying roll at the start of each turn, then does nothing:
    no actions, no recovery (Assumptions register)."""
    p = derive(load_build("l1_sample"), RULES)
    big = Script(turns=[[("x", 2)]])
    battle = Battle(
        RULES,
        [Entrant("x", "a", p, Script()), Entrant("y", "a", p, Script()), Entrant("z", "b", p, big)],
        Dice(initiative=[12, 12, 6, 6, 1, 1], attack_z=[5, 5], dying=[1, 1]),
        seed=0,
        round_cap=2,
        check=True,
    )
    result = battle.run()
    x = result.state.get("x")
    # Round 1: z hits unblocking x for 16, less armor 2: 8 - 14 = -6 HP, 6 Shock.
    rolls = of(result.log, DyingRolled)
    assert [(e.who, e.total, e.shock_after) for e in rolls] == [("x", 1 + 1 + 2, 7)]
    assert (x.hp, x.dying.shock, x.active) == (-6, 7, False)  # 2d12 + STR 2 < 10 + 6
    assert not of(result.log, Recovered, lambda e: e.who == "x" and e.amount > 0)
    turns = of(result.log, TurnStarted, lambda e: e.who == "x")
    assert len(turns) == 2  # x still gets turns, for the dying roll


def test_dying_roll_adds_will_from_0_9_1() -> None:
    """Packet: Dying and Death (0.9.1): the dying roll is 2d12 + Will, not + Strength."""
    from dataclasses import replace

    from stamina_engine.rules.ruleset import v0_9_2

    rules = v0_9_2()
    sample = load_build("l1_sample")
    willful = replace(sample, attributes=replace(sample.attributes, WIL=3), budget="ignore")
    p, x = derive(sample, rules), derive(willful, rules)
    big = Script(turns=[[("x", 2)]])
    battle = Battle(
        rules,
        [Entrant("x", "a", x, Script()), Entrant("y", "a", p, Script()), Entrant("z", "b", p, big)],
        Dice(initiative=[12, 12, 6, 6, 1, 1], attack_z=[5, 5], dying=[1, 1]),
        seed=0,
        round_cap=2,
        check=True,
    )
    result = battle.run()
    # z hits x for 16, less armor 2: HP 10 - 14 = -4, 4 Shock. 1 + 1 + WIL 3 < 10 + 4.
    rolls = of(result.log, DyingRolled)
    assert [(e.who, e.total, e.shock_after) for e in rolls] == [("x", 1 + 1 + 3, 5)]


def initiative(rules: RuleSet, faces: list[int], agi: tuple[int, int] = (0, 0)) -> InitiativeRolled:
    ps = [
        derive(Build(f"b{i}", 99, Attributes(AGI=a), (("m", Loadout()),)), rules)
        for i, a in enumerate(agi)
    ]
    battle = Battle(
        rules,
        [Entrant("a", "x", ps[0], Script()), Entrant("b", "y", ps[1], Script())],
        Dice(initiative=faces),
        seed=0,
        round_cap=0,
    )
    result = battle.run()
    (event,) = of(result.log, InitiativeRolled)
    return event


def test_initiative_tiebreaks() -> None:
    # Tie at 10 (5+5 each). list_order: a first. reroll: b's reroll is higher.
    assert initiative(review_sim(), [5, 5, 5, 5]).order == ("a", "b")
    rerolled = initiative(v0_9(), [5, 5, 5, 5, 1, 1, 6, 6])
    assert rerolled.order == ("b", "a")
    assert rerolled.rolls == (("a", 10), ("b", 10), ("a", 2), ("b", 12))
    # Higher agility: AGI 2 vs 0 at equal totals (odd AGI adds nothing at 0 or 2).
    agi = v0_9().override({"turn_order": {"tiebreak": "higher_agility"}})
    assert initiative(agi, [5, 5, 5, 5], agi=(0, 2)).order == ("b", "a")
