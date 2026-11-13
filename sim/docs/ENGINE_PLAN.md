# Rules Engine Plan (v0.9 fixes)

Initial plan for creating a TTRPG rules simulator to aid in design.

## Purpose and scope

Build a Python rules engine that can run every experiment in the fix order (Phases 0–8) on a real 5 ft grid, switching rule variants from config rather than code. It is a measuring instrument for the design, not a playable product: the only interactive front end is a command-line agent used to measure decision load (F11).

| Fix phase | Questions the engine must answer | Capability it needs |
|---|---|---|
| 0 Assumptions | How much do stamina visibility, aim-dice crits and initiative ties move results? | Each as a rule switch; agents that respect hidden information |
| 1 Exchange engine (F1, F2, F8 principle) | Attack vs full-block cost by k; full strike from full; r by level | Exact exchange calculators; duel runner; crit, surcharge and block-slope variants |
| 2 Resource formulas (F5, F7, H-2) | Where the level bonus goes; how HP feeds max stamina | Formula variants for HP, max stamina, recovery, strain; L1/L30/L99 build library |
| 3 Focus fire (F6) | Does 1v3 still end in 1–2 rounds once the defender can move and retreat? | Team battles on a grid; per-attacker block-reset and free-retreat variants |
| 4 Positioning (F9, F10, F14) | Can reach weapons threaten; does cheap extra movement erase range; does off-turn order matter? | Pathing, per-square OA triggers, avoidance, off-turn windows with ordering variants |
| 5 Ranged (F3, H-1) | Unshielded targets vs arrows; diving for cover; Dodge folded into RD; aim as damage or precision | Line of sight and cover, range bands, dive reactions, point-blank OAs, ranged block-cost variants |
| 6 Equipment (F4, F8) | Shield value, two-hander defense, light vs heavy weapon niches | Swappable weapon, armor and shield tables; armored-vs-unarmored and efficiency reports |
| 7 Content gaps (F13, H-4, H-6) | Class-core pricing; can control effects be resisted; NPC commitment as the lethality dial | Ability hooks, strain and overage, System Shock, NPC profiles |
| 8 Load and text (F11) | Prompts and arithmetic per round | Decision log with option counts; human CLI agent with timing |

Out of scope until a phase needs it: spell lists, skill checks, advancement beyond derived numbers, out-of-combat rules, any graphical interface.

## What the first simulator lacked

The review's simulator got the exchange math right but could not see space, so every finding about movement, cover, reach and focus fire was either untested or tested with a stand-in.

| Gap in the first simulator | Consequence in the review | How this engine closes it |
|---|---|---|
| No grid | 1v3 ran all-adjacent with no movement; F9 and F10 were argued from arithmetic | 2D square grid with walls, cover objects, reach and pathing |
| 1-D distance with a crude kite | The archer scenario could not test kiting, cover or flanking | Real geometry; archer agents that seek cover and spacing |
| Diving for cover tested statically | No measure of how often a dive is available or what it costs | Dive reactions that search reachable squares for cover |
| Fights run to incapacitation, no retreat or surrender | "Rounds" was an upper bound; GM-1 (NPCs value survival) untestable | Retreat, surrender and flee-the-map as end states, driven by NPC profiles |
| No abilities or strain | Class cores priced only by argument (F13) | Ability hooks with strain and overage costs |
| TODO rules hard-coded as assumptions | Results can't show how much each assumption matters | Every assumption is a named switch, stamped on each result |
| No decision log | F11's prompt counts were estimated by hand | Every decision logged with its option count and, for humans, its time |

**Carry over unchanged:** the exchange rules as verified against every packet example; the five scripted commitment policies (alpha, fixed k, reserve 5, chip-kill, one-ply look-ahead); the defender's valuation of 3 stamina per HP, checked at 1.5 and 6; and the review's tables as parity targets. Its code (`tests/oracle/sim.py`, `experiments.py`, `variants.py`, `grid.py`) is the parity oracle; see Verification.

## Engineering principles

1. **Code reads like the rulebook.** Each procedure mirrors the packet's numbered steps and names the packet section and ledger ID it implements, so a rules change maps to one function.
2. **One price list.** Every stamina cost comes from a single `Pricing` service. Agents use it to plan and the engine uses it to charge, so what an agent expects to pay is always what it pays.
3. **Variants are components, not branches.** Each Mechanism open or Numbers placeholder rule the fix order touches is a swappable component chosen in config. No `if ruleset == ...` anywhere in procedures.
4. **One way to change state.** All mutation goes through `StateOps`, which checks invariants (stamina within 0 and max, max recomputed when HP changes) and emits a typed event. Telemetry, replay and debugging come from that log for free.
5. **The engine never decides for a creature.** Every choice is a typed decision request answered by that creature's controller, human or AI.
6. **Deterministic.** Seeded random streams per battle; the same seed and config produce the same event log, byte for byte. Dice can be scripted for tests.
7. **Exact where possible, sampled where necessary.** Single-exchange questions (block costs, full-strike lethality, r) are computed from exact distributions; only whole fights use Monte Carlo.
8. **Plain, typed Python.** Python 3.12, frozen dataclasses, `mypy --strict`, `ruff`, `pytest` with `hypothesis`. The engine and its CLI use only the standard library, so a checkout runs with nothing installed (a chat may not reach PyPI); pyarrow, optional, writes Parquet results, and the property tests skip without `hypothesis`. No game framework.

## Architecture overview

Data files configure rules, builds and maps; the engine runs procedures that ask agents for every choice; experiments read the event log.

```text
                 data/  (TOML rule sets, builds, equipment, maps, scenarios, NPC profiles)
                   |                        |                         |
                   v                        v                         v
   rules/ (RuleSet components,      model/ (Build ->           grid/ (terrain, LOS,
   Pricing, block solver)           CombatProfile via RuleSet)  cover, threat, pathing)
      |            \                        |                         |
      v             \_______________        v        _________________/
   analysis/                        \-> engine/ <---/        <---->  agents/
   (exact exchange tables,              (timeline, procedures,       (answer every decision:
    r-band checker)                      nested timing windows,       scripted, tactical, search,
      |                                  StateOps: sole mutator)      NPC profiles, human CLI)
      |                                      |
      |                                      v
      |                                  events (typed, append-only log)
      |                                      |
      v                                      v
   experiments/ (scenarios, sweeps, metrics, phase suite, reports: Parquet, tables, plots)
```

Only the engine changes battle state; the two-way arrow is the decision loop, where the engine sends a request and the creature's agent answers it. The layers depend downward only. `rules/` and `analysis/` never import `engine/`, so the exact calculators stay usable without a battle, and `agents/` sees the battle only through observations and price quotes.

```text
stamina_engine/
  core/         dice expressions, seeded streams, scripted dice, ids, errors
  data/         rulesets/*.toml  weapons/*.toml  armor.toml  builds/*.toml
                maps/*.txt  scenarios/*.toml  profiles/*.toml
  rules/
    ruleset.py      RuleSet, presets (v0_9 to v0_10_0, review_candidate, review_sim), with_(), hash, TOML I/O
    registry.py     component registry: (kind, name) -> class
    plugins.py      load extra variants from a file outside the package (design-chat experiments)
    components/     crit  surcharge  blocks  defenses  resources  wounds  movement
                    off_turn  opportunity  ranged  turn_order  dying  information  grid
    pricing.py      every stamina quote, used by agents and engine alike
    block_solver.py optimal (perfect, grazing) choice for a defender
  model/
    build.py        Build spec and budget validation (Expertise, AP)
    equipment.py    Weapon, Armor, Shield, damage terms
    derive.py       Build x RuleSet -> CombatProfile
    state.py        CombatantState, BattleState, trackers, clone()
  grid/
    battlefield.py  terrain, occupancy
    geometry.py     distance metric, reach
    los.py          line of sight and 5e-style cover
    threat.py       cached threat maps
    pathing.py      reachable sets, exact cheapest paths under an agent's cost model
  engine/
    battle.py       Battle = state + ruleset + rng + broker + log
    stateops.py     the only mutator; emits events
    events.py       typed, append-only events
    timeline.py     rounds, initiative queue, turn loop
    context.py      timing-context stack for nested windows
    procedures/     melee  ranged  movement  opportunity  off_turn  abilities  dying
  agents/
    decisions.py    DecisionRequest types, Observation
    broker.py       routing, validation, decision logging
    scripted.py     alpha, fixed_k, reserve, chip_kill, lookahead
    grid_view.py    what an agent can work out about the grid from its observation
    tactical.py     grid-aware utility agent
    listed.py       answers from lists given in advance (tests, worked examples)
    profiles.py     NPC aggression profiles (data-driven)
    search.py       expectimax / MCTS auditor (later)
    human_cli.py    ASCII map and prompts, with timing
    replay.py       answers decisions from a saved log
  abilities/    framework, class cores, candidate abilities
  analysis/     exact distributions, exchange tables, r-band checker
  experiments/  scenarios, runner, sweeps, metrics, reports, phase suite
  provenance.py the stamp on every result: RuleSet digest, source hash, git, plugins
  cli.py        se table | se run | se sweep | se suite | se compare | se play | se replay
tests/          golden/  parity/  oracle/  properties/  geometry/
```

## Rule variants: the RuleSet

Every rule the fix order may change is a component of one frozen `RuleSet`; an experiment names a base preset and overrides components, and the result is stamped with the RuleSet's hash.

Locked rules (offense before defense, deterministic blocks, end-of-turn recovery timing) are plain code. Their numbers can still be parameters, but their shape is not pluggable. That keeps the variant surface to the places the review actually questions.

