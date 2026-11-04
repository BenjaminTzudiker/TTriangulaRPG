"""Per-fight, per-attack and per-decision rows from a battle, and summaries over trials."""

from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from stamina_engine.engine.battle import BattleResult
from stamina_engine.engine.events import (
    AttackDeclared,
    AttackResolved,
    AttackRolled,
    BlocksDeclared,
    Recovered,
    RoundStarted,
    Spent,
)
from stamina_engine.experiments.stats import Interval, mean_interval, median, wilson
from stamina_engine.model.state import Status

Row = dict[str, Any]


def fight_row(result: BattleResult, trial: int, seed: int) -> Row:
    state = result.state
    teams = sorted({c.team for c in state.combatants})
    first = state.get(result.order[0])
    winners = [c for c in state.combatants if c.team == result.winner]
    losers = [c for c in state.combatants if result.winner is not None and c.team != result.winner]
    spent: Counter[str] = Counter()
    wasted = 0
    for e in result.log:
        if isinstance(e, Spent):
            spent[f"{state.get(e.who).team}:{e.category}"] += e.amount
        elif isinstance(e, Recovered):
            wasted += e.wasted
    row: Row = {
        "trial": trial,
        "seed": str(seed),  # 64-bit unsigned: text, so every table format can hold it
        "winner": result.winner,
        "reason": result.reason,
        "rounds": result.rounds,
        "first": first.id,
        "first_team": first.team,
        "first_won": None if result.winner is None else first.team == result.winner,
        "winner_untouched": None
        if result.winner is None
        else all(not c.damage_taken for c in winners),
        "loser_hp": None if not losers else sum(c.hp for c in losers) / len(losers),
        "dead": sum(1 for c in state.combatants if c.status is Status.DEAD),
        "down_alive": sum(1 for c in state.combatants if c.status is Status.INCAPACITATED),
        "stabilized": sum(
            1
            for c in state.combatants
            if c.status is Status.INCAPACITATED and c.hp < 0 and not c.dying.in_shock
        ),
        "attacks": sum(1 for e in result.log if isinstance(e, AttackResolved)),
        "decisions": len(result.decisions),
        "acted_decisions": sum(1 for d in result.decisions if d.acted),
        "recovery_wasted": wasted,
        "log_sha256": result.log_sha256(),
    }
    for team in teams:
        row[f"win:{team}"] = result.winner == team
        for category in ("attack", "block"):
            row[f"spent:{team}:{category}"] = spent[f"{team}:{category}"]
    return row


def attack_rows(result: BattleResult, trial: int) -> list[Row]:
    rows: list[Row] = []
    current: Row = {}
    round_ = 0
    for e in result.log:
        if isinstance(e, RoundStarted):
            round_ = e.round
        elif isinstance(e, AttackDeclared):
            current = {
                "trial": trial,
                "round": round_,
                "attacker": e.attacker,
                "target": e.target,
                "steps": e.steps,
                "cost": 0,
                "block_cost": 0,
                "perfect": 0,
                "grazing": 0,
            }
        elif isinstance(e, Spent) and e.category == "attack":
            current["cost"] = e.amount
        elif isinstance(e, AttackRolled):
            current.update(total=e.total, crit_dice=e.crit_dice)
        elif isinstance(e, BlocksDeclared):
            current.update(perfect=e.perfect, grazing=e.grazing)
        elif isinstance(e, Spent) and e.category == "block":
            current["block_cost"] = e.amount
        elif isinstance(e, AttackResolved):
            current["injury"] = e.injury
            rows.append(current)
    return rows


def decision_rows(result: BattleResult, trial: int) -> list[Row]:
    return [
        {
            "trial": trial,
            "round": d.round,
            "who": d.who,
            "kind": d.kind,
            "option_count": d.option_count,
            "nondominated": d.nondominated,
            "answer": d.answer,
            "acted": d.acted,
            "context": " > ".join(d.context),
        }
        for d in result.decisions
    ]


@dataclass(frozen=True)
class Summary:
    trials: int
    wins: dict[str, Interval]
    draws: Interval
    rounds: Interval
    rounds_median: float
    first_mover: Interval  # among decisive fights
    winner_untouched: Interval  # among decisive fights
    loser_hp: Interval
    dead: Interval  # deaths per fight
    decisions_per_round: float

    def lines(self) -> list[str]:
        out = [f"Trials: {self.trials}"]
        out += [f"{team} wins: {iv.pct()}" for team, iv in self.wins.items()]
        out += [
            f"Draws: {self.draws.pct()}",
            f"Rounds: mean {self.rounds}, median {self.rounds_median:g}",
            f"First mover wins (decisive fights): {self.first_mover.pct()}",
            f"Winner untouched (decisive fights): {self.winner_untouched.pct()}",
            f"Loser ends at (HP): {self.loser_hp}",
            f"Deaths per fight: {self.dead}",
            f"Decisions per round: {self.decisions_per_round:.2f}",
        ]
        return out


def summarize(fights: Sequence[Row]) -> Summary:
    n = len(fights)
    teams = sorted({k.split(":", 1)[1] for f in fights for k in f if k.startswith("win:")})
    decisive = [f for f in fights if f["winner"] is not None]
    rounds = [float(f["rounds"]) for f in fights]
    return Summary(
        trials=n,
        wins={t: wilson(sum(1 for f in fights if f.get(f"win:{t}")), n) for t in teams},
        draws=wilson(sum(1 for f in fights if f["winner"] is None), n),
        rounds=mean_interval(rounds),
        rounds_median=median(rounds),
        first_mover=wilson(sum(1 for f in decisive if f["first_won"]), len(decisive)),
        winner_untouched=wilson(sum(1 for f in decisive if f["winner_untouched"]), len(decisive)),
        loser_hp=mean_interval(
            [float(f["loser_hp"]) for f in decisive if f["loser_hp"] is not None]
        ),
        dead=mean_interval([float(f["dead"]) for f in fights]),
        decisions_per_round=sum(f["decisions"] for f in fights)
        / max(1, sum(f["rounds"] for f in fights)),
    )
