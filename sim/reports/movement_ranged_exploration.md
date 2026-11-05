# Movement, second pass: where the flatness comes from, and what a shooter changes

Design chat, 2026-11-04 (second round). Engine `exp/movement` at b1d826c plus the changes in §7 (patch attached). Fight rows are 300 trials with 95% Wilson intervals in the raw results (`reports/movement_ranged_results/*.jsonl`); intervals are quoted in the text wherever a difference is claimed. Agents only; the agent each number depends on is named. Companion: `movement_ranged_exploration_notes.md`.

Baseline stamp: `RuleSet v0.9 3bf6fc070dbf; Code git b1d826c (uncommitted changes)`. Variant digests: capped at Movement `f7fd70927981`, one square flat `ef5c0f656642`, one square escalating `db6edbbd9a74`, extra movement as an action `6c640468b694`, none `8da823bc5604`.

## 0. The question, and the short answer

The designer asked whether movement's flatness is inherent to the mechanics, a matter of the numbers, or something that content elsewhere (ranged, AoE, abilities) is supposed to fix; whether a fast character can kite slow, powerful enemies; and what ranged combat does on top of movement.

Short answer: there are three different things being called "flat", and they have three different causes.

1. **The chase is flat because of a number**: purchased movement is uncapped at 1 stamina per purchase, so any creature can turn its whole pool into distance. A 3-square speed edge is worth about 1 stamina a turn to the pursuer, which it always has. An Agility 5 kiter with a 16-square head start against two Agility 0 brutes wins 6% of fights under v0.9 and 42–61% under any rule that stops the all-in dash (cap, one-square purchases, none). This is the designer's deliberate "melee must be able to catch retreating archers" choice (ledger MV-1, p.1706) doing exactly what it was meant to, and also catching everyone else.
2. **The approach is less flat than it looks, and the part that is flat is the exchange's, not movement's.** The first mover's edge in a duel is 67–71% whenever the close is free, *including when the two start adjacent*: it is the first-strike edge of the exchange, measured in the review's all-adjacent duels (69–71%). Each stamina the close costs takes about 6 points off it: 61% at one purchase, 53% at two, 49% at three, 45% at four. v0.9 therefore already prices distance; the price is simply 0 for the first seven squares and 1 per two squares after, so on a 12×12 map almost every start is in the free band. Steeper rules move the edge to even by 9–11 squares apart, and past the point where the close cannot be bought they hand the fight to distance parity (whoever ends inside the other's free reach loses the first strike: 27–30% vs 73% by starting distance under "none").
3. **Square value in melee is flat because the exchange is position-blind, by design.** No facing, no flanking, no elevation, OAs capped at 1 and avoidance flat at 1 ("no facing rules", "without making the battlefield sticky", both stated). The only positional inputs to a melee exchange are the attacker count and the arrival budget. That is a mechanics choice that keeps load down, and it means square value has to come from elsewhere: shooters, cover, chokepoints, zones. A longbow at short range is already the steepest gradient in the game (an unshielded target loses 7–12 stamina and 11–18 HP per 6-stamina shot), and cover is the steepest counter (+2/+5 on a defense of 1). Those gradients are invisible in the fights measured so far only because the approach erases them in one turn.

So: the chase is a numbers problem with a one-line fix available (cap purchased movement at your Movement); the approach has a dial whose slope is now measured, and the designer should pick where typical encounter distances sit on it; and square value is a content-plus-two-pending-rules problem (ranged lethality, F3; diagonal corners, `grid.corners`), not a movement-rules problem. The sections below show the measurements behind each sentence and evaluate the options against the pillars.

## 1. What makes a square worth something

A square's value to a creature is the sum of what can happen to it there before its next turn and what it can do from there. Under v0.9, per square of distance:

| Term | Gradient under v0.9 | Why |
|---|---|---|
| Melee threat: who can attack me here next turn | 0 inside the threat radius, which is the whole map | Free movement 5–8 plus 1 stamina per 1–4 squares: an Agility 1 creature reaches 7 squares for nothing, 13 for 3 stamina, 23 for 8 (table in the notes). On open ground every melee enemy threatens every square. |
| Engager count: how many can attack me here | 0 on open ground; 1→3 at a wall or corridor | The block count resets per attack, so being engaged by three is three duels at once. Only walls change the count (first report, §4). |
| My approach: what reaching a target from here costs | 0 for 7 squares, then ≈ 0.5 stamina per square (Agility 1) | Each stamina is worth ≈ 6 points of first-mover win rate (§2). |
| Leaving: OAs and avoidance | 1 stamina per adjacent enemy per square left | OAs are capped at 1 stamina; avoidance is a flat 1 (MV-3, MV-5). |
| Ranged threat: a shooter's band and my cover | Short/medium/long cost the *shooter* 0/1/3 extra stamina and lower its damage; cover adds +2/+5 to a Ranged Defense of 1–3 | A 6-stamina longbow shot at short range costs an unshielded target 7–12 stamina and 11–18 HP (§4). Half cover roughly halves that; total cover ends it. |

Everything in the first four rows is small or binary at the scale of a 12×12 map; the fifth row is enormous. That is the shape of the designer's observation that only "in melee / can reach melee / far away" matter: melee has two bands plus a gentle slope, and the slope is gentle because the rules price a square at half a stamina. Shooters add a steep gradient, which the melee rules then let a fighter cross for 3 stamina.

Which of these is inherent? The engager-count and leaving rows are mechanics the designer chose and stated (position-blind exchange, non-sticky battlefield). The threat-radius and approach rows are numbers (free movement, purchase price, cap). The ranged row is content whose steepness is set by the open F3 question. The rest of this report measures the two numbers rows and shows what the ranged row does when the numbers let it persist.

## 2. The approach: a distance sweep

Two sample fighters, both tactical (chip-kill), on a 32×10 open strip, starting 1–15 squares apart, under each movement rule. First-mover win rate (300 trials; "squares to contact" is one less than the distance apart):

| Apart | Cost to close (Agility 1) | v0.9 | capped | one square, flat | one square, escalating | extra movement is an action | none |
|---|---|---|---|---|---|---|---|
| 1 (adjacent) | 0 | 66.8% [61.2, 71.9] | | | | | |
| 2 | 0 | 68.8% | | | | | |
| 3 | 0 | 68.4% | 68.4% | | 68.4% | | 68.4% |
| 5 | 0 | 67.1% | 67.1% | | 67.1% | | 67.1% |
| 7 | 0 | 70.6% | 70.6% | 70.6% | 70.6% | 70.6% | 70.6% |
| 9 | 1 / 1 / 2 / 3 / 1 / — | 60.9% [55.2, 66.3] | 60.9% | 52.4% | 47.6% | **27.0%** | **27.0%** |
| 11 | 2 / 2 / 4 / 10 / 3 / — | 52.9% [47.2, 58.5] | 52.9% | 42.8% | **7.4%** | 29.9% | 29.9% |
| 13 | 3 / 3 / 6 / 21 / 6 / — | 49.0% [43.3, 54.7] | 49.0% | 30.2% | 29.5% | 22.2% | 29.5% |
| 15 | 4 / — / 8 / 36 / 10 / — | 44.8% [39.2, 50.6] | **37.8%** | 20.5% | 47.7% | **8.8%** | **73.0%** |

(Costs: v0.9 and capped / one square flat / one square escalating / extra as action / none; "—" is unreachable in one turn.)

Reading:

- **The 67–71% at a free close is the exchange, not movement.** It is the same at 1 square apart as at 7, and it is the review's all-adjacent duel figure (69–71%, `m1_parity.md`). Striking first from a full pool is worth about 20 points, and nothing in the movement rules touches it for the first seven squares.
- **Under v0.9 each stamina the close costs is worth about 6 points of first-mover edge** (−8, −8, −4, −4 for the first four). Approach is already a priced decision; the price is just 0 until 8 squares to contact and 1 per 2 squares after. The edge reaches even at 13 apart. The earlier duel at 8 apart (58.7%) sits where one purchase puts it.
- **One square per purchase (F10 option 1) doubles the slope**: even at 9 apart, 43% at 11, 20% at 15 — the last two with a tactical agent that dashes whenever one attack step remains affordable, which is a losing habit under this rule (it arrives with 6 and strikes weakly). A player would stop short instead, and the fight would fall into the next regime.
- **Where the close cannot be bought, distance parity decides.** Under "none" (and under the cap beyond 13 apart, and under one-square escalating where the dash is ruinous) the first mover loses the first strike whenever its free move ends inside the second mover's free reach: 27–30% at 9–13 apart, then 73% at 15, where the parity flips. With no purchases a 6-square free move gives a 12-square period, and the fight is decided by where the two happened to start. With smarter agents this becomes a standoff instead: both stop just outside reach and wait. Either way the players' choices are not what decides it.
- **Cheap flat purchases smooth the sawtooth into a slope.** That is a merit of the designer's "flat 1 per purchase" ruling that was not in the design log's reasoning (which was about chases): it removes distance-parity luck from the approach. The cost is that it leaves the first-strike edge untouched at the distances dungeon rooms give.
- **"Extra movement is an action"** (a purchase costs 1 + the surcharge and raises it, so a base-2 strike after one purchase costs 3+4+5 and after two 4+5+6, instead of 2+3+4) turns every dash into a trap for the dashing agent (27% at 9 apart, 9% at 15). It is the steepest coupling of approach to strike available, and it reverses a 2026-11-01 ruling; §6 weighs it.

**Two follow-up cells on the opening itself (O1, 300 trials, same duel at 1 / 7 / 11 apart).** The review-candidate +2 surcharge lowers the level-1 first mover to 57.6% / 62.7% / 50.4% but leaves 20–21% of fights drawn at the 30-round cap (mean 15 rounds), and at level 30 it draws 79–84% of fights: the balanced exchange stops landing anything while armor soaks the graze leaks, which is the stalemate the graze-leak change in `Crit_Rule_Alternatives` exists to break. Starting the fight at half stamina (`resources.start_stamina = half`, a new switch) changes nothing: 67.9% / 70.3% / 55.3% at level 1 against 66.8% / 70.6% / 52.9%, and 61.8% / 65.6% / 58.2% at level 30 against 65.0% / 67.4% / 58.7% (v0.9, 10–12% draws), with fights 40–60% longer. Both pools climb at the same rate and the first mover reaches each threshold first: the edge is in the order of turns, not the size of the opening strike.

Where the design should want to be: the first-mover edge at the distances fights actually start should not be 70%, and approaching should not be suicidal, and distance parity should not decide. v0.9 satisfies the last two everywhere and the first only beyond 11 squares. The dial that moves the even point closer is the price of the first one or two purchases; the lever that moves it furthest without new rules is encounter distance (fights that start 11–15 apart are even under v0.9 already).

## 3. The chase: a fast kiter against slow brutes

The designer's scenario: a high-Agility character fighting outnumbered against powerful, slow enemies. Built as: a kiter (Agility 5, Finesse 3, longbow with a quick-drawn shortsword, light armor; free movement 8, 4 squares per purchase, 13 stamina, HP 7) against two brutes (Strength 4, Agility 0, heavy armor 3, greataxe 2d6+12 a step; free movement 5, **1 square per purchase**, 16 stamina, HP 10). Field 38×10 with the kiter 16 squares from the brutes (longbow medium range) and 20 squares of room behind it. A brute's single step forces the kiter to block for 8–9 of its 13 stamina; any arrival with three stamina is a disaster for the kiter, and a three-step strike kills it from full.

### 3.1 The arithmetic

- **Speed is worth one stamina a turn.** The kiter moves 8 free squares to the brute's 5, so a brute keeps pace for 3 stamina a turn, or closes a 16-square gap in one turn for 10 (5 free + 10 purchased squares, 1 stamina each) and still has 6 for a one-step strike. Each stamina the kiter spends running (4 squares) costs an Agility 0 brute 4, an Agility 2 brute 2, an Agility 5 chaser 1. That exchange rate only matters if the pursuer runs out of pool before it arrives, and 16 stamina covers 15 squares.
- **The dash is the brute's winning move, not an accident.** When the brutes refuse to pay more than 0–2 stamina for movement a turn (`chase_spend`), the kiter wins 57–59% [51, 64]; when they pay up to 4, 42%; when they pay anything that leaves one strike step, 6% [3.8, 9.3]. The 10-stamina sprint that arrives with a 3-stamina poke is correct play because the poke forces an 8-stamina block out of a 13-stamina pool.
- **The field decides whether speed can be used.** A kiter that cannot be reached in one turn still needs room to run: under the cap it is caught only at the wall (traces in the notes), after 5–6 rounds on a 20-square field.

### 3.2 What the movement rule does to the matchup (K1a, K1d, K2, K3; 300 trials each)

Kiter wins (draws under 1% except where shown); "brutes' sprint" is the brutes' purchased-movement stamina per fight.

| Matchup | v0.9 | capped at Movement | one square, escalating | none |
|---|---|---|---|---|
| Kiter vs two brutes, long field | **6.0%** [3.8, 9.3]; 0.8 shots; brutes sprint 16 | **42.0%** [36.6, 47.7]; 2.0 shots; sprint 1.4 | 45.0% [39.5, 50.7]; 2.6 shots | 61.3% [55.7, 66.7]; 3.6 shots |
| Same, brutes in light armor | 10.3% | 69.7% | 63.7% | 83.0% |
| Same, brutes Agility 2 (free 6, 2 per purchase) | 0.0% [0.0, 1.3], 1 round | 17.3% | 29.0% | 37.0% |
| An ordinary archer (Agility 1, Finesse 2) as the kiter | 0.0% | 8.7% | 23.7% | 25.3% |
| One brute instead of two | 81.7% | 100% | | |
| Two shielded sample fighters (Agility 1, Ranged Defense 3) instead of brutes | 0.0% | 1.3% [0.5, 3.4] | | 6.3%, 9% draws |
| The room (three squares of floor behind the kiter) | 0.0% | 11.7% | 11.7% | 12.0% |
| Gap-holding kiter (reserve 6), long field | 0.0% | 14.7% | 14.0% | 10.0%, **84.7% draws** |
| Gap-holding kiter, the room | 0.0% | 5.0% | 5.3% | 10.0%, **88.7% draws** |
| Extra movement as an action, long field (D1x-k) | kiter 15.7–16.7%, 16–32% draws, 10–12 rounds; brutes spend 17–22 on movement | | | |

Reading:

- **Under v0.9 the kiter cannot kite**, with any policy tried: running 1–4 stamina a turn gives 3–8%; not running at all gives 26% (K1b), because stamina spent running is stamina not available for the block that follows the inevitable arrival. It is caught in round 1 whenever the brutes win initiative.
- **The rule that stops the all-in sprint flips the matchup.** Capping purchases at Movement is the mildest: it costs the brutes nothing they were using in any other fight (D1 is identical to v0.9 through 13 apart), and it turns 6% into 42% here and 10% into 70% against light armor. Shots per fight go from 0.8 to 2–3.6; the brutes' movement spend collapses from 16 to 1–2.
- **The cap keeps the designer's p.1706 property.** An ordinary Agility 1 archer still cannot outrun Agility 0 brutes under the cap (8.7%), and Agility 2 brutes still mostly catch the Agility 5 kiter (17%). Speed buys escape only when the gap in Agility is wide: the cap makes Agility the chase stat without making every archer uncatchable.
- **Armor and shields, not speed, decide whether the kiter can "pick them off".** Against heavy armor its shots down 1.1 brutes a fight under the cap; against light armor 1.6. The longbow at medium range (one aim, 6 stamina) deals an expected 8 injury to a Ranged Defense 1 brute in heavy armor and 11 in light (§4), so kiting is attrition, and the kiter wins when it has the room for two or three shots per brute. Against two shielded sample fighters (Ranged Defense 3) it deals 4 injury in a whole fight and wins 0–6% under every rule: the shield is the counter the packet says it is, and the cap does not change that.
- **The room ends every version of the kite.** With three squares behind it the kiter wins 0–12% under every rule: the brutes walk it to the wall and the greataxe does the rest. Encounter geography decides whether speed or power wins, which is as plausible as anything in the system and is a GM lever that needs no rule.
- **"None" lets the fast creature refuse the fight.** A gap-holding kiter under "none" produces 85–89% draws at the 20-round cap, on the field and in the room alike (K1e): the brutes' reach is 6 and the kiter circles at 7 forever, shooting too little to finish them. The fast side can always disengage and nothing can force it; that is a stall, not a tactic.
- **"Extra movement as an action" slows the chase without ending it.** The brutes still sprint (17–22 stamina a fight, escalating), the fights run 10–12 rounds, and a third end at the cap; the kiter wins 16–17%.

The gap-holding kiter (K1e) was not better than the simple "run as far as you can" one (15–17% vs 42% under the cap); its reserve rule made it fire low-aim shots that heavy armor shrugs off, and it hugged the brutes' reach too closely. Read the kiting rows as "what a competent runner gets", not an optimum.

## 4. Ranged on top of movement

### 4.1 The exchange a shot forces (exact, `analysis/ranged`)

What one longbow shot costs the target, against its best blocks, for the kiter (Finesse 3, Strength 1) and the review's archer (Finesse 2, Strength 1). "Spend" is stamina the target pays blocking; "down" is the chance the shot incapacitates from full.

| Shot | Cost | Brute (RD 1, armor 3, HP 10) | Light brute (RD 1, armor 1) | Sample fighter with shield (RD 3, armor 2, HP 8) | Two-hander, no shield (RD 1, armor 2, HP 8) |
|---|---|---|---|---|---|
| Kiter, short, no aim | 5 | 4.2 injury, 7.5 spend, 12% down | 7.0 / 7.5 / 38% | 0.0 / 3.9 / 0% | 6.4 / 5.6 / 38% |
| Kiter, short, one aim | 6 | 15.4 / 11.3 / 69% | 18.2 / 12.0 / 69% | 1.5 / 9.6 / 0% | 18.3 / 8.4 / 75% |
| Kiter, medium, one aim (the mandatory one) | 6 | 8.4 / 7.5 / 38% | 11.1 / 7.5 / 38% | 0.0 / 6.5 / 0% | 10.4 / 6.0 / 38% |
| Kiter, long, two aims | 8 | 12.4 / 7.9 / 38% | 14.5 / 10.2 / 38% | 0.8 / 8.5 / 0% | 14.2 / 6.9 / 62% |
| Archer, short, one aim | 6 | 11.1 / 9.1 / 48% | 13.8 / 9.7 / 50% | 0.6 / 7.8 / 0% | 13.5 / 7.2 / 56% |
| Archer, medium, one aim | 6 | 5.4 / 6.0 / 25% | 7.9 / 6.0 / 25% | 0.0 / 4.5 / 0% | 7.1 / 4.8 / 25% |

Two things follow for movement:

- **Being inside a bow's short range is the most expensive place on the map for anyone without a shield.** A 6-stamina shot takes 7–12 stamina *and* 11–18 HP from a Ranged Defense 1 target; the shield turns the same shot into a 4–10 stamina tax with almost no injury. No melee position differs from another by anything like this. This is the gradient the designer expected ranged combat to supply, and it is already here; the F3 question (ranged lethality) sets how steep it is for whom.
- **The bands are a price on the shooter, not a defense for the target.** Medium range costs the shooter one mandatory aim and the first d6; long costs two. Against heavy armor that halves the injury (15 → 8 → 12 for the kiter). So distance from a shooter is worth 3–7 injury per band to an unshielded target, which is a real gradient, and cover is worth more.

Why none of this showed in the archer fights of the first report: the sample fighter crosses 11 squares for 3 stamina and strikes from a near-full pool, so the shooter gets one volley and the gradient lasts one turn. Under rules that stop the dash the volleys multiply (0.8 → 2–3.6 per fight in §3) and the gradient is the fight.

### 4.2 A free turn for a shooter, and a screen (R1, S1)

**A shooter with a free turn kills.** The kiter shooting a brute that only stands and blocks (R1; 300 trials each): one shot, 100% down, at 6 squares and at 12, in heavy armor and in light. The agent fires the full three-aim volley (11 stamina, 33–44 expected injury against a 10-HP target that spends 13–14 blocking). This is the F3 "known problem" in its purest form, and it is why every approach rule in this report comes down to how many free turns the shooter gets: one volley is a kill, so the fighter's only play is to arrive before the shooter has one.

**A melee body protects a shooter only when the approach cannot be bought.** An archer (`l1_archer`) with a sample fighter one or two squares in front of it, against two sample fighters eight squares off, open ground (S1, 300 trials):

| Screen | Party wins, v0.9 | Party wins, no extra on-turn movement |
|---|---|---|
| Fighter one square ahead, tactical | 14.3% [10.8, 18.8]; 0.6 shots a fight | **83.0%** [78.3, 86.8]; 2.8 shots |
| Fighter one square ahead, holding its square | 3.7% [2.1, 6.4]; 0.4 shots | 56.7% [51.0, 62.2]; 2.3 shots |
| Fighter two squares ahead, tactical | 23.7% [19.2, 28.8] | 52.3% [46.7, 57.9] |
| Fighter two squares ahead, holding | 4.3% | 23.0% |

Under v0.9 the two attackers walk around the screen (14–15 squares of on-turn movement a fight, 1.5–1.9 stamina bought) and reach the archer in round 1; the screen is a speed bump that the archer's one shot does not pay for. With no purchasable movement the attackers need two turns to get round a body, the archer shoots two or three times, and the screened party wins. The holding screen is worse than the tactical one under both rules because a fighter that never steps forward never threatens the squares beside it. Formations, like kiting and like cover, exist only at the pace the movement numbers allow; today they do not.

## 5. Inherent, numbers, or elsewhere?

Taking the designer's three candidates in turn.

**Inherent to the mechanics.** The melee exchange is position-blind: a square adjacent to an enemy is like every other adjacent square, and the first strike from a full pool is worth 67–71% whatever the distance. That is a consequence of three stated choices — no facing or flanking, OAs capped at 1 with flat avoidance, and blocks that reset per attack — and of a fully informed, deterministic exchange. It is not a flaw to fix with movement rules; it is what keeps the attack sequence to one roll and a block count. The thing it implies is that melee position can only ever carry two signals (how many engage me, and what reaching them costs), so any richer positional game must come from terrain, shooters, zones and abilities.

**The numbers.** Two of them, and both are "Numbers placeholder" in the packet:
- *Purchased movement is uncapped at 1 per purchase.* This single fact makes the chase un-winnable by speed (§3), makes off-turn movement's stated purpose ("force pursuers to spend stamina") toothless (the first report), and puts every square of a 12×12 map inside every melee creature's threat radius. The cap at Movement is the smallest change that fixes the first without touching duels through 13 squares.
- *Free movement 5–8 against the distances fights start.* Free closes decide nothing and leave the first-strike edge at 70%; v0.9's purchase price only starts to bite at 8+ squares to contact. The slope is right (6 points per stamina); its origin is 7 squares too far out for indoor fights.

**Elsewhere.** The designer is right that square value needs shooters, cover, chokepoints and areas to exist, and the design notes say the tactical interest "should come from the shared core systems (stamina, commitment, blocking, movement), not mainly from a large catalogue of class abilities" (§3.6). Ranged combat, cover and terrain are core, so this is not a contradiction: ranged supplies the steepest gradient in the game and cover its counter. But content cannot do the job while the numbers above let a fighter erase a 12-square gradient for 3 stamina, and the two pending readings that make terrain real (`grid.corners` for doorways; the corridor results of the first report) are rules, not content. Abilities and AoE come after that, and they will inherit whatever the approach dial says.

So the honest ranking is: numbers first (one cap, one placement of the price curve), then the two pending rules (corners, F3), then content. The inherent part is fine as it is.

## 6. Options, against the pillars

| Option | What it does (measured) | P1 stamina | P2 danger seen and answered | P3 fiction | P4 builds | C1 load | Cost |
|---|---|---|---|---|---|---|---|
| **Cap purchased movement at your Movement** (`extra_cap = free_movement`) | Kiting 6% → 42%; archer-vs-fighter and all duels to 13 apart unchanged; brutes' sprint 16 → 1.4 | ✓ still priced in stamina | ✓ a countable radius: "he can reach 11 squares at most" | ✓ you cannot sprint forever in one turn | ✓ Agility becomes the chase stat; same-speed archers still caught | ✓ no new number (your Movement, doubled) | Adjacent to the rejected "Dash action"; must be argued against the p.1706 intent, which it preserves |
| **Keep flat 1-per-purchase, uncapped** (v0.9) | Smooth approach slope, no parity luck, chasers always win | ✓ | ✓ | ✓ | ✗ speed cannot escape power | ✓ | First-strike edge 70% at ≤ 7 apart; kiting impossible |
| **One square per purchase** (F10 option 1, `extra_squares = one`) | Even at 9 apart, 43% at 11; archer unchanged at 11 squares; kiting 45% (escalating version) | ✓ | ✓ | ~ | ✗ removes Agility's purchase edge (4 squares a stamina → 1) | ✓ | Dashing becomes a trap at 13+; standoffs with good players |
| **Extra movement is an action** (`extra_is_action`) | Every dash past free movement is punished (27% at 9 apart, 9% at 15) | ✓ reuses the surcharge | ~ | ~ "a sprint tires the swing" | ✓ | ✓ no new number | Reverses the 2026-11-01 ruling; too steep as measured; standoffs |
| **No extra on-turn movement** | Kiting 61%; a fast creature can refuse the fight forever (85% draws); approach decided by distance parity (27% vs 73%); prompts double | ✗ movement leaves the economy | ✗ parity luck | ~ | ~ | ✗ off-turn prompts 15 → 35 a round | Rejected on the first report's evidence |
| **Lower free movement (4)** | Even at 8 apart (49%), retreats 31% → 22%, archer 25% → 43% | ✓ | ✓ | ~ | ~ | ✓ | Against the locked "movement shouldn't be discouraged"; hurts retreat more than pursuit |
| **Rule on `grid.corners = no_cut`** | Doors become chokepoints (first report §4.2: 0% → 35% draws) | — | ✓ | ✓ | — | ✓ | Corridors around corners slower for everyone |
| **Resolve F3 (ranged lethality)** | Sets how steep the ranged gradient is; today a cliff for unshielded targets (69–75% down to one aimed shot) | — | ✗ today: a shot can kill from full with no answer but a shield | — | ✗ today: shield-less builds are helpless | — | Not a movement rule; decides what "far away" is worth |
| **Encounter distance and map size** (GM guidance, no rule) | Fights that start 11–15 apart are even under v0.9; rooms end kites | — | — | ✓ | — | ✓ | Does nothing for the dungeon fights that start at 6 |

What I would do, in order: (1) adopt the cap and re-run the archer, kiting and duel suites under it; it is the one change with no measured downside in anything run so far, and it gives Agility its identity. (2) Rule on corners, then fix F3, so that terrain and shooters can carry square value. (3) Decide where the even point of the approach should be, and set it with the first purchase's price or with encounter-distance guidance rather than with free movement. (4) Only then look at abilities and areas; they will be priced on top of whatever (1)–(3) produce.

Two warnings. Steeper approach pricing trades the first-strike edge for standoffs: agents that dash into it lose 7–30%, players who refuse to dash will wait at mutual threat range, and the only pressure the rules put on waiting is the wasted recovery at full stamina. And every kiting number here depends on the brutes being willing to chase; a patient brute that walks and blocks beats the current rules' kiter only because the kiter's shots do little to heavy armor — change F3 and that changes.

## 6b. Three checks prompted by the designer's challenges (C1–C3, 300 trials each)

- **Does the HP–stamina link ever bind in a fight?** No. In 200 adjacent level-1 duels with 461 injuries the maximum-stamina clamp at injury never removed a point, and no recovery was wasted at the cap; at level 30, 34 points over 200 fights, all by near-full winners. The first-mover edge is sequencing alone, and the earlier suggestion that F7 compounds it is withdrawn.
- **Do opportunity attacks change behaviour even when unpaid?** No. With `opportunity.enabled = false` the screen fight is 87.3% for the attackers against 84.7% as written, the 3v3 is 52.0/47.7 against 51.0/48.0, and the corridor 1v3 is unchanged — all inside the intervals. The agents do route around threatened squares (3.5 stamina of avoidance a fight in the 3v3), but the rule's presence changes neither the paths that matter nor any outcome. Untested: FIN 3 creatures (cap 4) and reach weapons with the F9 options.
- **The designer's preferred stalemate fix: pricier grazes, armor intact** (`blocks.graze_cost = 2`; digest `018337d87d3d` under v0.9, `3731943d0d6d` with the +2 surcharge). Under the v0.9 surcharge it hands the fight to the first mover — 88.0% at level 1 and 84.3% at level 30, no draws, 3–5 rounds — because the defender's one cheap answer is gone. With the +2 surcharge it does what was hoped at level 1 (first mover 65.0%, 0% draws, 6 rounds; +2 alone is 57.6% with 20.7% draws) and goes half way at level 30 (draws 80.0% → 31.0%, mean 27.6 → 18.7 rounds, first mover 60%). So pricier grazes plus +2 is a real alternative to the graze-leak change, with the same first-mover edge as v0.9 at level 1 and a third of level-30 fights still undecided at 30 rounds. Graze cost 2 is a blunt setting; a graze that escalates with the perfect blocks (1, 2, 3 on the attack's own count) would be the refined version, and the next thing to build if this route is preferred.

## 7. Engine changes (on `exp/movement`, patch attached)

- Tactical agent: `kite = "distance"` (run from the nearest melee enemy after shooting, buying up to `kite_spend`; `kite_gap` holds a distance instead of maximising it; `shot_reserve` keeps stamina for the run and caps aims; a kiter caught with its blade out runs instead of fighting; no agent now buys a shot that is a certain miss at medium or long range), `chase_spend` (a pursuer's ceiling on movement stamina to reach an attack square).
- `movement.extra_is_action` (experiment variant, pending designer): a purchase costs its base plus the on-turn surcharge and advances it. Default off; digests unchanged; `component_defaults.json` regenerated; Assumptions register row added.
- Builds `l1_kiter`, `l1_brute`, `l1_brute_light`, `l1_brute_agi2` and maps `kite_field`, `kite_room`, `open_32x10` under `reports/movement_ranged_results/`.
- `experiments_ranged_movement.py` (runners K1, K1e, K2, K3, D1, D1x, R1, S1), raw rows and console logs under `reports/movement_ranged_results/`.
- Fast suite, `mypy --strict src` and `ruff check src tests examples` pass from source.

Agent limitations that bound these results: the tactical pursuer dashes whenever one attack step remains affordable (a losing habit under steep pricing: the 7–30% rows); the kiter's gap-holding variant under-performs the simple runner; no agent waits at mutual threat range, so the standoff regime is inferred from the parity sawtooth, not measured; the brutes never spread out to cut off a runner. Human play (`se play`) on `kite_field` under the cap, and on the 11-apart duel under v0.9 and one-square flat, would test the two claims that matter most.
