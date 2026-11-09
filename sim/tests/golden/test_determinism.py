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
    ("archer_wall.toml", 2, "84ff86cacaf6871b8c35ff907d5a7b3ce25e866f5ad372dac5930109c485617e"),
    (
        "one_v_three_corridor.toml",
        0,
        "e49db71fd42201bea7fa85b154b13bd90d075d5d17bc2f0c2099552bcfb2db05",
    ),
    (
        "reach_chokepoint.toml",
        3,
        "a81b71accf352bdf75a0cc9d20d83bb6a1a4d45b7ee3dece97de3f60823079ad",
    ),
    (
        "extraction_3v3.toml",  # objectives (O1)
        0,
        "1e300c59be0dc27512ee2d9518779b761183246f146eee47bfa3647e6f13b2db",
    ),
    (
        "breakthrough_3v3.toml",  # objectives (O1)
        0,
        "3be2654b72c628da50d8f45ffa3e9b7c44ad65f8b20902e8e5764c1777fad19c",
    ),
    (
        "hold_hill_3v3.toml",  # objectives (O1)
        0,
        "e85479c696d3f9e85b377726d2fc9e7e157bd2d7cd834c377067bd31a289e3b7",
    ),
    (
        "hold_the_door_1v3.toml",  # objectives (O1)
        0,
        "01a5c252da21353d9605d45533bf036cd2c70c8a708b4417eb7d2036f24e27e4",
    ),
]


@pytest.mark.parametrize(("scenario", "trial", "expected"), GRID_PINNED)
def test_pinned_grid_log_hashes(scenario: str, trial: int, expected: str) -> None:
    """Grid battles (tactical and scripted agents, OAs and off-turn windows), under each
    scenario's own ruleset: the baseline (v0.9.2) since it moved there."""
    from pathlib import Path

    from stamina_engine.experiments.runner import run_trial
    from stamina_engine.experiments.scenario import load_scenario

    path = Path(__file__).resolve().parents[2] / "src/stamina_engine/data/scenarios" / scenario
    got = run_trial(load_scenario(path), trial, check=True).log_sha256()
    assert got == expected, f"log hash changed: {got}"
