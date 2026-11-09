# O1 implementation plan: zones, Reach, Escape and Hold

*Status: proposal (2026-11-07). Phase O1 of [OBJECTIVES_PLAN.md](OBJECTIVES_PLAN.md). Paths are relative to `sim/src/stamina_engine/` unless they start with `sim/`. This changes engine procedures, so it goes on a branch (`objectives/o1`) with a pull request.*

## Goal

A scenario can give one side an objective other than downing every opponent:
- **Reach:** get N creatures into a zone.
- **Escape:** get N creatures off the map through exits.
- **Hold:** control a zone for some rounds, or at the deadline.

The fight then ends when that objective is met or fails. Agents can pursue or deny it, and the results report how often it succeeded and how each fight ended.

O1 adds no new action types, no new RuleSet components and no new rules readings beyond the ones a scenario states explicitly. Every fight without an objective keeps an identical event log.

## What already exists and gets reused

- **Exits and fleeing.** `>` squares, `Battlefield.is_exit`/`exits()` (`grid/battlefield.py:102`), `StateOps.flee` (`engine/stateops.py:224`), and the `Flee` answer with `TurnCommand.can_flee`. Escape needs nothing new for movement.
- **Spawn markers.** Any letter in a map that no combatant uses is plain floor, and its squares are collected in `Battlefield.spawn_list`. A zone can name a marker, so zones can be drawn on the map without a second layer.
- **The fight-end hook.** `Battle.check_end` (`engine/battle.py:102`) is already called after every injury, after a flee or surrender, and before round 1. Every loop already stops on `b.outcome is not None`.
- **Agents.**
  - The tactical agent's `_approach` (`agents/tactical.py:350`) and `Board.route`/`engagers` (`agents/grid_view.py`) path to any square and score it.
  - `_leaving` (`agents/tactical.py:146`) already routes to the nearest exit and flees.
  - The scripted `approach` (`agents/scripted.py:298`) moves toward a target.
- **Metrics.** `fight_row` already records `reason` and `fled:{team}`. `summarize` builds Wilson intervals with `stats.wilson`.

## Scenario format

The scenario format gains two new table arrays, both whitelisted in `scenario_from_toml` and written back out by `scenario_to_toml`:

```toml
[[zone]]
id = "hill"
marker = "H"            # every square with this map letter; or
# cells = [[5, 4], [6, 4]]
# rect = [5, 3, 7, 5]   # x0, y0, x1, y1, inclusive

[[objective]]
id = "take_hill"
kind = "hold"           # reach | escape | hold
team = "P"              # the side pursuing it; the other side denies it
zone = "hill"           # reach and hold
who = ["P0", "P1"]      # optional: only these creatures count (default: the whole team)
count = 2               # reach and escape: how many must make it (default: all who count)
control = "uncontested" # hold: present | uncontested | majority  (required, no default)
score = "consecutive"   # hold: consecutive | cumulative | final   (required, no default)
rounds = 2              # hold with consecutive or cumulative: rounds of control needed
deadline = 8            # the round by whose end it must be done (required for hold;
                        # optional for reach and escape, where it defaults to the round cap)
```

**Validation** (raises `ConfigError`):
- objectives need a map and exactly two teams;
- O1 allows one objective per scenario;
- zone squares must be in bounds and walkable;
- `who` must name members of `team`;
- `count` can't exceed the number of creatures who count;
- escape needs at least one exit;
- `deadline` must be at most `round_cap`;
- `control` and `score` must be given for hold.

Because `control` and `score` are required, no hold rule ever gets a silent default (ground rule 1).

## Engine changes

1. **Specs: new module `model/objectives.py`.** Frozen dataclasses `Zone(id, cells)` and `ObjectiveSpec(...)` matching the TOML. It also holds pure helpers:
   - `in_zone(state, zone, team)`, which counts active creatures only;
   - `controls(state, spec, field)`, which implements the three control readings.
2. **State.**
   - `BattleState` gains `objectives: dict[str, ObjectiveState]`, empty by default.
   - `ObjectiveState` holds `progress`, `streak`, `reached: frozenset[str]` and `status` (`open`, `done` or `failed`).
   - Only new StateOps methods write it: `objective_progress`, `objective_reached` and `resolve_objective`. Each emits an event; the stub `advance_control` is the model.
   - `validate()` checks the invariants: progress within bounds, and a resolved objective never reopens.
3. **Events: three new types in `engine/events.py`.**
   - `ObjectiveReached(id, who, round)` for reach.
   - `ObjectiveProgress(id, progress, needed, round)` for hold.
   - `ObjectiveResolved(id, status, team, round)`.
   They are emitted only when a scenario has an objective, so pinned log hashes don't move.
