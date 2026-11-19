# Playing test fights by hand: rules, tool, and what to report

You are playing fights of a tabletop RPG under design, on a rules engine, to find out how one
new rule (the **hold**) behaves in real fights. You play **both sides**, each as well as you
can. The designer wants insight, not a winner: what the rule made creatures do, which
decisions it created or removed, and where it broke.

Work only inside your own folder (given in your task). Do not edit `table.py`, the engine, or
any repository. Do not push anything anywhere.

## 1. The rules the engine plays (level-1 creatures)

**Resources**
- **HP.** At 0 or below a creature is down and out of the fight.
- **Stamina.** Maximum = 6 + current HP, so wounds shrink it. You recover 4 at the end of
  your own turn. Attacking, blocking and dashing all spend it. "Ready" stamina is what you
  can spend right now.
- **Escalation.** Every action costs its base **+1 for each action you have taken since your
  last turn ended**. Actions are: each melee attack step, each dash, a shot, each aim step.
  It goes back to 0 when your turn ends. So a dash before your turn makes that turn's attack
  steps dearer.

**The round.** Creatures act in a fixed initiative order. **Before every turn, including the
first, there is a dash phase** in which anyone may dash. On your turn you have **6 squares of
free movement** (split it as you like), and may attack, dash, shoot or draw. When you end
your turn: escalation resets, any tokens you have out come back, you may set holds, then you
recover 4 (holds below).

**Dash.** An action: 1 + escalation, moves up to 2 squares. Any number, on your turn, in a
dash phase, or when you are the target of a shot.

**Melee attack.** Choose a target in reach and a number of steps, and pay for all of them at
once. Step costs: weapon base + escalation, rising by 1 per step (a fresh longsword: 2, 3, 4,
5). Each step rolls the weapon's damage; a die showing one of its top two faces is a critical die
(top face only for the Finesse-0 spearman).
The defender sees the total, then **blocks**: every block stops its Melee Defense in damage.
Perfect blocks cost 1, 2, 3, ... within one attack. Grazing blocks cost 1 each, but each
leaks 1 damage. What is left meets armor (minus 1 per critical die). If anything gets
through, the defender loses that much HP, +1 per critical die.
- Several steps in one attack are much harder to block than the same steps in separate
  attacks. A creature with no ready stamina takes everything.
- **The tool blocks automatically** with the engine's block solver (it weighs 1 HP as 3
  stamina and never accepts a knock-down it can avoid). You can force a different choice for
  one attack by adding `blk=P,G` to the attack order if the automatic one would clearly be
  wrong for that creature's plans.

