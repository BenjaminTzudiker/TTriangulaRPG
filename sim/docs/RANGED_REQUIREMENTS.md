# Simulator requirements: candidate ranged package, reactions to shots, and step-by-step play

*Copied on 2026-11-23 from the claude.ai project doc `claude/Sim_Requirements_Ranged_Package_2026-11-11.md`, unchanged except that `CLAUDE.md` now reads `AGENTS.md`. [RANGED_TESTING_PLAN.md](RANGED_TESTING_PLAN.md) is the plan that answers it. A frozen record: where it disagrees with the packet or the changelog, they win.*

*Status: requirements for the coding agent (2026-11-11). This is not an implementation plan. The coding agent writes the plan, following `AGENTS.md` and `sim/docs/USAGE_FOR_CHATS.md`.*

## Update: the designer's rulings, packet 0.10.0 (2026-11-11)

The designer has committed most of this as **packet 0.10.0**. Its rules text and the 0.10.0 section of `rules/CHANGELOG.md` are authoritative; where this doc disagrees, they win. Build the preset as **`v0.10.0`** (not `ranged-candidate`). Keep the other readings below as switches for experiments.

What the `v0.10.0` preset uses:

| Area | Setting |
|---|---|
| Reaction timing | The target reacts **after the roll, before blocks**, as in v0.9.3. Keep `before_roll` as a switch (`reaction_point`): the designer may revisit it |
| Judged after the reaction | Defense (Melee vs Ranged), cover and the range band |
| Reaction purchases | No cap |
| Opportunity attacks from shooting | Provocation is decided at declaration. An enemy must be able to attack both at declaration and when the attacks come after the shot: it must still have the shooter in reach and not be incapacitated |
| Band-width bonus | Finesse 1/3/5 (+1/+2/+3 squares). The split with Cunning is shelved (packet's Not in This Version); keep it as a variant |
| Size | Shelved (packet's Not in This Version): no size scaling in v0.10.0, −2 per band for every target. Keep the size table as a variant |
| Strength shortfall | A band width of 0 or less means the bow can't fire. No minimum band width |
| Ranged Defense sources | Base 1; +1 if the target moved in reaction to **this** shot (per shot: against a second shot it has to move again); +1 per **even** Agility value, with the existing medium and heavy armor steps (as for Melee and Dodge); shield +1 |
| Shields | **+1 Melee Defense and +1 Ranged Defense** (was +2/+2). This changes melee too. A second weapon in the off hand stays +1 Melee Defense and gives no Ranged Defense |
| Crits | Aim dice are never critical (rule A); the crit bonus applies after the aim limit |
| Shortbow | Shot cost 3, 1d4 + FIN. Finesse adds to the total, but like aim not to the wound directly. Precise: HP lost ≤ the higher of the d4 and FIN, after armor; crits after. See the packet's worked example. The chat's solver found this much deadlier than the version without FIN in the total (bow doc, addendum 7) |
| Cover | Half +1, three-quarters +2; a dive fully behind cover counts as three-quarters |

## 0. Why this is needed

The ranged design work (project docs `claude/Ranged_*`, 2026-11-08 to 11) has so far been tested only with small exact solvers. Those solvers model one round, abstract distance as a number, and play optimally. They can't answer the questions that are left, which depend on maps, movement and several rounds:
- Does reacting to a shot (diving for cover, closing to melee, backing off) make archer-vs-melee fights interesting, or does it create a dead zone around archers?
- How lethal are two or three archers at normal ranges, not just point blank?
- Do the bow niches the solvers found (shortbow up close, longbow against soft targets, warbow against armor and at range, superheavy against armor and at extreme range) survive real fights?

The engine already has most of the movement machinery: the grid, off-turn purchases, dives to any reachable square, cover by the 5e corner method, and opportunity attacks from shooting in reach. What it's missing:
1. **The candidate ranged rules,** as named variants.
2. **Switches for the timing questions** the designer hasn't ruled on.
3. **Agents** that make the reactions the rules allow.
4. **A way for a chat agent** to play a combatant one decision at a time.

## 1. Ground rules

- **The baseline stays as it is.** `v0.9.3` must reproduce exactly. Everything here is a new named variant, or a new preset built on `v0.9.3` (working name `ranged-candidate`).
- **Every reading the packet leaves open becomes a switch** with an Assumptions register row in `sim/docs/ENGINE_PLAN.md`, marked "pending designer".
- **Provenance as in the usage doc.** RuleSet digest, code and source hashes, and plugin hashes on every result.
- **Tests for every component,** plus the parity tests in §8.

## 2. Range bands (R1)

**R1.1. Linear bands with a flat penalty.** Range from the shooter to the target is split into bands of a fixed width per weapon.
- The first band has no penalty; each further band subtracts a flat amount from the shot total: `penalty = per_band × floor((distance − 1) / band_width)`.
- The total is floored at 0. A total reduced to 0 has no critical dice.

**R1.2. Parameters:**
- `per_band`: default 2.
- **Band width per weapon** (§3).
- **Attribute band bonus:** +N squares per band. Which attribute is undecided, so make it a parameter, with N capped at a parameter (default 3).
- **Strength shortfall:** −1 square per band per point of Strength below the weapon's requirement.
- **Optional maximum range:** default none. The penalty is the limit.

**R1.3. Target size scales the per-band penalty.** Proposed table:

| Size | Per-band penalty |
|---|---|
| Small | ×2 (−4) |
| Medium | ×1 (−2) |
| Large | ×½ (−1) |
| Huge | 0 |

Make the table data, and give a creature's size in its build or stat block. Size has no effect inside the first band. Allow an optional Ranged Defense bonus for Small creatures.

**R1.4. Keep the existing `v0_9`, `minus_d6` and `none` band variants** for parity.

**R1.5. Ranged Defense sources** (the designer's placeholders; each a parameter):
- **Base 1.** It becomes 0 if Agility is below 0.
- **+1 if the defender moved.** What counts as having moved is undecided, so make it a switch:
  - any movement on its last turn;
  - paid movement only;
  - movement since its last turn, including off-turn movement.

  The engine has to track this.
- **+1/+2/+3 from attributes.** Switch between Agility 1/3/5, and Agility 1/5 plus Cunning 3.
- **+1 for a shield.**
- **Cover: +1 half, +2 three-quarters.** A dive that ends fully behind cover counts as three-quarters. These replace the packet's +2/+5 in this preset.
- **Point-blank shots.** Cover also applies to Melee Defense against point-blank shots, as the packet says. Keep that as a switch.

## 3. Bows and piercing (R2)

**R2.1. Bow fields:**
- draw cost (the flat per-shot cost, replacing `base`);
- Strength requirement;
- band width;
- damage formula;
- wound cap formula;
- piercing;
- number of free aim dice;
- hands.

**R2.2. Aim never adds to HP lost** (ranged only; there's no general wound cap, and melee is unchanged). Aim dice make the shot harder to block but don't add to the wound: HP lost to one shot is at most the bow's damage roll (dice + modifier).
- **The critical bonus applies after this limit** (designer ruling, 2026-11-11).
- **Keep the switch `crit_in_cap`** for parity, defaulting to "outside".

**Shortbow property (Finesse).** Some aim can reach HP, up to Finesse. The wording has two readings; implement both as variants:
- **R1:** HP lost ≤ d4 face + FIN.
- **R2:** HP lost ≤ max(d4 face, FIN).

**R2.3. Piercing N: the weapon ignores N armor.**
- Stacks with critical armor-ignore.
- Floored so effective armor ≥ 0.
- Generalize the packet's Hammer property into it (Hammer = pierce 1), so melee hammers can use it too.

**R2.4. Candidate table**, as a new weapons file (e.g. `data/weapons/ranged_candidate.toml`); `v0_9.toml` stays as it is.

| Bow | Damage | Wound cap | Draw | Band | Strength required | Pierce |
|---|---|---|---|---|---|---|
| Shortbow | 1d4 (default; 1d6 as a variant) | per the shortbow property (R2.2) | 2 | 2 | 0 | 0 |
| Longbow | 1d8 + STR | die + STR | 4 | 3 | 1 | 0 |
| Warbow | 1d10 + STR | die + STR | 6 | 4 | 3 | 1 |
| Superheavy | 1d12 + STR | die + STR | 8 | 5 | 5 | 2 |

All bows have one free aim die (R3.3).

**R2.5. Multi-die damage** (e.g. 2d8) supported for variants. Each die that rolls in its critical range is a critical die.

## 4. Aim and the shared counter (R3)

**R3.1. Aim die.** Each aim step adds `aim_die` (default 1d6). A switch says whether Finesse is added (candidate: no).

**R3.2. One shared on-turn counter.** Draws and aim steps are both actions on the existing on-turn surcharge, the same counter melee attack steps use:
- a draw costs `draw + actions so far`;
- each aim step costs `aim_base (1) + actions so far`;
- each one advances the counter.

A variant resets aim escalation per shot while draws still escalate.

**R3.3. Free aim dice** come with every shot. They cost nothing and don't advance the counter.

**R3.4. A shot with no aim never misses** under the candidate bands. The v0.9 minimum-aim rule belongs to the `v0_9` band variant only.

## 5. Critical dice on shots (R4)

The engine currently defaults `crit.aim_dice_can_crit = True`, uncapped and Finesse-widened (`rules/exchange.py` uses the weapon's widening for aim dice). That's the review's assumption.

**The designer's current position:** keep the existing rule until there's a reason to change it, which means only the bow's damage die can crit (rule A). The candidate preset should use A. The packet's TODO is still open, and the solver study rejects that reading: it makes the Finesse shortbow the best single-archer weapon against plate.

**Switches needed:**
- `aim_dice_can_crit`: no / yes.
- `aim_dice_widen`: as the weapon / none (aim dice crit only on a 6).
- `per_shot_crit_cap`: none / 1. Ranged only: melee steps are untouched, so the greataxe's 2d6 can still crit twice.
- `crit_in_cap` (R2.2).

**Named configurations the studies used** (each crit ignores 1 armor and adds +1 if anything gets through):

| Name | Rule |
|---|---|
| A | Only the bow die can crit (Finesse-widened) |
| B | Every die can crit; each counts |
| C′ | Aim dice crit only on a 6; at most one crit per shot |
| C | Every die can crit; at most one crit per shot |

**Optional table switch:** cap widening so every die keeps at least one non-critical face. A d4 at Finesse 5–6 would crit on 2–4 instead of always.

## 6. Reactions to a shot (R5)

The target may react after the roll with off-turn movement. Today the engine judges reach after the dive (register row "The dive (M3)") but measures range at declaration. The designer is weighing two consistent options, so each piece needs its own switch.

**Switches:**
- `defense_timing`: `declaration` | `after_reaction` (current). Decides whether the shot uses Melee or Ranged Defense, which also settles the row "Diving out of a point-blank shooter's reach".
- `range_timing`: `declaration` (current) | `after_reaction`. Decides the band penalty.
- `reaction_purchase_cap`: none (current) | 1. Applies to every reaction to a shot.
- `swap_requires_single_purchase`: false (default) | true. The defense swap only counts if one purchase reached or left reach. Cover dives are unaffected.
- `provoke_check`: when a point-blank shot's provocation is decided. `declaration` | `resolution` (current reading: the shooter's position after the shot).
  - Under `declaration`, the shot that made the target close in doesn't provoke; later shots do.
  - Opportunity attacks still resolve after the shot either way.

Cover from a dive stays as written (total cover counts as three-quarters).

**Designer packages to run as presets:**
- **"Reaction changes cover only":** `defense_timing = declaration`, `range_timing = declaration`.
- **"Resolve against where you end up":** `after_reaction` for both.

## 7. Agents (R6)

Movement results depend on the agents more than on anything else. Each item below needs documented heuristics and a test.

**R6.1. Reacting to a shot (tactical agent).** Choose between staying, diving to cover, closing to the shooter, and backing off (where `range_timing = after_reaction` makes that worth something).
- Value each by the exact block outcome of this shot: the agent already solves blocks exactly.
- Add a positional term. Ending adjacent to the shooter is worth what it does to the shooter's next turn: it must pay or provoke to leave, or shoot point blank. Use a parameter weight, or a one-reply lookahead like the archer's.
- Today the agent dives only for cover.

**R6.2. Archer (tactical agent).**
- Aim by exact expected value as now, extended to:
  - the band penalty;
  - the wound cap;
  - piercing;
  - free aim dice;
  - the crit switches.
- Weigh the target's possible reactions: cover nearby, or within one reaction of the shooter.
- Keep its existing step-out-of-reach behavior.

**R6.3. Melee pursuer.**
- Buy on-turn squares when that gets it to contact a turn earlier. Scripted pursuers never buy today.
- Know that arrival stamina matters in steps. In the solver study, the charge's value jumped at 5, 9 and 14 stamina (the costs of 2, 3 and 4 attack steps), so the pursuer should weigh buying squares against the step it would drop below.

**R6.4. Coverage.** Every experiment reports both agent families, as the usage doc already requires for positional results.

## 8. Parity and acceptance tests (R7)

The reference is the project's exact solver `bows5.py` (sha256 0c0cbdadab42, the last copy in project doc `claude/ranged_study/bundle_bows.txt`). It adds `cap_floor` for the shortbow's R2 reading. Its functions `shot_dist` and `injury` are small and self-contained.

**R7.1. Shot distribution.** For each candidate bow, aim count 0–6 and distance 0–40, the engine's exact distribution of (total, critical dice, wound cap) must equal `shot_dist`'s exactly. Cover every crit configuration in §5 and both shortbow dice.

**R7.2. Injury.** For totals 0–40, critical dice 0–3, D 1–5, armor 0–4, pierce 0–2, perfect blocks 0–8 and grazes 0–8, the engine's HP loss must equal `injury` (with armor reduced by pierce, and both `crit_in_cap` settings).

**R7.3. Costs.** For sequences of draws and aim steps after 0–3 earlier actions, the engine's prices match the solver's (draws and aims advance the counter; free aims don't).

**R7.4. Baseline unchanged.** The existing `v0.9.3` and `v0.9` suites pass unchanged.

**R7.5. Known reference numbers** (one round, one archer, point blank, rule A, target D2 and 14 stamina unless noted). The engine can't reproduce these through a full fight, but a test harness that calls the same block solver with the target's best reply should.

| Archer | Target | Down / HP | Source |
|---|---|---|---|
| Longbow 1d8+1, FIN 1 | Caster (HP 8) | 38% / 6.2 | `i1.txt` |
| Warbow 1d10+3, pierce 1 | Plate (armor 3, HP 12) | 4% / 4.2 | `h.txt` |

If that harness is too much work, R7.1–R7.3 are enough.

## 9. Step-by-step play for chat agents (R8)

`se play --as` exists, but it reads from the keyboard. A chat agent runs one command at a time, so it needs a resumable mode:

**R8.1. Interface:**

```
se play scenario.toml --as ID [--as ID2] --trial N --answers answers.jsonl --step
```

- Replays the fight deterministically from the trial seed plus the answers so far.
- Stops at the next decision for a controlled combatant and prints it as JSON:
  - where the battle is (the timing context path);
  - the decision kind;
  - the observation (positions, HP, stamina, defenses, armor, cover from each candidate square, off-turn escalation level);
  - the options with their prices;
  - the answer schema.
- Then exits.
- Exit codes distinguish "awaiting decision", "fight over" and "invalid answer".

**R8.2. Answers are JSON lines** appended to the answers file. An invalid answer is reported with the reason, never as a crash, and isn't consumed.

**R8.3. An ASCII map in the request**, using the existing map legend plus combatant markers.

**R8.4. Same session-log format as `--log`,** so `se load` reports decision load for chat-played sessions too.

**R8.5. Determinism.** The same scenario, trial and answers must produce the same state and the same next request. Test it.

## 10. Scenarios and measures (R9)

**Scenarios** (library maps or inline):

| Scenario | Purpose |
|---|---|
| S1. One archer vs one melee fighter (sword-and-board and two-hander), starting 4, 8 and 12 squares apart, open ground | Approach, dead zone, arrival stamina |
| S2. As S1 with low walls near the fighter's path | Cover vs closing reactions |
| S3. Two archers + one melee vs a melee fighter and a caster near cover | Focus fire and covering fire |
| S4. Two archers at 6–10 squares vs a caster and an armored knight | The lethality budget at normal ranges |
| S5. Archer vs knight in full plate (armor 3), with and without shield | Bow niches against armor |
| S6. Archers vs one Large armored beast (armor 4, HP ~20) | Superheavy niche, size rule |
| S7. Archer pair vs a Small target at 2–4 bands | Size rule at range |

Run each with the bows in R2.4, both §6 presets, and crit rules A, C′ and C.

**Measures** (alongside `se run`'s standard output):
- chance any PC is down by round 2 (the focus-fire measure);
- down rate per target type;
- archer stamina drained vs HP dealt;
- reactions by kind (stay, cover, close, back off) and their cost;
- rounds to contact;
- the archer's turn-1 spend and reserve;
- shots per band;
- critical dice per shot;
- opportunity attacks provoked by shooting, and taken.

## 11. Out of scope

Tested in the solver studies and not adopted:
- tracking aim;
- snap shots;
- held (draw-and-loose) shots;
- Strength refunds;
- steep within-turn cost ladders.

Not yet designed: crossbows, thrown weapons, mounted archery.

## 12. Priority

1. **Rules:** R1–R4 (ranges, bows, piercing, aim, crit switches), with the parity tests in R7.1–R7.3.
2. **Reaction switches:** R5.
3. **Step-by-step play:** R8. This lets chat agents explore before the agents in step 4 are written.
4. **Agents:** R6.
5. **Scenarios and measures:** R9, then a first report in `sim/reports/`.

## 13. Designer decisions these switches leave open

- Reaction timing (§6).
- Purchase cap (§6).
- Aim-dice crits and the per-shot cap (§5); the current lean is rule A.
- Which reading of the shortbow property (R2.2).
- What counts as "moved" for Ranged Defense, and the attribute split (R1.5).
- Which attribute widens bands (R1.2).
- The size table beyond Small and Large (R1.3).
- The per-band penalty (R1.2).
- Whether a free aim die is included (R3.3).
- The piercing values (R2.4).