```python
@dataclass(frozen=True)
class RuleSet:
    name: str
    crit: CritRule
    surcharge: SurchargeRule
    blocks: BlockRule
    defenses: DefenseRule
    resources: ResourceRule
    wounds: WoundRule
    movement: MovementRule
    off_turn: OffTurnRule
    opportunity: OpportunityRule
    ranged: RangedRule
    turn_order: TurnOrderRule
    dying: DyingRule
    information: InformationRule
    grid: GridRule

    def with_(self, **changes) -> "RuleSet": ...
    def digest(self) -> str: ...   # hash of variants and non-default parameters


class CritRule(Protocol):
    def is_crit(self, die: int, face: int, finesse: int, source: DieSource) -> bool: ...
    def armor_ignored(self, crit_dice: int) -> int: ...
    def finalize(self, after_armor: int, crit_dice: int) -> int: ...


@register("crit", "per_die_bonus")
@dataclass(frozen=True)
class PerDieBonus:                  # parity only (review-sim)
    bonus: int = 2
    aim_dice_can_crit: bool = True
    ...
```

In config, a variant is a base plus overrides:

```toml
[ruleset]
base = "v0.9"
name = "review-candidate"
surcharge = { kind = "linear", slope = 2 }
```

| Component | Variants to implement (v0.9 first) | Findings it serves |
|---|---|---|
| `crit` | ×2 after armor once per attack (v0.9); +1 per crit die only if damage gets through (`per_die_if_through`, packet 0.9.2); ×2 only at 2+ crit dice; none; +N per crit die even when nothing gets through (parity only, see Assumptions register). Switches: per-die armor ignore, aim dice can crit | F2, F14 |
| `surcharge` | +s per prior action (s = 1, 2); quadratic; light weapons skip the first surcharge point; hard step cap | F1, F8 |
| `blocks` | Perfect 1, 2, 3…; half slope 1, 1, 2, 2…; flat cost for ranged perfect blocks; graze leak size and whether armor soaks it; block count reset per attacker per round; guard rules (shift or +1 MD after ≤ G actions) | F1, F3, F6, Addendum 2 |
| `defenses` | MD, RD and Dodge formulas; Dodge folded into RD; shield values; two-hander +1 MD; AGI steps by armor; MD growth with level | F3, F4, F5 |
| `resources` | HP formula (6 + STR in v0.9; base + 2 per even STR from 0.9.1: `hp_strength`, `hp_base`); Intelligence's core-ability discount and bonus AP (0.9.1: `core_discount`, `bonus_ap`); max stamina (6 + HP + L/5, 8 + HP/2, 10 + HP − STR, armor or shield float); recovery; strain maximum and both recovery options; level bonus into maximum or recovery | F5, F7 |
| `wounds` | None; H-1 wound cap applied before any crit effect; H-2 damage lowers max stamina | F1 option 3, F3, F7 |
| `movement` | Free movement formula; extra movement priced per purchase, per square, or capped at free movement | F10 |
| `off_turn` | Escalation slope; what counts toward it; window order (ascending initiative, descending, repeat until all pass); purchase cap | F14, MV-4 |
| `opportunity` | OA cap (1 + odd FIN in v0.9; none from 0.9.1; weapon base + odd FIN; per-square optional rule); avoidance cost (flat 1, attacker's cap, counts on mover's off-turn track); avoidance at 0 stamina (forbidden or debt); point-blank OAs avoidable; OA timing in multi-square moves | F9, F14 |
| `ranged` | Aim as damage (1d6 + FIN) or precision (crit range, armor ignore); range-band penalties (v0.9, flat −1d6 at medium, none); cover values; dive outcomes; point-blank uses MD | F3, F11 |
| `turn_order` | Initiative dice and bonuses (odd AGI + odd CUN in v0.9; + CUN from 0.9.1: `bonus`); tiebreak (reroll, higher AGI, shared turn, list order for parity) | F14 |
| `dying` | System Shock thresholds and roll (+ STR in v0.9; + WIL from 0.9.1: `roll_attribute`); stabilization amount | Packet: Dying and Death |
| `information` | Stamina public or hidden; what observers see of blocks and recovery | F6a |
| `grid` | Diagonal metric; moving through creatures; creatures as cover; reach through walls | Assumptions register |

Weapon, armor and shield tables are data files, not components, so F8 alternatives (STR multipliers, die upgrades, STR capped at die size) are separate tables a scenario selects.

