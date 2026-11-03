# Playtest Packet: Consolidated Prototype
Version 0.9

> **Purpose**
>
> This is the current implementation of the game, written for internal playtesting rather than publication. Treat everything here as the current rules unless it's marked **TODO**.

## Reading the status markers

Each rule carries one of these markers so you can tell what's settled.

| Marker | Meaning |
|---|---|
| **Locked** | A deliberate current choice. "Locked" doesn't mean closed: a good enough reason can reopen anything. |
| **Numbers placeholder** | The intent and shape are decided, but the values may change. Playtest the shape; treat the numbers as illustrative. |
| **Mechanism open** | The goal is decided, but this procedure is the current version to test. |
| **Exploratory** | A trial idea. Even the shape is open. |
| **TODO** | Not written yet, or a detail still needs a decision. |

Some rules carry two markers, one for each part (for example, "Locked (timing); Numbers placeholder (amount)").

## What changed from v0.8

- **Maximum HP Damage is removed for now** (see **Not in This Version**). Everything that gets past blocks and armor is HP damage.
- **The on-turn surcharge** now counts melee attack steps **and aim steps** as actions. Ranged shots pay a flat cost.
- **Opportunity attacks:**
  - Avoiding one costs 1 stamina per enemy, per square you leave.
  - Shooting within an enemy's reach provokes.
  - The stamina you can spend on an opportunity attack is capped (1, +1 per odd Finesse), replacing "+1 stamina for opportunity attacks".
  - Opportunity attacks share an escalation track with off-turn movement.
- **Off-turn movement** can happen after any creature's turn, including your own. It's capped at 4 squares per purchase, and it shares that escalation track.
- **New rules:**
  - Extra on-turn movement.
  - Base movement.
  - Armor's effect on Agility, and Strength requirements for armor.
  - The weapon table.
  - Critical hits.
  - Dying and death (System Shock).
  - Expertise and Skill Point costs.
  - How class trees and tiers are bought.
  - Class core abilities.
  - Losing base defenses at negative Agility.
- **Corrected:**
  - Dodge Defense uses half your Agility.
  - Initiative uses odd Agility and odd Cunning, with no tiebreaker.
  - The Strain example now costs 9, not 7.
  - Casting isn't allowed in armor or with a shield.
  - Characters start at level 1.
- **Removed:** the 10-level tier advancement, and v0.8's editorial scaffolding sections.

---

# What This Game Is Trying To Do

Stamina isn't a resource you spend to enhance your defense, it *is* your defense. The game is about managing the ebb and flow of stamina, because when you run out you can no longer do things and you might just straight up die.

**Combat should feel dangerous without being swingy.**
- One good hit can take someone out of the fight.
- Players should have the tools to outplay their opponents, and they shouldn't die to bad dice luck as long as they play smart.
- The model is the named characters in *Game of Thrones*. They do sometimes die, but they have to be pressured before they take a fatal hit. Mooks die to a stab they never saw coming; named characters don't.

**The rules should describe plausible events in a fight.**
- Every mechanic should be understandable as something that could actually happen.
- Where the game departs from realism, it does so on purpose, and in favor of the characters' awareness and agency.
- Attributes are human-scale. Even the best possible score is the peak of real human ability, not a heroic-fantasy feat.

**Tactical depth shouldn't come from arithmetic or decision overload.** Most of the depth comes from one shared resource that every choice draws on.

**Build the character you imagine.** You should never have to choose between staying true to your concept and being effective. That's why combat attributes and out-of-combat skills are bought with separate currencies.

**Outside combat, the rules stay much lighter** and lean on the GM's judgment.

---

# Core Concepts

## Shared Resources

Almost every combat decision draws on the same resource: **stamina**. Attacking, blocking, moving, reacting and using abilities all cost it. Attack hard and you'll have less left to block, move or react with later in the round.

## Commitment

You decide how much to commit before you see the result of your attack.
- **Commit too little,** and your opponent may recover before your next attack.
- **Commit too much,** and you may leave yourself exposed.

The defender sees exactly what's coming and decides how much to spend stopping it.

## Injury

Most of an attack's damage is usually stopped by stamina spent on blocks. Whatever gets past the blocks and armor is real, lasting injury, and HP is small.

## Positioning

Positioning matters all round, not just on your turn. You can:
- move after other creatures' turns;
- dive for cover when shot at;
- punish enemies who slip past you;
- control space with reach.

---

# Core Resources

## HP

*Status: Numbers placeholder*

HP represents lasting physical injury. It's deliberately small: one solid stab is meant to take someone out of commission.

**Maximum HP = 6 + Strength.**

HP doesn't increase with level. You recover **1 HP per night of rest**.

Dropping to 0 HP or below takes you out of the fight (see **Dying and Death**).

## Stamina

*Status: Numbers placeholder (maximum); Locked (recovery timing); Numbers placeholder (recovery amount)*

Stamina is the effort immediately available to you: footwork, weapon control, concentration, balance, and the energy to react under pressure.

**Maximum Stamina = 6 + current HP + round(Level / 5)**

Because it uses *current* HP, injuries lower your maximum stamina. Your current stamina can never exceed your maximum: if a wound drops your maximum below your current stamina, your current stamina drops to the new maximum. Otherwise it's unaffected.

**At the end of your own turn,** recover **4 + round(Level / 10)** stamina, up to your maximum.
- Round halves up, so the bonus becomes +1 at level 5.
- No attribute affects recovery.

Why the end of your turn?
- It's a safety net: you can't spend yourself to zero and then face a whole round defenseless.
- You'll want to spend some stamina right away, or your first recovery is wasted. That discourages passive standoffs.
- It rewards going early.

Stamina recovers every turn, so it's effectively full again after a short breather between fights. There's no formal rule for this yet.

## Strain

*Status: Numbers placeholder (maximum); Mechanism open (recovery)*

