# ruff: noqa: E501
"""Movement exploration (design request 2026-11-04): off-turn window order, on-turn extra
movement variants, terrain and counts. Run from sim/ with PYTHONPATH=src:

    python3 -u experiments_movement.py <runner> [trials]

Runners: B1 (window order, six scenarios), B1n (window order with no on-turn extra movement),
B2 (on-turn extra movement variants, seven scenarios), B2rest (its last three), B2x (the cost dial),
B3 (terrain, counts, Agility), B3e (a defender that holds its square), B3f (the door under the
diagonal-corner rule). Write-ups: reports/movement_exploration.md and its notes.

Writes results as JSON lines to reports/movement_exploration_results/*.jsonl and prints tables.
Every row carries the RuleSet digest and the code stamp."""

import json
import sys
import time
from pathlib import Path

from stamina_engine.experiments.metrics import summarize
from stamina_engine.experiments.runner import run_scenario
from stamina_engine.experiments.scenario import scenario_from_toml
from stamina_engine.provenance import collect
from stamina_engine.rules.ruleset import preset

OUT = Path("reports/movement_exploration_results")
OUT.mkdir(parents=True, exist_ok=True)
BASE_DIR = Path("src/stamina_engine/data/scenarios")

# ---------------------------------------------------------------------------- rulesets
ORDER_RULESETS = {
    "asc (v0.9)": {},
    "desc": {"off_turn": {"order": "descending_initiative"}},
    "desc+restart (declare/tiebreak)": {
        "off_turn": {"order": "descending_initiative", "restart_after_move": True}
    },
    "desc+restart, 1 purchase per move": {
        "off_turn": {"order": "descending_initiative", "restart_after_move": True, "purchase_cap": 1}
    },
    "asc, 1 purchase per move": {"off_turn": {"purchase_cap": 1}},
}
EXTRA_RULESETS = {
    "agi, flat (v0.9)": {},
    "one square, flat": {"movement": {"extra_squares": "one"}},
    "agi, escalating": {"movement": {"extra_mode": "escalating"}},
    "one square, escalating": {"movement": {"extra_squares": "one", "extra_mode": "escalating"}},
    "agi, capped at Movement": {"movement": {"extra_cap": "free_movement"}},
    "none": {"movement": {"extra_mode": "none"}},
}


def rules_for(overrides: dict, base: str = "v0.9", name: str | None = None):
    r = preset(base)
    if overrides:
        r = r.override(overrides)
    return r.with_(name=name) if name else r


# ---------------------------------------------------------------------------- scenarios
def toml_scenario(text: str):
    return scenario_from_toml(text, BASE_DIR)


def duel_apart(agent_a: str, agent_b: str, distance: int = 8, build: str = "l1_sample") -> str:
    xa = 2
    xb = xa + distance
    return f"""
[scenario]
name = "duel-apart-{distance}"
ruleset = "v0.9"
map = "open_12x12"
round_cap = 30
trials = 500
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
spawn = [{xb}, 6]
agent = {agent_b}
"""


TACT_PIN = '{ kind = "tactical", commit = "chipkill", off_turn = "retreat_pin" }'
TACT_PIN_FLEE = '{ kind = "tactical", commit = "chipkill", off_turn = "retreat_pin", retreat_engaged = 1, low_stamina = "1/2" }'
TACT = '{ kind = "tactical", commit = "chipkill" }'
TACT_FLEE = '{ kind = "tactical", commit = "chipkill", retreat_engaged = 1, low_stamina = "1/2" }'


def archer_scenario(fighter_agent: str, map_name: str = "archer_open") -> str:
    return f"""
[scenario]
name = "archer-{map_name}"
ruleset = "v0.9"
map = "{map_name}"
round_cap = 30
trials = 500
seed = 20261104
[[combatant]]
id = "A"
team = "archer"
build = "l1_archer"
spawn = "A"
agent = {{ kind = "tactical", commit = "chipkill" }}
[[combatant]]
id = "F"
team = "fighter"
build = "l1_sample"
spawn = "F"
agent = {fighter_agent}
"""


def one_v_three(map_name: str, defender_agent: str, attacker_agent: str, spawn_d: str = "A") -> str:
    spawns = '["1", "2", "3"]'
    return f"""
[scenario]
name = "1v3-{map_name}"
ruleset = "v0.9"
map = "{map_name}"
round_cap = 20
trials = 500
seed = 20261104
[[combatant]]
id = "D"
team = "defender"
build = "l1_sample"
spawn = "{spawn_d}"
agent = {defender_agent}
[[combatant]]
id = "x"
team = "attackers"
build = "l1_sample"
count = 3
spawn = {spawns}
agent = {attacker_agent}
"""


