# How These Notes Work

The rules text, one note per rule. Start at [[Playtest Packet]]: it lists every note in reading order. Every change to these notes gets a line in [[CHANGELOG]].

## Layout

- Every section of the packet is a note. A subsection becomes its own note only if it carries its own status marker. Its parent then embeds it (`![[Aim]]`) where it used to be, so the parent still reads as one section.
- Core Concepts and Quick Reference stay whole, because they're read together.
- Folders are the packet's parts, numbered for reading order. Note names aren't numbered, so links read naturally and match the engine's citations: `"Packet: Blocking"` in the engine means [[Blocking]], and `"Packet: Triggers"` means the Triggers heading inside [[Opportunity Attacks]].
- Note names are unique across `rules/`.

## Formatting a note

- First line: `# Note Name`, exactly the file name.
- Then the status line, `*Status: …*`, as before. It stays in the text rather than in properties, so it shows when the note is embedded or compiled.
- Subsections are `##`.
- Callouts: examples are `> [!example] Example: Title`; known problems `> [!warning]`; open naming or design questions `> [!question]`; optional rules `> [!note]`.
- References to other rules are links: `(see [[Cover]])`, or `[[Opportunity Attacks#Making Opportunity Attacks|Making Opportunity Attacks]]` for a heading inside a note. Inside a table, leave out the `|…` part.
- Bold is for emphasis, not for references.

## Changing a rule

Rules interact, and several notes repeat other notes' rules. Before reasoning about a change or proposing one, read the whole packet, not just the note in question:

```bash
python3 tools/check_rules.py --compile packet.md   # about 8,500 words; packet.md is gitignored
```

When the change is made, in the same commit:

1. Edit the rule's own note.
2. Update every restatement. Search `rules/` for links to the note (`[[Aim`) and for the rule's own terms and numbers (`aim step`, `1d6 + Finesse`), because links alone miss some. Restatements live in:
   - [[Quick Reference]], whose sections each name what they restate on their *Restates* line, including [[Quick Reference#Sample Character|Sample Character]];
   - [[Defined Terms]];
   - notes that state the same rule from both sides: the attribute notes and the [[Defenses]] tables; [[Stamina]], [[Strain]], [[Rest and Healing]] and [[Character Advancement]].
3. Add the [[CHANGELOG]] line.
4. Run `python3 tools/check_rules.py`. If the engine implements the rule, its change goes in the same commit (see `CLAUDE.md`).

A new Quick Reference section needs its own *Restates* line; the checker fails without one.

## Adding, renaming or removing a note

- List it in [[Playtest Packet]] at its place in the reading order. The checker fails on notes the index doesn't reach.
- Rename inside Obsidian, so its links update. Outside Obsidian, update every link to it and any engine `cites` that name it.
- Log it in [[CHANGELOG]] under Editorial.

## Checks, and the packet as one file

From the repo root:

```bash
python3 tools/check_rules.py                       # links resolve, titles match, the index reaches every note
python3 tools/check_rules.py --compile packet.md   # the whole packet as one plain Markdown file
```

The compiled file is for reading or sharing the whole packet at once (a playtest handout, a full review). Don't commit it; the notes are the source.

CI (the `rules` workflow) runs the check on every push that touches `rules/`, and fails if `rules/` changed without a [[CHANGELOG]] entry.

## Obsidian setup

- Open the repo root as the vault, so notes in `design/` can link to rules too.
- Appearance → Show inline title: off. Each note already starts with its title.
- Files and links → `Use [[Wikilinks]]`: on. Automatically update internal links: on.
- Files and links → Excluded files: `sim/src` and `sim/tests`, to keep search and the graph to the documents.
