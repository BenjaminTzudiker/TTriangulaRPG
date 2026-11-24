---
up: "[[Class Trees]]"
---
# Candidate Abilities

*Status: Exploratory*

> [!note] Placeholder drafts
> All abilities in this note are exploratory placeholders and taste anchors for future design. Don't micro-tune their numbers or add new supporting subsystems for them until playtesting tests the core combat loop.

Abilities being tried out before they're settled. Where each one sits is part of the candidate. A Tier 1 feature needs the tree's core ability, and a Tier N feature needs the tree's Tier N ability (see [[Class Trees]]). An ability listed in two trees can be bought through either. The earlier candidates are in [[Earlier Candidate Abilities]].

| Ability | Fighter | Rogue | Barbarian | Monk |
|---|---|---|---|---|
| [[#Great Weapon Training]] | Tier 1 | | | |
| [[#Covering Hold]] | Tier 1 | | | |
| [[#Sweep]] | Tier 2 | | Tier 1 | |
| [[#Hard to Shake]] | Tier 2 | | | |
| [[#Steady Aim]] | Tier 2 | Tier 1 | | |
| [[#Hold the Line]] | Tier 3 | | | |
| [[#Unshaken]] | Tier 3 | | | |
| [[#Riposte]] | | Tier 1 | | Tier 2 |
| [[#Tumble]] | | Tier 1 | | Tier 1 |
| [[#Dual Wielding]] | | Tier 1 | | |
| [[#Paired Blades]] | | Tier 3 | | |
| [[#Many Hands]] | | | | Tier 1 |
| [[#Long Stride]] | | | Tier 2 | Tier 1 |
| [[#Shove]] | | | Tier 1 | Tier 2 |
| [[#Tear Free]] | | | Tier 2 ability | |
| [[#Cornered]] | | | Tier 3 ability | |
| [[#Drive Through]] | | | Tier 3 | |

[[#Tear Free]] is the Barbarian's **Tier 2 ability** and [[#Cornered]] is the Barbarian's **Tier 3 ability**: the pieces you buy to reach those tiers, not standalone tier features.

## Great Weapon Training

**Where:** Fighter Tier 1.

Your heavy melee weapons, those with a base cost of 3, reach 1 square further.
- A greatsword or greataxe reaches 2 squares instead of 1.
- A heavy weapon that already has reach, such as a halberd that reaches 2, reaches 3.

Reach sets which squares you threaten, so this also widens your opportunity attacks and holds (see [[Opportunity Attacks]] and [[Holds]]).

## Covering Hold

**Where:** Fighter Tier 1.

While you're using a shield, a hold you set on an enemy also triggers when that enemy makes a melee attack on an ally next to you, if the enemy is within your reach. After that attack resolves, you may make the hold's opportunity attack against the enemy. The hold then ends (any unspent held stamina becomes returning stamina; see [[Holds]]).
- "Next to you" means in one of the 8 squares around you when the attack is declared.
- The opportunity attack works as usual: it can spend your cap plus the stamina you hold on that enemy, held stamina first (see [[Opportunity Attacks#Making Opportunity Attacks|Making Opportunity Attacks]]).
- A shot at your ally from within your reach is already covered: shooting in melee provokes from you anyway (see [[Opportunity Attacks#Triggers|Triggers]]).

## Sweep

**Where:** Fighter Tier 2 and Barbarian Tier 1.

With a heavy melee weapon (base cost 3), you can make the **first step** of a normal melee attack a **sweep** that swings across several squares in one arc. It is still part of that attack, not a separate ability.
- **Arc:** start at your primary target's square (within your reach) and sweep clockwise or counterclockwise through consecutive adjacent squares **at the same distance from you** (for example, along the 8-square ring 1 square away, or along the outer ring 2 squares away with a reach-2 weapon).
  - You can add at most **your Strength** extra squares (so none at Strength 0), and you can never sweep into the same square twice.
  - The sweep stops if it hits a wall or pillar.
  - Every creature in the swept squares—**enemies and allies alike**—is hit by the sweep.
- **Cost:** the step's usual cost, **+2 stamina for each extra square** in the sweep (whether empty or occupied). The extra stamina isn't an action.
- **Rolling:** roll the first step once. Each creature in the sweep blocks it separately, and its own armor applies.
- **Later steps** of the attack add to the total against your primary target alone. Every other creature hit by the sweep faces only the first step.

> [!example] Example: A Sweep
> ```text
> a b c
> . F A
> . d .
> ```
> F has Strength 2 and a greatsword (reach 1); a, b, c and d are enemies and A is an ally. F declares a 2-step attack with b as its primary target, making the first step a sweep of 2 extra squares clockwise: b → c → A would hit ally A, so F sweeps counterclockwise instead—b → a (1 extra square, +2 stamina). As F's first action, the two steps cost (3 + 2) + 4 = 9. Both a and b face the first step; b faces the second step too.
>
> With [[#Great Weapon Training]] (reach 2), F could instead start at a target 2 squares away and sweep up to 2 extra consecutive squares along that distance-2 ring.

## Hard to Shake

**Where:** Fighter Tier 2.

Your hold on a creature doesn't end when it leaves a square in your reach. Every square it leaves in your reach costs it 1 + the stamina you still hold on it to avoid your opportunity attack, and an opportunity attack you make there can still spend that held stamina.
- A hold still ends when you lose HP (see [[Holds#When a Hold Ends|When a Hold Ends]]).
- This only changes leaving. A hold that ends for another reason, such as [[#Covering Hold]], still ends.
- If the creature leaves your reach, the hold stays on it until your held stamina returns. If it returns and leaves a square in your reach again, it pays again.

## Steady Aim

**Where:** Rogue Tier 1 and Fighter Tier 2.

When you shoot a creature you hold, you may **spend** stamina you hold on it to pay for aim steps. This is an exception to the rule that held stamina never pays for your own shots (see [[Holds]]).
- An aim step paid entirely with held stamina doesn't add to your escalation. So each one costs 1 + your escalation as it stands after the shot: 2 if the shot was your first action since your last turn ended, 3 if you'd taken one action before it, and so on.
- Aim steps you pay for normally work as usual, counting from that same escalation (see [[Aim]]).
- Held stamina spent this way is gone, as when it pays for an opportunity attack. The hold is smaller by that much, and doesn't end unless you spend all of it.

> [!example] Example: Steady Aim
> You hold 6 on an orc. On your turn you shoot it with a longbow as your first action: 4 for the shot, and your escalation is now 1.
> - Three aim steps paid from the hold cost 2 each and spend all 6 held stamina.
> - A fourth aim step, paid from ready stamina, also costs 2, and a fifth costs 3.

## Hold the Line

**Where:** Fighter Tier 3. **Prerequisite:** [[#Hard to Shake]].

At the end of your turn, instead of holding individual creatures, you may hold your entire reach. That one hold applies to every enemy while it's within your reach.
- An enemy that leaves a square in your reach pays 1 + the stamina you hold to avoid your opportunity attack, and an opportunity attack against it can spend that held stamina.
- Any held stamina spent on an opportunity attack is gone; whatever remains keeps applying to every enemy in your reach.
- As with [[#Hard to Shake]], the hold doesn't end when an enemy leaves a square in your reach. It ends when you lose HP (any unspent held stamina becomes returning stamina).

> [!question] Hold the Line and Covering Hold
> Whether a hold on your reach also triggers [[#Covering Hold]] is undecided. If it does, Covering Hold would end the whole hold.

## Unshaken

**Where:** Fighter Tier 3.

When an attack costs you HP no greater than your Will, it doesn't end your active holds. Instead, each of your active holds loses that much held stamina (which becomes returning stamina until the end of your next turn; see [[Holds]]); a hold reduced to 0 ends.
- With Will 0, any HP loss still ends your holds as usual.
- If a single attack costs you more HP than your Will, all your holds end as usual.

## Riposte

**Where:** Rogue Tier 1 and Monk Tier 2.

When you stop all the damage of an enemy's melee attack with perfect blocks alone, your next melee attack step against that enemy, before the end of your next turn, isn't an action: it costs the weapon's base cost, and it doesn't add to your escalation.
- "Perfect blocks alone" means no grazing blocks and no damage left for armor.
- Only that one step is free of escalation. Later steps of the same attack cost the usual amount, which is 1 less than it would have been because the riposte step didn't count.
- Opportunity attacks aren't actions anyway, so Riposte only changes attacks on your turn.

## Tumble

**Where:** Rogue Tier 1 and Monk Tier 1.

When you move, you pay each enemy at most once to avoid its opportunity attacks, however many of its squares you leave in that move. A hold still adds its stamina to that payment.
- A **move** is all the moving you do, free or dashing, without doing anything else in between. An attack, a shot, an aim step, helping the dying, the end of your turn and the end of a dash phase all end it.
- The first time you pay an enemy during a move covers every later square of that move. Until you pay, it can make an opportunity attack for each square as usual.
- Against [[#Hard to Shake]], you still pay that enemy only once per move.

## Dual Wielding

**Where:** Rogue Tier 1.

While you wield a light melee weapon (base cost 1) you're proficient with in each hand, you keep a separate escalation counter for each hand (both reset when your turn ends).
- **Melee steps:** a melee attack step uses and raises **that hand's** escalation counter.
- **Other actions:** any other action (such as a dash or helping the dying) uses the **higher** of the two counters and raises **both** counters by 1.
- **Separate attacks:** each melee attack uses one hand (you can't combine steps from both hands into a single attack, so attacking with the other hand starts a new attack and resets the defender's block count).
- **Defense trade-off:** if you make melee attacks with **both** hands between the end of your last turn and the end of this one (or since the fight began, on your first turn—the same window your escalation counters track), you lose the +1 Melee Defense from carrying a second weapon (see [[Defenses]]) until the start of your next turn.

> [!example] Example: Dual Wielding
> You hold a shortsword and a dagger (both base 1), starting at escalation (0, 0).
> 1. You dash once: uses the higher (0) for **1** stamina; counters become (1, 1).
> 2. You make a 2-step shortsword attack: uses the sword's counter (1, then 2) for **2 + 3** stamina; counters become (3, 1).
> 3. You make a 1-step dagger attack (a separate attack): uses the dagger's counter (1) for **2** stamina; counters become (3, 2). Having attacked with both hands, you lose the second weapon's +1 Melee Defense until your next turn starts.
> 4. You make a 1-step shortsword attack: uses the sword's counter (3) for **4** stamina; counters become (4, 2).
> 5. You dash again: uses the higher (4) for **5** stamina; counters become (5, 3).

## Paired Blades

**Where:** Rogue Tier 3. **Prerequisite:** [[#Dual Wielding]].

Attacking with both hands no longer costs you the +1 Melee Defense from carrying a second weapon.

## Many Hands

**Where:** Monk Tier 1.

On your turn, the first melee attack step you make against each enemy after the first enemy you attack this turn doesn't add to your escalation, at most twice a turn.
- Each such step still costs its normal stamina (weapon base + your current escalation); it simply doesn't raise your escalation for what comes after.

## Long Stride

**Where:** Monk Tier 1 and Barbarian Tier 2.

Your Movement is 1 square more (see [[Free Movement]]). This can take it past 8.

## Shove

**Where:** Barbarian Tier 1 and Monk Tier 2.

Once per attack, when your melee attack deals HP damage to a creature whose **Strength is no higher than yours**, you may move it 1 square (see [[Forced Movement]]).

## Tear Free

**Where:** the Barbarian's Tier 2 ability.

When you pay to avoid opportunity attacks, you may pay some or all of it in HP. Each HP pays for **up to** your Strength in stamina.
- That includes the extra stamina a hold adds.
- It's losing HP, so it ends your holds (turning their held stamina into returning stamina) and lowers your maximum stamina (see [[Holds]] and [[Stamina]]). Blocks and armor don't apply to it.
- It can't take you below 1 HP.
- With Strength 0 it does nothing.

> [!example] Example: Tear Free
> Your Strength is 2, and an orc holds you with 3. Stepping out of its reach costs 1 + 3 = 4. You can pay 2 HP, or 1 HP and 2 stamina, or 4 stamina. If you owed only 1 stamina instead, 1 HP still covers it.

## Cornered

**Where:** the Barbarian's Tier 3 ability.

Once per turn, when you attack a creature that holds you, add one more step to the end of the attack for free. It rolls and adds like any other step, but costs no stamina.
- You must pay for at least one other step of that attack.
- It's still an action, so it adds to your escalation for whatever you do after the attack.

## Drive Through

**Where:** Barbarian Tier 3. **Prerequisite:** [[#Shove]].

When you move a creature with [[#Shove]], if the square it left is next to you, you may immediately step into it. That step is free and doesn't provoke an opportunity attack from that creature (other enemies can still provoke as usual).
