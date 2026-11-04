"""Shared fixtures. The oracle (tests/oracle/sim.py) is loaded read-only, never edited."""

import importlib.util
import types
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

import pytest

ORACLE_PATH = Path(__file__).parent / "oracle" / "sim.py"
REPO_ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = REPO_ROOT / "rules" / "Playtest_Packet_v0.9.md"

_oracle_module: types.ModuleType | None = None


def _load_oracle() -> types.ModuleType:
    global _oracle_module
    if _oracle_module is None:
        spec = importlib.util.spec_from_file_location("oracle_sim", ORACLE_PATH)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _oracle_module = module
    return _oracle_module


@pytest.fixture
def oracle() -> Iterator[Any]:
    """The review's simulator with its variant knobs set to v0.9 and restored afterwards.

    Tests that need other knobs set them on the returned module; this fixture restores them.
    """
    sim = _load_oracle()
    saved = (sim.STEP_SLOPE, sim.BLOCK_SLOPE, sim.CRIT_MODE)
    sim.STEP_SLOPE, sim.BLOCK_SLOPE, sim.CRIT_MODE = 1, 1.0, "double"
    try:
        yield sim
    finally:
        sim.STEP_SLOPE, sim.BLOCK_SLOPE, sim.CRIT_MODE = saved


@pytest.fixture
def scripted_randint(oracle: Any, monkeypatch: pytest.MonkeyPatch) -> Callable[[list[int]], None]:
    """Make the oracle roll the given faces, in order, instead of using the global random."""

    def script(faces: list[int]) -> None:
        it = iter(faces)

        def randint(lo: int, hi: int) -> int:
            face = next(it)
            assert lo <= face <= hi, (face, lo, hi)
            return face

        monkeypatch.setattr(oracle, "random", types.SimpleNamespace(randint=randint))

    return script
