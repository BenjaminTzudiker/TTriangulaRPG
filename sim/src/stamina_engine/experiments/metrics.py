"""Per-fight, per-attack and per-decision rows from a battle, and summaries over trials."""

from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from stamina_engine.engine.battle import BattleResult
from stamina_engine.engine.events import (
    AbilityUsed,
    AttackDeclared,
    AttackResolved,
    AttackRolled,
    BlocksDeclared,
    Dived,
    Drew,
    Injured,
    Moved,
    ObjectiveResolved,
    OpportunityAvoided,
    OpportunityDeclared,
    OpportunityProvoked,
    PointBlankProvoked,
    RangePenalized,
    Reacted,
    Recovered,
    RoundStarted,
    ShotDeclared,
    ShotMissed,
    Spent,
    TurnEnded,
    TurnStarted,
)
from stamina_engine.experiments.stats import Interval, mean_interval, median, wilson
from stamina_engine.model.state import Status

Row = dict[str, Any]

CATEGORIES = (
    "attack",
    "block",
    "opportunity",
    "avoid",
    "extra_move",
    "off_turn_move",
    "shot",
    "draw",
    "ability",  # every ability's stamina (cost and strain overage), summed
)


def fight_row(result: BattleResult, trial: int, seed: int) -> Row:
    state = result.state
    teams = sorted({c.team for c in state.combatants})
    first = state.get(result.order[0])
    winners = [c for c in state.combatants if c.team == result.winner]
    losers = [c for c in state.combatants if result.winner is not None and c.team != result.winner]
    spent: Counter[str] = Counter()
    moved: Counter[str] = Counter()
    uses: Counter[str] = Counter()
    wasted = 0
    provoked = avoided = taken = shots = aims = missed = dives = draws = 0
    contact: int | None = None
    round_ = 0
    for e in result.log:
        if isinstance(e, RoundStarted):
            round_ = e.round
        elif isinstance(e, Spent):
            spent[f"{state.get(e.who).team}:{e.category.split(':')[0]}"] += e.amount
        elif isinstance(e, AbilityUsed):
            uses[state.get(e.who).team] += 1
        elif isinstance(e, Recovered):
            wasted += e.wasted
        elif isinstance(e, Moved):
            moved[f"{state.get(e.who).team}:{'off' if e.how == 'off_turn' else 'on'}"] += 1
        elif isinstance(e, OpportunityProvoked):
            provoked += len(e.enemies)
        elif isinstance(e, OpportunityAvoided):
            avoided += len(e.enemies)
        elif isinstance(e, OpportunityDeclared | AttackDeclared | ShotDeclared):
            taken += isinstance(e, OpportunityDeclared)
            if isinstance(e, ShotDeclared):
                shots += 1
                aims += e.aims
            if contact is None:
                contact = round_
        elif isinstance(e, ShotMissed):
            missed += 1
        elif isinstance(e, Dived):
            dives += 1
        elif isinstance(e, Drew):
            draws += 1
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
        "contact_round": contact,  # the first round anyone attacked (None: nobody did)
        "oa_provoked": provoked,  # enemies provoked, counted per square left
        "oa_avoided": avoided,
        "oa_taken": taken,
        "shots": shots,
        "aims": aims,
        "shots_missed": missed,
        "dives": dives,
        "draws": draws,
        "log_sha256": result.log_sha256(),
    }
    row.update(ranged_measures(result))
    if result.objective is not None:  # scenarios with an objective only (O1)
        row["objective"] = result.objective  # done, failed, or open (the fight ended first)
        row["objective_round"] = next(
            (e.round for e in result.log if isinstance(e, ObjectiveResolved)), None
        )
        row["ending"] = result.reason.split(":")[0]
    for team in teams:
        row[f"win:{team}"] = result.winner == team
        for category in CATEGORIES:
            row[f"spent:{team}:{category}"] = spent[f"{team}:{category}"]
        row[f"abilities:{team}"] = uses[team]  # ability uses by the team's creatures
        row[f"strain:{team}"] = sum(c.strain for c in state.combatants if c.team == team)
        row[f"moved:{team}:on"] = moved[f"{team}:on"]
        row[f"moved:{team}:off"] = moved[f"{team}:off"]
        row[f"down:{team}"] = sum(1 for c in state.combatants if c.team == team and not c.active)
        row[f"dead:{team}"] = sum(
            1 for c in state.combatants if c.team == team and c.status is Status.DEAD
        )
        row[f"fled:{team}"] = sum(
            1 for c in state.combatants if c.team == team and c.status is Status.FLED
        )
        row[f"surrendered:{team}"] = sum(
            1 for c in state.combatants if c.team == team and c.status is Status.SURRENDERED
        )
    return row


