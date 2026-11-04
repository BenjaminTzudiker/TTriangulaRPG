"""ENGINE_PLAN Verification 6: a fixed set of seeded battles must produce the same event-log
hash on every commit, unless a rule change is declared.

If one of these fails after a deliberate change (a rule, a component parameter, an event
field), say so in the commit message and update the pinned hash: the new value is in the
assertion message.
"""

import pytest

from stamina_engine.agents.scripted import make_agent
from stamina_engine.core.rng import SharedStream, Streams
from stamina_engine.engine.battle import Battle, Entrant
from stamina_engine.model.build import load_build
from stamina_engine.model.derive import derive
from stamina_engine.rules.ruleset import RuleSet, preset


def battle(
    rules: RuleSet, roster: list[tuple[str, str, str, str]], seed: int, lockstep: bool
) -> str:
    dice = SharedStream(seed) if lockstep else Streams(seed)
    entrants = [
        Entrant(
            cid,
            team,
            derive(load_build(build), rules),
            make_agent(
                {
                    "commit": spec,
                    "estimator": "sampled" if lockstep else "exact",
                    "target": "lowest_stamina",
                },
                rules,
                dice.dice(f"agent:{cid}"),
            ),
        )
        for cid, team, build, spec in roster
    ]
    result = Battle(
        rules, entrants, dice, seed=seed, dice_mode="lockstep" if lockstep else "named", check=True
    ).run()
    return result.log_sha256()


DUEL = [("a", "red", "l1_sample", "chipkill"), ("b", "blue", "l1_duelist", "alpha")]
SWARM = [("d", "red", "l1_heavy", "fixed:2")] + [
    (f"x{i}", "blue", "l1_sample", "fixed:2") for i in range(3)
]
DEEP = [("a", "red", "l30_sample", "lookahead"), ("b", "blue", "l30_duelist", "reserve:5")]

PINNED = [
    ("v0.9", DUEL, 7, False, "6c39e11e897f757aa3c8c2b649596ed77cbfc3f11a11ba3d1f25a20ef2492dbe"),
    (
        "review-candidate",
        SWARM,
        3,
        False,
        "2a3695c363a5b725bf28a84cf6b284de62188ea9e400bef4dcab5aa861ceb796",
    ),
    ("v0.9", DEEP, 5, True, "809d35cd8bfca85ca9c16215955574712e334deba30d136f06d9b135d81c835f"),
]


@pytest.mark.parametrize(("ruleset", "roster", "seed", "lockstep", "expected"), PINNED)
def test_pinned_log_hashes(
    ruleset: str, roster: list[tuple[str, str, str, str]], seed: int, lockstep: bool, expected: str
) -> None:
    got = battle(preset(ruleset), roster, seed, lockstep)
    assert got == expected, f"log hash changed: {got}"