def retreat_line(fleer_agent: str, chaser_agent: str) -> str:
    return f"""
[scenario]
name = "retreat-line"
ruleset = "v0.9"
map = "retreat_line"
round_cap = 30
trials = 500
seed = 20261104
[[combatant]]
id = "F"
team = "line"
build = "l1_sample"
spawn = "F"
agent = {fleer_agent}
[[combatant]]
id = "A"
team = "line"
build = "l1_sample"
spawn = [4, 4]
agent = "fixed:2"
[[combatant]]
id = "C"
team = "chasers"
build = "l1_sample"
spawn = "C"
agent = {chaser_agent}
[[combatant]]
id = "B"
team = "chasers"
build = "l1_sample"
spawn = "B"
agent = {chaser_agent}
"""


# ---------------------------------------------------------------------------- running
def get(lines: list[str], key: str) -> str:
    for line in lines:
        if line.startswith(key):
            return line.split(":", 1)[1].strip()
    return ""


def pct(s: str) -> str:
    return s.split()[0] if s else ""


def run_cell(label: str, scenario_text: str, overrides: dict, trials: int, group: str) -> dict:
    s = toml_scenario(scenario_text)
    rules = rules_for(overrides)
    s = s.with_rules(rules)
    t = time.time()
    res = run_scenario(s, trials=trials)
    lines = summarize(res.fights).lines()
    teams = [line for line in lines if line.endswith("]") and " wins: " in line]
    row = {
        "group": group,
        "label": label,
        "scenario": s.name,
        "ruleset": rules.name,
        "digest": rules.digest()[:12],
        "trials": trials,
        "wins": {line.split(" wins:")[0]: line.split(":", 1)[1].strip() for line in teams},
        "draws": get(lines, "Draws"),
        "rounds": get(lines, "Rounds"),
        "first_mover": get(lines, "First mover wins"),
        "winner_untouched": get(lines, "Winner untouched"),
        "loser_hp": get(lines, "Loser ends at"),
        "deaths": get(lines, "Deaths per fight"),
        "decisions_per_round": get(lines, "Decisions per round"),
        "rounds_to_contact": get(lines, "Rounds to contact"),
        "oas": get(lines, "Opportunity attacks per fight"),
        "off_turn_squares": get(lines, "Squares moved off-turn"),
        "seconds": round(time.time() - t, 1),
        "stamp": collect(rules).text(),
    }
    with (OUT / f"{group}.jsonl").open("a") as f:
        f.write(json.dumps(row) + "\n")
    return row


def show(rows: list[dict], cols: tuple[str, ...]) -> None:
    for r in rows:
        wins = " ".join(f"{k} {pct(v)}" for k, v in r["wins"].items())
        extra = " | ".join(f"{c}: {pct(r[c]) if c != 'rounds' else r[c].split('median')[1].strip() if 'median' in r[c] else r[c]}" for c in cols)
        print(f"  {r['label']:38s} [{r['digest']}] {wins:34s} | {extra}")


# ---------------------------------------------------------------------------- B3: terrain, counts, stats
CORNER_MAP = '''##############
#D...........#
#............#
#............#
#............#
#............#
#............#
#.1..........#
#.2..........#
#.3..........#
#............#
#............#
#............#
##############'''
PILLARS_MAP = '''##############
#............#
#..o...o...o.#
#............#
#D.o...o...o.#
#............#
#..o...o...o.#
#............#
#1.o...o...o.#
#2...........#
#3.o...o...o.#
#............#
#............#
##############'''
DOOR_MAP = '''##############
#......#.....#
#......#.....#
#......#.....#
#......#.....#
#1.....#.....#
#2......D....#
#3.....#.....#
#......#.....#
#......#.....#
##############'''


def n_v_m(n: int, m: int, agent_a: str, agent_b: str, map_name: str = "open_12x12") -> str:
    xs_a = [(2, 3 + 3 * i) for i in range(n)]
    xs_b = [(10, 3 + 3 * i) for i in range(m)]
    def group(prefix: str, team: str, cells: list, agent: str) -> str:
        return "\n".join(f'''[[combatant]]
id = "{prefix}{i}"
team = "{team}"
build = "l1_sample"
spawn = [{c[0]}, {c[1]}]
agent = {agent}''' for i, c in enumerate(cells))
    return f'''
[scenario]
name = "{n}v{m}-{map_name}"
ruleset = "v0.9"
map = "{map_name}"
round_cap = 30
trials = 400
seed = 20261104
{group("a", "A", xs_a, agent_a)}
{group("b", "B", xs_b, agent_b)}
'''


