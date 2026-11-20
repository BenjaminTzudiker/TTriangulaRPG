---
up: "[[Playtest Packet]]"
prev: "[[Movement]]"
next: "[[Holds]]"
---
# Opportunity Attacks

*Status: Locked (triggers); Mechanism open (avoidance, making them); Numbers placeholder (the cap)*

Slipping past an engaged enemy should cost something, without making the battlefield sticky. There are no facing rules.

## Triggers

**Leaving a threatened square:** you provoke an opportunity attack whenever you move out of a square an enemy threatens (one within its reach, usually the 8 squares around it). That includes:
- moving sideways within its reach;
- leaving its reach;
- stepping closer to an enemy with a reach weapon.

Moving into reach doesn't provoke; only leaving a threatened square does.

**Shooting in melee:** declaring a ranged attack while within an enemy's reach provokes from **every** enemy threatening you at that moment, whether or not it's the target. The opportunity attacks happen after your shot finishes resolving (see [[Ranged Attacks#Procedure|Procedure]]). An enemy must be able to make its opportunity attack both when you declare the shot and when the attacks happen. So an enemy that comes within reach during the shot doesn't get one, and neither does one that's no longer within reach, for example because it backed away in reaction to the shot.

## Avoiding Opportunity Attacks

To deny an enemy its opportunity attack for one square you leave, pay **1 stamina**.
- Pay as you leave the square, before the enemy says whether it would attack.
- Pay once per enemy, per square.
- The cost is always 1, on or off your turn.
- It isn't an action, so it doesn't add to your escalation, and your escalation doesn't add to it.
- **If the enemy holds you,** the first square costs 1 + the stamina it holds on you instead (see [[Holds]]).
- **If an enemy couldn't make even one step** of an opportunity attack against you, there's nothing to avoid: you owe it nothing.
- **For now, you can't pay to avoid the opportunity attacks a point-blank shot provokes.**

> [!example] Example: Avoiding Opportunity Attacks
> You leave a square threatened by A and B: 2 stamina.
> The next square is threatened only by C: 1 more.
> The next square is also threatened by C: 1 more, even though you already paid C once.

## Making Opportunity Attacks

An opportunity attack is a normal attack (see [[Attack Procedure]]) with its own pricing.
- **Steps:** each costs the weapon's base cost, +1 for each earlier step of the same opportunity attack. For a longsword that's 2, then 3, then 4 (2, 5 and 9 in total).
- **It isn't an action.** It doesn't add to your escalation, and your escalation doesn't add to it. Each opportunity attack starts fresh.
- **Cap:** one opportunity attack can cost at most **1, +1 per odd Finesse value** (see [[Finesse]]), plus any stamina you hold on that creature (see [[Holds]]). Held stamina is spent before your other stamina.
- Each trigger allows one. You can make one for every trigger you're given, while you have the stamina.

So a weapon with a base cost of 3 can't make an opportunity attack without Finesse 3 or a hold. Heavy weapons have to commit to punish an enemy for leaving.

> [!example] Example: Opportunity Attack Caps
> The sample fighter (Finesse 1) has a cap of 2: one longsword step.
> Holding the creature that leaves adds the stamina you hold on it to the cap. It takes 3 held stamina for a second step (2 + 3 = 5), 7 for a third (9), and 12 for a fourth (14).
