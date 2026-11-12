# Using the engine from a design chat

For claude.ai chats in the "Tactical fantasy TTRPG" project. Claude Code keeps this file current.

**Status:** milestones M0–M5 are done (tags `m0`–`m5`): the turn engine, maps and movement, opportunity attacks, ranged attacks, cover and diving, drawing weapons, equipment variant tables, NPC profiles, fleeing and surrendering, the full phase suite, class cores and candidate abilities with strain, playing a side yourself, and the load report. M5's gate still needs one session played by a person. Packet versions 0.9.1–0.10.0 are the presets `v0.9.1`, `v0.9.2`, `v0.9.3` and `v0.10.0` (below).

## Purpose: evidence, not the answer

The engine exists to support design decisions. Its fights are a simplified model of the game, played by scripted agents; it cannot tell you whether the game is fun, whether a decision feels meaningful, or how players will actually behave. A design chat's main work is reasoning about the rules: brainstorming, playing scenarios out by hand, and arguing from the pillars. The engine is a secondary check on that reasoning.

- **Default to reasoning.** For questions about feel, decisions, incentives or pacing, play two or three rounds of a specific fight by hand: real positions, the choices each side faces, what each player would be thinking. That captures what the engine leaves out, and it is the default evidence for those questions.
- **Run the engine only to test a specific claim** your advice depends on. Before running, write down the claim, why the engine can test it, what you expect to see, and what each plausible result would mean for the design. If you can't fill that in, don't run it.
- **Check every result against the limitations below** before using it. Ask: "Could this result change if the missing thing were present?" If plausibly yes, the engine can't settle the question; say so, and reason it out instead.
- **A number never stands alone.** A simulated result appears in a reply only as support for a design point, with its design implication and the limitation most likely to undercut it.

## What the engine doesn't capture

These are the simplifications most likely to matter to design advice. Name the relevant ones whenever you draw a conclusion from a run.

**Players and agents**
- **Agents are heuristics, not players.** Scripted agents follow one fixed commitment policy (`alpha`, `fixed:k`, `reserve:N`, `chipkill`, `lookahead`). Tactical agents score squares and retreat by fixed thresholds. Neither reads the opponent, adapts across a fight, bluffs, baits, or plans several turns ahead.
- **Blocking is a fixed exchange rate.** The block solver minimizes stamina + w × injury with a constant `w` (3 by default). Real players value an HP point very differently depending on the situation (the next fight, a downed ally, how close they are to dying).
- **"No dominant strategy" can't be established here.** The search auditor (M6) isn't built, so a strategy the agents don't try can still dominate. Absence of an exploit in engine results is weak evidence.
- **Teamwork is minimal.** Agents focus fire by target policy, but there is no coordinated plan: no flanking setups, protecting a weak ally, body-blocking a gap, or trading position for tempo. Deniers in objective scenarios attack rather than block routes.
- **Scripted agents barely use movement.** They approach with free movement and never move off-turn or buy squares. Results from scripted agents say little about positioning, diving, retreat or opportunity attacks.
- **Agent behavior can produce a result by itself.** A result that holds for only one agent family, or that a smarter choice would plausibly overturn, is about the agents, not the rules.

**The game around the fight**
- **Each fight is the whole world.** Fights start at full HP and stamina with strain 0. There's no adventuring day: wounds don't carry into the next fight as lower maximum stamina, strain isn't a day budget, and nightly recovery isn't modeled (CAMPAIGN_PLAN.md is a proposal, not built). Anything about attrition, risk-taking across a day, or how punishing a loss is lives mostly outside the engine.
- **No GM.** There's no telegraphing, morale beyond NPC profile thresholds, reinforcements, terrain the GM invents, or narrative stakes. Fleeing and surrender are engine conventions, not packet rules.
- **Scenarios are chosen, not representative.** Maps, rosters and builds come from a small library (mostly level 1, a few at 30 and 99). A result describes that scenario, not encounters in general.

**Rules coverage**
- **Packet 0.10.0 isn't implemented.** The ranged package, cover and Ranged Defense changes, and shields at +1 aren't in any preset yet (see Packet versions).
- **Out of scope:** spells and spell lists, conditions, grappling, extended contests, skill checks, out-of-combat rules, and advancement beyond derived numbers.
- **Silent readings.** Where the packet is unclear, the engine picks a reading recorded in the Assumptions register (`sim/docs/ENGINE_PLAN.md`). A result can hinge on one; check the register before trusting a surprising number.

**Experience**
- **The engine measures outcomes, not experience.** Win rates, rounds and HP lost don't show whether choices feel meaningful, whether arithmetic feels like busywork, or whether fights feel tense or grindy. The load report (`se load`) counts decisions and options, not whether they're interesting. The single human `se play` session is the only experience data, and it hasn't been played yet.

