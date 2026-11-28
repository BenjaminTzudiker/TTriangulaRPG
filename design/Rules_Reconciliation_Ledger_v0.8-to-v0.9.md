> **⚠ STATUS: WORKING NOTES — NOT CANONICAL RULES.**
> This is an in-progress reconciliation of the v0.8 playtest packet against the design transcript, awaiting the designer's rulings.
> - Only entries marked **DECISION** reflect confirmed rules. Even then, check each entry's **Firmness**: many decided rules have placeholder numbers, and their **Intent** line is what to evaluate. "Locked" means a deliberate current choice, not off-limits: a compelling reason can reopen anything.
> - **PROPOSAL**, **UNCERTAIN** and **ABANDONED** entries are *not* rules; don't treat them as current design.
> - The designer's rulings (logged verbatim in Part G) are folded into Parts A–D. **Part H (SHELVED)** holds ideas deliberately left out of the current rules; they are not rules.
> - **Playtest Packet v0.9** is now the rules source and incorporates these rulings (through round 9). This ledger remains the record of where each rule came from and how firm it is.
> - **Later packets:** the entries describe packet v0.9. `rules/CHANGELOG.md` records every change since then. Seven entries carry a **Later changes** line for what packet 0.11.0 changed (CB-2, CB-9, MV-1, MV-2, MV-4, MV-5 and CP-7; the reaction to a shot is under MV-2), five for packet 0.11.1 (CR-2, MV-3, MV-5, EQ-2 and H-4), and four for packet 0.11.2 (CB-9, IN-1, CP-9 and MV-1). Part H gained H-7, the stamina cap, after 0.11.2, and H-8, Dodge Defense, which packet 0.11.3 shelved (DF-3 has a **Later changes** line for it). It gained H-9, recovery holds, after 0.11.4, and H-10, strain, in packet 0.12.0 (CR-4, CR-5, MG-2, CP-1, CP-7 and CP-8 have **Later changes** lines for 0.12.0). MV-3 has one for packet 0.11.4, which moved the opportunity attacks a shot in melee provokes to the moment the target is declared. The rest have not been brought up to date, and neither have the summaries in Parts A to C.

# Rules Reconciliation Ledger: Playtest Packet v0.8 vs. Design Transcript

*An accuracy pass only. It records what you decided; it doesn't critique or rebalance anything. Written from a full read of all 495 of your turns plus a chunk-by-chunk read of the whole transcript (2,048 pp.).*

---

## How to read this

**Statuses**
- **DECISION**: you stated it, or explicitly accepted or adopted it.
- **PROPOSAL**: floated (by ChatGPT, or by you as a "maybe") and never confirmed.
- **ABANDONED**: rejected or replaced.
- **UNCERTAIN**: ambiguous. Each one says why. These are for you to rule on.
- **SHELVED**: deliberately out of the current rules, but a strong candidate to return (Part H). Not a rule; don't critique it as one. Do consider it when its problem comes up.

**Packet comparison**
- **Matches**: the packet agrees.
- **Contradicts**: the packet says something different.
- **Missing**: the packet omits it entirely.
- **Undefined**: the packet references it but never defines it.
- **Not in transcript**: the packet has it, but you never said it.

**Firmness (how settled is it?)** A second axis, separate from Status. Status says *whether* you decided something. Firmness says *which part* is settled, so a reader knows whether to critique the exact numbers or only the intent behind them.
- **Locked**: intent and specifics both settled *for now*. Locked means "current, deliberate choice", not "closed to change": a compelling enough reason can reopen anything in this ledger. Labels describe how settled something is today, so a critic knows what was deliberate. They are not a list of untouchables.
- **Intent locked, numbers placeholder**: the shape and purpose are decided; the values may move. Critique the intent and the shape. Treat the numbers as illustrative.
- **Intent locked, mechanism open**: the goal is decided, but the procedure isn't (or is under review).
- **Exploratory**: a trial idea; the shape itself is open.
- Some entries split the label by part (e.g. "Locked (timing) / Intent locked, numbers placeholder (amount)").

**Intent**: what the rule is *for*, so a critique can protect the goal while challenging the implementation.
- **STATED** means it comes from your own words, with a page reference.
- **INFERRED** means I deduced it. Treat INFERRED firmness labels and intents as my reading, for you to confirm.
- Hedges like "for now", "placeholder", "assume" and "TBD" are cited where they set the label.

**Page references**
- [p.N] is the "N of 2048" page marker.
- Text extraction sometimes puts the marker at the end of a page instead of the start, so treat every page as ±1.
- Quotes are your words unless marked *(ChatGPT)*.

**Verification.** After drafting, an independent reviewer checked the 20 highest-impact claims in this ledger against the transcript, looking for anything later that overturns them. None were refuted. Two were refined: the initiative entry (B10/CB-9) and the aim cost (RG-2).

**Two caveats about the sources**
1. **The packet is ChatGPT's export, written before the conversation ended.**
   - ChatGPT generated packet v0.2–v0.8 at pp.1545–1555 from your consolidation answers at pp.1469–1484.
   - You only gave process approvals ("Sounds good. Do that now."). At p.1556 you noted it "still has notes you left yourself for edits in future revisions."
   - The conversation then ran another ~500 pages. Several mechanics were reworked there (pp.1576–2048), mostly as *proposals you raised but never locked*. Those are marked UNCERTAIN (post-export).
   - The packet's "Editorial Revision Notes", "Editing TODO", "Editorial Refactor Plan", "Cross-Reference Checklist" and "Suggested Table of Contents" sections are ChatGPT scaffolding, not rules.
2. **The PDF itself is clipped at the right margin.** Some line-final words are missing in both the PDF and the text (e.g. "Grazing blocks always cost ▯ stamina", p.1480). Where that matters, the entry says so.

---

## Where things stand (after your rulings of 2026-11-01)

- **Nine rounds of your rulings are folded into the entries** (Parts A–D). Part G keeps them verbatim.
- **New status, SHELVED:** deliberately out of the current rules, but kept as a strong candidate. Part H holds the shelved ideas:
  - Maximum HP Damage
  - damage reducing max stamina
  - lingering injuries
  - control / extended contests
  - spellcasting details
  - NPC profiles
- **Biggest rule changes from your rulings:**
  - **Opportunity attacks:**
    - Avoidance costs 1 stamina per square, per enemy.
    - Making an OA is capped at 1 stamina, +1 per odd Finesse.
    - OAs share an off-turn escalation with off-turn movement.
    - Shooting inside anyone's reach provokes OAs.
  - **The on-turn surcharge counts actions:** melee attack steps and aim steps. Ranged shots now pay a flat base cost.
  - **Armor** keeps Agility's every-3rd/4th scaling and adds placeholder Strength thresholds. Below-0 Agility costs you your base defenses.
  - **Class trees:**
    - Core abilities cost +1 AP per core already owned.
    - Tier N abilities are the only way to reach Tier N.
    - The 10-level tier advancement is gone.
  - **Death:** below 0 HP you enter System Shock; you die at 10 Shock or −10 HP.
  - **Healing:** no HP-restoring spells are planned.
- **Packet errors confirmed:**
  - the Strain example (9 stamina, not 7);
  - Dodge (half Agility);
  - off-turn movement after any creature's turn.
- **Still open:** Part F lists what's left.

---

## PART A: Terms the packet references but never defines (now ruled)

| # | Packet term | Current state | Firmness | Entry |
|---|---|---|---|---|
| A1 | Critical hits | Natural max; +1 range per odd FIN (max +3); defender sees crits first; each crit die ignores 1 armor; ≥1 crit doubles HP damage after armor | Locked | CB-6 |
| A2 | Maximum HP Damage | Not in the current rules | SHELVED | H-1 |
| A3 | Opportunity attacks | Leaving a threatened square or shooting in anyone's reach provokes; pay 1 per square per enemy to avoid | Triggers locked; avoidance mechanism open | MV-3 |
| A4 | Action surcharge | Actions are melee attack steps and aim steps, +1 per prior action this turn; ranged shots pay a flat base cost | Mechanism open | CB-2 |
| A5 | Perfect Block progression | 1, 2, 3… within one attack; resets per attack | Locked | CB-3 |
| A6 | Off-turn movement costs | 1, 2, 3… on the off-turn escalation shared with OAs; resets at the start of your turn; 1 square, up to 4 with AGI | Locked | MV-2, MV-4 |
| A7 | Character progression | Start at level 1; per-level table; trees via core and Tier N abilities | Intent locked; numbers or mechanism placeholder | CP-1, CP-2 |
| A8 | Finesse OA stamina | Replaced: cap of 1 stamina per OA, +1 per odd FIN | Mechanism open | MV-5 |
| A9 | Aim steps | 1d6 + FIN per step; each step is an action | Cost exploratory; step value placeholder | RG-2 |
| A10 | Range bands | Medium: first aim step adds FIN only, and ≥1 aim required. Long: the same for the first two aim steps, and ≥2 aim required. Beyond long misses | Numbers placeholder | RG-3 |
| A11 | Learning spells early | Idea only | Exploratory / SHELVED | H-5 |
| A12 | "Proficient" weapon | Sources: class cores, Expertise, Skill Points; no list | Exploratory | CP-6 |
| A13 | Initiative roll | 2d12 (placeholder); +1 per odd AGI and per odd CUN; no tiebreaker | Exploratory | CB-9 |
| A14 | Tiers | Tier N abilities bought in each tree | Mechanism open | CP-2 |
| A15 | STR "heavy armor synergy" | STR thresholds reduce armor penalties (placeholder); +1 HP is suspect | Exploratory | AT-1, EQ-1 |
| A16 | Conditions | No list; maybe none universal | Exploratory | CT-1 |
| A17 | Extended contests / grappling | TBD; ideas shelved | Mechanism open | CT-1, H-4 |
| A18 | Cover | +2 / +5; reactive dive = 3/4 | Numbers placeholder | RG-4 |

---

## PART B: Where the packet is wrong or out of date (after your rulings)

| # | Packet says | Current rule | Entry |
|---|---|---|---|
| B1 | Strain example costs 7 | **9**: excess strain is counted after paying the ability's own strain | CR-5 |
| B2 | Dodge = 1 + Agility | 1 + floor(AGI/2); base 1 lost if AGI < 0; Dodge's inclusion uncertain | DF-3 |
| B3 | Off-turn movement after "another creature" | After any creature's turn, including your own | MV-2 |
| B4 | Off-turn movement has its own progression | Shares the off-turn escalation with OAs; resets at the start of your turn | MV-4 |
| B5 | Ranged attack "while threatened in melee" uses Melee Defense | Shooter in the target's reach: target uses Melee Defense **+ cover**; shooting in anyone's reach provokes OAs | DF-2, MV-3 |
| B6 | OA payment covers a whole move | 1 stamina per square per enemy | MV-3 |
| B7 | Global "hands occupied" rule | Hands used for a shot or somatic casting can't draw normal weapons until your next turn; drawing between turns costs 1; daggers and shortswords are exempt | EQ-3 |
| B8 | Armor reduces Agility scaling (no numbers) | Every 3rd/4th point, plus placeholder STR thresholds | EQ-1 |
| B9 | Every ten levels form a Tier | Tiers reached only by buying Tier N abilities | CP-1, CP-2 |
| B10 | Odd AGI +1 init and initiative = AGI + CUN | +1 per odd AGI and +1 per odd CUN; no tiebreaker | CB-9 |
| B11 | Dive after rolling | Confirmed: all offense steps, then all defense steps | CB-7, RG-1 |
| B12 | Select trees freely | Core abilities cost +1 AP per core already owned | CP-2 |
| B13 | Max HP Damage as a core step | SHELVED | H-1 |
| B14 | Strain recovered "after resting" | 4 + level bonus per night (mechanism open); alternative 1 per 6 hours | CR-4 |
| B15 | Aim steps aren't Actions; each shot is surcharged | Reversed: aim steps are actions, shots are flat | CB-2, RG-2 |
| B16 | Strength gives max HP damage | Shelved with H-1 | AT-1 |
| B17 | Spellcasting armor interaction TODO | No casting in any armor or with a shield, unless an ability allows it | MG-2 |

---

## PART C: Settled rules the packet leaves out (current)

- **Movement:**
  - Base on-turn movement 5 squares, up to 8 with Agility, free and interleaved with actions [MV-1].
  - Extra on-turn movement: 1 stamina per purchase, flat; 1 square, +1 per odd Agility [MV-1].
- **Opportunity attacks:** full trigger text, including point-blank shooting; the OA cap and how it's computed [MV-3, MV-5].
- **Defenses:** losing base defenses below 0 Agility [AT-2, DF-1].
- **Armor:** the every-3rd/4th Agility scaling and the STR thresholds [EQ-1].
- **Weapons:** dagger, shortsword and greatsword stats; hammers ignore 1 armor; dagger/shortsword drawing rules [EQ-2, EQ-3].
- **Attribute costs:** Expertise is triangular; Skill Point attribute bonuses cost 1/2/4/7; specific skills are triangular with no hard cap [CP-5, SK-2, SK-3].
- **Class trees:** core abilities and their escalating cost; Tier N abilities [CP-2]; class cores, including the Monk's 1-strain version [CP-7].
- **Casting:** not in armor or with a shield [MG-2].
- **Death and healing:** System Shock and −10 HP death [IN-1]; no HP-restoring magic [IN-4].
- **Start:** level 1 [CP-1]. The attribute is named **Will** [AT-4].

---

# PART D: Full ledger (one entry per mechanic)

**Firmness index.** Each entry also has an **Intent** line. SHELVED items are in Part H.

| Entry | Firmness |
|---|---|
| CR-1 Hit Points | Intent locked, numbers placeholder. Formula changed (4+STR → 6+STR); you called 6+STR a quasi-placeholder in this review. |
| CR-2 Maximum Stamina | Intent locked, numbers placeholder. Confirmed as current but "not set in stone" (your ruling, 2026-11-01). |
| CR-3 Stamina recovery (regen) | Locked (timing) / Intent locked, numbers placeholder (amount). Timing restated with reasons three times [p.127, p.788, p.1275]. The formula 4 + round(level/10) is yours [p.1469]. Only its "placeholder" status was my inference, which you accepted (your ruling, 2026-11-01). |
| CR-4 Strain (maximum and recovery) | Intent locked, numbers placeholder (max). Intent locked, mechanism open (recovery). |
| CR-5 Exceeding maximum strain | Locked. Stated with worked examples, then explicitly confirmed ("Yes, we are going with…") [p.1135, p.1469]. |
| CR-6 Damage reducing max stamina → SHELVED | SHELVED (Part H) |
| CR-7 Overexertion (lower max stamina to gain stamina) | n/a (abandoned). |
| AT-0 The six attributes | Locked (the six) / open (Will vs Willpower). Stable since p.163. |
| AT-1 Strength | Exploratory. |
| AT-2 Agility | Intent locked, numbers placeholder. |
| AT-3 Finesse | Intent locked, numbers placeholder. |
| AT-4 Intelligence / Will / Cunning (combat benefits) | Exploratory. |
| AT-5 Attribute ranges and meaning | Intent locked, numbers placeholder. The descriptions are a draft, revised by you (your ruling, 2026-11-01); edit freely. |
| DF-1 Melee Defense | Intent locked, numbers placeholder. |
| DF-2 Ranged Defense | Locked (structure). Intent locked, numbers placeholder (cover values). |
| DF-3 Dodge Defense | Exploratory (whether Dodge stays in the system). Locked (formula while it exists). |
| CB-1 No to-hit roll; the damage roll is the attack | Locked. Core premise since p.90; corrected ChatGPT on it [p.783]. |
| CB-2 Actions and the on-turn surcharge | Intent locked, mechanism open. |
| CB-3 Perfect Block | Locked. Same structure since p.90; formalized [p.1480]. |
| CB-4 Grazing Block | Locked. |
| CB-5 Maximum HP Damage → SHELVED | SHELVED (Part H) |
| CB-6 Critical hits | Locked. |
| CB-7 Attack resolution order | Locked (principle). Intent locked, mechanism open (exact steps). |
| CB-8 Attack vs defense efficiency (design constraint on numbers) | Locked (as a constraint). This is a target, not a number. |
| CB-9 Initiative and turn structure | Exploratory. |
| MV-1 On-turn movement | Locked (free base movement).; Intent locked, numbers placeholder (5→8 squares; extra movement). |
| MV-2 Off-turn movement | Locked. |
| MV-3 Opportunity attacks: triggers and avoidance | Locked (triggers). Intent locked, mechanism open (avoidance cost). |
| MV-4 Off-turn escalation | Intent locked, mechanism open. |
| MV-5 Making opportunity attacks: cost and cap | Intent locked, mechanism open. |
| RG-1 Ranged attack procedure | Intent locked, numbers placeholder. |
| RG-2 Aim steps | Exploratory (cost: probably locked, but not confidently). Intent locked, numbers placeholder (what each step adds). |
| RG-3 Range bands | Intent locked, numbers placeholder. |
| RG-4 Cover | Intent locked, numbers placeholder. |
| RG-5 Area attacks (fireball, dragon breath) | Exploratory. "What if…" [p.1320]. |
| EQ-1 Armor | Locked (armor values 1/2/3; order after blocks).; Intent locked, numbers placeholder (the Agility steps).; Exploratory (the STR-threshold penalties). |
| EQ-2 Weapons | Intent locked, numbers placeholder. The list is **partially incomplete**. |
| EQ-3 Drawing weapons and occupied hands | Exploratory. |
| EQ-4 Dagger/shortsword quick-draw → merged into EQ-3 | merged (see entry) |
| EQ-5 Shields | Locked. Stated without hedge [p.1481]. |
| MG-1 Magic access | Locked (as a goal). |
| MG-2 Casting requirements | Intent locked, numbers placeholder. |
| CP-1 Levels and advancement | Intent locked, numbers placeholder. |
| CP-2 Class trees: core abilities and tier abilities | Intent locked, mechanism open. This is the current implementation to test. |
| CP-3 Additional trees (multiclassing) → merged into CP-2 | merged (see entry) |
| CP-4 Starting currencies | Intent locked, numbers placeholder. "about 25… about 5" [p.1277]; "Assume" [p.1473]. |
| CP-5 Expertise costs | Intent locked, numbers placeholder. "Assume… standard triangle" [p.1474]. |
| CP-6 What each currency buys; class trees | Locked (structure). Stated in detail [p.1473]. |
| CP-7 Class core abilities | Intent locked, numbers placeholder (Fighter, Rogue, Barbarian).; Exploratory (Monk). |
| CP-8 Martial vs caster tree structure | Locked (as principle). |
| CP-9 Candidate abilities you kept | Exploratory. A candidate list. |
| SK-1 Skill checks | Exploratory. Skill system details are TBD (your ruling, 2026-11-01). |
| SK-2 Skill-point attribute bonus | Exploratory (skill details TBD). |
| SK-3 Specific skill proficiency | Exploratory (skill details TBD). |
| SK-4 Skill list and sub-groups | Exploratory (TBD). |
| IN-1 0 HP, dying and death | Intent locked, numbers placeholder. |
| IN-2 Lingering injuries → SHELVED | SHELVED (Part H) |
| IN-3 Rest | Intent locked, mechanism open. |
| IN-4 Healing | Locked (for now: no HP-restoring magic). |
| CT-1 Conditions and agency-removing effects | Locked (principle).; Exploratory (conditions list). |
| CT-2 Control resolution procedure → SHELVED | SHELVED (Part H) |
| CT-3 Control details → SHELVED | SHELVED (Part H) |
| CT-4 In-combat skill contests (older) | n/a (abandoned). |
| GM-1 NPCs use PC mechanics and value survival | Locked (principle). |
| GM-2 NPC aggression profiles → SHELVED | SHELVED (Part H) |
| PL-1 Reference tables; stamina tokens | Locked (tables) / Exploratory (tokens). [p.2044] |
| PL-2 Presentation instructions you gave | Locked. |

