# Run from sim/: python3 reports/movement_ranged_results/drivers/space.py 300
# Open-country distances: does one-square pricing give "the further you start, the more you have
# spent when the fight begins" without multi-turn kiting? D2: duels at 11-31 apart under v0.9,
# one square flat, capped; a dash-anything approacher and a disciplined one (chase_spend 6).
# A2: archer vs fighter at 16 / 20 / 24 squares. K4: the kiter on the long field under one square flat.
import json, sys, time
sys.argv = ["x"]
import pathlib
SIM = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(SIM)); sys.path.insert(0, str(SIM / "src"))
import experiments_ranged_movement as em
from stamina_engine.experiments.runner import run_scenario
from stamina_engine.experiments.scenario import scenario_from_toml
from stamina_engine.experiments.metrics import summarize
from stamina_engine.experiments.stats import wilson
from stamina_engine.provenance import collect
from stamina_engine.rules.ruleset import preset

trials = int(sys.argv[1]) if len(sys.argv) > 1 else 300
RULES = {"v0.9": {}, "one square, flat": {"movement": {"extra_squares": "one"}}, "capped at Movement": {"movement": {"extra_cap": "free_movement"}}}
MAP = str(em.MAPS / "open_38x10") + ".txt"
TACT = em.TACT
DISC = '{ kind = "tactical", commit = "chipkill", chase_spend = 6 }'

def duel(d, agent):
    return f'''
[scenario]
name = "duel-at-{d}"
ruleset = "v0.9"
map = "{MAP}"
round_cap = 30
trials = 400
seed = 20261104
[[combatant]]
id = "A"
team = "A"
build = "l1_sample"
spawn = [2, 6]
agent = {agent}
[[combatant]]
id = "B"
team = "B"
build = "l1_sample"
spawn = [{2 + d}, 6]
agent = {agent}
'''

def archer(d, fighter_agent):
    return f'''
[scenario]
name = "archer-at-{d}"
ruleset = "v0.9"
map = "{MAP}"
round_cap = 30
trials = 400
seed = 20261104
[[combatant]]
id = "A"
team = "archer"
build = "l1_archer"
spawn = [2, 6]
agent = {{ kind = "tactical", commit = "chipkill" }}
[[combatant]]
id = "F"
team = "fighter"
build = "l1_sample"
spawn = [{2 + d}, 6]
agent = {fighter_agent}
'''

def cell(label, text, ov, group, events=0):
    s = scenario_from_toml(text, em.BASE_DIR)
    rules = preset("v0.9").override(ov) if ov else preset("v0.9")
    s = s.with_rules(rules)
    t = time.time()
    res = run_scenario(s, trials=trials)
    f = res.fights; n = len(f)
    lines = summarize(f).lines()
    teams = sorted({k.split(":")[1] for k in f[0] if k.startswith("win:")})
    row = {"group": group, "label": label, "scenario": s.name, "ruleset": rules.name, "digest": rules.digest()[:12], "trials": n,
           "wins": {tm: wilson(sum(1 for x in f if x[f"win:{tm}"]), n).pct() for tm in teams},
           "first_mover": em.get(lines, "First mover wins"), "draws": wilson(sum(1 for x in f if x["winner"] is None), n).pct(),
           "rounds": em.get(lines, "Rounds"), "deaths": em.get(lines, "Deaths"), "winner_untouched": em.get(lines, "Winner untouched"),
           "contact_round": round(sum(x["contact_round"] for x in f if x["contact_round"] is not None) / max(1, sum(1 for x in f if x["contact_round"] is not None)), 2),
           "shots_per_fight": round(sum(x["shots"] for x in f) / n, 2), "seconds": round(time.time() - t, 1), "stamp": collect(rules).text()}
    for tm in teams:
        row[f"spent:{tm}:extra_move"] = round(sum(x[f"spent:{tm}:extra_move"] for x in f) / n, 2)
        row[f"moved:{tm}:on"] = round(sum(x[f"moved:{tm}:on"] for x in f) / n, 2)
    if events:
        row.update(em.injury_pass(s, min(events, n)))
    with (em.OUT / f"{group}.jsonl").open("a") as fh:
        fh.write(json.dumps(row) + "\n")
    wins = " ".join(f"{k} {v.split(' ')[0]}" for k, v in row["wins"].items())
    spend = " ".join(f"{tm}:{row[f'spent:{tm}:extra_move']}" for tm in teams)
    print(f"  {label:44s} [{row['digest']}] {wins:28s} fm {row['first_mover'][:5]:6s} draws {row['draws'][:5]:6s} rounds {row['rounds'].split(',')[0][5:10]} contact {row['contact_round']} move-spend {spend} shots {row['shots_per_fight']}")
    sys.stdout.flush()
    return row

if __name__ == "__main__":
    print("## D2. Duels at open-country distances; dash-anything approachers")
    for rule, ov in RULES.items():
        for d in (11, 15, 19, 23, 27, 31):
            cell(f"{rule}: {d} apart", duel(d, TACT), ov, "D2")
    print("## D2d. The same, disciplined approachers (spend at most 6 on the close)")
    for rule, ov in RULES.items():
        for d in (11, 15, 19, 23, 27):
            cell(f"{rule}, disciplined: {d} apart", duel(d, DISC), ov, "D2d")
    print("## A2. Archer vs fighter at 16 / 20 / 24 squares (longbow medium, medium, long)")
    for rule, ov in RULES.items():
        for d in (16, 20, 24):
            cell(f"{rule}: {d} apart", archer(d, TACT), ov, "A2")
    print("## K4. The kiter vs two brutes, long field, one square flat")
    cell("one square, flat", em.kite_scenario(em.kiter(2), em.brute()), RULES["one square, flat"], "K4", events=100)
    print("space done")