## Packet versions

Each packet version is a preset. **`v0.10.0` (packet 0.10.0, the ranged package) is the baseline** (ruled 2026-11-11): the library's scenarios and the milestone suites name it, and it's what a scenario without a ruleset, a sweep without rulesets and `se table` use. Its equipment is the `v0_10` table (the new bows and the +1 / +1 shield): a scenario that names no `equipment` gets its RuleSet's own, `v0_10` for 0.10.0's range bands and `v0_9` for earlier presets, and the engine refuses to mix 0.10.0's rules with v0.9's bows, or the reverse. Results from before 2026-11-11 ran under `v0.9.3` (+2 shields, v0.9's ranged rules) or earlier presets. `v0.9` stays the v0.9 packet, so earlier results still reproduce, and `review-sim` (parity) and `review-candidate` are built on it. Name `v0.9` to reproduce the review or an earlier result: `se table 5 --ruleset v0.9`, or `se compare scenario.toml --a v0.9.3 --b v0.10.0`. Every report in `sim/reports/` names the preset it ran under in its stamp.

| Preset | Rules (see `rules/CHANGELOG.md`) |
|---|---|
| `v0.9.1` | No opportunity-attack cap (`opportunity.cap_rule = "none"`); extra on-turn movement 1 square a purchase (`movement.extra_squares = "one"`); initiative 2d12 + Cunning (`turn_order.bonus = "cunning"`); maximum HP 6 + 2 per even Strength (`resources.hp_strength = "per_even"`); the dying roll adds Will (`dying.roll_attribute = "will"`); Intelligence's core-ability discount and bonus AP in build budgets (`resources.core_discount`, `resources.bonus_ap`) |
| `v0.9.2` | 0.9.1, with +1 per critical die only if damage gets past blocks and armor (`crit` kind `per_die_if_through`) and maximum HP 8 + 2 per even Strength (`resources.hp_base = 8`) |
| `v0.9.3` | 0.9.2's components and digest under the new name: 0.9.3's changes (healing below 0 HP, dying rolls after a fight ends) are all after a fight, which the engine doesn't play yet. The campaign layer's rest rules will extend it |
| `v0.10.0` | 0.9.3, with linear range bands: a band width per bow, −2 per further band measured after the target's reaction, no maximum range (`ranged.bands = "linear"`, `ranged.range_measured = "after_reaction"`); shots are actions (`ranged.shot_action`) with one free aim die (`ranged.free_aim_dice = 1`); aim steps 1d6 with no Finesse (`ranged.aim_finesse = false`); the aim limit (`ranged.aim_limit = "damage_roll"`); aim dice never critical (`crit.aim_dice_can_crit = false`); cover +1 / +2; +1 Ranged Defense for moving in reaction to a shot (`ranged.reaction_bonus = 1`) and per even Agility (`defenses.ranged_mode = "dodge_folded"`); point-blank OAs only from enemies in reach both when the shot is declared and when they happen (`opportunity.point_blank_eligible`). Use it with `equipment = "v0_10"`: shortbow, longbow, warbow and superheavy warbow with band widths, Strength requirements, Piercing and Precise, and the +1 / +1 shield |
| `v0.10.0-cover-only` | Not a packet version: the "reaction changes cover only" package. 0.10.0, with the range penalty and Melee vs Ranged Defense judged where the target was when the shot was declared (`ranged.range_measured = "declaration"`, `ranged.defense_timing = "declaration"`); a reaction still earns cover and the +1 |
| `v0.10.0-crit-c-prime`, `v0.10.0-crit-c` | Not packet versions: the solver study's crit rules C′ (aim dice crit only on a 6, at most one critical die a shot) and C (every die can crit, Finesse-widened, at most one a shot). 0.10.0 itself is rule A |

Nightly HP recovery isn't modeled, since the engine plays single fights. Without a cap, engine agents size an opportunity attack by their commitment policy rather than spending everything (Assumptions register).

## Reading the code

`rules/`, `design/` and `sim/` sync into the project automatically, so a chat can read them without cloning. Synced copies can lag behind GitHub; clone when the exact current code matters.

## Running it

```bash
git clone --depth 1 https://github.com/BenjaminTzudiker/TTriangulaRPG.git
cd TTriangulaRPG/sim
pip install -e . --break-system-packages   # add [parquet], as in '.[parquet]', for --out
```

**No PyPI? Install nothing.** The engine and its CLI use only the standard library (Python 3.12 or newer), so a chat that can't reach PyPI runs them straight from the checkout:

```bash
cd TTriangulaRPG/sim
export PYTHONPATH=src
python3 -m stamina_engine table 1   # every se command works this way
python3 -m pytest                   # needs pytest; the property tests skip without hypothesis
```

Only `--out` (Parquet tables) needs a package, pyarrow; without it, `--out` says so and everything else runs. From Python, `invoke(["table", "1"]).output` (from `stamina_engine.cli`) runs any command and returns its output.

In a claude.ai chat, attach the repo first if the clone is refused. To reproduce a quoted result, check out the tag or commit its stamp names (`git fetch --depth 1 origin tag m1 && git checkout m1`).

## Commands

Run from `sim/`. With uv (`uv sync` once, then prefix commands with `uv run`), after `pip install -e .`, or with nothing installed as `python3 -m stamina_engine` in place of `se` (with `PYTHONPATH=src`):

```bash
se table 1                                             # Table 1's layout under the baseline, packet rounding
se table 1 --ruleset v0.9                             # review Table 1 under the review's rules
se table 1 --ruleset review-sim --rounding half-even   # reproduces the review's printed Table 1
se table 8 --ruleset v0.9 --rounding half-even         # review Table 8
se run src/stamina_engine/data/scenarios/l1_duel.toml --trials 2000 --workers 4
se compare src/stamina_engine/data/scenarios/one_v_three.toml --a v0.9.3 --b v0.10.0
se sweep src/stamina_engine/data/scenarios/surcharge_sweep.toml --out results/surcharge
se suite parity --workers 8 --out reports/m1_parity.md # every published review fight, in lockstep
se map list                                            # library maps
se map show corridor                                   # a map with coordinates and spawns
se run src/stamina_engine/data/scenarios/one_v_three_corridor.toml --trials 500 --workers 4
se trace src/stamina_engine/data/scenarios/one_v_three_corridor.toml --trial 0
se suite positioning --workers 8 --out reports/m2_positioning.md
se table 5 --ruleset v0.9                             # review Table 5, exactly, beside the review's figures
se table 5 --ruleset my_f3_idea.toml                   # the same single shots under your variant
se suite ranged --workers 8 --out reports/m3_ranged.md # archers on three maps, F3 options
se suite phase --workers 8 --out reports/phase_suite.md # all eight phase-suite items, review layouts
se table 8 --equipment f8_die_upgrades                 # an exact table with a variant equipment table
se suite cores --workers 8 --out reports/cores_suite.md # each core and candidate ability, off and on
se suite objectives --workers 8 --out reports/objectives_o1_suite.md # O1: objective scenarios, kill v first
se suite ranged10 --workers 8 --out reports/ranged10_suite.md # 0.10.0 ranged: S1-S6 by bow, package, crit rule
se play src/stamina_engine/data/scenarios/l1_duel_open.toml --as A --log session.jsonl
se play src/stamina_engine/data/scenarios/archer_open.toml --as A --step --answers a.jsonl  # one decision at a time
se load src/stamina_engine/data/scenarios/one_v_three_open.toml --trials 200
se load --session session.jsonl                        # a person's decisions, with seconds
```

### Equipment variants and NPC profiles (M4)

A scenario's `equipment = "f4_shield_1"` swaps the weapon, armor and shield table for a variant in `src/stamina_engine/data/equipment/` (each overlays the packet's table entry by entry; copy one to try your own). `v0_10` is packet 0.10.0's bows and shield, for the `v0.10.0` preset. The other shipped variants are Review F8's (die upgrades, Strength capped at die size) and F4's (a +1/+2 shield, a shield with a Strength requirement); F8's light-weapon discount and F4's two-hander bonus are RuleSet switches (`surcharge.light_exempt`, `defenses.two_hander_bonus`, `defenses.agility_split`).

