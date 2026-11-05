# ruff: noqa: E501
"""Movement + ranged exploration (design request 2026-11-04, second round): kiting, the distance
sweep, and what gives squares value once a shooter is on the field. Run from sim/ with
PYTHONPATH=src:

    python3 -u experiments_ranged_movement.py <runner> [trials]

Runners: K1 (AGI 5 kiter vs two slow brutes, by movement rule and kiter policy), K1e (a
gap-holding kiter, field and room), K2 (the same against brutes in light armor, against
Agility-2 brutes, an Agility-1 archer as the kiter, one brute), K2e (against two shielded
sample fighters), K3 (the room: the field runs out), D1 and D1x (duel first-mover edge by
starting distance and movement rule), S1 (an archer screened by a fighter), R1 (a shooter
against a target that only blocks).

Results go to reports/movement_ranged_results/*.jsonl, one JSON row per cell with the RuleSet
digest, the provenance stamp and per-team stamina spend by category."""

import json
import sys
import time
from pathlib import Path

from stamina_engine.engine.events import AttackResolved, ShotDeclared
from stamina_engine.experiments.metrics import summarize
from stamina_engine.experiments.runner import run_scenario, run_trial
from stamina_engine.experiments.scenario import scenario_from_toml
from stamina_engine.experiments.stats import mean_interval, wilson
from stamina_engine.provenance import collect
from stamina_engine.rules.ruleset import preset

HERE = Path(__file__).resolve().parent
OUT = HERE / "reports" / "movement_ranged_results"
OUT.mkdir(parents=True, exist_ok=True)
BUILDS = OUT / "builds"
MAPS = OUT / "maps"
BASE_DIR = HERE / "src" / "stamina_engine" / "data" / "scenarios"

# ---------------------------------------------------------------------------- rulesets
MOVE_RULES = {
    "v0.9": {},
    "capped at Movement": {"movement": {"extra_cap": "free_movement"}},
    "one square, escalating": {"movement": {"extra_squares": "one", "extra_mode": "escalating"}},
    "none": {"movement": {"extra_mode": "none"}},
}

# ---------------------------------------------------------------------------- agents
KITER = '{{ kind = "tactical", commit = "chipkill", kite = "distance", kite_spend = {spend}, kite_gap = {gap}, shot_reserve = {reserve}, retreat_engaged = {re} }}'
BRUTE = '{{ kind = "tactical", commit = "chipkill", target = "nearest", chase_spend = {chase} }}'
TACT = '{ kind = "tactical", commit = "chipkill" }'


def kiter(spend: int = 2, reserve: int = 0, retreat_engaged: int = 2, gap: int = 0) -> str:
    return KITER.format(spend=spend, reserve=reserve, re=retreat_engaged, gap=gap)


def brute(chase: int = -1) -> str:
    return BRUTE.format(chase=chase)


def rules_for(overrides: dict, base: str = "v0.9"):
    r = preset(base)
    return r.override(overrides) if overrides else r


# ---------------------------------------------------------------------------- scenarios
def kite_scenario(
    kiter_agent: str,
    brute_agent: str,
    map_name: str = "kite_field",
    kiter_build: str = "l1_kiter",
    brute_build: str = "l1_brute",
    brutes: int = 2,
    round_cap: int = 20,
) -> str:
    kb = str(BUILDS / f"{kiter_build}.toml") if kiter_build.startswith("l1_kiter") else kiter_build
    bb = str(BUILDS / f"{brute_build}.toml")
    spawns = '["1", "2"]' if brutes == 2 else '["1"]'
    return f"""
[scenario]
name = "kite-{map_name}-{brutes}"
ruleset = "v0.9"
map = "{MAPS / map_name}.txt"
round_cap = {round_cap}
trials = 300
seed = 20261104
[[combatant]]
id = "K"
team = "kiter"
build = "{kb}"
spawn = "K"
agent = {kiter_agent}
[[combatant]]
id = "b"
team = "brutes"
build = "{bb}"
count = {brutes}
spawn = {spawns}
agent = {brute_agent}
"""


