# Movement exploration: off-turn windows, on-turn extra movement, terrain and numbers

Design chat, 2026-11-04. Engine `main` = 7bd1bb8 plus the `exp/movement` changes in §6 (patch attached; nothing pushed, since push access is refused for the chat). Fight rows are 300–400 trials; 95% Wilson intervals are in the raw results (`reports/movement_exploration_results/*.jsonl`) and quoted in the text wherever a difference is claimed. Engine agents only, two families (scripted, and tactical with the new `pin` and `hold` options); no human play. Where a result depends on agent behavior rather than rules, the text says so. Companion: `movement_exploration_notes.md` (scenarios, agent specs, traces).

Baseline stamp: `RuleSet v0.9 3bf6fc070dbf; Code git 7bd1bb8 (uncommitted changes)`. The source hash in the stamps moved from `262c361abfc1` to `ca09d562aaf5` to `4a3e9bc3225f` as agent options and the `scope` switch were added between runs; no rule component changed between runs (every variant's digest is the same in every file it appears in). Variant digests are in each table.

## 1. Summary

1. **The off-turn window order barely matters in fights, and the designer's intuition about why is right.** In every fight scenario the three orders (ascending initiative as written, descending, and the designer's "declare, tiebreak on initiative, respond" scheme) gave the same outcomes within noise. The mechanism is real but small: when a fleer and a pinner contest one window, the order decides who moves first, and moving first costs the fleer about one stamina of avoidance per contested window (3 vs 2 in the micro-race) or costs the pinner the last word at equal budgets. Fights rarely contest windows at all, because free on-turn movement does the chasing for nothing.
2. **On open ground, off-turn movement is never used in duels and cannot change a dogpile.** Equal duels: 0.0 off-turn squares per fight under every order rule. 1v3 on open ground, in a corner, among pillars and behind a door: the defender loses 100% with windows on or off. In the corridor the windows lengthen the fight (median 2 rounds instead of 1) and cut deaths per fight by about 0.15. This is Addendum 2's arithmetic (retreat cannot buy tempo against 5–8 free squares) measured in team fights.
3. **On-turn extra movement is priced out of the arriving fighter's exchange budget, and that is the only way it matters.** The sample fighter has 14 stamina. Whatever the close costs is missing at the moment of contact, for the strike and for the blocks against the reply. Against the archer the result is a cliff: as long as the fighter arrives with a two-step strike in hand (close ≤ 9 of 14), the archer wins 22–25% under every priced variant; when it arrives with 4 (free 4 + escalating, close 10) the archer wins 43%; when it cannot arrive in one turn, 53%. Against an equal melee opponent it is a slope: first mover 58.7% arriving with 13 stamina, 56.7% with 12, 49–55% with 11, 38.2% with 8, 29–33% when it cannot arrive and the second mover strikes first with a full pool. At the distances fights actually start (7–9 squares to contact) v0.9 prices the close at 1–2 stamina, so the price is invisible; flat versus escalating never differs within three purchases.
4. **Removing extra on-turn movement makes approach a liability and turns the windows into the chase.** With no on-turn purchases, the first mover in a duel 8–10 squares apart wins 29–33% (v0.9: 57–59%): it closes to two squares and eats the first strike. Team fights go from 3–8 off-turn squares a fight to 56–115, fights lengthen (2v2: 4 → 7 rounds; 3v3: 4 → 7.5), retreating to an ally works (fleer's side 31% → 57%), off-turn prompts more than double in team fights, and a kiting archer on an unbounded field would be uncatchable.
5. **Numbers dominate everything movement can do.** Equal sample fighters, tactical agents, open ground: 1v2 is 0.0% [0.0, 1.3], 2v3 is 0.0%, 2v4 is 0.0%, 3v4 is 2.7%. One body of advantage decides the fight at these stamina and recovery numbers, because blocks reset per attack while the pool and the recovery are shared. Movement rules change how long it takes (2v3 lasts 5 rounds instead of 2 when the outnumbered side can run; 7% instead of 0%), not the result.
6. **Terrain helps only a defender that holds it, only real terrain, and the diagonal-corner rule decides what is real.** A defender that stays one square inside a one-wide corridor and attacks whatever reaches it turns 1v3 from a two-round loss into an eight-round fight it survives to the round cap 36% of the time (28% against tactical attackers). Standing in the corridor mouth or in a corner gives nothing. A one-square door gives nothing under the engine's default corner rule (`no_squeeze`: attackers step diagonally out of the gap past the defender) and becomes a chokepoint as good as the corridor under `no_cut` (35% draws, 9 rounds, deaths 0.19). That switch is pending the designer in the assumptions register, and it decides whether doorways matter in this game. The tactical defender steps out of the corridor to attack and dies in the open; discipline, not geometry, is the scarce input.
7. **Decision load.** Off-turn windows are 31–56% of all requests in every fight (3.6 asks per round in a duel, 13–15 in 1v3 and 3v3) and are acted on in 0–11% of asks; 0–27% of windows see any move. Skipping the window after allies' turns removes a third of off-turn asks in team fights with no change in play. The designer's declaration scheme asks 25–50% more in a contested window and slightly fewer overall. Removing extra on-turn movement raises off-turn asks from 15 to 35 per round in 3v3.

**Where this leaves the design.** Movement is the second axis the single-pool exchange lacks, and at the moment it is almost free, so the game has a priced exchange economy and an unpriced position economy. The levers that actually change play are (a) what the close costs out of the arriving creature's pool at the distances fights start, (b) how many turns the close takes (free movement against typical distance, which is what gives archers and retreats a game), and (c) whether terrain is a chokepoint, which is a rules question (corners) before it is a map question. The window-order rule is a fairness and rules-text question, not a balance one; the declaration scheme is the cleaner rule. §5 has the options.

## 2. Off-turn windows and the order rule

### 2.1 The mechanism, isolated (`window_race.py`, deterministic)

Two creatures in one window: F wants a gap of more than one square, P wants adjacency. Both have an off-turn budget and pay the packet's escalation (1, 2, 3…). F pays to avoid every OA; P takes OAs. Start gap 2.

| Case | Order | Higher initiative | Final gap | F paid (move + avoid) | P paid | Asks |
|---|---|---|---|---|---|---|
| Equal AGI 1, budgets 6 and 6 | asc | F | 3 | 6 + **3** | 6 | 12 |
| | asc | P | 3 | 6 + 2 | 6 | 12 |
| | desc | F | 3 | 6 + 2 | 6 | 12 |
| | desc | P | 3 | 6 + **3** | 6 | 12 |
| | desc + restart | F | 3 | 6 + 2 | 6 | 15 |
| | desc + restart | P | 3 | 6 + **3** | 6 | 18 |
| Pinner richer (10 vs 6) | any | any | **1 (adjacent)** | 6 + 2–3 | 10 | 12–20 |
| Fleer AGI 1 vs pinner AGI 3 | asc | F | 3 | 6 + 3 | 6 | 12 |
| | asc | P | **1** | 6 + 2 | 6 | 12 |
| | desc | F | **1** | 6 + 2 | 6 | 12 |
| | desc | P | 3 | 6 + 3 | 6 | 12 |
| Fleer AGI 3 vs pinner AGI 1, full moves | any | any | 4 | 3 + 1–2 | 3–6 | 9–13 |
| Fleer AGI 3 vs pinner AGI 1, one purchase per move | F moves first in the exchange (asc with F lower, desc with F higher) | | **5** | 6 + 1 | 6 | 15–18 |
| | P moves first | | 3 | 3 + 1 | 6 | 12 |

Reading:
- The race alternates: P closes, F retreats, P closes… It ends when a budget runs out, so **budget decides adjacency**; at equal budgets the creature that moves *second* in each exchange has the last word. The order rule decides who moves first: under ascending order the lower-initiative creature, under descending the higher.
- Moving first as the fleer costs the avoidance tax: once P is adjacent, every retreat leaves a threatened square. Ascending order with F higher: F pays 3; descending: 2. About one stamina per contested window, which is the size of the effect the designer suspected.
- The designer's reading ("high initiative is bad under ascending") is right in direction: ascending lets the low-initiative pinner impose the tax before the high-initiative fleer can act. Under descending the higher creature has a choice: pre-empt (no tax, but it has moved first and may lose the last-word parity) or pass and react (tax, parity). Under ascending it has no choice.
- Agility already tells under full-move resolution (the AGI 3 fleer ends 4 away instead of 3, paying half as much). Per-segment resolution (one purchase per move) adds the "surprise distance" the designer described, but only when the fleer answers each of the pinner's segments, which it does when it is the first to move in the exchange: it then gains a square per exchange and ends 5 apart. When the pinner moves first the fleer settles at 3 and saves its stamina. So per-segment resolution makes the order rule matter *more*, not less: it decides who gets to be the reactor.
- The declaration scheme (descending + restart) asks 25–50% more questions in a contested window (15–18 vs 12), because the first creature in order is re-asked after every move.

### 2.2 In fights (B1, 400 trials per row)

| Scenario | asc (v0.9) | desc | desc + restart | desc + restart, 1 purchase per move |
|---|---|---|---|---|
| Duel 8 apart, both retreat+pin | first mover 58.7%, 0.0 off-turn squares | identical | identical | identical |
| Archer vs pinning fighter, open | archer 27.8%, 0.3 off-turn squares | 27.5% | 27.5% | 27.5% |
| 1v3 open, retreating D vs pinning attackers | D 0%, 1 round, 5.8 off-turn squares | same | same | 1.2 off-turn squares |
| 1v3 corridor, same | D 0%, 1 round, 5.3 | same | same | 1.4 |
| Retreat line 2v2, fleer vs pinning chasers | line 53.5% [48.6, 58.3] | 50.0% [45.1, 54.9] | 50.0% | 47.0% |

Nothing moves outside the intervals. Duels show zero off-turn movement because the tactical agent retreats only to a square with fewer engagers, and on open ground none exists (an adjacent enemy's free movement covers every reachable square); the pin behavior fires only when the target is out of reach, which in a duel it never is after turn 1.

With extra on-turn movement removed (B1n) the windows carry the chase, and the order still does not matter: archer vs pinning fighter 68.8 / 69.0 / 69.0%; retreat line 62.0 / 58.2 / 58.2% for the fleer's side; duel first mover 55.7 / 55.9 / 55.9% with draws 3.5 / 6.0 / 6.0%. The one-purchase-per-move variant changes results (57.5%, 65.5%, 28.9%) by disabling the pin heuristic, which needs a full move to reach adjacency: an agent effect, not a rule effect.

Two agent facts shape these numbers. Pinning is a bad trade on open ground: the fighter that pins off-turn wins 31% of archer fights against 47% without pinning (B1n-a vs B1n-b), because the chase race costs the chaser as much as the fleer and positions reset on the fleer's turn. And the duel with both agents set to flee when engaged (B1n-d) is a retreat-and-approach loop — flee six squares after the enemy's turn, walk six back on your own, flee again (18–24 off-turn squares a fight) — so its 55.7% first-mover figure measures that loop, not the rule. The designer's scheme would reward a smarter fleer (pass, then react) that no engine agent implements.

### 2.3 Decision load (`window_load.py`, 150 fights per row)

| Scenario | Variant | Windows / round | Off-turn asks / round | Asks acted on | Windows with any move | All requests / round |
|---|---|---|---|---|---|---|
| Duel 8 apart | v0.9 | 1.8 | 3.6 | 0.0% | 0.0% | 11.5 |
| 1v3 open | v0.9 | 2.6 | 13.2 | 5.1% | 25.6% | 27.6 |
| | not after allies | 2.6 | **8.6** | 7.9% | 25.6% | 22.9 |
| | desc + restart | 2.6 | 12.3 | 5.5% | 25.6% | 26.7 |
| 1v3 corridor | v0.9 | 3.3 | 14.1 | 1.8% | 7.7% | 25.0 |
| | not after allies | 3.3 | **8.9** | 2.9% | 7.7% | 19.9 |
| Archer, open | v0.9 | 1.2 | 3.2 | 11.0% | 26.7% | 10.2 |
| | no on-turn extra | 1.6 | 4.2 | 13.0% | 33.2% | 11.9 |
| Retreat line 2v2 | v0.9 | 3.0 | 8.8 | 2.7% | 6.4% | 19.6 |
| | not after allies | 2.9 | 6.5 | 3.0% | 6.0% | 17.0 |
| 3v3 open | v0.9 | 3.8 | 15.2 | 3.5% | 12.0% | 29.6 |
| | not after allies | 3.9 | **10.7** | 4.9% | 12.0% | 25.2 |
| | no on-turn extra | 4.9 | **34.7** | 6.1% | 39.8% | 49.0 |
| | desc + restart | 3.8 | 14.5 | 3.6% | 10.8% | 29.4 |

Off-turn prompts are the game's most frequent request and, outside the archer fight, its least consequential: in a 3v3, fifteen questions a round of which one in thirty changes anything. Skipping windows after allies' turns cuts a third of them at no cost to what happens (the "windows with any move" column is unchanged). Removing extra on-turn movement more than doubles them.

## 3. On-turn extra movement

### 3.1 The arithmetic

Stamina to move N squares on your turn (free movement first). AGI 1 has free 6 and 2 squares per purchase, AGI 5 free 8 and 4 per purchase; "free 5" and "free 4" lower the free base by 1 and 2. Contact distances in the scenarios: 7 squares (duel 8 apart), 9 (duel 10 apart), 11 (archer 12 apart). The sample fighter's pool is 14.

| Variant | AGI 1: 7 | 9 | 11 | 12 | 14 | 18 | AGI 5: 12 | 16 | 20 |
|---|---|---|---|---|---|---|---|---|---|
| agi, flat (v0.9) | 1 | 2 | 3 | 3 | 4 | 6 | 1 | 2 | 3 |
| one square, flat | 1 | 3 | 5 | 6 | 8 | 12 | 4 | 8 | 12 |
| agi, escalating (1, 2, 3…) | 1 | 3 | 6 | 6 | 10 | 21 | 1 | 3 | 6 |
| agi, escalating slope 2 (1, 3, 5…) | 1 | 4 | 9 | 9 | 16 | 36 | 1 | 4 | 9 |
| free 5, agi escalating | 1 | 3 | 6 | 10 | 15 | 28 | 1 | 3 | 6 |
| free 4, agi escalating | 3 | 6 | 10 | 10 | 15 | 28 | 3 | 3 | 6 |
| one square, escalating | 1 | 6 | 15 | 21 | 36 | 78 | 10 | 36 | 78 |
| agi, capped at Movement | 1 | 2 | 3 | 3 | — | — | 1 | 2 | — |
| none | — | — | — | — | — | — | — | — | — |

Off-turn, for comparison: AGI 1 buys 2 squares for 1, 4 for 3, 6 for 6, 8 for 10; AGI 5 buys 4 for 1, 8 for 3, 12 for 6.

Flat and escalating differ only from the second purchase on (9 squares and more for AGI 1), and the cap never binds inside a 12×12 map. The "one square per purchase" variants (F10 option 1) are the only ones that change prices at ordinary distances.

### 3.2 The archer fight (B2a, B2x-a; archer and fighter both tactical, 12 squares apart, open ground, 400 trials)

| On-turn extra movement | Stamina to reach the archer (11 squares) | Fighter arrives with | Archer wins | First mover wins | Median rounds |
|---|---|---|---|---|---|
| agi, flat (v0.9); capped | 3 | 11 | 25.2% [21.2, 29.7] | 75.5% | 1 |
| one square, flat | 5 | 9 | 24.5% | 74.8% | 1 |
| agi, escalating slope 1 | 6 | 8 | 24.5% | 74.8% | 1 |
| free 5, agi escalating | 6 | 8 | 21.8% | 72.0% | 1 |
| agi, escalating slope 2 | 9 | 5 | 25.5% | 73.8% | 1 |
| free 4, agi escalating | 10 | 4 | **43.0%** [38.2, 47.9] | 50.2% | 2 |
| one square, escalating | 15 (cannot) | — | **53.2%** [48.4, 58.1] | 46.0% | 3 |
| none | cannot | — | **52.8%** [47.9, 57.6] | 45.5% | 3 |

The fight is about the arrival strike. After an approach the first attack step costs 2 (the movement purchases count as a prior action), so a two-step strike costs 5: a fighter that arrives with 5 or more stamina has one, a fighter that arrives with 4 has a one-step poke for 2. Traces (notes §3): under v0.9 the fighter that wins initiative pays 3, arrives with 11 and lands a three-step strike (9) that kills or cripples the archer; under escalating slope 2 it pays 9 and lands two steps; under free 4 it pays 10 and pokes once for 2, which the archer blocks for 3 and then shoots at short range. When the fighter loses initiative, the archer's opening volley (three aims, 11 stamina) costs the fighter 9–13 stamina in blocks, after which it cannot buy anything: under free 6 it ends its turn 4–6 squares from the archer, under free 4 eight squares away and takes a second volley before contact. The archer cannot punish a drained fighter in melee (point-blank shots provoke and use Melee Defense; the tactical archer steps away and the fighter re-closes for free), but a drained fighter cannot hurt the archer either, and the volleys it absorbed in the meantime decide the fight. On the scattered-cover map the archer loses 97–100% under every variant: the fighter approaches in half cover and the archer's medium-range shots lose their first aim die.

### 3.3 Melee (B2c, B2d, B2x-b, B2x-d; both tactical, 400 trials)

The approach cost is the same stamina the first mover needs for its strike and for the blocks against the reply. Trace (notes §3): at 10 squares under one-square escalating the first mover pays 6 to arrive, strikes two steps (5) and has 3 left; the defender blocks for 3–7 and answers with a three-step strike into a near-empty pool. Under v0.9 at the same distance the first mover pays 2, strikes two steps and has 7 left to block with.

| Variant | Duel 8 apart (7 sq): cost → first mover | Duel 10 apart (9 sq): cost → first mover | Winner untouched (8 / 10) | 2v2: first mover, median rounds, off-turn squares |
|---|---|---|---|---|
| agi, flat (v0.9) | 1 → 58.7% [53.8, 63.5] | 2 → 56.7% [51.7, 61.5] | 80.5% / 84.8% | 64.5%, 4, 2.8 |
| agi, capped at Movement | 1 → 58.7% | 2 → 56.7% | 80.5% / 84.8% | not run |
| one square, flat | 1 → 58.7% | 3 → 55.1% | 80.5% / 82.3% | not run |
| agi, escalating slope 1 | 1 → 58.7% | 3 → 55.1% | 80.5% / 82.3% | 64.2%, 4, 2.8 |
| agi, escalating slope 2 | 1 → 58.7% | not run | 80.5% / — | 64.2%, 4, 2.8 |
| free 5, agi escalating | 1 → 58.7% | not run | 80.5% / — | 57.5%, 4, 2.2 |
| free 4, agi escalating | 3 → **49.0%** [44.0, 53.9] | not run | 81.9% / — | 50.4%, 4, 2.4 |
| one square, escalating | 1 → 58.7% | 6 → **38.2%** [33.5, 43.1] | 80.5% / 79.0% | 65.8%, 4, 2.8 |
| none | cannot → **28.9%** [24.6, 33.5] | cannot → **32.5%** [28.1, 37.3] | 64.1% / 62.2% | 57.7%, **7**, **56.0** |

Arriving with 13 stamina gives the first mover 58.7%; with 12, 56.7%; with 11, 49–55%; with 8, 38%; and when it cannot arrive, 29–33%. At the distance a duel actually starts (7 squares to contact) every priced variant but "free 4" charges 1 stamina, so they are literally the same fights on the same seeds. With no extra movement the first mover closes six free squares to distance two and the second mover steps in and strikes first with a full pool (trace: a 14-stamina four-step strike for 32 with two crits, incapacitating from full). Approach becomes the losing move and waiting becomes right, which the design notes list as the thing to avoid. In 2v2 the "none" variant turns fights into chases: 56 off-turn squares a fight, 7 rounds, 25 requests a round against 19.

### 3.4 Retreating to an ally (B2e, B2x-c; fleer tactical with retreat-when-engaged, ally 6 squares back, two tactical chasers, 400 trials)

| Variant | Fleer's side wins | First mover | Off-turn squares |
|---|---|---|---|
| agi flat (v0.9); one flat; agi escalating (slope 1 or 2); capped; one escalating | 30.8–31.5% ([26.4, 35.4] for v0.9) | 62–63% | 2.3 |
| free 5, agi escalating | 20.0% | 57.9% | 2.9 |
| free 4, agi escalating | 22.2% | 53.0% | 3.7 |
| none | **56.8%** [51.9, 61.5] | 88.4% | 6.7 |

Retreating to an ally only works when the chasers cannot buy the last squares. Lowering free movement hurts the fleer more than the chasers (it has six squares to cover to reach its line), so "free 4" is not a retreat-friendly change. Under "none" whoever acts first wins 88%.

1v3 (open and corridor): identical under every variant, because the attackers start within free movement.

## 4. Terrain, numbers and stats

### 4.1 Terrain with a tactical defender (B3a/b, 300 trials; fixed 2-step attackers)

| Terrain | Defender wins | Median rounds | Deaths per fight: windows on / off | Off-turn squares |
|---|---|---|---|---|
| Open 12×12 | 0% | 2 | 0.44 / 0.45 | 2.3 |
| Corner | 0% | 2 | 0.39 / 0.39 | 0.0 |
| Pillars | 0% | 2 | 0.46 / 0.45 | 1.8 |
| Door (defender behind a one-square gap) | 0% | 2 | 0.39 / 0.42 | 0.5 |
| Corridor, one square wide | 0% (3% draws) | 2 | **0.24 / 0.42** | 0.8 |

With pinning tactical attackers (B3b) every terrain is a one-round loss and windows cut deaths by 0.1–0.15 (open 0.42 vs 0.57; corridor 0.44 vs 0.59). Traces show why the corridor does so little for this agent: it steps out of the corridor mouth to attack, retreats off-turn (1 stamina plus 1 avoidance), steps out again and dies at 0 stamina when the second attacker enters the mouth; in another fight it charges out of the corridor to alpha-strike and dies in the open. The mouth square of a one-wide corridor is adjacent to three open squares; the one-at-a-time benefit begins one square inside, and the defender has to want to stay there.

### 4.2 A defender that holds its square (B3e, B3f, 300 trials; `hold = true`, attacks whatever is in reach)

| Terrain and square | Attackers win | Draws (20-round cap) | Median rounds | Deaths per fight | Attackers untouched |
|---|---|---|---|---|---|
| Open | 100% | 0% | 2 | 0.47 | 98% |
| Corner | 100% | 0% | 2 | 0.40 | 97% |
| Behind the door, corners `no_squeeze` (engine default) | 100% | 0% | 2 | 0.46 | 92% |
| **Behind the door, corners `no_cut`** | **64.7%** [59.1, 69.9] | **35.3%** | **9** | **0.19** | 95% |
| Corridor mouth (8,4) | 100% | 0% | 2 | 0.45 | 99% |
| **Corridor, one square in (9,4)** | **63.7%** [58.1, 68.9] | **36.3%** | **8** | **0.18** | 94% |
| …against tactical attackers | 72.3% | 27.7% | 5.5 | 0.12 | — |

Windows on or off makes no difference to any of these rows (the holder never moves). One square inside a corridor, only one attacker can reach the defender at a time, so the fight is three duels in sequence against a defender that carries its wear from one to the next; it never wins (0%), but a third of the time it is still standing when the round cap falls, and deaths per fight drop from 0.45 to 0.18.

The door is the same chokepoint or no chokepoint at all depending on one pending switch. Under the engine's default (`grid.corners = no_squeeze`: a diagonal step is blocked only when both orthogonal neighbours are walls) an attacker in the gap steps diagonally past the defender onto the squares beside it, because one of those neighbours is the defender, not a wall; three attackers engage within a round. Under `no_cut` (no diagonal past any wall corner) the gap is a corridor one square long and the door holds exactly as well as the corridor. The tactical defender benefits too (`no_cut`: attackers 93.0%, 7.0% draws, 5 rounds, deaths 0.28 against 0.39). Two holders side by side in the open against three attackers (B3e3) lose 100% in 4 rounds (tactical pair: 2 rounds), with 0.88 deaths instead of 1.30.

### 4.3 Numbers (B3c; equal sample fighters, tactical chip-kill, open ground, 300 trials)

| Match | v0.9: outnumbered side wins | No on-turn extra | Median rounds (v0.9 / none) | Off-turn squares (v0.9 / none) | Requests per round (v0.9 / none) |
|---|---|---|---|---|---|
| 1v1 | 53 / 46 | 50 / 49 | 5 / 5 | 0 / 0 | 11.5 / 11.3 |
| 1v2 | **0.0% [0.0, 1.3]** | 0.3% | 2 / 2 | 0 / 5.7 | 17.3 / 16.3 |
| 2v2 | 51 / 48 | 45 / 53 | 4 / 7 | 2.8 / 55.9 | 19.2 / 25.2 |
| 2v3 | **0.0%** | 7.3% [4.9, 10.9] | 2 / 5 | 4.0 / 76.6 | 34.7 / 41.4 |
| 3v3 | 51 / 48 | 48 / 51 | 4 / 7.5 | 6.0 / 94.8 | 30.6 / 49.8 |
| 2v4 | **0.0%** | 0.3% | 1 / 5 | 4.6 / 90.3 | 49.5 / 61.9 |
| 3v4 | 2.7% [1.4, 5.2] | 10.3% [7.4, 14.3] | 2 / 7 | 7.5 / 115.2 | 49.3 / 74.2 |

One body of advantage is decisive. The cause is the exchange economy, not movement: each attacker's attack resets the defender's block count, every defender shares one pool and one recovery, and a two-step attack costs about as much to answer as to make. Movement changes how long the outnumbered side lasts (five rounds instead of two when it can run) and barely the result. The first-mover column is 59–67% in every unequal match under v0.9 because most combatants are on the larger side.

### 4.4 Agility (B3d, 300 trials; AGI 5 defender: free 8, 4 squares per purchase, Melee Defense 5)

In the corridor the AGI 5 defender turns 3% draws into 13% and 0.24 deaths into 0.34 (it lives longer and dies more often than it is incapacitated); behind the door (default corners) it still loses 100%, with deaths 0.49 against 0.39 and attackers untouched 55% against 70%. Movement variants change none of these rows: the attackers start within free movement, and the defender's purchases never matter. Agility's movement value is a chase value, and 1v3 is not a chase.

## 5. How important movement is, and what the numbers suggest

**Movement is the second axis, and the system does not price it.** The exchange is deliberately symmetric and fully informed, so an equal duel on featureless ground has no decision that changes its expectation (Crit_Rule_Alternatives, Addendum 2). Whatever makes one turn different from another — who is engaged by how many, whether a shooter has a line, whether an ally is reachable, whether approaching costs the first strike — is position. The design's distinctive promise is that position is paid for in the same currency as attack and defense. The promise holds only if moving costs something at the margins that matter, and today it does not: 5–8 free squares plus one-stamina purchases make every engagement-range gap free to close and every retreat futile. Measured: duels have zero off-turn movement, 1v3 is decided before the defender's second turn on every terrain, windows are acted on in a few percent of asks, and the archer fight is decided by whether the fighter wins initiative. The game has a rich exchange economy and an almost free position economy, and fights are static after turn 1. In the designer's Starsector analogy, flux management is interesting because range and speed are contested; stamina management needs range to be contested too.

**The levers that actually move results.**
- *What the close costs out of the arriving creature's pool, at the distances fights start.* This is the lever the movement price pulls, and it works because the same 14 stamina pay for the approach, the arrival strike and the blocks against the reply. Each stamina of approach cost is worth a few points of first-mover win rate in melee (13 left: 58.7%; 11: 49–55%; 8: 38%), and against a fragile target it is a cliff at the last two-step strike. Under v0.9 a 7–9 square close costs 1–2, which is why nothing measured in melee changes between the priced variants; "free 4 + escalating" is the one variant that charges 3 at a duel's starting distance, and it brings the first mover to 49% — approach neither free nor suicidal — at the price of hurting retreats (22%) and giving the archer 43%.
- *Turns to close.* A threshold. When one turn suffices, the fight is static after it; when it does not, range exists (archer 43–53%), approach becomes a liability (first mover 29–33%), windows become the chase (56–115 off-turn squares a fight), retreating to allies works, fights lengthen, prompts double. The dial is free movement against typical starting distance and map size — and lowering free movement alone hurts retreat as much as pursuit.
- *Whether terrain is a chokepoint.* Decided by the corner rule before the map: a one-square door is nothing under `no_squeeze` and a corridor under `no_cut`. Then by the defender: the chokepoint pays only for one who holds it.

**What movement cannot do.** It cannot make a numbers disadvantage survivable (1v2, 2v3 and 2v4 are 0%), and it cannot save an open-ground defender from three attackers under any window rule. Those are exchange-economy facts (per-attack block resets, shared pool and recovery). Movement can decide where a fight happens, and that pays only for a defender who holds real terrain.

**Options for the designer, in the order I would test them.**
1. *Window order:* adopt the declaration scheme (descending initiative; after any move, anyone may move again). Outcomes are the same as the current rule within noise; its property — higher initiative gets the choice to pre-empt or react — is the right one; the rules text is one sentence and needs no pre-declared movement order. Cost: more questions in a contested window. Per-segment resolution is optional on top: adopt it only if Agility should be the chase stat (it decides the micro-race, and makes the order rule matter more) and the extra prompts are acceptable.
2. *Prompt scope:* before any playtest, decide who gets asked. "Not after allies' turns" removes a third of off-turn prompts in team fights at no cost; "only creatures within N squares of the creature whose turn ended, or who were attacked during it" would remove more and is the next thing to measure. Fifteen questions a round with one answer in thirty mattering is how a table learns to skip a rule.
3. *Corners:* rule on `grid.corners`. It is in the assumptions register as pending, and §4.2 shows it decides whether a doorway is a position worth holding. `no_cut` is the reading that makes doors, gaps and corners matter; it also makes corridors around corners slower for everyone.
4. *On-turn extra movement:* decide what a close should cost at 7–9 squares, not the formula. One stamina (v0.9) is invisible; three brings the first mover to even; six makes approach a loss. Among the formulas, flat and escalating are identical within three purchases, the cap never binds, and "one square per purchase" (F10 option 1) is the only one that changes prices at ordinary distances — and at 11 squares it prices the archer out of reach (53%). If archers and kiting should exist, typical engagement distances must take two turns to close for an AGI 1 fighter (free 4–5 with escalation, or one-square purchases), with bounded or terrain-rich maps so the kite ends. If approach must not be suicidal (the design notes' p.762 worry), the counterweight is a strike budget that survives the close: a cheaper first purchase, a smaller first-step surcharge after moving, or reach weapons with teeth (F9). "None" is the extreme: it gives archers and retreats a game and makes the open-field approach a loss and the kite unbounded.
5. *Dogpiling:* stop looking for a movement fix. Holding real terrain is the only movement answer (§4.2), and the real levers are the exchange economy's (block count reset per attacker per round, F6 option 2; the numbers curve) and encounter design (NPC profiles, counts).

## 6. Engine changes (branch `exp/movement`, patch attached)

- `movement.extra_mode`: `flat` (v0.9), `escalating` (nth extra purchase costs `extra_cost` + `extra_slope`×(n−1), on the existing `extra_purchases` tracker, like attack steps), `none`. `Pricing.extra_movement` takes the trackers.
- `off_turn.restart_after_move`: a pass restarts from the first creature in order after any move. With `order = descending_initiative` this is the designer's declaration scheme. `off_turn.purchase_cap = 1` on top gives per-segment resolution.
- `off_turn.scope`: `all` (as written) or `not_after_allies` (no prompt after an ally's turn; you still move after your own turn and after enemies'). A load experiment, not a packet reading.
- Tactical agent: `off_turn = "retreat" | "pin" | "retreat_pin"` with `pin_budget` (close off-turn to a square that threatens the target), and `hold = true` (never move on your turn; attack what is in reach).
- Assumptions register: three rows added, all pending the designer. (`grid.corners` was already there, pending.)
- Tests: `tests/golden/test_movement_variants.py` (pricing of the three modes; the restart order's question sequence); `component_defaults.json` records the new defaults, so the preset digests are unchanged. The fast suite passes from source (`PYTHONPATH=src python3 -m pytest`), `mypy --strict src` and `ruff check src tests examples` are clean.
- Scripts: `experiments_movement.py` (every B-series run: `python3 -u experiments_movement.py B1|B1n|B2|B2rest|B2x|B3|B3e|B3f [trials]`), `window_race.py`, `window_load.py`; raw results and console logs under `reports/movement_exploration_results/` (the AGI 5 build is `builds/l1_agi5.toml` there).
- Known test-environment note: `tests/properties/test_no_hypothesis.py` fails in a source-only checkout because its subprocess replaces `PYTHONPATH`; it passes with the package installed. Unrelated to these changes.

Three agent limitations to keep in mind when reading any of this: the tactical defender leaves terrain to attack; the pin heuristic spends off-turn stamina on a trade that loses on open ground; and no agent kites pre-emptively or waits-then-reacts in a window. Human sessions (`se play`) on the corridor, door and archer scenarios would be the right next measurement.
