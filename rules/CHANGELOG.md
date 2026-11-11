# Changelog

Every change to the rules notes in `rules/`, newest first. [[Playtest Packet]] is the index.

## How to write an entry

Add the entry under **Unreleased**, in the same commit as the change. One line per change:

`- [[Note]]: what changed, old → new. Why: the reason. Source: where it was decided.`

- **Why** names what the change serves or fixes: a pillar (P1–P4, C1), a review finding, a playtest or sim result. If you don't know why, write *Why: not recorded.* Never guess a reason.
- **Source** says where it was decided, so it can be found again: a review finding (Review F3), a ledger entry (Ledger MV-3), a sim report, or a design chat and its date.
- If the change affects the engine, end with *Engine:* and the component or preset that implements it.

File each entry under one of these headings:

| Heading | For |
|---|---|
| Rules | Anything that changes what a rule means: a new or removed rule, a changed number, cost or procedure. |
| Status | A status marker changing, for example Exploratory → Mechanism open. |
| Clarified | Wording that makes a rule clearer without changing what it means. If you're not sure it's only a clarification, it goes under Rules. |
| Editorial | Structure and formatting: splitting, renaming or moving notes, links, callouts. |

A commit that only fixes typos can skip the entry by putting `[no changelog]` in its commit message.

**Cutting a version:** rename **Unreleased** to the new version and its date, start a fresh empty **Unreleased** above it, and update the version line on [[Playtest Packet]].

## Unreleased

## 0.10.0 (2026-11-11)

The ranged package. None of it is in the engine yet: the baseline preset stays `v0.9.3`, and the engine work is specified in the project doc `claude/Sim_Requirements_Ranged_Package_2026-11-11.md`. The design chat's evidence is in `claude/Ranged_Bow_Placeholders_2026-11-10.md` (addenda 1–6) and the earlier `claude/Ranged_*` docs.

### Rules

