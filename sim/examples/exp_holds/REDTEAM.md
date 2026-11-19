# Red team: try to break the hold rule

Read `BRIEF.md` first: it has the rules the engine plays, the tool and the order syntax.

Your job is different from playing a fair fight. **Find the ways the hold rule (`exp-holds`)
can be abused, becomes automatic, or produces something a designer wouldn't want**, and show
each one with a short constructed situation played on the tool. Also try to **knock down**
each of the suspicions below: say which ones turned out not to be problems, and why.

You may write your own scenario files. A scenario is a Python file defining `SCEN`:

```python
SCEN = dict(
    rules="exp-holds",            # or "exp-0.11.0" (no holds), or "exp-holds-per-square"
    seed=5, round_cap=6,
    map="\n".join(["############", "#..........#", "#..........#", "############"]),
    roster=[("A", "red", "l1_sample", "", (2, 1)),      # id, team, build, loadout, (x, y)
            ("X", "blue", "l1_sample", "", (3, 1))],
    hp={"X": 5},                  # optional: start wounded
    order=["A", "X"],             # optional: fixed initiative order
)
```

Builds: `l1_sample`, `l1_greatsword`, `l1_spear_fin0`, `l1_spear` (Finesse 1, cap 2),
`l1_archer` (loadout "bow" or "blade"), `l1_duelist` (two-handed longsword 1d10 + 3, no
armor, 8 HP). Change the seed to change the dice. `rg_holds.py`, `sc_holds.py` and
`br_holds.py` in this folder are ready-made fights you can use or cut down.

`exp-holds-per-square` is a variant under consideration: the cap is added again for every
square a mover leaves inside your reach without paying you off during one move, and one
opportunity attack may spend what has built up (so a creature that runs past you through
two of your squares can be hit with budget 2 x cap, and so on).

## Suspicions to test (add your own)

1. **Free holds.** A hold costs nothing if nobody can hit the holder before its next turn.
   Does "put everything you won't need on a hold" become the automatic end of every turn?
   How often can a creature know it won't be hit?
2. **The lock.** Two or three holders on one target make leaving cost more stamina than the
   target has. Is a caught creature then simply dead, with no decision left? What can its
   allies do: is attacking the holders (who have little ready stamina) a real answer? Does
   it matter that tokens stay out even when the holder is being hit?
3. **All-in then hold.** Holds are set after recovering 4. So a creature that spent
   everything attacking still has 4 tokens to place. Is that hold free? Compare with what
   would happen if holds had to be set before recovering.
4. **Initiative.** A holder who acts just before its target gives the target's allies no
   chance to act in between. A holder who acts just after its target holds it for almost a
   whole round. Find the worst case for the target in each.
5. **The retreat.** Can a wounded creature ever get away from a healthy one under holds?
   Can a creature use a hold to cover an ally's retreat (hold the pursuer so it can't follow
   without paying)? Is that strong, weak, or automatic?
6. **Archers.** A held archer; a held creature that is shot at (reacting by dashing means
   leaving the square: 1 + tokens); a holder who is shot at while its tokens are out.
7. **Big weapons.** The greatsword (base 3, cap 2) and the Finesse-0 spear (base 2, cap 1)
   can't make any opportunity attack without a hold. Can enemies just walk past them? Does
   `exp-holds-per-square` change that? Is the reach-2 spear's hold different (it can hold
   someone two squares away)?
8. **Splitting tokens** across several enemies, and a creature held by several enemies.
9. **Arithmetic.** Count what a player has to work out and track for one hold from start to
   finish. Find the situations where it gets worst.
10. **Anything the engine does that the rules digest didn't lead you to expect.**

Keep each demonstration small: two to four creatures, one or two rounds. Use
`python3 table.py NAME --odds A X` for odds at any point. Dice vary: when a finding depends
on a roll, say so, or try two or three seeds.

## What to send back

For each suspicion and each thing you found yourself: one short paragraph. Is it real? How
bad? The smallest situation that shows it (name the scenario file and orders file you left
in the folder). What the affected creature could have done instead. If you see an obvious
change to the rule that would fix it, say so in one line, marked as your suggestion. Rank
the real problems, worst first. Mark guesses as guesses. About 1,200 words at most.