Strain is longer-term exertion that doesn't recover during combat. It's the shared pool that pays for class abilities and spells, replacing per-day uses and spell slots. Taking more classes doesn't give you more total uses.

**Maximum Strain = 6 + round(Level / 5)**

**Recovery:** **4 + round(Level / 10)** strain per night of rest.
- **Alternative under consideration:** recover 1 strain per 6 hours of rest, with no strain-recovery bonus at levels ending in 5.

### Going Over Your Maximum Strain

*Status: Locked*

You can exceed your maximum strain. For each point you're over, every strain ability costs **+1 stamina**. That includes the ability you're using now: count your overage **after** adding its strain.

You can keep using abilities, but each use leaves you more exposed on the turn you use it.

> **Example: Strain**
>
> A wizard's maximum strain is 8, and they're currently at 10. They cast a spell costing 5 stamina and 2 strain.
>
> Paying the strain takes them to 12, which is 4 over their maximum. The spell costs **5 + 4 = 9 stamina**.

---

# Attributes

There are six attributes:
- **Physical:** Strength, Agility and Finesse.
- **Mental:** Intelligence, Will and Cunning.

There's no Constitution, because it would be an automatic pick. There's no Charisma either: presence and leadership come through the mental attributes.

## Attribute Scale

*Status: Numbers placeholder (ranges); the descriptions are a draft*

- **Expertise** sets each attribute from **0 to +6**. That value applies everywhere.
- **Skill Points** can add up to **+4 more, for skill checks only**. That's broad talent or education that doesn't hold up under the pressure of combat.
- So a skill check can use up to +10.

No value on this scale is superhuman. Even 10 is the limit of real human ability. This isn't a game where the strongest hero suplexes a 5,000 lb monster.

| Value | Meaning |
|---:|---|
| 0 | Clearly deficient, but you can still be an adventurer. For Strength, an old, weak wizard. |
| 1 | Functional but below average. |
| 2 | An average person (not an average adventurer). |
| 3 | A bit above average. For Strength, someone who would consistently beat the average person at arm wrestling. |
| 4 | Trained through regular use, but not exceptional. For Strength, a manual worker or regular gym-goer. |
| 5 | A standout. |
| 6 | Exceptional; among the best in a region. |
| 7 | Genius-level; among the best in the world. |
| 8 | Elite even among the world's best. |
| 9 | One of a handful alive. For Strength, a contender for world's strongest man: a 7 ft tall Eddie Hall, not a comic-book superhero. |
| 10 | The pinnacle of human ability; once in a generation. Reachable only on skill checks. |

## Odd and Even Values

Several attributes give a bonus at each **odd** value (1, 3 and 5) and a different bonus at each **even** value (2, 4 and 6). See the **Attribute Bonus Table** in the Quick Reference.

## Strength

*Status: Exploratory*

Strength is physical power.
- **+1 HP** per point. This also raises your maximum stamina through HP.
  - This is flagged as suspect, because it scales poorly at higher levels.
- Adds to damage on weapons that use it.
- Reduces armor penalties (see **Armor**).

## Agility

*Status: Numbers placeholder*

Agility is whole-body movement: balance, speed, evasiveness and cardiovascular endurance.

**Odd values (1, 3, 5):**
- +1 initiative.
- +1 square of on-turn movement.
- +1 square per off-turn movement purchase, and per extra on-turn movement purchase.

**Even values (2, 4, 6):**
- +1 Melee Defense and +1 Dodge Defense.
- Medium and heavy armor reduce this (see **Armor**).

**Below 0** (for example, from armor penalties): you lose your base 1 Melee, Ranged and Dodge Defense.

## Finesse

*Status: Numbers placeholder*

Finesse is fine motor control: precision, timing, coordination and weapon control.

**Odd values (1, 3, 5):**
- +1 critical range (see **Critical Hits**).
- +1 to your opportunity attack cap (see **Making Opportunity Attacks**).

**Even values (2, 4, 6):**
- +1 Melee Defense while wielding a melee weapon you're proficient with.

**Below 0** (for example, from armor penalties): you lose the +1 Melee Defense for wielding a proficient weapon.

## Intelligence

*Status: TODO*

Intelligence is learning, reasoning, memory and technical understanding.

Combat benefits: **TODO**.

## Will

*Status: TODO*

Will is determination, discipline, resolve and spiritual force.

Combat benefits: **TODO**.

## Cunning

*Status: Exploratory*

Cunning is awareness, instinct, perception, social insight, deception, and the ability to rapidly understand a situation as it unfolds.
- **Odd values (1, 3, 5):** +1 initiative. This is a placeholder whose job is to show that Cunning improves initiative.
- Other combat benefits: **TODO**.

The mental attributes need to matter to characters who don't use magic. They aren't fully defined yet.

---

# Combat

## Starting Combat and Turn Structure

*Status: Exploratory*

1. **Roll initiative:** **2d12** (placeholder) + 1 per odd Agility value + 1 per odd Cunning value. There's no tiebreaker for now.
2. **Take turns in initiative order.** On your turn:
   - Move and take actions in any order. Your movement can be split up around your actions.
   - End your turn.
   - Recover stamina.
3. **After any creature's turn ends** (including yours), anyone may buy off-turn movement (see **Off-Turn Movement**).

There are no separate action, bonus action and reaction economies. Everything runs on stamina.

## Actions and the On-Turn Surcharge

*Status: Mechanism open*

Doing several things in one turn is possible, but expensive.

An **action** is either:
- a **melee attack step**, or
- an **aim step** on a ranged attack.

Each action costs **+1 stamina for every action you've already taken this turn**. This is the **on-turn surcharge**. It resets at the start of your next turn.

These aren't actions:
- **The base cost of a ranged shot.** It's flat, with no surcharge.
- **Extra on-turn movement.** It always costs 1 stamina.

