# Fix order and dependency map (companion to the v0.9 review)

Findings are numbered as in `Review_Playtest_Packet_v0.9.md`. "Ripples to" means: if this changes, that finding's numbers or conclusions must be re-measured.

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
- Whether Dodge exists as a separate defense (spells and area attacks reference it).
- Stamina visibility (table procedure, telegraphing, Cunning's design space).
- Max stamina's coupling to HP (injury rules, H-2, healing all hang off it).

## 5. Loops to be aware of

- Phase 1 ↔ Phase 2: pool size sets max steps, the surcharge slope sets what those steps cost. Decide shape in 1, formulas in 2, re-check 1 once.
- Phase 1 → Phase 5: a steeper surcharge already lowers volley lethality (aim steps are actions); measure before adding ranged-specific fixes.
- Phase 4 → Phase 5: movement cost decides whether kiting exists at all; decide it before judging archers.