**Leaving a threatened square** (any square in an enemy's melee reach), by any movement,
gives that enemy a trigger. For each such enemy, as you leave each such square, you either
**pay it off** (1 stamina; not an action) or it may make an **opportunity attack**.

**Opportunity attacks under the two rule sets:**
- `exp-0.11.0` (the current packet's placeholder): exactly **one step at the weapon's base
  cost**, whatever its escalation. No holds exist. Paying off always costs 1.
- `exp-holds` and `exp-holds-next-turn` (the rules with holds): steps cost base, base + 1, base + 2 ... (a fresh count
  for each opportunity attack; never an action). The whole attack must fit a **budget = cap +
  tokens**, where the cap is 1 + 1 per odd Finesse value (**2** for the sample fighter, the
  greatsword fighter and the archer; **1** for the Finesse-0 spearman), and tokens are that
  attacker's hold on you. So with no hold a longsword (base 2) gets one step, and a
  greatsword (base 3) or the Finesse-0 spear (base 2, cap 1) gets none.

**Holds (rule set `exp-holds-next-turn`, the version under test).**
- At the end of your turn, in this order: (1) any tokens you have out come back to your ready
  stamina, and all your holds end; (2) you may set any of your ready stamina aside as
  **tokens** on enemies within your reach (any split); (3) you recover 4, but your ready
  stamina plus your tokens can't go above your maximum.
- Tokens are not ready stamina: you can't block, dash or attack with them, **including on your
  own next turn**. They stay out until the end of your next turn, when they come back (step 1
  above) and you can set new holds.
- While a hold is on you: the first square you leave inside that holder's reach costs **1 +
  its tokens** to pay off. If you don't pay, its opportunity attack has budget cap + tokens,
  and tokens are spent first. Either way that hold then ends (unspent tokens stay out until
  they'd come back anyway), and further squares cost 1 again.
- A hold lasts until the end of the holder's next turn. If the holder goes down, it ends.
- **The trade:** a hold costs nothing if it's never used, except that until the end of your
  next turn you have that much less ready stamina, both to block with and **to attack with on
  your next turn**. A small hold is cheap; a big one costs most of your next attack.

**Ranged (only in fights with archers).**
- The archer has two loadouts: `bow` (longbow; Melee Defense only 1 while holding it) and
  `blade` (shortsword, base 1, 1d6 + 2; Melee Defense 3). Drawing is free on your turn until
  you use a weapon; between turns (in a dash phase) drawing the blade is free
  (`W| C d blade`), and drawing the bow costs 1.
- A shot costs 4 + escalation and rolls 1d8 + 1 plus one free aim die (1d6). Each aim step
  (1 + escalation) adds 1d6. Range: no penalty within 4 squares, then -2 to the total per
  further 4 squares.
- After the roll the target may dash (+1 defense against that shot for moving; half cover
  +1, three-quarters +2; ending fully behind cover counts as three-quarters). Then it blocks
  with **Ranged Defense** (2 for the shielded fighter, 1 for others) plus cover; blocks cost
  the same as in melee. Armor applies. **The wound is capped at the bow's own damage roll**
  (the d8 + 1), +1 per critical die: aim makes a shot harder to block, never bigger.
- Shooting while inside an enemy's reach gives each such enemy an opportunity attack after
  the shot, and it can't be paid off. With holds, the enemy may spend hold tokens on
  it; the hold shrinks by what was spent and stays if any tokens remain.

**The creatures** (see the table printed by the tool for live numbers):

| Build | HP | Stamina | Melee Def. | Ranged Def. | Armor | Weapon |
|---|---|---|---|---|---|---|
| Sample fighter | 10 | 16 | 3 | 2 | 2 | longsword, base 2, 1d8 + 3, reach 1 |
| Greatsword fighter | 10 | 16 | 2 | 1 | 2 | greatsword, base 3, 1d12 + 5, reach 1 |
| Spearman (Finesse 0) | 10 | 16 | 3 | 2 | 2 | spear, base 2, 1d8 + 2, **reach 2**, cap 1 |
| Archer | 8 | 14 | 1 (bow) / 3 (blade) | 1 | 1 | longbow 4 per shot / shortsword base 1 |

Not in these fights: class abilities (the Fighter's "recover 4 now" is switched off), spells.

## 2. The tool

Everything is run from your folder with `./go.sh FIGHT 'order' 'order' ...`. It adds the
orders to `FIGHT.orders`, replays the whole fight from the start (it is deterministic: same
orders, same dice) and stops at the first decision with no order, showing what happened
since your last run, the map, a status table and the decision with its options and odds.
`./go.sh FIGHT` with no orders shows where the fight stands. `BOARD=0 ./go.sh ...` hides the
map. If an order doesn't fit, it says `ORDER PROBLEM`, explains, and **adds none** of that
call's orders: fix them and run again. To take back accepted orders, delete lines from the
end of `FIGHT.orders` and delete `FIGHT.seen`.

Squares are `x,y` (x across, y down, both from 0; the map shows the digits). Creatures are
single letters. On the map: `#` wall, `o` pillar (blocks movement and sight), `=` crate (low
cover, blocks movement), `>` exit, lower-case letter = a creature that is down.

**Orders** (one string per creature; `|` separates parts):

| Order | Meaning |
|---|---|
| `X| m 5,4` | Move to 5,4 by the route that leaves the fewest threatened squares. `m 5,4 6,4 7,5` gives an exact path. Add `pay=all`, `pay=none` or `pay=A,B` to settle every pay-off decision during that move in advance. |
| `X| a Y 2` | Attack Y with 2 steps. (`X| a Y` alone makes the tool show the odds for each number of steps; then answer `X| 2`.) |
| `X| e` | End the turn, no holds. `X| e Y:4 Z:2` ends it and puts 4 tokens on Y and 2 on Z. |
| `X| pay Y` / `pay all` / `pay none` | Answer a pay-off decision when the tool asks. |
| `X| oa 2` | Make an opportunity attack of 2 steps (`oa 0` declines). |
| `X| s Y 1` | Shoot Y with 1 aim step. `X| d blade` draws a loadout. |
| `X| stay` or `X| m 3,3` | When shot at: stay, or dash there first. |
| `X| flee` | On an exit square: leave the fight. |
| `W|` | A dash phase in which nobody dashes. |
| `W| Y m 12,4 pay=all | X m 9,4` | Dashes in a dash phase, in that order. A dash that needs more than 2 squares buys as many dashes as needed. |

Several parts can go in one order: `X| m 17,4 | a A 3`, then after seeing the result
`X| e A:5`.

**Dash phases.** If you have no orders queued when a dash phase opens, the tool stops and
asks. Answer `W|` (nobody) or list dashes. If you queue a turn order without a `W|` line
before it, that dash phase is skipped: do that only when you have decided nobody dashes.
Reactions that come up inside a dash phase (pay-offs, opportunity attacks) are answered with
ordinary orders after the `W|` line.

**Reading the status table.** `ready/max` is ready stamina and its maximum; `esc` is the
escalation right now; `tokens out` shows holds as `target:tokens` (and idle tokens that will
return). The odds tables assume the defender blocks as the solver would with its ready
stamina.

`./go.sh FIGHT` also writes `FIGHT.log`, the whole fight so far in words.
`python3 table.py FIGHT --odds A Y` prints A's attack and opportunity-attack odds against Y
at the current point.

## 3. How to play

- Play both sides to win their stated goal. Before each turn's orders, think of at least two
  plans for the creature and pick the better. Don't steer the fight toward a result.
- Use the dash phase when it helps: backing off before an enemy's turn makes it pay dashes
  (and dearer attack steps) to reach you; closing before your own turn costs escalation.
- Concentrate attacks: the second attacker meets a drained defender.
- What you keep after attacking is all you can block with until your next turn (+4).
- **Holds:** consider one whenever an enemy is in your reach at the end of your turn. Ask:
  does this enemy want to leave (to flee, to reach someone else, to get range)? Who can
  attack me before my next turn, and what do I need to keep to survive that? And what do I
  want to attack with next turn, since the tokens won't be available then? A hold that
  leaves you at 0 ready invites every enemy in range. A hold on an enemy that never meant to
  move does nothing.
- **When held:** compare (a) paying 1 + tokens, (b) leaving unpaid and blocking the attack
  (the tool shows its budget), (c) staying and hitting the holder, who has little ready
  stamina, (d) staying and doing something else. Allies can also attack the holder.
- Keep a file `NOTES.md` in your folder: for every turn, one line saying what the creature
  did and why, and for **every hold set and every decision made because of a hold**, what
  the options were and why you chose as you did. Short lines are fine.

## 4. What to send back

A report in plain language, at most about 800 words per fight, with:
1. The setup you played (file, rule set) and how it ended (who is up, HP, in which round).
2. **Every hold that mattered**: who held whom with how many tokens, what the target did
   about it, and what it cost each side. Then the holds that didn't matter and why.
3. Moments where a creature wanted to move and the hold changed what it did (or, under
   `exp-0.11.0`, where it simply paid 1 and left).
4. Moments where holding made the holder pay for it.
5. Whether choosing tokens was a real decision or had an obvious answer, and how much
   arithmetic and tracking it took at the table (count things if you can).
6. Anything that looked degenerate, dominant, unfun or implausible, with the turn it came
   up. Also anything in the rules digest that the engine seemed not to follow, and any tool
   trouble.
7. What you are unsure of.

Say plainly what you saw. A fight is one sample: don't generalize beyond it, and mark
guesses as guesses.
