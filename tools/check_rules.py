"""Checks for the rules notes in rules/, and a compiler that joins them into one file.

    python3 tools/check_rules.py                    links resolve, titles match, index reaches every note
    python3 tools/check_rules.py --changelog BASE   if rules/ changed since BASE, CHANGELOG.md did too
    python3 tools/check_rules.py --compile OUT.md   the whole packet as one plain Markdown file

Standard library only. The layout these checks enforce is described in rules/README.md.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULES = ROOT / "rules"
INDEX = "Playtest Packet"
CHANGELOG = "CHANGELOG"
META = {"README", CHANGELOG}  # notes about the rules, not rule notes
SKIP_MARK = "[no changelog]"

# [[Note]], [[Note#Heading]], [[Note|alias]], [[#Heading]], ![[Note]]; "\|" inside tables.
LINK = re.compile(r"(!?)\[\[([^\]#|\\]*)(?:#([^\]|\\]+))?(?:\\?\|([^\]]*))?\]\]")
HEADING = re.compile(r"^(#+)\s+(.+?)\s*$", re.M)
FENCE = re.compile(r"^```.*?^```", re.M | re.S)
INLINE_CODE = re.compile(r"`[^`\n]*`")


def load() -> tuple[dict[str, Path], list[str]]:
    notes: dict[str, Path] = {}
    problems = []
    for path in sorted(RULES.rglob("*.md")):
        if any(part.startswith(".") for part in path.relative_to(RULES).parts):
            continue
        if path.stem in notes:
            problems.append(f"two notes named {path.stem!r}: {notes[path.stem]} and {path}")
        notes[path.stem] = path
    return notes, problems


def prose(text: str) -> str:
    """Text with code removed, so examples of link syntax aren't read as links."""
    return INLINE_CODE.sub("", FENCE.sub("", text))


def headings(text: str) -> set[str]:
    return {m.group(2) for m in HEADING.finditer(prose(text))}


def links(text: str) -> list[tuple[bool, str, str | None, str | None]]:
    return [(m.group(1) == "!", m.group(2).strip(), m.group(3), m.group(4))
            for m in LINK.finditer(prose(text))]


def contents_links(index_text: str) -> list[str]:
    """Notes listed under the index's Contents heading, in order."""
    part = index_text.split("\n## Contents\n", 1)
    if len(part) != 2:
        sys.exit(f"{INDEX}.md has no '## Contents' section")
    return [target for _, target, _, _ in links(part[1]) if target]


def check() -> list[str]:
    notes, problems = load()
    texts = {name: path.read_text() for name, path in notes.items()}
    heads = {name: headings(text) for name, text in texts.items()}

    for name, text in texts.items():
        if name not in META and not text.startswith(f"# {name}\n"):
            problems.append(f"{name}: first line should be '# {name}'")
        for _, target, heading, _ in links(text):
            note = target or name
            if note not in notes:
                problems.append(f"{name}: link to missing note [[{target}]]")
            elif heading and heading not in heads[note]:
                problems.append(f"{name}: link to missing heading [[{target}#{heading}]]")

    if INDEX not in texts:
        return problems + [f"no index note {INDEX}.md"]
    reached: set[str] = set()
    todo = [t for t in contents_links(texts[INDEX]) if t in notes]
    while todo:
        name = todo.pop()
        if name in reached:
            continue
        reached.add(name)
        todo += [t for embed, t, _, _ in links(texts[name]) if embed and t in notes]
    for name in sorted(set(notes) - reached - META - {INDEX}):
        problems.append(f"{name}: not reached from the Contents of {INDEX}")
    return problems


def check_changelog(base: str) -> list[str]:
    def git(*args: str) -> str:
        return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True,
                              text=True).stdout

    changed = [f for f in git("diff", "--name-only", "-z", base, "HEAD", "--", "rules/").split("\0") if f]
    if not changed or f"rules/{CHANGELOG}.md" in changed:
        return []
    if SKIP_MARK in git("log", "--format=%B", f"{base}..HEAD"):
        return []
    since = base[:12] if re.fullmatch(r"[0-9a-f]{40}", base) else base
    return [f"rules/ changed since {since} without an entry in rules/{CHANGELOG}.md "
            f"({', '.join(changed[:5])}{'…' if len(changed) > 5 else ''}). Add a line under "
            f"Unreleased (format at the top of that file), or put {SKIP_MARK} in the commit "
            "message for a typo-only fix."]


def compile_packet(out: Path) -> None:
    """Join the notes in index order into one Markdown file: links become bold text, embeds
    are expanded in place, callouts become bold-titled quotes, headings nest by part."""
    notes, _ = load()
    texts = {name: path.read_text() for name, path in notes.items()}
    emitted: set[str] = set()

    def plain(text: str) -> str:
        def link(m: re.Match[str]) -> str:
            note, heading, alias = m.group(2).strip(), m.group(3), m.group(4)
            return f"**{alias or heading or note}**"

        text = LINK.sub(link, text)
        return re.sub(r"^> \[!\w+\] (.+)$", r"> **\1**\n>", text, flags=re.M)

    def render(name: str, depth: int) -> str:
        emitted.add(name)
        lines = []
        for line in texts[name].splitlines():
            embed = re.fullmatch(r"!\[\[([^\]#|]+)\]\]", line.strip())
            if embed and embed.group(1) in texts:
                lines.append(render(embed.group(1), depth + 1))
                continue
            m = HEADING.match(line)
            if m:
                line = "#" * (len(m.group(1)) + depth) + " " + m.group(2)
            lines.append(line)
        return plain("\n".join(lines)).strip() + "\n"

    index = texts[INDEX]
    front, contents = index.split("\n## Contents\n", 1)
    parts = [plain(front).strip() + "\n"]
    for block in re.split(r"^### ", contents, flags=re.M)[1:]:
        title, _, body = block.partition("\n")
        listed = [t for _, t, _, _ in links(body) if t in texts and t not in META | {INDEX}]
        listed = [t for t in listed if t not in emitted]
        if not listed:
            continue
        parts.append(f"# {title.strip()}\n")
        parts += [render(name, 1) for name in listed if name not in emitted]
    out.write_text("\n---\n\n".join(parts))
    print(f"wrote {out} ({len(emitted)} notes)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--changelog", metavar="BASE", help="git commit to compare HEAD with")
    parser.add_argument("--compile", metavar="OUT", type=Path, help="write the joined packet")
    args = parser.parse_args()
    if args.compile:
        compile_packet(args.compile)
        return
    problems = check_changelog(args.changelog) if args.changelog else check()
    for problem in problems:
        print(problem, file=sys.stderr)
    if problems:
        sys.exit(1)
    print("rules notes OK" if not args.changelog else "changelog OK")


if __name__ == "__main__":
    main()
