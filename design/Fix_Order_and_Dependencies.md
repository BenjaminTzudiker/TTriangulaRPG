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
| **F7** | Max stamina = 6 + current HP is a death spiral at low level | At level 1 a 6-HP wound cut the pool 43%, so the first real wound decided the fight: winners were untouched 63–85% of the time and losers ended at −3 HP. | Medium | **Still open, softened.** The formula is unchanged (Stamina). 0.9.2's HP raise means the sample (10 HP, 16 stamina) loses 37.5% of its pool to a 6-HP wound instead of 43% [exact arithmetic]. Damage reducing maximum stamina (H-2) is still shelved (NITV). The designer has called max stamina tracking HP "meaningful but non-crippling (because it's a once-per-fight nerf…)" (design notes §3.2, "Consequences should feel weighty but cost little", [C:2026-11-05]), which bears on how much this is a problem. An optimal-play duel solver under 0.9.1 found no spiral in adjacent duels: after the opening exchange, recovery never reached the cap, so a mid-fight wound cost nothing until 0 HP; the lopsided results came from crit doubling (`claude/Exchange_Proposal_Optimal_Play.md` §3.6, §4.6). The same solver found nobody gets back to the cap after the opening, so the incentive against waiting (recovery wasted at the cap) works only until the first exchange. *[checked]* |
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

## 11. Findings from the 0.10.x assessments (added 2026-11-23)

Assistant-written assessments of packets 0.10.0 and 0.10.1, kept as working docs in the claude.ai project. This section keeps what they found that is still open under the current rules and isn't recorded elsewhere. Everything here is the assessments' analysis and opinion, not the designer's, and every figure is for the packet named. Rules questions they raised went to Open Questions instead.

### 11.1 The independent system read of 0.10.1

Source: `claude/Independent_System_Read_0.10.1_2026-11-13.md`. Its figures are exact enumerations of the packet's attack and block arithmetic, with no movement, cover or terrain, and a defender that blocks with hindsight, so they're a floor on harm.