def duel_at(distance: int, agent_a: str = TACT, agent_b: str = TACT, build: str = "l1_sample") -> str:
    xa = 2
    return f"""
[scenario]
name = "duel-at-{distance}"
ruleset = "v0.9"
map = "{MAPS / 'open_32x10'}.txt"
round_cap = 30
trials = 400
seed = 20261104
[[combatant]]
id = "A"
team = "A"
build = "{build}"
spawn = [{xa}, 6]
agent = {agent_a}
[[combatant]]
id = "B"
team = "B"
build = "{build}"
spawn = [{xa + distance}, 6]
agent = {agent_b}
"""


def screen_scenario(archer_agent: str, screen_agent: str, enemy_agent: str, gap: int = 1) -> str:
    """An archer with a fighter in front of it, two enemy fighters eight squares off."""
    return f"""
[scenario]
name = "screen-{gap}"
ruleset = "v0.9"
map = "{MAPS / 'open_32x10'}.txt"
round_cap = 30
trials = 400
seed = 20261104
[[combatant]]
id = "A"
team = "party"
build = "l1_archer"
spawn = [4, 6]
agent = {archer_agent}
[[combatant]]
id = "F"
team = "party"
build = "l1_sample"
spawn = [{4 + gap}, 6]
agent = {screen_agent}
[[combatant]]
id = "e"
team = "enemies"
build = "l1_sample"
count = 2
spawn = [[13, 5], [13, 7]]
agent = {enemy_agent}
"""


def standing_exchange(shooter_build: str, target_build: str, distance: int, target_agent: str) -> str:
    sb = str(BUILDS / f"{shooter_build}.toml") if shooter_build.startswith("l1_kiter") else shooter_build
    tb = str(BUILDS / f"{target_build}.toml") if target_build.startswith("l1_brute") else target_build
    return f"""
[scenario]
name = "standing-{distance}"
ruleset = "v0.9"
map = "{MAPS / 'open_32x10'}.txt"
round_cap = 12
trials = 300
seed = 20261104
[[combatant]]
id = "S"
team = "shooter"
build = "{sb}"
spawn = [2, 6]
agent = {{ kind = "tactical", commit = "chipkill" }}
[[combatant]]
id = "T"
team = "target"
build = "{tb}"
spawn = [{2 + distance}, 6]
agent = {target_agent}
"""


# ---------------------------------------------------------------------------- running
def get(lines: list[str], key: str) -> str:
    for line in lines:
        if line.startswith(key):
            return line.split(":", 1)[1].strip()
    return ""


def pct(iv) -> str:
    return iv.pct()


def injury_pass(scenario, trials: int) -> dict[str, float]:
    """Injury dealt per fight by each team, and melee attacks landed on each team, from the
    event logs of the first `trials` trials."""
    dealt: dict[str, float] = {}
    melee_on: dict[str, float] = {}
    for t in range(trials):
        res = run_trial(scenario, t)
        state = res.state
        shots_pending: set[tuple[str, str]] = set()
        for e in res.log:
            if isinstance(e, ShotDeclared):
                shots_pending.add((e.shooter, e.target))
            elif isinstance(e, AttackResolved):
                team = state.get(e.attacker).team
                dealt[team] = dealt.get(team, 0.0) + e.injury
                if (e.attacker, e.target) in shots_pending:
                    shots_pending.discard((e.attacker, e.target))
                else:
                    tt = state.get(e.target).team
                    melee_on[tt] = melee_on.get(tt, 0.0) + 1
    out = {f"injury_by:{k}": round(v / trials, 2) for k, v in dealt.items()}
    out.update({f"melee_hits_on:{k}": round(v / trials, 2) for k, v in melee_on.items()})
    return out


