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

### Editorial

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
