"""Ground rules 4 and 6: every component cites real packet sections and ledger IDs, and no
code branches on a RuleSet's name."""

import re
from pathlib import Path

from stamina_engine.rules import components as _components  # noqa: F401
from stamina_engine.rules.registry import registered

REPO = Path(__file__).resolve().parents[3]
SRC = REPO / "sim" / "src" / "stamina_engine"
# The rules are one note per rule (rules/README.md). Every note starts with "# <its name>", so a
# packet citation can name a note or any heading inside one. README and CHANGELOG are not rules.
PACKET = "\n".join(
    p.read_text()
    for p in sorted((REPO / "rules").rglob("*.md"))
    if p.name not in ("README.md", "CHANGELOG.md")
)
LEDGER = (REPO / "design" / "Rules_Reconciliation_Ledger_v0.8-to-v0.9.md").read_text()
REVIEW = (REPO / "design" / "Review_Playtest_Packet_v0.9.md").read_text()

HEADINGS = {m.group(1).strip() for m in re.finditer(r"^#+\s+(.+)$", PACKET, re.M)}
LEDGER_IDS = set(re.findall(r"^### ([A-Z]{1,2}-\d+)", LEDGER, re.M))
REVIEW_IDS = set(re.findall(r"^### (F\d+)\.", REVIEW, re.M)) | set(
    re.findall(r"^## (Addendum(?: \d+)?)\b", REVIEW, re.M)
)


def check_cites(owner: str, cites: tuple[str, ...]) -> list[str]:
    problems = []
    if not any(c.startswith("Packet: ") for c in cites):
        problems.append(f"{owner}: no packet citation")
    for cite in cites:
        source, _, ref = cite.partition(": ") if ": " in cite else cite.partition(" ")
        if source == "Packet" and ref not in HEADINGS:
            problems.append(f"{owner}: no packet heading {ref!r}")
        elif source == "Ledger" and ref not in LEDGER_IDS:
            problems.append(f"{owner}: no ledger entry {ref!r}")
        elif source == "Review" and ref not in REVIEW_IDS:
            problems.append(f"{owner}: no review finding {ref!r}")
        elif source not in ("Packet", "Ledger", "Review"):
            problems.append(f"{owner}: unknown source in {cite!r}")
    return problems


def test_components_cite_real_sections() -> None:
    problems: list[str] = []
    for (kind, variant), cls in registered().items():
        problems += check_cites(f"{kind}/{variant}", cls.cites)
    assert not problems, problems


def test_no_branching_on_ruleset_name() -> None:
    pattern = re.compile(r"\.name\s*(==|!=|in\b)|match\s+\w+\.name")
    offenders = [
        f"{p.relative_to(SRC)}:{i}"
        for p in SRC.rglob("*.py")
        for i, line in enumerate(p.read_text().splitlines(), 1)
        if pattern.search(line) and "rules" in line.lower()
    ]
    assert not offenders, offenders


def test_procedure_modules_cite_real_sections() -> None:
    """Modules that implement rules (Pricing, derive, exchange...) declare module-level cites."""
    import importlib
    import pkgutil

    import stamina_engine

    problems: list[str] = []
    cited = 0
    for info in pkgutil.walk_packages(stamina_engine.__path__, "stamina_engine."):
        module = importlib.import_module(info.name)
        cites = getattr(module, "cites", None)
        if isinstance(cites, tuple):
            cited += 1
            problems += check_cites(info.name, cites)
    assert cited >= 3
    assert not problems, problems