**Spells** each say how they work, including how they interact with the surcharge.

> **About the name "action":** this name is provisional.
> - It's misleading next to D&D, where an action is a fixed slot per turn.
> - It implies that each attack step is a separate action, when several steps are really one committed attack.
> - It clashes with everyday uses of "action" in rules text.
>
> A better name is wanted.

## Melee Attacks

*Status: Locked (no to-hit roll; commitment); Mechanism open (exact steps)*

There's no separate roll to hit. **The damage roll is the attack.** An attack abstracts any number of swings, and the defender's blocks decide how much of it lands.

**Attack steps.** A melee attack is made of one or more **attack steps**. Each step adds the weapon's damage roll to the total.
- Each step costs the weapon's **base cost + the on-turn surcharge** (the number of actions already taken this turn).
- You declare every step before you roll.

| Steps (base-2 weapon, first actions this turn) | Costs | Total |
|---|---|---:|
| 1 | 2 | 2 |
| 2 | 2 + 3 | 5 |
| 3 | 2 + 3 + 4 | 9 |

A greatsword (base 3) costs 3 + 4 = 7 for two steps.

**Weapon card shorthand:** "3 × [1d10 + STR + FIN]" means three attack steps, each rolling 1d10 + STR + FIN.

**Attacking again.** You can attack again after an attack resolves, against the same target or a different one.
- Your surcharge carries on where it left off.
- The defender's block count resets (see **Blocking**).
- So attacking twice is easier to block than committing everything at once. Misjudging how much to commit costs you efficiency, but it isn't forbidden.

### Attack Procedure

*Status: Locked (offense before defense); Mechanism open (exact steps)*

All offensive steps come before any defensive step.

**Offense**
1. Declare the target.
2. Declare your attack steps (or shot and aim steps) and pay the stamina.
3. Roll and add up the total. Note any critical dice (see **Critical Hits**).

**Defense**

4. Reactions, such as diving for cover against a ranged attack.
5. Declare perfect and grazing blocks.

**Resolution**

6. Armor reduces what's left. Each critical die ignores 1 armor.
7. If any die was critical, double the remaining damage.
8. The defender loses that much HP.

## Defenses

*Status: Locked (structure); Numbers placeholder (values)*

Every attack is blocked using exactly one defense value. Your base defenses represent a baseline ability to weakly avoid damage.

### Melee Defense

Keeping an opponent's weapon off you with footwork, weapon control, shields and similar techniques.

| Source | Bonus |
|---|---|
| Base (lost if Agility is below 0) | 1 |
| Wielding a melee weapon you're proficient with (lost if Finesse is below 0) | +1 |
| A second proficient melee weapon in your other hand, **or** a shield | +1, **or** +2 |
| Each even Agility value (fewer in medium or heavy armor; see **Armor**) | +1 each |
| Each even Finesse value, while wielding a proficient melee weapon | +1 each |
| Abilities and equipment | as stated |

### Ranged Defense

Avoiding or disrupting missiles before they strike. You can't plausibly parry an arrow, so innate ranged defense is low. Cover, shields, positioning and armor do the heavy lifting.

| Source | Bonus |
|---|---|
| Base (lost if Agility is below 0) | 1 |
| Shield | +2 |
| Abilities | as stated |

**Cover** adds to whatever defense you use against a ranged attack (see **Cover**).

**Point-blank shots:** if the shooter is within your melee reach, use your **Melee Defense** instead. Cover still applies.

### Dodge Defense

*Status: Exploratory (whether Dodge stays); Locked (formula while it exists)*

Getting out of the way of things you can't block with a weapon or shield, such as:
- a rolling boulder;
- a collapsing structure;
- a dragon's sweeping tail;
- a spell that only needs to touch you.

**Dodge Defense = 1 + 1 per even Agility value** (fewer in medium or heavy armor). You lose the base 1 if Agility is below 0.

## Blocking

*Status: Locked*

Blocking is deterministic. The attacker rolls first; then you see the total, and how many dice were critical, and decide exactly how much stamina to spend.

Each block subtracts your defense value from the incoming damage. Mix the two kinds however you like.

**Perfect Block**
- Stops the blocked damage completely.
- The first perfect block against an attack costs 1 stamina. Each further perfect block **against the same attack** costs 1 more (1, 2, 3…).
- The count resets when you're attacked again, even before your own turn comes around.
- Blocking escalates only within one attack. It isn't part of any other surcharge.

**Grazing Block**
- Always costs **1 stamina**.
- Subtracts your defense value like a perfect block, but **1 damage leaks through** per grazing block.
- Further blocks can't stop the leak, but armor can.
- Grazing blocks don't count toward the perfect-block escalation.

Grazing blocks let you trade a minor wound for stamina. Armor makes them efficient, because it soaks the leaked damage. Against an attacker who over-commits, you can take a graze, keep your stamina, and hit back hard.

**Attack vs. defense efficiency** (*Locked, as a design target*): attacking should be somewhat more stamina-efficient than perfect blocking, so turtling doesn't pay. Grazing blocks and armor are the counterweight.

> **Example: Choosing Blocks**
>
> You're attacked for 9 damage. Your Melee Defense is 4 and your armor is 2.
>
> 1. Perfect block once (1 stamina): 5 damage left.
> 2. Grazing block once (1 stamina): 1 left, plus 1 leaked = 2.
> 3. Your armor soaks the 2.
>
> No injury, for 2 stamina.

## Armor

*Status: see the **Armor** table under Equipment*

Armor reduces injury **after** blocks. It never makes an attack miss.
- It applies to leaked grazing damage and to damage you didn't block.
- Each critical die ignores 1 point of armor.

The armor values and penalties are in **Equipment**.

## Critical Hits

*Status: Locked*

A critical hit means hitting a vital spot. It comes from skill, not luck.