def one_v_three_text(map_text: str, name: str, defender_agent: str, attacker_agent: str, build: str = "l1_sample") -> str:
    return f'''
[scenario]
name = "1v3-{name}"
ruleset = "v0.9"
map_text = """{map_text}"""
round_cap = 20
trials = 400
seed = 20261104
[[combatant]]
id = "D"
team = "defender"
build = "{build}"
spawn = "D"
agent = {defender_agent}
[[combatant]]
id = "x"
team = "attackers"
build = "l1_sample"
count = 3
spawn = ["1", "2", "3"]
agent = {attacker_agent}
'''


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "B1"
    trials = int(sys.argv[2]) if len(sys.argv) > 2 else 500
    print(collect(preset("v0.9")).text())

    if which == "B1":
        print("\n## B1a. Duel, 8 squares apart, both tactical with retreat+pin (retreat when engaged by 1 and below 1/2 stamina)")
        rows = [run_cell(k, duel_apart(TACT_PIN_FLEE, TACT_PIN_FLEE), v, trials, "B1a") for k, v in ORDER_RULESETS.items()]
        show(rows, ("first_mover", "draws", "rounds", "off_turn_squares", "oas", "decisions_per_round"))

        print("\n## B1b. Duel, 8 apart: A (declared first in file) pins, B flees; initiative random")
        rows = [run_cell(k, duel_apart(TACT_PIN, TACT_FLEE), v, trials, "B1b") for k, v in ORDER_RULESETS.items()]
        show(rows, ("first_mover", "draws", "rounds", "off_turn_squares", "oas"))

        print("\n## B1c. Archer (tactical) vs fighter that pins off-turn, open ground")
        rows = [run_cell(k, archer_scenario(TACT_PIN), v, trials, "B1c") for k, v in ORDER_RULESETS.items()]
        show(rows, ("first_mover", "rounds", "off_turn_squares", "oas", "rounds_to_contact"))

        print("\n## B1d. 1v3 open: retreating defender vs pinning attackers")
        rows = [run_cell(k, one_v_three("open_12x12", TACT_FLEE, TACT_PIN), v, trials, "B1d") for k, v in ORDER_RULESETS.items()]
        show(rows, ("rounds", "deaths", "off_turn_squares", "oas"))

        print("\n## B1e. 1v3 corridor: retreating defender vs pinning attackers")
        rows = [run_cell(k, one_v_three("corridor", TACT_FLEE, TACT_PIN, spawn_d="D"), v, trials, "B1e") for k, v in ORDER_RULESETS.items()]
        show(rows, ("rounds", "deaths", "off_turn_squares", "oas"))

        print("\n## B1f. Retreat line 2v2: fleer (tactical, retreat when engaged) vs pinning tactical chasers")
        rows = [run_cell(k, retreat_line(TACT_FLEE, '{ kind = "tactical", commit = "alpha", target = "first", off_turn = "pin" }'), v, trials, "B1f") for k, v in ORDER_RULESETS.items()]
        show(rows, ("first_mover", "rounds", "off_turn_squares", "oas"))

    if which == "B2":
        print("\n## B2a. Archer vs fighter, open ground, both tactical")
        rows = [run_cell(k, archer_scenario(TACT), v, trials, "B2a") for k, v in EXTRA_RULESETS.items()]
        show(rows, ("first_mover", "rounds", "rounds_to_contact", "off_turn_squares"))
        print("\n## B2b. Archer vs fighter, scattered cover, both tactical")
        rows = [run_cell(k, archer_scenario(TACT, "archer_cover"), v, trials, "B2b") for k, v in EXTRA_RULESETS.items()]
        show(rows, ("first_mover", "rounds", "rounds_to_contact", "off_turn_squares"))
        print("\n## B2c. Duel 8 apart, both tactical (first mover must buy 1 square to strike first)")
        rows = [run_cell(k, duel_apart(TACT, TACT), v, trials, "B2c") for k, v in EXTRA_RULESETS.items()]
        show(rows, ("first_mover", "draws", "rounds", "winner_untouched"))
    if which in ("B2", "B2rest"):
        print("\n## B2d. Duel 10 apart, both tactical")
        rows = [run_cell(k, duel_apart(TACT, TACT, distance=10), v, trials, "B2d") for k, v in EXTRA_RULESETS.items()]
        show(rows, ("first_mover", "draws", "rounds", "winner_untouched"))
        print("\n## B2e. Retreat line 2v2: tactical fleer vs tactical chasers")
        rows = [run_cell(k, retreat_line(TACT_FLEE, '{ kind = "tactical", commit = "alpha", target = "first" }'), v, trials, "B2e") for k, v in EXTRA_RULESETS.items()]
        show(rows, ("first_mover", "rounds", "off_turn_squares", "oas"))
        print("\n## B2f. 1v3 open, tactical defender vs 2-step attackers")
        rows = [run_cell(k, one_v_three("open_12x12", TACT, '"fixed:2"'), v, trials, "B2f") for k, v in EXTRA_RULESETS.items()]
        show(rows, ("rounds", "deaths", "off_turn_squares", "rounds_to_contact"))
        print("\n## B2g. 1v3 corridor, tactical defender vs 2-step attackers")
        rows = [run_cell(k, one_v_three("corridor", TACT, '"fixed:2"', spawn_d="D"), v, trials, "B2g") for k, v in EXTRA_RULESETS.items()]
        show(rows, ("rounds", "deaths", "off_turn_squares", "rounds_to_contact"))

    if which == "B1n":
        NONE = {"movement": {"extra_mode": "none"}}
        combos = {k + " | no on-turn extra": {**v, **NONE} for k, v in ORDER_RULESETS.items() if "1 purchase" not in k or "restart" in k}
        print("\n## B1n-a. Archer (tactical) vs fighter that pins off-turn, open ground, NO on-turn extra movement")
        rows = [run_cell(k, archer_scenario(TACT_PIN), v, trials, "B1n_a") for k, v in combos.items()]
        show(rows, ("first_mover", "rounds", "off_turn_squares", "oas", "rounds_to_contact"))
        print("\n## B1n-b. Archer vs plain tactical fighter (no pin), NO on-turn extra movement")
        rows = [run_cell(k, archer_scenario(TACT), v, trials, "B1n_b") for k, v in combos.items()]
        show(rows, ("first_mover", "rounds", "off_turn_squares", "oas", "rounds_to_contact"))
        print("\n## B1n-c. Retreat line 2v2, fleer vs pinning chasers, NO on-turn extra movement")
        rows = [run_cell(k, retreat_line(TACT_FLEE, '{ kind = "tactical", commit = "alpha", target = "first", off_turn = "pin" }'), v, trials, "B1n_c") for k, v in combos.items()]
        show(rows, ("first_mover", "rounds", "off_turn_squares", "oas"))
        print("\n## B1n-d. Duel 8 apart, both retreat+pin, NO on-turn extra movement")
        rows = [run_cell(k, duel_apart(TACT_PIN_FLEE, TACT_PIN_FLEE), v, trials, "B1n_d") for k, v in combos.items()]
        show(rows, ("first_mover", "draws", "rounds", "off_turn_squares", "oas"))

