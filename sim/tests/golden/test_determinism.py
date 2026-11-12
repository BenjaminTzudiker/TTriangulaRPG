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
    ("v0.9", DUEL, 7, False, "ac1f09dfa876c80cd5907cb62ff17f99c98abe356f54034e2e4bcea1a2c896e3"),
    (
        "review-candidate",
        SWARM,
        3,
        False,
        "90c8828f7fc08410b073e066f788c0bd61f9fcb283ee621451044f8d22986c78",
    ),
    ("v0.9", DEEP, 5, True, "aa4749bea977a475fa04adc12de64c33e8b8c47b4909c2a1b9758e6898c4b3a3"),
    (
        "v0.9.2",
        DUEL,
        7,
        False,
        "b3664cfa1ffacf3b14b86a2f780caa27b5aff49d870f385186ea6c823f1e8a6f",
    ),
]


@pytest.mark.parametrize(("ruleset", "roster", "seed", "lockstep", "expected"), PINNED)
def test_pinned_log_hashes(
    ruleset: str, roster: list[tuple[str, str, str, str]], seed: int, lockstep: bool, expected: str
) -> None:
    got = battle(preset(ruleset), roster, seed, lockstep)
    assert got == expected, f"log hash changed: {got}"


GRID_PINNED = [
    ("archer_wall.toml", 2, "036a8407b8a1645c0850413c065f246f2fa8cf47348f3db9374abc6129f0b9be"),
    (
        "one_v_three_corridor.toml",
        0,
        "52c4dc95c527391173f6e44b3194baa76e9f83abf2a66fdc0061f9b90e3c47f0",
    ),
    (
        "reach_chokepoint.toml",
        3,
        "71d2a158d6b67d198297c8bf3eb93fe1455112734c6b0b6fc6f9f31271b5ce7d",
    ),
    (
        "extraction_3v3.toml",  # objectives (O1)
        0,
        "0587c08695885c44105f7ada60ac93ee3f4387ca5fee89483f57ef9960e297cd",
    ),
    (
        "breakthrough_3v3.toml",  # objectives (O1)
        0,
        "2020116dd0bc88ff8835dd6de52c0d5c3325dec91f6de616e26528bcb1762f54",
    ),
    (
        "hold_hill_3v3.toml",  # objectives (O1)
        0,
        "e62b66a0df431866fd87513ad4c3f8906b6d5ea4c725de61be29561e77bb14ac",
    ),
    (
        "hold_the_door_1v3.toml",  # objectives (O1)
        0,
        "9c6542f27eba6d5d9a19838f3bde83c6647887708ac8dfd483b74fb29a67f2d7",
    ),
]


# 2026-11-11: the 3v3 hashes moved when shots got the Reacted and PointBlankProvoked events
# (measures only); without those two events each log hashes to its old pin.
@pytest.mark.parametrize(("scenario", "trial", "expected"), GRID_PINNED)
def test_pinned_grid_log_hashes(scenario: str, trial: int, expected: str) -> None:
    """Grid battles (tactical and scripted agents, OAs and off-turn windows), under each
    scenario's own ruleset: the baseline (now v0.10.0)."""
    from pathlib import Path

    from stamina_engine.experiments.runner import run_trial
    from stamina_engine.experiments.scenario import load_scenario

    path = Path(__file__).resolve().parents[2] / "src/stamina_engine/data/scenarios" / scenario
    got = run_trial(load_scenario(path), trial, check=True).log_sha256()
    assert got == expected, f"log hash changed: {got}"