- **Critical range:** a damage die is critical when it rolls its maximum. Each odd Finesse value widens the range by 1, up to +3. See the **Critical Range Table**.
- **The defender knows** how many dice were critical before choosing blocks.
- **Each critical die ignores 1 armor.**
- **Doubling:** if the attack has at least one critical die, double the damage that remains after armor.

**TODO:**
- Confirm that doubling happens once per attack, however many dice were critical.
- Can aim dice be critical?

> **Example: Melee Attack**
>
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

## Ranged Attacks

*Status: Numbers placeholder*

Ranged combat follows the same structure as melee wherever it can.

### Procedure

1. Declare the target.
2. Pay the weapon's flat base cost for the shot (see the **Weapon Table**).
3. Buy any number of aim steps.
4. Roll and total the damage: the weapon's damage plus every aim step.
5. The target may dive for cover with off-turn movement (see **Cover**).
6. The target blocks with Ranged Defense, or with Melee Defense if the shooter is within its reach. Cover applies either way.
7. Apply armor, then critical hits, then lose HP.

**Shooting within an enemy's reach** provokes opportunity attacks from every enemy threatening you, once the shot finishes resolving (see **Opportunity Attacks**).

### Aim

*Status: Exploratory (cost); Numbers placeholder (amount added)*

- **Damage:** each aim step adds **1d6 + Finesse**.
- **Cost:** each aim step is an **action**, so it costs **1 + actions already taken this turn**. The count carries across shots; it doesn't restart.

> **Known problem:** with Maximum HP Damage removed, aim damage can wound in full, so bows are more lethal than intended in this playtest. Fixing this is a priority.

> **Example: Two Aimed Longbow Shots**
>
> First shot: 5 (shot) + 1 (aim) + 2 (aim).
> Second shot: 5 (shot) + 3 (aim) + 4 (aim).
>
> Total: 5 + 1 + 2 + 5 + 3 + 4 = **20 stamina**.

### Range Bands

*Status: Numbers placeholder*

Each ranged weapon lists short, medium and long ranges. Some weapons may adjust them by Finesse; the weapon card says so.

| Band | Effect |
|---|---|
| Short | No penalty. |
| Medium | Your first aim step adds only Finesse, not the 1d6. You must aim at least once, or the shot misses. |
| Long | Your first **two** aim steps add only Finesse. You must aim at least twice, or the shot misses. |
| Beyond long | The shot automatically misses. |

### Cover

*Status: Numbers placeholder*

Cover is defined much as in 5e. Its bonus applies to whatever defense you use against a ranged attack.

| Cover | Bonus |
|---|---:|
| Half | +2 |
| Three-quarters | +5 |

**Diving for cover:** when you're targeted by a ranged attack, you can use off-turn movement after the damage is rolled.
- If you get fully behind cover, it counts as **three-quarters cover** for that attack. A reactive dive helps, but it can't fully negate a shot that's already committed.

> **Example: Diving for Cover**
>
> An archer targets a warrior standing in the open and rolls damage. The warrior buys off-turn movement and dives behind a stone wall.
>
> The attack was already committed, so the wall counts as three-quarters cover: +5 to the defense the warrior uses against this attack.

## Movement

### On-Turn Movement

*Status: Locked (free base movement); Numbers placeholder (distances)*

- **Free movement:** each turn you can move up to your **Movement** for free: 5 squares, +1 per odd Agility value (up to 8). Movement shouldn't be discouraged.
  - You can split it up around your actions.
  - Moving doesn't penalize your aim.
- **Extra movement:** **1 stamina** per purchase, every time.
  - Each purchase moves 1 square, +1 per odd Agility value (up to 4).
  - It isn't an action, and it doesn't touch the off-turn escalation.

### Off-Turn Movement

*Status: Locked*

Turns cover a lot of time, and HP is low. Off-turn movement keeps positioning live all round. It lets you:
- back out when your defenses run low;
- make pursuers spend stamina;
- dive for cover.

**When:**
- right after **any** creature's turn ends, including your own (you can move then, but not act); or
- when you're targeted by a ranged attack (see **Cover**).

**Distance:** each purchase moves 1 square, +1 per odd Agility value (up to 4).

**Cost:** each purchase is an off-turn cost (see **Off-Turn Escalation**).
- Your own on-turn movement and actions never make it pricier, so advancing isn't punished.
- Leaving a threatened square can still provoke opportunity attacks.

### Off-Turn Escalation

*Status: Mechanism open*

Off-turn movement and opportunity attacks compete for the same stamina.
- **What counts:** each off-turn movement purchase and each attack step of an opportunity attack.
- **Cost:** each costs its base amount **+1 for every earlier off-turn cost since the start of your last turn**.
  - Off-turn movement's base is 1.
  - An opportunity attack step's base is the weapon's base cost.
- **Reset:** the track resets at the start of your turn.
- **Separate tracks:** it's separate from the on-turn surcharge. Blocks aren't part of either.

> **Example: Off-Turn Escalation**
>
> Between your turns you:
> 1. move 1 square (1);
> 2. move 1 square (2);
> 3. make an opportunity attack with a dagger, base 1 (3);
> 4. move 1 square (4).
>
> That's **10 stamina**. The 3-stamina opportunity attack needs an opportunity attack cap of at least 3, such as Finesse 3.

## Opportunity Attacks

*Status: Locked (triggers); Mechanism open (avoidance and cap)*

Slipping past an engaged enemy should cost something, without making the battlefield sticky. There are no facing rules.

### Triggers

**Leaving a threatened square:** you provoke an opportunity attack whenever you move out of a square an enemy threatens (one within its reach). That includes:
- moving sideways within its reach;
- leaving its reach;
- stepping closer to an enemy with a reach weapon.

Moving into reach doesn't provoke; only leaving a threatened square does.