REACTION_KINDS = ("close", "cover", "back", "shift")


def ranged_measures(result: BattleResult) -> Row:
    """The ranged measures (simulator requirements R9), per fight:
    - shot_crits: critical dice on shots; shots_band1, shots_band2, shots_band3plus: shots
      by the band they were blocked in (linear bands only);
    - shot_hp:{team}: HP the team's shots took (with shot_spent from spent:{team}:shot);
    - reactions:{kind} and reaction_cost: reactions to shots by kind (close, cover, back,
      shift; a shot with none was stayed against) and the stamina they cost;
    - pb_provoked, pb_taken: opportunity attacks a point-blank shot provoked and the ones
      made;
    - melee_round: the first round anyone made a melee attack (an OA included);
    - fell:{id}: the round each creature went down (None: it didn't), team:{id} its team;
      down_by_r2:{team}: any of the team down by the end of round 2;
    - t1_shot_spend, t1_shot_reserve: for creatures that shot in their first turn, the
      stamina that turn cost and what was left at its end (means; None if none did)."""
    state = result.state
    team_of = {c.id: c.team for c in state.combatants}
    reactions: Counter[str] = Counter()
    bands: Counter[str] = Counter()
    shot_hp: Counter[str] = Counter()
    crits = cost = pb_provoked = pb_taken = 0
    pb_open = False
    rolling: str | None = None
    open_shots: dict[str, str] = {}
    melee_round: int | None = None
    fell: dict[str, int | None] = {c.id: None for c in state.combatants}
    first_turn: dict[str, list[int]] = {}  # who -> [spent, stamina after, shot?]
    in_turn: str | None = None
    round_ = 0
    for e in result.log:
        if isinstance(e, RoundStarted):
            round_ = e.round
        elif isinstance(e, TurnStarted):
            in_turn = e.who if e.who not in first_turn else None
            if in_turn is not None:
                first_turn[e.who] = [0, -1, 0]
        elif isinstance(e, TurnEnded):
            in_turn = None
            pb_open = False
        elif isinstance(e, Spent) and in_turn is not None and e.who == in_turn:
            first_turn[in_turn][0] += e.amount
            first_turn[in_turn][1] = e.stamina_after
        elif isinstance(e, ShotDeclared):
            rolling = e.shooter
            open_shots[e.shooter] = e.target
            pb_open = False
            if in_turn is not None and e.shooter == in_turn:
                first_turn[in_turn][2] = 1
        elif isinstance(e, AttackRolled) and rolling == e.attacker:
            crits += e.crit_dice
            rolling = None
        elif isinstance(e, AttackResolved) and open_shots.get(e.attacker) == e.target:
            shot_hp[team_of[e.attacker]] += e.injury
            del open_shots[e.attacker]
        elif isinstance(e, RangePenalized):
            n = e.band.removeprefix("band ")
            bands["1" if n == "1" else "2" if n == "2" else "3plus"] += 1
        elif isinstance(e, Reacted):
            reactions[e.kind] += 1
            cost += e.cost
        elif isinstance(e, PointBlankProvoked):
            pb_provoked += len(e.enemies)
            pb_open = True
        elif isinstance(e, OpportunityDeclared):
            pb_taken += pb_open
            if melee_round is None:
                melee_round = round_
        elif isinstance(e, AttackDeclared):
            pb_open = False
            if melee_round is None:
                melee_round = round_
        elif isinstance(e, Moved):
            pb_open = False
        elif isinstance(e, Injured) and e.status_after != "active" and fell.get(e.who) is None:
            fell[e.who] = round_
    shooters = [v for v in first_turn.values() if v[2]]
    row: Row = {
        "shot_crits": crits,
        **{f"shots_band{k}": bands[k] for k in ("1", "2", "3plus")},
        **{f"reactions:{k}": reactions[k] for k in REACTION_KINDS},
        "reaction_cost": cost,
        "pb_provoked": pb_provoked,
        "pb_taken": pb_taken,
        "melee_round": melee_round,
        "t1_shot_spend": sum(v[0] for v in shooters) / len(shooters) if shooters else None,
        "t1_shot_reserve": sum(v[1] for v in shooters) / len(shooters) if shooters else None,
    }
    for team in sorted(set(team_of.values())):
        row[f"shot_hp:{team}"] = shot_hp[team]
        row[f"down_by_r2:{team}"] = any(
            r is not None and r <= 2 for cid, r in fell.items() if team_of[cid] == team
        )
    for cid, r in fell.items():
        row[f"fell:{cid}"] = r
        row[f"team:{cid}"] = team_of[cid]
    return row


