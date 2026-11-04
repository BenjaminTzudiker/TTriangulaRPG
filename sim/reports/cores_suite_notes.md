# Cores suite: notes (M5)

Companion to `cores_suite.md`, which `se suite cores --workers 8 --trials 300` generates. It ran on commit 3f54432 (clean), RuleSet v0.9 (digest 89e49ba8c42d): 300 trials a row, with 95% intervals.

Each ability is played off and on over the same trial seeds, so each difference is paired. Each build is the sample fighter's stats with one core, or with no core and one candidate ability. Duels start adjacent on open ground, against the sample fighter with its own core unused (Heavy Swing faces the heavy-armor build). One against three is Phase 3's open-ground layout. The policies that decide when each ability fires are simple, documented heuristics (`agents/ability_policy.py`). A fight starts at 0 strain, so these are best cases for a day of several fights.

## What the M5 gate checked

- **Class cores priced in sims:** all four cores and the three buildable candidate abilities, off and on, in duels and one against three for both agent families, plus the four cores against each other.
- **The human CLI:** `se play` plays a side at the keyboard with timed decisions and writes a session log; `se load --session` reports it. Both are tested with scripted input and a fake clock. **Still open: one session played by a person.** That needs you (see "For the designer", item 5).
- **Nothing earlier changed:** M5 touches no rule component, and the pinned M1–M4 logs are byte-identical, digest included.

## For the designer

### 1. Every ability is worth a lot in an equal duel