NPC profiles (`src/stamina_engine/data/profiles/`) configure the tactical agent the way a stat block would: `agent = { kind = "npc", profile = "disciplined_2step" }` commits 2 steps, 3 against a target below half stamina, and focuses fire. `cautious` flees through an exit square (`>` on a map) at half HP and surrenders at a quarter. Fleeing and surrendering aren't in the packet; they're engine end states pending the designer (Assumptions register).

### Objectives (O1)

A scenario on a map can give one side an objective other than downing every opponent, with `[[zone]]` and `[[objective]]` tables (format at the top of `src/stamina_engine/experiments/scenario.py`):
- `reach`: get `count` creatures into a zone;
- `escape`: get `count` creatures off the map through exits (`>`);
- `hold`: control a zone, by a `control` reading (`present`, `uncontested`, `majority`) and a `score` reading (`consecutive`, `cumulative`, `final`) that the scenario must state.

Every objective has a `deadline` round. The fight ends when the objective is done (its side wins, reason `objective:<id>`), fails (the other side wins, `objective_failed:<id>`), or one side is out first (`side_out`). `se run` then also prints the objective's success rate and how fights ended. A zone can be a map letter that no combatant uses (`marker = "H"`), a list of squares or a rectangle.

Agents ignore objectives unless their spec says `objective = "first"` (the default `"kill"` is today's behaviour and the control). `se suite objectives` runs the five objective scenarios (`extraction_3v3`, `breakthrough_3v3`, `hold_hill_3v3`, `hold_hill_final_3v3`, `hold_the_door_1v3`) under both agent families, pursuers in `kill` and in `first`, and reports the paired first − kill difference: if it is near zero, the objective adds nothing a straight fight doesn't already decide. The readings the packet doesn't give are in the Assumptions register; the plan is `sim/docs/OBJECTIVES_PLAN.md`.

#### Setting up an objective scenario that tells you something

The engine measures whatever fight you give it. An objective only produces an insight if the scenario makes the objective hard in the way your question is about. If you put an escape on open ground with the exits in reach, you've measured a footrace. Work through these before trusting a number:

1. **Start from the question, then choose the objective.** Name the rule or finding you're probing, and pick the objective and terrain that put pressure on it. For example:
   - opportunity attacks and reach (F9): a breakthrough through a gap a defender can stand in;
   - focus fire (F6): a lone defender holding a corridor;
   - retreat economics (Review Addendum 2): an escape that has to break contact, with pursuers able to reach the route;
   - stamina banking: a hold scored only at the deadline (`score = "final"`).
2. **Use the current rules.** Name the baseline, `ruleset = "v0.10.0"` (or leave the ruleset out). The `v0.9` preset predates packet 0.9.1, so its extra on-turn purchase moves 1 + odd Agility squares instead of 1 square, and it keeps the opportunity-attack cap. Movement decides most objective fights, so this matters more here than anywhere else.
3. **Do the movement arithmetic.** Under current rules a creature covers its free Movement (5, +1 per odd Agility) plus 1 square per stamina it spends, all on its own turn. It can also move off-turn, at escalating prices. With `se map show <map>`, measure each pursuer's distance to the goal and each denier's distance to the intercept squares.
   - If a pursuer can reach the goal on its first turn before any denier can engage it, the fight is a race decided by initiative.
   - That is a fine thing to measure on purpose, but not by accident.
   - To get a contest, put the deniers between the pursuers and the goal, give the route a chokepoint, or start the goal further away.
4. **Give terrain a job.** Corridors, gaps in a wall, low walls and pillars make position matter. Open ground makes most objectives a matter of speed and numbers.
   - Spread the deniers so that every route passes through someone's reach.
   - Give the deniers a reason to choose between positions, such as two gaps and three defenders.
5. **Set the deadline from the movement arithmetic.** Make it long enough that the objective takes several turns, and short enough that turtling fails. A reach or escape deadline defaults to the round cap.
6. **Choose the hold readings deliberately.**
   - `present` lets a single body hold against any number of enemies.
   - `uncontested` lets one enemy deny the hold by standing in the zone.
   - `majority` rewards numbers.
   - `consecutive` punishes losing the zone even once; `final` lets a side fight elsewhere and arrive late.
   These change the answer, so say which you used.
7. **Balance the straight fight first.** Run the scenario with the pursuers in `kill` mode. If one side wins the straight fight almost every time, the objective has little room to matter. To measure the straight fight, remove the objective (`dataclasses.replace(scenario, objectives=(), zones=())`), or every pursuer in `kill` mode still loses on the objective's deadline. The first hill scenario had the party losing the straight fight 96% of the time, so almost every hold fight ended with one side wiped out and said nothing about the hold. Adjust the sides or the map until the straight fight is roughly even, or until its imbalance is the thing you're studying. Mirroring the rosters is the quickest fix; the shipped 3v3 objective scenarios do that, and the party wins their straight fights 40–47% of the time.
8. **Read how fights ended, not just who won.**
   - Mostly `side_out`: the objective isn't deciding the encounter.
   - Mostly round 1: a race.
   - Mostly `objective_failed` well before the deadline: the pursuers are being wiped out, not outplayed on the objective.
   Then `se trace` a few trials of each kind of ending before you believe the pattern.
9. **Run both agent families, and know their limits.**
   - Scripted pursuers move with free movement only and never buy squares.
   - Tactical pursuers buy up to half their stamina.
   - Deniers of either family attack the pursuer nearest its goal; they don't body-block gaps.
   A result that holds for only one family, or that a blocking denier would plausibly overturn, is about the agents, not the rules.
10. **Compare rules on the same seeds.**
    - `se compare` (or suite rows that share a scenario) gives paired differences.
    - `first − kill` tells you whether the objective matters at all.
    - Comparing RuleSet variants with the pursuers in `first` tells you how a rule changes the objective.

### Abilities, people and load (M5)

A build's cores bring their abilities (`cores = ["barbarian"]` gives it `barbarian_core`), and `abilities = ["heavy_swing"]` adds candidate abilities (`heavy_swing`, `riposte`, `tactical_withdrawal`; Feint waits for contests). The library has the sample fighter's stats with each core (`l1_sample` is the Fighter, `l1_barbarian`, `l1_monk`, `l1_rogue`) and with each candidate alone (`l1_heavy_swing`, `l1_withdrawal`, `l1_riposte`). How each one reads where the packet is silent is in the Assumptions register; `src/stamina_engine/abilities/cores.py` shows how one is written. Strain starts at 0 every fight, so a fight's results are the best case for a day of several.

Engine agents pass every ability window unless their spec says `abilities = "use"`, so results without abilities stay comparable; the heuristics they then follow are documented in `src/stamina_engine/agents/ability_policy.py`. `se suite cores` prices each ability by turning it off and on over the same seeds, in duels and one against three, and plays the four cores against each other.

`se play scenario.toml --as ID` lets you play one combatant at the keyboard; everyone else keeps the scenario's agent, and the dice are trial N's, so the fight is comparable with the engine's. Each prompt lists the options with their prices (`?` shows the answer formats). Every decision is timed, and `--log` writes the session as JSON lines. `se load` reports decision load (Review F11): requests per creature-round by kind, their option counts, how many are non-trivial, how often they did something, dice per attack, and, from session logs, seconds per decision.

#### Agents for ranged fights (0.10.0)

By default, engine agents play ranged fights simply:
- the tactical target reacts to a shot only for this shot's blocks;
- the tactical archer aims as if the target will stay put;
- scripted pursuers never buy movement, and nobody closes in off-turn.

These agent spec fields make them play the reactions 0.10.0 allows. They're off by default so earlier results reproduce; report both agent families, as for any positional result.

| Field | Agents | What it does |
|---|---|---|
| `buy = "keep_steps"` or `"any"` | scripted, tactical | Buy on-turn squares to attack this turn. `keep_steps` buys only if the attack keeps as many steps; `any` (the tactical default) if at least one is left |
| `close = "off_turn"` | tactical | In the window right before its turn, buy off-turn squares so its free movement reaches the target |
| `reaction = "position"` | tactical | A reaction also values where it ends: contact with the shooter (it has to pay to leave, or take an opportunity attack), plus `approach_weight` per square closer (default `"0"`; try `"1/2"` or `"1"` for sensitivity) |
| `aim = "reaction"` | tactical archer | Aim counts the target's best reaction to each roll: cover, closing in, backing off |

For example: `agent = { kind = "tactical", aim = "reaction", reaction = "position", close = "off_turn", buy = "keep_steps" }`.

#### The 0.10.0 ranged scenarios (`se suite ranged10`)

The library has the simulator requirements' scenarios, each on 0.10.0 with the tactical agents' ranged behaviors on (`approach_weight = "1"`: a square closer is worth what buying it on-turn costs):

| Scenario | What's in it |
|---|---|
| `s1_archer_v_melee` | Longbow archer v sword-and-board fighter, open ground (`range_open`), 8 apart |
| `s2_low_walls` | The same with low walls near the fighter's path (`range_walls`) |
| `s3_focus_fire` | Two archers and a fighter v a fighter and a caster near cover (`range_party`) |
| `s4_two_archers` | Two archers 8–10 squares from a caster and a shielded knight in heavy armor |
| `s5_archer_v_plate` | One archer v the heavy-armor knight, 8 apart |
| `s6_archers_v_beast` | Two superheavy archers v an armored beast, 10 apart |

`se suite ranged10` runs them by distance, bow, melee build, reaction package (`v0.10.0` or `v0.10.0-cover-only`), crit rule (A, C′, C) and agent family. It ends with a sensitivity group for `approach_weight`.

Every fight row (`se run --out`) also carries the ranged measures:
- shots by band and critical dice on shots;
- HP the shots took per stamina they cost;
- reactions by kind (close, cover, back, shift) and their cost;
- point-blank opportunity attacks provoked and made;
- the first melee round;
- each creature's round down, and whether a side was down by round 2;
- the turn-1 shooter's spend and reserve.

`metrics.ranged_measures` documents each one.

Caveats:
- **Over-budget archers.** The archers other than the longbow's (`l1_archer_shortbow`, `l1_archer_warbow`, `l1_archer_superheavy`) are over the level-1 Expertise budget, as the design study's were, so each bow is compared at the attributes it wants.
- **A stand-in beast.** S6's `l1_beast` has armor 4 (the `s6_beast` table) and HP 14: the engine has no stat blocks, and the size rule is shelved.

#### Playing one decision at a time (`se play --step`)

A chat can't answer prompts, so `--step` plays a fight from an answers file, one decision per command:

```bash
se play scenario.toml --as A --step --answers a.jsonl              # print the waiting decision
se play scenario.toml --as A --step --answers a.jsonl --answer "s F"  # answer it, print the next
```

- **How it works.** Each command replays the trial from its seed with every answer in the file, then stops at the first decision with no answer and prints it as JSON.
  - Nothing else is kept between commands, so the same scenario, trial and answers always reach the same request.
  - Use `--trial N` for other dice. Repeat `--as` to play several combatants from one file, answering in the order they're asked.
- **What the decision says.** `decision` has:
  - `kind`, `who` and `context` (where the battle is);
  - `observation`: everyone's position, HP, stamina, defenses, armor and weapon, plus your own counters (`actions_this_turn` for the surcharge, `off_turn_costs` for the escalation);
  - `fields`: the request's options with their prices. A reaction to a shot (`react`) lists every reachable square with the cover, total to block and defense you'd face there (`cover_after`, `damage_after`, `defense_after`).
  - `answer_help` (the answer format) and `text` (the same prompt `se play` shows).

  The report also has `map` with a `legend`, and `events_since_last_decision`.
- **Answers.** An answer is the line you'd type at `se play` (`s F`, `2`, `m 4,3`, `p`).
  - `--answer` appends it to the file only if the engine accepts it.
  - A rejected answer is reported with the reason and isn't written. A bad line already in the file is reported by its line number; delete it.
  - The file holds one JSON object a line, `{"who": "A", "kind": "aim", "answer": "2"}`. `who` is checked against the decision.
- **Exit codes.** 10: a decision is waiting. 0: the fight is over (the report has the winner). 11: an invalid answer.
- **The session log.** With `--log session.jsonl`, the command that ends the fight writes the session log `se load --session` reads. Its seconds are empty, since a chat's timing isn't a person's.

`--rounding half-even` reproduces the review, whose simulator used Python's `round()`. The packet's rounding is half up, which changes three Table 1 cells and Table 8's 2.125 (see the Assumptions register).

### Fights

A **scenario** names the combatants, their builds and agents, the RuleSet, the round cap, trials and seed. The format is documented at the top of `src/stamina_engine/experiments/scenario.py`; the examples are in `src/stamina_engine/data/scenarios/`. Agents are `alpha`, `fixed:2`, `reserve:5`, `chipkill`, `lookahead` or `never`, or a table such as `{ commit = "chipkill", target = "lowest_stamina", w = "3" }`; they block with the exact solver. Add `abilities = "use"` to a table to have it use its abilities.

- `se run` prints win rates with 95% Wilson intervals, rounds, first-mover rate, winner-untouched rate, the loser's final HP, deaths and decisions per round, then the provenance stamp.
- `se compare` runs the same scenario under two RuleSets **on the same seeds** and reports each difference with a paired 95% interval. It is the cheapest honest way to test a rule change.
- `se sweep` runs scenarios × RuleSets × agent pairings (format at the top of `src/stamina_engine/experiments/sweep.py`); RuleSets in a sweep share seeds too.
- `--out DIR` writes Parquet tables (`runs`, `fights`, `attacks`, `decisions`); every row carries the run id and RuleSet digest, and `runs` holds the full stamp, the RuleSet TOML and the scenario TOML. Read them with Polars or pandas.
- Any fight re-runs alone: its seed is in the `fights` table, and `run_trial(scenario, trial)` replays it. `se trace scenario.toml --trial N` prints that fight's events with the board at each turn; read one before trusting a surprising number.

### Maps and positioning (M2)

A scenario with `map = "open_12x12"` (a library map in `src/stamina_engine/data/maps/`, or a `.txt` path) is fought on a grid; without one, everyone is adjacent, as in M1 and the review. Map legend: `.` floor, `#` wall, `=` low wall or crate, `o` pillar; other letters and digits are spawn markers. Each combatant gets `spawn = "A"` (a marker) or `spawn = [x, y]`; a counted group takes a list. `map_text = """..."""` puts the map inline.

On a grid, movement is square by square: free movement, then extra purchases (1 stamina, flat) on your turn; off-turn purchases (escalating) in the window after every turn. Leaving a threatened square provokes an opportunity attack from each enemy threatening it unless the mover pays to avoid it. Every reading the packet leaves open (corners, reach lines, what threatens, window order, the per-square cap and the F9/F10/F14 options) is a switch in the Assumptions register in `sim/docs/ENGINE_PLAN.md`.

Agents on a grid:
- **Scripted** (`alpha`, `chipkill`, ...): approach their target with free movement, attack if they can, never move off-turn. Add `avoid = "worth_it" | "always" | "never"` and `oa = "max" | "never"` to a table spec.
- **Tactical** (`"tactical"`, or `{ kind = "tactical", commit = "fixed:2", target = "lowest_stamina" }`): picks squares by how many enemies could engage it, keeps reach-weapon spacing, retreats off-turn when two or more could engage it (`retreat_engaged`) or when engaged with low stamina (`low_stamina = "1/3"`), and values avoidance exactly.

At range (M3), a creature with a bow shoots enemies within its long range that aren't in total cover. Cover is the 5e corner method; the target may dive for cover with off-turn movement after the roll; a shooter within an enemy's reach provokes from every enemy threatening it. Scripted shooters take `aims = 3` (a spec field) and stand; tactical archers choose aims by exact expected value (looking one enemy reply ahead), step out of reach, ready a quick-draw blade between turns and dive. Builds with several loadouts (`l1_archer`: `bow` and `blade`) switch with the packet's drawing costs.

Report positional results for both families: agent behavior can drive a result as much as the rules do. The variant switches Phases 4 and 5 ask about:

```toml
[ruleset]
base = "v0.10.0"
opportunity = { cap_rule = "weapon_base" }       # F9 option 1: bring back a cap of weapon base + odd FIN
# opportunity = { avoid_price = "attacker_cap" } # F9 option 2 (needs a cap: base = "v0.9", or option 1)
# opportunity = { avoid_track = "off_turn" }     # F9 option 3 (or "off_turn_only")
# opportunity = { per_square_cap = true }        # v0.9's optional rule (needs a cap)
# opportunity = { avoid_debt = true }            # F14: avoidance paid from the next recovery
# movement = { extra_squares = "agility" }       # v0.9's 1 + odd AGI squares a purchase (F10 option 1 is now the rule)
# movement = { extra_cap = "free_movement" }     # F10 option 2
# off_turn = { order = "descending_initiative" } # F14: who moves first after a turn
# defenses = { ranged_mode = "dodge_folded" }    # F3 option 1: RD gains even Agility
# blocks = { ranged_flat = 2 }                   # F3 option 2: flat ranged perfect blocks
# ranged = { aim_mode = "precision" }            # F3 option 3: aim widens crit range instead
# ranged = { bands = "minus_d6" }                # F11 (b): range bands as -1d6 / -2d6
# crit = { aim_dice_can_crit = false }           # v0.9's TODO (0.10.0 rules it false)
# ranged = { defense_timing = "declaration" }    # Melee vs Ranged Defense from where the target was
# ranged = { reaction_purchases = 1 }            # a reaction to a shot buys at most 1 purchase
# ranged = { swap_single_purchase = true }       # the defense swap only counts within one purchase
# ranged = { crit_in_limit = true }              # the critical bonus counts toward the aim limit
# crit = { aim_dice_can_crit = true, aim_dice_widen = false, per_shot_cap = 1 }  # crit rule C'
```

From Python:

```python
from stamina_engine.experiments.scenario import load_scenario
from stamina_engine.experiments.runner import run_scenario
from stamina_engine.experiments.metrics import summarize
from stamina_engine.experiments.sweep import compare
from stamina_engine.analysis.strike import mirror_strike   # the opening full strike, exactly
from stamina_engine.analysis.retreat import escape, table  # Addendum 2 retreat costs, exactly
from stamina_engine.analysis.one_round import Archer, Target, solve_round  # one round of shots, exactly

s = load_scenario("src/stamina_engine/data/scenarios/l1_duel.toml")
print("\n".join(summarize(run_scenario(s, trials=500).fights).lines()))
```

The core pieces for single exchanges:

```python
from stamina_engine.rules.ruleset import preset, load_ruleset   # presets: "v0.9" ... "v0.10.0", the v0.10.0-* packages, "review-candidate", "review-sim"
from stamina_engine.model.build import load_build        # library builds in src/stamina_engine/data/builds
from stamina_engine.model.derive import derive           # Build x RuleSet -> CombatProfile
from stamina_engine.rules.pricing import Pricing, Trackers
from stamina_engine.rules.block_solver import best_block, cheapest_zero_injury
from stamina_engine.analysis import dist                 # exact (total, crit dice) distributions
from stamina_engine.provenance import collect            # the stamp to quote with results

rules = preset("v0.10.0")                               # the baseline
fighter = derive(load_build("l1_sample"), rules)
Pricing(rules).melee_attack(base=2, steps=3).total      # 9
print(collect(rules).text())
```

`review-sim` reproduces the review's simulator, quirks included; use `v0.10.0`, the current packet (or your variant on it), for design questions. `uv run pytest` takes under a minute; `uv run pytest -m slow` adds the full-count oracle parity runs.

## Trying a rule change

Never edit the baseline: not the v0.9 components, not the presets, not `rules/`. The baseline is what you compare against, and only the designer changes it. Try ideas as **new, named variants** instead. That keeps the old and new rules side by side in one run, and keeps every result honest about which rules produced it. Pick the lightest of three tiers that fits:

1. **Numbers or an existing variant: no code.** Override parameters in a RuleSet file:

   ```toml
   # steep.toml
   [ruleset]
   base = "v0.10.0"
   name = "steep-surcharge"
   surcharge = { slope = 2 }
   blocks = { slope_num = 1, slope_den = 2 }   # perfect blocks 1, 1, 2, 2, 3...
   ```

   Run with `se table 8 --ruleset steep.toml`, or `load_ruleset("steep.toml")` in Python. `sim/docs/ENGINE_PLAN.md` lists every component and its parameters; the source is in `src/stamina_engine/rules/components/`.

2. **A new mechanism that fits a component: one plugin file.** Write a variant class in a file outside the package, registered under a new name starting with `exp_`. The working example is `examples/exp_quadratic_surcharge.py` with `examples/exp_quadratic_surcharge.toml`:

   ```python
   from dataclasses import dataclass

   from stamina_engine.rules.components.surcharge import SurchargeRule
   from stamina_engine.rules.registry import register


   @register("surcharge", "exp_quadratic")
   @dataclass(frozen=True)
   class QuadraticSurcharge(SurchargeRule):
       slope: int = 1

       def surcharge(self, prior_actions: int) -> int:
           return self.slope * prior_actions * prior_actions
   ```

   ```bash
   se table 8 --plugin examples/exp_quadratic_surcharge.py --ruleset examples/exp_quadratic_surcharge.toml
   ```

   In Python, call `load_plugin("my_idea.py")` (from `stamina_engine.rules.plugins`) before loading a RuleSet that names its variants. Subclass the kind's base class (`CritRule`, `BlockRule`, `DefenseRule`...): it supplies the methods to implement and the packet citations. Taking a name that already exists is refused, so a plugin can't quietly replace a rule.

3. **A change to a procedure or timing** (a new reaction window, a new kind of action): this needs engine code. Work in your clone, on a branch named `exp/<topic>`. Run the baseline from the same commit before your change, so both sides differ only by your diff. Say in the report that the idea needed a procedure change; Claude Code can then add a component for it, so the next idea like it fits tier 2.

If the designer wants to keep an idea, Claude Code moves it into the engine as a proper component with tests. Ideas the designer rejects are deleted, or kept for parity only if a published result depends on them.

## Reporting results

Every `se` command prints a provenance stamp after its result; in Python, `collect(rules, plugins).text()` gives the same lines. For example:

```text
RuleSet exp-quadratic-surcharge 509a51df050e
Code git m0 (f57367eb5d62, clean); source ee6c5479eb85; stamina-engine 0.0.1
Plugin exp_quadratic_surcharge.py 9460148edc70: surcharge/exp_quadratic
```

- **RuleSet** is the rules configuration: which variants, which parameters. Parameters left at their default don't enter the digest, so a digest stays the same as the engine gains new switches. Digests stamped at tags `m0`–`m5` hashed every parameter and differ from today's for the same rules: v0.9 was `89e49ba8c42d` at `m5` and is `3bf6fc070dbf` now.
- **source** hashes the engine's code and data tables. It identifies the implementation even outside git, in an unpacked copy or with uncommitted edits. "uncommitted changes" means that copy's code differs from the commit shown.
- **Plugin** lines hash each plugin file.

Provenance lives in the results file, not the reply:

- **Results file:** save each investigation's full results (tables, every number with its whole stamp, trial counts, 95% confidence intervals, and the limitations that apply) to a results file. Attach plugin and RuleSet files so anyone can rerun it. Write-ups for the designer go in `sim/reports/`; working results can be project docs. The report, not the branch, is what lasts.
- **Replies and design docs:** cite only the few numbers that carry the argument, each with a short tag such as `[rs:3bf6fc, n=2000, ±2%]`, and point to the results file for the rest.

## Sharing changes

A chat can push only if the Claude GitHub App has access to this repo.
- With access: push experiments to `exp/<topic>` branches, never to `main`. Small, safe changes (scenarios, maps, builds, reports) can go to `main`. Engine procedure and rule component changes go on a branch with a pull request.
- Without access: hand over the report, plus the plugin or RuleSet files or a patch, for Claude Code or the designer to commit.

## Rules for chats

- Read `CLAUDE.md` at the repo root before changing anything. Its ground rules apply to chats too.
- Never change what a rule means. Experiments are new named variants, never edits to the baseline. If the packet is unclear, flag it and add it to the Assumptions register in `sim/docs/ENGINE_PLAN.md`.
- Every simulated number is traceable: full stamp in the results file, short tag in prose (see Reporting results).
- Run the engine only to test a stated claim, and name the limitations that could undercut the result (see Purpose and What the engine doesn't capture).