def attack_rows(result: BattleResult, trial: int) -> list[Row]:
    rows: list[Row] = []
    current: Row = {}
    round_ = 0
    for e in result.log:
        if isinstance(e, RoundStarted):
            round_ = e.round
        elif isinstance(e, AttackDeclared | OpportunityDeclared | ShotDeclared):
            if isinstance(e, ShotDeclared):
                kind, attacker, steps = "shot", e.shooter, e.aims
            else:
                kind = "melee" if isinstance(e, AttackDeclared) else "opportunity"
                attacker, steps = e.attacker, e.steps
            current = {
                "trial": trial,
                "round": round_,
                "kind": kind,  # for a shot, steps counts its aim steps
                "attacker": attacker,
                "target": e.target,
                "steps": steps,
                "cost": 0,
                "block_cost": 0,
                "perfect": 0,
                "grazing": 0,
            }
        elif isinstance(e, Spent) and e.category in ("attack", "opportunity", "shot"):
            current["cost"] = e.amount
        elif isinstance(e, AttackRolled):
            current.update(total=e.total, crit_dice=e.crit_dice, dice=len(e.faces))
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
            "seconds": d.seconds,
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
    contact_round: Interval | None = None  # among fights with any attack
    oa_taken: Interval | None = None  # per fight
    off_turn_squares: Interval | None = None  # per fight, all teams
    objective: Interval | None = None  # scenarios with an objective: share of fights it's done
    endings: dict[str, Interval] | None = None  # how fights ended: objective, side_out...

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
        if self.contact_round is not None:
            out.append(f"Rounds to contact: {self.contact_round}")
        if self.oa_taken is not None:
            out.append(f"Opportunity attacks per fight: {self.oa_taken}")
        if self.off_turn_squares is not None:
            out.append(f"Squares moved off-turn per fight: {self.off_turn_squares}")
        if self.objective is not None:
            out.append(f"Objective done: {self.objective.pct()}")
        if self.endings:
            out += [f"Ended by {how}: {iv.pct()}" for how, iv in self.endings.items()]
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
        contact_round=_mean_or_none(
            [float(f["contact_round"]) for f in fights if f.get("contact_round") is not None]
        ),
        oa_taken=_mean_or_none([float(f.get("oa_taken", 0)) for f in fights]),
        objective=_objective(fights),
        endings=_endings(fights),
        off_turn_squares=_mean_or_none(
            [
                float(sum(v for k, v in f.items() if k.startswith("moved:") and k.endswith(":off")))
                for f in fights
            ]
        ),
    )


ENDINGS = ("objective", "objective_failed", "side_out", "round_cap")


def _objective(fights: Sequence[Row]) -> Interval | None:
    if not fights or "objective" not in fights[0]:
        return None
    return wilson(sum(1 for f in fights if f["objective"] == "done"), len(fights))


def _endings(fights: Sequence[Row]) -> dict[str, Interval] | None:
    if not fights or "ending" not in fights[0]:
        return None
    n = len(fights)
    return {how: wilson(sum(1 for f in fights if f["ending"] == how), n) for how in ENDINGS}


def _mean_or_none(values: list[float]) -> Interval | None:
    return mean_interval(values) if values else None