**Its verdict.** The duel is sound. Three things stood between it and the party game the brief describes: nothing bounds how much offense lands on one defender between its recoveries; the 0.10.0 shield change reopened the opener guard (23%, now in §10's F1 row); and the day runs on HP, the one resource a player can't manage. It put about 65% on the direction reaching a good party game with two additions: a bound on concentrated offense, and a buffer in the day layer.

**Findings still open:**
- **Focus fire.** Two sample fighters making 3-step attacks before a fresh sample fighter's next recovery took it to 0 HP or below 64% of the time (19% at Melee Defense 4); three making 2-step attacks, 45%. If the target had just attacked for 9 stamina, 93%, half of those dead outright. 0.11.0's dash phase answers gang-ups that start apart, not ones that start in reach (§6; §10, F6).
- **Overkill skips System Shock.** Death at −10 HP is about 20 damage from full, so concentrated attacks often kill outright instead of reaching the dying rules.
- **Armor barely matters against an unblocked arrow.** Armor applies before the aim limit, so the free aim die absorbs it: armor 3 saved 0.45 HP against a plain Strength 1 longbow shot, and 0.02 HP once the archer bought one aim step. If plate should turn arrows, the order of armor and the aim limit in the procedure is the lever.
- **Casters in the open.** A level-1 caster (8 HP, Ranged Defense 1) was down 22% of the time to one archer's two plain shots and 73% to three, and 73% to one three-step melee attack (§10, F13).
- **The +1 for moving in reaction to a shot** is always worth its 1 stamina for a low-defense target, so it becomes a ritual on every shot, with a prompt each time.
- **The level curve (F5).** Maximum all-in against a fresh sword-and-shield mirror: level 1, 23%; level 30, 22% for a defense-first build and 52% for an offense-first one; level 99, 49% and 95%. The builds were its own assumptions, so the sizes are an upper range; the direction stands.
- **The day.** HP heals 1–2 a night for most level-1 characters, so one fight costs one to three nights. It suggested testing a partial recovery after each fight, for example graze leaks healing in full overnight.
- **No way out.** At equal speed a retreating side can't break contact, so fights that turn bad can't be left. (The designer has kept ending a fight by leaving the map out of the rules for now; design chat, 2026-11-17.)
- **What a GM needs** beyond what Open Questions lists: a default for how hard NPCs commit (it would pull the shelved NPC aggression profiles, Ledger H-6, forward); a cheap NPC, since the intro's mooks sit against "NPCs use the same rules as PCs"; and a "full strike" figure on stat blocks, so players can see the danger coming.

**Tensions it found in the packet text:**
- "Magic should be optional for anyone" (Magic) against casting in no armor and with no shield.
- Skill Points buying "extra choices under an ability you already own" (Currencies) against the reason for the currency split.
- A tier ability being "mostly an opportunity cost" against "An Ability Point purchase should be a real power boost" (both in Class Trees).
- "Attacking should be somewhat more stamina-efficient than perfect blocking" (Blocking) against "Lasting harm is fair in this game because you control whether you take hits" (Rest and Healing).

**Its guidance for abilities and magic** (its constraints, not adopted):
- Lethality is the offense that lands between a defender's recoveries, so abilities that add offense inside one recovery window (extra or moved turns, refunds on your own turn) feed the weakest point.
- Resistances should subtract once per attack, like armor, not add a defense value.
- An ability may change a price or add an option, but not add a number computed on every attack.

**A teaching shortcut it found:** the best block choice reduces to "blocks needed = damage ÷ defense, rounded up; one perfect block is free; armor soaks that many grazes; then buy back further wounds at 1, 2, 3 stamina". That's easier to teach than mixing perfect and grazing blocks freely.

### 11.2 The FableMax combat assessment of 0.10.0

Source: `claude/FableMax_Combat_Assessment_2026-11-11.md`, the synthesis of eleven workstreams (each with its own `claude/FableMax_*_2026-11-11.md` doc) and five blind reviews (`claude/FableMax_Reviews_2026-11-11.md`). Its figures are as corrected by the blind reviews. Tags: `[exact]` no sampling; `[solver]` an optimal-play duel solver; `[engine]` fights between the engine's agents, which attack all-in more than a careful player would, block at one fixed price and shoot once a turn. Packet 0.10.1 moved none of the headline figures.

**Its verdict.** The core was still promising, and the ranged package did what it set out to do. But whenever two or three attackers share a target, the fight is decided that round, and the target has nothing to buy that changes it. That's as true of a Strength archer firing three shots a turn as of swordsmen. It put about two in three on the direction surviving a table once the first-table list was done, and read the strongest case against it as "solvable arithmetic one-on-one, rocket tag in groups". It didn't accept that case yet: players aren't meant to be in equal fights, the engine overstates the rates, the lethal half is separable, and nothing had tested positioning.

**Its problems, worst first, and where each stands under the current rules:**
1. **Three attackers on one defender decide the fight, and a drop usually ends in death.** A fresh fighter is safe against one fewer 2-step attacker than its Melee Defense, a coin flip against as many, and gone against one more `[exact, confirmed blind]`. Enemy commitment is the dial: a party member down in round 1 in 22% of three-a-side fights against one-step enemies, 90% against two-then-three `[engine]`. *Now:* helping the dying is written (0.11.2, close to its proposal B); the dash phase (0.11.0) prices giving ground; the gang-up that starts in reach, and the outright kill past System Shock, are still open (§11.1).
2. **One point of Melee Defense is too big a step, and the default fighter is on the wrong one.** Each point multiplies duel length by about 2.5 (2.7 rounds at Melee Defense 3, 6.9 at 4 `[solver]`); the opener's all-in downs a fresh equal 23% of the time at 3 against 1–8% at 4. With the Fighter core, the all-in becomes the best opening at Melee Defense 3. HP can't buy the guard back: HP 14 brings the stamina for a fifth step. Two-handers (Melee Defense 2) still duel as an initiative roll (98% first mover, 1.1 rounds). *Now:* unchanged; the two-handed grip still gives no Melee Defense. The Fighter core changes in 0.12.0.
3. **A Strength archer's three shots drop a target as fast as melee.** A Strength 2 archer fits three 4-stamina longbow shots in 16 stamina (4 + 5 + 6 = 15): one such archer downs an unarmored 8-HP target in one round 50% of the time, and two of them the sample fighter 53% `[exact]`. At Ranged Defense 1 no affordable block lowers the wound on 76% of shots, so neither player has a decision. *Now:* the longbow is still 4 a shot.
4. **The +1 for moving in reaction to a shot is a toll, not a choice.** Always moving costs 0.3 stamina a shot against perfect play, never moving 3.4; it's the same +1 at any speed, so it doesn't deliver its reason (target speed should matter) `[exact, confirmed blind]`. Folding it into base Ranged Defense never hurts the target (two longbow archers on the sample fighter: 44% → 17%). *Now:* unchanged (also §11.1).
5. **Drawing Weapons doesn't do its job.** A quick-draw blade is free the moment the archer's turn ends, so off-turn the archer has its blade's Melee Defense anyway; the rule bites only on the archer's own turn. One 2-step attack downs an archer at Melee Defense 1 / 2 / 3 77% / 16% / 0% of the time `[exact]`. *Now:* 0.11.4 added that drawing to block a shot's opportunity attacks gives up the shot; the between-turns exception is unchanged.
6. **Two of the four bows don't work for the build that should want them.** The shortbow has no level-1 niche and then jumps at Finesse 3; one point short of a bow's Strength costs only a square of band width. *Now:* unchanged.

**Lesser findings:** an equal-speed archer that acts first can't be forced into melee on open ground beyond about 5 squares, though a pressing fighter limits it to a dozen or so shots, none costing HP; there's no safe band for an archer; cover adjudication needs up to 16 line traces for a ±1 that matters a lot; shooting into a melee costs nothing beyond creature cover; acting first can hurt in two-a-side fights (party wins 17% acting first, 67% otherwise); at level 30 a soft target within 4 squares falls in one archer turn 93–100% of the time; a shot takes about 20 table steps against 12 for a melee attack.

**Changelog reasons that no longer hold, by its check:** 0.9.2's HP change (the guard was measured at Melee Defense 4; see §10, F1); 0.10.0's +1 for moving (speed-blind); 0.10.0's Precise at shot cost 3 (no level-1 niche against a reacting target, overshoots from Finesse 3). Others held, some only in direction (the shield cut reached parity by lowering the shield user).

**Its proposals** (try-first in bold; none adopted):
- Problem 1: **an enemy-commitment line on stat blocks** (the shelved NPC profiles, Ledger H-6); a help rule (done); a melee wound limit per attacker per turn, or a drop floor ("a blow that takes you from above 0 HP can't leave you below −5"). The engine tested the wound limit: deaths in three-a-side fights 65% → 24%, outright first drops 39–65% → about 10%, winners unchanged `[engine]`.
- Problem 2: **the other hand is always worth +1** (shield, second weapon or two-handed grip); then a proficient weapon +2, putting every martial style at Melee Defense 4; or keep 3 and take 1 off damage per step; rule on the Fighter core's timing; initiative bidding.
- Problems 3–4: **longbow back to 5 a shot** (50% → 18%, 53% → 21%); fold the +1 into base Ranged Defense 2; apply armor after the aim limit, not before.
- Problem 5: **a blade drawn into a hand that shot this turn gives only +1 Melee Defense until your next turn**; or drop the rule's purpose and write its gaps.
- Problem 6: **+1 shot cost per point of Strength short**; decide what the shortbow is for.

**What it said only a table can answer:** whether positioning answers the gang-up; whether blocks feel like decisions (watch for players asking for a chart); time per attack and per shot; duel length by feel at Melee Defense 3 and 4; whether a GM can run enemy commitment from a one-line profile; how a table takes a first drop in round 1; whether players react to every shot; whether anyone fires three shots a turn; whether the quick-draw ritual gets forgotten; the tracking load.

**What the workstream docs add** (read 2026-11-23). Each `claude/FableMax_*_2026-11-11.md` doc carries its own blind-review corrections at the top; these are the points the synthesis above leaves out that still bear on the current rules. Figures are for 0.10.0.
- *Exchange guard:* melee builds sit on three plateaus: Melee Defense 2 duels last about 1.2 rounds with the first mover winning 95–98%, Melee Defense 3 about 2.5 rounds at 73–85%, Melee Defense 4 five to seven rounds at 64–67% `[solver]`. A point of Melee Defense is worth more than going from 1d8 to 1d10, so parity between a shield and a two-handed grip falls about half a point apart, where no whole-point rule can put it. Tested and rejected: a melee wound cap at the best step's die + Strength leaves the opening guard at 23.0%, because every one of those downs involves critical dice. Argued: damage reducing maximum stamina (H-2) would steepen the tempo spiral. Its solver priced the first move at 2–3 stamina for shield builds and 7–8, cliff-shaped, at Melee Defense 2. Level 30 wasn't measured.
- *Focus fire and deaths:* raising every Melee Defense by a point didn't change round-1 drops in three-a-side fights (about 90% under 0.10.0, 0.9.3 and all melee +1 `[engine]`): Melee Defense decides duels, not gang-ups. Arrows drop people and blades kill them: three archers dropped a party member by round 2 in 44% of fights and killed one in 2.5%, three melee enemies 95% and 65% `[engine]`. A party member died in 4–5% of 1v1 fights, 28–32% at 2v2, 61–65% at 3v3 and 91% at 6v6 `[engine]`. It would word the melee wound limit per attacker per turn, so that splitting a turn into two attacks gains nothing. One less damage per step (d8 + 2) halves the guard (23.0% → 11.0%) and three attackers' drop chance (45% → 21%), with best-play mirrors at 3.7 rounds and 66.5% `[exact; solver]`.
- *Mixed parties:* the drop in group fights came from the turn-1 charge and counter-charge (whoever charges arrives at about 5 stamina, where a 3-step reply drops even the shield fighter 73% of the time `[exact]`), not from focus fire; archers on the enemy side lowered round-1 drops (91% against three melee, 56% against one melee and two archers). Danger rises steeply between 1v1 and 2v2 (a PC down by round 2 in 15% against 69–75%). Its "price the charge" proposal (bought squares count as actions) is in effect the 0.11.0 dash. Its "set against a charge" idea (an opportunity attack when an enemy that bought movement ends in your reach and attacks you) wasn't taken up. It argued that both readings of the review's per-attacker block reset (F6 option 2) are weak, since the victim is beaten by the number of attacks against 4 a turn of recovery, not by escalation.
- *Ranged lethality:* the aim limit sets an HP cliff: the share of longbow shots that can take a target from full in one hit is 50% at 6 HP, 25% at 8 and 12.5% at 10, and the archer's own cliff is at 15 stamina (three shots a turn) `[exact]`. Levers beyond the synthesis's: make the reaction's +1 last until your next turn (two archers on a caster 88% → 85%, on a duelist 61% → 45%), or lower the aim limit a notch.
- *Reactions:* the +1 for moving pays only in a middle band of totals (7–18 against Ranged Defense 2, armor 2, limit 5), so the choice is block arithmetic done twice. Seeing the roll first is worth about 0.24 stamina a shot. The clause that point-blank opportunity attacks need the shooter in reach at declaration blocks a real exploit (closing in would otherwise also cost the archer an attack at Melee Defense 1). Its other options: the +1 only for a reaction of 3 squares or more (weak by the blind review), or per round.
- *Block decisions:* against Ranged Defense 1–4, 76% / 40% / 16% / 6% of shots leave no affordable block that lowers the wound; when some block helps, a partial block is best 39–45% of the time `[exact]`. A greedy rule matched the best block 96.8% of the time in melee: add blocks one at a time, each time taking whichever saves the most HP per stamina (a perfect block at its rank, a graze at 1, or upgrading a graze at rank − 1), until the next costs more than an HP is worth; for shots, do the same and then cap at the limit (98.5%). It found the shortcut "block ⌈damage ÷ defense⌉ times, then choose how many are perfect" wrong 61% of the time, because armor also soaks unblocked damage; compare the shortcut in §11.1. A shot takes about 20 table steps against 12 for a melee attack. Proposals: aim lowers the target's defense by 1 a step instead of adding dice, which removes the limit; or keep the rules and announce shots as two numbers ("16, wound 7").
- *Mixed turns:* n actions cost the same in any order, and a mixed bow-and-blade turn is never a bargain. The Drawing Weapons audit's gaps beyond the synthesis's are in Open Questions. With a free quick-draw blade the archer is a competent melee attacker; its weakness is defensive or nothing.
- *Cover and terrain:* +1 / +2 isn't noise (two archers on a caster in scattered cover, HP lost by round 2: 6.6 with cover worth nothing, 2.6 at +1 / +2 `[engine]`), and a point of cover is worth a point of shield or Agility. Because of the aim limit, a point's value peaks at total defense 3–4. Against three or more shooters, standing in cover beats diving into it each shot. The weak part is adjudication: a pillar "between" gives half cover 74% of the time and three-quarters 26%, the square behind a wall's end gives only half 37% of the time, and a call can mean 16 line traces. Proposals: a visible test (half if the centre line crosses an obstacle or creature, three-quarters if it crosses terrain you're hugging; its lean); standing in three-quarters cover worth more than diving into it; or one grade.
- *Attributes:* light armor uses Agility, armor uses Finesse, Strength covers HP and bows, with no spread winning everywhere at levels 1 and 30. Worst first: Agility 2 is mandatory for unarmored casters (their only bought Ranged Defense; two archers drop a caster 91% without it and 51% with it, standing still); on the two-handed longsword (1d10 + STR or AGI + FIN) Agility 2 strictly dominates; Finesse 2 is a dead point for an archer. Proposals: Ranged Defense from even Cunning instead of even Agility; remove even Agility's Ranged Defense; drop "or AGI" from the two-handed longsword.
- *Bow niches:* within 4 squares a fresh soft level-30 caster falls in one archer turn 93–100% of the time `[exact]`. Higher Finesse erodes the superheavy's edge over the warbow. Proposals beyond the synthesis's: Precise's limit at d4 + half Finesse, with the d4 no longer always critical at Finesse 5; a shortbow volley the target answers with one reaction (the blind review found it lowers lethality rather than making a niche, unless blocks escalate across the volley); give the superheavy Piercing 3 instead of band width.
- *Kiting and closing:* its stand-off figures predate 0.11.0's dash and single escalation, which reprice every chase. Its proposals (a shot spends 2 squares of free movement; a closing reaction off the off-turn track; or accept the stand-off with GM guidance) were written for the old movement rules.