if __name__ == "__main__" and (len(sys.argv) > 1 and sys.argv[1] == "B3"):
    trials = int(sys.argv[2]) if len(sys.argv) > 2 else 400
    NOWIN = {"off_turn": {"enabled": False}}
    NONE = {"movement": {"extra_mode": "none"}}
    terrains = {
        "open": one_v_three("open_12x12", TACT, '"fixed:2"'),
        "corner": one_v_three_text(CORNER_MAP, "corner", TACT, '"fixed:2"'),
        "pillars": one_v_three_text(PILLARS_MAP, "pillars", TACT, '"fixed:2"'),
        "door": one_v_three_text(DOOR_MAP, "door", TACT, '"fixed:2"'),
        "corridor": one_v_three("corridor", TACT, '"fixed:2"', spawn_d="D"),
    }
    print("\n## B3a. 1v3 by terrain, tactical defender (fixed:2) vs three 2-step attackers; windows on / off; no on-turn extra")
    for tname, text in terrains.items():
        rows = [run_cell(f"{tname}: {k}", text, v, trials, "B3a") for k, v in (("v0.9", {}), ("off-turn windows OFF", NOWIN), ("no on-turn extra", NONE))]
        show(rows, ("rounds", "deaths", "off_turn_squares", "oas", "rounds_to_contact"))
    print("\n## B3b. Same, attackers tactical with pin (focus fire, close off-turn)")
    for tname, text in terrains.items():
        text2 = text.replace('agent = "fixed:2"', f"agent = {TACT_PIN}")
        rows = [run_cell(f"{tname}: {k}", text2, v, trials, "B3b") for k, v in (("v0.9", {}), ("off-turn windows OFF", NOWIN))]
        show(rows, ("rounds", "deaths", "off_turn_squares", "oas"))
    print("\n## B3c. Numbers: N v M equal sample fighters on open ground, tactical chipkill both sides")
    for n, m in ((1, 1), (1, 2), (2, 2), (2, 3), (3, 3), (2, 4), (3, 4)):
        rows = [run_cell(f"{n}v{m}: {k}", n_v_m(n, m, TACT, TACT), v, trials, "B3c") for k, v in (("v0.9", {}), ("no on-turn extra", NONE))]
        show(rows, ("rounds", "deaths", "first_mover", "off_turn_squares"))
    print("\n## B3d. Agility 5 defender (free 8, 4 sq/purchase, MD 5) vs AGI 1, 1v3 corridor and door, by movement rule")
    for tname in ("corridor", "door"):
        for build in ("l1_sample", str((OUT / "builds" / "l1_agi5.toml").resolve())):
            text = one_v_three("corridor", TACT, '"fixed:2"', spawn_d="D").replace('build = "l1_sample"\nspawn = "D"', f'build = "{build}"\nspawn = "D"') if tname == "corridor" else one_v_three_text(DOOR_MAP, "door", TACT, '"fixed:2"', build=build)
            label = "AGI 5" if "agi5" in build else "AGI 1"
            rows = [run_cell(f"{tname} {label}: {k}", text, v, trials, "B3d") for k, v in (("v0.9", {}), ("no on-turn extra", NONE), ("one sq flat", {"movement": {"extra_squares": "one"}}))]
            show(rows, ("rounds", "deaths", "off_turn_squares", "oas"))


