# Phase suite: notes (M4)

Companion to `phase_suite.md`, which `se suite phase --workers 8 --trials 300` generates. It ran on commit b3c984b (clean): 300 trials a fight row, 95% intervals in the tables that print them. Fights are on maps with movement, off-turn windows and OAs. Duels start adjacent on open ground.

## What the M4 gate checked

- **The full phase suite runs in one command,** printing Tables 1, 5 and 8 exactly, Table 2's policy matrix, Table 3's level summary, Table 4's 1v3 layout and Table 7's armored-against-unarmored layout. It also runs the archer, reach, retreat and 3v3 items.
- **Review F4's and F8's options can be selected:** variant equipment tables (`data/equipment/`, `se table --equipment`) and RuleSet switches (`surcharge.light_exempt`, `defenses.two_hander_bonus`, `defenses.agility_split`), each tested.
- **NPC profiles** (`data/profiles/`), fleeing through exits and surrendering all work in play (`tests/golden/test_leaving_the_fight.py`), and random play on random maps, now with exits and NPC profiles, never breaks an invariant.
- **Nothing earlier changed:** M1's lockstep parity is still identical, and the pinned M1–M3 logs are byte-identical to the `m3-ranged` tip apart from the RuleSet digest.

## For the designer

### 1. Table 7 reproduces on a grid; F4's options close the shield's gap

The armored side's win %, alpha / chip-kill / 2-step:

| Pairing | Review (no grid) | v0.9 on a grid | F4 option 1 (shield +1 / +2) | F4 option 2 (two-hander +1, Agility split) |
|---|---|---|---|---|
| L1 heavy + shield v duelist | 79 / 88 / 87 | 82 / 88 / 88 | 54 / 54 / 58 | 68 / 74 / 77 |
| L1 sample v duelist | 80 / 86 / 85 | 80 / 87 / 85 | 61 / 61 / 68 | 72 / 76 / 78 |
| L1 sample v two-hander | 73 / 74 / 86 | 72 / 72 / 87 | 61 / 61 / 72 | 63 / 63 / 70 |
| L1 sample v greatsword | 77 / 78 / 84 | 73 / 73 / 82 | 57 / 57 / 63 | 63 / 63 / 66 |
| L30 heavy + shield v duelist | 63 / 64 / 78 | 64 / 64 / 81 | 59 / 59 / 48 | 54 / 55 / 68 |
| L30 sample v duelist | 70 / 70 / 82 | 72 / 72 / 83 | 60 / 60 / 59 | 58 / 57 / 75 |

F4's finding ("the shield's +2 dominates") holds on a grid. Option 1 (+1 Melee) brings most pairings to 54–68%; option 2 to 57–78%.

At L1, alpha and chip-kill give the same figures. With exact estimates, a level-1 full strike (6.1 HP against 8) always passes chip-kill's half-HP test, so chip-kill goes all in.

### 2. NPC commitment is the lethality dial (Review F6), and terrain only matters at low commitment

1v3, where each cell is the defender down / its deaths per fight / rounds:

| Attackers' profile | Open ground, tactical defender | Corridor, tactical defender |
|---|---|---|
| minion (1 step, focus fire) | 100% / 0.32 / 4.1 | 56% / 0.16 / 12.2 |
| disciplined (2 steps; 3 against low stamina) | 100% / 0.65 / 1.3 | 98% / 0.48 / 2.8 |
| berserker (all in) | 100% / 0.57 / 1.0 | 100% / 0.57 / 1.0 |
| cautious (chip-kill, flees, surrenders) | 100% / 0.56 / 1.0 | 100% / 0.47 / 1.2 |

Against 1-step attackers, the corridor lets the defender survive 44% of fights over about 12 rounds. Against 2-step or all-in attackers it buys at most a round and a half. That is F6's point ("NPC step count decides it"), measured with movement and terrain in play.

### 3. A 3v3 mixed party wins only against 1-step NPCs

A tactical party (fighter, duelist, archer) against two sample fighters and an archer:

| NPC profile | Party wins | Rounds |
|---|---|---|
| minion (1 step) | 64% | 8.5 |
| cautious | 43% | 4.4 |
| berserker | 42% | 4.6 |
| disciplined | 36% | 4.9 |

The NPCs' profile moves the party's chance from 36% to 64%, more than any rule variant in this suite.

### 4. Duels by level, with movement in play

Same pattern as the review's Table 3:
- **L1:** the first mover wins 72%, in about 7 rounds.
- **L30:** 67–69%, in 11–12 rounds, with 5–9% draws.
- **L99:** 84–87%, in 1.5 rounds (F5: the full strike kills).

In the L1 policy matrix every policy is within 42–51% of every other: no dominant strategy, as in the review.

## Readings added in M4, all pending your ruling

All are in the Assumptions register:
- **F8 option 1 (die upgrades):** the greatsword drops its multiplier too (1d12 + STR + FIN), alongside the review's greataxe (2d6 + STR + FIN); base costs are unchanged.
- **F8 option 2:** the dagger and shortsword are the "light" weapons (tagged in the table).
- **F8 option 3:** Strength is capped at the weapon's largest die.
- **F4 option 1's Strength-gated shield:** a requirement of 2 is my guess; the review gives no number.
- **F4 option 2's Agility split:** Dodge (and folded Ranged) count Agility one step finer than Melee.
- **Surrender:** on your own turn. Fleeing: from an exit square (`>`) on your own turn. Both leave the creature out of the fight.
- **NPC profiles** are agent configuration, not rules (the packet leaves them out of this version).