4. **New procedure module `engine/procedures/objectives.py`,** with `cites = ("Packet: Running the Game",)`. Its `evaluate(b, hook)` runs at named hooks:

   | Hook | Where | Checks |
   |---|---|---|
   | `after_move` | end of `move()` in `engine/procedures/movement.py`, on and off turn | reach: creatures standing in the zone are marked reached |
   | `after_leave` | the existing `check_end` call after Flee and Surrender | escape: success once `count` creatures have fled; failure once too few can still make it |
   | `after_injury` | the existing `check_end` call in `lose_hp` | reach and escape: failure once too few active creatures who count remain |
   | `end_of_round` | new call in `run_battle` after `play_round` | hold: score control by the `score` rule; every kind: failure at `deadline` |

5. **Fight end: `Battle.check_end`** evaluates the objective first and side-out second.
   - Escape depends on this order: when the last fleer leaves, the side is "out", and checking side-out first would hand the chasers the win.
   - Success makes the objective's team the winner, with reason `objective:<id>`.
   - Failure makes the other team the winner, with reason `objective_failed:<id>`.
   - Side-out stays live, with reason `side_out`, so wiping out the other side still ends the fight. The reason column shows which way each fight was won.
   - `Battle.__init__` and `experiments/runner.battle_for` pass the scenario's objectives through.
   - `BattleResult` gains `objective: str | None`, the final status.
6. **Observation.**
   - `Observation` gains `objectives: tuple[ObjectiveView, ...] = ()`, built in `engine/observe.py`.
   - `ObjectiveView` holds the spec fields, the zone squares, progress, streak, reached and status.
   - Objectives are public information (engine convention).
   - Decision records don't hold observations, so the records are unaffected.

## Agents

Each agent gets a new spec field `objective = "kill" | "first"`, which `make_agent` accepts. It defaults to `kill`, today's behaviour, which is the control. An agent's role follows from its team: **pursuer** if its team holds the objective, **denier** otherwise.

**Tactical agent (`agents/tactical.py`), `first` mode.** A goal layer runs before target choice in `turn_command`:
- **Reach or escape pursuer.**
  - Routes to the nearest goal square (a zone square or an exit), buying movement when it can still afford a 1-step attack if it gets caught.
  - Flees as soon as `can_flee` and it counts for escape.
  - Attacks only what is in reach after moving.
  - Already-reached creatures switch to screening: they stay in or near the zone and attack.
- **Hold pursuer.**
  - Moves into the zone if it isn't there, and otherwise stays.
  - Moves, attacking squares and off-turn retreats are filtered to zone squares while leaving would cost control under the scenario's `control` rule.
  - Targets enemies in the zone first, then whichever is closest to it.
- **Denier.**
  - Targets the pursuer closest to its goal: distance to the zone or to the nearest exit, with ties broken by the existing target mode.
  - For hold with `uncontested` or `majority` control, it moves into the zone to contest.
  - For escape, it approaches the fleer nearest an exit.

**Scripted agent (`agents/scripted.py`), `first` mode.** It approaches the goal square instead of its target, attacks whatever is in reach, and flees from an exit when it counts for escape. Deniers use `target = "objective"`, a new target helper that picks the pursuer closest to its goal.

**NPC profiles.** The profile schema (`agents/profiles.py`) gains an optional `objective` field that is passed through to the tactical agent. No profile files change.

**Human CLI (`se play`).** The board marks zone squares, and the status line shows the objective's progress and deadline. No new answers are needed.

The listed and random-legality agent needs no changes: O1 adds no new answer types.

## Metrics and report

- **`fight_row` gains:**
  - `objective`: done, failed, open or none;
  - `objective_round`;
  - `surrendered:{team}`, since `fled:{team}` already exists. This fills the gap ENGINE_PLAN:395 promised.
- **`Summary` gains:**
  - the objective success rate (Wilson);
  - a breakdown of how fights ended: objective, objective failed, side-out or round cap.
  Both are printed only when a scenario has an objective.
- **New `experiments/objectives_suite.py` and `se suite objectives`.** Each scenario runs under both agent families (scripted, tactical) and with the pursuers in `kill` mode and in `first` mode. Deniers are always in `first` mode.
- **Report columns:**
  - pursuer success rate with CI;
  - the `first − kill` difference with CI;
  - the reason breakdown;
  - median rounds;
  - deaths per fight.
  The `first − kill` column is the "does this objective matter?" test.

## New scenarios and maps (`data/scenarios`, `data/maps`)