## CR: Core resources

### CR-1 Hit Points
- **Firmness:** Intent locked, numbers placeholder. Formula changed (4+STR → 6+STR); you called 6+STR a quasi-placeholder in this review.
- **Intent:** STATED: HP is a small pool of real injury, so one clean hit can take someone out ("one solid stab is meant to take someone out of commission" [p.1156]). It does not grow with level, unlike D&D [p.1469]; you confirmed this in review. It heals slowly [p.90]. STR adds HP so sturdy frontliners survive longer [p.330]. Critique the ratio of HP to expected damage per level, not the constant 6.
- **Rule:** Max HP = 6 + STR. HP does not increase with level. Recover 1 HP per night of rest. HP is lasting injury, kept deliberately small: "one solid stab is meant to take someone out of commission" [p.1156].
- **Status:** DECISION
- **Packet:** Matches.
- **History:**
  - Small "meat" pool where one hit can KO or kill [p.90].
  - Then HP = 4 + STR [p.330].
  - Base 6 floated [p.1156].
  - 6 + STR fixed [p.1469].
- **Evidence:** "Max HP is now equal to 6 + strength. HP does not increase with level. Characters recover 1 HP with each night of rest." [p.1469]

### CR-2 Maximum Stamina
- **Firmness:** Intent locked, numbers placeholder. Confirmed as current but "not set in stone" (your ruling, 2026-11-01).
- **Intent:** STATED: a small pool, single digits to low double digits [p.87], "often double digit" [p.2044]. It's about the same size for everyone; roles come from spending it more or less efficiently [p.334]. Injury should modestly lower performance without a combat death spiral [p.1021]. STR shouldn't become a big stamina stat [p.330, p.615].
- **Rule:** 6 + current HP + round(level/5). The level bonus is +1 at levels ending in 3 or 8, so round() rounds halves up.
  - Current stamina can never exceed the maximum. If a lower maximum falls below current stamina, current drops to match; otherwise current is unaffected (your ruling, 2026-11-01).
- **Status:** DECISION
- **Packet:** Matches.
- **History:**
  - current HP + ceil(level/10) [p.99] → four layers [p.105] → level only [p.334] → HP + STR + level [p.998] → 2×HP floated [p.1150] → final [p.1469].
- **Evidence:** [p.1469]; confirmed (your ruling, 2026-11-01).
- **Later changes:**
  - *Packet 0.11.1 (your ruling, 2026-11-17):* hold tokens count toward the maximum. Whenever something would take you over it (a wound, your recovery, an ability), you lose the excess and choose where it comes from: current stamina, tokens, or some of each. "That will be the universal rule", with no special order for each case, "since it's assumed that the players can play optimally if they choose."
    - *Now in:* the rules notes Stamina and Holds.

### CR-3 Stamina recovery (regen)
- **Firmness:** Locked (timing) / Intent locked, numbers placeholder (amount). Timing restated with reasons three times [p.127, p.788, p.1275]. The formula 4 + round(level/10) is yours [p.1469]. Only its "placeholder" status was my inference, which you accepted (your ruling, 2026-11-01).
- **Intent:** STATED: recover a meaningful but partial share each turn (about 33–40% of max, rising "only a touch" with level [p.793]), so fights last a few rounds [p.115]. Never tie it to a stat, because that stat would become mandatory [p.783]. End-of-turn timing is a safety net against zero defense, rewards high initiative, and discourages passivity [p.788, p.1275].
- **Rule:** At the **end of your own turn**, recover 4 + round(level/10). That's +1 at levels ending in 5. No stat affects it.
- **Status:** DECISION
- **Packet:** Matches.
- **History:**
  - Should come from several stats [p.117].
  - Then half of max [p.218, p.334].
  - Then ~33–40% of max, rising "only a touch" with level, and not stat-tied because STR would become mandatory [p.783–793].
  - Then fixed at 4 + bonus [p.1469].
  - End-of-turn timing was set early [p.127] and reaffirmed [p.788, p.1275].
- **Evidence:** "Stamina recovery starts at 4 + level bonus… Stamina recovery is not impacted by stats." [p.1469]. On timing: "At the end of a character's turn. This is partially so there's a bit of a safety net… It's also to solve the issue of 'wasting' your first stamina regen" [p.1275].

### CR-4 Strain (maximum and recovery)
- **Firmness:** Intent locked, numbers placeholder (max). Intent locked, mechanism open (recovery).
- **Intent:** STATED: one shared, rest-recovered pool replaces X/day abilities and spell slots, so multiclassing or buying more abilities doesn't buy more uses [p.902, p.998]. It shouldn't tie pacing to a calendar day or let one class's rest needs hold the party hostage [p.553, p.1041].
- **Rule:**
  - Max strain = 6 + round(level/5).
  - Recovery: 4 + round(level/10) strain per night of rest.
  - **Alternative under consideration:** recover 1 strain per 6 hours of rest, with no strain-recovery bonus at levels ending in 5.
- **Status:** DECISION (recovery mechanism open)
- **Packet:** Matches the main rule; it lacks the alternative and the "mechanism open" flag.
- **History:**
  - Abandoned along the way: overexertion; an INT-based strain limit; per-tree pools; stat-keyed recovery [p.130–598].
  - Settled on a single pool [p.998, p.1469].
- **Evidence:** [p.1469]. Ruling B14 + clarification 9 (your ruling, 2026-11-01).
- **Later changes:**
  - *Packet 0.12.0 (your call, 2026-11-22 to 2026-11-24):* strain is removed from the current rules and shelved as **H-10** (see Part H and the rules note `Not in This Version`).

### CR-5 Exceeding maximum strain
- **Firmness:** Locked. Stated with worked examples, then explicitly confirmed ("Yes, we are going with…") [p.1135, p.1469].
- **Intent:** STATED: a soft cap. You can keep using abilities past your limit, but each use leaves you more exposed that turn, rather than locking you out or crippling you afterwards [p.474].
- **Rule:** You may exceed max strain. Every strain ability costs +1 stamina per point of excess, counted **after** adding this ability's own strain ("including the one currently being used").
- **Status:** DECISION. Confirmed in your ruling B1: at 1 over the limit, a 3-strain / 4-stamina ability takes you to 4 over, so it costs 4 + 4 = 8 stamina.
- **Packet:** The rule text matches. **The worked example contradicts it.** At max 8 and current 10, a 5 stamina / 2 strain spell takes you to 12, which is 4 over, so it costs **9** stamina. The packet says 7.
- **History:**
  - First version raised the cost of non-cantrip spells by the excess [p.474].
  - Extended to all strain abilities [p.1135].
  - Confirmed at p.1469.
- **Evidence:** "max strain is 11… The 6th time their strain is 12 which is 1 over max, so it costs 7 stamina instead. The seventh fireball costs 9 stamina" [p.1135]. "Yes, we are going with the 'over max strain -> extra stamina on all strain abilities, including the one currently being used.'" [p.1469]
- **Later changes:**
  - *Packet 0.12.0:* shelved with strain as **H-10**.

### CR-6 Damage reducing max stamina → SHELVED
- **Firmness:** n/a. Moved to Part H (SHELVED, H-2).
- **Status:** SHELVED. Excluded for its complexity, but worth serious consideration because it solves characters only "going down" at 0 HP (your ruling, 2026-11-01).

### CR-7 Overexertion (lower max stamina to gain stamina)
- **Firmness:** n/a (abandoned).
- **Rule:** None.
- **Status:** ABANDONED ("No overexertion", your ruling, 2026-11-01).
- **History:** requested once for the v0.3 playtest [p.334]; superseded by strain overage (CR-5).

---

## AT: Attributes

### AT-0 The six attributes
- **Firmness:** Locked (the six) / open (Will vs Willpower). Stable since p.163.
- **Intent:** STATED: separate the traits D&D lumps together (acrobat vs watchmaker; brave but naive) [p.1]. No stat is an auto-pick, which is why there's no Constitution [p.163].
- **Rule:** Strength, Agility, Finesse, Intelligence, Will(power), Cunning. There is no Constitution and no Charisma. Presence and leadership come through the mental stats. Agility is whole-body movement and cardio endurance; Finesse is fine motor control.
- **Status:** DECISION
- **Packet:** Matches, with two drifts:
  - The packet's Strength says "body mass". You moved it from size to power when "Build" became Strength [p.9].
  - The packet's Agility omits endurance [p.9].
- **History:**
  - Build became Strength [p.9].
  - Constitution rejected because it would be an auto-pick [p.163].
  - You also used the name "Might" once [p.876].
  - You use both "Will" and "Willpower".
- **Evidence:** "making Build more focused on strength rather than just size (maybe even rename it back to Strength), having Agility include the cardiovascular health aspects of endurance" [p.9]. "I don't want to have constitution be an auto-pick" [p.163]. "Agility governs macro movement… while finesse is micro movements" [p.881]
- **Notes:** UNCERTAIN on the name: Will or Willpower?

### AT-1 Strength
- **Firmness:** Exploratory.
- **Intent:** STATED: STR makes strong characters more survivable and powers heavy weapons, but must not become mandatory by also feeding stamina or regen [p.330, p.783]. Its role in armor is new (see EQ-1).
- **Rule:**
  - +1 HP per point (reminder: HP also raises max stamina).
  - Adds to damage on weapons that use it.
  - Reduces armor penalties (EQ-1).
- **Status:** DECISION (placeholder). You flagged +1 HP as suspect, because it "scales poorly at higher levels with the rest of the rules" (your ruling, 2026-11-01).
- **Packet:** "Heavy armor synergy (future rules)" now has a placeholder: the STR thresholds in EQ-1. The packet's Max HP Damage bullet is SHELVED (H-1).
- **History:** Expertise once alternated +1 HP / +1 max stamina [p.749]; then just +1 HP "for now" [p.1469].

### AT-2 Agility
- **Firmness:** Intent locked, numbers placeholder.
- **Intent:** STATED: Agility is the cleanest defensive stat (melee and dodge) plus mobility and initiative. Armor limits it so heavy-armor builds don't need it [p.330, p.1192].
- **Rule:**
  - **Odd** values: +1 initiative, +1 on-turn movement square, +1 square per off-turn movement purchase.
  - **Even** values: +1 Melee and Dodge Defense. In medium armor this counts every 3rd point; in heavy armor, every 4th (EQ-1).
  - **If Agility drops below 0** (e.g. from armor penalties), you lose your base 1 Melee, Ranged and Dodge Defense.
- **Status:** DECISION
- **Packet:** Mostly matches. **Missing:** the every-3rd/4th numbers and the below-0 rule.
- **Evidence:** [p.1276], [p.1469]. Rulings B2, B10, clarifications 5 and 7 (your ruling, 2026-11-01).

