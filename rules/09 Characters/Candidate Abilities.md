---
up: "[[Class Trees]]"
---
# Candidate Abilities

*Status: Exploratory*

Abilities being tried out before they're settled. Where each one sits is part of the candidate. A Tier 1 feature needs the tree's core ability, and a Tier N feature needs the tree's Tier N ability (see [[Class Trees]]). An ability listed in two trees can be bought through either. The earlier candidates are in [[Earlier Candidate Abilities]].

| Ability | Fighter | Rogue | Barbarian | Monk |
|---|---|---|---|---|
| [[#Great Weapon Training]] | Tier 1 | | | |
| [[#Covering Hold]] | Tier 1 | | | |
| [[#Sweep]] | Tier 2 | | Tier 1 | |
| [[#Hard to Shake]] | Tier 2 | | | |
| [[#Steady Aim]] | Tier 2 | Tier 1 | | |
| [[#Hold the Line]] | Tier 3 | | | |
| [[#Quick Reflexes]] | Tier 3 | Tier 2 | | |
| [[#Riposte]] | | Tier 2 | | Tier 1 |
| [[#Tumble]] | | Tier 2 | | Tier 1 |
| [[#Long Stride]] | | | Tier 2 | Tier 1 |
| [[#Cornered]] | | | Tier 2 | |
| [[#Tear Free]] | | | Tier 2 ability | |

[[#Tear Free]] is the Barbarian's **Tier 2 ability**: the piece you buy to reach Tier 2, not a Tier 2 feature.

## Great Weapon Training

**Where:** Fighter Tier 1.

Your heavy melee weapons, those with a base cost of 3, reach 1 square further.
- A greatsword or greataxe reaches 2 squares instead of 1.
- A heavy weapon that already has reach, such as a halberd that reaches 2, reaches 3.

Reach sets which squares you threaten, so this also widens your opportunity attacks and holds (see [[Opportunity Attacks]] and [[Holds]]).

## Covering Hold

**Where:** Fighter Tier 1.

While you're using a shield, a hold you set on an enemy also triggers when that enemy makes a melee attack on an ally next to you, if the enemy is within your reach. After that attack resolves, you may make the hold's opportunity attack against the enemy. The hold then ends.
- "Next to you" means in one of the 8 squares around you when the attack is declared.
- The opportunity attack works as usual: it can spend your cap plus the stamina you hold on that enemy, held stamina first (see [[Opportunity Attacks#Making Opportunity Attacks|Making Opportunity Attacks]]).
- A shot at your ally from within your reach is already covered: shooting in melee provokes from you anyway (see [[Opportunity Attacks#Triggers|Triggers]]).

## Sweep

**Where:** Fighter Tier 2 and Barbarian Tier 1.

With a heavy melee weapon (base cost 3), the first step of an attack can be a **sweep** that hits several enemies.
- **Targets:** your target, plus any other enemies within your reach that you add. You must be able to trace one path through all of them, each square to an adjacent one, using only squares within your reach that are empty or hold one of your targets. So a sweep can cross empty squares, but not an ally, an enemy you leave out, or a wall.
- **Cost:** the step's usual cost, +1 stamina for each enemy after the first. The extra stamina isn't an action.
- **Rolling:** roll the step once. Each enemy blocks it separately, and its own armor applies.
- **Later steps** of the attack add to the total against your target alone. The other enemies face only the sweep.

> [!example] Example: A Sweep
> ```text
> . a b
> . F A
> . d .
> ```
> F has a greatsword (reach 1); a, b and d are enemies and A is an ally. F can sweep all three enemies: the path runs b, a, then the three empty squares on the left, then d. As F's first action that costs 3 + 2 = 5.
>
> The path can't go through A. If the square to F's left held another ally, F could sweep a and b, or d, but not all three.

## Hard to Shake

**Where:** Fighter Tier 2.

Your hold on a creature doesn't end when it leaves a square in your reach. Every square it leaves in your reach costs it 1 + the stamina you still hold on it to avoid your opportunity attack, and an opportunity attack you make there can still use that held stamina.
- A hold still ends when you lose HP (see [[Holds#When a Hold Ends|When a Hold Ends]]).
- This only changes leaving. A hold that ends for another reason, such as [[#Covering Hold]], still ends.
- If the creature leaves your reach, the hold stays on it until your held stamina comes back. If it returns and leaves a square in your reach again, it pays again.

## Steady Aim

**Where:** Rogue Tier 1 and Fighter Tier 2.

When you shoot a creature you hold, you may pay for aim steps with the stamina you hold on it. This is an exception to the rule that held stamina never pays for your own shots (see [[Holds]]).
- An aim step paid entirely with held stamina doesn't add to your escalation. So each one costs 1 + your escalation as it stands after the shot: 2 if the shot was your first action since your last turn ended, 3 if you'd taken one action before it, and so on.
- Aim steps you pay for normally work as usual, counting from that same escalation (see [[Aim]]).
- Held stamina spent this way is gone, as when it pays for an opportunity attack. The hold is smaller by that much, and doesn't end.

> [!example] Example: Steady Aim
> You hold 6 on an orc. On your turn you shoot it with a longbow as your first action: 4 for the shot, and your escalation is now 1.
> - Three aim steps paid from the hold cost 2 each and use all 6.
> - A fourth aim step, paid normally, also costs 2, and a fifth costs 3.

## Hold the Line

**Where:** Fighter Tier 3.

At the end of your turn, instead of holding creatures, you may hold your reach. That one hold applies to every enemy while it's within your reach.
- An enemy that leaves a square in your reach pays 1 + the stamina you hold to avoid your opportunity attack, and an opportunity attack against it can use that held stamina.
- An opportunity attack spends held stamina as usual. Whatever is left keeps applying to every enemy.
- The hold doesn't end when an enemy leaves a square in your reach. It ends when you lose HP.

> [!question] Hold the Line and Covering Hold
> Whether a hold on your reach also triggers [[#Covering Hold]] is undecided. If it does, Covering Hold would end the whole hold.

## Quick Reflexes

**Where:** Fighter Tier 3 and Rogue Tier 2.

At any time, you may take 2 stamina off a hold you have on a creature and get 1 stamina back now. The other 1 is gone. You can do this as often as you like, 2 at a time.
- For example, after seeing an attack's roll and before you block, to pay for blocks with stamina you'd held.
- Once a hold has ended, for example because you lost HP, its stamina can't be taken back this way.
- It isn't an action.

## Riposte

**Where:** Monk Tier 1 and Rogue Tier 2.

When you stop all the damage of an enemy's melee attack with perfect blocks alone, your next melee attack step against that enemy, before the end of your next turn, isn't an action: it costs the weapon's base cost, and it doesn't add to your escalation.
- "Perfect blocks alone" means no grazing blocks and no damage left for armor.
- Only that one step is free of escalation. Later steps of the same attack cost the usual amount, which is 1 less than it would have been because the riposte step didn't count.
- Opportunity attacks aren't actions anyway, so Riposte only changes attacks on your turn.

## Tumble

**Where:** Monk Tier 1 and Rogue Tier 2.

When you move, you pay each enemy at most once to avoid its opportunity attacks, however many of its squares you leave in that move. A hold still adds its stamina to that payment.
- A **move** is all the moving you do, free or dashing, without doing anything else in between. An attack, a shot, an aim step, helping the dying, the end of your turn and the end of a dash phase all end it.
- The first time you pay an enemy during a move covers every later square of that move. Until you pay, it can make an opportunity attack for each square as usual.
- Against [[#Hard to Shake]], you still pay that enemy only once per move.

## Long Stride

**Where:** Monk Tier 1 and Barbarian Tier 2.

Your Movement is 1 square more (see [[Free Movement]]). This can take it past 8.

## Cornered

**Where:** Barbarian Tier 2.

Once per turn, when you attack a creature that holds you, add one more step to the end of the attack for free. It rolls and adds like any other step, but costs no stamina.
- You must pay for at least one other step of that attack.
- It's still an action, so it adds to your escalation for whatever you do after the attack.

## Tear Free

**Where:** the Barbarian's Tier 2 ability.

When you pay to avoid opportunity attacks, you may pay some or all of it in HP. Each HP pays for stamina equal to your Strength.
- That includes the extra a hold adds.
- It's losing HP, so it ends your holds and lowers your maximum stamina (see [[Holds]] and [[Stamina]]). Blocks and armor don't apply to it.
- It can't take you below 1 HP.
- With Strength 0 it does nothing.

> [!example] Example: Tear Free
> Your Strength is 2, and an orc holds you with 3. Stepping out of its reach costs 1 + 3 = 4. You can pay 2 HP, or 1 HP and 2 stamina, or 4 stamina.
