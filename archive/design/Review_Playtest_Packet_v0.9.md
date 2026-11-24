# Review: Playtest Packet v0.9

*Core-rules critique against the packet's own goals and the design notes (§2 pillars, §3 principles). Simulation method, assumptions and full tables are in Appendix A; the simulator is attached so every number can be re-run.*

---

## Executive summary

**1. The block-cost curve and the attack-cost curve have different orders, so commitment is pushed to the extremes.** A k-step attack costs ≈ k²/2 stamina; fully blocking it costs ≈ (rk)²/2, where r = damage per step ÷ defense value (≈1.9 for the level-1 sample fighter). So the defender's cost climbs r² ≈ 3.6× faster than the attacker's: against perfect blocks alone, full defense costs 2× the attack at two steps and 2.6× at four, and grazes-plus-armor buy parity only at one or two steps because their offset is flat. The consequence at level 1: an equal opponent who spends their whole pool (4 steps, 14 stamina, mean 30 damage) takes the sample fighter from 8 HP to 2 or less 54% of the time and incapacitates them 34% of the time, even when the fighter spends all 14 stamina optimally. In an equal duel the first mover wins 69%; 94% when the opening strike crits and rolls high. At level 30 the middle commitments (2–3 steps) flip to defender-favored and identical fighters stalemate (75% of 2-step duels unresolved after 30 rounds) while the full strike remains decisive through crits. At level 99 the first attack incapacitates 69% of the time. Nothing in the rules holds r steady across levels or builds.

**2. Critical doubling is the game's main luck multiplier.** At FIN 1, 44–68% of 2–4-step attacks contain a crit; at FIN 0 it is still 29–68%. The same attack against the same spend yields 0, 2 or 4 HP depending on the dice. Removing the doubling (crit dice still ignore armor) cuts the level-1 alpha strike's kill rate from 34% to 1% and the first-mover edge from 69% to 55%. Doubling is also what makes 1–2-step attacks dangerous at all against armor 2; without it, low commitment never wounds. The game's danger gradient is currently carried by dice rather than by pressure.

**3. Ranged Defense 1–3 under triangular block costs means anyone without a shield has no stamina answer to arrows.** An unaimed 3-stamina shortbow shot costs an unarmored character 4 HP on average and downs them 33% of the time; one aimed shot (4–6 stamina) downs them 59–88%, two aims 95–100%. A shielded, armored fighter spends 11–12 of 14 stamina to hold a two-to-three-aim longbow volley to 3–8 HP. Cover makes all of it vanish, so terrain decides. Maximum HP Damage (H-1) at the proposed numbers caps the no-block worst case, leaves the stamina drain untouched, does not save unshielded targets (cap ×2 on a 70%-likely crit ≥ their HP) and adds an all-or-nothing blocking cliff. It is not the right lever for this problem.

**4. The shield's +2 is worth more than any attribute investment, and defense is priced linearly for a good that is worth its square.** Melee Defense 4→6 cuts full-block costs 40–65%. The sample fighter beats a same-stats two-hander 73–86% of duels and beats "nimble" unarmored builds 65–88% at both levels tested, contradicting the stated armor/agility niche split (ledger EQ-1). Two-handers, archers and casters are both the ranged victims and the losing melee builds — the P4 pillar fails for exactly the concepts the game will need to sell.

**5. Focus fire has no answer and the GM holds the lethality dial.** Three equal attackers down a fresh sample fighter in 1–2 rounds 100% of the time, in heavy armor too, because blocking three 2-step attacks costs ~15 stamina against 4 recovery and nothing is left to withdraw with. That is plausible, but combined with (1) it means NPC commitment — how many steps the GM declares — is the single biggest lethality input, and it is invisible to players. Telegraphing is unsolved and NPC profiles are shelved.

**Overall assessment.** The core logic is right: one pool, deterministic blocks, commitment before results, grazes and armor as the counterweight, live positioning. At one or two steps of commitment the exchange trades near parity and every decision the designer wants a player to make is present. It is not yet sound enough to build weapons, classes and magic on, because the cost curves make the ends of the commitment range dominant and the crit doubling makes those ends swing on dice. Two shape changes are needed before content: (a) make the attacker's and defender's per-attack cost curves the same order (or bound the wound one attack can inflict), and (b) replace crit doubling with a linear crit effect. A third decision is needed on whether unshielded characters should have any stamina-based answer to missiles. Everything else — opportunity attacks, movement numbers, weapon table, strain, armor steps — is tuning that can proceed once those three are settled. Confidence: high that the shapes behave as described (they follow from the arithmetic and reproduce at every level tested); medium on severity at the table, which depends on how often NPCs commit fully.

---

## Findings, ranked by severity

### F1. Attack and block costs are different-order curves; commitment collapses to the extremes

**Problem.** Each attack step costs base + (steps already taken): k steps cost k·base + T(k−1). Each block costs 1, 2, 3… within the attack, and each step needs about r blocks (r = damage per step ÷ defense value). So the defender climbs the triangle r times faster than the attacker. At level 1 (r ≈ 7.5/4), fully blocking the mean roll costs 2 / 5 / 12 / 23 stamina against attacks costing 2 / 5 / 9 / 14. Grazes-plus-armor (two free leaks at armor 2) buy parity at k ≤ 2 and then stop mattering because the offset is flat while the gap is quadratic. Result: 1–2 steps is a stamina trade where nothing lands; 3 steps wounds; 4 steps is decisive.

**Stakes.** P2 (danger you can see and answer): the victim of a full strike sees it coming and has no answer; the defender's 14 stamina buys 2–6 HP of damage rather than safety. §3.1 "punish mistakes with lost tempo, not death": the victim made no mistake. §3.1 "attacking somewhat more efficient than perfect blocking": against perfect blocks alone it is 2× at k=2 and 2.6× at k=4, not "somewhat". §3.6 "core rules interesting without abilities": the interesting middle is one or two steps wide.

**Evidence.**
- Static (Appendix A, Table 1): full-block cost vs attack cost by MD and armor; the ratio rises with k at every defense value.
- Alpha strike vs full defender, level 1: injury 0 HP 2%, 1–3 HP 31%, 4 HP 12%, 6 HP 20%, down (≥8) 34%. Defender spends 12–14 stamina 69% of the time. A defender at 13 stamina instead of 14 dies 50%; at 9 (after one 2-step attack), 65%. Hand check: 30 damage, one crit die, MD 4, armor 2: 4 perfect + 4 grazing = 14 stamina, 8 blocks stop 32, 4 leaks − 1 armor = 3, doubled = 6 HP.
- Duel outcomes, level 1, equal fighters: first mover wins 69% (alpha vs alpha), 67% (2-step vs 2-step), 72% (chip-then-kill). Conditioned on the opening strike: crit and roll ≥30 → first mover wins 94%; no crit and roll <30 → first mover wins 26% (drained and punished). The strategy choice between sensible policies moves win rate ~5 points; initiative and the opening dice move it ~70.
- Holding a 5-stamina defensive reserve loses 75–22 to full commitment. Pure 1-step play never wins (0%): 7.5 damage never beats two grazes and armor 2.
- Level 30 (MD 6, 9.5/step, 21 stamina): block cost vs attack cost 2/2, 4/5, 8/9, 17/14, 23/20 for k=1…5. The middle flips to defender-favored; 2-step duels stall (75% undecided at 30 rounds), full-strike duels last 9 rounds median and are decided by crits (first mover 64%). Level 99 (MD 6, 11.5/step, 38 stamina, 7 steps): 35 to attack, 80 to block; the opening strike kills 69%.
- The variants in Appendix A, Table 9 show how knife-edged this is: steepening the surcharge to +2 per prior action balances level 1 (12 to attack 3 steps, 12 to block) but produces 68–86% stalemates at level 30; slowing block escalation does the same; +2 MD for everyone makes k=4 defender-favored at level 1. No single flat knob balances all levels because r drifts with level and build.

