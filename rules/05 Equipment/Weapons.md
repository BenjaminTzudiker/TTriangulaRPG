---
up: "[[Playtest Packet]]"
prev: "[[Dying and Death]]"
next: "[[Drawing Weapons]]"
---
# Weapons

*Status: Numbers placeholder; the list is incomplete*

Weapons differ in how efficiently they turn stamina into damage.
- **Light weapons** are efficient at low commitment.
- **Heavy weapons** are efficient at high commitment.
- **Strength weapons** are a bit more stamina-efficient.

A weapon card lists its category, base stamina cost (a shot cost, for ranged weapons), hands, damage per step (or per shot), reach or band width, and any special properties.

## Weapon Table

| Weapon | Base cost | Damage per step / shot | Hands | Notes |
|---|---:|---|---|---|
| Dagger | 1 | 1d4 + (AGI or FIN) | One | Quick-draw |
| Shortsword | 1 | 1d6 + (AGI or FIN) | One | Quick-draw |
| Longsword | 2 | 1d10 + (STR or AGI) + FIN | Two | One-handed: 1d8 + STR + FIN (STR replaces AGI) |
| Spear | 2 | 1d8 + STR + FIN | **TODO** | Reach: 1 extra square |
| Greatsword | 3 | 1d12 + 2×STR + FIN | Two | |
| Greataxe | 3 | 2d6 + 3×STR | Two | |
| Shortbow | 2 per shot | 1d4 + FIN | Two | Band width 2; Precise |
| Longbow | 4 per shot | 1d8 + STR | Two | Band width 3; Strength 1 |
| Warbow | 6 per shot | 1d10 + STR | Two | Band width 4; Strength 3; Piercing 1 |
| Superheavy warbow | 8 per shot | 1d12 + STR | Two | Band width 5; Strength 5; Piercing 2. Provisional |

**Bows:**
- A shot is an action, so it costs its shot cost + the on-turn surcharge (see [[Actions and the On-Turn Surcharge]]).
- Aim works as described in [[Aim]], and range as described in [[Range Bands]].
- **Strength N** is the bow's Strength requirement. Each point of Strength you're short shortens its band width by 1 square.

**TODO:** confirm the hands for every weapon except the longsword.

**Draft weapons (TODO: base costs and details):** polearm 1d10 + 3×STR (reach 2); axe 1d10 + 2×STR (cleave); rapier 1d8 + AGI + FIN.

**Reach:** the grid uses 5 ft squares. Most small and medium weapons reach 1 square.

**Proficiency** (*Exploratory*):
- **Sources:** your class core abilities, or Expertise spent on weapons outside your class.
- The proficiency list is **TODO**.

## Weapon Properties

- **Quick-draw** (daggers, shortswords): free to draw between turns, even into a hand you used this turn (see [[Drawing Weapons]]).
- **Piercing N:** the weapon ignores N armor. Critical dice ignore armor on top of this, but armor can't go below 0.
- **Hammer** (hammer-type weapons): Piercing 1. **TODO:** hammer stats.
- **Reach:** extends how far the weapon threatens.
- **Precise** (shortbows): Finesse adds to the shot's total, but like aim it doesn't add to the wound directly. Instead, the aim limit for this weapon is the **higher of its damage die and your Finesse** (see [[Aim]]). So unblocked damage up to your Finesse reaches HP, as long as blocks and armor don't stop it.

> [!example] Example: A Precise Shot
> An archer with Finesse 4 shoots a shortbow: 1d4 + FIN plus the free aim die. They roll 1 on the d4 (not critical: at Finesse 4, a d4 crits on 2–4) and 3 on the aim die, for 1 + 4 + 3 = **8**. The target has no armor.
> - **The target blocks 4, leaving 4.** Without Precise, the aim limit would let only the d4's 1 through. With it, the limit is the higher of 1 and Finesse 4, so the target loses **4 HP**.
> - **The target blocks 6 instead, leaving 2.** The limit is still 4, but only 2 got through, so the target loses **2 HP**. Precise raises what can reach HP; it never adds damage past what blocks and armor let through.
