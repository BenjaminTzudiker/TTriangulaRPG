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
    ("archer_wall.toml", 2, "effd6b3bdfdfe704032699fc79d10456cedbdc374491d5ff5737db427862d88e"),
    (
        "one_v_three_corridor.toml",
        0,
        "6b7688257c000346783539897eea5a96d324ae5664a1e12306f27aa0f013e564",
    ),
    (
        "reach_chokepoint.toml",
        3,
        "e0feb2246db2014f2a584e1d9af3ea5225cf2cfe64162011e358f81e3da627c8",
    ),
    (
        "extraction_3v3.toml",  # objectives (O1)
        0,
        "400cdd62bb72eeb386bb740f9c76082bf1640ab59927c560ef571b5925f27622",
    ),
    (
        "breakthrough_3v3.toml",  # objectives (O1)
        0,
        "2080f9ba4775f7a402953c35ff0bed0e3334eaca17545264b7cb1fb3a9145897",
    ),
    (
        "hold_hill_3v3.toml",  # objectives (O1)
        0,
        "6aae8d1470b9b8bec37dd938b8500c92a1984eb15f0a4fd7c675e5659313f24a",
    ),
    (
        "hold_the_door_1v3.toml",  # objectives (O1)
        0,
        "4bdead2a3b14d863401b9696a2fa778879162877d396e7bdb0b8bdb4b947aee1",
    ),
]


@pytest.mark.parametrize(("scenario", "trial", "expected"), GRID_PINNED)
def test_pinned_grid_log_hashes(scenario: str, trial: int, expected: str) -> None:
    """Grid battles (tactical and scripted agents, OAs, holds and dash phases), under each
    scenario's own ruleset: the baseline (now v0.12.1). The hashes moved with v0.12.1's
    changes (BattleStarted ruleset digest, quick-draw and step-4 reaction draws, Strength-gated
    armor Agility, action-tax armor shortfall, and heavy-armor +1 dash cost)."""
    from pathlib import Path

    from stamina_engine.experiments.runner import run_trial
    from stamina_engine.experiments.scenario import load_scenario

    path = Path(__file__).resolve().parents[2] / "src/stamina_engine/data/scenarios" / scenario
    got = run_trial(load_scenario(path), trial, check=True).log_sha256()
    assert got == expected, f"log hash changed: {got}"
