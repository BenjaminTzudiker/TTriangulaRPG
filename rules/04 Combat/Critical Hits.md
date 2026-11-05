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
- **Doubling:** if the attack has at least one critical die, double the damage that remains after armor.

**TODO:**
- Confirm that doubling happens once per attack, however many dice were critical.
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
> **Attacking again.** If the fighter attacks again this turn, their steps cost 2 + 2 = 4, then 2 + 3 = 5. The orc's perfect blocks start at 1 again.
