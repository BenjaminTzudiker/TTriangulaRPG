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
    ("archer_wall.toml", 2, "677e547e76b94ff25500147db2573ca31a7037b0da80c8a4e32708461340282f"),
    (
        "one_v_three_corridor.toml",
        0,
        "3c3430b6e246418702232e1c555414187ec289bae004b2f7d8b409d0df5189ef",
    ),
    (
        "reach_chokepoint.toml",
        3,
        "f72c8277589662bcde08a9d540d8279e70dceb95edf5cf085edf3f612600cc78",
    ),
    (
        "extraction_3v3.toml",  # objectives (O1)
        0,
        "0b80a3db02b3e04fef511f7ddfa0644232bb6c76ae562d4d0c2bdb97864c0e07",
    ),
    (
        "breakthrough_3v3.toml",  # objectives (O1)
        0,
        "bbf696370297289cdbfffde260e3f6a1d5b77b390a960cc03cfa6f331db630c1",
    ),
    (
        "hold_hill_3v3.toml",  # objectives (O1)
        0,
        "ff837c011f45dcf67e5a607c46038e66a0a6d9ecfa1925dbc5cab62f658d05b2",
    ),
    (
        "hold_the_door_1v3.toml",  # objectives (O1)
        0,
        "b04abe9615b2d4afeeb39aacf60940e381abb6cd85c033be7138d5d363550adb",
    ),
]


@pytest.mark.parametrize(("scenario", "trial", "expected"), GRID_PINNED)
def test_pinned_grid_log_hashes(scenario: str, trial: int, expected: str) -> None:
    """Grid battles (tactical and scripted agents, OAs and off-turn windows), under each
    scenario's own ruleset: the baseline (now v0.10.1). The hashes moved with the baseline
    from v0.10.0 only because a log's first event names the RuleSet and its digest: the
    fights themselves are the same, event for event (all bundled scenarios, 25 trials
    each, 2026-11-13)."""
    from pathlib import Path

    from stamina_engine.experiments.runner import run_trial
    from stamina_engine.experiments.scenario import load_scenario

    path = Path(__file__).resolve().parents[2] / "src/stamina_engine/data/scenarios" / scenario
    got = run_trial(load_scenario(path), trial, check=True).log_sha256()
    assert got == expected, f"log hash changed: {got}"
