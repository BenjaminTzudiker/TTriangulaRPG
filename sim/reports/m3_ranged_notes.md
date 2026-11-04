# M3 ranged: notes on the suite

Companion to `m3_ranged.md`, which `se suite ranged --workers 8 --trials 500` generates. It ran on commit 85c6aab (clean). The fight figures are 500 trials a row with 95% intervals; the single-shot tables are exact. Rows in one group share seeds, so differences within a group are paired.

Two agent families played. Read differences between them as agent effects:
- **Scripted:** the archer takes 3 aims and stands; the fighter approaches with free movement only.
- **Tactical:**
  - The archer picks its aims by exact expected value, looking one enemy reply ahead. It steps out of reach, readies its quick-draw blade between turns, and dives.
  - The fighter buys movement when that lets it attack this turn, prefers squares with cover from the archer, and dives.

## What the M3 gate checked

- **Review Table 5's static part, exactly:** all 96 printed figures (8 shots × 4 targets × stamina, injury and % down) agree with the exact values. Each is within its printed rounding plus three standard errors of the review's 4000 rolls. `se table 5` prints the comparison, and `tests/golden/test_ranged_static.py` pins it.
- **The archer scenario on three maps** (open ground, scattered cover, a wall line with gaps), for both agent families.
- **Ranged golden battles:**
  - The packet's two aimed longbow shots (20 stamina).
  - Range bands: misses with too few aims, and aim dice dropped at medium and long.
  - No shot beyond long range or into total cover.
  - Half cover added to defense.
  - Point-blank shots blocked with Melee Defense, followed by OAs that can't be paid off.
  - A dive behind a wall counting as three-quarters cover.
  - The drawing rules.
- **Cover geometry tests,** and random play on random maps with archers and every ranged variant.
- **Nothing earlier changed:** M1's lockstep parity is still identical, and the pinned M1 and M2 logs are byte-identical to the `m2-grid` tip apart from the RuleSet digest.

## For the designer

### 1. Buying movement settles the archer fight in one turn (F10, measured)

Archer against an approaching sample fighter, 12 squares apart on open ground:

| Archer and fighter | Archer wins | First mover wins |
|---|---|---|
| Scripted archer, scripted fighter (free movement only) | 50% | 40% |
| Tactical archer, scripted fighter | 57% | 45% |
| Tactical archer, tactical fighter (buys movement) | 24% | 77% |

The tactical fighter crosses 12 squares in one turn (6 free plus three purchases at 1 stamina each) and strikes before the archer's second shot.

Against an unshielded two-handed duelist the fight is decided by initiative: the first mover wins 100% of fights, in one round, whoever it is.

This is Review F10's "the archer scenario is settled on turn 1 or never", measured on a grid. Range bands barely enter into it, and the archer's kiting can't outrun flat extra movement. Phase 4's F10 decision decides whether archers have a game at all on open ground.

### 2. Map cover is the strongest input

Same pairings, the archer's win rate by map:

| Map | Scripted archer, scripted fighter | Tactical archer, scripted fighter | Tactical archer, tactical fighter |
|---|---|---|---|
| Open ground | 50% | 57% | 24% |
| A wall line with gaps | 34% | 35% | 1% |
| Scattered cover | 1% | 2% | 0% |

With cover between them, the fighter approaches in half cover (+2) most of the way. It also dives when shot (0.48 dives a fight on the wall line). The archer's medium-range shots lose their first aim die. Archers lose almost everywhere except open ground, where they win only if the fighter won't buy movement.

That is the review's Appendix B point ("map cover is one of the biggest lethality inputs"), now with numbers. It cuts both ways for F3: shield-less targets are helpless in the open, and archers are helpless against a fighter with cover.

### 3. F3's options, exactly on single shots, and in a fight

Single shots, from the exact tables in the report:
- **Option 1 (Dodge folded into RD)** changes nothing for any of the review's Table 5 targets: all have Agility 1, and only even Agility adds. It helps the Agility-2 duelist; for example, a longbow with 1 aim at short range: 79% down unfolded, 29% folded.
- **Option 2 (flat 2 per ranged perfect block)** lowers injury for unshielded targets, but they spend their whole pool doing it. Unarmored against a shortbow with 1 aim: 12.4 → 8.7 HP and 72% → 58% down, at 12 stamina spent.
- **Option 3 (aim as precision)** cuts injury the most. Shortbow, 1 aim, against the unarmored target: 12.4 → 4.0 HP. Longbow, 2 aims, against the shielded fighter: 3.3 → 0.0 HP.

In the archer-against-duelist fight (both tactical), on paired seeds:
- **Option 3** halves the archer's wins: 49% → 25%.
- **Options 1 and 2, and F11 (b)'s band reading,** leave it unchanged: 49%. The duelist dies to the first shot either way, or reaches the archer first.

### 4. Point-blank shooting and drawing work as written, and agents use them

The tactical archer readies its blade between turns whenever the fighter could reach it, and re-draws its bow on its turn for free. It also pays to step out of reach before shooting, so its shot doesn't provoke and isn't blocked with Melee Defense.

No agent has yet found a reason to shoot point-blank on purpose.

## Readings added in M3, all pending your ruling

All are in the Assumptions register with their switches:
- **Cover lines** (5e corner method): touching a corner or running along an outside edge doesn't block; a low wall can't give total cover; creatures give half at most.
- **Range bands:**
  - A shot with too few aims for its band is still paid for, misses, and still provokes.
  - Shots beyond long range aren't offered.
- **Aim steps** add Finesse after armor penalties.
- **The dive:**
  - It's one off-turn move after the roll, provoking OAs as any move does.
  - Cover is measured from the new square; range and sight aren't rechecked.
  - Point-blank status is judged after the dive.
- **Point-blank OAs:** every enemy threatening the shooter, lowest initiative first, after the shot resolves.
- **Drawing:**
  - Loadout switches, priced per newly drawn item.
  - After a bow shot, no normal item can be drawn until your next turn.
  - Drawing between turns happens in the off-turn windows.
- **F3 option 3 and F11 (b),** as built:
  - Precision: each aim step widens the shot's critical range by 1.
  - Bands: −1d6 at medium and −2d6 at long, with no minimum aims.

## A change to M2's scripted agents

Scripted agents on a map now approach even when they can't afford to attack this turn; only the `never` policy stands still. In M2 they stood still at 0 stamina, which left melee chasers stranded by an archer's opening shot.

The M2 report's figures came from the M2 commit and still reproduce there. On this branch, M2 scenarios where a scripted agent drains to 0 stamina before contact will differ slightly.
