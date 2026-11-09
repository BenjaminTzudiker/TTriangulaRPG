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

- [[Critical Hits]]: if any damage gets past blocks and armor, each critical die adds +1, replacing "if any die is critical, double the damage left after armor". Each critical die still ignores 1 armor. The TODO on doubling once per attack goes with the doubling, and the melee example gains a critical-die case. Restated in [[Attack Procedure]] (step 7), [[Defined Terms]] and [[Quick Reference]] (Attack Sequence). Why: doubling was the game's main luck multiplier (Review F2, P2) and made the opener's all-in the right bet: under optimal play, ×2 openers end 33% of level-1 duels on the first attack, while linear-crit openers decline the gamble (`claude/Exchange_Escalation_and_Guards.md` §3.1). +1 rather than +2 because +2 carries most of the remaining all-in risk (same doc, §3.5). "Only if something gets past" keeps a full block a full answer: a +2 bonus added regardless wounded a defender who blocked everything in 44% of 2-step attacks in the review's oracle simulator (`claude/Crit_Rule_Alternatives.md` §1). Source: design chat, 2026-11-06/08. *Engine:* not implemented; the `v0.9` preset doubles (`crit/double_once`), and the registered `crit/per_die_bonus` adds its bonus even when nothing gets past armor, so it isn't this rule.
- [[HP]]: maximum HP = 8 + 2 per even Strength value, up from 6 + 2 (8, 8, 10, 10, 12, 12, 14 for Strength 0–6). [[Strength]]'s wording is unchanged. Restated in [[Quick Reference]] (Sample Character: HP 8 → 10, maximum stamina 14 → 16). Why: HP is the main lever on how often a fresh defender can't survive an opener's maximum all-in (P2). In the duel solver at Melee Defense 4 with +1 per critical die, sample HP 10 puts the sample mirror at 0.9% (`claude/Exchange_Escalation_and_Guards.md` §2.4). In engine party days, base 8 with the new crit cut "someone dies" in a fresh two-bandit fight from 34% to 24% (`claude/Party_Day_Study.md`). Base 8 is the designer's starting point "for now". Known costs: the two-hander mirror still fails that guard at sample HP 10 (7.8%; 0.4% at base 10). Maximum stamina rises with HP, so attacks grow too, and focus-fire drops don't fall (61% → 70% in that fight). Source: design chat, 2026-11-08. *Engine:* not implemented; the `v0.9` preset still uses HP = 6 + Strength (v0.9).

### Editorial

- [[Playtest Packet]]: version line 0.9.1 → 0.9.2. Why: cutting 0.9.2. Source: design chat, 2026-11-08.

## 0.9.1 (2026-11-06)

### Rules

- [[Opportunity Attacks]]: removed the opportunity attack cap (1 stamina, +1 per odd Finesse) and the optional per-square cap; the off-turn escalation is now the only limit on an opportunity attack. [[Finesse]] loses its odd-value cap bonus. Restated in [[Off-Turn Escalation]]'s example, [[Defined Terms]] and [[Quick Reference]] (Stamina Costs, Attribute Bonus Table, Sample Character). Why: no sign it was solving a real problem, or that it was the best solution if one exists; may return later. In the engine, turning opportunity attacks off entirely changed no measured outcome (`claude/Movement_Ranged_Exploration.md` §6b, check C2). Source: design chat, 2026-11-05/06. *Engine:* not implemented; the `v0.9` preset still applies the cap.
- [[On-Turn Movement]]: each extra on-turn movement purchase moves 1 square, not 1 + odd Agility; the cost stays 1 stamina, flat. [[Agility]]'s odd values no longer add to it (they still add free movement and off-turn squares). Restated in [[Quick Reference]]. Why: uncapped purchases at up to 4 squares a stamina let a melee fighter cross 30+ squares in one turn and made chases unwinnable by speed. The designer wants a melee fighter who starts far away to arrive low on stamina, not to be kited for several turns (Review F10; `claude/Movement_Ranged_Exploration.md` §2c, §3). Source: design chat, 2026-11-05/06. *Engine:* `movement.extra_squares = "one"`; not in the `v0.9` preset.
- [[Starting Combat and Turn Structure]]: initiative is 2d12 + Cunning (every point), not 2d12 + 1 per odd Agility + 1 per odd Cunning. [[Agility]] loses its initiative bonus; [[Cunning]] gives +1 per point. Restated in [[Quick Reference]]. Why: Agility was overloaded (initiative, movement and defense); a placeholder until initiative gets a fuller design (see [[Not in This Version]]). Source: design chat, 2026-11-05/06. *Engine:* not implemented.
- [[Strength]]: +2 maximum HP per even value and +1 nightly HP recovery per odd value, replacing +1 HP per point. [[HP]]: maximum HP = 6 + 2 per even Strength value; recovery 1 + 1 per odd Strength value per night. Restated in [[Rest and Healing]] and [[Quick Reference]] (Attribute Bonus Table, Sample Character: HP 8 unchanged, now recovering 2 per night). Why: the designer's proposal, so high-Strength characters keep taking hits day after day and a 5 or 6 feels like embodying the stat. +1 HP per point was flagged as suspect, and in-fight HP proved worth little against stamina (`claude/Strength_Value_Experiment.md`). Known costs: recovery's value depends on fights per rest, and the Strength 0 character heals slowest (see [[Open Questions]]). Source: design chat, 2026-11-05/06. *Engine:* not implemented (HP recovery is outside a single fight; the HP formula isn't).
- [[Dying and Death]]: the System Shock dying roll is 2d12 + Will, not 2d12 + Strength. [[Will]] gains it as its first combat benefit. Why: proposed in the chat (refusing to die fits Will, and Strength already covers the body through HP); the designer agreed. Source: design chat, 2026-11-05/06. *Engine:* not implemented.
- [[Intelligence]]: odd values reduce the rising cost of core abilities (one owned core per odd value isn't counted); even values grant extra Ability Points at levels 10/40/70 (Intelligence 2), 20/50/80 (4) and 30/60/90 (6), applying retroactively. Restated in [[Costs]], [[Class Trees]], [[Character Advancement]] and [[Quick Reference]]. Why: Intelligence had no bonuses. The level schedule keeps the AP from being a level-1 auto-pick while making Intelligence a flagship over a career; the odd-value discount was the designer's favorite of the odd-value candidates. Source: design chat, 2026-11-05/06. *Engine:* not implemented (character-building budgets only).

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