- [[Range Bands]]: short / medium / long ranges, minimum aims and "beyond long misses" → a band width per weapon: no penalty out to one band width, **−2 to the shot's total for each further band** (floored at 0, measured after the target's reaction), and no maximum range. Band width is +1 square per odd Finesse value and −1 square per point of Strength below the weapon's requirement; at 0 or less you can't shoot the weapon. Restated in [[Finesse]], [[Weapons]], [[Quick Reference]] (Attribute Bonus Table) and [[Defined Terms]]. Why: the designer wants range to be plausible with no sudden cutoffs, and prefers linear bands with a flat penalty (with additive aim, geometric bands would let each aim point double the range); −2 per band with a free aim die (see [[Aim]]) makes bows stronger close in, weaker far out, and adds about one point of defense headroom (`claude/Ranged_Bow_Placeholders_2026-11-10.md`, addendum 1). Source: design chat, 2026-11-08/11. *Engine:* not implemented.
- [[Weapons]]: the bows. Shortbow 3 per shot, 1d6 + FIN, ranges 6 / 12 / 18 → 3 per shot (unchanged), 1d4 + FIN, band width 2, Precise. Longbow 5 per shot, 1d8 + FIN + STR, ranges 8 / 16 / 24 → 4 per shot, 1d8 + STR, band width 3, Strength 1. New warbow: 6 per shot, 1d10 + STR, band width 4, Strength 3, Piercing 1. New superheavy warbow (provisional): 8 per shot, 1d12 + STR, band width 5, Strength 5, Piercing 2. Why: the designer's placeholder bows, with Strength standing in for draw weight. Piercing gives the heavy bows an armor niche without making them deadlier against unarmored targets, and makes longbow vs warbow a real choice (longbow better against soft targets up close, warbow against armor and at range; addendum 3); extra damage dice (2d8, 3d4) pierced armor mostly by adding damage against everyone (addendum 2). The shortbow stays a d4 so it's easy to roll alongside the d6 aim dice, and keeps Finesse in its total (designer's ruling). The superheavy is kept provisionally: it's best against armor at every range, and against soft targets at extreme range (addendum 4). Source: design chat, 2026-11-10/11. *Engine:* not implemented.
- [[Weapons]]: new weapon properties **Piercing N** (ignores N armor; Hammer is restated as Piercing 1, the same effect) and **Precise** (shortbows: Finesse adds to the total but, like aim, not to the wound directly; the aim limit is the higher of the damage die and your Finesse, so unblocked damage up to Finesse reaches HP). Restated in [[Armor]], [[Critical Hits]], [[Attack Procedure]], [[Quick Reference]] and [[Defined Terms]]. Why: the heavy bows need Piercing. Precise is the designer's ruling, with a worked example in [[Weapons]]. A single Precise shot can't drop a typical caster (8 HP), so the shortbow does its work through several shots a turn. Finesse in the total made it much deadlier than the version without it at a shot cost of 2 (`claude/Ranged_Bow_Placeholders_2026-11-10.md`, addendum 7), so the shot cost stays 3: that puts a Finesse 3 shortbow between the Strength 1 and Strength 3 longbows up close and below them at range (addendum 8). The designer is fine with a strong close-range niche against soft targets, paid for by taking big range penalties further out. Source: design chat, 2026-11-11. *Engine:* not implemented.
- [[Actions and the On-Turn Surcharge]]: a ranged shot becomes an action, costing the shot cost + the surcharge, instead of a flat base cost outside the surcharge; the free aim die isn't an action. Restated in [[Ranged Attacks]], [[Aim]], [[Weapons]], [[Quick Reference]] (Stamina Costs) and [[Defined Terms]]. Why: with flat shots, cheap bows fire many shots a turn (the shortbow up to seven, downing a standing caster every time; `claude/Ranged_Bow_Placeholders_2026-11-10.md`, finding 2), and the designer agreed shots should count as actions. One counter shared with aim steps and melee attack steps was the least lethal option tested and works the way melee does (addendum 1), and the designer confirmed it. Source: design chat, 2026-11-10/11. *Engine:* not implemented.
- [[Aim]]: each aim step 1d6 + Finesse → **1d6**; every shot comes with **one free aim die** (not an action, no surcharge); new **aim limit**: the HP a shot takes can't exceed the weapon's damage roll (its die plus any Strength), with critical bonuses added on top. Melee gets no general wound cap. The known-problem warning goes, and the example is redone. Restated in [[Ranged Attacks]], [[Attack Procedure]], [[Critical Hits]], [[Quick Reference]], [[Defined Terms]] and [[Not in This Version]]. Why: fixes the packet's first open problem, aim damage wounding in full (Review F3); Finesse on aim dice was the main lethality driver in the ranged studies; the free die is the designer's choice alongside −2 per band; the designer ruled that critical bonuses apply after the limit and held off a general wound cap until melee shows it needs one. Source: design chat, 2026-11-10/11. *Engine:* not implemented.
- [[Critical Hits]]: TODO "Can aim dice be critical?" → **aim dice are never critical**. Critical dice ignore armor on top of any Piercing. Restated in [[Aim]] and [[Defined Terms]]. Why: the designer keeps the existing rule (only damage dice) until there's a reason to change it; letting aim dice crit with Finesse widening made the Finesse shortbow the best single-archer weapon against plate (addendum 3). Source: design chat, 2026-11-10/11. *Engine:* not implemented; the `v0.9.3` preset assumes aim dice *can* crit (Assumptions register), so a 0.10.0 preset needs the opposite.
- [[Ranged Attacks]]: the target may react by closing in on the shooter or backing away, as well as diving for cover. Its reaction still comes after the roll, just before blocks. Melee vs Ranged Defense, cover and the range penalty are all judged after the reaction. Whether a shot provokes is decided when it's declared, and the opportunity attacks come after the shot: an enemy needs to be able to make its attack both when the shot is declared and when the attacks happen. So one that comes within reach during the shot gets none, and so does one that's no longer within reach, for example because it backed away instead. Restated in [[Cover]], [[Opportunity Attacks]], [[Defenses]], [[Quick Reference]] and [[Defined Terms]]. Why: closing in on an archer to use Melee Defense, and backing away into a further band, are the designer's proposals. The designer considered moving the reaction before the roll (better fiction, a little useful uncertainty) but kept it after the roll for now: it keeps "the attacker does everything, then the defender does everything", which keeps resolution moving, and it's what has been tested. An enemy that backs away from the shooter is doing that instead of attacking. Source: design chat, 2026-11-10/11. *Engine:* not implemented; the `v0.9.3` preset measures range at declaration and has no ruling on enemies that leave reach.
- [[Cover]]: half +2 → **+1**, three-quarters +5 → **+2**; a dive that ends fully behind cover still counts as three-quarters. Restated in [[Defined Terms]]. Why: the designer's placeholder numbers; with shots bounded by the aim limit, +5 made a reactive dive close to immunity against a lone archer (`claude/Ranged_Brainstorm_Round2_2026-11-09.md`, finding 3). Source: design chat, 2026-11-10. *Engine:* not implemented.
- [[Defenses]]: new Ranged Defense sources: **+1 if you moved in reaction to this shot** (off-turn movement bought when targeted by this shot; against a second shot you have to move again; moving on your own turn or between turns doesn't count) and **+1 per even Agility value**, reduced in medium and heavy armor as for Melee and Dodge Defense. A second weapon in the other hand adds nothing to Ranged Defense. Restated in [[Agility]], [[Armor]], [[Cover]] and [[Quick Reference]] (Attribute Bonus Table, Sample Character). Why: the designer's placeholder numbers; the designer wants target speed to matter to a shot. The designer chose the per-shot reading of moving (simpler, to be tested further) and Agility's even values with the existing armor steps. Source: design chat, 2026-11-10/11. *Engine:* not implemented.
- [[Shields]]: +2 Melee Defense and +2 Ranged Defense → **+1 and +1**. A second weapon in the other hand stays +1 Melee Defense. Restated in [[Defenses]] and [[Quick Reference]] (Sample Character: Melee Defense 4 → 3, Ranged Defense 3 → 2). Why: earlier testing showed shields were very strong for defense; at +1, two-handed weapons and dual wielding need less adjustment to stay at parity. Being tried out. Source: designer's ruling, design chat, 2026-11-11. *Engine:* not implemented; every engine preset still gives a shield +2.

### Editorial

- [[Not in This Version]]: the Maximum HP Damage entry now points to the aim limit as the ranged version. Adds split attribute bonuses for ranged, and creature sizes with their range penalties (Tiny −8, Small −4, Medium −2, Large −1), both shelved by the designer. Why: keeping the list current; sizes wait until the packet has size categories. Source: design chat, 2026-11-11.
- [[Open Questions]]: "ranged aim lethality is the first problem to solve" → ranged lethality under 0.10.0 is untested at normal ranges. Why: the aim limit addresses the old problem. Source: design chat, 2026-11-11.
- [[Playtest Packet]]: version line 0.9.3 → 0.10.0. Why: cutting 0.10.0. Source: designer's request, 2026-11-11.
- [[CHANGELOG]]: the *Engine:* notes on the 0.9.1 and 0.9.2 entries, "not implemented" → the switches and presets (`v0.9.1`, `v0.9.2`) that implement them. No rule changes. Why: the engine now implements both versions. Source: engine pull request, 2026-11-08.

## 0.9.3 (2026-11-08)

### Rules

- [[HP]]: nightly HP recovery works the same below 0 HP (at −3 HP with Strength 0, a night of rest takes you to −2); the packet didn't say where recovery starts from. Restated in [[Rest and Healing]]. Why: simulating fights in series needs to know how a downed character heals; the designer ruled it recovers like any other wound. Source: designer's answers to the adventuring-day plan's questions (`sim/docs/CAMPAIGN_PLAN.md`), 2026-11-08. *Engine:* not implemented (rest is outside a single fight; planned for the campaign layer, phase C1).
- [[Dying and Death]]: when a fight ends with anyone still in System Shock, turns continue in initiative order until everyone is stabilized or dead, and allies who aren't incapacitated can help them stabilize (how is **TODO**). Previously the packet didn't say what happens to the dying once a fight is over. Why: the designer's ruling, so a fight's end doesn't freeze or skip the dying rolls. Source: designer's answers to the adventuring-day plan's questions (`sim/docs/CAMPAIGN_PLAN.md`), 2026-11-08. *Engine:* not implemented; the campaign plan uses a stand-in for the help (each active ally gives one extra roll that can only lower Shock), recorded as an engine assumption, not a rule.

### Clarified

- [[Dying and Death]], [[HP]] and [[Rest and Healing]]: you stay incapacitated until rest brings you back to 1 HP or more, so a character at 0 HP or below can't take part in a later fight. This follows from "at 0 HP or below, you're incapacitated". Why: the designer confirmed the reading for simulating fights in series. Source: designer's answers to the adventuring-day plan's questions (`sim/docs/CAMPAIGN_PLAN.md`), 2026-11-08.

### Editorial

- [[Playtest Packet]]: version line 0.9.2 → 0.9.3. Why: cutting 0.9.3. Source: designer's request, 2026-11-08.

## 0.9.2 (2026-11-08)

### Rules

- [[Critical Hits]]: if any damage gets past blocks and armor, each critical die adds +1, replacing "if any die is critical, double the damage left after armor". Each critical die still ignores 1 armor. The TODO on doubling once per attack goes with the doubling, and the melee example gains a critical-die case. Restated in [[Attack Procedure]] (step 7), [[Defined Terms]] and [[Quick Reference]] (Attack Sequence). Why: doubling was the game's main luck multiplier (Review F2, P2) and made the opener's all-in the right bet: under optimal play, ×2 openers end 33% of level-1 duels on the first attack, while linear-crit openers decline the gamble (`claude/Exchange_Escalation_and_Guards.md` §3.1). +1 rather than +2 because +2 carries most of the remaining all-in risk (same doc, §3.5). "Only if something gets past" keeps a full block a full answer: a +2 bonus added regardless wounded a defender who blocked everything in 44% of 2-step attacks in the review's oracle simulator (`claude/Crit_Rule_Alternatives.md` §1). Source: design chat, 2026-11-06/08. *Engine:* `crit` kind `per_die_if_through` (bonus 1), in the `v0.9.2` preset. The `v0.9` preset still doubles (`crit/double_once`), and `crit/per_die_bonus`, which adds its bonus even when nothing gets past armor, stays the review's parity variant.
- [[HP]]: maximum HP = 8 + 2 per even Strength value, up from 6 + 2 (8, 8, 10, 10, 12, 12, 14 for Strength 0–6). [[Strength]]'s wording is unchanged. Restated in [[Quick Reference]] (Sample Character: HP 8 → 10, maximum stamina 14 → 16). Why: HP is the main lever on how often a fresh defender can't survive an opener's maximum all-in (P2). In the duel solver at Melee Defense 4 with +1 per critical die, sample HP 10 puts the sample mirror at 0.9% (`claude/Exchange_Escalation_and_Guards.md` §2.4). In engine party days, base 8 with the new crit cut "someone dies" in a fresh two-bandit fight from 34% to 24% (`claude/Party_Day_Study.md`). Base 8 is the designer's starting point "for now". Known costs: the two-hander mirror still fails that guard at sample HP 10 (7.8%; 0.4% at base 10). Maximum stamina rises with HP, so attacks grow too, and focus-fire drops don't fall (61% → 70% in that fight). Source: design chat, 2026-11-08. *Engine:* `resources.hp_base = 8` with `hp_strength = "per_even"`, in the `v0.9.2` preset; the `v0.9` preset still uses HP = 6 + Strength.

### Editorial

- [[Playtest Packet]]: version line 0.9.1 → 0.9.2. Why: cutting 0.9.2. Source: design chat, 2026-11-08.

## 0.9.1 (2026-11-06)

### Rules

- [[Opportunity Attacks]]: removed the opportunity attack cap (1 stamina, +1 per odd Finesse) and the optional per-square cap; the off-turn escalation is now the only limit on an opportunity attack. [[Finesse]] loses its odd-value cap bonus. Restated in [[Off-Turn Escalation]]'s example, [[Defined Terms]] and [[Quick Reference]] (Stamina Costs, Attribute Bonus Table, Sample Character). Why: no sign it was solving a real problem, or that it was the best solution if one exists; may return later. In the engine, turning opportunity attacks off entirely changed no measured outcome (`claude/Movement_Ranged_Exploration.md` §6b, check C2). Source: design chat, 2026-11-05/06. *Engine:* `opportunity.cap_rule = "none"`, in the `v0.9.1` and `v0.9.2` presets; the `v0.9` preset still applies the cap.
- [[On-Turn Movement]]: each extra on-turn movement purchase moves 1 square, not 1 + odd Agility; the cost stays 1 stamina, flat. [[Agility]]'s odd values no longer add to it (they still add free movement and off-turn squares). Restated in [[Quick Reference]]. Why: uncapped purchases at up to 4 squares a stamina let a melee fighter cross 30+ squares in one turn and made chases unwinnable by speed. The designer wants a melee fighter who starts far away to arrive low on stamina, not to be kited for several turns (Review F10; `claude/Movement_Ranged_Exploration.md` §2c, §3). Source: design chat, 2026-11-05/06. *Engine:* `movement.extra_squares = "one"`, in the `v0.9.1` and `v0.9.2` presets; not in the `v0.9` preset.
- [[Starting Combat and Turn Structure]]: initiative is 2d12 + Cunning (every point), not 2d12 + 1 per odd Agility + 1 per odd Cunning. [[Agility]] loses its initiative bonus; [[Cunning]] gives +1 per point. Restated in [[Quick Reference]]. Why: Agility was overloaded (initiative, movement and defense); a placeholder until initiative gets a fuller design (see [[Not in This Version]]). Source: design chat, 2026-11-05/06. *Engine:* `turn_order.bonus = "cunning"`, in the `v0.9.1` and `v0.9.2` presets.
- [[Strength]]: +2 maximum HP per even value and +1 nightly HP recovery per odd value, replacing +1 HP per point. [[HP]]: maximum HP = 6 + 2 per even Strength value; recovery 1 + 1 per odd Strength value per night. Restated in [[Rest and Healing]] and [[Quick Reference]] (Attribute Bonus Table, Sample Character: HP 8 unchanged, now recovering 2 per night). Why: the designer's proposal, so high-Strength characters keep taking hits day after day and a 5 or 6 feels like embodying the stat. +1 HP per point was flagged as suspect, and in-fight HP proved worth little against stamina (`claude/Strength_Value_Experiment.md`). Known costs: recovery's value depends on fights per rest, and the Strength 0 character heals slowest (see [[Open Questions]]). Source: design chat, 2026-11-05/06. *Engine:* the HP formula is `resources.hp_strength = "per_even"`, in the `v0.9.1` and `v0.9.2` presets. Nightly HP recovery isn't modeled: the engine plays single fights.
- [[Dying and Death]]: the System Shock dying roll is 2d12 + Will, not 2d12 + Strength. [[Will]] gains it as its first combat benefit. Why: proposed in the chat (refusing to die fits Will, and Strength already covers the body through HP); the designer agreed. Source: design chat, 2026-11-05/06. *Engine:* `dying.roll_attribute = "will"`, in the `v0.9.1` and `v0.9.2` presets.
- [[Intelligence]]: odd values reduce the rising cost of core abilities (one owned core per odd value isn't counted); even values grant extra Ability Points at levels 10/40/70 (Intelligence 2), 20/50/80 (4) and 30/60/90 (6), applying retroactively. Restated in [[Costs]], [[Class Trees]], [[Character Advancement]] and [[Quick Reference]]. Why: Intelligence had no bonuses. The level schedule keeps the AP from being a level-1 auto-pick while making Intelligence a flagship over a career; the odd-value discount was the designer's favorite of the odd-value candidates. Source: design chat, 2026-11-05/06. *Engine:* build budget checks only, `resources.core_discount = "odd_intelligence"` and `resources.bonus_ap = "even_intelligence"`, in the `v0.9.1` and `v0.9.2` presets.

### Status

- [[Will]]: TODO → Exploratory. [[Intelligence]]: TODO → Exploratory. [[Opportunity Attacks]]: "Mechanism open (avoidance and cap)" → "Mechanism open (avoidance)". [[Strength]]: Exploratory, now noting that the even/odd split is the designer's proposal. Why: they follow from the changes above. Source: design chat, 2026-11-05/06.

### Clarified

- [[Strain]]: states that no attribute changes maximum strain or strain recovery; both depend only on level. This was already the rule. Why: the designer decided strain stays level-only, because choosing strain capacity isn't a fun choice. Source: design chat, 2026-11-05/06.

### Editorial

- [[Magic]]: added a "Direction Being Explored" section, marked not yet rules: spell schools as tracks within a caster tree (ranks with AP, extra spells with SP), a casting stat per tree, and riders that scale with a fitting stat of their own. Why: to record the current thinking where the Magic note only said TODO. Source: design chat, 2026-11-05/06.
- [[Not in This Version]]: added a Strength requirement for shields, and initiative you have agency over (bidding). [[Open Questions]]: updated the attribute questions for the changes above. Why: the designer deferred both ideas rather than adopting them. Source: design chat, 2026-11-05/06.
- [[Playtest Packet]]: version line 0.9 → 0.9.1. Why: cutting 0.9.1. Source: design chat, 2026-11-05/06.

- [[Playtest Packet]]: split the v0.9 packet into one note per rule, with the old single file replaced by the index. No rule changes. Why: the single file had become unwieldy to edit and navigate. Source: design chat, 2026-11-04.
  - Every section is a note; a subsection got its own note only where it carries its own status marker, and its parent embeds it. The layout is described in `rules/README.md`.
  - The two Armor sections (under Combat and under Equipment) are merged into [[Armor]]. Only the two sentences pointing from one to the other were dropped.
  - The packet's "What changed from v0.8" section moved here, as the 0.9 entry.
  - Examples, known problems and optional rules are Obsidian callouts; "see **Section**" references are links.

- [[Quick Reference]]: each section now names the rules it restates, and [[Rest and Healing]] and [[Character Advancement]] link the rules they repeat. `rules/README.md` gains a "Changing a rule" checklist. No rule changes. Why: a rule change could leave a restated copy stale, with nothing pointing from the rule to its copies. Source: design chat, 2026-11-04.

- [[Full Packet]]: new generated note that embeds every note in reading order, and each note gains generated `up`/`prev`/`next` properties along the same order. Both come from the Contents of [[Playtest Packet]] via `tools/check_rules.py --nav`. No rule changes. Why: to read the notes in sequence without hand-kept links. Source: design chat, 2026-11-05.

## 0.9

Changes from v0.8. Moved here from the packet's former "What changed from v0.8" section; it predates the headings above.

- **Maximum HP Damage is removed for now** (see [[Not in This Version]]). Everything that gets past blocks and armor is HP damage.
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