| Scenario | Map | Setup | Tests |
|---|---|---|---|
| `extraction_3v3` | `extraction` (exits 24 squares away, past a low wall with one gap) | The party starts engaged with the NPC melee and must get 2 of 3 out; deadline 6 | Addendum 2 retreat economics in a team fight; F14 |
| `breakthrough_3v3` | `breakthrough` (a wall line with two gaps, a defender standing in each; the zone is beyond one turn's movement) | Attackers need 2 of 3 to reach the zone; deadline 8 | F9 opportunity attacks and reach at a line |
| `hold_hill_3v3` | `hill` (a central `H` zone ringed by low walls open on four sides) | Attackers must hold `uncontested`, `consecutive`, 2 rounds, deadline 10. A copy uses `final` at round 6 | Banking stamina against spending it; F6 focus fire on whoever stands in the zone |
| `hold_the_door_1v3` | `corridor` (existing), with the corridor mouth as the zone | The lone defender must hold `present` and `final` at round 4 | F6 and F9: whether a chokepoint ever lets one creature hold |

Builds come from the existing library. The 3v3 sides are mirrored (sample fighter, duelist and archer each; the party is tactical, the NPCs use `disciplined_2step`), so the straight fight is close to even. Every scenario uses v0.9.1 movement (`movement.extra_squares = "one"`). They were rebuilt on 2026-11-08 by the setup checklist in `USAGE_FOR_CHATS.md`; the first versions put goals within one turn's reach on open ground.

## Assumptions register (new and updated rows in `sim/docs/ENGINE_PLAN.md`)

| Row | Engine default | Switch | Status |
|---|---|---|---|
| When a fight ends (updated) | The scenario objective is checked first, then side-out, then the round cap. The reasons are `objective:<id>`, `objective_failed:<id>`, `side_out` and `round_cap` | scenario `[[objective]]` | engine convention |
| Who counts in a zone | Active creatures only. Incapacitated, fled and surrendered creatures don't count | — | pending designer |
| Zone control | Stated per scenario. There is no default | objective `control` | pending designer |
| Hold scoring | Stated per scenario, and scored at the end of each round | objective `score`, `rounds`, `deadline` | pending designer |
| Reaching a zone | A creature counts once it stands in the zone after any of its moves, on or off turn. Passing through mid-path doesn't count. Once counted, it stays counted | — | engine convention |
| Escape | Only through exits (the existing fleeing row). It fails once too few creatures who count are still active to make `count` | objective `count`, `who` | engine convention |
| Objective failure | The other team wins (two-team scenarios only) | — | engine convention |
| Objectives as information | Public: every creature sees zones, progress and deadlines | — | engine convention |

## Tests

- **Golden (`tests/golden/test_objectives.py`)**, hand-built small battles with scripted dice:
  - escape succeeds on the Nth flee;
  - escape fails when too many are downed;
  - escape counts before side-out when the last fleer leaves;
  - a reached creature stays counted after it leaves the zone;
  - a hold streak resets when the zone is contested under each `control` value;
  - `final` scoring happens only at the deadline;
  - a deadline failure produces `objective_failed`.
- **Properties:**
  - StateOps `validate` holds with objectives on;
  - random-play legality on the new maps (the broker never rejects an engine agent);
  - scenario TOML round-trips with zones and objectives;
  - validation errors for each bad config above.
- **Determinism:** every hash pinned in `tests/golden/test_determinism.py` and the grid-battle pins is unchanged, the M1 parity lockstep is unchanged, and the RuleSet digest is unchanged. New pins are added for one seeded fight of each new scenario.
- **Traceability:** the new procedure module cites "Packet: Running the Game", and `tests/properties/test_traceability.py` passes.

## Done when

- `se suite objectives` runs all four scenarios across both agent families in `kill` and `first` modes, and writes its report to `sim/reports/`. The report records the digest, the switches, trial counts and CIs.
- All earlier logs and digests are unchanged.
- The tests above pass, and `mypy --strict`, `ruff` and `pytest` are green.
- `USAGE_FOR_CHATS.md` documents the `[[zone]]` and `[[objective]]` tables and the suite.
- The scenario docstring and the Assumptions rows are updated.
- The M7 row in ENGINE_PLAN moves from proposed to adopted, once the designer agrees.

If `first` doesn't beat `kill` in some scenario, or deniers can always win by killing, that is a design finding (or an agent-quality finding) to write up and flag, not to tune away. Tag the merge `o1`.

## Build order (small commits on the branch)

1. Specs, scenario parsing, validation and round-trip, with no engine behaviour yet.
2. State, StateOps, events, the evaluation hooks and the `check_end` ordering, plus the golden tests.
3. Observation, then tactical and scripted `first` modes and the `objective` target helper.
4. Metrics fields and the summary.
5. Maps and scenarios, the suite and the CLI wiring.
6. Docs (the Assumptions rows, USAGE_FOR_CHATS, the scenario docstring), the report, the PR.

## Not in O1

These are left out of O1:
- several objectives per scenario, secondary objectives and graded outcomes (O2);
- morale and breaking (O3);
- objects, interacting and carrying (O4);
- escort, waves, asymmetric pairs and capture alive (O5);
- map-edge exits, which stay `>` squares only.