**Shooting in melee:** making a ranged attack while within an enemy's reach provokes from **every** enemy threatening you, whether or not it was the target. The opportunity attacks happen after your shot finishes resolving.

### Avoiding Opportunity Attacks

To deny an enemy its opportunity attack for one square you leave, pay **1 stamina**.
- Pay once per enemy, per square.
- The cost is always 1, on or off your turn.
- It doesn't escalate, and it isn't an off-turn cost, so it doesn't add to the off-turn escalation.
- **For now, you can't pay to avoid the opportunity attacks a point-blank shot provokes.**

> **Example: Avoiding Opportunity Attacks**
>
> You leave a square threatened by A and B: 2 stamina.
> The next square is threatened only by C: 1 more.
> The next square is also threatened by C: 1 more, even though you already paid C once.

### Making Opportunity Attacks

**Cost:** an opportunity attack is a normal attack, but its steps go on your **off-turn escalation**, not your on-turn surcharge.
- So you can get efficient damage in even after attacking on your own turn.
- But it makes your later opportunity attacks and off-turn movement more expensive until your next turn.

**Cap:** you can spend at most **1 stamina** on a single opportunity attack. That counts the weapon's base cost and the escalation together.
- **+1 per odd Finesse value** (up to +3 at Finesse 5–6). Some abilities raise it too.
- At the default cap, you can only make an opportunity attack with a base-1 weapon, and only if you haven't already made one or moved off-turn since your last turn began.
- A higher cap lets you:
  - take extra steps;
  - use bigger weapons;
  - make several opportunity attacks;
  - mix opportunity attacks with off-turn movement.

> **Optional rule (Mechanism open):** your cap against a creature is (1 + your Finesse bonus) for **each** square it leaves within your reach, instead of just once.
>
> Example: with no Finesse, a creature that leaves three squares you threaten could be attacked for up to 3 stamina. An enemy that exposes itself for long enough can be punished harder, even by someone without Finesse.
>
> **TODO:** when exactly you make the attack during a multi-square move.

## Conditions and Control Effects

*Status: Locked (principle); TODO (mechanics)*

Anything that takes away a character's agency (grapples, holds, charms, paralysis) must be **progressive and resistible with stamina**. It should never be an instant, all-or-nothing save.
- **Control effects and grappling:** **TODO**.
- **Conditions:** there's no list yet. It's undecided whether there will be universal conditions like "paralyzed", or whether each ability says what it does.

## Dying and Death

*Status: Numbers placeholder*

0 HP is meant to be deadly, dangerous and impactful: clearly worse than being knocked out.

**At 0 HP or below,** you're incapacitated. At exactly 0 HP you're incapacitated but not in System Shock.

**Below 0 HP,** you enter **System Shock**.
- **Starting Shock:** equal to your negative HP. At −2 HP you have 2 Shock.
- **More damage:** taking damage while in System Shock lowers your HP as normal and raises your Shock by the same amount.
- **Dying roll:** at the start of each of your turns, roll **2d12 + Strength**.

  | Roll | Result |
  |---|---|
  | Below 10 + Shock | +1 Shock (bleeding out). Your HP doesn't change. |
  | 10 + Shock to 14 + Shock | No change. |
  | 15 + Shock or more | −1 Shock (stabilizing). |

- **Death:** you die at **10 Shock** or at **−10 HP**.
- **Stabilized:** reaching 0 Shock, on your own or with help, ends System Shock.
  - Helping someone stabilize uses a **Medicine** roll (**TODO:** specifics).
  - You stay at your negative HP and stay incapacitated, but you stop rolling.
- **Damaged while stabilized:** you re-enter System Shock, with Shock equal to the damage taken.

> **Example: System Shock**
>
> 1. You're at 3 HP and take 5 damage. You're now at −2 HP with 2 Shock.
> 2. On your next turn you roll low: 3 Shock, still at −2 HP.
> 3. You take 3 more damage: −5 HP and 6 Shock.
> 4. Over the next few turns you're fully stabilized. You're at −5 HP, so still incapacitated, but no longer in System Shock and no longer rolling.
> 5. You take 1 damage: −6 HP and 1 Shock. You're rolling every turn again until you die or stabilize.
>
> To put the odds in context: at 9 Shock you need 24 or more to drop to 8. Below 19, you reach 10 and die.

---

# Equipment

## Weapons

*Status: Numbers placeholder; the list is incomplete*

Weapons differ in how efficiently they turn stamina into damage.
- **Light weapons** are efficient at low commitment.
- **Heavy weapons** are efficient at high commitment.
- **Strength weapons** are a bit more stamina-efficient.

A weapon card lists its category, base stamina cost, hands, damage per step (or per shot), reach or ranges, and any special properties.

### Weapon Table

| Weapon | Base cost | Damage per step / shot | Hands | Notes |
|---|---:|---|---|---|
| Dagger | 1 | 1d4 + (AGI or FIN) | One | Quick-draw |
| Shortsword | 1 | 1d6 + (AGI or FIN) | One | Quick-draw |
| Longsword | 2 | 1d10 + (STR or AGI) + FIN | Two | One-handed: 1d8 + STR + FIN (STR replaces AGI) |
| Spear | 2 | 1d8 + STR + FIN | **TODO** | Reach: 1 extra square |
| Greatsword | 3 | 1d12 + 2×STR + FIN | Two | |
| Greataxe | 3 | 2d6 + 3×STR | Two | |
| Shortbow | 3 per shot | 1d6 + FIN | Two | Ranges 6 / 12 / 18 squares |
| Longbow | 5 per shot | 1d8 + FIN + STR | Two | Ranges 8 / 16 / 24 squares |

For bows, aim steps work as described in **Aim**. **TODO:** confirm the hands for every weapon except the longsword.