if __name__ == "__main__" and (len(sys.argv) > 1 and sys.argv[1] == "B3e"):
    trials = int(sys.argv[2]) if len(sys.argv) > 2 else 300
    HOLD = '{ kind = "tactical", commit = "chipkill", hold = true, retreat_engaged = 2 }'
    HOLD_NORETREAT = '{ kind = "tactical", commit = "chipkill", hold = true, retreat_engaged = 9 }'
    NOWIN = {"off_turn": {"enabled": False}}
    CORR_DEEP = one_v_three("corridor", HOLD_NORETREAT, '"fixed:2"', spawn_d="D").replace('spawn = "D"', 'spawn = [9, 4]')
    CORR_MOUTH = one_v_three("corridor", HOLD_NORETREAT, '"fixed:2"', spawn_d="D")
    DOOR_HOLD = one_v_three_text(DOOR_MAP, "door", HOLD_NORETREAT, '"fixed:2"')
    OPEN_HOLD = one_v_three("open_12x12", HOLD_NORETREAT, '"fixed:2"')
    CORNER_HOLD = one_v_three_text(CORNER_MAP, "corner", HOLD_NORETREAT, '"fixed:2"')
    print("\n## B3e. 1v3 with a defender that HOLDS its square (attacks whoever is in reach), vs three 2-step attackers")
    for tname, text in (("open", OPEN_HOLD), ("corner", CORNER_HOLD), ("door (behind the gap)", DOOR_HOLD), ("corridor mouth (8,4)", CORR_MOUTH), ("corridor one square in (9,4)", CORR_DEEP)):
        rows = [run_cell(f"{tname}: {k}", text, v, trials, "B3e") for k, v in (("v0.9", {}), ("windows OFF", NOWIN))]
        show(rows, ("rounds", "deaths", "off_turn_squares", "oas", "winner_untouched"))
    print("\n## B3e2. Same, attackers tactical (chipkill, fewest-engagers squares)")
    for tname, text in (("door (behind the gap)", DOOR_HOLD), ("corridor one square in (9,4)", CORR_DEEP)):
        text2 = text.replace('agent = "fixed:2"', f"agent = {TACT}")
        rows = [run_cell(f"{tname}: {k}", text2, v, trials, "B3e2") for k, v in (("v0.9", {}),)]
        show(rows, ("rounds", "deaths", "off_turn_squares", "oas"))
    print("\n## B3e3. 2v3: two holders side by side in the open vs three 2-step attackers; and 2v3 all tactical")
    for label, text in (("2v3 holders", n_v_m(2, 3, HOLD_NORETREAT, '"fixed:2"')), ("2v3 tactical", n_v_m(2, 3, TACT, TACT))):
        rows = [run_cell(f"{label}: v0.9", text, {}, trials, "B3e3")]
        show(rows, ("rounds", "deaths", "first_mover", "off_turn_squares"))


