# Fix order and dependency map (companion to the v0.9 review)

Findings are numbered as in the v0.9 review (`archive/design/Review_Playtest_Packet_v0.9.md`, archived; its findings are indexed in section 10). "Ripples to" means: if this changes, that finding's numbers or conclusions must be re-measured.

## 1. Dependency table

| Finding | Depends on (settle these first) | Ripples to (re-check after changing) | Blast radius | Phase |
|---|---|---|---|---|
| **F2** crit ×2 → linear | nothing (one-line rule) | every lethality number: F1 tuning, F3 volleys, F4 shield worth (each leak is worth 2 today), F5 L99 kills, F6 1v3 speed, F8 dagger identity, F11 block-decision branch | very large | 1 |
| **F1** curve mismatch (surcharge slope; r target) | F2 (leak size decides parity vs stalemate); F12 (starting budget sets L1 defense → r); F5/F7 (pool size sets max steps) | F3 (aim steps are "actions", so a steeper surcharge raises volley costs; a block-slope change alters ranged blocks), F4 (how much defense is worth), F5, F6, F8 (base costs live in the surcharge formula; multiplier principle), F13 mental stats, monsters, class cores (Barbarian refunds the biggest step), F11 | very large | 1 (shape), re-check in 2 |
| **F5** level scaling (where the level bonus goes) | F1 shape | every level's numbers; strain growth; any ability that references pool size; F7 formula | large | 2 |
| **F7** max stamina = 6 + HP (death spiral) | F1 shape, F5 | pool size → max steps → F1 numbers (loop: re-run F1's table after); H-2's fate; STR +1 HP question; F6 (wounded defenders) | medium | 2 |
| **F12** L1 Expertise budget vs scale text | nothing | L1 attribute spreads → L1 MD and damage → r at L1 (F1); whether "nimble" L1 builds can exist (F4) | small, but upstream | 0 |
| **F6a** stamina visibility (rules text) | nothing | commitment decision (F1), avoid-vs-block (F9), telegraphing, all sim policies | small, upstream | 0 |
| **F6b** focus fire; block reset per attacker option | F1, F2 (re-run 1v3 after them) | F1 defender math vs multiple attackers | medium | re-check after 2; decide in 3 if still 1–2 rounds |
| **F6c** NPC profiles (H-6) | everything tuned | GM material only | none upstream | 7 |
| **F10** extra movement too cheap | nothing (constraint: chasers must still win) | F3 archer/chase dynamics; F9 off-turn vs on-turn economy | small | 4 (can start any time) |
| **F9** OA avoidance vs cap; reach | F6a (visibility), F10 (movement costs) | reach-weapon identity (F8), Finesse's value, positioning text | small–medium | 4 |
| **F3** ranged defense; H-1 for ranged; aim; Dodge's fate | F2, F1 (surcharge/blocks), F10 (chase) | casters' baseline (F13), shield worth (F4: +2 RD), cover values, area attacks (Dodge), magic scope, H-1's fate | large | 5 |
| **F4** shield / defense pricing | F1, F2, F3 (RD side of the shield) | F8 two-hander vs shield trade, armor table, "nimble" build viability | medium | 6 |
| **F8** weapon table; multipliers; light-weapon niche | F1 (principle on per-step damage growth decided there; base costs), F2 (dagger crits), F4 | F5 (damage growth with STR), monsters (damage per step scale), OA cap (base costs) | medium | principle in 1, table in 6 |
| **F13** mental attributes, monsters, control, casters, cores | F1, F2, F5, F7 (final economy); F3 for casters; F6c for monsters | class trees, magic, monster blocks | downstream only | 7 |
| **F11** decision/arithmetic load | all mechanics settled | presentation, tokens, reference tables | none | 8 (budget stated in 0) |
| **F14** edge cases | mostly none; off-turn order → F9/F10; Rogue timing → cores; aim-dice-crit → F2/F3 | text | small | 0 for the three decisions, 8 for the rest |

Shelved items: **H-1** (max HP damage) is decided *by* F1 and F3, not an input — if F1+F2 land, it is probably unnecessary for melee; if F3 is handled through Ranged Defense, unnecessary for ranged. **H-2** (damage reduces max stamina) belongs with F7 in Phase 2. **H-3** (injuries) after Phase 2. **H-4** (control) and **H-6** (NPC profiles) in Phase 7.

## 2. Suggested order

Each phase is one chat (or two). Re-run the four scenarios at the end of every phase; the simulator makes that a minute.

**Phase 0 — Lock the assumptions (no simulation, one short chat).**
- Stamina is public information: yes/no. (Everything downstream assumes an answer.)
- Aim dice count as crit dice: yes/no.
- The complexity budget as a hard constraint on fix shapes: e.g. "no new number computed per attack" — this rules in/out the wound-cap route before anyone argues for it.
- Starting Expertise budget and the attribute scale anchor (F12). Decide this now because it fixes the level-1 defense values the engine is tuned against.
- Initiative tiebreaker (F14), simply so playtests can run.

**Phase 1 — The exchange engine.** Order within the phase matters.
1. F2: crit effect. Replace ×2 with a linear per-crit-die bonus; keep armor-ignore. Re-run; confirm that one- and two-step attacks still leak (no stalemates).
2. F1: surcharge slope (+2 per prior action is the tested candidate), confirm block escalation stays 1,2,3…, and write the r discipline: the target band for damage-per-step ÷ defense, and the test ("full-block cost of the mean roll within ±1 of attack cost for k ≤ 3; full strike from full ≤ 3–5 HP").
3. Principle for per-step damage growth (F8's upstream half): STR multipliers stay or go; how damage per step is allowed to grow with attributes, so r holds at higher levels.
4. Decide H-1's role for melee (likely none).
Output: a locked L1/L30 exchange table and the r rule.

**Phase 2 — Core resource formulas (then loop back once).**
- F5: where the level bonus goes (recovery vs maximum vs strain).
- F7: the HP ↔ max-stamina coupling; whether H-2 comes back for "out of the fight before 0 HP".
- STR's +1 HP, decided as part of the HP formula.
- Then re-run Phase 1's table at L1/L30/L99 with the new pools; adjust the surcharge slope if max steps moved.
Output: resource formulas + the three-level scaling check.

**Phase 3 — Focus-fire re-check (short).** With Phases 1–2 in place, re-run 1v3 and the equal-duel first-mover edge. If 1v3 still ends in 1–2 rounds, decide F6b (block count reset per attacker per round, or a free retreat step). If the first-mover edge is still above ~60%, that is where to look at end-of-turn recovery's size, not timing.

**Phase 4 — Positioning economy (can run in parallel with 1–3).**
- F10 extra on-turn movement cost (constraint: chasers still win via the off-turn escalation on the fleer).
- F9 OA cap vs avoidance cost; reach weapons able to threaten; whether the off-turn track mirrors any surcharge change from Phase 1.
- F14: order of simultaneous off-turn movement; avoidance when out of stamina.
Output: the positioning rules text; archer chase assumptions for Phase 5.

**Phase 5 — Ranged.** Needs 1, 2 and 4.
- F3: Ranged Defense structure (fold Dodge in, or not); ranged block cost shape; aim as damage or precision; range-band exceptions; cover values; H-1's role for ranged.
- Casters' baseline survivability (F13) falls out of this; so does the magic-scope decision's cost.
Output: re-run Table 5 and the archer scenario.

**Phase 6 — Equipment.** Needs 1–5.
- F4 shield value, two-hander defense, AGI/FIN defense steps by armor.
- F8 weapon table numbers and the light-weapon niche mechanism; armor table and Strength thresholds.
Output: re-run armored-vs-unarmored and the weapon efficiency table.

**Phase 7 — Content-facing gaps.** Needs everything above.
- Mental attribute combat benefits (price against the now-known value of +1 stamina and +1 defense).
- Class cores re-priced against block savings (Monk, Barbarian, Fighter); Rogue turn-order timing.
- Control effects (H-4) against the real spare-stamina budget.
- Monsters and NPC profiles (H-6); telegraphing.
- Magic scope.

**Phase 8 — Load and text.** F11 audit of a real turn, tokens and reference tables, remaining F14 wording, the v1.0 packet.

## 3. What can be worked on independently right now

With no dependency on Phase 1's outcome: Phase 0 decisions; F12; F10 (numbers, with the chasers-win constraint); most F14 wording fixes; the Fighter-core strain-overage oddity; initiative tiebreaker. F9 can start once stamina visibility is decided.

## 4. One-way doors (settle before any content is written)

These are cheap to change now and expensive once weapons, classes and spells reference them:
- The crit shape (weapon identities are built on it).
- The r discipline and the surcharge slope (every weapon base cost and attribute step is checked against them).
- Where the level bonus goes (abilities will reference pool and recovery sizes).
- Whether Dodge exists as a separate defense (spells and area attacks reference it). Packet 0.11.3 shelves it for now (Ledger H-8).
- Stamina visibility (table procedure, telegraphing, Cunning's design space).
- Max stamina's coupling to HP (injury rules, H-2, healing all hang off it).

## 5. Loops to be aware of

- Phase 1 ↔ Phase 2: pool size sets max steps, the surcharge slope sets what those steps cost. Decide shape in 1, formulas in 2, re-check 1 once.
- Phase 1 → Phase 5: a steeper surcharge already lowers volley lethality (aim steps are actions); measure before adding ranged-specific fixes.
- Phase 4 → Phase 5: movement cost decides whether kiting exists at all; decide it before judging archers.

## 6. After packet 0.11.0 (added 2026-11-16)

This file was written against packet v0.9 and has not been kept current. Section 10 gives each finding's status as of packet 0.11.5. `rules/CHANGELOG.md` says what each later packet changed and which finding it answers (F10 in 0.9.1, F2 in 0.9.2 and F3 in 0.10.0, among others).

Packet 0.11.0 replaced both kinds of bought movement with one **dash**, and the on-turn surcharge and off-turn escalation with one **escalation**. That changes six things above:

- **F10 (extra movement too cheap)** has now been answered twice. Packet 0.9.1 cut each extra on-turn purchase to 1 square. Packet 0.11.0 makes bought movement a dash: an action, costing 1 + your escalation.
- **"Chasers must still win"** (the F10 row, Phase 4 and §3) no longer describes the rules. It relied on the fleeing side paying an off-turn escalation while the chaser paid a flat price. Both sides now pay the same price for a dash, and a fighter chasing an archer is worse off than under packet 0.10.1 (the changelog's 0.11.0 entry gives the figures). The designer left that to later changes on the ranged side, which is Phase 5's subject.
- **F6b (focus fire).** Packet 0.11.0 is a priced form of the "retreat step" option in Phase 3: a creature that gives ground can no longer be followed for nothing. It has been checked for one round only (changelog, 0.11.0). The first-mover edge in a duel that starts within free movement is not changed by it (`claude/v0.11.0_Checks_2026-11-16.md`).
- **F9.** "Whether the off-turn track mirrors any surcharge change" no longer applies: there is one escalation. The opportunity attack cap went in packet 0.9.1, and making an opportunity attack is a one-step placeholder until it is redesigned.
- **F14.** The order of simultaneous off-turn movement is ruled: in the dash phase before each turn, the highest in initiative of those who want to dash goes, and this repeats until nobody wants to. (The review suggested lowest first.) The Rogue's timing is ruled only as far as the dash phase goes: its core is declared just after a dash phase ends, and that is open to change. Where a moved turn sits in the next round is still unstated. The initiative tiebreaker (Phase 0) is still missing, and the dash phase now relies on initiative order.
- **§5, Phase 4 → Phase 5** still holds, with one difference: the movement price was chosen for gang-ups, and kiting was knowingly left for the ranged work.

## 7. After packet 0.11.1 (added 2026-11-17)

Packet 0.11.1 adds **holds** and gives opportunity attacks a rule again. At the end of your turn you can put stamina on enemies as tokens; a creature you hold pays 1 + the tokens to leave your reach, and the tokens add to your opportunity attack against it. That touches four things above:

- **F9.** Making an opportunity attack has a rule again: steps priced like an attack's, starting fresh, with a cap of 1 + 1 per odd Finesse (the cap 0.9.1 removed) plus a hold's tokens. Avoidance stays 1 per enemy per square, or 1 + the tokens for the first square left in a holder's reach. Both are Mechanism open.
- **F6b (focus fire).** Holds make a close gang-up deadlier when an attacker acts before the lone fighter: three on one from 3 squares, 6% → 58% to go down in the first round (exact, one round; `claude/Hold_Rule_Study_2026-11-17.md`). That raises the stakes of the initiative work in Phase 0 (the tiebreaker) and of the bidding idea in Not in This Version. The designer: "another sign that we need to revamp initiative".
- **Phase 0, stamina visibility.** Still undecided. It is now also in the packet's Open Questions, with how stamina is tracked when a creature has more than one pool, and the caveat that a band or a hidden number leaks if every attack and block is visible. Hold sizing depends on it.
- **§5, loops.** Holds belong to the loop the 2026-11-15 notes drew between the stamina cap (hard flux), giving ground and tackle. Once a cap is tried, pressed fighters will want to break contact more often, so holds will matter more and should be re-checked with it.

## 8. After packet 0.11.2 (added 2026-11-17)

Packet 0.11.2 adds two placeholders so a first playtest can run and a rule for moving past wall corners, and it replaces the candidate abilities.
- **Phase 0, the initiative tiebreaker (F14)** has a placeholder: the higher Agility + Cunning, then a d12 roll-off. The dash phase's priority by initiative is now always defined.
- **Helping the dying,** the readiness review's one blocker that needed a new rule, has a placeholder: an action with a base cost of 5, rolling 2d12 + Intelligence against 10 + the target's Shock.
- **Grid movement (added 2026-11-18):** you can't move diagonally past the corner of a wall or pillar (Free Movement). It's the first grid reading the packet states; the engine's others (moving through creatures, reach past walls) are still its own readings. Its threat half, a diagonal step past a threatened square provoking, is an open question.
- **Phase 7 (content-facing gaps):** the candidate abilities are now one, Great Weapon Training (Fighter; +1 square of reach for heavy weapons). The earlier candidates moved to their own note.
- **§5, loops (added 2026-11-18).** The stamina cap is shelved (Not in This Version; Ledger H-7). The re-check of holds that section 7 tied to a cap waits until one comes back.

## 9. After packet 0.11.3 (added 2026-11-19)

Packet 0.11.3 shelves Dodge Defense (Not in This Version; Ledger H-8), so there are two defense values.
- **F3, Dodge's fate:** shelved for now. Since 0.10.0, Ranged Defense has carried Agility's even values (option 1). Dodge comes back if spells, monsters or hazards need a defense of their own; area attacks remain an open question.

## 10. Index of the v0.9 review (added 2026-11-23)

The v0.9 review (`archive/design/Review_Playtest_Packet_v0.9.md`) is archived, so design chats can't open it. This section keeps what's still useful: one row per finding with where it stands now, the keys that engine docs and reports use ("F3 option 1", "Table 5", "Addendum 2"), and the review's own views that no other live doc holds. Statuses are as of the `rules/v0.11.5` branch (2026-11-23).

**Reading it.** Everything in this section is a record of the review's analysis, written by an assistant against packet v0.9. It argued from the design notes' draft pillars (P1–P4, C1), so its "stakes" and recommendations are its reading, not the designer's. The review's figures are for v0.9's rules (HP 6 + Strength, crits doubling, shield +2/+2, flat-priced movement). The engine reproduces them (`se table 1|5|8 --ruleset v0.9`, `se suite parity`).

### 10.1 Findings

| ID | Finding (review's title, short) | What the review found | Review's severity | Where it stands now |
|---|---|---|---|---|
| **F1** | Attack and block costs are curves of different order; commitment collapses to the extremes | Each extra attack step costs 1 more, but fully blocking it needs about r more perfect blocks (r = damage per step ÷ defense value, about 1.9 for the sample fighter), so full defense grows about r² faster than the attack. 1–2-step attacks were an even trade; 4 steps decided fights. At level 1 an all-in opener downed an equal, fully blocking fighter 34% of the time, and the first mover won 69% of duels; at level 30 the middle commitments stalemated. Nothing holds r steady across levels or builds. | Critical | **Partly addressed; still open.** 0.9.2 replaced crit doubling with +1 per critical die (F2) and raised HP to 8 + 2 per even Strength, aimed at this (changelog 0.9.2, HP entry: "HP is the main lever on how often a fresh defender can't survive an opener's maximum all-in"). The escalation is still +1 per action and block costs still 1, 2, 3…; no target for r is written down. 0.10.0's shield cut (+2 → +1) moved the sample fighter from Melee Defense 4 to 3, which undid most of 0.9.2's gain for that build: its opening all-in against an identical fighter at full downs it 23.0% of the time (mean 7.3 of 10 HP), against 0.9% at Melee Defense 4 under the same rules [exact: `analysis.strike.mirror_strike`, preset `v0.10.1`, build `l1_sample`]. At Melee Defense 3 and armor 2, fully blocking the mean roll costs 3 / 8 / 23 / 38 against attacks of 2 / 5 / 9 / 14 [exact: `se table 1 --ruleset v0.10.1`]. Duel length still hinges on defense: 2.7 / 6.9 / 15.7 rounds at Melee Defense 3 / 4 / 5 (NITV, stamina cap, exact duel solver under 0.10.1). *[checked]* The same 23% figure appears in two claude.ai project docs, `claude/FableMax_Exchange_Guard_2026-11-11.md` and `claude/Design_Pillars_Redraft_2026-11-14.md`; the repo didn't record it until this index. |
| **F2** | Critical doubling is a frequent luck multiplier, not a skill reward | Any critical die doubled what got through, and with 2–4 dice a crit was the normal case (44–68% at Finesse 1). The same attack against the same blocks gave 0, 2 or 4 HP by the dice. Without doubling, the level-1 opener's down rate fell from 34% to 1%. | Critical | **Fixed in 0.9.2:** each critical die adds +1 if any damage gets past blocks and armor, and still ignores 1 armor (changelog 0.9.2, Critical Hits; Source Review F2). This is the review's option 1 at +1, with "only if something gets past" added. What's left: Finesse still widens the range as before, and the Critical Hits note still says "It comes from skill, not luck" (10.6). *[checked]* |
| **F3** | Ranged Defense 1–3 gives unshielded targets no stamina answer; Maximum HP Damage isn't the fix | Against a missile a perfect block stops only Ranged Defense (1, or 3 with a shield), so without a shield no stamina buys safety; aim stacked 1d6 + Finesse per step. One aimed shortbow shot downed an unarmored target 72% of the time, and cover made it all vanish, so the GM's map decided. A Maximum HP Damage cap wouldn't help (10.4). | High | **Partly addressed in 0.10.0:** aim steps are 1d6 without Finesse plus one free aim die; the aim limit (a shot's HP loss can't exceed the weapon's damage roll); aim dice never crit; shots are actions; Ranged Defense gains +1 per even Agility (option 1) and +1 for moving in reaction to the shot; cover +1 / +2; shield +1 (changelog 0.10.0: Range Bands, Aim, Critical Hits, Defenses, Shields, Cover). Dodge Defense shelved in 0.11.3 (Ledger H-8). **Still open:** "Ranged lethality under the 0.10.0 bows: untested at normal ranges. Two archers shooting one target back to back are the main risk" (Open Questions). Options 2 and 4 weren't taken. *[checked]* |
| **F4** | The shield's +2 dominates; defense is priced linearly for a good worth its square | Full-block cost scales with (damage ÷ defense)², so the first points of Melee Defense are worth far more than the last. A free +2 from a shield beat any attribute investment: the shielded sample beat a same-stats two-hander 73–86% and nimble unarmored builds 65–88%. | High | **Partly addressed.** 0.10.0: shield +2 / +2 → +1 / +1, "being tried out" (changelog 0.10.0, Shields). A Strength requirement for shields is shelved (NITV, citing Review F4). Not taken: two-handers +1 Melee Defense, the Agility split, publishing an exchange rate between defense and weapon size. The convexity behind it remains, tied to F1: one point of Melee Defense is the whole gap between 0.9% and 23.0% above. No repo doc re-measures armored against unarmored (Table 7) under 0.10.x; the phase suite ran under `v0.9`. *[checked; no re-measure inferred from the reports]* |
| **F5** | Level scaling: pools grow, HP and defense don't, so the full strike grows from cripple to kill | Max stamina grows with level, so affordable steps rise from 4 (level 1) to 7 (level 99) while HP stays 6–12 and defense tops out around 6–7. At level 99 the opening strike killed 69% and duels lasted a median of 1 round. | High | **Still open.** The level bonuses (round(Level / 5) to maximum stamina, round(Level / 10) to recovery) are unchanged, HP still doesn't grow with level, and nothing adds defense by level (Stamina, HP, Character Advancement). The crit change removed doubling, which carried much of the level-99 kill rate, but no repo doc re-measures levels 30 and 99 under current rules (the phase suite's 84–87% first mover at level 99 is under `v0.9`). *[rules checked; no re-measure inferred]* |
| **F6** | Focus fire has no answer, and NPC commitment is the hidden lethality dial | Blocks reset per attack, so three equal attackers downed a fresh fighter in 1–2 rounds every time, in heavy armor too. How many steps NPCs commit, which players can't see, was the biggest lethality input. | High | **Partly addressed.** *Stamina visibility (F6a):* open, in Open Questions since 0.11.1. *Answer to a gang-up (F6b):* 0.11.0's dash phase and single escalation make giving ground cost pursuers their attack; three attackers that all act first, from 7 squares, now down a fresh fighter 1.4% of the time (exact, one round; changelog 0.11.0). Holds (0.11.1) push the other way: a close three-on-one from 3 squares, one attacker acting first, 6% → 58% (changelog 0.11.1; NITV, initiative). Fix_Order §6–7. The per-attacker block reset (option 2) wasn't taken. Fights that start with all three in reach aren't changed by any of this *[inferred]*. *NPC profiles (F6c):* shelved (NITV; Ledger H-6). *[checked]* |
| **F7** | Max stamina = 6 + current HP is a death spiral at low level | At level 1 a 6-HP wound cut the pool 43%, so the first real wound decided the fight: winners were untouched 63–85% of the time and losers ended at −3 HP. | Medium | **Still open, softened.** The formula is unchanged (Stamina). 0.9.2's HP raise means the sample (10 HP, 16 stamina) loses 37.5% of its pool to a 6-HP wound instead of 43% [exact arithmetic]. Damage reducing maximum stamina (H-2) is still shelved (NITV). The designer has called max stamina tracking HP "meaningful but non-crippling (because it's a once-per-fight nerf…)" (design notes §3.2, "Consequences should feel weighty but cost little", [C:2026-11-05]), which bears on how much this is a problem. *[checked]* |
| **F8** | Weapon table: heavy weapons are more stamina-efficient at every commitment; light weapons have no niche | The greataxe out-damaged the dagger per stamina at every number of steps, against the stated intent (light weapons efficient at low commitment). The ×2 and ×3 Strength multipliers give 25-damage steps at Strength 6, past the human scale. | Medium | **Still open.** The melee rows are as the review tested them (the Weapon Table matches Table 8's formulas, and no changelog entry touches a melee weapon's numbers). Only the spear's hands changed (0.11.1). Great Weapon Training (a candidate, Fighter Tier 1) gives heavy weapons reach, a style rather than efficiency. The engine has all three options as equipment tables or switches. *[checked]* |
| **F9** | Opportunity attacks: avoiding them dominates the cap; reach weapons can't threaten | Avoiding cost a flat 1, so whenever Finesse raised the cap enough to matter the mover paid 1 to switch it off. The default cap of 1 meant a base-2 weapon at Finesse 0 could never make one: a spearman threatened nothing. | Medium | **Partly addressed.** 0.9.1 removed the cap, 0.11.0 used a one-step placeholder, and 0.11.1 brought back a cap of 1 + 1 per odd Finesse plus holds. The stamina you hold on a creature adds to your cap against it and to its price for leaving (1 + held stamina for the first square), so a committed holder is expensive to slip past, close to the review's option 2 (changelog 0.11.1; Holds). Still true: without a hold, a base-2 weapon at Finesse 0 can't make an opportunity attack (cap 1), so Core Concepts' "control space with reach" is still false for that spearman (10.6). Avoidance is still a flat 1 and not an action (option 3 not taken). Design notes §5 item 15. *[checked]* |
| **F10** | Extra on-turn movement is too cheap to be plausible and makes range irrelevant | 1 stamina bought 1 + odd Agility squares, unlimited: 130–240 ft a turn, so range bands never mattered and the archer fight was settled on turn 1. | Medium | **Fixed, twice.** 0.9.1: each extra purchase moves 1 square (option 1). 0.11.0: all bought movement is one dash, an action costing 1 + escalation (changelog 0.9.1 and 0.11.0; Source Review F10). Known cost: a fighter chasing an archer is worse off; left to the ranged work (Fix_Order §6; design notes §5 item 21). *[checked]* |
| **F11** | Decision and arithmetic load is highest in the block choice and the off-turn prompts | The defender's search over perfect and grazing pairs, with crits changing armor and doubling the rest, plus 20–25 off-turn "do I move?" prompts in a five-creature round. It flagged four rules as costing more attention than they return, (a)–(d). | Medium | **Partly addressed; table time unmeasured.** (a) Doubling is gone (0.9.2), but each critical die still has two effects (ignore 1 armor, +1). (b) The range-band aim exceptions are gone (0.10.0, linear bands). (c) One escalation replaced the two tracks (0.11.0); tracking stamina at the table and on a virtual tabletop is open (Open Questions). (d) A strain-overage stamina cost on the Fighter core, which costs no stamina, is an Assumptions-register reading "pending designer" (ENGINE_PLAN). Holds add an end-of-turn choice (0.11.1). The engine measures request counts (`sim/reports/m5_load.md`): off-turn windows are a third to a half of all decisions (`cores_suite_notes.md`, item 5). The human session that measures seconds hasn't been played (AGENTS.md, M5 gate). *[checked]* |
| **F12** | The level-1 Expertise budget contradicts the attribute scale's own words | With 5 Expertise and attributes starting at 0, and the scale calling 2 "an average person", every starting adventurer is below an average person in most attributes. (The review's examples were "2/1/1/0/0/0 or 2/2/0/0/0/0". The second doesn't fit today's costs, where the Nth point costs N, so 2/2 would cost 6: at most one attribute can reach 2, and at least five are below average.) | Low | **Still open, and in no other live doc.** Character Creation still gives 5 Expertise with attributes starting at 0, and the Attribute Scale text is unchanged. Proposed for Open Questions (Attributes). *[checked; the cost arithmetic is from Costs: the Nth point costs N]* |
| **F13** | Where the core makes the known gaps hard to fill | Advice, not a defect: mental attributes, monsters, control effects, casters and class cores all hinge on F1's economy (10.4). | Advisory | **Still open, mostly tracked.** Will got the dying roll and Intelligence its Ability Point bonuses (0.9.1) and helping the dying (0.11.2); Will and Cunning combat benefits, monster stat blocks, control effects and magic's scope are in Open Questions; class cores are placeholders, and Fix_Order Phase 7 holds the pricing advice. The review's reasoning about each is only in 10.4. *[checked]* |
| **F14** | Interactions, ambiguities and exploitable timing | Thirteen edge cases; see 10.5. | Low–Medium | **Six settled or no longer arising, seven open** (10.5). *[checked item by item]* |
| **Addendum** | Configuration test after the review | Is F1/F2 tunable or structural? A grid over block-cost slope, surcharge slope, crit effect and Melee Defense at levels 1 and 30. No single flat change fixed both levels; with no crit effect at all nothing ever got through; +2 surcharge with +2 per critical die landed in the review's target band at both levels; r is the master parameter. | — | **Partly taken.** The crit half came in at +1 per critical die, not +2, because +2 "carries most of the remaining all-in risk" (changelog 0.9.2). The surcharge half wasn't taken, and the target band for r isn't written down. The engine reproduces the grid (`experiments/parity.py`, `ADDENDUM`). Readings in 10.4. *[checked]* |
| **Addendum 2** | 1v1 against XvX, retreat economics, a guard-rule test | Under v0.9 movement, retreating on open ground can't buy time: the fleer pays 4:1 to 11:1 against the chaser. A guard rule (cheaper perfect blocks, or +1 Melee Defense, after a light turn) makes turtles under v0.9 and creates no rock-paper-scissors. The +2 surcharge's side effects. | — | **Retreat figures describe v0.9 movement only.** 0.11.0's dash prices both sides the same (Fix_Order §6). The engine computes the figures exactly under any rule set (`analysis/retreat.py`; `tests/golden/test_retreat.py`), and code cites "Review Addendum 2". The guard-rule result is recorded only in 10.4. *[checked]* |

### 10.2 The review's numbered options (engine docs and reports cite these)

What each option was, and what became of it.

- **F1:** 1. Make the attack's surcharge grow faster than block escalation (+2 per earlier action): not taken. 2. Write down a target for r and make the tables obey it: not done. 3. Bound the wound per attack (one step's dice + Strength, after armor, instead of doubling): not taken for melee (NITV, Maximum HP Damage: "a general rule stays out until melee shows it needs one").
- **F2:** 1. Linear crit, +1 or +2 per critical die after armor: **taken at +1, only if damage gets past (0.9.2).** 2. Doubling only with two or more critical dice: not taken. 3. If doubling goes, give low commitment some other bite: not needed, since the +1 is a leak.
- **F3:** 1. Fold Dodge into Ranged Defense (1 + even Agility + shield): **taken in 0.10.0** (`defenses.ranged_mode = "dodge_folded"`), with Dodge itself shelved in 0.11.3. 2. Ranged perfect blocks cost a flat 2: not taken (engine switch exists; `sim/reports/m3_ranged.md`). 3. Aim as precision rather than damage: partly; the aim limit keeps aim from adding to the wound, though aim still adds dice to the total. 4. State "no shield in the open means you die" in the rules: not done.
- **F4:** 1. Price the shield like an attribute step (+1 Melee / +2 Ranged, or +2 Melee with a Strength requirement): **shield +1 / +1 taken (0.10.0);** the Strength requirement is shelved (NITV). 2. Agility counting every point for Dodge and Ranged and every other point for Melee, and two-handers +1 Melee Defense: not taken. 3. Publish the implied rule "two points of Melee Defense are worth about one weapon size": not done.
- **F5:** 1. Put the level bonus into recovery, not maximum stamina: not taken. 2. Melee Defense +1 per 25 levels: not taken. 3. Keep Strength's HP: kept, and reworked (0.9.1: +2 HP per even value).
- **F6:** 1. NPC aggression profiles as the default way monsters are written: shelved (NITV; Ledger H-6). 2. A non-stamina answer to being swarmed (a free retreat step, or the perfect-block count resetting once per attacker per round): the priced retreat came in as 0.11.0's dash; the block reset wasn't taken (engine switch, ENGINE_PLAN Assumptions). 3. Public stamina: open (Open Questions).
- **F7:** 8 + HP / 2 + a level term; 10 + HP − Strength; or armor or a shield adding to maximum stamina: none taken.
- **F8:** 1. Swap Strength multipliers for bigger dice and give Strength weapons their efficiency through base cost: not taken. 2. Light weapons skip the first point of surcharge: not taken. 3. Cap Strength's contribution per step at the weapon's die size: not taken. All three exist as engine equipment tables or switches (`sim/reports/phase_suite.md`).
- **F9:** 1. Cap = weapon base cost + odd Finesse: not taken (cap is 1 + odd Finesse). 2. Avoiding costs the attacker's cap instead of a flat 1: partly, through holds (1 + held stamina). 3. Avoidance counts toward the mover's escalation: not taken (avoidance isn't an action).
- **F10:** 1. Extra movement costs 1 per square whatever your Agility: **taken (0.9.1), then replaced by the dash (0.11.0).** 2. Cap purchased movement at your free movement: not taken.
- **F11 (a)–(d):** (a) merge the two crit effects; (b) cut the range-band aim exceptions; (c) a physical token for the shared off-turn counter; (d) the strain-overage oddity on the Fighter core. Status in 10.1.

### 10.3 The review's tables (engine docs and reports cite these)

All of them are under v0.9's rules. The engine reproduces them: `sim/tests/parity/` and `experiments/parity.py`, with the review's original simulator in `sim/tests/oracle/`.
- **Table 1:** stamina to fully block a longsword attack at its mean roll, by Melee Defense and armor, against the attack's cost, for 1–5 steps.
- **Table 2:** level-1 equal duel, attack policy against attack policy (all in, fixed 3 / 2 / 1 steps, keep a 5-stamina reserve, chip then kill).
- **Table 3:** equal duels by level (1, 30, 99): rounds, first-mover win rate, the loser's final HP, how often the winner was untouched; plus the opening full strike.
- **Table 4:** one defender against three, level 1.
- **Table 5:** a single shot by bow and number of aims against four targets (unarmored, light armor, shield + medium armor, the same with three-quarters cover): stamina spent / HP taken / chance of going down.
- **Table 6:** archer against an approaching fighter, 12 squares, with and without cover and kiting.
- **Table 7:** armored against unarmored builds, levels 1 and 30.
- **Table 8:** damage per stamina by weapon and number of steps.
- **Table 9:** shape changes tested as evidence (surcharge +2; blocks escalating every second block; both; +2 Melee Defense for everyone; no crit doubling).
- **Appendix A** is the model and its assumptions (aim dice can crit; doubling once per attack; stamina observable; no abilities; fights to incapacitation). **Appendix B** is a goal-by-goal scorecard, and **Appendix C** the severity table (the "Review's severity" column above).

### 10.4 The review's views that no other live doc holds

These are the review's analysis and opinions, kept so they aren't lost. None is a design decision or a principle the designer has adopted.

**Its overall verdict.** The core logic was right (one pool, deterministic blocks, commitment before results, grazing blocks and armor as the counterweight, live positioning), but not yet sound enough to build weapons, classes and magic on. It asked for two shape changes before content: (a) attack and block costs of the same order, or a bound on the wound one attack can do; (b) a linear crit effect. It also asked for a decision on whether unshielded characters get any stamina answer to missiles, and called everything else tuning. Since then: (b) is done (0.9.2); (a) has only the HP raise, partly offset by the shield cut (F1 row); the missile question is partly answered (0.10.0) and open at normal ranges; content work has started (candidate abilities, 0.11.2–0.11.5).

**What it said to protect, with its evidence** (at v0.9 numbers):
- At one or two steps the exchange was almost exactly even (to block the mean roll: 2 against an attack of 2, 5 against 5, for the sample at Melee Defense 4 and armor 2), "the part of the curve the whole game should live on". At today's sample Melee Defense of 3 this no longer holds: 3 against 2 and 8 against 5 [exact, `se table 1 --ruleset v0.10.1`].
- End-of-turn recovery worked as a safety net: in thousands of fights nobody faced a turn at zero after their own spending, and holding a 5-stamina reserve lost to full commitment (Table 2).
- Diving for cover was the most powerful decision in the ranged game, "the right kind of agency". Its worry that it was the *only* ranged agency is out of date: since 0.10.0 a target can also close in or back away.
- System Shock's dying roll drifts toward stabilizing below about 4 Shock and toward death above about 6, so the window is real (2d12 against 10 / 15 + Shock; the attribute added is now Will, not Strength).
- Also: one pool for everything, offense before defense, status markers and the ledger, separate currencies. Those are already principles in the design notes and rules.

**Its challenges to core commitments:**
- *"Lasting harm is fair because damage is avoidable"* (design notes §3.2). In the equal duel, the three-on-one and the open-field archer case, no decision avoided the damage, so until F1–F3 were fixed, slow healing punished fights players couldn't have played differently, which the project brief rules out. It expected convalescence to dominate downtime, and pressure to bring back damage reducing maximum stamina (H-2) and injuries (H-3). Its figures (losers at −3 HP, 9–11 nights to heal) are v0.9's; HP and nightly recovery have changed since (0.9.1, 0.9.2).
- *"One regenerating pool pays for nearly everything."* Because offense and defense draw on the same pool, whoever spends first on offense forces the other to spend on defense. The review argued that one pool therefore needs attack and defense to drain it at the same rate per unit of threat, so the two cost curves must be of the same order. If that can't be done, the fallback is a small defensive float that can't be spent on attacks, a partial retreat from one pool. Related: the stamina cap's "Why it came up" in NITV, where stamina spent attacking and stamina spent defending would work differently.
- *"Nothing on the attribute scale is superhuman."* True of the scale, but the weapon formulas leak past it: ×2 and ×3 Strength and stacked aim gave steps of 25+ that no human-scale defender can answer. Either drop the multipliers (F8) or restate the commitment as "attributes are human-scale; outputs may not be". Since 0.10.0 the aim limit bounds what aim can wound; the multipliers remain.

**On a wound cap (Maximum HP Damage, Ledger H-1), from F3:**
- A defender who blocks at all is below the cap before it binds, so a cap doesn't change the stamina a shielded target spends.
- Under a cap, blocks are worthless until the remainder drops below it, so blocking becomes all-or-nothing.
- Against a cap, cheap unaimed shots beat aimed ones, so the lethality moves rather than falls.
- Its real promise is as a melee wound ceiling, applied before any crit effect and paired with something that makes the pressure above the cap count.

Since then: 0.10.0's aim limit is a cap of this kind for shots, and the Aim note states the cliff ("Blocks and armor save HP only once they bring the shot below the limit"); shots being actions taxes the spray. NITV keeps a general rule out until melee shows it needs one.

**On the gaps the core makes hard (F13):**
- *Mental attributes:* while the economy is this convex (13 against 14 stamina facing a full strike was life or death; +1 defense was worth 20–40% of block costs), anything a mental attribute does to stamina, defense or initiative becomes mandatory, and anything else gets dumped. Information hooks (Cunning seeing enemy stamina, or forcing the defender to declare blocks first) come out either very strong or very weak. It advised fixing F1 first, so small flavourful benefits can be priced.
- *Monsters:* an attack whose damage per step is more than about twice a character's defense can't be blocked, so big hits on named characters can't exist, and monsters must be written as many small attacks or as pressure. That makes monster design depend on F1 and on NPC profiles. (The sample's Melee Defense is now 3, not 4.)
- *Control effects:* resisting with stamina draws on the pool that focus fire empties exactly when a target is being ganged up on, so resistance is a fiction unless control costs are small or paid from another track.
- *Casters:* no armor and no shield leave them the lowest Ranged Defense, so their survival must come from spells, which sits badly with "core rules interesting without abilities". Since 0.10.0, Ranged Defense also gets even Agility and +1 for moving in reaction to the shot.
- *Class cores:* price them against the block stamina they save, not against each other. The Monk core saved 28 stamina against a level-1 full strike and was "the only thing in the packet that answers F1" (also in Phase 7).

**From the Addendum (configuration grid, v0.9):**
- The targets the review set itself: a full strike from full does at most about 3–5 HP and downs under 10%; the first-mover edge is at most about 60%; no stalemates; duels of 4–10 rounds. These are the review's numbers, not the designer's. The designer's stated pace target is a soft 3–5 rounds for an equal level-1 duel (NITV, stamina cap: "the 3–5 rounds the game aims for").
- Every single flat change that fixed level 1 broke level 30 (stalemate) or the reverse, because r drifts between levels and both triangular curves amplify r².
- With no crit effect at all, mean-roll parity means nothing ever lands. Some leak per attack is needed, and the fix is to make it bounded and linear.
- r is the master parameter: write down a target band (about 1.5–1.9 at v0.9's costs) and check every new weapon, attribute step or armor entry against it. Even Melee Defense 5 against 6 at level 30 moved duels from 4 rounds with a 46% first-mover share to 7 rounds and 57%.

**From Addendum 2 (guard-rule test, v0.9 and the +2 surcharge / +2 crit candidate):**
- A guard rule, meaning cheaper perfect blocks or +1 Melee Defense until your next turn if you took at most G actions on your turn, made turtles under v0.9 (15–45% draws). On the candidate rules it gave a flat matrix (46–57%, no draws) and no rock-paper-scissors.
- The review's reading: in a symmetric duel on open ground, the core economy's job is to be flat. Interest in a duel has to come from asymmetries (position with teeth, information, builds, abilities that counter particular commitment levels). Group fights supply asymmetry by themselves; one-on-one doesn't.
- Side effects of a +2 surcharge: aimed volleys cost more, attacking again costs more, and the Barbarian refund grows.

**Its scorecard's "no" verdicts (Appendix B):** "not swingy; deaths earned" failed at the extremes, because initiative and the opening roll decided equal duels (F1, F2). "Balance resilient to GM style" failed, because NPC commitment and map cover were the two biggest lethality inputs (F3, F6).

### 10.5 F14, item by item

| Edge case the review raised | Where it stands |
|---|---|
| Order of simultaneous off-turn movement | **Ruled (0.11.0):** in a dash phase the highest in initiative goes, repeating until nobody wants to dash (Dash; Ledger MV-2). The review had suggested lowest first. *[checked]* |
| Is stamina public? | **Open:** Open Questions, since 0.11.1. *[checked]* |
| Can aim dice crit? | **Ruled (0.10.0):** never. *[checked]* |
| Does doubling happen once per attack? | **Moot:** doubling was removed in 0.9.2. *[checked]* |
| What a dive into half cover gives | **Open.** Cover still covers only a dive that ends fully behind cover (it counts as three-quarters). The engine reads a dive into partial cover as half cover (ENGINE_PLAN Assumptions, "pending designer"). Proposed for Open Questions. *[checked]* |
| Diving out of a point-blank shooter's reach: both sides provoke in one exchange | **No longer arises as described.** Since 0.11.4 a shot's opportunity attacks resolve when the target is declared, before paying, and the target reacts after the roll, so the two provocations come at different steps (Ranged Attacks, Procedure). Point-blank opportunity attacks still can't be avoided by paying. *[inferred from the procedure text]* |
| "Attack again" as probing is never worth it | **Matches intent:** Melee Attacks says attacking twice is easier to block; design notes §3.1, "Commit up front; misjudging should cost efficiency, not be forbidden". *[checked]* |
| The Rogue core: where a moved turn sits next round | **Partly ruled.** Its place against the dash phase was ruled in 0.11.0 ("Moving your turn doesn't change your place in initiative for later dash phases"); its slot next round is still unstated (Fix_Order §6; the engine keeps the new slot, "pending designer"). *[checked]* |
| The Barbarian core refunds the largest step (5 after a 4-step attack, more than a whole recovery), so part of the surcharge is refundable | **Unchanged.** The rule text is the same, and the largest step can now include escalation from dashes too. The engine's reading is "pending designer". *[checked]* |
| Initiative ties | **Placeholder (0.11.2):** higher Agility + Cunning, then a d12 roll-off. *[checked]* |
| The cheap retreat is right after your own turn | **Now explicit and intended:** Dash ("nothing you did on your turn makes a dash after it pricier"); design notes §3.1, "Don't punish aggression with unrelated costs". *[checked]* |
| Maximum stamina at negative HP | **Open:** 6 + current HP has no stated floor (Stamina). The engine floors the HP term at 0 (ENGINE_PLAN Assumptions, engine convention). Proposed for Open Questions. *[checked]* |
| Leaving at 0 stamina: you can't pay to avoid and can't block, so you're trapped | **Open.** You can still leave and take the opportunity attack. The designer (design chat, 2026-11-17): a creature at 0 stamina can still leave, just taking an opportunity attack it can't block, and should probably go down without much trouble. The review's idea of paying avoidance from your next recovery (a debt) is an engine variant "pending designer" (ENGINE_PLAN Assumptions). *[checked]* |

### 10.6 Wording items from the review still open

Checked against the 0.11.5 branch. Each is a one-line text fix or decision, and none changes a rule unless the designer chooses one that does.
- **Core Concepts, Positioning: "control space with reach."** Still false for a base-2 reach weapon at Finesse 0 without a hold (cap 1). Change the rule (F9) or the sentence.
- **Critical Hits: "It comes from skill, not luck."** A die still crits on its maximum at Finesse 0, so a multi-die attack often has one. The review suggested "skill widens it". The +1 per die makes the luck matter less than doubling did.
- **Blocking: "Attack vs. defense efficiency (Locked, as a design target)"** states the target without a test. The review's test: at k steps, the stamina to fully block the mean roll should be within ±1 of the attack's cost for k ≤ 3 (also in Phase 1 above). The current sample (Melee Defense 3, armor 2) fails it: 3 / 8 / 23 against 2 / 5 / 9 [exact].
- **Weapon Table, longsword: "One-handed: 1d8 + STR + FIN (STR replaces AGI)"** is confusing, since the two-handed form already allows Strength. The review suggested "one-handed: 1d8 + STR + FIN; STR only".
- **Drawing Weapons:** "Used hands … can't draw a normal weapon until the start of your next turn" comes before "Between turns: drawing a normal weapon costs 1 stamina", and the second can never apply to a used hand. Ordering or wording could make that obvious.
- **"Action":** a better name is wanted (Open Questions; the callout in Actions and Escalation). The review's suggestion was "beat" ("third beat costs base + 2").
- Diving to half cover and the floor on maximum stamina: see 10.5.
