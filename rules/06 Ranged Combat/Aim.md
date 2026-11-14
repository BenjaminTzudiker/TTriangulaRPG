---
up: "[[Ranged Attacks]]"
---
# Aim

*Status: Exploratory (cost); Numbers placeholder (amount added)*

- **Free aim die:** every shot comes with **one aim die** (1d6, the same as an aim step), paid for by the shot cost. It isn't an action and doesn't add to the surcharge.
- **Aim steps:** each adds **1d6** to the shot's total. Finesse doesn't add to aim.
- **Cost:** each aim step is an **action**, so it costs **1 + actions already taken this turn**. Shots are actions too, and the count carries across shots; it doesn't restart.
- **Aim limit:** aim makes a shot harder to block, but it never adds to the wound. The HP a shot takes can't exceed the weapon's damage roll: its die plus any Strength it adds. Other bonuses to the total, such as the shortbow's Finesse, count like aim (see [[Weapons#Weapon Properties|Weapon Properties]]). Apply the limit after armor and before the critical bonus, so each critical die still adds +1 on top of it.
  - Blocks and armor save HP only once they bring the shot below the limit. Stopping part of a shot that's still over its limit changes nothing.
  - The range penalty comes off the shot's total, never off the limit (see [[Range Bands]]).
- **Aim dice are never critical** (see [[Critical Hits]]).

> [!example] Example: Two Aimed Longbow Shots
> An archer with Strength 1 shoots a longbow (shot cost 4, damage 1d8 + STR) twice in one turn, aiming once each time.
>
> First shot: 4 (shot, the first action) + 2 (aim). It rolls 1d8 + 1 and two aim dice: the free one and the aim step.
> Second shot: 6 (shot: 4 + 2 earlier actions) + 4 (aim).
>
> Total: 4 + 2 + 6 + 4 = **16 stamina**.
>
> **The aim limit.** Say the first shot rolls 3 on the d8 and 5 and 6 on the aim dice: 3 + 1 + 5 + 6 = **15** to block. The shot's damage roll was only 3 + 1 = 4, so it can take at most **4 HP**. The target has Ranged Defense 2 and no armor.
> - **No blocks:** all 15 gets through, and the limit cuts it to **4 HP**.
> - **Three perfect blocks** (1 + 2 + 3 = 6 stamina) leave 9. That's still over the limit, so the target still loses **4 HP**. The 6 stamina bought nothing.
> - **Six perfect blocks** (21 stamina) leave 3, which is under the limit: **3 HP**.
>
> Blocks only save HP once they bring the shot below its limit.
