---
up: "[[Playtest Packet]]"
prev: "[[Melee Attacks]]"
next: "[[Blocking]]"
---
# Actions and Escalation

*Status: Mechanism open*

Doing several things in a round is possible, but expensive.

An **action** is one of:
- a **melee attack step**;
- a **ranged shot** (see [[Ranged Attacks]]);
- an **aim step** on a ranged attack (see [[Aim]]);
- a **dash** (see [[Dash]]).

Each action costs its base **+1 stamina for every action you've taken since your last turn ended**. That number is your **escalation**.
- There's one escalation. It counts dashes you take outside your turn as well as everything you do on it, so dashing between turns makes your own turn more expensive.
- **Reset:** it goes back to 0 when your turn ends, as you recover stamina and before the next dash phase. Nothing else resets it.
- Before your first turn of a fight, it counts every action you've taken since the fight began.

**Bases:** a melee attack step costs the weapon's base cost; a shot costs its shot cost; an aim step and a dash cost 1.

These aren't actions. They don't add to your escalation, and your escalation doesn't add to their cost:
- your **free movement** (see [[Free Movement]]);
- **blocks**, whose costs rise only within one attack (see [[Blocking]]);
- **the free aim die** that comes with every shot (see [[Aim]]);
- **paying to avoid an opportunity attack**, and **making one** (see [[Opportunity Attacks]]);
- **setting a hold** (see [[Holds]]);
- **drawing a weapon** (see [[Drawing Weapons]]).

Outside your turn, the only action you can take is a dash.

**Spells** each say how they work, including how they interact with escalation.

> [!example] Example: Escalation
> An archer shoots at you and you dash for cover: 1.
> In the dash phase before your turn you dash toward the archer: 2.
> On your turn you make two longsword steps: 2 + 2 = 4, then 2 + 3 = 5.
>
> That's **12 stamina** for four actions. Your turn ends: you recover stamina and your escalation goes back to 0.
> In the next dash phase you dash away: 1.

> [!question] About the name "action"
> This name is provisional.
> - It's misleading next to D&D, where an action is a fixed slot per turn.
> - It implies that each attack step is a separate action, when several steps are really one committed attack.
> - It clashes with everyday uses of "action" in rules text.
>
> A better name is wanted.