**Confidence.** High on shape; the numbers reproduce at three levels and under three defender valuations of HP. Playtesting will tell you how often tables actually commit fully — the sim assumes rational play.

**Scope.** Shape. The problem is the pairing of two triangular progressions with r ≈ 2, not any one number. It cannot be fixed by HP, armor or defense values alone (each moves r, which re-breaks a different level).

**Options.**
1. *Make the surcharge grow faster than the block escalation* (surcharge is Mechanism open). Step cost = base + 2×(actions already taken), or base + (actions)² − but keep it flat-integer. This alone fixes level 1 and over-corrects level 30; pair it with a deliberate r target per level (below).
2. *Decide and hold a target r by level.* r is the master balance parameter. Write it down (e.g. "damage per step ≈ 1.6× the common defense value at all levels") and make the attribute/weapon/armor tables obey it — damage per step grows with STR/FIN at +1 per point, defense grows at +1 per two points, so today r drifts. The cheapest lever is the weapon flat bonus (e.g. STR adds to damage only on STR weapons at every other point, mirroring defense) or the Melee Defense attribute steps.
3. *Bound the wound per attack rather than the stamina.* A per-attack wound ceiling (one step's weapon dice + STR, applied after armor and *instead of* doubling) keeps the full strike's stamina pressure — it still forces 14 stamina — but turns "down from full" into "wounded from full". This is H-1 re-aimed at melee; see F3 for why it does not work as a ranged fix, and note the cliff (partial blocks are worthless until the residual drops below the cap) unless the pressure above the cap also does something (H-2-style max-stamina loss is the natural candidate).

### F2. Critical doubling is a frequent luck multiplier, not a skill reward

**Problem.** Any crit die doubles everything that gets through blocks and armor. With 2–4 dice in play, a crit is the normal case (FIN 1: 44 / 58 / 68%; FIN 3: 61 / 76 / 85%; FIN 0 d8: 23 / 33 / 41%), so the multiplier fires more often than not and the "no crit" attack is the discount. Because HP is 6–12 and armor 2, the doubling converts a 1-point leak into 2 HP and a 4-point leak into a kill. Finesse does not make crits skilful; it moves the frequency from "often" toward "always" (a FIN 5 dagger crits on every die).

**Stakes.** P2's test, verbatim: "a named character is only seriously wounded after being pressured or misjudging, never by luck alone." §3.3 "skill, not luck, should decide decisive outcomes." §3.6 "a recurring rule must earn its per-attack cost": the rule has two per-attack effects (armor-ignore per die; doubling once), and the small one is the one you compute per die.

**Evidence.**
- 2-step attack (mean 15) vs MD 4 / armor 2, defender spends the "correct" 5 stamina (2 perfect, 2 grazing): 0 HP with no crit, 2 HP with one crit die, 4 HP with two. To stay at 0 HP the defender must instead spend 5 / 7 / 10 — the dice double the block cost.
- Variant D (no doubling, crit dice still ignore 1 armor): level-1 alpha kill rate 34% → 1%, mean injury 6.1 → 3.8; first-mover edge 69% → 55%; duels lengthen from 4 to 13 rounds median because 1–2-step attacks now never wound armor 2. That last point is the honest cost of the change: today, chip damage exists *only* through doubling.
- The winner of a level-1 duel is untouched 63–85% of the time and the loser ends at −3 HP on average: fights are lopsided because the first crit cascade (wound → lower max stamina → cannot block the next strike) settles them.

**Confidence.** High. This is arithmetic on a Locked rule; the argument for reopening it is that the rule's own stated intent (skill, not luck) is not what the numbers produce.

**Scope.** Shape (×2 after armor). The crit *range* mechanism is fine and can stay.

**Options.**
1. *Linear crit:* each crit die ignores 1 armor **and** adds +1 (or +2) HP damage after armor; no doubling. Finesse then scales the expected bonus smoothly, a dagger at FIN 5 is reliably nasty rather than automatically doubled, and the block decision loses one branch.
2. *Doubling only on a threshold* (two or more crit dice), which makes it rare and genuinely skill-gated — but it keeps the branch in the defender's arithmetic.
3. If doubling goes, give low commitment a non-random bite so F1's middle is not dead: e.g. grazing leaks 1 **before** armor applies only on the first graze, or armor soaks leaks but not residual (so a 1-step attack that out-rolls two blocks puts a point through). Test against the design target that k=1–2 should be a near-even trade.

### F3. Ranged Defense 1–3 gives unshielded targets no answer; H-1 is not the fix (evaluation item 7)

**Problem.** A perfect block against a missile stops Ranged Defense (1, or 3 with a shield) per escalating stamina, and a graze at RD 1 stops nothing net. So a character without a shield cannot buy safety from an arrow at any price; their only answers are cover (+2/+5) and armor. Aim then stacks 1d6+FIN per step on top. The intent (DF-2: innate ranged defense is low; cover, shields, positioning and armor do the work) is honored, but the magnitude means P2 fails for every two-hander, archer and caster caught in the open, by rule rather than by misplay.

**Stakes.** P2; P4 (the shield-less concepts are the fragile ones); §3.5 balance resilient to GM style (whether there is cover is the GM's map); §3.2 lasting harm is acceptable *because* damage is avoidable.

**Evidence** (Appendix A, Table 5; level 1, archer FIN 2 STR 1, aim dice can crit — see assumptions):
- Shortbow, no aim (3 stamina) vs unarmored no-shield (6 HP): target spends 5.3 stamina trying, takes 4.0 HP, down 33%. One aim (4 stamina): down 72%. Two aims (6 stamina): down 100%.
- Longbow, no aim (5 stamina) vs the same target: 6.2 HP, down 25%. One aim: down 88%.
- vs shield + medium armor (sample fighter, RD 3): no aim → 3.2 stamina, 0 HP. Two aims (8 stamina) → 11.0 stamina, 3.4 HP, down 16%. Three aims (11 stamina) → 12.3 stamina, 7.7 HP, down 50%.
- With three-quarters cover (dive): every row above becomes 1–6 stamina, 0 HP.
- Shots are flat-cost, so an archer can also fire four unaimed shortbow shots for 12 stamina: four separate attacks, blocks reset each time, each one ~4 HP to an unshielded target.
- Scripted archer vs approaching fighter (12 squares, open field): the archer's opening volley decides it — archer wins 24% (fighter downed before contact), fighter wins 76% and arrives with 4.5 of 8 HP on average; archer is dead within a turn of contact (MD 3 with a quick-drawn shortsword). With cover for the fighter: 100% fighter, 0 damage. Kiting does not work: free movement is equal and the fighter buys 2 squares per stamina flat.

**On Maximum HP Damage (H-1) as the fix.** Reading the shelved rule as "injury = min(residual after armor, weapon dice + STR, floor FIN), then doubled on a crit":
- *Shielded target:* a defender who blocks at all is already below the cap by the time the cap would bind, so the stamina drain (11–12 of 14) is unchanged. The cap only changes the zero-block case from 19.5 to 5.5 (11 with a crit) — still "block everything or probably die".
- *Unshielded target:* the cap is 3.7 (shortbow) to 5.5 (longbow) average, ×2 on a crit that fires 33–70% of the time, against 6–7 HP. One shot is still a coin-flip kill; two shots kill. Aim becomes pointless against them (cap binds), so the optimal archer sprays cheap unaimed shots instead — the lethality moves, it does not fall.
- *Cliff:* under a cap, partial blocking is worthless until the residual drops below the cap, so the decision degenerates to all-or-nothing and the p/g search gains a term, which is the per-attack cost you were already worried about (p.1720).
- *Weapon identity:* the cap would differentiate STR from AGI/FIN weapons, but the weapon table already has die size, base cost, STR multipliers and properties to do that with, and F8 shows those knobs are what actually need work.
- Verdict: worthwhile problem, wrong lever. The lethality comes from RD 1–3 under triangular costs and from doubling; H-1 touches neither. Its real promise is as a melee wound ceiling (F1, option 3) — if it comes back, come back for that reason and apply it before any crit effect.

**Confidence.** High on the table; medium on the archer scenario (scripted policies; a smarter archer with AGI 3 and party support does better, but the open-field result is driven by RD, not tactics).

**Scope.** Shape for the unshielded case (RD 1 and triangular costs); numbers for the shielded case.

**Options.**
1. *Fold Dodge into Ranged Defense* (Dodge is Exploratory; this answers "whether Dodge stays"): RD = 1 + even AGI (armor-adjusted) + 2 shield, + cover. A nimble unarmored archer gets RD 2–4, a shielded fighter 3–6. Narration: the departure from realism you already made is awareness — the target is moving as the bow comes up, not parrying the arrow. This is the structural fix; it conflicts with your p.1142 taste against "I dodge the arrow", so decide that first.
2. *Different cost shape for ranged blocks:* ranged perfect blocks cost a flat 2 (no escalation) — you cannot parry an arrow, but keeping your shield up and your head down does not get harder with each arrow. Removes the quadratic blow-up against shields; does nothing for RD 1 alone, so pair with (1) or with shields on more builds.
3. *Aim as precision, not damage:* aim steps widen crit range / ignore armor and do not add dice. This removes the volley stack but, with doubling intact, converts archers into crit fishers, so it depends on F2.
4. If the design intent is genuinely "no shield in the open means you die", say so in the rules text and make sure every class concept has a route to a shield or to cover-generation; then H-1 is unnecessary for ranged.

### F4. The shield's +2 dominates; defense is priced linearly for a good worth its square

**Problem.** Because full-block cost scales with (D/V)², the first points of Melee Defense are worth far more than the last. A shield gives +2 for nothing; Agility gives +1 per two points at triangular Expertise cost and is cut to every third or fourth point in medium or heavy armor; Finesse gives +1 per two points. At level 1 (5 Expertise) no build can reach the shield's +2 through attributes.

**Stakes.** P4 (build the character you imagine); EQ-1 intent "nimble, high-defense builds shine one-on-one"; §3.4 no auto-pick.

**Evidence.**
- Full-block cost for a 3-step attack (mean 22.5), armor 2: MD 4 → 12 stamina; MD 6 → 5. For 4 steps: 23 → 8.
- Sample fighter vs same stats with a two-handed longsword (1d10 instead of 1d8, no shield, MD 2): shield wins 73% (alpha/alpha), 74% (chip-kill), 86% (2-step). Vs greatsword (1d12 + 2×STR, MD 2): 77 / 78 / 84%.
- Heavy armor + shield (MD 4, armor 3) vs level-1 "duelist" (AGI 2, FIN 1, unarmored two-hander, MD 3): 79 / 88 / 87%. Level 30, heavy + shield (MD 5, armor 3) vs AGI 4 / FIN 3 duelist (MD 5, armor 0, 12.5/step): 63 / 64 / 78%. The duelist's extra damage does not compensate for armor 0 because armor's free grazes are what make low-commitment exchanges even.
- Level-30 STR 5 build with MD 4 loses 67% to the MD 6 sample at equal level: two points of defense outweigh +1 damage per step and +2 HP.

**Confidence.** High. **Scope.** Numbers mostly (the shield's +2, the attribute steps), with a shape component: any linear pricing of V will misprice it while block costs are triangular. If F1 is fixed by flattening the curves, this finding shrinks on its own.

**Options.**
1. Price the shield like an attribute step: +1 Melee / +2 Ranged, or +2 Melee with a Strength requirement like armor.
2. Let the AGI defense step count every point for Dodge/Ranged and every other point for Melee (so unarmored builds get *something* a shield-bearer does not), and let two-handed weapons grant +1 Melee Defense (a reach/leverage parry bonus) — your own p.731 draft had "+1 melee defense" properties that were dropped.
3. Whatever you do, publish the implied rule: "two points of Melee Defense are worth about one weapon size". Right now the table hides it.

### F5. Scaling: pools grow, HP and defense do not, so the full strike grows from "cripple" to "kill"

**Problem.** Max stamina grows +1 per 5 levels and recovery +1 per 10, so the affordable number of steps rises from 4 (L1) to 5 (L30) to 7 (L99), and damage per step rises with STR/FIN from 7.5 to 11.5. HP stays 6–12 and Melee Defense from attributes tops out at +3 (AGI) +3 (FIN), realistically 6–7. The full strike's damage therefore grows from ~30 to ~80 while the defender's ceiling (blocks affordable × V) grows from 32 to ~60. Recovery also rises as a fraction of the pool (29% → 37%), so there are more full strikes per fight at high level, not fewer.

**Stakes.** §3.5 "high-level characters should dominate low-level ones" is met, but high-level vs high-level becomes a coin flip on initiative; CR-3 intent "fights last a few rounds" (L99: median 1).

**Evidence.** Level 99 equal duel: median 1 round, first mover wins 83–87%, opening strike kills 69% from full. Level 30: first mover 64–67%, 9–10 rounds, but only because MD 6 makes k ≤ 3 futile (see F1). The STR +1 HP: at level 1 each point of Strength is +12% HP and +7% max stamina; at level 99 it is +8% HP and +3% stamina — its HP value barely decays, its stamina value does. The real decay is HP against damage per step (7.5 at L1 vs 8 HP; 11.5 at L99 vs 12 HP): one unblocked step incapacitates at every level, by design, but the number of steps per attack doubles. Your suspicion about Strength is right in direction and misattributed: it is HP-vs-steps that scales poorly, and STR just rides it.

**Confidence.** High on direction; the exact L99 numbers assume a 44-Expertise build (STR 6, AGI 6, FIN 1).

**Scope.** Shape (which quantities get the level bonus) more than numbers.

**Options.**
1. Grow recovery, not maximum: recovery is a per-turn flow, maximum is burst capacity, and burst is what breaks the quadratic. Keep max stamina near 6 + HP and put the level bonus into recovery (or into strain). Fewer steps per strike, more strikes per fight, same "dominate low levels" via attributes and recovery.
2. Let Melee Defense grow with level very slowly (+1 per 25 levels, say) so r holds; cheaper than retuning every attribute step.
3. Keep STR's +1 HP; it is the only thing giving sturdy concepts a body. Address the stamina coupling separately (F7).

### F6. Focus fire is unanswerable and NPC commitment is the hidden lethality dial

**Problem.** Blocks reset per attack, so three attackers at 2 steps each cost the defender ~5 + 5 + 5 stamina per round against 4 recovery; by round 2 the defender has nothing, and leaving costs stamina they do not have. The defender's own attack (5 stamina) makes it worse.

**Stakes.** "Positioning: back out when your defenses run low" presumes stamina to back out with. §3.2 telegraphing is unsolved; §3.5 balance across GM style; GM-1 (NPCs value survival) does not help the victim.

**Evidence.** Level 1, three sample fighters vs one: defender down 100%, median round 1 (full strikes), 1.5 (2-step attackers), 4 (1-step attackers); heavy armor 1.7. Defender kills 0.00–0.01 attackers per fight. One log: round 1 the defender blocks 9 → 19 (crit) → 14 damage for 2 + 11 + 5 stamina and is at 0; round 2 the first attack (22, two crits) is unblocked and lands for 44.

**Confidence.** High. This is also plausible fiction; the issue is not that 3v1 is deadly but that it is deadly in one round with no window, and that NPC step count decides it.

**Scope.** Design/GM-facing more than shape. **Options.** (1) Bring NPC aggression profiles (H-6) back as the *default* way monsters are written: a stat block says "commits 2 steps; 3 against a target below half stamina". Without it every GM is tuning lethality blind. (2) Give a defender one non-stamina answer to being swarmed: e.g. a free one-square retreat when attacked by a third enemy in a round, or let the perfect-block count reset only once per round per attacker rather than per attack when the attacks come from different enemies — this last one directly targets focus fire and leaves duels unchanged. (3) Make telegraphing mechanical: NPC stamina is public information (see F11: stamina visibility is unstated).

### F7. Max stamina = 6 + current HP is a death spiral at low level and makes fights lopsided

**Problem.** At level 1, HP is 57% of max stamina, so a 6-HP wound cuts the pool from 14 to 8 (−43%); the wounded character can no longer block a 3-step attack and cannot muster one. CR-2's intent is "injury should modestly lower performance without a combat death spiral" (p.1021). At level 30 the cut is 29%, at 99 it is 16%.

**Evidence.** Winner untouched 63–85% of level-1 duels; loser ends at −3 HP mean. Fights do not produce two bloodied survivors; they produce one unmarked winner and one dying loser, because the first real wound decides the rest. H-2 (damage also reducing max stamina) would deepen this at low levels unless the coupling is loosened first.

**Confidence.** High. **Scope.** Numbers. **Options.** 8 + HP/2 (rounded up) + level term; or 10 + HP − STR (so STR's HP does not double-dip); or keep 6 + HP but let armor or a shield add to max stamina as "effort you do not have to spend", which also softens F4 in the right direction.

### F8. Weapon table: heavy weapons are more stamina-efficient at *every* commitment; light weapons have no niche

**Problem.** EQ-2's intent is light-efficient-at-low-commitment, heavy-efficient-at-high. At the placeholder numbers (STR 2, FIN 1): damage per stamina at 1 step — dagger 3.5, shortsword 4.5, longsword 3.75, greatsword 3.83, greataxe 4.33; at 5 steps — 1.17, 1.50, 1.88, 2.30, 2.60. The greataxe beats the dagger at every k, and beats the longsword at k=1 too. Light weapons' only real assets are the OA cap (base 1), quick-draw and small-die crits. The 2× and 3× STR multipliers also mean STR 6 makes a greataxe step 25 damage — the attribute scale is human, the weapon formula is not.

**Stakes.** P3 (grounded scale, via multipliers); P4 (the dagger rogue is a crit-fishing build that depends on F2); §3.6 complexity (multipliers are a second thing to compute per step).

**Evidence.** Table 8 in Appendix A. Also: base costs are integers 1/2/3, so the efficiency ratio between weapon classes can only be tuned in coarse jumps.

**Confidence.** High. **Scope.** Numbers, with one shape note: with integer base costs the "efficient at low commitment" niche can only exist if light weapons get a *per-step* cost advantage that heavy weapons lose at high k — e.g. light weapons ignore the first point of surcharge (steps cost base, base, base+1…), heavy weapons pay surcharge from the first extra step. **Options.** (1) Replace multipliers with die upgrades (greataxe 2d6+STR+FIN, polearm 1d12+STR+FIN) and give STR weapons their efficiency through base cost instead. (2) Give light weapons the surcharge exemption above. (3) Cap the STR contribution per step at the weapon's die size, which keeps 25-damage steps off the table without a new rule type.

### F9. Opportunity attacks: avoidance dominates the cap; reach weapons cannot threaten

**Problem.** Avoiding an OA is a flat 1 per enemy per square. Blocking a dagger OA (3.5 dmg) at MD 4 / armor 2 costs 1 — a wash — but blocking a longsword OA (7.5) costs 2, and against MD 1–3 targets 3 or more. So whenever Finesse raises the cap enough to matter, the mover pays 1 to switch it off; the cap matters only against someone with no stamina, which after F1/F6 is "someone already losing". Separately, the default cap of 1 means any base-2 weapon (longsword, spear) with FIN 0 can never make an OA: a FIN-0 spearman threatens nothing, and an archer can shoot point-blank next to him for free. The packet's own positioning bullet "control space with reach" is false at the current cap.

**Stakes.** MV-5 intent ("exposure should be punishable… even without Finesse"); P3 (a spearman who cannot punish a man walking past him); R2:1 wording.

**Confidence.** High on the arithmetic; medium on how often tables will pay to avoid (it also depends on whether stamina is visible).

**Scope.** Mechanism (MV-3/MV-5 are Mechanism open). **Options.** (1) Cap = weapon base cost + odd FIN, so every proficient weapon gets one step and FIN buys extra steps or repeats; this restores reach. (2) Avoidance costs the attacker's cap rather than a flat 1 (pay what they could have spent), so investing in Finesse makes you more expensive to slip past — that gives the cap a purpose. (3) Keep both but make avoidance count toward the mover's off-turn escalation, so the third enemy slipped past costs 3, not 1.

### F10. Extra on-turn movement is too cheap to be plausible and makes range irrelevant

**Problem.** 1 stamina buys 1 + odd AGI squares, unlimited and flat. AGI 1 with 10 spare stamina covers 26 squares (130 ft) in a turn; AGI 5 covers 48 (240 ft). Off-turn movement, by contrast, escalates. The chase dynamic you wanted (chasers win) is delivered, but so is "range bands never matter" and "the archer scenario is settled on turn 1 or never".

**Stakes.** P3; RG-3 (range bands "should change how much you aim and whether you risk closing in" — closing is free).

**Confidence.** High. **Scope.** Numbers. **Options.** 1 stamina per square regardless of AGI (AGI improves free movement only); or cap purchased movement at your free movement per turn. Both keep chasers winning via the off-turn escalation on the fleeing side.

### F11. Decision and arithmetic load is highest in the block choice and in off-turn prompts (evaluation item 4)

**What a player does on a typical turn.** *Attacker:* choose target; estimate the defender's response to 1–4 steps (needs their defense, armor and stamina — is stamina visible? the rules never say); pay base + surcharge per step (a triangular sum); roll k dice; compare each die to the crit threshold; total k rolls plus k × flat bonus. *Defender:* read total and crit count; compute effective armor (armor − crit dice); search over (perfect, grazing) pairs for the least stamina that gets residual + leaks − armor to 0, then decide whether to accept 1–4 HP instead — knowing a crit doubles whatever is left. *Between turns, every player, after every turn:* "do I buy off-turn movement?", tracking a personal escalation counter that also includes any opportunity attack steps since their last turn; when moving, count threatened squares × enemies for avoidance payments. A five-combatant round therefore has 20–25 off-turn prompts and 5–10 two-variable block searches.

**Where the load is highest.** The block search with crits (two sub-cases, a doubling, a changing armor value) and the shared off-turn counter. The surcharge, the attack triangle and avoidance payments are fine — they are additive and the Quick Reference table carries them.

**Rules costing more attention than they return.** (a) Crit dice ignoring 1 armor each — a per-die comparison for a 1-point effect sitting next to a ×2; merge into one crit effect (F2). (b) Range-band aim exceptions ("first aim step adds only FIN") — rarely matter once F10 makes closing free; cut them or fold into a flat "medium: −1d6 from the shot". (c) The shared off-turn escalation across movement and OAs — defensible, but it needs a physical token (the design notes already contemplate tokens; this is where they earn their keep). (d) Strain overage counted after adding the ability's own strain — a known gotcha; the example is correct now, but the Fighter core (0 stamina) means overage produces a stamina cost from nothing, which players will find odd.

**Stakes.** C1. **Confidence.** Medium (table time is a playtest measurement). **Scope.** Presentation plus the F2 shape.

### F12. The level-1 Expertise budget contradicts the attribute scale's own words

**Problem.** Five Expertise buys 2/1/1/0/0/0 or 2/2/0/0/0/0. The scale says 0 is "clearly deficient", 1 "functional but below average", 2 "an average person (not an average adventurer)". So every starting adventurer is below the average person in at least three attributes and average in at most two. A "big, strong" concept gets STR 2 — "an average person". This is a P4 problem in the fiction and a presentation problem in the text.

**Scope.** Numbers (budget or scale text). **Options.** Start attributes at 1 (so 0 is a deliberate dump, as §3.4 wants); or 8–10 starting Expertise; or re-anchor the scale so 1 is average.

### F13. Where the core makes the known gaps hard to fill

- **Mental attributes.** The economy sits on a knife edge (13 vs 14 stamina against a full strike is life or death; +1 defense is worth 20–40% of block costs). Anything a mental stat does that touches stamina flow, defense value or initiative becomes mandatory; anything that does not gets dumped. The hooks that remain (information — e.g. Cunning sees enemy stamina or forces the defender to declare blocks first; off-turn escalation discounts; strain capacity for Will) are all either very strong or very weak at these numbers. Fix F1 first; a less convex economy makes small, flavourful benefits price-able.
- **Monsters.** Any attack whose damage per step exceeds ~2× a PC's defense is unblockable (Table 1: MD 4 vs 20 per step needs 5 blocks per step). "Big hits" cannot exist for named-character targets; monsters must be written as many small attacks or as pressure (stamina) rather than wounds. That is a strong, possibly welcome, constraint — but it means monster design depends on F1's resolution and on H-6 profiles.
- **Control effects.** "Progressive and resistible with stamina" draws on the pool that F6 shows is empty exactly when a target is being focused. Resisting will be a fiction unless control costs are small or paid from a different track (strain, or the off-turn escalation).
- **Casters.** No armor, no shield → RD 1, MD 1–2. From Table 5 a caster in the open is downed by a single aimed shortbow shot 72% of the time. Their survival must come entirely from spells, which contradicts "core rules interesting without abilities" and makes "magic may be cut" cleaner than "magic stays": if magic stays, casters need a core-rules defense (F3 option 1 gives them Dodge-as-RD).
- **Class cores (as written, placeholders).** They show the leverage points: the Monk core (1 strain: blocks do not escalate) saves 28 stamina against a level-1 full strike — it is the only thing in the packet that answers F1 — and the Barbarian core refunds up to 5 stamina for 1 strain while the Fighter's refunds 4 for 3. Price cores against block savings, not against each other.

### F14. Interactions, ambiguities and exploitable timing (evaluation item 6)

- **Simultaneous off-turn movement.** After a turn ends, several creatures may buy movement; the rules give no order. Order matters for OAs and for who ends adjacent to whom. Suggest: in initiative order, lowest first, so faster creatures react last.
- **Stamina visibility.** Never stated. The commitment decision and the OA/avoidance choice both hinge on whether the attacker knows the defender's stamina. Decide (recommend: public, like HP) and say so.
- **Aim dice and crits.** TODO. The sim assumes they can; if they cannot, ranged crit rates drop from ~70% to 25% on a 2-aim longbow shot, which is a large swing and worth deciding before any ranged tuning.
- **Doubling once per attack** — TODO; the sim assumes once. Confirm.
- **Diving to half cover** — the rule covers only "fully behind cover → three-quarters"; say what partial cover gives.
- **Dive out of a point-blank shooter's reach** — provokes under the leaving-a-threatened-square trigger; and the point-blank OA cannot be avoided by payment, so the archer and the diver are both provoking in the same exchange. Clarify order.
- **"Attack again" as probing.** Two 1-step attacks cost the same as one 2-step attack (2+3 either way) but the defender blocks each with a fresh count; the attacker gets information between them. Intended (p.490) and fine — but note it flips against unarmored targets, where two 7.5s cost 6 to block and one 15 costs 10, so probing is strictly worse there and strictly better nowhere; nobody will probe.
- **Rogue core and the next round.** A Rogue who delays "takes it after a later turn"; nothing says where their turn sits next round or whether their end-of-turn recovery moved with them.
- **Barbarian core "at any time on your turn"** refunds the largest step cost; after a 4-step attack that is 5, more than a Fighter's whole recovery. It also makes the surcharge partly refundable, which interacts with F1.
- **Initiative ties** on 2d12 are ~6% per pair; with six combatants (15 pairs) a tie is more likely than not in every fight. "No tiebreaker for now" will bite at the first table.
- **Off-turn movement after your own turn** happens after recovery, so the fresh pool pays for it; combined with free on-turn movement this means a character can act, recover, then move 1–4 squares — fine, but it is the only time the escalation starts from a full pool, and players will learn that the cheap retreat is right after their own turn.
- **Max stamina at negative HP** — the formula uses "current HP"; say that it floors at 0 (the character is incapacitated anyway, but the arithmetic should close).
- **Avoiding OAs while out of stamina** — a character at 0 stamina cannot pay 1 to avoid and cannot block; retreat is impossible, which is the F6 trap. Consider letting avoidance be paid from the next recovery (a debt) as the one exception.

---

## What is working well and should be protected

- **One pool, everything on it.** Every situation the sim ran turned on stamina, and the economy never needed a second currency to explain an outcome. P1 is delivered.
- **Offense before defense, deterministic blocks.** The defender always decides with full information (total, crit count), and the packet's worked examples are internally consistent — every one of them reproduced in the simulator to the point.
- **Grazing blocks and armor as the counterweight.** At one and two steps the exchange is almost exactly even (2 vs 2, 5 vs 5 at level 1), which is precisely the parity the design target asks for. This is the part of the curve the whole game should live on; the fixes above are about making more of the commitment range look like this.
- **End-of-turn recovery.** The safety net works (nobody in thousands of fights faced a turn at zero after their own spending), it rewards going early as intended, and passivity is punished: holding a reserve loses.
- **Off-turn movement and diving for cover.** Positioning is live and cover is the single most powerful decision in the ranged game — a 3/4 dive turns a lethal volley into 1–6 stamina. That is the right kind of agency; the problem is only that it is the *only* ranged agency.
- **Status markers, intent lines and the ledger.** Being able to tell what is deliberate made this review possible; keep the discipline.
- **System Shock.** The 2d12 + STR walk drifts toward stabilizing below ~4 Shock and toward death above ~6; the window is real and the example math is right.
- **Separate currencies for arenas of play** (P4's mechanism) — clean, and the Skill-Point attribute bonus is a good answer to "smart but not in combat".

---

## Challenges to core commitments

**"HP is small and doesn't grow; there's no HP-restoring magic", justified by "lasting harm is fair because damage is avoidable".** The justification does not hold at these numbers: in the equal duel, the 3v1 and the open-field ranged case, damage is not avoidable by any decision. Until F1–F3 are fixed, slow healing is punishing players for fights they could not have played differently — the exact thing the project brief rules out. The commitment itself is fine; its precondition is not yet met. A related campaign-pacing consequence: the loser of a typical fight ends at −3 HP and needs 9–11 nights to be whole, and the winner is wounded 15–40% of the time; expect convalescence to dominate downtime, and expect H-2/H-3 to come back as a consequence.

**"Stamina is your defense; one regenerating pool pays for nearly everything."** Perfect fungibility between offense and defense is what makes the first strike unanswerable: whoever spends first on offense forces the other to spend on defense from the same pool, and the pool that blocks is the pool that would strike back. This is not a reason to abandon the commitment; it is a reason the commitment *requires* that attack and defense draw down the pool at the same rate per unit of threat (F1). If you keep one pool, the two cost curves must be the same order. If you ever find you cannot make them so, the alternative is a small defensive float that cannot be spent on attacks (e.g. a shield's or armor's stamina), which is a partial retreat from the commitment.

**"Nothing on the attribute scale is superhuman."** True of the table, leaked by the weapon formulas: 2× and 3× STR on heavy weapons and stacked aim dice produce per-step numbers (25+) that no human-scale defender can answer. Either the multipliers go (F8) or the commitment should be restated as "attributes are human-scale; outputs may not be".

**"No to-hit roll; blocking is deterministic."** Works, and nothing here argues against it. One honest observation: removing the to-hit roll did not remove luck, it moved all of it into the damage dice and the crit check, where the defender sees it but cannot answer it. The commitment is sound; the crit doubling is where the moved luck landed (F2).

---

## Wording and presentation issues

1. **Positioning intro: "control space with reach."** False at the default OA cap (base-2 reach weapons cannot make OAs without Finesse). Either change the rule (F9) or the sentence.
2. **Critical Hits: "It comes from skill, not luck."** At FIN 0, 8–25% of dice crit and 29–68% of multi-die attacks do; soften to "skill widens it" or fix F2.
3. **"Attack vs. defense efficiency (Locked, as a design target)"**: the packet states the target but not the measurement. Add the one-line test: "at k steps, the stamina to fully block the mean roll should be within ±1 of the attack's cost for k ≤ 3" — it would have caught F1.
4. **Longsword row:** "One-handed: 1d8 + STR + FIN (STR replaces AGI)" is confusing because the two-handed form already allows STR. Say "one-handed: 1d8 + STR + FIN; STR only".
5. **Stamina visibility, simultaneous off-turn order, aim crits, doubling-once, dive to half cover** — all unstated (F14); each is a one-line fix.
6. **"Maximum Stamina = 6 + current HP"** — state the floor at negative HP.
7. **Aim: "The count carries across shots; it doesn't restart."** Also carries across melee steps in the same turn (they are all "actions"); say so, since bow-then-dagger turns will happen.
8. **Sample character** lists "Dodge Defense 1" but AGI 1 gives no even value — correct, but a reader will check; add "(AGI 1: no even step)".
9. **Opportunity attack "Optional rule":** the per-square cap is ambiguous between "one OA with cap 3" and "three OAs with cap 1 each"; the example implies the former. Say which.
10. **Drawing Weapons:** "Used hands … can't draw a normal weapon until the start of your next turn" interacts with "Between turns: drawing a normal weapon costs 1 stamina" — the second sentence can never apply to a used hand; order the two rules so that is obvious.
11. **Range bands** describe "your first aim step adds only Finesse" but the Aim example's medium-range case is absent; one worked example would prevent misreads.
12. **"Action"** — your note already covers the naming problem. For what it is worth, "beat" tested best in this review's own notes because "third beat costs base + 2" reads naturally and does not collide.
13. **Quick Reference → Stamina Costs** omits the OA *avoidance* line's interaction (not an off-turn cost) — it is in the prose; the table should repeat "does not escalate".
14. **Design notes §7** already flags "most attacks are dangerous" vs "pressure"; the numbers here agree with the nuance: at k ≤ 2 against armor, attacks are threats you must answer, not dangers.

---

## Appendix A — Simulation setup and results

**Model.** Python implementation of v0.9 as written: HP 6 + STR; max stamina 6 + current HP + round(L/5), current clamped when max falls; recovery 4 + round(L/10) at end of own turn; melee steps cost base + actions already taken; blocks subtract the defense value, perfect blocks 1,2,3… within an attack, grazes 1 flat with 1 leak; armor soaks residual + leaks; each crit die ignores 1 armor; any crit doubles what remains; crit range = die max widened by odd FIN (max +3); initiative 2d12 + odd AGI + odd CUN; melee defense = 1 + 1 (proficient melee weapon) + 2 shield + even AGI (every 2nd/3rd/4th point by armor) + even FIN; ranged defense 1 + 2 shield (+ cover). Verified against every worked example in the packet (Choosing Blocks: 1 perfect + 1 graze = 2 stamina, 0 injury; Melee Attack example: all four listed block lines; Strain example 9).

**Assumptions where the packet is TODO or silent.** Aim dice can crit (Table 5 and the archer scenario are *less* lethal if not — 25% rather than ~70% crit on a 2-aim shot). Doubling happens once per attack. Stamina is observable (attack policies use it). No abilities, no strain spending, no retreat or surrender — fights run to incapacitation (so "rounds" is an upper bound on how long a decision-rich fight lasts). Defender policy: choose the (perfect, grazing) pair minimizing injury × w + stamina, never choosing incapacitation when avoidable; w = 3 stamina per HP by default, checked at 1.5 and 6 (results in the text change by ≤3 points). Attacker policies: *alpha* (all affordable steps), *fixed k*, *reserve 5*, *chip-kill* (2 steps unless the full strike is expected to take half the target's HP or kill ≥50%), and a 1-ply look-ahead; the matrix in Table 2 is how "dominant strategy" was tested. Builds: L1 sample fighter as in the packet; L30 (16 Expertise) STR 3 AGI 3 FIN 2 CUN 1, medium + shield → HP 9, stamina 21, +7, MD 6; L30 STR 5 FIN 1 heavy + shield → MD 4, armor 3, HP 11; L30 duelist AGI 4 FIN 3, unarmored two-hander → MD 5, armor 0, HP 6, 12.5/step; L99 (44 Expertise) STR 6 AGI 6 FIN 1 → HP 12, stamina 38, +14, MD 6. Archer: STR 1 AGI 1 FIN 2, light armor, longbow, quick-drawn shortsword for melee defense (MD 3). 1v3 attackers are sample fighters; the defender attacks the lowest-stamina attacker with 2 steps when it can afford to. Each duel cell: 600–2000 trials; static tables 4000–20000 rolls.

**Table 1 — Stamina to fully block a longsword attack at its mean roll (no crit) vs attack cost.**

| Defender | k=1 (att 2) | k=2 (att 5) | k=3 (att 9) | k=4 (att 14) | k=5 (att 20) |
|---|---|---|---|---|---|
| MD 2, armor 0 | 10 | 36 | 66 | 120 | 190 |
| MD 2, armor 2 | 5 | 22 | 47 | 93 | 155 |
| MD 3, armor 2 | 3 | 8 | 22 | 38 | 68 |
| **MD 4, armor 2 (sample)** | **2** | **5** | **12** | **23** | **38** |
| MD 4, armor 3 | 2 | 4 | 9 | 18 | 31 |
| MD 5, armor 2 | 2 | 3 | 8 | 12 | 23 |
| MD 6, armor 2 (L30 sample, 9.5/step) | 2 | 4 | 8 | 17 | 23 |
| MD 6, armor 2 (L99, 11.5/step) | 2 | 5 | 12 | 23 | 38 → k7: 80 |

**Table 2 — Level-1 equal duel, strategy matrix (A win % / draw % / mean rounds; 600 trials per cell).**

| A \ B | alpha | k3 | k2 | k1 | reserve5 | chip-kill |
|---|---|---|---|---|---|---|
| alpha | 49/1/6.3 | 47/1/6.9 | 54/2/7.5 | 77/23/13.6 | 77/3/8.6 | 52/2/6.6 |
| k3 | 53/2/6.8 | 50/2/7.4 | 54/3/8.3 | 74/26/13.4 | 79/2/8.5 | 55/2/6.8 |
| k2 | 45/2/7.1 | 42/1/7.9 | 51/2/9.2 | 74/26/14.7 | 73/4/10.6 | 50/2/7.4 |
| k1 | 0/20/12.6 | 0/21/12.1 | 0/24/13.7 | 0/100/30 | 0/51/21.9 | 0/25/13.2 |
| reserve5 | 22/2/8.3 | 18/4/9.2 | 22/4/10.6 | 54/46/21 | 50/4/11.3 | 22/3/9.1 |
| chip-kill | 50/1/6.8 | 48/2/7.3 | 50/2/7.5 | 78/22/13.2 | 76/4/9.2 | 55/2/6.4 |

Reading: no sensible policy beats another by more than ~5 points; holding a reserve and pure chip are dominated. The fight is decided elsewhere (initiative, opening roll).

**Table 3 — Equal duels by level.**

| Level / policy | Winner | Rounds (median / mean) | First mover wins | Loser ends at | Winner untouched |
|---|---|---|---|---|---|
| L1 alpha v alpha | — | 4 / 6.5 | 69% | −3 HP | 63% (chip-kill) |
| L1 k2 v k2 | — | 6 / 8.7 | 65% | −4 HP | 85% |
| L1 chip-kill | — | 4 / 6.3 | 69–72% | −3 HP | 63% |
| L30 alpha v alpha | 6% draws | 9 / 11.5 | 64% | −3 HP | 59% |
| L30 k2 v k2 | **75–77% draws** | 30 / 28 | 55% | — | — |
| L30 STR-brute (MD 4) v sample (MD 6) | MD 6 wins 67% | 2 / 3.4 | 77% | | |
| L99 alpha v alpha | — | 1 / 1.6 | 83% | | |

Opening full strike vs identical defender at full: L1 4 steps/14 st → mean 6.1 HP, down 34%; L30 5 steps/20 st → 5.3 of 9 HP, down 9%; L99 7 steps/35 st → 14.0 of 12 HP, down 69%. Conditioned (L1): crit & roll ≥30 (48% of strikes) → first mover wins 94%, 70% decided within 2 rounds; no crit & roll <30 (26%) → first mover wins 26%.

**Table 4 — One defender vs three (level 1).**

| Defender | Attackers | Defender down | Rounds to down (mean / median) |
|---|---|---|---|
| sample | 2-step each | 100% | 1.5 / 1 |
| sample | 1-step each | 100% | 4.0 / 4 |
| sample | chip-kill | 100% | 1.0 / 1 |
| sample, never attacks | 2-step each | 100% | 1.6 / 2 |
| heavy armor + shield | 2-step each | 100% | 1.7 / 2 |

Attackers downed per fight: 0.00–0.01.

**Table 5 — Ranged, level 1 (archer FIN 2, STR 1; aim 1d6+2; aim dice can crit). Target spends / takes / downed.**

| Shot | Unarmored, no shield (6 HP) | Light armor, no shield (7 HP) | Shield + medium (8 HP) | Shield + medium + 3/4 cover |
|---|---|---|---|---|
| Shortbow, 0 aim (3 st) | 5.3 / 4.0 / 33% | 5.3 / 3.3 / 17% | 2.0 / 0 / 0% | 1.0 / 0 / 0% |
| Shortbow, 1 aim (4 st) | 8.0 / 12.4 / 72% | 7.6 / 12.1 / 59% | 6.2 / 0.3 / 0% | 1.8 / 0 / 0% |
| Shortbow, 2 aim (6 st) | 7.9 / 22.7 / 100% | 8.1 / 22.3 / 95% | 10.5 / 2.3 / 5% | 3.3 / 0 / 0% |
| Shortbow, 3 aim (9 st) | — / — / 100% | — / — / 100% | 12.2 / 6.2 / 41% | 5.4 / 0 / 0% |
| Longbow, 0 aim (5 st) | 6.0 / 6.2 / 25% | 4.7 / 5.8 / 25% | 3.2 / 0 / 0% | 1.3 / 0 / 0% |
| Longbow, 1 aim (6 st) | 7.1 / 15.3 / 88% | 7.3 / 14.9 / 73% | 7.7 / 0.6 / 0% | 2.2 / 0 / 0% |
| Longbow, 2 aim (8 st) | — / — / 100% | — / — / 99% | 11.0 / 3.4 / 16% | 3.8 / 0 / 0% |
| Longbow, 3 aim (11 st) | — / — / 100% | — / — / 100% | 12.3 / 7.7 / 50% | 6.1 / 0 / 0% |

**Table 6 — Archer vs approaching fighter (12 squares, medium range; 3000 trials each).** Open field, 3 aims: fighter 76%, archer 24%, 2.4 rounds, fighter ends at 4.5/8 HP. 2 aims: 81/19. 0 aims: fighter 100%, no damage. Fighter has cover: fighter 100%, no damage. Archer stands and fires rather than kiting: 75/25 (kiting changes nothing).

**Table 7 — Armored vs unarmored (win % for the armored side: alpha / chip-kill / 2-step).** L1 heavy+shield v duelist: 79 / 88 / 87. L1 sample v duelist: 80 / 86 / 85. L1 sample v same-stats two-hander: 73 / 74 / 86. L1 sample v greatsword: 77 / 78 / 84. L30 heavy+shield (MD 5, armor 3) v duelist (MD 5, armor 0): 63 / 64 / 78. L30 sample (MD 6) v duelist: 70 / 70 / 82.

**Table 8 — Damage per stamina by commitment (STR 2, FIN 1, AGI 1).**

| Weapon | k=1 | k=2 | k=3 | k=4 | k=5 |
|---|---|---|---|---|---|
| Dagger 1d4+1 (base 1) | 3.50 | 2.33 | 1.75 | 1.40 | 1.17 |
| Shortsword 1d6+1 (1) | 4.50 | 3.00 | 2.25 | 1.80 | 1.50 |
| Longsword 1H 1d8+3 (2) | 3.75 | 3.00 | 2.50 | 2.14 | 1.88 |
| Longsword 2H 1d10+3 (2) | 4.25 | 3.40 | 2.83 | 2.43 | 2.12 |
| Greatsword 1d12+5 (3) | 3.83 | 3.29 | 2.88 | 2.56 | 2.30 |
| Greataxe 2d6+6 (3) | 4.33 | 3.71 | 3.25 | 2.89 | 2.60 |

**Table 9 — Candidate shape changes (evidence only, not proposals). Opening full strike vs identical at full → mean injury / down; equal-duel first-mover edge and draw rate.**

| Variant | L1 strike | L30 strike | L99 strike | L1 duel (first mover / draws) | L30 duel (draws) |
|---|---|---|---|---|---|
| Baseline v0.9 | 6.1 / 34% | 5.3 / 9% | 14.0 / 69% | 69% / 1% | 6% (alpha), 75% (k2) |
| A: surcharge +2 per prior action | 2.3 / 6% | 2.2 / 0% | 6.6 / 0% | 61% / 17%; 13 rounds | 68–86% |
| B: blocks escalate every 2nd block | 2.8 / 18% | 0.9 / 0% | 6.4 / 5% | 67% / 24%; 13 rounds | 94–100% |
| A + B | 0.4 / 0% | 0.0 / 0% | 0.4 / 0% | 45% / 63% | 100% |
| C: +2 MD for everyone | 1.6 / 0% | 1.5 / 0% | 7.8 / 0% | (k4 is defender-favored at L1) | — |
| D: no crit doubling | 3.8 / 1% | 4.5 / 0% | 10.0 / 0% | 55% / 9%; 13 rounds | — |

Reading: every single-knob change that fixes lethality at level 1 produces stalemate at level 30, because the ratio r = damage per step ÷ defense value moves between levels. The fix has to pin r (F1, option 2) and then choose the curve shape.

## Appendix B — Goal-by-goal scorecard

| Goal / pillar | Delivered? | Works against it |
|---|---|---|
| Stamina *is* the fight (P1) | Yes | — |
| Danger you can see and answer (P2) | At k ≤ 2 in melee; with shield + cover at range | Full strike (F1), crit doubling (F2), arrows vs no shield (F3), focus fire (F6) |
| Plausible in the fiction (P3) | Mostly | 130–240 ft turns (F10); spearmen who cannot punish (F9); 25-damage steps (F8) |
| Build the character you imagine (P4) | Currencies yes | Shield near-mandatory, two-handers/archers/casters structurally fragile (F3, F4); L1 budget vs scale text (F12) |
| Complexity budget (C1) | Attack side yes | Block search with crits; N² off-turn prompts; shared counter (F11) |
| Not swingy; deaths earned | No at the extremes | Initiative + opening roll decide equal duels (F1, F2) |
| Punish mistakes with tempo, not death (§3.1) | At k ≤ 2 | Victim of a full strike made no mistake |
| Attack somewhat more efficient than perfect blocking (§3.1) | Over-delivered | 2–2.6× vs perfect blocks; parity only via grazes + armor at k ≤ 2 |
| Positioning live all round | Yes | Movement so cheap that range is irrelevant (F10) |
| Balance resilient to GM style (§3.5) | No | NPC commitment and map cover are the two biggest lethality inputs (F3, F6) |
| Grounded power scale | Attributes yes | Weapon multipliers, aim stacking (F8) |
| Lighter outside combat | Yes | — |

## Appendix C — Severity and scope at a glance

| # | Finding | Severity | Scope | Needs playtest? |
|---|---|---|---|---|
| F1 | Different-order cost curves; commitment at the extremes | Critical | Shape | To calibrate, not to confirm |
| F2 | Crit doubling as luck multiplier | Critical | Shape (Locked) | No |
| F3 | Ranged defense / unshielded; H-1 evaluation | High | Shape + numbers | Partly (archer play) |
| F4 | Shield dominance, defense pricing | High | Numbers (+shape) | No |
| F5 | Level scaling of pools vs HP/defense | High | Shape | No |
| F6 | Focus fire; GM as lethality dial | High | Design/GM | Yes (NPC behavior) |
| F7 | HP→max-stamina death spiral | Medium | Numbers | No |
| F8 | Weapon efficiency, multipliers | Medium | Numbers | No |
| F9 | OA avoidance vs cap; reach | Medium | Mechanism | Partly |
| F10 | Extra movement too cheap | Medium | Numbers | No |
| F11 | Decision/arithmetic load | Medium | Presentation | Yes |
| F12 | L1 budget vs attribute scale | Low | Numbers/text | No |
| F13 | Gaps the core makes hard | Advisory | — | — |
| F14 | Edge cases | Low–Medium | Text | No |

## Addendum — configuration test after the review (same simulator)

Question asked afterwards: is F1/F2 tweakable, or structural? A grid over block-escalation slope (1,2,3… vs 1,1,2,2,3,3…), surcharge slope (+1 vs +2 per prior action), crit effect (×2 after armor; +2 per crit die after armor; +1 per crit die; none) and Melee Defense (L1: 4, 5; L30: 5, 6, 7), longsword mirror-match duels at levels 1 and 30. Targets: full strike from full ≤ ~3–5 HP and <10% down; first-mover edge ≤ ~60%; no stalemates; 4–10 round duels.

| Configuration | L1 full strike (HP, down) | L1 duel (rounds, first-mover, draws) | L30 full strike | L30 duel |
|---|---|---|---|---|
| v0.9 as written (MD 4 / MD 6) | 6.1, 35% | 3–4, 69%, 0% | 5.2, 8% | 9–11, 67%, 10% |
| Crit → +1 per crit die (nothing else changed) | 4.7, 16% | 7, 59%, 0% | 5.6, 2% | 7, 54%, 0% |
| Crit → none | 3.8, 1% | 13, 59%, 12% | 4.5, 0% | 30, 51%, **49%** |
| Surcharge +2 per prior action, crit ×2 | 2.3, 6% | 12, 64%, 18% | 2.2, 0% | 30, 57%, **83%** |
| **Surcharge +2, crit → +2 per crit die** | **3.2, 6%** | **7, 55–64%, 0%** | **4.6, 5%** (MD 6) / 5.6, 7% (MD 5) | **5–7, 54–57%, 0%** / 4, 46% |
| Surcharge +2, crit → +1 per crit die | 2.6, 0% | 11, 54–61%, 3% | 3.7, 0% | 11–15, 56%, 0% |
| Block slope ½, crit ×2 | 2.8, 17% | 15–17, 64–70%, 27% | 0.9, 0% | 30, 65%, **96%** |
| Block slope ½, crit → +2 per crit die | 3.4, 18% | 6–7, 63–68%, 0% | 4.0, 4% | 5–7, 60%, 0% |

Reading. (1) Every flat change that fixes level 1 on its own breaks level 30 (stalemate) or vice versa, because r = damage per step ÷ defense drifts between levels and both triangular curves amplify r². Numbers alone cannot do it. (2) With no crit effect at all, mean-roll parity means nothing ever lands: some per-attack leak is required, which is what the crit rule is actually doing in v0.9 — so the fix is to make the leak *bounded and linear*, not to remove it. (3) Two shallow, already-open knobs together — surcharge +2 per prior action (the soft version of "limit steps per attack"; it scales into bigger pools where a hard cap would not) and crit = +2 per crit die after armor (armor-ignore per die kept) — land inside the target band at both levels with the block escalation, HP, defense and damage tables untouched: full strike from full 3–5 HP and ≤7% down, 4–7 round duels, winners typically bloodied 2–4 HP, no stalemates, first-mover edge 55–64% (the residue of end-of-turn recovery rewarding going early, which is intended). (4) What stays structural is a discipline rather than a redesign: r is the master parameter and the system amplifies it quadratically, so the target band for r (≈1.5–1.9 at these costs) must be written down and every new weapon, attribute step or armor entry checked against it; MD 5 vs 6 at level 30 still moves duels from 4 rounds / 46% to 7 rounds / 57%. Untested under the new configuration: heavy and light weapons, 1v3, ranged, abilities. F3 (ranged defense), F4 (shield pricing), F7 and F10 are unaffected by these two changes.

## Addendum 2 — 1v1 vs XvX, retreat economics, guard-rule test

**Retreat cannot buy tempo on open ground (deterministic).** Fleer starts adjacent; chaser has free movement 6 (AGI 1) and buys 2 squares per flat stamina. To be out of the chaser's free reach the fleer needs distance 8: AGI 1 → 4 off-turn purchases (1+2+3+4 = 10 stamina, +1 to avoid the OA); AGI 3 → 3 purchases (6, +1); AGI 5 → 2 purchases (3, +1). The chaser then pays 1. Exchange rate 4:1 to 11:1 against the fleer. This is the intended "chasers win" rule (MV-1), but it means "save stamina to fall back" is not a counterweight to alpha striking on open ground; retreat only pays to break contact entirely or to reach terrain/allies.

**Strategy matrix with and without a guard rule (L1 mirror, 400 duels per cell, A-win% / draw%).** Guard: if you took at most G actions on your turn, until your next turn your perfect blocks cost 0,1,2,… instead of 1,2,3,… ("shift") or your Melee Defense is +1 ("md1").

| Engine | Guard rule | Result |
|---|---|---|
| v0.9 | none | alpha/k3/k2/chip-kill all 43–56% vs each other; 1-step play 0% |
| v0.9 | shift, G ≤ 1 | 1-step guard still 0% wins but 60–80% draws; 10–20% draws everywhere |
| v0.9 | shift or md1, G ≤ 2 | flat 35–50% with 15–45% draws (turtles) |
| candidate (+2 surcharge, +2/crit die) | none | flat 48–56% everywhere; 1-step play 29–36%; 0 draws |
| candidate | shift or md1, G ≤ 2 | flat 46–57% **including** the 2-steps-then-guard policy; 0 draws |

Reading: the candidate engine is fair but strategically empty in a symmetric open-ground duel (no policy beats another, and a state-aware policy gains nothing with public stamina). A guard rule makes holding back viable only on top of the candidate engine, and does not by itself create a rock-paper-scissors structure. The core economy's job is to be flat; duel interest must come from asymmetries (position with teeth, information, builds, abilities such as Riposte/Feint/Press that counter specific commitment levels). XvX supplies asymmetries by itself; 1v1 does not.

**Surcharge +2 alone vs with linear crits (from the grid).** v0.9 → +2 surcharge (crit ×2 kept): L1 full strike 6.1 HP/35% down → 2.3 HP/6%; max steps 4 → 3 (12 stamina); att/def by k 2/2, 6/5, 12/12; first-mover 69% → 57–64%; duels 4 → 12 rounds median with 14–18% draws; L30 MD 6: 71–83% draws. Adding +2 per crit die: L1 3.2 HP/6%, 7 rounds, 55–64%, 0 draws; L30 MD 5–6: 4.6–5.6 HP/5–7%, 4–7 rounds, 46–57%, 0 draws. Side effects of the +2 surcharge: aimed volleys cost more (longbow +2 aims 8 → 9, +3 aims 11 → 14), "attack again" is pricier, the Barbarian refund grows (largest step 6 instead of 5).

**Not tested:** off-turn movement in XvX (the simulator has no grid). The 1v3 runs were all-adjacent with no movement; the archer scenario used a 1-D distance with a crude kite, which failed for the exchange-rate reason above; diving for cover was tested statically only.
