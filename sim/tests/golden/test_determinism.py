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
]


@pytest.mark.parametrize(("ruleset", "roster", "seed", "lockstep", "expected"), PINNED)
def test_pinned_log_hashes(
    ruleset: str, roster: list[tuple[str, str, str, str]], seed: int, lockstep: bool, expected: str
) -> None:
    got = battle(preset(ruleset), roster, seed, lockstep)
    assert got == expected, f"log hash changed: {got}"


GRID_PINNED = [
    ("archer_wall.toml", 2, "73657905ee2fa8220f25634927c37f103c5b42efe8bed07bf7b5ee32e4c23e86"),
    (
        "one_v_three_corridor.toml",
        0,
        "3b934a47f499afb3a8f1980fd786b5c8541860ce2b4b0a981db21e2c0a84624f",
    ),
    (
        "reach_chokepoint.toml",
        3,
        "46424a70978ac29b27a2becdeeb7adb71bce1fe7c9b469d9fe4dae0569de9b7f",
    ),
    (
        "extraction_3v3.toml",  # objectives (O1)
        0,
        "bfab25a6340ad8123cfa3d41ad9d8d4f6a8cdcc2ac1d514209700d27099e969a",
    ),
    (
        "breakthrough_3v3.toml",  # objectives (O1)
        0,
        "49660da934ca586e219b399d3ca4a4a7e7d2faa56669fe1cba43687987109b9b",
    ),
    (
        "hold_hill_3v3.toml",  # objectives (O1)
        0,
        "93d98ca701874a7a8ace46772f347286640c3d98f2cf10461dd85e0c1f1c36e4",
    ),
    (
        "hold_the_door_1v3.toml",  # objectives (O1)
        0,
        "71d6adca8d5604c6e0745aa085a7428110afd63b554ee7075eb820ca26cdb543",
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
