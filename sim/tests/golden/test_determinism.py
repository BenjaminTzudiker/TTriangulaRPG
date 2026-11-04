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
    ("v0.9", DUEL, 7, False, "98e51f458deedabb6223c48a4f6526cd9c7e6f144438c60109ad7ec84c385f9f"),
    (
        "review-candidate",
        SWARM,
        3,
        False,
        "29778fb23231ed7e97f09e78833e01fa93b6274e60bc7f0060ec99b8c8e652c6",
    ),
    ("v0.9", DEEP, 5, True, "673b53c6dae31ae73f09baecdc845c3805b0bf0d240bc2c8e4ffc5b7e0fb6b67"),
]


@pytest.mark.parametrize(("ruleset", "roster", "seed", "lockstep", "expected"), PINNED)
def test_pinned_log_hashes(
    ruleset: str, roster: list[tuple[str, str, str, str]], seed: int, lockstep: bool, expected: str
) -> None:
    got = battle(preset(ruleset), roster, seed, lockstep)
    assert got == expected, f"log hash changed: {got}"


GRID_PINNED = [
    (
        "one_v_three_corridor.toml",
        0,
        "8bf5943bf90f8273595be2424ef8f39aee7f64b00fc0070a84e83141b8a87512",
    ),
    (
        "reach_chokepoint.toml",
        3,
        "c9a825c6dd77852681d2c7ced9195d6af38ff8debd39800acc1c5ecac1fbf79d",
    ),
]


@pytest.mark.parametrize(("scenario", "trial", "expected"), GRID_PINNED)
def test_pinned_grid_log_hashes(scenario: str, trial: int, expected: str) -> None:
    """Two grid battles (tactical and scripted agents, OAs and off-turn windows)."""
    from pathlib import Path

    from stamina_engine.experiments.runner import run_trial
    from stamina_engine.experiments.scenario import load_scenario

    path = Path(__file__).resolve().parents[2] / "src/stamina_engine/data/scenarios" / scenario
    got = run_trial(load_scenario(path), trial, check=True).log_sha256()
    assert got == expected, f"log hash changed: {got}"
