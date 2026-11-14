---
up: "[[Playtest Packet]]"
prev: "[[Critical Hits]]"
next: "[[Dying and Death]]"
---
# Attack Procedure

*Status: Locked (offense before defense); Mechanism open (exact steps)*

This is the whole sequence for one attack, melee or ranged. All offensive steps come before any defensive step.

**Offense**
1. Declare the target.
2. Declare your attack steps (or shot and aim steps; see [[Ranged Attacks]]) and pay the stamina.
3. Roll and add up the total. Note any critical dice (see [[Critical Hits]]).

**Defense**

4. Reactions, such as diving for cover against a ranged attack (see [[Cover]]).
5. Declare perfect and grazing blocks.

**Resolution**

6. Armor reduces what's left. Each critical die and each point of Piercing ignores 1 armor (see [[Armor]] and [[Weapons#Weapon Properties|Weapon Properties]]).
7. For a ranged attack, the aim limit caps what's left at the weapon's damage roll (see [[Aim]]).
8. If any damage is left, add 1 for each critical die.
9. The defender loses that much HP.

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
