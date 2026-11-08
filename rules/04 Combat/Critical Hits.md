---
up: "[[Playtest Packet]]"
prev: "[[Blocking]]"
next: "[[Ranged Attacks]]"
---
# Critical Hits

*Status: Locked*

A critical hit means hitting a vital spot. It comes from skill, not luck.

- **Critical range:** a damage die is critical when it rolls its maximum. Each odd Finesse value widens the range by 1, up to +3. See the [[Quick Reference#Critical Range Table|Critical Range Table]].
- **The defender knows** how many dice were critical before choosing blocks.
- **Each critical die ignores 1 armor.**
- **Critical bonus:** if any damage gets past blocks and armor, add **+1 per critical die**. If blocks and armor stop all of it, critical dice add nothing.

**TODO:**
- Can aim dice be critical?

> [!example] Example: Melee Attack
> A fighter (STR 2, FIN 1) attacks an orc with a one-handed longsword: base cost 2, damage 1d8 + STR + FIN.
>
> **The attack.** It's the fighter's first action this turn, and they commit two steps: 2 + 3 = **5 stamina**. They roll 6 and 3. That's (6 + 3) + (3 + 3) = **15 damage**, with no critical dice. With FIN 1, the fighter's d8 would be critical on a 7 or 8.
>
> **The defense.** The orc has Melee Defense 4 and armor 1. Some of its options:
>
> | Blocks | Stamina | Through blocks | After armor |
> |---|---:|---:|---:|
> | 4 perfect | 1 + 2 + 3 + 4 = 10 | 0 | 0 |
> | 3 perfect + 1 grazing | 6 + 1 = 7 | 1 (leak) | 0 |
> | 2 perfect + 2 grazing | 3 + 2 = 5 | 2 (leaks) | 1 |
> | 2 perfect + 1 grazing | 3 + 1 = 4 | 3 + 1 leak = 4 | 3 |
>
> **With a critical die.** Suppose the first die had rolled 7 instead: (7 + 3) + (3 + 3) = **16 damage**, with one critical die. The orc's armor counts as 0 against this attack. Four perfect blocks still stop all of it, so the critical die adds nothing. Two perfect and two grazing blocks let the 2 leaks through: 2 + 1 = **3 HP**.
>
> **Attacking again.** If the fighter attacks again this turn, their steps cost 2 + 2 = 4, then 2 + 3 = 5. The orc's perfect blocks start at 1 again.