**Draft weapons (TODO: base costs and details):** polearm 1d10 + 3×STR (reach 2); axe 1d10 + 2×STR (cleave); rapier 1d8 + AGI + FIN.

**Reach:** the grid uses 5 ft squares. Most small and medium weapons reach 1 square.

**Proficiency** (*Exploratory*):
- **Sources:** your class core abilities, or Expertise spent on weapons outside your class.
- The proficiency list is **TODO**.

### Weapon Properties

- **Quick-draw** (daggers, shortswords): free to draw between turns, even into a hand you used this turn (see **Drawing Weapons**).
- **Hammer** (hammer-type weapons): ignores 1 armor automatically. **TODO:** hammer stats.
- **Reach:** extends how far the weapon threatens.

## Drawing Weapons

*Status: Exploratory*

This mainly stops archers from shooting and then immediately switching to a melee weapon for extra defense. A rushed archer can still pull an emergency blade.
- **On your turn:** until you use a weapon, you can draw or sheathe weapons freely. Dropping an item is always free.
- **Used hands:** a hand you used this turn for a bow shot or somatic spellcasting can't draw a normal weapon until the start of your next turn.
- **Between turns:** drawing a normal weapon costs **1 stamina**.
- **Exception:** quick-draw weapons are free to draw between turns, even into a hand you used this turn.

## Armor

*Status: Locked (values; applies after blocks); Numbers placeholder (Agility steps); Exploratory (Strength requirements)*

Armor shines when you're taking many attacks. Nimble, high-defense builds shine one-on-one.

| Armor | Value | Agility's defense bonus | Strength requirement |
|---|---:|---|---|
| Light | 1 | Normal (every even value) | None |
| Medium | 2 | Every 3rd point (3, 6) | −1 Agility and −1 Finesse per point of Strength below 1 |
| Heavy | 3 | Every 4th point (4) | −1 Agility and −1 Finesse per point of Strength below 3 |

- **Agility's defense bonus** covers Melee and Dodge Defense. The medium and heavy steps apply whatever your Strength.
- **Strength penalties** lower the attributes themselves.
  - Agility below 0 costs you your base defenses.
  - Finesse below 0 costs you the +1 for wielding a weapon.
- **Spellcasting** isn't possible in any armor (see **Magic**).
- Specific armor or abilities may add other rules.

## Shields

*Status: Locked*

- A shield gives **+2 Melee Defense and +2 Ranged Defense**.
- You only benefit from one shield at a time.
- You can't cast spells while using a shield.

---

# Magic

*Status: Locked (access goal); Numbers placeholder (casting requirements); TODO (everything else)*

Magic should be optional for anyone and never required.

**Casting Requirements** (*Numbers placeholder*):
- A free hand.
- No armor (light, medium or heavy) and no shield, unless an ability says otherwise.
- Each spell states its stamina cost, its strain cost, and how it works.

**Spells run on the same stamina and strain economy as everything else.** Costs vary from spell to spell. Going over your maximum strain applies to spells too.

Spell lists, schools and progression are **TODO**. There are no HP-restoring spells (see **Rest and Healing**).

---

# Character Creation

*Status: Numbers placeholder*

1. Choose a concept.
2. Allocate Expertise (attributes).
3. Allocate Skill Points.
4. Open one or more class trees by buying their core abilities.
5. Buy abilities.
6. Equip starting gear.

**Starting point:** characters start at **level 1** with:
- **25 Skill Points**;
- **5 Expertise Points**, which already include the Expertise Point from the starting levels;
- **1 Ability Point**, normally spent on the core ability of their first class tree.

Attributes start at 0.

## Currencies

*Status: Locked (structure)*

Combat power and out-of-combat flavor are bought with separate currencies. That way, building the character you imagine never costs you effectiveness.

| Currency | Buys |
|---|---|
| **Ability Points (AP)** | Most class tree features. |
| **Expertise** | Attributes; weapon proficiencies outside your class. |
| **Skill Points (SP)** | Skill-check attribute bonuses; skills; languages; ribbon abilities; extra choices under an ability you already own (for example, more maneuvers). |

## Costs

*Status: Numbers placeholder (Expertise, AP); Exploratory (Skill Point costs)*

Costs rise with each purchase. That works as a soft cap, so over-specializing isn't automatically correct.

| Purchase | Cost |
|---|---|
| Attribute point (Expertise) | The Nth point costs N (1, 2, 3…). +3 costs 6 in total; +6 costs 21. Maximum +6. |
| Skill-check attribute bonus (SP) | +1 to +4 per attribute, costing 1, 2, 4, 7 (totals 1, 3, 7, 14). Applies to skill checks only. |
| Skill rank (SP) | The Nth rank costs N. +1 per rank, no hard cap. |
| Core ability (AP) | 1, +1 for each core ability you already own. |
| Tier ability (AP) | 1. |

## Class Trees

*Status: Locked (structure: core ability first, refunds, the martial/caster principle); Mechanism open (tier and core-ability costs)*

Each class is a tree of purchasable features.

**Core ability.** You open a tree by buying its core ability.
- It grants the tree's signature ability, and may grant proficiencies.
- It's the prerequisite for the tree's Tier 1 features.
- Each core ability you already own makes other core abilities cost 1 AP more. Opening a new tree is worth more than going deeper in one, so it costs more.

**Tier abilities.** To reach Tier N of a tree (N above 1), buy that tree's **Tier N ability** for 1 AP.
- It's mostly an opportunity cost, but it carries a minor benefit that fits the tree's theme.
- It's also where fitting mechanics go that players might not choose if they were sold separately.
- Each Tier N ability requires the tree's Tier N−1 ability. The normal Tier N features need only the Tier N ability, though some features may have other prerequisites.

There are no separately unlocked tiers, and tiers don't come from levelling. The tier abilities *are* the unlocks.

