"""The load report (`se load`): how much a fight asks of the people playing it (Review F11).

For each kind of request: how often it comes up per creature-round, how many options it
offers, how often it is non-trivial (more than one option worth considering: for blocks,
more than one non-dominated pair), how often the answer did something, and, for a person's
session, the seconds it took. Then the dice rolled per attack.
"""

from collections import defaultdict
from collections.abc import Sequence
from statistics import mean, median

from stamina_engine.experiments.metrics import Row

cites = ("Packet: Starting Combat and Turn Structure", "Review F11")

KINDS = (
    "turn_command",
    "commitment",
    "blocks",
    "off_turn_move",
    "avoid",
    "take_oa",
    "aim",
    "dive",
    "ability",
)


def _trivial(d: Row) -> bool:
    if d["kind"] == "blocks" and d.get("nondominated") is not None:
        return int(d["nondominated"]) <= 1
    return int(d["option_count"]) <= 1


def _fmt(values: Sequence[float], digits: int = 1) -> str:
    return f"{mean(values):.{digits}f}" if values else "-"


def load_report(
    decisions: Sequence[Row],
    attacks: Sequence[Row],
    creature_rounds: int,
    title: str,
    who: set[str] | None = None,
) -> str:
    """creature_rounds: rounds summed over the creatures whose decisions are counted (the
    denominator for "per round"). who: count only these creatures' decisions."""
    rows = [d for d in decisions if who is None or d["who"] in who]
    by: dict[str, list[Row]] = defaultdict(list)
    for d in rows:
        by[d["kind"]].append(d)
    timed = any(d.get("seconds") is not None for d in rows)
    head = ["Request", "Per round", "Options (mean)", "Options (max)", "Non-trivial", "Acted"]
    if timed:
        head += ["Seconds (mean)", "Seconds (median)"]
    lines = [f"# {title}", "", "| " + " | ".join(head) + " |", "|---" * len(head) + "|"]
    total_seconds: list[float] = []
    for kind in KINDS + tuple(sorted(set(by) - set(KINDS))):
        ds = by.get(kind)
        if not ds:
            continue
        options = [float(d["option_count"]) for d in ds]
        cells = [
            kind,
            f"{len(ds) / max(1, creature_rounds):.2f}",
            _fmt(options),
            f"{max(options):.0f}",
            f"{100 * sum(not _trivial(d) for d in ds) / len(ds):.0f}%",
            f"{100 * sum(bool(d['acted']) for d in ds) / len(ds):.0f}%",
        ]
        if timed:
            secs = [float(d["seconds"]) for d in ds if d.get("seconds") is not None]
            total_seconds += secs
            cells += [_fmt(secs), f"{median(secs):.1f}" if secs else "-"]
        lines.append("| " + " | ".join(cells) + " |")
    n = len(rows)
    nontrivial = sum(not _trivial(d) for d in rows)
    lines += [
        "",
        f"- Decisions: {n}, {n / max(1, creature_rounds):.2f} per creature-round; "
        f"non-trivial: {nontrivial} ({nontrivial / max(1, creature_rounds):.2f} per round).",
    ]
    if timed and total_seconds:
        lines.append(
            f"- Seconds deciding: {sum(total_seconds):.0f} in all, "
            f"{sum(total_seconds) / max(1, creature_rounds):.1f} per creature-round."
        )
    mine = [a for a in attacks if who is None or a["attacker"] in who]
    for kind in ("melee", "opportunity", "shot"):
        dice = [float(a["dice"]) for a in mine if a["kind"] == kind and "dice" in a]
        if dice:
            lines.append(
                f"- Dice per {kind} attack: {_fmt(dice)} (max {max(dice):.0f}, "
                f"{len(dice)} attacks)."
            )
    return "\n".join(lines) + "\n"