### 11.3 Skill, uncertainty and positioning (2026-11-14)

Source: `claude/Skill_Uncertainty_Positioning_Notes_2026-11-14.md`, an argued note on packet 0.10.1 (nothing run for it). The principle it proposed is in the design notes (§3.2, agency through foresight, marked UNCERTAIN). What else it argued:
- **Where uncertainty should sit.** Hiding the die buys little: a longsword step against Melee Defense 3 is uncertain by about one block, while whether the next enemy commits nothing or four steps is about ten. So the exchange can stay all-at-once and fast, and the uncertainty worth having is what other creatures will commit, and when. Bounding that (with reach, and with enemy commitment stated on stat blocks) is what would make holding stamina back a real bet.
- **The numbers carry skill when the best choice sits in the middle and moves with the state.** By that test commitment passes at Melee Defense 4 and fails at 3 with the Fighter core, blocks fail (one price fits), and movement failed before 0.11.0.
- **For abilities:** the core loop has to hold with none (characters with no tree, GM creatures). Abilities should bend one fight state for one class, gated by that state rather than usable "at any time", and should change the situation (break contact, deny reach, swap places) rather than postpone it (refills, soak).
- Its section 4 compares how other games handle the same jobs (Exalted 3e, The Riddle of Steel, Mythras, GURPS, Shadow of the Demon Lord, BattleTech, Into the Breach, Gloomhaven, 13th Age, Draw Steel, Starsector), with sources.


