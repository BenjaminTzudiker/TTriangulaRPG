# Scenario objectives: brainstorm and phased plan

*Status: proposal (2026-11-07). Not yet part of the milestone plan in `ENGINE_PLAN.md`; the detailed implementation plan for phase O1 comes next. Paths below are relative to `sim/src/stamina_engine/` unless they start with `sim/` or `rules/`.*

## Context

Today a fight ends only when one team has no active members (`Battle.check_end`, `sim/src/stamina_engine/engine/battle.py:102`) or the round cap is reached, which counts as a draw. Every agent's turn logic is "pick an enemy, approach, attack" (`agents/tactical.py:176`, `agents/scripted.py:345`). The packet itself says otherwise. *Running the Game* says "Combat usually ends when one side retreats, surrenders, is defeated, or achieves its objective." ENGINE_PLAN:365 already lists "an objective square" as a planned end condition, but it was never built. The review's Addendum 2 concludes that the core economy is deliberately flat: "duel interest must come from asymmetries". Objectives are the cheapest source of asymmetry the engine can measure.

The goal is to measure how the stamina rules behave when killing everyone isn't the point. This step produces the brainstorm and a phased plan. The detailed implementation plan comes later.

## What the research says (design lessons to build in)

- **An objective must not reduce to "kill them all".** If killing everyone is still the best route, the objective is decoration. ([Woo The Moon](https://woothemoon.bearblog.dev/how-is-combat-objective/), [Draw Steel playtest discussion](https://redlib.andus.dev/r/rpg/comments/1hso5gt/how_have_you_seen_rpgs_and_your_own_homebrew_with)). The engine can test this directly: run a kill-first agent against an objective-first agent on the same scenario.
- **Every objective needs a clock and a clear failure condition.** These include a round deadline, a failure threshold, and when the objective is scored. Lancer's Holdout checks its zone only in the final round, which punishes turtling. ([Lancer GM guide](https://owacsender.substack.com/p/the-gms-guide-to-building-lancer), [Sitrep Showdown](https://knowledgeandknicknacks.blogspot.com/2024/01/sitrep-showdown-outpost-assault.html))
- **Losing the fight can still mean winning the encounter, and partial success should be graded.** ([PF2e GM Core, secondary objectives](https://2e.aonprd.com/Rules.aspx?ID=2733), [Into the Breach bonus objectives](https://www.gamedeveloper.com/design/reimagining-failure-in-strategy-game-design-in-i-into-the-breach-i-))
- **Secondary objectives make a party split its attention.** Examples are a captive, a fleeing foe to capture, or a ritual to stop. They work best sparingly. (PF2e GM Core)
- **Morale and retreat triggered at dramatic milestones** beat both fights to the death and morale checks every round. ([Angry GM on morale](https://theangrygm.com/flesh-is-willing-spirit-failed), [The Morale Mechanic](https://kateplays.substack.com/p/the-morale-mechanic))
- **Established catalogues:** Lancer's sitreps (Control, Escort, Extraction, Holdout, Gauntlet, and others) and Draw Steel's objectives (escort an NPC, grab and escape, keep enemies from a point). Both are built-in encounter frames rather than add-ons.

## Brainstorm: objective catalogue

The catalogue is built from a few **primitives**, so each new objective is configuration rather than new code:

- **Zone:** a named set of squares.
- **Object:** something static or carryable that can have hit points or a progress track.
- **Clock:** a round deadline or a scoring schedule.
- **Marked creature:** a VIP, leader or captive.

| # | Objective | Primitives | Which finding it stresses |
|---|---|---|---|
| 1 | **Break through / Reach**: get N creatures into a zone or off an exit | zone, clock | F10 cheap movement and range; MV-1 chaser economics |
| 2 | **Escape / Extraction**: the whole side leaves the map, pursued | exits, clock | Addendum 2 retreat economics (4:1 to 11:1 against the fleer); F14 (no retreat at 0 stamina) |
| 3 | **Hold / Control**: score a zone each round, or only in the final round | zone, clock, control rule | F9 opportunity attacks and reach; F3 archers against people holding a point; stamina banking against spending |
| 4 | **Escort / Protect VIP**: a weak ally must survive or reach the exit | marked creature, zone | F6 focus fire with no answer; a defender's off-turn tools |
| 5 | **Defend object**: a static object with HP (a gate, ritual circle or wagon) that enemies must break | object with HP, clock | Attackers choosing between hitting the object and fighting the defenders |
| 6 | **Interact / Progress**: a lever, ritual or disarm that takes several turns and may be interrupted | object with progress track | F1 commitment (stamina spent on progress isn't spent on attacks or blocks); the on-turn surcharge |
| 7 | **Retrieve / Carry**: pick up an item and carry it out; it drops when the carrier goes down | carryable object, exits | Off-turn movement; opportunity attacks; focus fire on the carrier |
| 8 | **Decapitation**: down the leader, and the rest break | marked creature, morale | NPC profiles (H-6) as the lethality dial |
| 9 | **Survive N rounds / reinforcement waves** | clock, spawns | F7 death spiral; regeneration across a long fight |
| 10 | **Capture alive**: down the target without killing it | marked creature, Dying and Death | How often the injury and death rules allow a nonlethal finish |
| 11 | **Asymmetric pairs**: each side has its own objective (attack against defend, ritual against stop-the-ritual) | any two of the above | First-mover advantage when the sides want different things |
| 12 | **Morale / break**: a side withdraws on casualties, the leader going down, or HP thresholds | per-side trigger | The packet's "NPCs value their own survival" (GM-1) |
| S | **Secondary objectives** scored alongside the main one: protect a bystander, keep the hostage alive, "nobody seriously hurt" | any primitive | Graded outcomes; the packet's cost of "carrying the injuries" |

Recommended first wave: 1, 2, 3 and 12. They need only zones, exits, clocks and existing movement, with no new action types and no new rules readings. They also test the most-flagged findings (F6, F9, F10, retreat economics).

## High-level implementation plan

### Where it lives
- **Objectives are scenario configuration, not RuleSet components.** This follows the precedent of the equipment table (ENGINE_PLAN:497). Fights without objectives keep identical event logs, so parity, golden and determinism tests are unaffected.
- **Rules readings the packet doesn't state become named switches in a new RuleSet component.** Examples: what interacting costs, how carrying affects movement, who controls a zone, whether an object can be attacked. The default is off/absent, so existing digests don't change. Each switch gets an Assumptions-register row marked *pending designer*.

### Pieces
1. **Map overlay.** Named zones in the scenario TOML, as rectangles or square lists, or as a second ASCII layer, because letters on the map are already spawn markers. Exits stay as they are. Generalise "exit" to "zone with role exit" only if that turns out to be needed.
2. **Objective state and StateOps.**
   - An `ObjectiveState` on `BattleState` holding progress, holder, control score and status.
   - It is written only through new StateOps methods (advance, pick up, drop, damage object, complete). These are modelled on the existing `advance_control` progress stub (`engine/stateops.py:195`).
   - Each method emits new event types.
3. **End conditions.** `check_end` becomes an ordered list of end conditions, with `side_out` first and unchanged.
   - Each condition is evaluated at defined hooks: after an injury, after movement, at end of turn, at end of round.
   - The outcome reason becomes `objective:<id>`, `side_out`, `broke` or `round_cap`.
4. **Graded outcome and metrics.**
   - `BattleResult` gains per-objective status.
   - `fight_row` and `summarize` report:
     - each objective's success rate with a Wilson interval;
     - fled and surrendered counts (a gap ENGINE_PLAN:395 already promised);
     - the cost of success in HP, deaths and stamina.
5. **Agents.**
   - `Observation` exposes objectives.
   - `TurnCommand` gains Interact and PickUp answers. These go through the broker and `option_count`, and every agent family must answer them.
   - The tactical agent gets a goal layer that weighs objective value against kill value. Its existing `_approach` already paths to any square.
   - Scripted control policies: **kill-first**, **objective-first** and **screen/bodyguard**.
   - NPC profiles gain a priority field and morale triggers.
6. **Suite.** `se suite objectives` runs a handful of scenarios across agent families. Kill-first against objective-first is the standard control, and it answers "does this objective matter?"
7. **Docs.**
   - A proposal to amend ENGINE_PLAN with a new milestone (M7, Objectives) and a "Done when" gate.
   - New Assumptions rows.
   - Updates to `USAGE_FOR_CHATS.md`.
   - One worked plugin example in `sim/examples/`.

### Phases
- **O1: zones and movement objectives.** Reach, Escape, Hold and the end-condition hooks. No new actions.
- **O2: outcomes and metrics.** Graded results, secondary objectives, the fled/surrendered metric gap, and the suite with kill-first and objective-first controls.
- **O3: morale and break.** Per-side triggers in NPC profiles; this is decapitation.
- **O4: objects and interaction.** Defend, Interact/Progress and Retrieve/Carry, plus the new answer types. This phase is blocked on designer rulings about interaction cost.
- **O5: escort and VIP, survive and waves, asymmetric pairs, capture alive.**

### Questions for the designer (go into the Assumptions register, never silent defaults)
- Does interacting with an object cost stamina? Does it count as an action for the surcharge? Can it happen off-turn?
- Does carrying an object slow you or block attacks? Does it drop when you go down, and can someone pick it up off-turn?
- How is a zone controlled? Options include more active creatures, any uncontested presence, or presence at the end of the round.
- Is the map edge an exit in escape scenarios? ENGINE_PLAN:451 currently treats it as a wall.
- Defense and HP for objects; whether damage interrupts progress.
- What a morale trigger is, and whether it should be the shelved H-6 profiles brought back.

## Next step

A detailed implementation plan for O1, written once the designer has seen the questions above. Later phases will be gated on:
- unchanged event-log hashes for every existing scenario;
- golden tests for each objective type;
- a kill-first against objective-first differential that shows a measurable difference.