**Other rules:**
- Some features belong to no tree, such as languages and weapon proficiencies. It's possible to own no tree at all.
- If a later feature grants something you already bought, the earlier purchase is refunded.
- **Martial trees** have one defining strain ability that stays roughly the same but scales, plus mostly flat passives and active abilities that cost no strain.
- **Caster trees** put many Ability Points into spell ranks.
- An Ability Point purchase should be a real power boost, not just more versatility.

### Core Abilities

*Status: Numbers placeholder (Fighter, Rogue, Barbarian); Exploratory (Monk)*

Each core ability is simple, powerful and defining.

| Class | Core ability |
|---|---|
| Fighter | Gain 3 strain to recover your normal stamina recovery amount now. You can do this at any time. |
| Rogue | Gain 3 strain to take your turn now, skipping it later in the round. Or skip your turn and take it after a later turn. You can do this between anyone's turns, as long as you haven't taken your turn this round. |
| Barbarian | Gain 1 strain to recover the biggest stamina expenditure you spent on an attack step. You can do this at any time on your turn. |
| Monk | Gain 1 strain: your perfect block costs don't escalate for the current attack. |
| Wizard (and other casters) | Grants spellcasting (**TODO**). |

### Candidate Abilities

*Status: Exploratory; not yet assigned to trees*

- **Heavy Swing:** +1 stamina per attack step to penetrate 2 armor.
- **Feint:** a Cunning contest; if it works, the defender declares blocks first. **TODO:** contests aren't defined yet.
- **Riposte:** an opportunity attack after a perfect block.
- **Tactical Withdrawal:** 2 stamina to move before an attack resolves.
- **Press the Advantage, Momentum, Fluid Footwork, Step Through:** names only. **TODO**.

---

# Character Advancement

*Status: Numbers placeholder*

Levels run from 0 to 99, roughly like 5e's levels 1–20 in fine-grained steps. High-level characters should dominate low-level ones.

Each level grants a benefit based on its last digit:

| Last digit | Benefit |
|---:|---|
| 0 | Ability Point |
| 1 | Expertise Point |
| 2 | Ability Point |
| 3 | +1 maximum stamina, +1 maximum strain, +1 Skill Point |
| 4 | Expertise Point |
| 5 | +1 stamina recovery, +1 strain recovery, +1 Skill Point |
| 6 | Expertise Point |
| 7 | Ability Point |
| 8 | +1 maximum stamina, +1 maximum strain, +1 Skill Point |
| 9 | Expertise Point |

The stamina and strain lines are what the round(Level / 5) and round(Level / 10) formulas produce.

"Tier" may still be used as a loose name for a band of levels. But tiers in a class tree come only from tier abilities.

---

# Skill Checks

*Status: Exploratory; the skill system is TODO*

Outside combat, most uncertain actions use:

**2d12 + attribute + skill**

- **The attribute** includes any Skill Point bonus.
- **The GM decides** whether to roll at all, and what the result means. DCs are suggestions, not requirements. The dice are a tool for the GM to use however they see fit.
- **Each skill uses exactly one attribute.** Where a skill would straddle two attributes, split it, so players aren't arguing for their best stat. The GM can make an explicit exception.
- The skill list is **TODO**. Ideas so far:
  - Inspire (Will) vs. Persuade (Cunning).
  - Grouping skills under each attribute, such as Intelligence → horsepower and knowledge; Cunning → people and the world.

Skill checks stay much lighter than combat.

---

# Rest and Healing

*Status: Mechanism open (rest); Locked (no HP-restoring magic, for now)*

**Each night of rest:**
- recover **1 HP**;
- recover **4 + round(Level / 10) strain** (or see the alternative under **Strain**).

**Healing:** HP comes back only through rest. **No HP-restoring spells** like 5e's *Healing Word* or *Cure Wounds* are planned. Don't assume a healer role that refills HP.

Lasting harm is fair in this game because you control whether you take hits.

---

# Running the Game

*Status: Locked (principles)*

**NPCs use the same rules as PCs.** Humanoid NPCs follow the same stamina rules as the player characters.

**NPCs value their own survival.**
- Most intelligent opponents shouldn't automatically fight to the death.
- An NPC that throws itself into grazing hits makes fights miserable: it dies quickly, but the players are left carrying the injuries.
- Combat usually ends when one side retreats, surrenders, is defeated, or achieves its objective.

**Telegraph dangerous threats whenever practical.** Players can only make good tactical decisions with enough information. How best to do this is still an open problem.

**As GM, you should:**
- present meaningful tactical situations;
- use the rules as tools rather than obstacles.

---

# Quick Reference

## Attack Sequence

**Melee:** Declare target → declare steps and pay → roll → blocks → armor → double if critical → lose HP

**Ranged:** Declare target → pay shot → buy aim → roll → dive for cover → blocks → armor → double if critical → lose HP

## Stamina Costs