**Presets:** `v0.9` (as written, plus the review's assumptions for silent rules), `review-candidate` (+2 surcharge, v0.9 crits), and one preset per phase as decisions lock (`phase1`, `phase2`…), so later phases build on what earlier ones settled.

A further `review-sim` preset reproduces the old simulator's quirks for parity runs only: initiative ties go to the first-listed combatant, duels carry no off-turn costs, static tables round the mean roll half to even, and the per-die crit bonus is available for the review's linear-crit runs (see Verification).

### Experiments from design chats

Design chats try rule ideas themselves, so the engine keeps one baseline and makes every other idea cheap to add beside it, never in place of it. `sim/docs/USAGE_FOR_CHATS.md` is the chat-facing version of this.

| Change | How it's tried | What lands in the repo |
|---|---|---|
| Numbers, or an existing variant | A RuleSet TOML override (`--ruleset idea.toml`) | Nothing, or the TOML beside a report |
| A new mechanism that fits a component | A plugin: a file outside the package that registers a variant named `exp_...` (`--plugin idea.py`); taking an existing name is refused | The plugin and TOML beside a report |
| A procedure or timing change | Engine code on an `exp/<topic>` branch, compared against the commit it started from | A branch or patch; if kept, a PR that adds a component for it |

Variants move from experiment, to candidate (on `main`, in a phase preset), to ruled. Only the designer moves them. A ruled variant becomes the baseline, and the rejected ones are deleted, or kept for parity only if a published result depends on them. Keeping only live candidates on `main` keeps the test matrix and the register small.

**The digest.** It hashes each component's variant and the parameters not at their default; the name is left out. A new switch whose default keeps the current rule therefore changes no digest, the baseline's included. In exchange, a released default never changes (`tests/golden/component_defaults.json` pins them, and the presets' digests are pinned too): a ruling that changes a rule sets the new value where it applies, in a preset for the baseline, and the digest changes with it. `to_toml()` still writes every parameter. Digests stamped before this convention (tags `m0`–`m5`) hashed every parameter, so they differ from today's for the same rules; recompute one at the commit its stamp names.

**Provenance.** The RuleSet digest identifies the rule configuration, not the code. Every result is therefore also stamped with:
- a hash of the package's source and data files (`source`), which identifies the implementation even outside git;
- the git commit and whether the engine's files have uncommitted changes;
- each plugin file's hash.

`se` prints the stamp after every result, `provenance.collect()` returns it, and the experiment runner (M1) writes it on every result row.

## Battlefield: grid, reach, sight and pathing

The battlefield is a square grid of 5 ft cells loaded from ASCII maps; it answers four questions for the engine: who threatens a square, what cover a shot has, where a creature can get to, and at what price.

**Maps.** A scenario names a map file and a legend. Default legend: `.` floor, `#` wall (blocks movement and sight), `=` low wall or crate (blocks movement, blocks sight lines for cover), `o` pillar, digits and letters for spawn points. Maps stay at or under 40 × 40 so geometry can be cached.

```text
# archer_field.txt
##############
#A..........1#
#....==......#
#..........o.#
#.=......=...#
#B..........2#
##############
```

**Distance and occupancy.** Chebyshev distance (diagonals count as one square; confirmed for now), with the alternating 1–2 diagonal as a `grid` switch. One creature per square; creatures may pass through allies but not enemies and may not end in an occupied square (switchable).

**Reach and threat.** A creature threatens every square within its ready melee weapon's reach that it has a clear line to; incapacitated creatures threaten nothing. `ThreatMap` is cached per state version and invalidated on any move, draw, drop or incapacitation.

**Line of sight and cover.** Cover follows the 5e grid method the packet points to: the shooter picks the corner of its square that gives the best result and traces lines to the four corners of the target's square. Blocked lines map to cover: none blocked, no cover; 1–2, half (+2); 3, three-quarters (+5); 4, total (no shot). Line tracing is exact segment-against-cell intersection, cached per square pair for static terrain. Creatures grant half cover (confirmed); this stays a switch.

**Diving for cover.** On a ranged attack, the dive window asks the planner for every square reachable with k off-turn purchases (k × squares per purchase) and the cover each gives against that shooter. A destination with total cover counts as three-quarters, as written; what a half-cover destination gives is in the Assumptions register.

**Pathing.** `pathing.py` offers three queries, all advisory:

- **Reachable set:** squares reachable within a stamina and purchase budget, used for dives and off-turn movement.
- **Cheapest path:** cost-aware A* to a goal, where the agent supplies the cost model: free squares, extra purchases, avoidance payments per threatening enemy per square left, and expected OA damage when not paying.
- **Safest square:** squares out of every enemy's reach, or behind cover from a named shooter.

Execution is always square by square in the engine (next section), which re-checks threat and triggers at each step, so a stale plan can never skip an opportunity attack.

## Timing engine

The engine is a set of procedures that follow the packet step by step, call agents at each decision point, and nest when one rule interrupts another (an opportunity attack mid-move, a dive mid-shot).

**State.** `BattleState` holds combatants, occupancy, round, initiative queue and the RNG; `clone()` gives a cheap copy for look-ahead agents. Each `CombatantState` carries the trackers the costs depend on:

```python
@dataclass
class CombatantState:
    id: str; team: str; profile: CombatProfile   # derived from Build x RuleSet
    pos: Cell; hp: int; stamina: int; strain: int; shock: int
    status: Status            # active, incapacitated, shock, stable, dead, fled, surrendered
    wielded: Loadout; used_hands: frozenset[Hand]
    actions_this_turn: int    # on-turn surcharge
    off_turn_costs: int       # off-turn escalation, reset at start of own turn
    free_move_left: int
    acted_this_round: bool
```

**StateOps** is the only code that writes state: `spend(c, n, category, track)`, `recover`, `injure`, `move_to`, `draw`, `set_status`, and so on. Each checks invariants, recomputes max stamina when HP changes (clamping current stamina, as written), and appends an event. A debug mode re-validates the whole state after every op.

**Pricing** answers every "what would this cost?" question from the RuleSet and the trackers: melee step (on-turn or opportunity), full attack quote for k steps, shot, aim step, extra movement, off-turn purchase, OA avoidance, nth perfect block, graze, draw between turns, strain ability with overage, and the OA cap. Agents call the same functions the engine charges with.

**A turn** (packet: Starting Combat and Turn Structure):

1. Start of turn: reset the surcharge, off-turn track and free movement; roll for System Shock if in it.
2. Command loop until the agent ends the turn: move, melee attack, ranged attack, draw or sheathe, use ability.
3. End of turn, then recovery.
4. Off-turn window after this turn ends, ordered by the `off_turn` rule.

**A melee attack** runs the packet's eight steps as eight functions: declare target; declare and pay steps; roll and note crit dice; reactions; blocks; armor (less crit ignores); crit effect; injury. An opportunity attack is the same procedure with off-turn pricing and the OA cap.

**A ranged attack** inserts the dive window after the roll, picks RD or MD by point-blank range, then opens a point-blank OA window once the shot resolves.

**Movement** executes one square at a time. Leaving a threatened square opens an OA window: the mover chooses which threatening enemies to pay off, each remaining enemy chooses whether to attack within its cap, and each attack resolves as a nested melee attack before the mover enters the next square. If the mover is incapacitated, movement stops.

**Nested windows.** A `TimingContext` stack records where the battle is (for example: Ana's turn → Ana's shot at Bors → Bors's dive → Cael's opportunity attack on Bors). Agents receive it with every request, abilities check it for their timing, and the log records it, which is how F14's ordering questions become measurable.

**Decision: plain calls, not coroutines.** Procedures call the broker synchronously and nesting is ordinary recursion, so procedures read like the rulebook. A generator design (yield each request, resume with the answer) would make pausing easier, but every need it serves is met another way: human play blocks on input, replay answers from a log, and look-ahead clones state. Revisit only if a web front end needs pause and resume.

## Decisions and agents

Every choice reaches an agent as a typed request with its legal options, the prices, an observation filtered by the information rule, and the timing context; the broker validates the answer and logs it.

| Request | Asked when | Answer |
|---|---|---|
| `TurnCommand` | Each loop of the agent's own turn | Move (path), melee attack, ranged attack, draw or sheathe, ability, end turn |
| `Commitment` | After choosing an attack | Steps, or shot plus aim steps |
| `Blocks` | After the roll and reactions | Perfect and grazing counts |
| `Dive` | Targeted by a ranged attack | Destination square, or stay |
| `OffTurnMove` | Each off-turn window | Path within purchases, or pass |
| `AvoidOA` | Leaving a threatened square | Which threatening enemies to pay off |
| `TakeOA` | An enemy leaves a square you threaten, or shoots in your reach | Steps within the cap, or decline |
| `UseAbility` | Any window an owned ability can fire in | Ability and parameters, or pass |

The broker records request type, option count, the answer, whether it differed from "pass", and response time for humans. That log is the F11 measurement.

**Agent families**, from cheapest to most capable:

1. **Block solver (shared).** Exact search over (perfect, grazing) pairs minimizing stamina + w × injury, never accepting an avoidable incapacitation; w defaults to 3 with 1.5 and 6 as sensitivity runs, as in the review. Also exposes "cheapest zero-injury block" for the static tables.
2. **Scripted commitment policies.** Alpha, fixed k, reserve N, chip-kill and one-ply look-ahead, ported from the review for parity. On a grid they approach by the cheapest path and otherwise stand still.
3. **Tactical agent.** A utility agent built from small, testable scorers: target choice (lowest effective stamina, nearest, greatest threat), approach paths that limit exposure, staying out of multiple reaches, keeping reach-weapon spacing, seeking cover against shooters, retreating after its own turn when stamina is low, diving when an incoming shot exceeds its block budget, and chasing.
4. **NPC profiles (H-6).** Data files that parameterize the tactical agent: commitment table ("2 steps; 3 against a target below half stamina"), aggression, focus-fire rule, retreat and surrender thresholds. Sweeping these is how F6's "GM as lethality dial" gets measured.
5. **Search auditor (later).** Expectimax or MCTS over macro-actions using `clone()`. It is not for bulk runs; it hunts for strategies that beat the scripted and tactical agents, which is the check that a "no dominant strategy" finding is real.
6. **Human CLI.** ASCII map, price quotes beside each option, prompts for every request, timings logged.
7. **Replay.** Answers from a saved decision log, for reproducing any fight exactly.

**Hidden information.** When stamina is hidden, observations carry only what a table would see (steps declared, blocks declared, recovery happened) and agents keep their own estimate. Phase 0 can then measure what stamina visibility is worth.

## Characters, equipment, abilities and dying

A build stores only what a player chooses; every number derived from it (HP, stamina, defenses, crit range, OA cap) is computed by the RuleSet, so changing a formula never means editing builds.

**Builds.** Level, Expertise allocation, AP purchases (cores, tier abilities, abilities), proficiencies and one or more loadouts (main weapon, off-hand or shield, armor, backup and quick-draw weapons). `validate(build, ruleset)` checks Expertise and AP budgets against the level table and triangular costs. Skill Points are ignored in combat.

```toml
# builds/l1_sample_fighter.toml
level = 1
attributes = { STR = 2, AGI = 1, FIN = 1 }
cores = ["fighter"]
loadouts.main = { weapon = "longsword", grip = "one-handed", shield = "shield", armor = "medium" }
```

**Derivation.** `derive(build, ruleset) -> CombatProfile` applies armor's Strength penalties first, then the defense, movement, initiative, crit and OA formulas per loadout. Defenses are recomputed when the wielded loadout changes; max stamina when HP changes.

**Equipment tables.** Weapons are data: base cost, damage terms (dice plus attribute terms with multipliers and "best of" choices, such as `1d10 + max(STR, AGI) + FIN`), hands, reach, ranges and properties (quick-draw, hammer, reach, cleave). Armor and shields likewise. Variant tables for F8 live beside the v0.9 table.

**Build library** for the phase suite: the L1 sample fighter; L1 duelist, two-hander, greatsword, heavy and archer from the review; an L1 unarmored, unshielded stand-in for casters; L30 sample, STR brute, heavy and duelist; the L99 build. These match `make_fighter` in `tests/oracle/sim.py`. Monsters arrive with NPC profiles in Phase 7.

**Abilities.** An ability declares its timing windows, cost (stamina, strain), conditions and an effect written against `StateOps`. Strain overage pricing comes from `Pricing`. First set:

- Class cores: Fighter (strain for an extra recovery), Rogue (take the turn now or later; this needs a mutable initiative queue), Barbarian (refund the largest step), Monk (no perfect-block escalation for this attack).
- Candidates: Heavy Swing, Riposte, Tactical Withdrawal. Feint waits until contests are defined.

**Control effects (H-4).** A generic progress track that the effect advances and the target pushes back with stamina, ready for Phase 7 to fill in; no conditions list until the design picks one.

**Dying.** System Shock as written: Shock from negative HP, dying roll at start of turn (2d12 + STR against 10 + Shock and 15 + Shock), damage adding Shock, death at 10 Shock or −10 HP, and stabilization by an ally with a placeholder amount until Medicine is defined. Retreat, surrender and fleeing the map are end states too, so a fight can end the way the packet says most fights should.

## Analysis and experiments

Single-exchange questions are answered exactly in milliseconds; whole-fight questions run as seeded Monte Carlo sweeps over scenarios, and both feed one re-runnable phase suite.

**Exact calculators (`analysis/`).** The damage of k steps is a convolution of die distributions that tracks the number of crit dice, giving the joint distribution of (total, crit dice). For each outcome the block solver gives the defender's best response at a given stamina, defense and armor. From those come, with no sampling error:

- attack cost vs full-block cost by k (review Table 1);
- damage per stamina by k for every weapon (Table 8);
- full strike from full: mean injury and chance of going down, by level (Table 3's strike column and the Addendum grid);
- single-shot ranged outcomes by aim steps and target (Table 5's static part);
- the r report: damage per step ÷ the defense it meets, for every build, weapon and level in the library, flagged against the target band once Phase 1 sets it.

**Scenarios** are TOML: map and legend, combatants (build, team, spawn, agent or NPC profile), RuleSet (preset plus overrides), end conditions (a side incapacitated, fled or surrendered; an objective square; a round cap counted as a draw), trials and master seed.

```toml
[scenario]
name = "one-vs-three-corridor"
map = "maps/corridor.txt"
ruleset = { base = "review-candidate" }
trials = 2000
round_cap = 30

[[combatant]]
build = "l1_sample_fighter"
team = "pc"
spawn = "A"
agent = "tactical"

[[combatant]]
build = "l1_sample_fighter"
team = "npc"
spawn = "1"
profile = "disciplined_2step"   # one entry per attacker; spawns 1-3
```

**Sweeps** take the product of RuleSet overrides, scenarios and agent pairings. Each trial's seed derives from the master seed and the cell, so any single fight can be re-run alone. Trials run across processes; results land in Parquet as three tables (one row per fight, per attack, per decision) with the RuleSet digest, assumption values and provenance stamp on every row. Reports print 95% Wilson intervals and reproduce the review's table layouts so old and new numbers sit side by side.

**Metrics.**

| Level | Measures |
|---|---|
| Exchange | Attack cost, block cost, injury distribution, chance of going down, crit rate, r |
| Fight | Winner, rounds, first-mover win rate, draws, winner untouched, loser's final HP, deaths vs stabilizations, retreats and surrenders |
| Positioning | Squares moved on and off turn, OAs provoked, avoided and taken, stamina spent avoiding, dives and their effect, rounds to contact, shots by range band and cover |
| Economy | Stamina by category per round, recovery wasted at the cap, stamina at start of turn, strain and overage |
| Load (F11) | Requests per round by type, option counts, non-trivial decisions, dice rolled per attack, human seconds per decision |

**Phase suite** (`se suite`), re-run at the end of every phase as the fix-order doc asks:

1. Exchange tables at L1, L30 and L99 (exact).
2. Equal duels at three levels on open ground, full policy matrix.
3. One vs three on open ground and in a corridor, with movement and retreat allowed.
4. Ranged table, then archer vs approaching fighter on three maps: open field, scattered cover, wall line.
5. Reach control: spear vs sword holding a chokepoint.
6. Retreat economics: a fleer and a chaser, with an allied line six squares back.
7. Armored vs unarmored builds, and weapon efficiency.
8. A 3v3 mixed party (fighter, duelist, archer) on a terrain map, as the integration check.

Encounters up to about 6v6 on maps up to 40 × 40 (confirmed).

## Assumptions register

Where v0.9 is silent or TODO, the engine takes the review's assumption when it had one and otherwise the reading closest to the packet's intent; each is a switch, and every result records which way it was set.

**Status** says who owns each default:
- *engine convention*: an engine or analysis choice that doesn't change what a rule means.
- *pending designer*: a plain-text reading or design fork the designer has not ruled on, so the default is provisional.
- *ruled*: the designer decided.

When a pending row is ruled, or a ruled row changes, the same commit updates the presets that use it and re-runs the parity gate, so a rules change can't leave a stale default behind.

| Unstated or TODO rule | Engine default | Switch | Status |
|---|---|---|---|
| Stamina is public | Public (review assumption) | `information.stamina` | pending designer |
| Aim dice can crit | Yes (review assumption) in the v0.9.x presets. Packet 0.10.0 rules that aim dice are never critical, so `v0.10.0` sets it false | `crit.aim_dice_can_crit` | ruled 2026-11-11 (0.10.0); v0.9.x keep the review's reading |
| Crit doubling happens once per attack | Once (review assumption). Packet 0.9.2 drops the doubling, and the TODO with it | `crit` kind `double_once` | pending designer (v0.9 only) |
| Per-die crit bonus (+N per crit die) | Dropped as a design candidate. Kept only as a parity component under `review-sim`, where it is added even when nothing gets past armor, as the review's simulator did. Packet 0.9.2's +1 per crit die applies only when damage gets through, so it is its own variant, `per_die_if_through` | `crit` kind `per_die_bonus` | ruled 2026-11-03 |
| Initiative ties | Reroll the tied creatures (the review's simulator gave ties to the first-listed combatant) | `turn_order.tiebreak` | pending designer |
| Order of off-turn movement after a turn | Lowest initiative first; repeat passes until everyone passes | `off_turn.order` | pending designer |
| Who and when in an off-turn window | After every turn that is taken, including an incapacitated creature's dying-roll turn (dead creatures take no turn, so there is no window). Every active creature may move, including the one whose turn just ended; only movement (drawing waits for M3). Order is over initiative positions, where ties are already broken; a creature that passed may move in a later pass; a creature with nowhere it can reach and afford isn't asked | `off_turn.order`, `off_turn.repeat_until_all_pass` | pending designer |
| "Since the start of your last turn" before your first turn | Counts from the start of the fight | — | engine convention |
| Range bands (M3) | Range is the Chebyshev distance between squares: up to short, short; up to medium, medium; up to long, long; beyond long, the shot can't be made (not offered). At medium the first aim step adds only Finesse and rolls no die (so it can't crit), and a shot with no aims misses; at long the first two, and fewer than two aims miss. A missed shot is still paid for and still provokes | `ranged.bands` | pending designer |
| Range-band variants (Review F11 (b)) | `minus_d6`: no minimum aims and no dropped dice; the shot loses 1d6 at medium and 2d6 at long, floored at 0. `none`: no band effects (beyond long still out of range) | `ranged.bands` | pending designer |
| What an aim step adds | Its die plus the shooter's Finesse after armor penalties, floored at 0 | — | pending designer |
| Aim as precision (Review F3 option 3) | `aim_mode = precision`: aim steps add no damage; each widens the critical range of the shot's dice by 1 (no cap); costs and band minimums unchanged | `ranged.aim_mode` | pending designer |
| Dodge folded into Ranged Defense (Review F3 option 1) | `ranged_mode = dodge_folded`: RD = 1 + 1 per even Agility (armor-adjusted, as for Dodge) + shield | `defenses.ranged_mode` | pending designer |
| Flat ranged perfect blocks (Review F3 option 2) | `ranged_flat = 2`: each perfect block against a ranged attack costs 2, no escalation; grazes and melee unchanged | `blocks.ranged_flat` (0 = as written) | pending designer |
| What a dive to half cover gives | Half cover; total cover counts as three-quarters, as written | `ranged.dive` | pending designer |
| Diagonal movement and reach | Chebyshev: a diagonal is one square | `grid.metric` | ruled (confirmed for now) |
| Moving through creatures | Through allies, not enemies; a move never ends in an occupied square, so you can't stop in an ally's square between actions. Incapacitated and dead creatures still fill their square but anyone may pass through it; passing through costs nothing extra | `grid.occupancy`, `grid.bodies` | pending designer |
| What threatens a square | Every ready melee weapon in the current loadout, main and off-hand, threatens its reach (so an off-hand dagger can make an OA under the default cap of 1 even when the longsword can't). A bow, a sheathed weapon or no weapon threatens nothing; unarmed threatens only with an unarmed proficiency, as for MD. Threat is geometric: it doesn't depend on whether the enemy can afford an OA. Incapacitated and dead creatures threaten nothing. An OA uses one ready melee weapon of the attacker's choice that reaches the square | — | pending designer |
| Which weapon an on-turn attack uses | The main weapon, as in M1; the packet has no two-weapon attack rules | — | engine convention |
| Creatures as cover | Half cover, as in 5e | `grid.creature_cover` | ruled (confirmed) |
| When a cover line is blocked (M3) | By a square it passes through the inside of, by running along the seam between two blocking squares, or by squeezing through a corner point between two blocking squares; touching a corner or running along a blocking square's outside edge doesn't block. The shooter uses its best corner | — | pending designer |
| What blocks cover lines (M3) | Walls, pillars, low walls and crates all count toward the line count (1–2 blocked: half; 3–4: three-quarters). Total cover (no shot) needs all four lines blocked by tall terrain: a low wall alone never gives total cover. Creatures between give half cover at most, if any line from the chosen corner passes through one | `grid.creature_cover` | pending designer |
| Targets in total cover | Can't be targeted | — | pending designer |
| Reach through walls | Needs a clear line from wielder to square: the centre-to-centre segment doesn't pass through the inside of a wall or pillar square, and doesn't squeeze between two of them at a corner. Low walls, crates and creatures don't block reach, so a spear reaches over an ally. Reach uses the movement metric | `grid.reach_needs_line` | pending designer |
| Diagonal steps past wall corners | Blocked only when both orthogonal neighbours are walls or pillars (no squeezing through a zero-width gap); creatures never block a diagonal. `free` and `no_cut` (blocked if either is) are the other values | `grid.corners` | pending designer |
| What map terrain does (M2) | `#` walls and `o` pillars block movement, sight and reach; `=` low walls and crates block movement only (their cover arrives with ranged attacks in M3). Every creature fills one square; no difficult terrain; the map edge is a wall, so nobody leaves the map | map legend | pending designer |
| When an OA lands during a multi-square move | On leaving each square, before entering the next: the mover is still in the square it is leaving. On each square left, the mover first decides which threatening enemies to pay off, not knowing who would attack; then each remaining enemy decides, in `off_turn.order` (lowest initiative first by default), each OA resolving before the next enemy decides | `opportunity.timing`, `off_turn.order` | the mover paying first, not knowing who would attack: ruled 2026-11-13; the rest pending designer |
| Repeat OAs during one move | Each threatened square left is its own trigger, so an enemy may OA on every one (its cap is per OA, so escalation usually stops repeats); one OA per enemy per trigger. Entering reach doesn't provoke; leaving the first square inside reach does (stepping closer to a spear) | — | pending designer |
| Paying off an enemy that couldn't OA | Allowed; it's a waste, not an error | — | pending designer |
| A mover downed by an OA | It stays in the square it was leaving and the move ends; enemies left on that square aren't offered OAs (attacks on the incapacitated aren't offered). If that square is an ally's, the body shares it | — | pending designer |
| The packet's optional per-square cap | One pooled cap per enemy per move: each square the mover leaves within your reach without paying you off adds 1 + odd FIN; an OA can spend what has built up minus what you already spent on that mover this move. So a FIN-0 spearman can pass at the first square and attack for 2 at the second (the packet's "up to 3 stamina" example only works pooled). Uses "leaves" (the packet), not "moves within" (the ledger) | `opportunity.per_square_cap` | pending designer |
| Committing to a path | A move is a whole path, carried out square by square; it stops only if the mover is incapacitated or the fight ends. Agents re-plan by moving in shorter hops. Each move is one logged decision (F11) | — | engine convention |
| Requests with one legal answer | Not asked: an avoidance request when the mover can't pay anyone, an OA request when no step fits the cap and stamina, an off-turn move request when nothing is reachable and affordable. Keeps all-adjacent logs identical to M1 | — | engine convention |
| Diving out of a point-blank shooter's reach | Dive OAs resolve first, then blocks; point-blank OAs after the shot | `ranged.point_blank_order` | pending designer |
| The dive (M3) | After the roll, the target may make one off-turn move (purchases on its off-turn track, provoking OAs as any move does; those resolve before blocks). Cover is then measured from the shooter's square to the target's new square, with total counting as three-quarters; range and line of sight aren't rechecked, since the shot is committed | `ranged.dive` | pending designer |
| Point-blank defense (M3) | The target uses Melee Defense (plus cover) if the shooter is in a square the target threatens with a ready melee weapon, judged after any dive | — | pending designer |
| OAs from shooting in melee (M3) | After the shot resolves (or misses), every enemy threatening the shooter's square may take an OA, lowest initiative first, the target included; they can't be paid off as written (`point_blank_avoidable` is the variant); caps and tracks as for any OA | `opportunity.point_blank_avoidable` | pending designer |
| Drawing weapons (M3) | A creature switches between its build's loadouts (never changing armor). Each weapon or shield the new loadout holds that the old one doesn't is drawn: free on your turn until you've used a weapon (attacked or shot); otherwise 1 stamina for a normal item and 0 for a quick-draw weapon. After a bow shot no normal item can be drawn until your next turn. Between turns means in an off-turn window, where drawing is an option beside moving; draw costs aren't off-turn costs. Sheathing and dropping are free | — | pending designer |
| Shots per turn (M3) | As many as affordable; the shot cost is flat and each aim step is an action, so the surcharge carries across shots | — | pending designer |
| Paying to avoid OAs at 0 stamina | Not allowed. The debt variant (F14): only avoidance can be paid without stamina; the shortfall comes out of the next recovery before any stamina is regained, carrying over if larger; stamina never goes below 0 | `opportunity.avoid_debt` | pending designer |
| Free squares before purchases | Purchases are only bought once the turn's free movement is used up (paying for free squares would be dominated) | — | engine convention |
| A purchase gives N squares and you use fewer | On your turn the rest is kept for the turn and can be split around actions like free movement; off-turn, it lasts only for that move | `movement.leftover` | pending designer |
| When a movement purchase is paid | When the move is declared, like an attack's steps: a move is one declared path, paid for before the mover sets off (so it is down that stamina even if an OA stops it), and nothing is paid for moves it hasn't declared yet. Between moves it can stop and re-plan; within one it can't, so agents that want to react square by square move in shorter hops | — | ruled 2026-11-03 |
| Negative Agility and movement | No bonus: the odd count of a negative value is 0, as for Finesse | — | engine convention |
| Purchases in one off-turn move | Any number; F14's "purchase cap" isn't in the packet | `off_turn.purchase_cap` (0 = none) | pending designer |
| F9 option 1, cap from the weapon | `cap_rule = weapon_base`: cap = the OA weapon's base + odd FIN; escalation still counts against it; stacks with the per-square rule | `opportunity.cap_rule` | pending designer |
| F9 option 2, avoidance at the attacker's cap | `avoid_price = attacker_cap`: each enemy denied costs its cap as its formula gives it, not reduced by its escalation or stamina (so the price reveals nothing hidden) | `opportunity.avoid_price` | pending designer |
| F9 option 3, avoidance on the off-turn track | Each avoidance costs 1 + earlier off-turn costs and counts as one, so the third enemy slipped past costs 3. On your own turn this makes your post-turn window pricier, which conflicts with "your own on-turn movement and actions never make it pricier", so two values are built: `off_turn` (always) and `off_turn_only` (only when paid off-turn) | `opportunity.avoid_track` | pending designer |
| F10 options | `extra_squares = one`: extra on-turn purchases move 1 square, off-turn purchases keep 1 + odd AGI (the chasers-win lever). `extra_cap = free_movement`: purchased squares per turn are at most your Movement, the last purchase cut short | `movement.extra_squares`, `movement.extra_cap` | pending designer |
| Max stamina at negative HP | HP term floors at 0 | `resources.max_stamina` | engine convention |
| Spear hands | One-handed, so a shield is allowed | weapon table | pending designer |
| Ability windows (M5) | An ability can fire only at the engine's timing windows: on your turn (between actions), in an off-turn window, after an attack on you is rolled and before you block, between turns, as your turn would begin, as you declare a melee attack, and in a melee attack's reactions step. "At any time" (the Fighter core) means your turn, off-turn windows and before blocks; not mid-move or mid-roll | — | pending designer |
| Fighter core (M5) | 3 strain: recover your normal recovery now; offered only when below maximum stamina; usable any number of times, the strain overage then costing stamina | — | pending designer |
| Barbarian core (M5) | 1 strain: recover the biggest stamina you spent on one attack step this turn and haven't refunded yet (each step refunds once; OA steps, paid off your turn, don't count) | — | pending designer |
| Monk core (M5) | 1 strain, before blocks: every perfect block against this attack costs what the first would | — | pending designer |
| Candidate abilities and the AP budget (M5) | A build lists candidate abilities (`abilities = [...]`); they aren't costed yet, so they don't count against the AP budget | build `abilities` | pending designer |
| Rogue core (M5) | 3 strain, between any two turns (including before the round's first) if it hasn't acted this round: take its turn now. Or, as its turn would begin, wait: it goes after the next creature's turn, and while waiting it chooses again at every later gap and turn start, for free; if it never comes back it goes last. The order turns were actually taken becomes next round's order | — | pending designer |
| Heavy Swing (M5) | Chosen as you declare a melee attack: +1 stamina on every step, and the attack ignores 2 more armor (before critical dice's own ignore) | — | pending designer |
| Riposte (M5) | After you make at least one perfect block against a melee attack, once it has resolved: an opportunity attack on the attacker, priced and capped as any OA, so uncapped from 0.9.1 (works in the all-adjacent arena too) | — | pending designer |
| Tactical Withdrawal (M5) | In a melee attack's reactions step: pay 2 stamina (flat, not an off-turn cost) to move up to one off-turn purchase's squares, provoking as any move does; if the attacker no longer reaches you, the attack is avoided (already paid for, no blocks, no damage) | — | pending designer |
| Control effects (M5 stub) | A progress track per effect on a creature: an effect's source advances it; the creature pushes it back 1 per stamina. What progress does (and when it can be resisted) waits for Phase 7 | — | pending designer |
| Strain at a fight's start (M5) | 0: every simulated fight is the first of a fresh day (Packet: Strain recovers only overnight), so ability results are the best case for a day of several fights | `CombatProfile.start_strain` (0 for now) | engine convention |
| Engine agents and abilities (M5) | Off unless the agent spec says `abilities = "use"`: an agent that has them passes every window and declines Riposte's OA, so results without abilities stay comparable. With them on it follows the heuristics in `agents/ability_policy.py` (Fighter before blocks when recovering saves at least one HP's worth, or on its turn when short of two steps; Barbarian refunds after attacking; Monk when flat blocks save at least 2; Rogue jumps in ahead of an enemy; Heavy Swing against armor 2+; Tactical Withdrawal when blocking would cost more than its 2 stamina plus the OAs it risks). Agent conventions, not rules | agent spec `abilities` | engine convention |
| A person's decisions (M5) | `se play` prices each option and lists the non-dominated blocks with their cost and injury, arithmetic a player at a table does in their head, so its seconds are a lower bound on table time. It re-asks on input it can't use rather than ending the fight | — | engine convention |
| Decision load (M5) | `se load` counts per creature-round (rounds x combatants for engine runs; rounds for a person's session); a request is non-trivial if it offers more than one option (blocks: more than one non-dominated pair). Requests with one legal answer are never asked (C14), so they don't count | — | engine convention |
| Where a Rogue's moved turn sits next round | Keeps the new slot | Rogue core parameter | pending designer |
| Recovery while incapacitated | None | `resources.recovery` | pending designer |
| Mean roll in the static tables (Table 1, `variants.py`, `grid.py`) | Round half up; `review-sim` rounds half to even, as Python's `round()` did, which changes three Table 1 cells and the L30/L99 rows (L99 k7: 80.5 → 80); printed figures likewise (Table 8's 2.125 prints as 2.12) | `se table --rounding` | engine convention |
| Expertise and AP budgets above level 1 | EP = 4 + levels 1..L ending in 1/4/6/9; AP = levels 0..L ending in 0/2/7 (L1/L30/L99: 5/16/44 EP, 1/10/30 AP). The base of 4, and reading level 0's point as the starting AP, need the designer | `resources.budget` | pending designer |
| Proficiency list | Builds list proficiencies explicitly; the library's Fighter core grants every v0.9 table weapon | build data | engine convention |
| "(STR or AGI)", "(AGI or FIN)" damage terms | Always the higher value; the chosen attribute is recorded, not just the value | weapon data | pending designer |
| Equipment variants (M4) | A variant table in `data/equipment/` names its base tables and replaces or adds weapons, armor and shields entry by entry; a scenario selects one with `equipment` (`se table --equipment` too). The table isn't part of the RuleSet digest: it's recorded in the scenario TOML that every result carries, and in the source hash | scenario `equipment` | engine convention |
| F8 option 1, die upgrades | `f8_die_upgrades`: greataxe 2d6 + STR + FIN (the review's), greatsword 1d12 + STR + FIN (the same idea: the multiplier dropped); base costs unchanged | equipment table | pending designer |
| F8 option 2, light weapons skip a surcharge point | `surcharge.light_exempt = 1`: a light weapon's steps pay 1 less surcharge, floored at 0 (base, base, base + 1…). The light weapons are the dagger and shortsword (the packet's base-1 light weapons, tagged `light` in the table) | `surcharge.light_exempt` | pending designer |
| F8 option 3, Strength capped at die size | `f8_str_cap`: a step's Strength term adds at most the weapon's largest die size | equipment table `str_cap` | pending designer |
| F4 option 1, shields | `f4_shield_1`: +1 Melee and +2 Ranged Defense. `f4_shield_str`: +2 / +2 with a Strength requirement of 2 (a guess; the review gives no number), penalizing AGI and FIN like armor, separately from armor's own requirement | equipment table | pending designer |
| F4 option 2, two-handers and Agility steps | `two_hander_bonus = 1`: +1 Melee Defense for a proficient two-handed melee grip. `agility_split`: Agility's Dodge (and folded Ranged) bonus comes one step finer than Melee's: every point unarmored or in light armor, every 2nd in medium, every 3rd in heavy | `defenses.two_hander_bonus`, `defenses.agility_split` | pending designer |
| Draft weapons with no base cost | Left out until costed | weapon table | pending designer |
| Armor's Strength penalties "lower the attributes themselves" | Penalized AGI and FIN apply everywhere: defenses, initiative, movement, crit range, OA cap, damage terms | — | pending designer |
| Negative flat damage (penalized AGI or FIN) | Each step's roll floors at 0 | weapon table `step_floor` | pending designer |
| A graze that stops less than its share | Still leaks 1. A graze that stops nothing leaks nothing, with perfect blocks counted first (ruled for packet 0.10.1): not implemented yet, `rules.exchange.resolve` leaks 1 per graze. The two differ only for a graze that stops nothing, which the block solver never chooses | — | ruled 2026-11-13; engine change pending |
| What armor soaks | Residual and leaks together, as one amount; the crit effect then applies to what remains | — | pending designer |
| Second melee weapon for +1 MD | A proficient one-handed melee weapon in the off hand, with no shield; a two-handed grip doesn't count | `defenses` | pending designer |
| Melee Defense with no melee weapon wielded | Base 1 only; the proficient-weapon and even-Finesse bonuses need a wielded proficient melee weapon; a held shield still counts. Unarmed is no weapon unless a build lists an unarmed proficiency | `defenses` | pending designer |
| Stamina and strain at the start of a fight | Stamina at maximum, strain 0 | `resources.start` | engine convention |
| Declaring steps or blocks you can't pay for | Not allowed; stamina never goes below 0 | — | engine convention |
| Strain overage on an ability that costs no stamina (Fighter core) | The overage is still paid in stamina | — | pending designer |
| Multi-die steps (greataxe 2d6) | Each die can crit separately; two crit dice ignore 2 armor | — | pending designer |
| Finesse below 0 and crit range | No widening (odd count of a negative value is 0); the +3 cap can't be passed at FIN ≤ 6 | — | engine convention |
| Block solver and avoidable incapacitation | Lexicographic: avoid incapacitation first, then minimize w × injury + stamina (the review used a +1000 penalty, identical below 1000) | solver option | engine convention |
| Initiative timing | Rolled once per fight (5e-like); the packet only says "roll initiative" | — | pending designer |
| "No tiebreaker for now" | Tied creatures reroll 2d12 + bonus among themselves until untied; `higher_agility` and (for review-sim) `list_order` are the other values | `turn_order.tiebreak` | pending designer |
| Recovery timing vs the off-turn window | Recover at the end of your own turn, before anyone's off-turn window (packet step 2, then step 3) | — | pending designer |
| Recovery if you did nothing | Still recover | — | pending designer |
| What "incapacitated" stops | No actions, blocks, stamina spending or recovery; only the start-of-turn dying roll. Attacks on incapacitated creatures aren't offered (coup de grâce is silent) | `resources.recovery`, `dying` | pending designer |
| When a fight ends | As soon as a side has no active members, checked after every injury; a round cap (30 for duels, 20 for 1v3, as the review) counts as a draw. With a scenario objective (O1), the objective is checked first, then side-out, then the round cap: reasons `objective:<id>`, `objective_failed:<id>`, `side_out`, `round_cap`. Objective checks run after every injury, flee or surrender, after every completed move, and at the end of each round | scenario `round_cap`, `[[objective]]` | engine convention |
| Fight metrics | First mover = first in initiative; first-mover rate over decisive fights; winner untouched = took 0 HP; loser ends at = the loser's final HP; rounds = the round it ended in | — | engine convention |
| Chip-kill and look-ahead estimates | Exact expected outcomes by default; `sampled` reproduces the review's 40/30-sample estimates in its order and float arithmetic (lockstep uses it) | agent `estimator` | engine convention |
| 1v3 defender targeting | The lowest (stamina, HP) living attacker, ties to the first listed, 2 steps | agent `target` | engine convention |
| Scripted policies and actions already taken | Policies size steps with real trackers; identical to the review's (which assumed 0) for one attack per turn | — | engine convention |
| Over-budget parity builds | Allowed only in `data/builds/parity/`, marked `budget = "ignore"` (the review's "illustrative" grid builds) | build `budget` | engine convention |
| No System Shock in the review | `review-sim` uses a parity-only dying rule: at 0 HP or below a creature is out and rolls nothing | `dying` kind `none` | engine convention |
| What hidden stamina means | `stamina = hidden` with `builds = known`: observers see declared steps and blocks, that recovery happened, and wounds; a public ledger then reconstructs stamina exactly, so scripted agents play exactly as with public stamina. Hidden stamina changes bookkeeping load, not information, unless builds are unknown (needs priors; not built) | `information.stamina`, `information.builds` | pending designer |
| HP under hidden stamina | Wounds, and so HP, stay visible | — | pending designer |
| Perfect-block count reset (F6 option 2) | v0.9 resets every attack (`per_attack`). F6's "reset per attacker per round" reads two ways, both built as named values: `per_attacker_round` (an attacker's later attacks in a round continue its count; in the review's 1v3, where each attacker attacks once, this changes nothing) and `per_round` (one count per defender per round, shared, which makes focus fire harder on the defender). Neither matches "directly targets focus fire", so the option's wording needs the designer | `blocks.reset` | pending designer |
| Decision option counts (F11) | Commitment: 1 + max affordable steps; Blocks: affordable (perfect, grazing) pairs, plus the count not beaten on both stamina and injury | — | engine convention |
| All-adjacent arena (M1) | Everyone is in reach of everyone and there is nowhere to move, so no square is ever left and no OA is provoked. It stays the default for scenarios without a map (the parity runs); a scenario with `map` uses the grid | scenario `arena`, `map` | engine convention |
| Scripted agents on a grid | They approach the chosen target by the cheapest path using free movement only (least avoidance exposure, then shortest), attack if in reach, and never move off-turn; an agent whose policy commits no steps stands still. Avoidance and OAs are spec fields: `avoid = worth_it` (pay off an enemy whose OA's expected cost, block stamina + w × injury, is more than the price) or `always` or `never`; `oa = max` or `never`. In the all-adjacent arena they behave exactly as in M1 | agent spec | engine convention |
| Tactical agent v1 | Melee only: target by policy; attack from the reachable square with the fewest enemies able to engage it next turn (then least exposure, then shortest), buying movement only if its commitment stays affordable; after attacking, reach spacing (a reach weapon steps out of the target's reach) or a free-of-avoidance step to a less engaged square; off-turn, retreats when `retreat_engaged` (2) enemies could engage it, or one with stamina below `low_stamina` (1/3), to the square with the fewest engagers if strictly fewer and it costs at most half its stamina. Enemies' next-turn reach is free movement only, and their OAs are priced as if their off-turn track were empty (others' trackers aren't observed) | agent spec | engine convention |
| Tactical agent at range (M3) | Aim: the count with the best exact expected value (w × injury + the stamina the target spends + 10w × P(down), minus the cost), less the worst enemy reply it could then face (one ply, as the review's look-ahead) when an enemy could engage it next turn. Dive: when blocking the known roll from better cover saves more than the move costs. As an archer: re-draws its bow on its turn (free before using a weapon), steps out of reach before shooting when that costs at most 3 stamina, shoots once, steps away again, and readies a free quick-draw blade between turns when an enemy could engage it. Approaching, it prefers squares with cover from shooters among equally close ones. Scripted agents still never dive, and shoot with `aims` (3) if they hold a bow | agent spec | engine convention |
| Scripted approach at 0 stamina (M3) | A scripted agent approaches its target even when it can't afford to attack this turn (in M2 it stood still); only the `never` policy stands still. It never moves from a square that already reaches its target | agent spec | engine convention |
| Surrender (M4) | The packet has none. On a map, any active creature may surrender on its own turn: it's out of the fight (takes no turns, can't be attacked, threatens nothing), and its square is a body. A side with no one active left has lost | — | pending designer |
| Fleeing the map (M4) | Exit squares (`>` in a map) are floor; a creature standing on one may leave on its own turn and is out of the fight. Nobody leaves except through an exit | map legend `>` | pending designer |
| Who counts in a zone (O1) | Active creatures only: incapacitated, fled and surrendered creatures neither hold nor contest a zone | — | pending designer |
| Zone control (O1) | No default: each hold objective states `present` (any of its side's creatures in the zone), `uncontested` (its side in it, no enemy in it) or `majority` (more of its side than of the enemy) | objective `control` | pending designer |
| Hold scoring (O1) | No default: each hold states `consecutive` (rounds of control in a row), `cumulative` (rounds in total) or `final` (control at the end of the deadline round, as Lancer's Holdout), scored at the end of each round | objective `score`, `rounds`, `deadline` | pending designer |
| Reaching a zone (O1) | A creature who counts is counted once it stands in the zone at any objective check (where a move ends, not squares passed through mid-path), and stays counted after it leaves | — | engine convention |
| Escape (O1) | Through exit squares only (the fleeing row); a creature who counts is counted when it flees. Reach and escape fail as soon as too few creatures who count are still active to make up `count` | objective `count`, `who` | engine convention |
| Objective failure (O1) | The other side wins; objective scenarios have exactly two teams. A reach or escape deadline defaults to the round cap, so not getting out by the cap is a loss, not a draw | objective `deadline` | engine convention |
| Objectives as information (O1) | Public: every creature sees zones, who counts, progress and deadlines | — | engine convention |
| Objective agents (O1) | Agent spec `objective = "kill"` (default: ignore objectives, as before; the control) or `"first"`: pursuers head for the zone or an exit (tactical: buying movement up to half its stamina; scripted: free movement only), flee as soon as they can when escaping, stay in a zone they hold (off-turn retreats too), and attack only what is in reach on the way; a reach pursuer already counted fights as in kill mode. Deniers attack the pursuer who counts closest to its goal; tactical deniers in a contested hold step into the zone when free movement gets them there without provoking | agent spec `objective` | engine convention |
| NPC profiles (M4) | Agent configuration, not rules (the packet leaves NPC aggression profiles out of this version): data files that set the tactical agent's commitment (with a heavier one against a target below a stamina fraction), target choice (`focus` attacks the enemy the most allies already threaten), fall-back, flee and surrender thresholds | agent spec `{kind = "npc", profile = ...}` | engine convention |
| Packet versions as presets (0.9.1–0.9.3) | `v0.9.1`, `v0.9.2` and `v0.9.3` select each version's rules (`v0.9.3` has 0.9.2's components: its changes are all after a fight); `v0.9` stays the v0.9 packet, and `review-sim` and `review-candidate` stay built on it, so earlier results and the parity gate are unchanged. The baseline was `v0.9.3` from 2026-11-08 and is `v0.10.0` from 2026-11-11 (next row). The parity suite stays on `review-sim`; tests and suite sections that reproduce the review (Table 5) name `v0.9` | presets, `BASELINE` | ruled 2026-11-08 |
| Packet 0.10.0 as a preset | `v0.10.0` is `v0.9.3` with the ranged package's switches (the rows below). The bows, Piercing, Precise and the +1 / +1 shield are equipment, in the `v0_10` table (`data/equipment/v0_10.toml`). A scenario, `se table` or `derive` that names no table gets its RuleSet's own: `v0_10` under linear bands, `v0_9` otherwise (`equipment_for`), and a written scenario records the table it used. Derive refuses v0.9's bows under linear bands and 0.10.0's bows under v0.9's ranges, so the two can't be mixed silently. **`v0.10.0` is the baseline** (`rules.ruleset.BASELINE`): the library's scenarios and milestone suites name it, and scenarios and sweeps without a ruleset and `se table` default to it. Suite rows that were variants on `v0.9.3` are variants on it; F3 option 1's row is now the same rules as the baseline, since 0.10.0 adopted it | `v0.10.0`, `BASELINE`, scenario `equipment` | ruled 2026-11-11 |
| The aim limit's "damage roll" (0.10.0) | The weapon's dice faces plus its Strength terms (after F8's `str_cap`, if set) and any constant; other attribute terms (the shortbow's Finesse) count like aim. Precise: the higher of that and Finesse after armor penalties. The range penalty lowers the total but not the limit; a critical bonus can take a shot past it | `ranged.aim_limit` | ruled 2026-11-11 |
| The defender knows the aim limit (0.10.0) | Yes: the dice are rolled openly, so the block request (and the reaction request) carries the limit | — | engine convention |
| Free aim die order (0.10.0) | The weapon's die, then the free aim die, then the aim steps. Under v0.9's bands (not a 0.10.0 combination) the dropped dice are the first bought aim steps and the free die always rolls | `ranged.free_aim_dice` | engine convention |
| Band width inputs (0.10.0) | Finesse after armor penalties, as everywhere; Strength is the build's (armor doesn't lower it). Band 1 runs out to one band width and a partial band counts as a full one, on the grid's metric (Chebyshev). With no maximum range, every enemy not in total cover is a target if the band width is above 0 | `ranged.bands = linear` | pending designer |
| The reaction to a shot (0.10.0) | One off-turn move to any square it can reach, as M3's dive; the shot isn't rechecked for line of sight. The range penalty is measured from the target's square once the move, and any OAs it provokes, are done | `ranged.range_measured` | pending designer |
| "+1 if you moved in reaction to this shot" (0.10.0) | Any reaction that moves at least one square, whatever it does to cover. Ranged Defense only: a target that closes into the shooter's reach blocks with Melee Defense and no +1 (the packet lists the +1 under Ranged Defense and says only cover applies either way) | `ranged.reaction_bonus` | ruled 2026-11-11 (for now) |
| Point-blank OAs from enemies in reach at declaration (0.10.0) | "When the shot is declared" is when the target is chosen, before aim is bought; nobody can move between then and the target's reaction, so it's the same check as just before the reaction. At resolution, the enemies that threatened the shooter then and still do may attack, lowest initiative first. The range band isn't fixed at declaration: the shooter chooses aim knowing the penalty at the target's square then, and the reaction can change it | `opportunity.point_blank_eligible` | ruled 2026-11-11 |
| Piercing in the engine (0.10.0) | Comes off armor before critical dice, floored at 0, for shots and melee alike; the defender is told the armor it faces after Piercing. A `hammer` property in a weapon table is Piercing 1. Heavy Swing's 2 counts the same way: the defender is told the armor left after both | weapon `piercing` | engine convention |
| Ranged Defense from even Agility (0.10.0) | `defenses.ranged_mode = dodge_folded` (Review F3 option 1) is the same rule: 1 + 1 per even Agility at the armor's step + shield. The name stays for parity | `defenses.ranged_mode` | ruled 2026-11-11 |
| When Melee vs Ranged Defense is judged (switch on 0.10.0) | `after_reaction` (0.10.0): from where the target ends its reaction. `declaration`: from where it was when the shot was declared, so closing into reach keeps Ranged Defense (and its +1 for moving) and backing out keeps Melee Defense. Cover is judged after the reaction either way | `ranged.defense_timing` | pending designer |
| A cap on purchases in a reaction to a shot (switch on 0.10.0) | 0 (0.10.0): any number, as for any off-turn move. N: at most N off-turn purchases, so N × the target's squares per purchase | `ranged.reaction_purchases` | pending designer |
| The defense swap needs a single purchase (switch on 0.10.0) | Off (0.10.0). On: if reaching or leaving the shooter's reach took more than one purchase, the defense judged at declaration stands. Purchases are counted from the move's length (squares per purchase, rounded up). The reaction request's per-square defense assumes the fewest purchases to each square | `ranged.swap_single_purchase` | pending designer |
| The critical bonus and the aim limit (switch on 0.10.0) | After the limit (0.10.0, ruled). `crit_in_limit = true`: the bonus counts toward it, so a shot never takes more HP than the limit | `ranged.crit_in_limit` | pending designer |
| Crit rules C′ and C on shots (switches on 0.10.0) | 0.10.0 is the solver study's rule A (aim dice never critical). `crit.aim_dice_widen = false`: aim dice that can crit do so only on a 6. `crit.per_shot_cap = N`: a shot counts at most N critical dice; melee steps are never capped. C′ = aim dice can crit, no widening, cap 1; C = aim dice can crit with the weapon's widening, cap 1 | `crit.aim_dice_widen`, `crit.per_shot_cap` | pending designer |
| Named packages on 0.10.0 (not packet versions) | `v0.10.0-cover-only`: range and defense judged at declaration (the requirements' "reaction changes cover only"; the reaction still earns cover and +1). `v0.10.0-crit-c-prime` and `v0.10.0-crit-c`: crit rules C′ and C. The shortbow variants, sizes, a maximum range, a crit-widening cap and a per-shot aim reset aren't built: 0.10.0 ruled or shelved each | presets | engine convention |
| The one-round harness | `analysis.one_round.solve_round`: archers shooting one target in one round, solved exactly as the design study's solver does (zero-sum on 100 × down + 3 × HP + stamina; no reaction, no recovery). It matches `tests/solver/bows5.py` on every figure | — | engine convention |
| Step-by-step play (`se play --step`) | Each command replays the trial from its seed with the answers so far and stops at the first decision without one; answers are `se play`'s typed lines, parsed by the same agent and checked by the broker's own checks before the battle sees them, so a bad one is reported (exit 11) and never appended. Exit 10 means a decision is waiting, 0 that the fight is over. A chat's seconds aren't logged (null), so `se load --session` counts its decisions untimed | — | engine convention |
| Engine agents and the reaction (0.10.0) | When the rules make moving pay for more than cover, the tactical agent weighs every reachable square by this shot's exact blocks less the move's cost; it doesn't value where it ends up (next to the archer, say). The tactical archer's aim counts the range penalty at the target's square now, the aim limit and Piercing, but not the target's possible reaction or its +1. Scripted agents never react | — | engine convention |
| Engine agents and uncapped opportunity attacks (0.9.1) | Under a cap, an engine agent takes the largest OA the cap allows, as through M5. With no cap, it takes the steps its commitment policy would put into an attack on its own turn (fixed:2 takes 2, chipkill 2 or all-in for a likely kill), as far as its stamina goes, rather than sinking its whole pool into one OA | agent policy | engine convention |
| Variant switches that need an OA cap | With no cap (`cap_rule = none`), the per-square cap and avoidance priced at the attacker's cap are refused as configuration errors. `cap_rule = weapon_base` on a 0.9.1 base reintroduces a weapon-based cap, as F9 option 1 | `opportunity.cap_rule` | engine convention |
| Intelligence's AP rules (0.9.1) | They act only in the build's budget check. Bonus AP count from the build's current Intelligence, which is what "applies retroactively" means for a build made at its level | `resources.core_discount`, `resources.bonus_ap` | engine convention |
| Nightly HP recovery (0.9.1) | Not modeled: the engine plays single fights, and no rest between fights exists yet | — | engine convention |
| Sweep and comparison seeds | Trial seeds key on (master seed, scenario and agent pairing, trial), not the RuleSet, so RuleSets are compared on the same dice | — | engine convention |

Off-turn order can move headline numbers on its own (it decides who ends adjacent to whom), so it gets a sensitivity run in the phase suite until it is decided.

## Verification

The engine is trusted only once it reproduces every worked example in the packet exactly and the review's published tables within sampling error; after that, invariants and determinism checks keep it trustworthy as rules change.

**1. Golden tests from the packet,** with scripted dice where rolls matter:

| Packet example | Must reproduce |
|---|---|
| Choosing Blocks | 9 damage vs MD 4, armor 2: 1 perfect + 1 graze = 2 stamina, 0 injury |
| Melee Attack | 2 steps = 5 stamina, 15 damage; block lines 10/7/5/4 stamina give 0/0/1/3 HP. 0.9.2's critical-die case: 16 damage, armor 0; 4 perfect blocks give 0 HP, 2 perfect + 2 grazing give 2 + 1 = 3 HP |
| Strain | 9 stamina for the spell at strain 10 of 8 |
| Two Aimed Longbow Shots | 20 stamina |
| Off-Turn Escalation | 10 stamina; the OA needs a cap of at least 3 in v0.9, and none from 0.9.1 |
| Avoiding Opportunity Attacks | 2, then 1, then 1 |
| System Shock | The five-step sequence: −2 HP / 2 Shock through −6 HP / 1 Shock (pure `dying` transitions, in M0) |
| Sample Character | v0.9: HP 8, stamina 14, MD 4, RD 3, Dodge 1, movement 6, 2 squares per off-turn purchase, crit 7–8, OA cap 2. 0.9.2: HP 10, stamina 16, the same defenses and movement, 1 square per extra purchase, initiative + 0, no OA cap |

**2. Parity with the review.** Tables 1 and 8 must match exactly, since they are deterministic. For fights, the engine runs in lockstep with the old simulator (ruled 2026-11-03): the oracle's global `random` is replaced by a seeded stream and the engine draws every die from one shared stream, so both see identical faces, and every fight behind Tables 2–4, 7, 9 and the Addendum grid must come out identical (`se suite parity`, `tests/parity/test_lockstep.py`). The suite's report then sets the engine's figures, at the review's trial counts, beside the review's printed ones; a printed figure outside the engine's interval is investigated, not assumed to be an engine bug: the review's figures are rounded and sampled, and the old simulator can be wrong too. Table 5 (ranged) waits for M3.

**2a. Differential tests against the old simulator.** `sim.py` lives in `tests/oracle/` unmodified. Its pure functions (`best_block`, `attack_cost`, `max_steps`, `crit_effect` for every `CRIT_MODE`, `BLOCK_SLOPE` and `STEP_SLOPE`) are compared with the engine's over thousands of random inputs; scores must match exactly, and the chosen (perfect, grazing) pair must match wherever the old tie-break (lower cost at equal score) applies. Its `make_fighter` builds are checked against `derive()`. Its `experiments.py`, `variants.py` and `grid.py` runs become the parity scripts, at the same trial counts, under the `review-sim` preset.

**3. Property tests** (`hypothesis`) over random builds, rule variants and decisions: stamina stays within 0 and max; trackers reset when the rules say; every charge equals the quote the agent saw; no incapacitated creature acts; a replayed log reproduces the battle; a RuleSet survives a round trip through TOML.

**4. Geometry tests:** hand-drawn reach lines, including lines that touch a corner or squeeze between two walls; steps around corners under each corner reading; threat maps with reach weapons and walls; path costs with avoidance payments; reachable sets against brute force (`tests/geometry/`, M2); cover by the corner method, with lines along seams, through corner points and past creatures (`tests/geometry/test_los.py`, M3).

**5. Traceability.** Each rule component and procedure declares what it implements (`cites = ("Packet: Blocking", "Ledger MV-3")`). A generated report lists packet sections with no implementation or no test, so gaps show up when the packet changes.

**6. Determinism in CI:** a fixed set of seeded battles must produce the same event-log hash on every commit unless a rule change is declared.

## Milestones

Six milestones, each ending at a gate of known numbers, so the engine is useful for Phase 0 and Phase 1 decisions after the first one rather than only at the end.

| Milestone | Builds | Unlocks | Done when |
|---|---|---|---|
| M0 Foundations | dice, RuleSet and registry, builds and derivation, Pricing, exchange resolution, block solver, exact calculators | Phase 0, Phase 1 (static) | Packet examples pass; Tables 1 and 8 match exactly; matches sim.py on random inputs |
| M1 Turn engine, no movement | timeline, StateOps, events, broker, scripted policies, runner, sweeps, metrics, all-adjacent arena | Phases 1–3, first pass | Every fight behind Tables 2–4, 7, 9 and the Addendum grid identical to the oracle in lockstep; parity report beside the review's figures; same seed gives the same log |
| M2 Grid and positioning | maps, threat, pathing, square-by-square movement, OAs, avoidance, off-turn windows, tactical agent v1 | Phases 3 and 4 | Packet movement and OA examples pass as battles; Addendum 2 retreat costs exact (calculator and played battle); geometry tests pass; 1v3 (open and corridor), reach-chokepoint and retreat scenarios run for both agent families, with the report; M1 lockstep parity still identical and all-adjacent logs unchanged apart from the digest; the broker never rejects an engine agent on random maps; pinned grid-battle hashes (ruled 2026-11-03) |
| M3 Ranged | sight lines and cover, range bands, aim, dive window, point-blank OAs, drawing weapons, archer agent | Phase 5 | Table 5's static part matches exactly within the review's sampling error (`se table 5`); archer scenario on three maps for both agent families (`se suite ranged`); ranged golden battles, cover geometry tests and random-play legality pass; M1 parity and the pinned M1 and M2 logs unchanged apart from the digest |
| M4 Equipment and NPC profiles | variant weapon and armor tables, NPC profiles, 3v3 integration scenario, report generator | Phase 6, F6 dial | Full phase suite in one command (`se suite phase`), printing Tables 1, 2, 3, 4, 5, 7 and 8 in the review's layouts; F4 and F8 variants selectable from data and switches; NPC profiles, fleeing and surrendering in play; earlier logs unchanged apart from the digest |
| M5 Content hooks and load | abilities, strain and overage, class cores, System Shock, control-track stub, human CLI with timing, load report | Phases 7 and 8 | Class cores priced in sims (`se suite cores`: each core and candidate ability off and on in duels and one against three, and the cores against each other); the human CLI (`se play`) logs a timed session that `se load` reports; one human session logged, played by the designer; earlier logs unchanged apart from the digest |

Phase 4 work can start as soon as M2 lands, in parallel with Phase 1–2 decisions, as the fix-order doc allows. An optional M6 adds the search auditor and an HTML replay viewer, built only if agent quality or playtest review calls for them.

**Proposed, not adopted: M7 Objectives.** Scenario objectives beyond downing every opponent (reach, escape, hold, morale break, then objects, carrying, escort and secondary objectives), as scenario configuration with unstated rules readings as named switches. Brainstorm, phases O1–O5 and the questions for the designer are in [OBJECTIVES_PLAN.md](OBJECTIVES_PLAN.md). Phase O1 (reach, escape, hold; `se suite objectives`) is built as [OBJECTIVES_O1_PLAN.md](OBJECTIVES_O1_PLAN.md) describes.

## Risks

The biggest risk is that agent behavior, not the rules, drives the conclusions; the plan answers it by reporting every headline result across at least two agent families and auditing with search.

| Risk | Mitigation |
|---|---|
| Scripted or tactical agents manufacture or hide a dominant strategy | Report across agent families; search auditor in M6; human sessions in M5 |
| Grid fights are too slow for big sweeps in Python | Exact calculators for single-exchange questions; cached geometry; maps ≤ 40 × 40; multiprocessing; profile before optimizing |
| Silent rule readings get baked into results | Assumptions register; every result stamped with RuleSet digest and switch values |
| The engine grows into a virtual tabletop | No interface beyond ASCII and the CLI until M6, and only if review needs it |
| Rule changes outpace the code | Traceability report and golden tests flag what a packet revision broke |
