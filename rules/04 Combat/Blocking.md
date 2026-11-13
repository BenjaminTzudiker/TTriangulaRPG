---
up: "[[Playtest Packet]]"
prev: "[[Defenses]]"
next: "[[Critical Hits]]"
---
# Blocking

*Status: Locked*

Blocking is deterministic. The attacker rolls first; then you see the total, and how many dice were critical, and decide exactly how much stamina to spend.

Each block subtracts your defense value from the incoming damage. Mix the two kinds however you like. You declare them together, so their order doesn't matter.

**Perfect Block**
- Stops the blocked damage completely.
- The first perfect block against an attack costs 1 stamina. Each further perfect block **against the same attack** costs 1 more (1, 2, 3…).
- The count resets when you're attacked again, even before your own turn comes around.
- Blocking escalates only within one attack. It isn't part of any other surcharge.

**Grazing Block**
- Always costs **1 stamina**.
- Subtracts your defense value like a perfect block, but **1 damage leaks through** per grazing block.
- The leak is 1 point of the damage that block stopped. A grazing block with nothing left to stop leaks nothing; count your perfect blocks first.
- Further blocks can't stop the leak, but armor can.
- Grazing blocks don't count toward the perfect-block escalation.

Grazing blocks let you trade a minor wound for stamina. Armor makes them efficient, because it soaks the leaked damage. Against an attacker who over-commits, you can take a graze, keep your stamina, and hit back hard.

**Attack vs. defense efficiency** (*Locked, as a design target*): attacking should be somewhat more stamina-efficient than perfect blocking, so turtling doesn't pay. Grazing blocks and armor are the counterweight.

> [!example] Example: Choosing Blocks
> You're attacked for 9 damage. Your Melee Defense is 4 and your armor is 2.
>
> 1. Perfect block once (1 stamina): 5 damage left.
> 2. Grazing block once (1 stamina): 1 left, plus 1 leaked = 2.
> 3. Your armor soaks the 2.
>
> No injury, for 2 stamina.