| What | Cost | Escalates on |
|---|---|---|
| Melee attack step | Weapon base + actions this turn | On-turn surcharge (it's an action) |
| Ranged shot | Weapon base, flat | — |
| Aim step | 1 + actions this turn | On-turn surcharge (it's an action) |
| Extra on-turn movement | 1 per purchase (1 square + odd AGI) | — |
| Off-turn movement | 1 + earlier off-turn costs | Off-turn escalation |
| Opportunity attack step | Weapon base + earlier off-turn costs (capped) | Off-turn escalation |
| Avoid an opportunity attack | 1 per enemy, per square | — |
| Perfect block | 1, 2, 3… within one attack | Resets every attack |
| Grazing block | 1 | — |
| Draw a normal weapon between turns | 1 | — |
| Strain ability over maximum strain | +1 per point over, counted after paying | — |

## Triangular Numbers

The running totals for perfect blocks, attribute costs and skill ranks.

| N | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| Total | 1 | 3 | 6 | 10 | 15 | 21 | 28 | 36 | 45 | 55 |

## Attribute Bonus Table

| Value | Odd-value bonuses | Even-value bonuses (normal / medium armor / heavy armor) |
|---:|---:|---|
| 0 | 0 | 0 / 0 / 0 |
| 1 | 1 | 0 / 0 / 0 |
| 2 | 1 | 1 / 0 / 0 |
| 3 | 2 | 1 / 1 / 0 |
| 4 | 2 | 2 / 1 / 1 |
| 5 | 3 | 2 / 1 / 1 |
| 6 | 3 | 3 / 2 / 1 |

**What each column means:**
- **Odd-value bonuses:**
  - Agility: initiative, movement squares.
  - Finesse: critical range, opportunity attack cap.
  - Cunning: initiative.
- **Even-value bonuses:**
  - Agility: Melee and Dodge Defense. The medium and heavy armor columns apply here.
  - Finesse: Melee Defense while wielding a proficient melee weapon. Armor doesn't change this.

## Critical Range Table

| Die | Finesse 0 | Finesse 1–2 | Finesse 3–4 | Finesse 5–6 |
|---|---|---|---|---|
| d4 | 4 | 3–4 | 2–4 | Always |
| d6 | 6 | 5–6 | 4–6 | 3–6 |
| d8 | 8 | 7–8 | 6–8 | 5–8 |
| d10 | 10 | 9–10 | 8–10 | 7–10 |
| d12 | 12 | 11–12 | 10–12 | 9–12 |

## Sample Character

*Illustrative only*

A level-1 **Fighter**, using the starting 5 Expertise and 1 Ability Point.

| | |
|---|---|
| **Attributes** | STR 2 (cost 3), AGI 1 (1), FIN 1 (1), INT 0, WIL 0, CUN 0 |
| **HP** | 8 |
| **Stamina** | Maximum 14; recovers 4 per turn |
| **Strain** | Maximum 6 |
| **Gear** | Longsword (one-handed), shield, medium armor (2). STR 2 meets medium armor's requirement. |
| **Melee Defense** | 4: base 1 + proficient weapon 1 + shield 2 |
| **Ranged Defense** | 3: base 1 + shield 2 |
| **Dodge Defense** | 1 |
| **Movement** | 6 squares; 2 squares per off-turn purchase |
| **Initiative** | 2d12 + 1 (odd AGI) |
| **Critical range** | d8 crits on 7–8 |
| **Opportunity attack cap** | 2 |
| **Attack** | Longsword: base 2, 1d8 + 3 per step |
| **Core ability** | Fighter (1 AP) |
| **Skill Points** | 25 (skills TODO) |

---

# Open Questions

**Combat**
- Ranged aim lethality: aim damage can wound in full. This is the first problem to solve.
- A better name for "action".
- Whether Dodge Defense stays in the game.
- Area attacks, such as a fireball or dragon breath. One idea: measure cover from the blast's origin, and let a dive out of the area count as three-quarters cover.
- An "out of the fight but alive" state above 0 HP.
- The TODO details marked through this packet.

**Attributes**
- Combat benefits for Intelligence, Will and (beyond initiative) Cunning.
- Strength's +1 HP, which scales poorly at high levels.

**Effects**
- Conditions: will there be universal conditions like "paralyzed", or will each ability say what it does?
- Control effects and grappling (see **Conditions and Control Effects**).

**Characters**
- Skills and their list.
- Proficiency lists.
- The remaining weapons, and armor tables.
- Class trees and their abilities.
- Magic: its scope, spells and progression.

**GM material**
- Monster stat blocks.
- Encounter guidelines.
- A complete combat example.
- A character sheet.

---

# Not in This Version

These ideas are deliberately left out of the current rules. They're strong candidates to come back, so don't build around their absence.
- **Maximum HP Damage:** only part of an attack's damage could become HP loss; the rest would only cost stamina. This is the leading fix for ranged aim lethality.
- **Damage reducing maximum stamina:** would let a character be worn out of the fight before reaching 0 HP.
- **Lingering and permanent injuries.**
- **Extended contests** for grapples, holds and charms.
- **Spell schools and spell progression.**
- **NPC aggression profiles:** balance-tested defaults for how NPCs play.

---

# Defined Terms

| Term | Meaning | Defined in |
|---|---|---|
| Action | A melee attack step or an aim step. Each costs +1 per earlier action this turn. | Actions and the On-Turn Surcharge |
| Attack step | One unit of commitment in a melee attack, adding one weapon damage roll. | Melee Attacks |
| Aim step | Adds 1d6 + FIN to a ranged attack; it's an action. | Aim |
| On-turn surcharge | +1 per action already taken this turn. | Actions and the On-Turn Surcharge |
| Off-turn escalation | +1 per earlier off-turn cost (off-turn movement, opportunity attack steps) since your turn began. | Off-Turn Escalation |
| Perfect block | Subtract your defense; costs 1, 2, 3… within one attack. | Blocking |
| Grazing block | Subtract your defense; costs 1; 1 damage leaks through. | Blocking |
| Critical die | A die rolling within its critical range; ignores 1 armor; any critical doubles damage after armor. | Critical Hits |
| Threatened square | A square within an enemy's melee reach. | Opportunity Attacks |
| Opportunity attack cap | The most stamina you can spend on one opportunity attack: 1 + odd FIN. | Making Opportunity Attacks |
| Off-turn movement | Movement bought after any creature's turn, or when targeted by a ranged attack. | Off-Turn Movement |
| Cover | Half +2, three-quarters +5, to the defense used against a ranged attack. | Cover |
| System Shock | The dying track below 0 HP. | Dying and Death |
| Strain | The rest-recovered pool for abilities and spells. | Strain |
| Core ability | The first purchase in a class tree. | Class Trees |
| Tier ability | The 1-AP purchase that opens a tree's next tier. | Class Trees |
