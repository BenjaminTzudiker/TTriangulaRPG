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