### AT-3 Finesse
- **Firmness:** Intent locked, numbers placeholder.
- **Intent:** STATED: crits come from skill, not luck [p.751]. Finesse gives weapon users defense, which matters most for heavy-armor builds [p.1192]. Finesse is the opportunity-attack stat (MV-5).
- **Rule (Finesse caps at 6):**
  - **Odd values (1, 3, 5):** +1 crit range, and +1 to your opportunity-attack stamina cap (MV-5).
  - **Even values (2, 4, 6):** +1 Melee Defense while holding a melee weapon.
  - Finesse below 0 (from armor, EQ-1) removes the +1 Melee Defense for holding a weapon.
  - (Finesse's floor on Max HP Damage is shelved with H-1.)
- **Status:** DECISION
- **Packet:** Mostly matches. Its OA wording is replaced by the MV-5 cap.
- **Clarified:** Finesse does **not** add initiative. The earlier mention was a typo (your ruling, 2026-11-01).
- **Evidence:** [p.1469], [p.1480]; clarifications 3 and 4 (your ruling, 2026-11-01).

### AT-4 Intelligence / Will / Cunning (combat benefits)
- **Firmness:** Exploratory.
- **Intent:** STATED: mental stats must matter to non-casters and not be dump stats [p.124]. Be careful with cross-arena rewards [p.1277].
- **Rule:**
  - **Cunning:** +1 initiative at odd values. This is a placeholder whose job is to show that Cunning improves initiative.
  - Everything else: TBD.
  - The attribute is named **Will** (not Willpower).
- **Status:** DECISION (placeholder)
- **Packet:** Matches the TODO. The Cunning initiative bonus is new.
- **Evidence:** Rulings B10, clarification 6 (your ruling, 2026-11-01).

### AT-5 Attribute ranges and meaning
- **Firmness:** Intent locked, numbers placeholder. The descriptions are a draft, revised by you (your ruling, 2026-11-01); edit freely.
- **Intent:** STATED:
  - A grounded scale where 2 is average [p.743].
  - Being average should be cheap and dumping should gain little [p.1434].
  - Skill-point bonuses are breadth that doesn't apply under combat pressure [p.1409].
- **Rule:**
  - 0 to +6 from Expertise, applying everywhere.
  - +0 to +4 more from Skill Points, for skill checks only, so up to +10 on checks.
- **Overall framing:** **no value on this scale is superhuman.**
  - Even 10 is the limit of real human ability.
  - This is not a heroic-fantasy or shounen game where top characters suplex 5,000 lb monsters (your ruling, 2026-11-01).
  - *My reading, not your words:* anything beyond human limits would come from magic or abilities, not from raw attributes.
- **Draft scale** (lines marked † are my interpolation):
  - **0:** clearly deficient, but still an adventurer. For Strength, "an old weak wizard" [p.740].
  - **1:** functional but below average [p.1429].
  - **2:** an average person (not an average adventurer) [p.743, p.1429].
  - **3:** a bit above average. For Strength, someone who "would beat the average person in arm wrestling consistently" [p.743].
  - **4:** trained through regular use, but not exceptional. For Strength, a manual worker or regular gym-goer [p.743].
  - **5:** standout [p.1429].
  - **6:** † exceptional; among the best in a region.
  - **7:** genius-level; among the best in the world at it [p.1429].
  - **8:** † elite even among the world's best.
  - **9:** one of a handful alive. For Strength, a world's-strongest-man contender ("a 7ft tall Eddie Hall, not a comic book superhero") [p.743].
  - **10:** the pinnacle of human ability; once in a generation. Only reachable on skill checks (+6 Expertise, +4 Skill Points) (your ruling, 2026-11-01).
- **History:** you originally placed "strongest man alive" at 9 [p.743] and "pinnacle" at 9 [p.1429]. With the +10 cap, the pinnacle moved to 10 (your ruling, 2026-11-01).
- **Status:** DECISION (ranges and framing); draft (descriptions).
- **Packet:** The ranges match; the scale is missing.

---

## DF: Defenses

### DF-1 Melee Defense
- **Firmness:** Intent locked, numbers placeholder.
- **Intent:** STATED: the defense number is applied once per block, so it must stay small [p.659]. It's built from several sources so no single stat owns defense [p.1979]. You think of the base 1 as "a baseline ability to weakly avoid damage" (your ruling, 2026-11-01).
- **Rule:**
  - Base 1, lost if Agility is below 0.
  - +1 holding a proficient weapon. You lose it if your Finesse is below 0, e.g. from armor (confirmed, your ruling, 2026-11-01).
  - +1 more for a second proficient weapon in the off hand, **or** +2 for a shield (one shield only).
  - Then add floor(AGI/2), adjusted by armor (EQ-1), and floor(FIN/2), which needs a melee weapon.
- **Status:** DECISION
- **Packet:** Matches. **Missing:** the below-0 Agility rule.
- **Wording note:** you prefer "you have a base 1… which you lose if your Agility goes below 0" over "nonnegative Agility grants +1".
- **Evidence:** [p.1469–1470]. Ruling B2 (your ruling, 2026-11-01).
- **Later changes:**
  - *Packet 0.12.1 (your calls, 2026-11-25 and 2026-11-26):* weapon proficiencies (**H-11**) and dual wielding (**H-12**) shelved; the melee weapon and even-Finesse Melee Defense bonuses apply to any melee weapon, and a second melee weapon no longer adds +1 Melee Defense.

### DF-2 Ranged Defense
- **Firmness:** Locked (structure). Intent locked, numbers placeholder (cover values).
- **Intent:** STATED: you can't plausibly parry arrows, so innate ranged defense is low. Counterplay comes from cover, positioning, shields, armor and magic [p.183, p.1142, p.1218]. Skilled archers are dangerous but answerable [p.186, p.188].
- **Rule:**
  - Base 1, lost if Agility is below 0. +2 with a shield.
  - Cover: +2 half, +5 three-quarters (RG-4).
  - **Point-blank:** if the shooter is within the target's melee range, the target uses its Melee Defense. (Cover still helps, because cover applies to any defense against a ranged attack; see RG-4.)
  - Making a ranged attack inside *anyone's* melee range provokes OAs (MV-3).
- **Status:** DECISION
- **Packet:** **Contradicts:** it says "while threatened in melee" and drops the cover clause.
- **Wording (your ruling, 2026-11-01):**
  - Write "use your Melee Defense".
  - Word cover as a bonus when **defending against a ranged attack**, not as a bonus to Ranged Defense.
  - Whether you may use Ranged Defense if it's higher is unspecified.
- **Evidence:** [p.1472]. Ruling B5 (your ruling, 2026-11-01).

### DF-3 Dodge Defense
- **Firmness:** Exploratory (whether Dodge stays in the system). Locked (formula while it exists).
- **Intent:** STATED: a rarely used avoid-only defense for things you can't parry: a rolling boulder, a collapsing building, a touch spell. It's the 5e Dex-save equivalent [p.1276, p.1470].
- **Rule:** 1 + floor(AGI/2). Armor reduces it through its Agility modifications (EQ-1). The base 1 is lost if Agility is below 0.
- **Status:** DECISION (inclusion uncertain)
- **Packet:** **Contradicts.** "1, plus Agility" reads as full Agility.
- **Evidence:** [p.1470]. Ruling B2, clarification 7 (your ruling, 2026-11-01).
- **Later changes:**
  - *Packet 0.11.3 (your proposal, 2026-11-19):* shelved for now (H-8). Nothing in the game used it yet.
    - *Now in:* the rules note Not in This Version.

---

## CB: Combat resolution

### CB-1 No to-hit roll; the damage roll is the attack
- **Firmness:** Locked. Core premise since p.90; corrected ChatGPT on it [p.783].
- **Intent:** STATED: deterministic defense, so you can outplay rather than out-roll; the damage roll carries the hit [p.90, p.783].
- **Rule:** There is no separate hit roll. The attacker's damage total is what the defender must block. Each attack is an abstraction of many swings.
- **Status:** DECISION
- **Packet:** Matches (implied).
- **Evidence:** "there's no 'to hit' roll, the damage roll includes the hitting portion as well" [p.783]. On abstraction: "An 'attack action' can include an arbitrary number of swings" [p.192]

### CB-2 Actions and the on-turn surcharge
- **Former names:** attack triangle, exertion; briefly "beat".
- **Naming:** called **"action"** for now. Known issues with the name:
  - It's misleading next to D&D, where "action" means a fixed slot per turn.
  - It implies each attack step is a separate action, when several steps are really one committed attack.
  - It clashes with everyday uses of "action" in rules text.

  Alternatives considered: beat, tempo, push, commit, exertion. Exertion was rejected because it overlaps with stamina and strain.
- **Firmness:** Intent locked, mechanism open.
- **Intent:** STATED: one stamina economy instead of action/bonus/reaction slots or Extra Attack [p.176, p.1361]. Doing several things in a turn should be "possible but expensive" [p.1226]. There should be some way to combine multiple actions per turn (your ruling, 2026-11-01).
- **Rule (current implementation to test; not confidently locked):**
  - Each melee attack step and each aim step is an **action**. Each action costs **+1 per action already taken this turn**.
  - **Melee attack step** = weapon base cost + actions so far. Melee has no separate "initiation" cost; each step is just more attacking. Greatsword (base 3), two steps: 3 + 4 = 7.
  - **Ranged:** each shot pays the weapon's **flat** base cost, which isn't an action and isn't surcharged. Each aim step costs 1 + actions so far.
    - Example: 2 longbow shots (base 5) with 2 aim steps each = 5 + 1 + 2 + 5 + 3 + 4 = **20** stamina.
  - **Spells:** each spell says how it works.
  - **Not actions:** extra on-turn movement (MV-1, always 1 stamina).
  - The surcharge resets each turn. Off-turn costs use a separate track (MV-4).
- **Status:** DECISION (mechanism open)
- **Packet:** **Contradicts:** the packet surcharges each ranged shot and exempts aim steps. You reversed both.
- **History:**
  - Triangular per extra die [p.90].
  - Defender's block count resets while the attacker's continues [p.490].
  - +1 per action [p.1226, p.1480].
  - Aim steps moved into the surcharge; ranged shots made flat (your ruling, 2026-11-01).
- **Evidence:** Ruling A4; clarifications 3 and 4 (your ruling, 2026-11-01).
- **Later changes:**
  - *Packet 0.10.0:* a ranged shot became an action: the shot cost + the surcharge. The flat shot above no longer applies.
  - *Packet 0.11.0 (your rulings, 2026-11-16):* the on-turn surcharge and the off-turn escalation (MV-4) became **one escalation**.
    - An action is a melee attack step, a ranged shot, an aim step or a **dash**, the new name for movement you pay for (MV-1, MV-2). That reverses "Not actions: extra on-turn movement" above.
    - Each action costs its base +1 per action you've taken since your last turn ended. The count includes dashes taken outside your turn.
    - It resets only when your turn ends, as you recover stamina. Before your first turn of a fight it counts every action since the fight began.
    - Not actions: free movement, blocks, the free aim die, drawing a weapon, paying to avoid an opportunity attack and, as a placeholder, making one (MV-5).
    - *Why:* so that dashing between turns to close a gap limits what you can do on your next turn, and so that one rule prices bought movement where there were two.
    - *Now in:* the rules note Actions and Escalation (Mechanism open). `rules/CHANGELOG.md`, 0.11.0, has the reasons, the evidence and the known costs.

### CB-3 Perfect Block
- **Firmness:** Locked. Same structure since p.90; formalized [p.1480].
- **Intent:** STATED: blocking gets steadily pricier within one attack, so a big enough commitment can break through. It resets per attack: blocking "only escalates within one attack" [p.1783].
- **Rule:**
  - Subtract your defense value from the incoming damage.
  - The first perfect block costs 1 stamina; each additional one **in the same attack** costs 1 more (1, 2, 3…).
  - The count resets when you're attacked again, even before your own turn.
  - Blocking is deterministic: you see the damage, then choose blocks.
  - Blocking "only escalates within one attack" and is not part of any other escalation.
- **Status:** DECISION
- **Packet:** Undefined. It says "triangular progression" with no start or reset.
- **History:**
  - 1 → N, 3 → 2N, 6 → 3N [p.90].
  - Triangular kept over diminishing-block [p.196–202].
  - Fixed block per step; only the cost escalates [p.809].
  - Formalized [p.1480].
  - Kept separate from reaction escalation [p.1783].
- **Evidence:** "This starts at 1 stamina, and increases in cost by 1 stamina for each additional perfect block made in this attack (resets if attacked again, even if the defender hasn't had a turn yet)" [p.1480]

### CB-4 Grazing Block
- **Firmness:** Locked.
- **Intent:** STATED: a cheap attrition option. You accept a minor wound to save stamina and counterattack an over-committed attacker. Armor makes it efficient [p.91, p.799].
- **Rule:** Subtract your defense value. 1 damage leaks through per grazing block. Further blocks can't stop the leak; armor and post-block effects can. **Costs 1 stamina** each, however many blocks you've made.
- **Status:** DECISION
- **Packet:** Matches.
- **Evidence:** [p.793]. Confirmed "Grazing blocks cost 1" (your ruling, 2026-11-01).

### CB-5 Maximum HP Damage → SHELVED
- **Firmness:** n/a. Moved to Part H (SHELVED, H-1).
- **Status:** SHELVED. Not in the current rules, but a strong contender. It's your initial proposed fix for the unsolved problem of how lethal ranged aiming is, and a way to differentiate STR, AGI and FIN (your ruling, 2026-11-01).
- **Consequence while shelved:** all damage that gets past blocks and armor becomes HP damage, including aim damage. Bows are therefore more lethal in this playtest than intended.

### CB-6 Critical hits
- **Firmness:** Locked.
- **Intent:** STATED: crits mean hitting a vital spot through skill (Finesse, aim), not luck [p.751, p.1235]. Die size is a tradeoff: bigger dice hit harder but crit less, and daggers slip through armor [p.1480].
- **Rule:**
  - A damage die crits on its **natural max**. Each odd Finesse value adds +1 crit range (up to +3): d12 crits on 9–12, d6 on 3–6, d4 always at high Finesse.
  - Crits are checked after the roll, and the defender knows how many before blocking.
  - **Each crit die ignores 1 armor.**
  - If the attack has ≥1 crit, **double the HP damage that remains after armor.** While Max HP Damage is shelved, there is no cap step before the doubling.
- **Status:** DECISION
  - UNCERTAIN minor details: doubling is once per attack ("if the attack crit"); whether aim dice can crit.
- **Packet:** Undefined in the packet.
- **Evidence:** [p.1275], [p.1471], [p.1480]. Ruling A1 "locked" (your ruling, 2026-11-01).

### CB-7 Attack resolution order
- **Firmness:** Locked (principle). Intent locked, mechanism open (exact steps).
- **Intent:** STATED: all offensive steps come before all defensive steps (your ruling, 2026-11-01).
- **Rule:**
  - **Offense:**
    1. Declare the target.
    2. Declare the stamina (attack steps, or shot + aim steps) and pay it.
    3. Roll and add up the total.
  - **Defense:**
    4. Reactions such as diving for cover (ranged attacks).
    5. Declare perfect and grazing blocks.
  - **Resolution:**
    6. Armor (crit dice ignore 1 each).
    7. Double if any crit.
    8. Lose HP.
  - You commit to the whole attack up front. A further attack keeps your place in the surcharge, but the defender's block count resets. Shorthand: "3 × [1d10 + STR + FIN]".
- **Status:** DECISION
- **Packet:** Matches, except that the Max HP Damage step is removed while shelved.
- **Evidence:** [p.1470–1471], [p.1481]. Ruling B11 (your ruling, 2026-11-01).

### CB-8 Attack vs defense efficiency (design constraint on numbers)
- **Firmness:** Locked (as a constraint). This is a target, not a number.
- **Intent:** STATED: attacking should be a bit more stamina-efficient than perfect blocking, to prevent turtling. Defense catches up through grazing blocks and armor, not by nerfing attacks [p.726, p.793, p.799].
- **Rule:** Per stamina, attacking should be somewhat more efficient than perfect blocking, to prevent turtling. The counterweight is the flat 1-stamina grazing block plus armor. Each step adds the same amount; only the cost rises. Don't also shrink the per-step amount.
- **Status:** DECISION
- **Packet:** Missing (design intent).
- **Evidence:** "I do want attacking to be overall a more efficient use of stamina to prevent turtling" [p.726]. "It's always 6+6+6+... or 4+4+4+..., not 6+3+1.5+..." [p.809]

### CB-9 Initiative and turn structure
- **Firmness:** Exploratory.
- **Intent:** INFERRED: a 5e-like flow in which Agility and Cunning (reflexes and reading the situation) set the order.
- **Rule:**
  - Roll **2d12** (temporary placeholder; your ruling, 2026-11-01) + modifier. The modifier is +1 per odd Agility value and +1 per odd Cunning value.
  - **No tiebreaker for now.**
  - Each turn: actions and movement in any order, then end the turn, then recover stamina.
- **Status:** DECISION (placeholder)
- **Packet:** **Contradicts:** it says "Agility + Cunning" for both the modifier and the tiebreaker.
- **History:**
  - d20 + mod [p.284].
  - Odd Agility +1 [p.1276].
  - AGI + CUN [p.1481].
  - Odd Agility + odd Cunning (your ruling, 2026-11-01).
- **Evidence:** Ruling B10, clarification 6 (your ruling, 2026-11-01).
- **Later changes:**
  - *Packet 0.9.1:* the modifier became Cunning, +1 per point: 2d12 + Cunning. Still a placeholder, with no tiebreaker.
  - *Packet 0.11.0 (your rulings, 2026-11-16):* each turn now goes: a **dash phase** before the turn starts (MV-2), then the turn, then the end of the turn, when you recover stamina and your escalation resets (CB-2). The first turn of a fight has a dash phase too.
    - The dash phase gives priority by initiative, and assumes a clear order. Ties are for the initiative rules to settle: "For now, tiebreaker is TBD - the entire initiative roll system is a known placeholder".
    - *Why a dash phase before the first turn:* without it, only the creature highest in initiative acts before anyone else can move.
    - *Now in:* the rules note Starting Combat and Turn Structure (Exploratory).
  - *Packet 0.11.2 (your ruling, 2026-11-17):* a placeholder tiebreaker, "first tiebroken by who has a higher AGI + CUN, and then by opposed die rolls until all ties are broken". The packet makes the opposed rolls a d12 roll-off. It's there so a first playtest can run; you called the close gang-up result with holds "another sign that we need to revamp initiative".
    - *Now in:* the rules note Starting Combat and Turn Structure; restated in Agility and Cunning.

---

## MV: Movement and opportunity attacks

### MV-1 On-turn movement
- **Firmness:**
  - Locked (free base movement).
  - Intent locked, numbers placeholder (5→8 squares; extra movement).
- **Intent:** STATED: movement is an active, interleaved part of combat and shouldn't be discouraged [p.1274]. Melee characters need a way to catch archers who retreat off-turn [p.1706]. Advancing shouldn't make later retreat pricier [p.1712].
- **Rule:**
  - **Base:** free, up to your Movement (5 squares at +0 Agility, +1 per odd Agility, up to 8). It can be interleaved with your actions. There is no aim penalty for moving.
  - **Extra on-turn movement:** **1 stamina per purchase, flat** (no escalation).
    - Each purchase moves 1 square, +1 per odd Agility (so up to 4), like off-turn movement.
    - It doesn't feed the off-turn escalation.
    - It isn't an action: it always costs 1 stamina (your ruling, 2026-11-01).
- **Status:** DECISION
- **Packet:** **Missing** (base values and extra movement).
- **History:** v0.3 had 1 stamina per extra square [p.334] → TBD [p.1481] → proposed [p.1712] → adopted (your ruling, 2026-11-01).
- **Evidence:** [p.1481], [p.1712]; clarification 6 (your ruling, 2026-11-01).
- **Later changes:**
  - *Packet 0.9.1:* each extra on-turn purchase moved 1 square, with no Agility bonus. The cost stayed 1 stamina, flat.
  - *Packet 0.11.0 (your rulings, 2026-11-16):* extra on-turn movement no longer exists as its own purchase. To go further than your free movement you **dash** (MV-2): an action, costing 1 + your escalation (CB-2), moving 1 square +1 per odd Agility.
    - That reverses "It isn't an action: it always costs 1 stamina" above, and brings the Agility bonus back.
    - Free movement is unchanged: 5 squares, +1 per odd Agility, split around your actions, no aim penalty.
    - *The intent above, as it stands:*
      - Movement "shouldn't be discouraged": still true of free movement.
      - "Advancing shouldn't make later retreat pricier" still holds for a retreat after your turn: the escalation resets when your turn ends. A dash taken on your turn, after attacking, does cost more.
      - "Melee characters need a way to catch archers who retreat off-turn" is not served by this version. A fighter chasing an archer is worse off than under packet 0.10.1 (the changelog's 0.11.0 entry gives the figures), and you left that to later changes on the ranged side.
    - *Why:* one rule for bought movement where there were two, and moving and attacking is taxed more than just moving.
    - *Now in:* the rules notes Free Movement (Locked for free movement; distances are placeholders) and Dash.
  - *Packet 0.11.2 (your ruling, 2026-11-18):* you can't move diagonally past the corner of a wall or pillar. If either square beside the diagonal is one, you go around (2 squares, not 1), dashes included.
    - Creatures and low obstacles (a crate, a low wall) don't block a diagonal, and you can still attack and threaten diagonally around a corner. That wording came from Claude's recommendation, which you accepted.
    - *Why:* a body can't slip through a wall's corner (P3); the packet said nothing about it before a first playtest; doorways and corners become real positions (P2). It's D&D 3.5's rule.
    - *Left out:* your second half, that a diagonal step past a square an enemy threatens provokes. It would make threat reach farther than the weapon and make some steps into reach provoke (the triggers are Locked: moving into reach doesn't provoke). It's now an open question.
    - *Now in:* Free Movement (Corners; Locked). Engine: preset `exp-0.11.2`.

### MV-2 Off-turn movement
- **Firmness:** Locked.
- **Intent:** STATED: big turns plus low HP make engaging suicidal. Off-turn movement lets you position aggressively, back out when your defenses run low, force pursuers to spend stamina, and dive for cover [p.91, p.762].
- **Rule:**
  - **When:** right after **any** creature's turn ends, including your own (you can't act then), or when targeted by a ranged attack.
  - **Cost:** each purchase is an off-turn cost on your **off-turn escalation** (MV-4), costing 1, 2, 3… It resets at the start of your turn and is shared with your opportunity attacks.
  - **Distance:** each purchase moves 1 square, up to 4 with Agility.
  - On-turn movement doesn't raise the cost.
  - Moving out of threatened squares can provoke OAs (MV-3).
- **Status:** DECISION
- **Packet:** **Contradicts:**
  - "another creature" should be any creature.
  - It describes a separate progression, but movement shares the off-turn track with OAs.
  - It omits the 4-square cap.
- **Evidence:** [p.1274], [p.1481]. Rulings A6, B3, B4 (your ruling, 2026-11-01).
- **Later changes:**
  - *Packet 0.11.0 (your rulings, 2026-11-16):* off-turn movement became the **dash**, one purchase used on your turn and off it.
    - **When:** on your turn; in the **dash phase** before any turn (your own, the turn after yours, anyone's); or when targeted by a ranged attack. "After any creature's turn" became "before every turn", which adds one moment: before the first turn of a fight.
    - **Cost:** 1 + your escalation (CB-2). The off-turn escalation (MV-4) is gone. Nothing you did on your turn makes a dash after it pricier, because the escalation has just reset. Every dash makes what you do before your next turn ends pricier, that turn's attacks included.
    - **Distance:** unchanged: 1 square, +1 per odd Agility, up to 4.
    - **How many:** any number each time, including none. You noted this may change for some occasions, such as being targeted by a ranged attack.
    - **Order in a dash phase:** anyone may say they want to dash, without saying where. Of those, the highest in initiative goes. Then anyone may say so again. The phase ends when nobody wants to. This settles what the entry left unstated (Review F14, which had suggested lowest first).
    - A dash taken in reaction to a shot is an action like any other ("For now, yes, this counts").
    - *Why:* the intent above is unchanged. Two things now let a creature that gives ground get away from several attackers: pursuers pay for each dash out of their own attack (CB-2), and there is a dash phase before the first turn. The order rule answers Review F14.
    - *Now in:* the rules note Dash (Mechanism open; Numbers placeholder (distance)). Off-Turn Movement, the note it replaces, was Locked.

### MV-3 Opportunity attacks: triggers and avoidance
- **Former names:** guarded movement, reposition carefully, "maneuver".
- **Firmness:** Locked (triggers). Intent locked, mechanism open (avoidance cost).
- **Intent:** STATED: slipping around or past an engaged enemy should cost something without making battlefields sticky; no facing rules [p.1324, p.1349]. OAs aren't free for the attacker either (MV-5).
- **Rule:**
  - **Triggers:**
    - Moving out of a square threatened by an enemy, including lateral moves within reach, leaving reach, and advancing on a reach weapon. The first square entering reach doesn't count.
    - Making a ranged attack within **anyone's** melee range. Every enemy threatening the shooter may make an OA once the ranged attack finishes resolving, even if it wasn't the target.
  - **Avoidance:** pay **1 stamina per square, per enemy**, to deny that enemy the OA for that square. Pay several times to deny several enemies, and again for each further threatened square you leave.
- **Status:** DECISION (avoidance mechanism open)
- **Packet:** **Contradicts:** the packet has one payment per enemy covering a whole move.
- **History:**
  - 1 per enemy for the turn [p.278].
  - Per-decision payment [p.1355].
  - Once per enemy per turn or instance [p.1361, p.1472].
  - Changed to per square per enemy (your ruling, 2026-11-01).
- **Evidence:** Rulings A3, B5, B6, clarifications 1 and 10 (your ruling, 2026-11-01).
- **Clarified (your ruling, 2026-11-01):**
  - Avoidance is **always a flat 1 stamina** per enemy, per square left, on or off your turn. It doesn't escalate.
  - Example: leaving a square threatened by A and B costs 2. The next square, threatened only by C, costs 1. A further square also threatened by C costs 1 more, even though you already paid for C.
  - **For now, you can't pay to avoid the OAs that a point-blank ranged attack provokes** (not set in stone).
- **Later changes:**
  - *Packet 0.11.1 (your rulings, 2026-11-17):* an enemy that holds you charges 1 + its tokens on you for the first square you leave in its reach, and the hold then ends (see H-4 and the note Holds). An enemy that couldn't make even one step of an opportunity attack is owed nothing.
    - *The intent above, as it stands:* "without making battlefields sticky" now also covers holds. They're opt-in, the holder pays for them with its next turn, and they were rare in the hand-played fights. "It's probably healthy for holds to not be happening constantly."
    - *Now in:* the rules notes Opportunity Attacks (Avoiding Opportunity Attacks) and Holds.
  - *Packet 0.11.4 (your ruling, 2026-11-20):* the opportunity attacks a shot in melee provokes happen when the shooter declares the target, before it pays, from every enemy threatening it then (not after the shot resolves). The shooter may then cancel, paying nothing. It blocks with what it holds; drawing a weapon to block gives up the shot.
    - *The trigger above, as it stands:* "once the ranged attack finishes resolving" is replaced by "when the target is declared". You accepted that point-blank shots get harsher, since the enemy next to the shooter always swings first.
    - *Now in:* the rules notes Ranged Attacks (Procedure), Opportunity Attacks (Triggers) and Drawing Weapons.

### MV-4 Off-turn escalation
- **Firmness:** Intent locked, mechanism open.
- **Intent:** STATED: off-turn movement and opportunity attacks compete for the same stamina [your ruling, 2026-11-01]. Off-turn costs are separate from on-turn costs so that aggression isn't punished [p.1712]. Blocking stays its own thing [p.1783].
- **Rule:**
  - Off-turn movement purchases and your opportunity-attack steps share one escalation. Each costs +1 per earlier off-turn cost since the start of your turn.
  - It resets at the start of your turn and is separate from the on-turn surcharge (CB-2).
  - Blocks are not part of it.
  - **Your example:** move 1 square, move 1 square, make a 1-stamina OA, move 1 square = 1 + 2 + 3 + 4 = **10**.
- **Status:** DECISION (mechanism open)
- **Packet:** **Contradicts:** the packet gives off-turn movement a separate progression and has no shared track.
- **Evidence:** [p.1783]. Rulings A6, B4 (your ruling, 2026-11-01).
- **Later changes:**
  - *Packet 0.11.0 (your rulings, 2026-11-16):* **removed.** There is one escalation (CB-2). It resets when your turn ends, not at the start of your turn.
    - Dashes are on it. Opportunity attacks are outside it (MV-5).
    - Your example above (move, move, a 1-stamina opportunity attack, move), started right after your turn ends, now costs 1 + 2 + 1 + 3 = **7**, not 10.
    - *The intent above, as it stands:*
      - "Off-turn costs are separate from on-turn costs so that aggression isn't punished": the separation is gone, and the aim is kept by the reset. Your turn's actions are forgotten when it ends, so they don't make a dash after it pricier. A link now runs the other way, on purpose: what you buy between turns makes your next turn pricier.
      - "Off-turn movement and opportunity attacks compete for the same stamina": they still draw on the same stamina, but neither raises the other's price any more.
      - "Blocking stays its own thing": unchanged.
    - *Now in:* the rules note Actions and Escalation. The note Off-Turn Escalation is removed.

### MV-5 Making opportunity attacks: cost and cap
- **Firmness:** Intent locked, mechanism open.
- **Intent:** STATED: OAs should be limited in power but not free, and Finesse is the OA stat. Even without Finesse, an enemy who exposes themselves enough should sometimes be punishable for more than 1 stamina (your ruling, 2026-11-01).
- **Rule:**
  - **Cost:** an OA uses normal attack costs: each attack step costs the weapon's base cost plus your **off-turn** escalation (MV-4), not your on-turn surcharge. So it's efficient damage even after attacking on your own turn, but it makes later OAs and off-turn movement pricier until your next turn.
  - **Cap:** you can spend at most **1 stamina** on a single OA, counting both the weapon's base cost and the escalation.
    - By default you can only OA with a base-1 weapon, and only if you haven't already made an OA or moved off-turn since your last turn began.
    - **+1 to the cap per odd Finesse value** (max +3 at FIN 5–6). Some abilities raise it too.
    - A higher cap lets you take extra attack steps, use bigger weapons, make several OAs, or combine OAs with off-turn movement.
  - **Optional add-on (mechanism open):** each square the enemy moves within your reach raises that OA's cap by 1 + your odd-Finesse bonus (+1 each at FIN 1, 3 and 5). A target that exposes itself for several squares can be punished harder.
- **Status:** DECISION (mechanism open)
- **Packet:** **Contradicts:** replaces "+1 stamina available for opportunity attacks each round".
- **Evidence:** Ruling A8, clarifications 1 and 2 (your ruling, 2026-11-01).
- **Clarified:** the Finesse part counts odd values (1, 3, 5), not FIN ÷ 2 rounded down (your ruling, 2026-11-01).
- **Later changes:**
  - *Packet 0.9.1:* the cap and the optional add-on were removed, along with Finesse's bonus to the cap. The off-turn escalation became the only limit on an opportunity attack.
  - *Packet 0.11.0 (your rulings, 2026-11-16):* a **placeholder**, because the off-turn escalation that priced and limited opportunity attacks is gone (MV-4).
    - An opportunity attack is exactly one attack step. You can't add steps to it.
    - It costs the weapon's base cost, whatever your escalation is. It isn't an action, so it doesn't add to your escalation.
    - Each trigger allows one. Stamina is the only other limit.
    - It stands in until opportunity attacks are redesigned. The hold rules planned for a later version are named as one way to complete them.
    - *The intent above, as it stands:* "limited in power but not free" is met by the single step and its base cost. More exposure means more triggers, at one step each. Finesse has not been the stat for them since packet 0.9.1.
    - *Now in:* the rules note Opportunity Attacks, under Making Opportunity Attacks (Exploratory).
  - *Packet 0.11.1 (your rulings, 2026-11-17):* the placeholder is replaced.
    - Steps cost the weapon's base +1 per earlier step of the same opportunity attack. Each opportunity attack starts fresh, and it still isn't an action.
    - One can cost at most 1, +1 per odd Finesse value (this entry's cap, back from before 0.9.1), plus the attacker's hold tokens on the target, which are spent first.
    - So a heavy weapon needs Finesse 3 or a hold to make one: big weapons have to commit (your ruling; paraphrased, so check the wording).
    - *The intent above, as it stands:* "limited in power but not free" is met by the cap and the step prices. "Finesse is the OA stat" holds again. "An enemy who exposes themselves enough should sometimes be punishable for more than 1 stamina" now comes through a hold: the attacker commits tokens in advance, rather than gaining cap per square the enemy moves.
    - *Now in:* the rules notes Opportunity Attacks (Making Opportunity Attacks, Mechanism open) and Holds.

---

## RG: Ranged combat

### RG-1 Ranged attack procedure
- **Firmness:** Intent locked, numbers placeholder.
- **Intent:** STATED: ranged combat mirrors melee where possible. Archers are dangerous but answerable [p.186, p.188] and vulnerable in melee after shooting [p.1484].
- **Rule:**
  1. Declare the target.
  2. Pay the weapon's flat base cost (shortbow 3, longbow 5; EQ-2).
  3. Buy aim steps (RG-2).
  4. Roll and total the damage.
  5. The target may then dive for cover with off-turn movement (RG-4).
  6. The target blocks with Ranged Defense (or Melee Defense + cover if the shooter is in its reach).
  7. Armor, then crits.

  Shooting within anyone's melee range provokes OAs (MV-3).
- **Status:** DECISION. The dive comes **after** the roll. The shot's base damage includes FIN, and STR for longbows but not shortbows (EQ-2) (your ruling, 2026-11-01).
- **Packet:** The order matches. The base cost is now flat (CB-2).
- **Evidence:** [p.1217]. Rulings B11, A4 (your ruling, 2026-11-01).

### RG-2 Aim steps
- **Firmness:** Exploratory (cost: probably locked, but not confidently). Intent locked, numbers placeholder (what each step adds).
- **Intent:** STATED: aim is non-deterministic [p.1142, p.1226]. It adds pressure. Aiming should be able to raise crit chance, because crits are placement [p.1235]. **Ranged lethality from aiming is an unsolved problem** (see H-1).
- **Rule:**
  - Each aim step adds **1d6 + FIN** to the damage total.
  - Aim steps are **actions** on the turn's surcharge (CB-2): each costs 1 + actions so far, continuing across shots rather than restarting.
- **Status:** DECISION (implementation not confidently locked)
- **Packet:** **Contradicts:** the packet says aim steps aren't Actions and adds only to blockable damage. With Max HP Damage shelved, aim damage can now wound.
- **History:** Own triangle restarting each shot [p.1218] → actions (your ruling, 2026-11-01).
- **Evidence:** [p.1472]. Rulings A9, A4, clarification 4 (your ruling, 2026-11-01).

### RG-3 Range bands
- **Firmness:** Intent locked, numbers placeholder.
- **Intent:** STATED: range should change how much you aim and whether you risk closing in [p.1243].
- **Rule:**
  - Each weapon sets short / medium / long ranges, possibly modified by Finesse on the weapon card.
  - **Short:** no penalty.
  - **Medium:** your first aim step adds only FIN, not the 1d6. If you don't aim at least once, the shot automatically misses.
  - **Long:** the same for your first two aim steps, and you need at least two aim steps.
  - **Beyond long:** automatic miss.
- **Status:** DECISION
- **Packet:** Partly matches. It lacks the penalty mechanic and the Finesse modifier.
- **Evidence:** [p.1276], [p.1472]; clarification 7 (your ruling, 2026-11-01).

### RG-4 Cover
- **Firmness:** Intent locked, numbers placeholder.
- **Intent:** STATED: cover is the main ranged defense. A reactive dive helps but can't fully negate a committed shot [p.1217].
- **Rule:**
  - Half cover +2; three-quarters +5; "defined similar to 5e".
  - Diving into full cover after being targeted counts as only 3/4 cover for that attack.
  - **Wording:** cover is a bonus to whatever defense you use against a ranged attack, not a bonus to Ranged Defense specifically. So it also applies when you use Melee Defense against a point-blank shot (DF-2) (your ruling, 2026-11-01).
- **Status:** DECISION
- **Packet:** Matches. It omits the point-blank case.
- **Evidence:** [p.1217–1218]. Ruling A18 (your ruling, 2026-11-01).

### RG-5 Area attacks (fireball, dragon breath)
- **Firmness:** Exploratory. "What if…" [p.1320].
- **Intent:** STATED: reactive movement against area attacks should help without nullifying them [p.1320].
- **Rule:** Cover is measured from the blast origin. You can dive out of an AoE, but it gives only a 3/4-cover equivalent.
- **Status:**
  - PROPOSAL (your "What if…" [p.1320]).
  - Cover from the origin: UNCERTAIN.
  - Whether a fireball uses Dodge: ChatGPT only.
- **Packet:** Missing.

---

## EQ: Equipment

### EQ-1 Armor
- **Firmness:**
  - Locked (armor values 1/2/3; order after blocks).
  - Intent locked, numbers placeholder (the Agility steps).
  - Exploratory (the STR-threshold penalties).
- **Intent:** STATED: armor reduces damage, so it shines against many attackers, while nimble high-defense builds shine one-on-one [p.811]. Heavy armor shouldn't lean on Agility, so Agility isn't mandatory [p.330]. Penalties should be realistic [p.847].
- **Rule:**
  - **Values:** Light 1, Medium 2, Heavy 3. Armor applies after blocks, so it reduces grazing leaks and unblocked damage. Crit dice ignore 1 armor each.
  - **Agility scaling:** in medium armor, Agility's defense bonus counts every 3rd point; in heavy armor, every 4th. This holds regardless of Strength.
  - **Strength thresholds (placeholder):**
    - Heavy armor: −1 Finesse and −1 Agility for each point of Strength below 3.
    - Medium armor: the same for each point of Strength below 1.
    - If this pushes Agility below 0, you lose your base defenses (AT-2).
  - **Casters:** you can't cast spells in any armor (MG-2).
- **Status:** DECISION
- **Packet:** Partly matches. **Missing:** the every-3rd/4th numbers, the STR thresholds and the below-0 rule.
- **History:**
  - Every-3rd/4th Agility [p.1471].
  - Flat −1 AGI / −1 FIN / −1 CUN proposed [p.1638]; ABANDONED.
  - STR thresholds added (your ruling, 2026-11-01).
- **Evidence:** Rulings A15, B8, clarification 5 (your ruling, 2026-11-01).
- **Later changes:**
  - *Packet 0.12.1 (design chats 2026-11-26 to 2026-11-27):* replaced the every-3rd/4th Agility steps with **Strength-gated even Agility** (light: full even Agility; medium: even Agility capped at even Strength; heavy: even Agility capped at even Strength − 1, min 0), replaced the `−1` Agility / `−1` Finesse Strength-shortfall penalties with **`+1` stamina on every action per point of Strength below the requirement** (medium STR 1, heavy STR 3; removing negative attributes from the packet), and gave heavy armor **`+1` stamina per dash** (base 2 instead of 1).
    - *Now in:* the rules notes Armor, Defenses, Ranged Defense, Agility, Finesse, Strength, Dash, Actions and Escalation, and Quick Reference.

### EQ-2 Weapons
- **Firmness:** Intent locked, numbers placeholder. The list is **partially incomplete**.
- **Intent:** STATED: weapons differ by efficiency curve. Light weapons are efficient at low commitment, heavy ones at high [p.504]. STR weapons should be a bit more stamina-efficient [p.1200].
- **Card fields:** category, base stamina cost, hands, damage, special properties. (The Max HP Damage line is shelved.)
- **Known stats:**

| Weapon | Base cost | Damage per step / shot | Notes |
|---|---|---|---|
| Dagger | 1 | 1d4 + (AGI or FIN) | Quick-draw (EQ-3) |
| Shortsword | 1 | 1d6 + (AGI or FIN) | Quick-draw (EQ-3); from p.731 |
| Longsword | 2 | 1d10 + (STR or AGI) + FIN | Two hands; one-handed: d8 and STR instead of AGI |
| Spear | 2 | 1d8 + STR + FIN | Reach (1 extra square) |
| Greatsword | 3 | 1d12 + 2×STR + FIN | |
| Greataxe | 3 | 2d6 + 3×STR | |
| Shortbow | 3 per shot | 1d6 + FIN | Ranges 6 / 12 / 18 squares; aim steps as actions (CB-2) |
| Longbow | 5 per shot | 1d8 + FIN + STR | Ranges 8 / 16 / 24 squares; aim steps as actions (CB-2) |
| Others from p.731 | — | Polearm 1d10 + 3×STR (reach 2); axe 1d10 + 2×STR (cleave); rapier 1d8 + AGI + FIN | Your p.731 draft; unconfirmed placeholders |

- **Placeholder properties:**
  - **Hammer-type weapons** ignore 1 armor automatically.
  - **Daggers and shortswords:** see EQ-3.
- **Reach:** 5-ft grid; most small and medium weapons reach 1 square.
- **Status:** DECISION (placeholder numbers)
- **Packet:** The longsword matches. Everything else is missing.
- **Evidence:** [p.731], [p.1474], [p.1484] and your weapon rulings (your ruling, 2026-11-01). The greatsword was 2d6 briefly, then went back to 1d12.
- **Later changes:**
  - *Packet 0.11.1 (your ruling, 2026-11-17):* the spear is one- or two-handed, and has its reach (1 extra square) only in two hands, "so you can't pull this trick with a spear + shield": combining reach with a shield's defense, for example to hold a sword fighter 2 squares away.
    - *Now in:* the rules note Weapons.

### EQ-3 Drawing weapons and occupied hands
- **Firmness:** Exploratory.
- **Intent:** STATED: archers stay vulnerable in melee after shooting [p.1484], but a rushed archer can pull an emergency blade [p.1480].
- **Rule (current placeholder):**
  - On your turn, you may draw or sheathe freely until you use a weapon. Dropping is always free.
  - **A hand used on your turn** for a bow shot or somatic spellcasting can't draw a normal weapon until the start of your next turn.
  - Drawing a normal weapon **between turns** costs 1 stamina.
  - **Daggers and shortswords** are free to draw between turns, even into a hand you used this turn.
- **Status:** DECISION (exploratory)
- **Packet:** **Contradicts:** the packet has a global "hands occupied" rule and lacks the dagger/shortsword exception.
- **Evidence:** [p.1480], [p.1484]. Ruling B7 and your weapon ruling (your ruling, 2026-11-01).
- **Later changes:**
  - *Packet 0.12.1 (your call, 2026-11-26 to 2026-11-27):* simplified around whether you have attacked, shot or cast since your last turn started (blocking and opportunity attacks don't count); before acting on your turn, drawing, sheathing and grip changes are free; post-action drawing on your turn and off-turn drawing (in a dash phase or in step 4, Reactions, of an attack) are always **actions** costing weapon base + escalation (normal weapons require not having attacked, shot or cast since turn start; Quick-draw daggers and shortswords cost 1 + escalation even after acting). Removing a shield frees that hand immediately; equipping a shield is disallowed after attacking, shooting or casting on your turn.

### EQ-4 Dagger/shortsword quick-draw → merged into EQ-3
- **Status:** Superseded. The earlier rule (draw when attacked for 1 stamina [p.1480]) is replaced by EQ-3's "free to draw between turns".

### EQ-5 Shields
- **Firmness:** Locked. Stated without hedge [p.1481].
- **Intent:** INFERRED: a simple, one-shield bonus to both melee and ranged defense.
- **Rule:** +2 Melee and +2 Ranged Defense. You benefit from one shield only.
- **Status:** DECISION
- **Packet:** Matches.
- **History:** Main-hand shield rule scrapped [p.1481].
- **Later changes:**
  - *Packet 0.10.0 (your ruling, 2026-11-11):* lowered from +2/+2 to +1 Melee Defense and +1 Ranged Defense.
  - *Packet 0.12.1 (your call, 2026-11-26 to 2026-11-27):* added tiered Strength requirements (+1 Ranged Defense requires Strength 1; +1 Melee Defense requires Strength 2; no attribute penalties), made equipping a shield a base-5 action and removing one a base-1 action (both on your turn only; can't be dropped freely; removing frees the hand immediately), and removed the blanket ban on casting spells while using a shield.

---

## MG: Magic

*Only the access goal and casting requirements are current rules. Everything else about magic is shelved in H-5.*

### MG-1 Magic access
- **Firmness:** Locked (as a goal).
- **Intent:** STATED: magic is optional for anyone, never required. Mental stats shouldn't be dump stats for non-casters [p.124].
- **Status:** DECISION. Everything else about magic is summarized in Part H (H-5) and is not current rules.

### MG-2 Casting requirements
- **Firmness:** Intent locked, numbers placeholder.
- **Intent:** STATED: magic runs on the same stamina/strain economy. Casters shouldn't match martials' sustained armor-based defense [p.354].
- **Rule:**
  - Casting requires a free hand.
  - **No spellcasting in light, medium or heavy armor, or while using a shield,** unless an ability says otherwise.
  - Each spell states its own stamina and strain costs and how it works.
- **Status:** DECISION
- **Packet:** **Contradicts / incomplete:** the packet has armor as TODO and nothing about shields.
- **Evidence:** [p.1472–1473] and your spellcasting ruling (your ruling, 2026-11-01).
- **Later changes:**
  - *Packet 0.12.0:* spells no longer list a strain cost or strain overage (strain shelved as **H-10**); limits across fights or outside combat are **TODO**.
  - *Packet 0.12.1 (your call, 2026-11-26 to 2026-11-27):* removed the blanket ban on casting spells while using a shield (shields occupy one hand and require STR 1 for +1 RD, STR 2 for +1 MD). Added exploratory directions for 1H vs. 2H spells, multi-action spellcasting, and exploring an armor-casting stamina surcharge.

---

## CP: Character creation and progression

### CP-1 Levels and advancement
- **Firmness:** Intent locked, numbers placeholder.
- **Intent:** STATED: levels give fine-grained growth, roughly 5e levels 1–20 [p.330]. High-level characters should dominate low-level ones [p.1388].
- **Rule:**
  - Characters **start at level 1** with 25 Skill Points, 5 Expertise (which already includes the starting levels' Expertise Point) and 1 Ability Point, normally spent on a first core ability (your ruling, 2026-11-01).
  - *Note:* in your ruling the Ability Point came at level 1 and the Expertise Point at level 0. The table below (from your p.1277 notes) has them the other way round. The totals are the same either way.
  - Per level, by the last digit:
    - 0: Ability Point
    - 1: Expertise
    - 2: Ability
    - 3: +1 max stamina, +1 max strain, +1 Skill
    - 4: Expertise
    - 5: +1 stamina regen, +1 strain regen, +1 Skill
    - 6: Expertise
    - 7: Ability
    - 8: +1 max stamina, +1 max strain, +1 Skill
    - 9: Expertise
  - "Tier" may still be used as a label for a band of levels. But tiers in a tree are reached only by buying that tree's tier abilities (CP-2), not by levelling.
- **Status:** DECISION
- **Packet:** **Contradicts:** the packet's "Tier advancement" at level 0 is gone, and starting level 1 is new.
- **Evidence:** [p.1277]. Rulings A7, A14, B12, clarification 8; starting level (your ruling, 2026-11-01).
- **Later changes:**
  - *Packet 0.12.0:* "+1 max strain" (digits 3 and 8) and "+1 strain regen" (digit 5) removed when strain was shelved (**H-10**).

### CP-2 Class trees: core abilities and tier abilities
- **Firmness:** Intent locked, mechanism open. This is the current implementation to test.
- **Intent:**
  - STATED: going deeper costs breadth, not raw power [p.1665].
  - Every purchase should feel like something happened, and tier abilities carry the tree's identity [p.1687].
  - Opening a new tree is worth more than deepening one, so it costs more [p.1673].
- **Rule:**
  - **Opening a tree:** buy its **core ability**, which is the tree's Tier 1 prerequisite.
    - It grants the tree's signature ability (Fighter instant stamina regen, Rogue turn-order manipulation, Wizard spellcasting, etc.) and some proficiencies.
    - Each core ability you already own makes other core abilities cost **+1 AP**.
    - Treeless abilities exist, so owning no tree is possible.
  - **Going deeper:** a **Tier N ability** (N > 1, 1 AP) is the prerequisite for that tree's Tier N abilities.
    - It requires the tree's Tier N−1 ability. Normal Tier N features need only the Tier N ability, though other prerequisites may appear in places (your ruling, 2026-11-01).
    - It's mostly an opportunity cost, with a minor benefit that fits the tree.
    - It's also a place for fitting mechanics players might not choose if they were sold separately.
  - There are no separately "unlocked" tiers; the prerequisite abilities *are* the unlocks.
- **Status:** DECISION (mechanism open)
- **Packet:** **Contradicts:** the packet has 10-level tiers and free tree selection.
- **Evidence:** [p.1665], [p.1673], [p.1687]. Rulings A14, B9, B12 (your ruling, 2026-11-01).
- **Later changes:**
  - *Packet 0.12.1 (your call, 2026-11-25):* weapon proficiencies shelved (**H-11**); core abilities no longer grant weapon proficiencies.

### CP-3 Additional trees (multiclassing) → merged into CP-2
- **Status:** Superseded by CP-2. Each owned core ability makes other core abilities cost +1 AP.

### CP-4 Starting currencies
- **Firmness:** Intent locked, numbers placeholder. "about 25… about 5" [p.1277]; "Assume" [p.1473].
- **Intent:** INFERRED: a modest starting budget that doesn't let new characters max a stat.
- **Rule:** 25 Skill Points, 5 Expertise Points (including the starting levels' Expertise) and 1 Ability Point (your ruling, 2026-11-01).
- **Status:** DECISION
- **Packet:** Matches.
- **Evidence:** [p.1473]

### CP-5 Expertise costs
- **Firmness:** Intent locked, numbers placeholder. "Assume… standard triangle" [p.1474].
- **Intent:** STATED: escalating costs keep rushing one attribute from being automatically correct [p.322, p.1041].
- **Rule:** Attributes rise with Expertise on the standard triangle: the Nth point costs N, so +3 costs 6 and +6 costs 21. Maximum +6.
- **Status:** DECISION
- **Packet:** **Missing.**
- **Evidence:** "Assume attributes are up to +6 from expertise using standard triangle" [p.1474]. "+3 to cunning… This costs 1+2+3=6 *expertise* points." [p.1402]

### CP-6 What each currency buys; class trees
- **Firmness:** Locked (structure). Stated in detail [p.1473].
- **Intent:** STATED: separate currencies for separate arenas of play [p.565, p.1493]. Duplicate purchases are refunded so nothing is wasted [p.1473].
- **Rule:**
  - **Ability Points:** most tree features.
  - **Expertise:** attributes, and weapon proficiencies outside your class.
  - **Skill Points:** ribbon abilities; versatility under an owned ability (more spells in a school, more maneuvers); languages; skill bonuses.
- **Trees:**
  - Features sit in tiers. A tier's features require that tree's Tier N ability (CP-2); there are no separate tier unlocks. Features may have other prerequisites.
  - The **core ability** is the first purchase and the prerequisite for the rest. It includes the tree's signature ability and may grant proficiencies (CP-2).
  - Treeless features exist.
  - If a later feature duplicates an earlier purchase, the earlier one is refunded.
- **Status:** DECISION
- **Packet:** Mostly matches. **Missing:** which currency buys what, and the tier gating.
- **Evidence:** "Many of these will be purchased with ability points, but some might be purchased with expertise points (like weapon proficiencies that aren't part of your class) or skill points (ribbon abilities, and abilities that buy versatility under an already purchased ability…)" [p.1473]. "spend one or more ability points to buy a 'battlemaster maneuver die' ability + a small number of maneuver choices, and then you could spend skill points to buy extra maneuver choices" [p.1054]
- **Later changes:**
  - *Packet 0.12.1 (your call, 2026-11-25):* weapon proficiencies shelved (**H-11**); Expertise now buys attributes only.

### CP-7 Class core abilities
- **Firmness:**
  - Intent locked, numbers placeholder (Fighter, Rogue, Barbarian).
  - Exploratory (Monk).
- **Intent:** STATED: each core is simple, powerful and defining, and interacts with stamina or turn order [p.942]. Cores are strong enough to be near-mandatory [p.1673].
- **Fighter:** "Gain 3 strain to recover your normal stamina recovery amount now (can be done at any time)."
- **Rogue:** "Gain 3 strain to take your turn now skipping it later in the round, or to skip your turn and take it after a later turn (can be done between anyone's turns as long as you haven't taken your turn for this round yet)."
- **Barbarian:** "Gain 1 strain to recover the biggest stamina expenditure spent on an attack step (can be done at any time on your turn)."
- **Monk:** **1 strain: your perfect-block costs don't escalate for the current attack.** This replaces the earlier "until your next turn, unarmored" version and its 2 + armor-level cost.
- **Wizard (and other casters):** the core grants spellcasting (H-5).
- **Status:** DECISION (Monk exploratory)
- **Packet:** Missing.
- **Evidence:** [p.942], [p.957–960] and your Monk ruling (your ruling, 2026-11-01).
- **Later changes:**
  - *Packet 0.11.0 (your rulings, 2026-11-16):* the Rogue's core is declared **just after a dash phase ends** (it was "between anyone's turns"), and the turn that follows starts with no new dash phase. So nobody can dash in answer to the announcement. Marked as open to change if that makes the ability degenerate.
  - *Packet 0.12.0 (your calls, 2026-11-22 to 2026-11-24):* with strain shelved (**H-10**), all four martial cores are replaced by exploratory, strain-free placeholders: Fighter (**Second Wind**: off-turn normal recovery, skips next recovery, 0 stamina, counts as an action), Rogue (**Opportunist**: once between turns including the opening dash phase, act in a dash phase up to `1 + Cunning` stamina), Barbarian (**Press the Wound**: once on your turn, on melee HP damage, recover weapon base cost), and Monk (**Poised Guard**: unarmored/no shield, spend up to 2 held stamina on an attacking held enemy, including opportunity attacks, for non-escalating perfect blocks).

### CP-8 Martial vs caster tree structure
- **Firmness:** Locked (as principle).
- **Intent:** STATED: martials get one static defining strain ability plus passives; casters invest in school ranks [p.1121].
- **Rule:**
  - Martials have one defining strain ability that stays roughly static but scales, plus mostly flat passives and no-strain actives.
  - Casters put many Ability Points into school ranks.
  - Ability-point purchases should be real power, not just versatility.
- **Status:** DECISION
- **Packet:** Missing.
- **Evidence:** "Martials would get a higher portion of flat buff passives and no strain active abilities. Casters would get abilities that aren't just 'increase a spell specialization rank' but that would be where casters are expected to invest a lot of their ability points" [p.1121]
- **Later changes:**
  - *Packet 0.12.0:* reworded after shelving strain (**H-10**): martial trees have one defining core ability (sometimes upgraded by later features) plus passives and actives paid inside the fight (ready stamina, held stamina, escalation or timing).

### CP-9 Candidate abilities you kept
- **Firmness:** Exploratory. A candidate list.
- **Intent:** INFERRED: grounded abilities that hook into blocks, OAs and movement.
- **List:**
  - Press the Advantage
  - Heavy Swing (+1 stamina per step to penetrate 2 armor)
  - Feint (Cunning contest: the defender declares blocks first)
  - Riposte (OA after a perfect block)
  - Momentum
  - Fluid Footwork
  - Step Through
  - Tactical Withdrawal (2 stamina to move before an attack resolves)
- **Status:** DECISION as a kept candidate list. They aren't assigned to trees. Other ability lists are ChatGPT's.
- **Packet:** Missing.
- **Evidence:** "Some of the abilities I liked from before, with minor alterations" [p.856]
- **Later changes:**
  - *Packet 0.11.2 (your ruling, 2026-11-17):* these moved unchanged to the rules note Earlier Candidate Abilities. The candidate list is now one ability, Great Weapon Training: with the Fighter core ability, heavy melee weapons (base cost 3: greatswords, greataxes, halberds) get +1 square of reach. *Why (your words, 2026-11-18):* none of the earlier candidates "actually reflected what I expect abilities to look like"; Great Weapon Training "feels like the right sort of enhancement of a particular set of weapons. Potentially powerful and meaningfully changes the style of using them, but not just by making the damage numbers better." Later the same day: "I don't plan on adding generic active abilities like 'Riposte' or 'Parry' as ability point costed abilities. The assumption is that those are already represented implicitly via an interpretation of the normal combat mechanics."
    - *Now in:* the rules notes Candidate Abilities and Earlier Candidate Abilities.

---

## SK: Skills

### SK-1 Skill checks
- **Firmness:** Exploratory. Skill system details are TBD (your ruling, 2026-11-01).
- **Intent:** STATED: skill should outweigh luck for skilled characters [p.871]. The GM decides when to roll and what it means [p.1452]. A deliberately thin layer [p.1402].
- **Rule (current placeholder):**
  - Roll 2d12 + attribute + skill.
  - One stat per skill; the GM may make an explicit exception.
  - The GM decides whether to roll at all; DCs are only suggested.
- **Status:** DECISION (placeholder; details TBD)
- **Packet:** Matches.
- **Evidence:** [p.75], [p.1402], [p.1452]; clarification 10 (your ruling, 2026-11-01).

### SK-2 Skill-point attribute bonus
- **Firmness:** Exploratory (skill details TBD).
- **Intent:** STATED: being average should be cheap, so dumping gains little [p.1434]. Skill-point bonuses never feed combat [p.1409].
- **Rule (current placeholder):** up to +4 per attribute, for skill checks only, with marginal costs 1, 2, 4, 7.
- **Status:** DECISION (placeholder)
- **Packet:** The +4 cap matches; it's missing the costs.
- **Evidence:** [p.1474]

### SK-3 Specific skill proficiency
- **Firmness:** Exploratory (skill details TBD).
- **Intent:** STATED: rising costs work as a soft cap on specialization; no hard caps [p.1439].
- **Rule (current placeholder):** +1 per skill rank, at triangular Skill Point cost, with no hard cap. The skill list is TBD.
- **Status:** DECISION (placeholder)
- **Packet:** Missing.
- **Evidence:** [p.1439], [p.1474]

### SK-4 Skill list and sub-groups
- **Firmness:** Exploratory (TBD).
- **Intent:** STATED: each skill keys off exactly one stat, with clear boundaries [p.39, p.75].
- **Ideas so far:**
  - Inspire (Will) vs Persuade (Cunning) [p.75].
  - Attribute sub-groups, e.g. INT: horsepower / knowledge; CUN: people / world [p.560, p.876].
- **Status:** TBD
- **Packet:** Missing.

---

## IN: Injury, 0 HP, death, rest

### IN-1 0 HP, dying and death
- **Firmness:** Intent locked, numbers placeholder.
- **Intent:** STATED: 0 HP is "deadly, dangerous, and impactful" and clearly worse than being knocked out [p.339, p.342]. There is still no "out of the fight but alive" state above 0 HP; see H-2.
- **Rule:**
  - **At 0 HP or below:** you're incapacitated. At exactly 0 HP you're not in System Shock.
  - **Dropping below 0 HP:** you enter **System Shock**, starting at a Shock value equal to your negative HP (−2 HP → 2 Shock).
  - **Damage while in System Shock:** lowers your HP as normal and raises Shock by the same amount.
  - **Dying roll:** at the **start of each of your turns** while in System Shock, roll 2d12 + STR.
    - **Below 10 + Shock:** +1 Shock (bleeding out). This doesn't change HP.
    - **At least 15 + Shock:** −1 Shock (naturally stabilizing).
    - In between: no change.
  - **Death:** you die at **10 Shock** or at **−10 HP**.
  - **Stabilized:** reaching 0 Shock, naturally or with help (a **Medicine** roll, specifics TBD), ends System Shock. You stay at your negative HP and remain incapacitated, but stop rolling.
  - **Damage while stabilized (below 0 HP, not in System Shock):** you re-enter System Shock with Shock equal to the damage taken.
- **Worked example (yours):**
  1. At 3 HP you take 5 damage: −2 HP, 2 Shock.
  2. Next turn you roll low: 3 Shock, still −2 HP.
  3. You take 3 damage: −5 HP, 6 Shock.
  4. Over the next few turns you're fully stabilized: −5 HP, incapacitated, no longer rolling.
  5. You take 1 damage: −6 HP and 1 Shock, rolling again each turn until you die or stabilize.
- **Status:** DECISION (placeholder)
- **Packet:** Missing.
- **History:** ChatGPT's p.608–612 track (death at 3 Shock, +1 per round) → your thresholds, 10-Shock death and Shock tied to negative HP (your ruling, 2026-11-01).
- **Later changes:**
  - *Packet 0.11.2 (your ruling, 2026-11-17):* the Medicine roll gets a placeholder. As an action with a base cost of 5, a creature within 1 square (5 ft) of someone in System Shock rolls 2d12 + Intelligence; at 10 + the target's Shock or more, its Shock drops by 1. It's there so a first playtest can run.
    - *Now in:* the rules note Dying and Death (Helping the Dying); restated in Actions and Escalation and Intelligence.

### IN-2 Lingering injuries → SHELVED
- **Status:** SHELVED (Part H, H-3) (your ruling, 2026-11-01).

### IN-3 Rest
- **Firmness:** Intent locked, mechanism open.
- **Intent:** STATED: rest should be clear without GM adjudication, not tied to a calendar day, and not harsh on interruption [p.553].
- **Rule:**
  - Per night of rest: recover 1 HP and 4 + round(level/10) strain.
  - The strain alternative is in CR-4.
- **Status:** DECISION (placeholder)

### IN-4 Healing
- **Firmness:** Locked (for now: no HP-restoring magic).
- **Intent:** STATED: HP is slow-healing real injury, and lasting harm is fair because damage is avoidable [p.90, p.339].
- **Rule:**
  - HP recovers only through nightly rest (1 HP per night).
  - **No HP-restoring spells like 5e's *Healing Word* or *Cure Wounds* are planned.** Don't assume a healer role that refills HP.
- **Status:** DECISION
- **Packet:** Consistent. The packet never mentions healing spells, but the "no HP-restoring magic" point should be stated explicitly in v0.9.
- **Evidence:** your ruling (your ruling, 2026-11-01).

---

## CT: Control effects, conditions, grappling

### CT-1 Conditions and agency-removing effects
- **Firmness:**
  - Locked (principle).
  - Exploratory (conditions list).
- **Intent:** STATED: anything that removes agency is progressive and resistible with stamina, not a binary save. Paralysis etc. must not happen at once [p.1277, p.1858].
- **Rule:**
  - **Control effects (grapple, Hold Person, charm): TBD.** They aren't in the current rules; the extended-contest ideas are in H-4.
  - **Conditions:** no list yet. Undecided whether there will be universal conditions like "paralyzed", or whether each spell or ability explains its own effects.
- **Status:** DECISION (principle); TBD (mechanics)
- **Evidence:** [p.1858]. Rulings A16, A17 and your control ruling (your ruling, 2026-11-01).

### CT-2 Control resolution procedure → SHELVED
- **Status:** SHELVED (Part H, H-4).

### CT-3 Control details → SHELVED
- **Status:** SHELVED (Part H, H-4).

### CT-4 In-combat skill contests (older)
- **Firmness:** n/a (abandoned).
- **Rule:** 2d6 + skill per triangle step, with extended contests tracking a difference [p.871].
- **Status:** ABANDONED (superseded by CT-2).

---

## GM: NPCs and running the game

### GM-1 NPCs use PC mechanics and value survival
- **Firmness:** Locked (principle).
- **Intent:** STATED: same rules for PCs and NPCs [p.241]. NPCs value survival [p.1286].
- **Rule:**
  - Humanoid NPCs use the same stamina rules as PCs.
  - NPCs must play with self-preservation, or they'll "suicide into a grazing hit".
  - Telegraphing danger matters, but it's GM-dependent and still unsolved.
- **Status:** DECISION (preference / concern)
- **Packet:** Matches ("value their own survival", "telegraph").
- **Evidence:** "It'd feel weird to not have them use the same mechanics" [p.241]. "if a DM doesn't play NPCs with self preservation then each fight will be annoying" [p.1286]

### GM-2 NPC aggression profiles → SHELVED
- **Status:** SHELVED (Part H, H-6).

---

## PL: Play aids and presentation

### PL-1 Reference tables; stamina tokens
- **Firmness:** Locked (tables) / Exploratory (tokens). [p.2044]
- **Intent:** STATED: cut table arithmetic without removing the decision [p.2044].
- **Rule:** Provide reference tables for common calculations. Physical stamina tokens as an option.
- **Status:**
  - Tables: DECISION [p.2044].
  - Tokens: PROPOSAL.
- **Packet:** Partly matches (GM quick-reference sheet).

### PL-2 Presentation instructions you gave
- **Firmness:** Locked.
- **Instructions:**
  - Markdown with linked keywords (Obsidian).
  - Write in your voice, polished.
  - Weapon cards use the shorthand "3 × [1d10 + STR + FIN]".
  - Avoid "bundle".
  - Use TBD and playtest-status markers.
  - Add non-mechanical explanations (what stamina represents, what Cunning covers).
  - Intro must stress that "Stamina isn't a resource you spend to enhance your defense, it *is* your defense…" [p.1826].
- **Status:** DECISION
- **Packet:** Partly done. The intro emphasis is weak.

---

# PART E: Gap check against the packet's "What This Game Is Trying To Do"

The full comparison is in the design notes (§7). Short version: the packet's intro is accurate but thin. It covers tactical decisions over big HP pools, managing stamina and commitment, deadly-but-earned deaths, and light out-of-combat rules. It's missing goals you stated repeatedly:

- stamina *is* your defense;
- the "named characters, not mooks" model of danger, with an explicit departure from realism to give characters agency;
- mechanics should read as plausible events in a fight;
- positioning stays live mid-round, so aggression isn't suicidal;
- never trade character fidelity for optimization (arenas of play);
- a low arithmetic and decision budget;
- balance that holds up across GM pacing and rest frequency;
- agency-removing effects are progressive.

One nuance: the packet says "Most attacks are dangerous". Your framing was that most attack damage is *pressure* the defender spends stamina against, and wounds are capped [p.1200]. That's compatible but worth wording carefully.

---

# PART F: What's left for you

**A. Open questions**
- None outstanding from your latest answers.

**B. Entries to review: my calls, not your words.** Firmness labels or rules I inferred, or that came from ChatGPT text you adopted by name:
- **EQ-2:** the remaining p.731 weapons (polearm, axe, rapier) kept as placeholders. Your p.731 "+1 melee defense" properties were dropped.
- **AT-3:** odd/even structure labeled placeholder (inferred).
- **CB-7:** the resolution step list (assembled from several of your statements).
- **Locked only because you stated them without a hedge:**
  - CB-1 (no to-hit roll)
  - CB-3 (Perfect Block)
  - CB-4 (grazing cost 1)
  - EQ-5 (shields +2/+2)
  - CR-5 (strain overage)
  - MV-2 (off-turn movement)
  - DF-2 structure

  Remember: Locked just means a deliberate current choice.
- **The 4 intents marked INFERRED** (search "INFERRED" in Part D): CB-9, CP-4, CP-9, EQ-5.
- **Part H:** check the shelved summaries still capture what you meant, especially H-4 (control) and H-5 (spellcasting).

**C. Not reviewed yet**
- Part E (gap check against the packet's "What This Game Is Trying To Do").
- The design notes file. Its decision log and tensions don't yet reflect today's rulings or the shelved items.

---

# PART G: Your rulings, verbatim (log)

All rounds are folded into Parts A–D and H. This log is the source of truth if anything above misstates them.

**Round 1 (2026-11-01): answers to Parts A and B**

> A1: All of that looks good, and I'd consider it locked.
> A2: Not including this for now, but it's a strong contender for adding later. It should probably be included in anticipation of wanting to differentiate STR/AGI/FIN and reducing ranged attack lethality.
> A3: Opportunity attack when leaving any threatened square. 1 stamina per person per square. Mechanism open.
> A4: Mechanism open. There should probably be some way to combine multiple actions per turn, but haven't established the precise mechanics. Integrate ranged mechanics by having aim steps count as these "actions" rather than the base stamina cost per shot (eg 2 shots from a 5 stamina longbow w/ 2 aim steps each attack is 5 + 1 + 2 + 5 + 3 + 4 = 20 stamina). Ideally don't call them actions since that'll be misleading, but no worries if you can't think of a better name.
> A5: Locked.
> A6: Locked. Off-turn costs like this reset at the start of your turn. Stacks with opportunity attack cost progression the same way that the A4 "action" stacking increases costs (eg assuming you only move 1 square per off-turn movement step, if you want to move 2 squares off turn, then opportunity attack for 1 stamina, then move 1 more square, that costs 1 + 2 + 3 + 4 = 10 stamina).
> A7: Intent locked, numbers/mechanism placeholder depending on what part of it you're referring to.
> A8: Replace with this intent locked, mechanism open mechanic to limit opportunity attack power: You can spend 1 stamina max per opportunity attack, including both extra weapon stamina costs and escalating costs for multiple opportunity attacks in a round. Each finesse adds +1 to this, allowing larger weapons and/or repeated opportunity attacks.
> A9: Aim escalation is probably locked. Step addition is intent locked, numbers placeholder.
> A10: Intent locked, mechanism open.
> A11: Exploratory.
> A12: Exploratory.
> A13: Exploratory.
> A14: Intent locked, mechanism open. "Tier unlock nodes" that cost an ability point (meaning there's an ability point opportunity cost for each tier level you want to unlock in a tree) are the current implementation to test. These will probably have minor benefits that fit the overall theme of the tree, which will also be used as a place to put fitting mechanics that people might not choose to unlock if given the choice to buy them normally.
> A15: Exploratory. Strength gives +1 HP, but this is suspect since this scales poorly at higher levels with the rest of the rules. There will probably be something like -1 finesse and -1 agility for each strength below 3 for heavy armor, and for each strength below 1 for medium armor (though this is definitely a placeholder).
> A16: Conditions list not established. Unclear whether there will be universal conditions like "paralyzed" or if spells/abilities will just explain what they do.
> A17: Intent locked, mechanism open.
> A18: Intent locked, numbers placeholder.
> B1: Strain-based extra stamina cost is calculated *after* spending the strain on the ability. If you're 1 over your strain limit and trying to use a 3 strain 4 stamina ability, then you go to 4 strain over limit in total and therefore need to spend 4 extra (8 total) stamina to use the ability.
> B2: Locked, though I'm not sure whether to phrase it as "you have 1 base melee and ranged defense (but somewhere say that you lose this if your agility goes below 0)" or "your nonnegative agility grants you +1 to melee and ranged defense". I'm leaning towards the former, since I think of it as just you having a baseline ability to weakly avoid damage.
> B3: You can also do it after your turn. Locked.
> B4: Separate from on-turn, at least in the current rules. This "off turn" cost escalation also scales with opportunity attacks, so off turn movement competes with opportunity attacks for stamina. Off turn cost escalation resets at the start of your turn.
> B5: Locked. Not sure if I should specify that you *can* use ranged defense if it's higher (though this would be rare and might be impossible in the system, at least unless I only allow cover to apply to the ranged defense - for now just say "use your melee defense, and you also get cover", or "use your melee defense" and reword cover to refer to defending from ranged attacks rather than applying to ranged defense rolls). Also, any time someone makes a ranged attack within anyone's melee range, they can make an opportunity attack (even if they're not the target of the ranged attack) once the ranged attack is done resolving.
> B6: Intent locked, mechanism open mechanic that I said before where it's every square for every person.
> B7: Exploratory.
> B8: Specified further up in this message.
> B9: Intent locked, mechanism open.
> B10: Mental stats are just not fully defined. For now, keep it as +1 initiative every other agility *and* +1 initiative every other cunning. Don't specify a tiebreaker for now.
> B11: Dive for cover happens after rolling damage. Keep all relevant offensive steps (declaring target, declaring stamina, rolling, adding up total) before defensive steps (reactions like diving for cover, declaring blocks, etc).
> B12: Intent locked, mechanism open. "Unlocking" a tree is just buying its first ability, which grants the tree core ability (instant stamina regen for fighter, manipulate turn order for rogue, spellcasting for wizard, etc) as well as some proficiencies. This ability serves as a prerequisite for Tier 1 abilities like the Tier N unlock abilities from A14 unlock Tier N abilities. For these core tree Tier 1 abilities, each core ability you already unlocked makes other core abilities cost 1 more, which effectively makes each unlocked tier cost more AP than the previous tree. The first is "free" in the sense that you're probably going to spend your first ability point to unlock a tree, but isn't literally free - if there are "treeless" abilities, then you could theoretically not unlock any tree. We're removing the concept of unlocking "tier trees" now that we have the abilities (either core Tier 1 or mostly opportunity cost Tier N > 1) that themselves have costs.
> B13: Explained in A2.
> B14: Placeholder exploratory rule that you recover 1 strain every 6 hours.
>
> Also: include reduced maximum stamina from taking damage as a mechanic excluded for its complexity but worth seriously considering since it solves the issue of characters only "going down" when they hit 0 HP.


**Round 2 (2026-11-01): clarifications (numbered as my questions) and the remaining Part F answers**

> 1. Moving out of a square threatened by an enemy is one way to provoke an opportunity attack (though not the only one - making a ranged attack in melee does the same thing). In order to prevent getting opportunity attacked when you do that, you can pay 1 stamina per square to stop a specific enemy from getting the option to opportunity attack you. You can do this multiple times to prevent multiple enemies from attacking you if multiple enemies threaten the square you're leaving. You can also pay it multiple times if you're moving more than one square. The enemies don't get to opportunity attack for free. Their attacks face the same (escalating) stamina costs as a normal attack, except it counts towards their off-turn escalation instead of their on-turn escalation, meaning they can get some extra efficient damage in even if they attacked on their turn. However, it also means that future opportunity attacks and off-turn movement is more expensive until the start of their next turn. By default you can only spend 1 stamina max on a given opportunity attack, meaning you can only opportunity attack with a small (base 1 stamina) weapon and only if you haven't already opportunity attacked already or done off turn movement since the start of your last turn (since both would increase the stamina cost so your first attack step would cost 2). Finesse and certain abilities will increase this cap, allowing you to take additional attack steps, opportunity attack multiple times, or opportunity attack and do off-turn movement all in the same round. Also, I might have it so each square adds that 1 + (FIN / 2), meaning if someone moves several squares within your reach then you have more opportunity to opportunity attack them - please add this w/ a certainty of "mechanism open", with the intent being that it's still sometimes possible to opportunity attack for more than 1 stamina even if you don't invest in finesse as long as the enemy exposes themself enough.
> 2. Every other point. Finesse caps at 6, so you can get a max of +3 stamina from your Finesse.
> 3. No, melee just adds to each attack step cost since each attack step is just doing more "attacking" - there's no separate "initiation" step for melee like there is with ranged, since melee doesn't need to track individual swings the way ranged tracks each shot separately. Each spell would say how it works.
> 4. Yes, replace the old system for now but note that the implementation is not confidently locked.
> 5. Replace the flat -1 AGI/FIN/CUN for now, but keep the AGI only improving your defense every 3rd/4th point regardless of your STR.
> 6. Odd values for now, unless I already have an odd value and no even value. The mental stats are not fully defined so it's basically just a placeholder to show that cunning improves initiative.
> 7. Dodge also, though mark dodge as being an uncertain inclusion in the system.
> 8. You can keep references to the tiers, just don't refer to unlocking tiers as separate things from buying the "next tier prereq" abilities.
> 9. Actually just keep 4 + level per night but mark mechanism open and note the 1 recovery per 6 hours (and no strain recovery bonus on levels ending in 5) as an alternative implementation in the explanation. Keep 1HP recovered per night of rest.
> 10. Yes, any enemy that threatens the shooter (has them within melee range). Same as movement-triggered OAs.
> 11. Yes, but please note that ranged weapon aiming is an unsolved problem that maximum HP damage would fix. This issue is going to be one of the first I have Claude try to help me solve, and this fix will be how I initially propose to solve it.
>
> Exertion might compete with strain and stamina in terms of overlapping meaning. I'm also looking more for something to refer to each "action-like step" - it's a bit awkward to say "I've done 4 exertions this turn".
>
> Grazing blocks cost 1.
>
> Armor reduces dodge via AGI reductions/modifications as described earlier.
>
> Weapon list should be marked as partially incomplete. For some placeholder abilities, give:
> * Hammer-type weapons ignore 1 armor automatically.
> * Daggers and shortswords are free to draw in between turns (unlike normal weapons which cost 1 stamina), and can be drawn even in a hand you used on your turn for something like a bow shot or somatic spellcasting (unlike normal weapons which can't be drawn in those hands until the start of your next turn).
>
> Otherwise use the weapon stats specified - things like dagger has a starting stamina attack cost of 1 and does 1d4+(AGI or FIN) damage, greatsword has a starting stamina attack cost of 3 and does 2d6+2*STR+FIN damage, etc.
>
> Spellcasting can't be done in light, medium, or heavy armor (or with a shield), barring some ability that says otherwise.
>
> Monk's core cost? As in, their core ability? If so, then just let them spend 1 strain to make perfect block costs not escalate for the current attack and mark that implementation as exploratory.
>
> Don't worry about getting the specifics of spellcasting exactly right. Just try to summarize my overall ideas and put them in the SHELVED section for now.
>
> Level 1.
>
> Will.
>
> Just use the -10 HP and system shock rules, with the assumption that taking damage that puts you to exactly 0HP incapacitates you but doesn't start system shock. Make sure to include max stamina reduction in SHELVED.
>
> Actually, put the permanent injury rules in SHELVED for now. Like the other SHELVED items, you can make these more of a loose collection of ideas rather than the exact mechanical specifications.
>
> Control effects TBD. Put a summary of the extended contest rules in SHELVED but don't include them in the "real" rules yet.
>
> No need to specify healing yet beyond the nightly rest. HP recovery spells like Healing Word or Cure Wounds from 5e aren't planned to be included, which might be important to communicate to Claude explicitly in some way.
>
> Don't worry about specifying NPC profiles beyond a quick mention in SHELVED.


**Round 3 (2026-11-01): answers to the Part F clarifications**

> Part F clarifications:
>
> 1. 1 stamina flat. Imagine you want to avoid all opportunity attacks. If you leave a square threatened by A and B, then you need to spend 2 stamina. If the next square you leave is threatened by only C, then you only spend 1 more stamina. If the next square you leave is also threatened by C, you need to spend 1 more stamina even though you already paid for C.
> 2. For now no, but this rule is not set in stone.
> 3. Odd (so 1, 3, and 5 each give +1 initiative, +1 OA max expenditure, and +1 crit range, and 2, 4, and 6 each give an extra +1 melee defense while holding a melee weapon).
> 4. Yes.
> 5. Let's say you roll 2d12+STR. If you roll below the current system shock, your system shock increases by 1 (bleeding out or similar). If you roll higher than 5 + your current system shock, your system shock decreases by 1 (naturally stabilizing). Just say you roll medicine (specifics TBD).
> 6. Yes, 1 per extra square flat. Every odd agility increases this by 1 square per expenditure, just like it increases off-turn movement by 1 per expenditure (except off-turn movement escalates in cost).
> 7. At medium range, your first aim step does not get the 1d6 (but it does get the FIN bonus), and if you don't aim at least once then the shot automatically misses. At long range, this applies to your first two aim steps instead. STR adds to some bow damages (longbows but not shortbows).
> 8. No overexertion.
> 9. Just try your best from the transcript and I'll fix it myself if I dislike it.
> 10. Skill system details TBD.
> 11. Yeah, numbers not set in stone but currently 6 + current HP + round(level / 5).
> 12. After making these changes, can you list which ones I need to look at?


**Round 4 (2026-11-01)**

> 1. You're right, finesse does not contribute. That was a typo, good catch.
> 2. Oh right, 10 + current system shock is the target number.
> 3. Correct. It's always 1 stamina.
>
> Otherwise looks good for now.


**Round 5 (2026-11-01)**

> Yes, you naturally recover on a roll of 15 + shock (so you need to get at least 24 on 2d12 + STR to improve from 9 to 8 shock naturally, and if you roll under a 19 then you go to 10 and die). Getting down to 0 system shock -either naturally or via someone else's help - ends it.


**Round 6 (2026-11-01)**

> You start at shock equal to your negative HP. Reaching either 10 system shock or -10HP kills you. Taking damage while already in system shock increases your shock by that amount. For now, say that you roll for system shock at the start of your turn.
>
> Example:
>
> You're at 3HP and take 5 damage. You got to -2HP and start at 2 system shock. On your next turn, you roll low, so you go to 3 system shock (but stay at -2HP). Then you take 3 more damage, going to -5HP and 6 system shock. Then you get fully stabilized over the next few turns, leaving you at -5HP (and therefore incapacitated) but not in system shock (so no more rolls every turn). If you took 1 damage at that point, you'd be at -6HP and 1 system shock (back to making rolls every turn until you die or system shock stops).


**Round 7 (2026-11-01)**

> * AT-5: Tone 8 down a little bit. Maybe that fits for 9, and 10 is the pinnacle of human ability/once in a generation sort of thing. None of these are literally superhuman; maybe that's better as an overall explanation to say that none of these are like "suplex 5000lbs" for a heroic fantasy/shounen themed game.
> * IN-1: Any more clarification needed here? I think this was just covered.
> * EQ-2: Some more weapons include Greataxe 2d6+3*STR base cost 3 and Spear 1d8+STR+FIN base cost 2 w/ reach (1 extra tile range). Change Greatsword back to 1d12. Some ranged weapons include Shortbow 1d6+FIN w/ 3 stamina per shot (escalating aim starting at 1 after that) and 6/12/18 square normal/medium/long range bands and Longbow 1d8+FIN+STR 5 stamina per shot (same aim) and 8/16/24 range.
> * CB-2: Just call it an "action" for now and make a note of the issues (misleading compared to D&D, implies multiple attack steps are treated as separate actions, etc).
> * CR-3: I think that's fine? Is there really no listed stamina regen formula? If not then I suspect that 4 + round(level / 10) is what I had.
> * DF-2: Do the latter wording for now.


**Round 8 (2026-11-01)**

> The wording you chose is fine. It's possible I'll move the design in a direction without magic (and I'd like the core rules to be interesting without leaning on a big list of abilities), but currently I'm guessing there'll be something like what you described.


**Round 9 (2026-11-01)**

> Initiative die is 2d12 as a temporary placeholder.
>
> A new character gets the 1 ability point at level 1, which they then presumably use to buy the core ability in their first ability tree. The "level 0" expertise point is assumed as part of the starting 5.
>
> Current stamina only changes when the maximum drops if the maximum is reduced below the current, since your current stamina can never exceed your maximum. Otherwise, your current stamina is unaffected.
>
> Yes. The Tier N unlock ability has the Tier N-1 unlock ability as a prereq. There might be other prereqs sprinkled throughout ability trees, but the actual Tier N normal abilities don't necessarily depend on anything other than the Tier N unlock ability.

---

# PART H: SHELVED (not current rules; idea bank)

These ideas are deliberately **out of the current rules**, but they're strong enough to remember.
- Each is a loose collection of your ideas, not a specification.
- Don't treat them as rules when critiquing the system. Do consider them as candidate solutions when the problem they address comes up.

### H-1 Maximum HP Damage
- **Why it's shelved:** you're not including it for now, but it's a strong contender to add later.
- **What it solves:**
  - **Ranged aiming lethality is an unsolved problem.** Aim adds damage, and without a cap that damage can wound. This is one of the first problems you plan to work on, and the cap is your initial proposed fix.
  - It differentiates STR, AGI and FIN.
- **The idea:**
  - Only part of an attack's damage can become HP loss: the weapon dice plus STR, floored by FIN on weapons that can use FIN, even if AGI was used. AGI and aim never count.
  - Everything else is pressure that costs the defender stamina but can't wound.
  - It applies after armor, before crit doubling.
- **Sources:** [p.183, p.207, p.1178, p.1200, p.1471]; questioned at [p.1720]; shelved by your ruling A2.
- **Later changes:**
  - *Packet 0.10.0:* the aim limit is a cap of this kind for shots: a shot's HP loss can't exceed the weapon's damage roll, so ranged aiming lethality has its fix, and the melee half stays shelved until melee shows it needs one.
    - *Now in:* the rules notes Aim and Not in This Version.

### H-2 Damage reducing max stamina
- **Why it's shelved:** excluded for its complexity, but worth serious consideration.
- **What it solves:** characters only "go down" when they hit 0 HP. Lost max stamina would let someone be knocked out of the fight before 0 HP. It would also give healing something to do besides HP, and give rest more meaning.
- **The idea:**
  - Taking damage lowers max stamina beyond the HP link (e.g. 2 max stamina per HP lost, until rest).
  - 0 max stamina means out of the fight but alive (the "luck, endurance, morale" state).
- **Sources:** [p.99–112, p.334, p.607, p.892, p.998]; shelved by your ruling.

### H-3 Lingering and permanent injuries
- **Tiers:**
  - Minor: heals by the next rest.
  - Major: heals over an extended period.
  - Permanent: needs substantial magic. Severed limbs, lost eyes, brain trauma; not quick-killing wounds.
- **Tables** by body part (head, torso, arm, leg), maybe by damage type.
- **Triggers** floated: 3 / 5 / 10 damage at once.
- **Effects** should change *what* you can do, not just subtract numbers.
- **Sources:** [p.339, p.368, p.371, p.386].

### H-4 Control effects / extended contests
- **The idea:** progressive tracks for grapple, Hold Person and charm.
  - The controller pays escalating stamina to roll (e.g. 1d6 + stat per step).
  - The target defends deterministically with stamina.
  - Unblocked effort advances the track: slowed, then restrained, then paralyzed.
  - Extra stamina pushes the track back.
- **Details you leaned toward:**
  - Advance on the controller's turn.
  - Damage to the controller reduces progression 1:1.
  - Effects need range and line of sight to keep rolling.
  - The effect ends if the controller stops paying.
  - Trip is an ordinary immediate attack, not a contest.
- **Rejected:** opposed 2d12 rolls ("rolling two sets of dice just to give each person something to do"); defense = 1 + attribute (too swingy).
- **Open:** which defense number, ideally with several sources like Melee and Ranged Defense.
- **Sources:** [p.871, p.1276, p.1858–1979].
- **Later changes:**
  - *Packet 0.11.1 (2026-11-17):* the hold rule (rules note Holds) takes this idea's first rung, without the roll, for a different job: stopping a beaten enemy getting away. The holder pays (tokens set aside until the end of its next turn), the target resists with stamina (it pays 1 + the tokens to leave), and hurting the holder ends it. This entry stays shelved for grapples, Hold Person and charms.

### H-5 Spellcasting (overall ideas)
- **Scope note:** you may move the design in a direction without magic; for now you expect something like the ideas below (round 8).
- **Economy:**
  - Spells use the shared stamina/strain economy.
  - Costs vary per spell, even within a rank.
  - Exceeding max strain adds stamina cost (CR-5).
- **Schools:**
  - Casters advance **spell schools** (wizards: the eight 5e schools) by spending Ability Points per rank.
  - Each school purchase grants a free spell.
  - Extra spells in an owned school cost Skill Points.
  - Rank 1 grants a strainless cantrip.
- **Early ranks:** ranks may be bought early at a stamina surcharge until you're on-tier. Never extra strain.
- **Out-leveled spells** get cheaper in strain, not stamina, possibly delivered through tier abilities.
- **Traditions:**
  - Arcane, divine and natural differ by tendency in their spell lists, not by rule.
  - Arcane casters get burst defense, not sustained tankiness.
  - No blanket discount for gishes; give them specific hybrid abilities.
- **Ideas:**
  - Some spells could scale per step like attacks ("committable" spells).
  - Classes might be organized by mental stat × magic domain.
  - Cleric and sorcerer might merge into a Will caster.
- **Sources:** [p.354, p.474, p.969, p.1033–1135, p.1680–1697, p.1763].

### H-6 NPC aggression profiles
- **The idea:**
  - About 3 attack/defense profiles per NPC, defaulting to the middle one, with stated triggers for switching.
  - Minions might reset stamina each turn or use fixed defense steps.
- **The goal:** a balance-tested default that GMs can override [p.1294].

### H-7 Stamina cap (hard flux)
- **Why it's shelved:** your ruling (2026-11-17). It "might not be a bad mechanic and it might end up in the game", but it layers a new core mechanic on a system that already has enough of them, so it isn't right for the current version. You weren't sure whether something else needs simplifying to make room for it, or the cap itself needs to change. Packet 0.11.0 had already left it out.
- **What it solves:**
  - Pressure that sticks. Recovery returns everything a probe costs (a 1-step attack takes 3.1 stamina from the sample fighter at Melee Defense 3; recovery is 4), so nothing sits between "back next turn" and a wound, and only big commitments count.
  - Stamina spent on offense and on defense would work differently, so a mis-tuned balance wouldn't tip into "whoever commits first wins" or "whoever is aggressive first dies". That's why you value hard flux in Starsector.
  - Long, armor-backed duels at higher Melee Defense, and true stalemates.
- **The idea (yours, 2026-11-15, offered as a first instinct to try):**
  - Stamina spent on perfect blocks and on avoiding opportunity attacks also lowers a cap that recovery can't pass.
  - The cap resets at the start of your turn if you made no perfect block and avoided no opportunity attack since your last turn.
  - Grazing blocks neither lower the cap nor prevent the reset, so armor gets a niche.
  - You wondered whether it could replace fluctuating maximum stamina, or bring back damage reducing maximum stamina (H-2), with an "overload" that downs you before 0 HP.
- **What was tried** (packet 0.10.1; an exact solver for duels in contact with no movement, and engine fights for groups):
  - *Your version:* under best play, 6.9 → 6.1 rounds at Melee Defense 4 and 15.7 → 14.2 at 5, with the first mover's share up about a point. It still shapes play: a fighter who ignores it gives up 7 points of win chance at Melee Defense 4 and 35–42 at 5. Engine agents, which ignore it, play duels of 3.3 rounds instead of 3.9, and 6.5 instead of 12.4 with one more point of guard.
  - *No exemption* (every block locks; it clears only after a round with no block): 2.6 / 4.2 / 5.8 rounds at Melee Defense 3 / 4 / 5, against 2.7 / 6.9 / 15.7. It snowballs: a fighter 4 stamina behind wins 7% at Melee Defense 4 (15% without it) and 11% at 5 (29%), and the first mover's share goes from 64% to 68% at 4. An opening price of 2 stamina brings the first mover back to 51–52% at 4 and 5.
  - *Partial clearing, decay, never clearing:* every version falls on one line, where a shorter fight comes with a bigger first-mover edge and a costlier deficit.
  - *As a replacement for the rising price of perfect blocks:* no. At a flat 1 a block, a duel at Melee Defense 4 never ends without the lock and lasts about 50 rounds with it.
  - *Stamina back for attacking* (your question about the other direction): favors the first attacker (73% → 86.5% at Melee Defense 3). Only a refund for attacks that draw no blood leaves first strike alone.
  - *Group fights in the engine,* under 0.10.1's movement: no measurable change, because a creature was down in round 1 in 81% of three-a-side fights. With the movement proposal that led to 0.11.0, the no-exemption lock shortened fights by about half a round, and in two a side it raised the first actor's side from 56% to 72%.
  - *A breather anyone may take,* in a duel: win-more. The fighter who uses it is the one who just went all in.
- **Merits:** light pressure leaves something behind; true stalemates end; a pressed fighter has a reason to back off and catch its breath, and a hold has something to deny; a public cap shows who's under pressure.
- **Why it stayed out:** a second number per creature, the GM's included, that changes on most blocks and is checked at every recovery; a small effect in fights of the 3–5 rounds you aim for; a strong form that snowballs; and a problem that 0.11.0's single escalation and 0.11.1's holds may now meet in other ways, unplayed.
- **What would bring it back:** signs in play that pressure doesn't stick: nobody wants to step back and catch their breath; small attacks feel pointless; both sides wait for the other to commit. Lighter candidates: numbers in the existing rules, or a breather that recovers extra if you neither attacked nor were attacked since your last turn. A cap would need to make room for itself, for example as one that turns perfect against grazing blocks into a real trade-off.
- **Sources:** C:2026-11-15, C:2026-11-17; `claude/Hard_Flux_First_Read_2026-11-15.md`, `claude/Cap_Duel_Study_2026-11-15.md`, `claude/Lock_Movement_Engine_Runs_2026-11-15.md` (claude.ai project). Now in the rules note Not in This Version.

### H-8 Dodge Defense
- **Why it's shelved:** your proposal (2026-11-19), "for now". Nothing in packet 0.11.2 used it: there were no spells, monster stat blocks or rules for hazards, so it was a number on every sheet that never came up.
- **What it was for** (DF-3, STATED): a rarely used, avoid-only defense for what you can't parry, such as a rolling boulder, a collapsing building or a touch spell; the equivalent of a Dexterity save in 5e. You marked its inclusion uncertain from the start [R2:7].
- **The rule (packets v0.9 to 0.11.2):** 1 + 1 per even Agility value, reduced by armor through Agility's defense steps (EQ-1); the base 1 is lost if Agility is below 0.
- **Overlap:** since packet 0.10.0, Ranged Defense also gains Agility's even values (Review F3, option 1), so Dodge matched Ranged Defense without the shield and the reaction bonus.
- **What would bring it back:** spells, monsters or hazards that you can't block with a weapon or shield and that need a defense of their own.
- **Sources:** DF-3; C:2026-11-19. Now in the rules note Not in This Version.

### H-9 Recovery holds (held stamina with no target)
- **Why it's shelved:** your call (2026-11-21), after the study below. You agreed that "this benefitting long range archers is the wrong approach", noted that "it is hard to have a stamina risk and payout system that doesn't reward those in very safe positions", and concluded "this just isn't really doing what I want it to do". It was never a rule.
- **What it was for:**
  - Pressure and "paycheck to paycheck" recovery, without a cap (H-7). Your framing: being in contact is itself the pressure, because recovering extra there is too risky. That is the hard-flux equivalent that keeps pressure on.
  - Making held stamina a core mechanic instead of only a tool for opportunity attacks.
  - A balancing knob for abilities besides strain, which would make dropping strain easier.
  - Possibly reviving the refund for shots and spells ("vulnerable, not exhausted").
- **The idea (yours, 2026-11-21):**
  - At the end of your turn, hold stamina with no target. It comes back when your holds do, and you recover extra with it, "say, half".
  - Your follow-ups: rare use, and almost none in actual engagements, would be a plus, with abilities enabling builds around it. Held stamina could return together with normal recovery, with holds set afterwards, so that this turn's recovery can go into a hold. Resting could be an action that escalates other costs, or forbid attacking, or cap what you do on the turn you hold.
- **What was tried** (packet 0.11.4; stamina arithmetic, an exact solver for an archer nobody can reach, engine fights, two fights played by hand, and the 17 November hold solvers with 0.11.4's wound rule):
  - *As written:* a character nobody attacks can hold 8 every turn and spend 8 a turn instead of 4 (10 if the extra is all of it). An archer behind a wall, against a sample fighter in its first range band who steps in reaction to each shot and blocks optimally, downs it within 6 rounds 59% of the time against 28% (24% against 6% in the second band). The first runs left out the reaction dash and gave much higher figures (56% against 36% within 4 rounds in the second band); those describe a fighter who can't step, such as one pinned in melee.
  - *In a duel in contact:* no change at any rate (exact).
  - *On a breather:* under the current order a fighter at 0 gains nothing. Set after recovering, from 0 it's back to full a turn sooner; from 3 it has 14 instead of 11 after two quiet turns.
  - *Hand play:* at a gap in a wall, a fighter that stepped back and held 4 (to gain 1) was reached through the dash phase and went down to an attack that was 92% to down it instead of 57%. On open ground, walking past a two-fighter screen cost an enemy 2 stamina, and the archer behind it died before its first turn.
  - *Engine fights* (eight scenarios, tactical agents): careful agents rested under once a fight per side and nothing moved beyond ±2–4 points. Agents that rested within an enemy's reach did worse (screened archer's side 45% → 38%).
  - *Limits* (first band, fighter steps in reaction): spending forfeits the extra, 30% within 6 rounds; no attack or shot while it's out, 28% within 6 rounds (no change) and 47% against 46% within 8; only if attacked since your last turn, no gain for the archer at all (you disliked this lever). Once per fight was proposed and not tested.
  - *The timing change for holds on enemies:* close three-on-one, lone fighter down in round 1 41.4% → 59.9% (55.3% with holds capped at 4); chase, a 7-HP fighter gets away 30.1% → 28.2%. The 7.1% quoted earlier predates 0.11.4's rule that a wounded holder's hold ends.
  - *Ranged by situation:* a plain longbow shot costs 4 and recovery is 4, so aim is the archer's exposure; a longbow's good range (8 squares) is inside a fighter's charge range (13). The only unpriced case is a shooter nobody can reach firing at a target that can't answer. Against a target that can't even step, such as one pinned in melee, a plain shot is about three-quarters of a 2-step melee attack; against one that can step, a lone archer is slow (28% within 6 rounds at close range).
- **Merits:** a reason to break contact and come back; a second use for held stamina; a hook for abilities.
- **Why it stayed out:** it pays only when you're safe for two turns, which fighters in melee rarely are, so it mostly serves shooters behind terrain or a front line; any risk-priced rule is free to whoever has no risk, so conditions can't fix that; the payoff where it works is about 3 stamina; it adds an end-of-turn choice and a forfeit to track (C1), and needs the recover-then-hold order; and no human playtest has shown the problem yet.
- **The best version found:** after you recover, hold any ready stamina with no target; it comes back at the end of your next turn with half extra, unless you attack, shoot or lose HP first.
- **What would bring it back:** play showing worn-out fighters who step back with nothing useful to do, or parties that want to rotate and find it pointless. A candidate form is an ability in a melee tree (a second wind) instead of a core rule. Whether the unanswered shooter is too strong is a separate question about shot numbers.
- **Not shelved:** held stamina as a cost for abilities ("hold 2 stamina to do X"; holding is worth roughly half of spending the same amount).
- **Sources:** C:2026-11-21; `claude/Held_Stamina_As_Core_2026-11-21.md`, `claude/Rest_Hold_Arithmetic_and_Timing_2026-11-21.md`, `claude/Rest_Hold_Sim_Study_2026-11-21.md`, `claude/Ranged_Pressure_By_Situation_2026-11-21.md`, and the engine experiment's diff in `claude/rest_hold_study/bundle_sim_2026-11-21.txt` (claude.ai project; engine branch `exp/rest-hold`, not merged). Now in the rules note Not in This Version.

### H-10 Strain
- **Why it's shelved:** your call (2026-11-22 to 2026-11-24), implemented in packet 0.12.0.
- **What it was for:** one shared rest-recovered pool (`6 + round(Level / 5)`, recovering `4 + round(Level / 10)` per night) replacing per-day uses and spell slots, so multiclassing didn't inflate total uses; overage (+1 stamina per point over max, counted after adding the ability's strain) as a soft limit taxing the present turn rather than locking players out.
- **What was found:**
  - Because cores ran on a nightly pool (6 strain at level 1, while the old Monk core always on was worth ~+43 points in a contact duel and one extra recovery ~+20), class balance swung sharply with how many fights per day the GM ran—recreating the pacing-dependent balance problem strain was meant to avoid.
  - It was a second tracked pool in a one-pool system (maximum, recovery rate, two advancement lines and an overage rule), while HP already carries lasting between-fight cost.
  - Exploratory strain-free cores can instead pay inside the fight (through ready stamina, held stamina, escalation or timing).
- **What would bring it back:** magic that needs a limit across fights that time, rituals, materials or HP can't provide, or abilities that truly need a per-day budget.
- **Sources:** CR-4, CR-5, CP-7, CP-8, MG-2; `claude/Dropping_Strain_2026-11-21.md`; design chats 2026-11-21 to 2026-11-24. Now in the rules note Not in This Version.

### H-11 Weapon proficiencies
- **Why it's shelved:** your call (2026-11-25), implemented in packet 0.12.1.
- **What it was for:** gating which weapons a character was trained with (granted by class core abilities, or bought with Expertise outside your class; proficiency lists were TODO, A12). In packet 0.12.0, proficiency gated Melee Defense's weapon, second-weapon and even-Finesse bonuses, plus the exploratory Rogue Tier-1 candidate Dual Wielding, while leaving attacks, ranged weapons, armor and shields untouched.
- **What replaces it:** treating weapon competence as investing Expertise in the attributes a weapon scales with, alongside weapon requirements (such as bow Strength requirements) and weapon-style class abilities. Holding any melee weapon now grants Melee Defense's weapon bonuses (subject to Finesse below 0), and Expertise buys attributes only.
- **What would bring it back:** exotic or technical weapons that attributes and class abilities can't cleanly differentiate, or playtesting showing that ungated weapon access blurs martial and non-martial roles.
- **Sources:** A12, DF-1, CP-2, CP-6; design chat 2026-11-25. Now in the rules note Not in This Version.

### H-12 Dual wielding
- **Why it's shelved:** your call (2026-11-26), implemented in packet 0.12.1. You noted that dual wielding has a reasonable chance of returning in some form (possibly in a different shape than the shelved version).
- **What it was for:** a universal +1 Melee Defense from carrying a second melee weapon in your other hand (no bonus to Ranged Defense, DF-1), plus the exploratory Rogue Tier-1 Dual Wielding (separate escalation counters per light melee weapon, forfeiting the +1 Melee Defense when attacking with both hands) and Tier-3 Paired Blades (keeping the +1 Melee Defense) candidates.
- **What was found:** without general off-hand attacking rules, a second melee weapon acted mostly as a passive +1 Melee Defense stat stick. After 0.10.0 cut shields from +2/+2 to +1/+1, that matched a shield's Melee Defense with none of a shield's restrictions, creating several exploits and distortions: (1) Monks hitting MD 4 alongside Poised Guard (which only banned armor and shields); (2) casters bypassing the no-shield rule via a second quick-draw blade between turns or holding two blades on non-casting turns; (3) versatile 2H users (longsword, reach-2 spear) and archers pulling a free second quick-draw blade between turns for MD 3; (4) 1H longsword + off-hand shortsword matching shield MD while also granting FIN 0 opportunity attacks and bypassing any future Shield Strength requirement; and (5) strictly penalizing single-blade concepts with an empty off hand.
- **What would bring it back:** a dedicated two-weapon fighting design (possibly quite different from this version) that gives holding a second weapon a clear tactical role without bypassing shields, Monk limits or casting restrictions.
- **Sources:** DF-1; design chat 2026-11-26. Now in the rules notes Not in This Version and Earlier Candidate Abilities.

---

*Supporting files: per-chunk ledgers (10 files, one per ~200 pages) with fuller quotes are available on request. They were the running ledger for this pass.*