def run_cell(label: str, scenario_text: str, overrides: dict, trials: int, group: str, events: int = 0) -> dict:
    s = scenario_from_toml(scenario_text, BASE_DIR)
    rules = rules_for(overrides)
    s = s.with_rules(rules)
    t = time.time()
    res = run_scenario(s, trials=trials)
    fights = res.fights
    lines = summarize(fights).lines()
    teams = sorted({k.split(":")[1] for k in fights[0] if k.startswith("win:")})
    n = len(fights)
    row: dict = {
        "group": group,
        "label": label,
        "scenario": s.name,
        "ruleset": rules.name,
        "digest": rules.digest()[:12],
        "trials": n,
        "wins": {team: pct(wilson(sum(1 for f in fights if f[f"win:{team}"]), n)) for team in teams},
        "draws": pct(wilson(sum(1 for f in fights if f["winner"] is None), n)),
        "rounds": get(lines, "Rounds"),
        "first_mover": get(lines, "First mover wins"),
        "winner_untouched": get(lines, "Winner untouched"),
        "deaths": get(lines, "Deaths"),
        "contact_round": f"{mean_interval([f['contact_round'] for f in fights if f['contact_round'] is not None]).estimate:.2f}" if any(f["contact_round"] is not None for f in fights) else "never",
        "no_contact": pct(wilson(sum(1 for f in fights if f["contact_round"] is None), n)),
        "shots_per_fight": f"{sum(f['shots'] for f in fights) / n:.2f}",
        "attacks_per_fight": f"{sum(f['attacks'] for f in fights) / n:.2f}",
        "decisions_per_round": f"{sum(f['decisions'] for f in fights) / max(1, sum(f['rounds'] for f in fights)):.2f}",
        "rounds_mean": f"{sum(f['rounds'] for f in fights) / n:.2f}",
    }
    for team in teams:
        for cat in ("attack", "block", "shot", "extra_move", "off_turn_move", "avoid", "opportunity"):
            row[f"spent:{team}:{cat}"] = round(sum(f[f"spent:{team}:{cat}"] for f in fights) / n, 2)
        row[f"moved:{team}:on"] = round(sum(f[f"moved:{team}:on"] for f in fights) / n, 2)
        row[f"moved:{team}:off"] = round(sum(f[f"moved:{team}:off"] for f in fights) / n, 2)
        row[f"down:{team}"] = round(sum(f[f"down:{team}"] for f in fights) / n, 3)
    if events:
        row.update(injury_pass(s, min(events, n)))
    row["seconds"] = round(time.time() - t, 1)
    row["stamp"] = collect(rules).text()
    with (OUT / f"{group}.jsonl").open("a") as fh:
        fh.write(json.dumps(row) + "\n")
    return row


def show(rows: list[dict], extra: tuple[str, ...]) -> None:
    for r in rows:
        wins = " ".join(f"{k} {v.split(' ')[0]}" for k, v in r["wins"].items())
        more = " | ".join(f"{k}: {r.get(k, '')}" for k in extra)
        print(f"  {r['label']:44s} [{r['digest']}] {wins:34s} | draws {r['draws'].split(' ')[0]} | rounds {r['rounds_mean']} | {more}")
    sys.stdout.flush()