Turning the ability on (A's win rate, change in percentage points):

| Ability | Duel win | Uses per fight |
|---|---|---|
| Fighter core | +30 [+25, +35] | 1.0 |
| Barbarian core | +26 [+21, +31] | 2.4 |
| Monk core | +35 [+30, +40] | 1.5 |
| Rogue core | +20 [+15, +24] | 0.5 |
| Heavy Swing (against heavy armor) | +25 [+20, +31] | 2.4 |
| Tactical Withdrawal | +52 [+46, +57] | 1.3 |
| Riposte | +9 [+5, +12] | (an OA, not counted) |

Each core takes an equal duel from 46% to 65–81%. That's 1 AP at level 1, within 6 strain.

**One against three, no ability changes the outcome:** the defender is always down. The most any ability buys is about half a round: Fighter +0.5–0.6, Monk +0.4–0.5, Tactical Withdrawal +0.6. Three abilities shorten the fight slightly instead:
- Rogue: −0.35 rounds for the tactical defender. Jumping in moves its turn earlier.
- Riposte and Heavy Swing: −0.1 to −0.2 rounds. Riposte's OAs spend stamina that would have gone on blocks, and Heavy Swing's +1 a step does the same, against attackers in only medium armor.

### 2. Tactical Withdrawal is the outlier, and the number rests on my reading

With Withdrawal on, A wins 97% of duels instead of 46%, using it 1.3 times a fight. The reading in the register is that if the attacker no longer reaches you after the move, the attack is avoided, already paid for.

So 2 stamina cancels an attack its maker paid 5–14 stamina for. The attacker's next turn goes on walking back.

The packet says only "2 stamina to move before an attack resolves". Readings that would price it differently:
- The move comes before the attacker declares steps, so it keeps its stamina.
- An attacker with reach left can follow.
- The cost scales with the attack's steps.
- Withdrawal counts as an off-turn cost.

Worth deciding before it goes in a tree.

### 3. Core against core: the Barbarian edges every core, and the Rogue trails

The report's matrix gives A's win rate with both sides using their cores. Averaged over both seats, each pairing comes out as follows. Each cell is the row core's wins against the column core; draws are the rest.

| Core \ against | Fighter | Barbarian | Monk | Rogue |
|---|---|---|---|---|
| Fighter | mirror | 46% | 34% | 60% |
| Barbarian | 54% | mirror | 57% | 53% |
| Monk | 56% | 39% | mirror (44% draws) | 88% |
| Rogue | 40% | 47% | 6% | mirror |

- **The Barbarian** wins a little over half against every other core. Its fights are short (2–4 rounds), except against the Monk (7.5).
- **The Monk** beats the Fighter and crushes the Rogue (88%), but loses to the Barbarian. Two Monks stall: 44% draws, 21 rounds on average, many ended by the 30-round cap. Flat perfect blocks make defending cheap.
- **The Rogue** loses to every other core: 40% against the Fighter, 47% against the Barbarian and 6% against the Monk.
  - At level 1 its jump buys initiative at most twice a fight (3 strain each), and the new slot stays.
  - In a duel that's one round of first-mover advantage, and it is first half the time anyway: 0.5 uses a fight.

### 4. The cores make fights shorter, except the Monk's

With one side using its core, duels last:
- Fighter: 3.4 rounds, against 6.7 without.
- Barbarian: 2.8 rounds.
- Monk: 10.2 rounds, with 8% draws.

Flat perfect blocks (Monk) lengthen fights; recovering (Fighter) and refunding steps (Barbarian) shorten them, because the stamina goes into bigger attacks.

### 5. Decision load and the human session

`se load` on four scenarios (`m5_load.md`), engine agents, per creature-round:

| Scenario | Decisions | Off-turn windows (of which acted) | Ability windows |
|---|---|---|---|
| L1 duel, open ground | 5.7 | 1.8 (0%) | 0.6 |
| 1v3, open ground | 7.2 | 3.4 (4%) | 0.5 |
| Archer among scattered cover | 6.3 | 2.2 (14%) | 0.5 |
| 3v3 party on a terrain map | 5.0 | 2.5 (3%) | 0.4 |

By option count nearly every request is non-trivial. A turn offers 80–140 options once every reachable square counts, and blocks offer 18–28 affordable pairs.

**Off-turn windows are the biggest share of the load** (Review F14 and F11), a third to a half of it: 1.8–3.4 asks per creature-round, and the engine agents move in at most 14% of them. Whether people pass that often is the question a human session answers.

**Ability windows add about half a request per creature-round.** For example, the sample fighter's core is offered before every block once it is below maximum stamina. So M1–M4 decision counts rise in M5 for builds with a core. The rules and the logs are unchanged; it's a new request.

To log the session the gate needs, play one side of a scenario:

```bash
uv run se play src/stamina_engine/data/scenarios/l1_duel_open.toml --as A --log reports/session_1.jsonl
uv run se load --session reports/session_1.jsonl
```

The CLI prices each option and lists the blocks worth considering. That's arithmetic a player at a table does in their head, so its seconds are a lower bound on table time.

## Readings added in M5, all pending your ruling

All are in the Assumptions register:

- **Ability windows:** abilities fire only at the engine's timing windows:
  - on your turn, between actions;
  - in an off-turn window;
  - before blocks;
  - between turns;
  - as your turn would begin;
  - as you declare a melee attack;
  - in a melee attack's reactions step.

  "At any time" means your turn, off-turn windows and before blocks.
- **Fighter core:** offered only below maximum stamina, any number of times; the overage costs stamina.
- **Barbarian core:** refunds the biggest step paid this turn not yet refunded. OA steps don't count.
- **Monk core:** chosen before blocks; every perfect block against that attack costs what the first would.
- **Rogue core:**
  - It can jump in between any two turns, including before the round's first.
  - It can wait at its turn's start, choosing again at every later gap for free.
  - The order turns were actually taken becomes next round's order.
- **Heavy Swing:** chosen as you declare: +1 stamina a step, 2 more armor ignored.
- **Riposte:** an OA on the attacker after at least one perfect block, priced and capped as any OA.
- **Tactical Withdrawal:** see item 2.
- **Candidate abilities** are listed on a build and don't count against the AP budget yet.
- **The control-track stub:** a progress track per effect, pushed back 1 per stamina. What progress does waits for Phase 7.
- **Engine conventions, not rules:**
  - Strain starts at 0 every fight.
  - Engine agents use abilities only when their spec opts in.
  - The CLI's arithmetic help, described in item 5.
  - The load report's denominators.