if __name__ == "__main__" and (len(sys.argv) > 1 and sys.argv[1] == "B2x"):
    trials = int(sys.argv[2]) if len(sys.argv) > 2 else 400
    DIAL = {
        "agi, flat (v0.9): 12 sq = 3": {},
        "agi, escalating slope 1: 12 sq = 6": {"movement": {"extra_mode": "escalating"}},
        "agi, escalating slope 2: 12 sq = 9": {"movement": {"extra_mode": "escalating", "extra_slope": 2}},
        "free 5, agi escalating slope 1: 12 sq = 10": {"movement": {"free_base": 4, "extra_mode": "escalating"}},
        "free 4, agi escalating slope 1: 12 sq = 15": {"movement": {"free_base": 3, "extra_mode": "escalating"}},
        "one sq, escalating slope 1: 12 sq = 21": {"movement": {"extra_squares": "one", "extra_mode": "escalating"}},
        "none": {"movement": {"extra_mode": "none"}},
    }
    print("\n## B2x-a. The on-turn movement dial: archer vs fighter, open ground, both tactical")
    rows = [run_cell(k, archer_scenario(TACT), v, trials, "B2x_a") for k, v in DIAL.items()]
    show(rows, ("first_mover", "rounds", "winner_untouched", "off_turn_squares"))
    print("\n## B2x-b. Duel 8 apart, both tactical")
    rows = [run_cell(k, duel_apart(TACT, TACT), v, trials, "B2x_b") for k, v in DIAL.items()]
    show(rows, ("first_mover", "draws", "rounds", "winner_untouched", "off_turn_squares"))
    print("\n## B2x-c. Retreat line 2v2, tactical fleer vs tactical chasers")
    rows = [run_cell(k, retreat_line(TACT_FLEE, '{ kind = "tactical", commit = "alpha", target = "first" }'), v, trials, "B2x_c") for k, v in DIAL.items()]
    show(rows, ("first_mover", "rounds", "off_turn_squares", "oas"))
    print("\n## B2x-d. 2v2 open, tactical chipkill")
    rows = [run_cell(k, n_v_m(2, 2, TACT, TACT), v, trials, "B2x_d") for k, v in DIAL.items()]
    show(rows, ("first_mover", "rounds", "deaths", "off_turn_squares", "decisions_per_round"))


if __name__ == "__main__" and (len(sys.argv) > 1 and sys.argv[1] == "B3f"):
    # Does the diagonal-corner rule (grid.corners, pending designer) decide whether a one-square
    # door is a chokepoint? Default no_squeeze lets an attacker step diagonally out of the gap past
    # the defender; no_cut forbids any diagonal past a wall corner.
    trials = int(sys.argv[2]) if len(sys.argv) > 2 else 300
    HOLD_NORETREAT = '{ kind = "tactical", commit = "chipkill", hold = true, retreat_engaged = 9 }'
    DOOR_HOLD = one_v_three_text(DOOR_MAP, "door", HOLD_NORETREAT, '"fixed:2"')
    DOOR_TACT = one_v_three_text(DOOR_MAP, "door", TACT, '"fixed:2"')
    NOCUT = {"grid": {"corners": "no_cut"}}
    print("\n## B3f. The door under the corner rule: no_squeeze (engine default) vs no_cut; holding defender behind the gap, then tactical defender")
    rows = [
        run_cell("holder, corners no_squeeze (default)", DOOR_HOLD, {}, trials, "B3f"),
        run_cell("holder, corners no_cut", DOOR_HOLD, NOCUT, trials, "B3f"),
        run_cell("tactical D, corners no_squeeze (default)", DOOR_TACT, {}, trials, "B3f"),
        run_cell("tactical D, corners no_cut", DOOR_TACT, NOCUT, trials, "B3f"),
    ]
    show(rows, ("draws", "rounds", "deaths", "winner_untouched", "off_turn_squares"))