KITE_COLS = ("contact_round", "no_contact", "shots_per_fight", "injury_by:kiter", "injury_by:brutes", "melee_hits_on:kiter", "spent:brutes:extra_move", "spent:kiter:extra_move", "spent:kiter:shot", "down:brutes")

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "K1"
    trials = int(sys.argv[2]) if len(sys.argv) > 2 else 300
    print(collect(preset("v0.9")).text())

    if which == "K1":
        print("\n## K1a. AGI 5 kiter (longbow, FIN 3) vs two AGI 0 brutes (greataxe, heavy armor), long field; kiter spends up to 2 on the run, brutes chase at any price")
        rows = [run_cell(k, kite_scenario(kiter(2), brute()), v, trials, "K1a", events=100) for k, v in MOVE_RULES.items()]
        show(rows, KITE_COLS)
        print("\n## K1b. v0.9 only: the kiter's run budget (0 = free movement only) and shot reserve")
        rows = []
        for spend, reserve in ((0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (2, 6), (3, 6)):
            rows.append(run_cell(f"kite_spend {spend}, shot_reserve {reserve}", kite_scenario(kiter(spend, reserve), brute()), {}, trials, "K1b", events=100))
        show(rows, KITE_COLS)
        print("\n## K1c. v0.9: patient brutes (chase_spend 0 / 2 / 4) against the kiter spending 2")
        rows = [run_cell(f"brutes chase_spend {c}", kite_scenario(kiter(2), brute(c)), {}, trials, "K1c", events=100) for c in (0, 2, 4)]
        show(rows, KITE_COLS)
        print("\n## K1d. Capped and none, with the kiter's run budget")
        rows = []
        for rule in ("capped at Movement", "none"):
            for spend in (0, 2, 4):
                rows.append(run_cell(f"{rule}, kite_spend {spend}", kite_scenario(kiter(spend), brute()), MOVE_RULES[rule], trials, "K1d", events=100))
        show(rows, KITE_COLS)

    if which == "K1e":
        # A kiter that holds the gap its rule needs (the brutes' one-turn reach plus one) instead of
        # running to the wall: v0.9 20 (5 free + 13 purchases + reach), capped 12 (5 + 5 + 1 + 1),
        # one-square escalating 11 (5 + 4 + 1 + 1), none 7 (5 + 1 + 1).
        print("\n## K1e. A gap-holding kiter (spend 3, reserve 6) against the brutes, by movement rule; then the same kiter in the room")
        gaps = {"v0.9": 20, "capped at Movement": 12, "one square, escalating": 11, "none": 7}
        rows = [run_cell(f"{k}, hold gap {gaps[k]}", kite_scenario(kiter(3, 6, gap=gaps[k]), brute()), v, trials, "K1e", events=100) for k, v in MOVE_RULES.items()]
        show(rows, KITE_COLS)
        rows = [run_cell(f"{k}, hold gap {gaps[k]}, no reserve", kite_scenario(kiter(3, 0, gap=gaps[k]), brute()), v, trials, "K1e", events=100) for k, v in MOVE_RULES.items()]
        show(rows, KITE_COLS)
        rows = [run_cell(f"room: {k}, hold gap {gaps[k]}", kite_scenario(kiter(3, 6, gap=gaps[k]), brute(), map_name="kite_room"), v, trials, "K1e", events=100) for k, v in MOVE_RULES.items()]
        show(rows, KITE_COLS)

    if which == "K2":
        print("\n## K2a. The same kiter against brutes in light armor (can it wear them down?)")
        rows = [run_cell(k, kite_scenario(kiter(2), brute(), brute_build="l1_brute_light"), v, trials, "K2a", events=100) for k, v in MOVE_RULES.items()]
        show(rows, KITE_COLS)
        print("\n## K2b. Against Agility-2 brutes (free 6, 2 squares per purchase)")
        rows = [run_cell(k, kite_scenario(kiter(2), brute(), brute_build="l1_brute_agi2"), v, trials, "K2b", events=100) for k, v in MOVE_RULES.items()]
        show(rows, KITE_COLS)
        print("\n## K2c. An Agility-1 archer (l1_archer, FIN 2) as the kiter against the AGI 0 brutes")
        rows = [run_cell(k, kite_scenario(kiter(2), brute(), kiter_build="l1_archer"), v, trials, "K2c", events=100) for k, v in MOVE_RULES.items()]
        show(rows, KITE_COLS)
        print("\n## K2d. One brute instead of two (v0.9 and capped)")
        rows = [run_cell(k, kite_scenario(kiter(2), brute(), brutes=1), v, trials, "K2d", events=100) for k, v in MOVE_RULES.items() if k in ("v0.9", "capped at Movement")]
        show(rows, KITE_COLS)

    if which == "K2e":
        print("\n## K2e. The kiter against two shielded sample fighters (Ranged Defense 3, armor 2, Agility 1), long field")
        text = kite_scenario(kiter(2), brute()).replace(str(BUILDS / "l1_brute.toml"), "l1_sample")
        rows = [run_cell(k, text, v, trials, "K2e", events=100) for k, v in MOVE_RULES.items() if k in ("v0.9", "capped at Movement", "none")]
        show(rows, KITE_COLS)

    if which == "K3":
        print("\n## K3. The room: three squares of floor behind the kiter")
        rows = [run_cell(k, kite_scenario(kiter(2), brute(), map_name="kite_room"), v, trials, "K3", events=100) for k, v in MOVE_RULES.items()]
        show(rows, KITE_COLS)

    if which == "D1":
        print("\n## D1. Duel first-mover edge by starting distance (squares apart) and movement rule, sample fighters, both tactical")
        for rule, ov in MOVE_RULES.items():
            rows = [run_cell(f"{rule}: {d} apart", duel_at(d), ov, trials, "D1") for d in (3, 5, 7, 9, 11, 13, 15)]
            show(rows, ("first_mover", "contact_round", "winner_untouched", "spent:A:extra_move", "spent:B:extra_move"))

    if which == "D1x":
        print("\n## D1x. The distance sweep continued: adjacent and near starts under v0.9, and two more rules (one square flat = F10 option 1; extra movement as an action)")
        rows = [run_cell(f"v0.9: {d} apart", duel_at(d), {}, trials, "D1x") for d in (1, 2)]
        show(rows, ("first_mover", "contact_round", "winner_untouched", "spent:A:extra_move", "spent:B:extra_move"))
        more = {"one square, flat": {"movement": {"extra_squares": "one"}}, "extra movement is an action": {"movement": {"extra_is_action": True}}}
        for rule, ov in more.items():
            rows = [run_cell(f"{rule}: {d} apart", duel_at(d), ov, trials, "D1x") for d in (7, 9, 11, 13, 15)]
            show(rows, ("first_mover", "contact_round", "winner_untouched", "spent:A:extra_move", "spent:B:extra_move"))
        print("\n## D1x-k. Kiting under 'extra movement is an action' (field and room, gap-holding kiter)")
        rows = [run_cell("field, hold gap 20", kite_scenario(kiter(3, 6, gap=20), brute()), more["extra movement is an action"], trials, "D1x", events=100),
                run_cell("field, maximise distance", kite_scenario(kiter(3, 6), brute()), more["extra movement is an action"], trials, "D1x", events=100)]
        show(rows, KITE_COLS)

    if which == "S1":
        print("\n## S1. An archer behind a fighter against two fighters, open ground, by gap and movement rule")
        for rule in ("v0.9", "none"):
            for gap in (1, 2):
                rows = [run_cell(f"{rule}, gap {gap}: {lbl}", screen_scenario(TACT, screen, TACT, gap), MOVE_RULES[rule], trials, "S1") for lbl, screen in (("tactical screen", TACT), ("holding screen", '{ kind = "tactical", commit = "chipkill", hold = true, retreat_engaged = 9 }'))]
                show(rows, ("first_mover", "contact_round", "shots_per_fight", "deaths", "down:party", "down:enemies"))

    if which == "R1":
        print("\n## R1. The standing exchange: kiter (longbow) shooting a brute that never moves and only blocks, by armor and distance; who runs dry")
        HOLD = '{ kind = "tactical", commit = "chipkill", hold = true, retreat_engaged = 9 }'
        rows = []
        for tb in ("l1_brute", "l1_brute_light"):
            for d in (6, 12):
                rows.append(run_cell(f"{tb} at {d}", standing_exchange("l1_kiter", tb, d, HOLD), {}, trials, "R1", events=100))
        show(rows, ("shots_per_fight", "injury_by:shooter", "spent:shooter:shot", "spent:target:block", "down:target"))