### 11.4 Attribute roles brainstorm (2026-11-05)

Source: `claude/Attribute_Roles_Brainstorm.md`, an assessment and brainstorm against packet v0.9 (two exact calculations, nothing run). Its diagnosis, most severe first: three empty mental attributes, an overloaded Agility (in its words, "the de facto Constitution"), a polarized Strength (too strong on ×2 and ×3 weapons, nearly worthless past 3 for everyone else), and a hollow half of Finesse (the opportunity attack cap, while opportunity attacks did little).

**Acted on since:** System Shock's dying roll uses Will (0.9.1); Agility no longer adds to initiative, and Cunning sets it (Agility + Cunning only breaks ties); purchased on-turn movement became the dash; a Strength requirement for shields is in Not in This Version; whether stamina is public, including bands, is in Open Questions. The designer's stated wariness about Will as "the extended contest ability" and the decision that strain grows only with level are in the design notes (§3.2 and §3.4).

**Still open:** Strength's ×2 and ×3 multipliers (F8 above); mental attributes' combat benefits (Open Questions; Phase 7).

**Its proposal:** give each attribute one home it owns instead of more small bonuses to stamina flow and defense, which it argued become mandatory: Strength for force (bounded per-step damage, shoves and grapples, armor and shield requirements), Agility for movement and evasion, Finesse for precision, Cunning for tempo and awareness, Will for resistance, Intelligence for technique. Its candidate hooks for Phase 7, with its verdicts (assistant suggestions; the designer hasn't taken a view on them unless noted):
- *Cunning:* one off-turn cost per round per odd Cunning doesn't count toward escalation (promising once off-turn costs matter); the opportunity attack cap moves from Finesse to Cunning (only if opportunity attacks matter); "reading the shot", improving the dive or adding Ranged Defense, as an answer to unshielded builds facing archers (strong candidate; the Ranged Defense version risks being mandatory); a deterministic Feint comparing Cunning values (ability, not base).
- *Will:* each odd Will soaks 1 progress per step of a control track, as armor soaks damage (once control exists); a morale threshold (if being out of the fight before 0 HP returns); Rally, paying part of a nearby ally's block (ability; a possible answer to focus fire, at the cost of another off-turn prompt). Rejected as weak: ignoring strain overage (it's more strain in disguise, which the designer doesn't want as a choice) and soaking a graze leak (brings back stalemates).
- *Intelligence:* ignoring 1 armor per odd Intelligence per attack, not per step (a light-weapon niche against armor; check against the crit rule's armor ignore); crossbows and devices keyed to Intelligence through cost, not per-step damage; revealing a creature's damage or special attacks (an information hook on telegraphing lethality, at risk of blurring into a Knowledge skill). Casting keyed to Intelligence belongs to trees, not base bonuses. Rejected as weak: a lower surcharge (whatever touches it becomes mandatory) and more prepared options (versatility is what Skill Points buy).
- *Strength:* requirements instead of multipliers, adding at most ×1 per step; shoves and grapples (a role that doesn't ride step count, so it stays useful at high level); grazes from heavy Strength weapons leaking 2 (test before liking: it raises lethality on a sensitive lever).
- *Initiative and stamina (its second round):* initiative bought with stamina (since studied: Not in This Version); medium and heavy armor reducing Agility's share of initiative (moot while Agility only breaks ties); control defense split by kind (physical holds by Strength or Agility, fear by Will, deception by Cunning), with stamina still the main answer.

**The designer's leans it recorded (its summary, not quotes; not decisions):** undecided whether to weaken Agility or raise the others; purchased on-turn movement would almost certainly be cut back (it was); leaning away from opportunity attacks until they clearly solve a problem (they came back in 0.11.1, with holds); a Strength requirement on shields sounds reasonable; leaning toward public stamina in principle, without a way to track it at a table.

Its engine runs to do later, once their phases land: an attribute-spread sweep at a fixed Expertise budget (does any attribute's first two points buy more than another's?), the value of +1 initiative after the first-mover edge is re-measured, "reading the shot" against an archer, and the per-attack armor ignore on light weapons against armor 2–3.

## 12. After packets 0.11.4 to 0.11.6 (added 2026-11-24)

- **Packet 0.11.4 (2026-11-20):** Opportunity attacks provoked by shooting in melee resolve immediately when the target is declared, before paying, and the shooter may cancel at no cost (Ledger MV-3; engine experiment preset `exp-0.11.4`). Removes the F14 double-provocation edge case during ranged reactions (§10.5).
- **Packet 0.11.5 (2026-11-23):** Recovery holds shelved (Ledger H-9; Not in This Version). The end-of-turn hold order (hold from what you have left, then recover) was kept to protect close 3v1 fights (41% vs. 60%) and reworded by what it does. Twelve exploratory martial candidate abilities were placed in the class trees (Phase 7).
- **Packet 0.11.6 (2026-11-24):**
  - Clarified stamina and hold states (`ready`, `held`, `returning`, `spent`) across `Stamina`, `Holds`, `Starting Combat and Turn Structure`, `Quick Reference` and `Defined Terms` (aids F11 table tracking; avoids colliding with the `Locked` status marker).
  - Added `Forced Movement` (exploratory) and six martial candidates (`Shove` comparing Strength instead of adding creature sizes, `Drive Through`, `Unshaken`, `Many Hands`, `Dual Wielding`, `Paired Blades`), revised `Sweep`, `Tumble`, `Riposte`, `Hold the Line`, `Tear Free` and `Cornered`, and shelved `Quick Reflexes` and the remaining unplaced 0.11.6 candidates. Watch-item for Playtest #1: `Dual Wielding` (Tier 1) uses separate attacks per hand and forfeits `+1 Melee Defense` when both hands attack, which is much weaker in 1v1 duels than the combined-attack version tested earlier; test whether group-fight utility carries it before `Paired Blades` (Tier 3).
  - All candidate abilities remain `Exploratory` taste anchors pending first table playtesting; F1, F4, F5, F6 (close start), F8 and F12 remain open underneath.

## 13. After packet 0.12.0 (added 2026-11-24)

Packet 0.12.0 removes and shelves **Strain** (Not in This Version; Ledger H-10) and replaces all four martial class cores with `Exploratory`, strain-free placeholders (`Second Wind`, `Opportunist`, `Press the Wound`, `Poised Guard`), plus two core-upgrade candidates (`Patient Opportunist`, `Relentless Fury`).
- **F5 (level scaling):** strain growth lines (`+1 maximum strain`, `+1 strain recovery`) are gone; stamina pool growth vs. flat HP/defense remains open.
- **F11 (d) (Fighter strain-overage oddity):** gone with strain.
- **F13 (class cores):** all four martial cores are rewritten as exploratory placeholders paid inside the fight (ready stamina, held stamina, escalation or dash-phase timing); multiclass balance now leans on cores competing for in-fight bottlenecks rather than a shared nightly strain pool.
- **F14 (Rogue turn-order timing):** the old turn-moving Rogue core's next-round slot ambiguity is gone; `Opportunist` acts inside the existing initiative-ordered dash phase (including the opening dash phase before the first turn, capped at `1 + Cunning`), keeping permanent turn order separate from class cores.
- **Mechanical lessons from 0.12.0 core design & cross-review (2026-11-24):**
  - *Turn-1 heavy ceiling:* at L1 max stamina 16 (vs. 18 for 4 base-3 steps), giving ≥2 upfront offensive stamina on Turn 1 unlocks Turn-1 one-shots (`Reckless −2` downed a fresh sample fighter 80.4% with a greatsword and 99.3% with a greataxe `[exact]`); averaged 1v1 win rates hid this. `Press the Wound` refunds after the attack instead.
  - *Second Wind action tax vs. multiclassing:* on the same trigger (`only when attacked`, no `−1`), adding `"counts as an action"` drops a Fighter mirror from `+12.2` to `+3.8`; comparing the two candidate rules side by side, the adopted version (`any time off-turn + action`, no `−1`) gives `+7.8` mirror / `+3.8` shortsword duelist / `+3.6` greatsword against the alternative (`only when attacked, no action`, no `−1`) at `+12.2` mirror / `+12.4` shortsword duelist / `+5.4` greatsword `[exact, L1 contact duel solver]`, and costs nothing to a defensive Fighter who blocks and holds.
  - *Poised Guard before contact:* spending (rather than refunding) held stamina avoids cross-room standoffs (closing still beats waiting: Monk 82% vs. 32%, enemy 68% vs. 18% at MD 3 `[exact, L1 contact duel solver]`), and dropping the reach gate lets `Poised Guard` work against reach-2 attackers and opportunity attacks.
  - *Patient Opportunist:* Rogue Tier 2 intentionally allows a capped `1 + Cunning` dash-phase hold (a small, gated exception to the end-of-turn hold order).
- **Engine:** existing presets keep strain so earlier reports reproduce; a 0.12.0 preset is deferred until after 0.12.0 is released.
