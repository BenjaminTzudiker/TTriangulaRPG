"""Shared fixtures. The oracle (tests/oracle/sim.py) is loaded read-only, never edited."""

import importlib.util
import sys
import types
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

import pytest


class _AnyStrategy:
    """Stands in for any strategy expression (st.integers(...).map(...), st.composite...)
    when hypothesis isn't installed. Never drawn from: the tests using it are skipped."""

    def __getattr__(self, name: str) -> "_AnyStrategy":
        return self

    def __call__(self, *args: Any, **kwargs: Any) -> "_AnyStrategy":
        return self

    def __or__(self, other: object) -> "_AnyStrategy":
        return self


def _install_hypothesis_stub() -> None:
    """Without hypothesis (a chat that can't reach PyPI), the @given property tests are
    reported as skipped and every other test in their modules still runs."""

    def given(*args: Any, **kwargs: Any) -> Callable[[Callable[..., Any]], Callable[[], None]]:
        def wrap(test: Callable[..., Any]) -> Callable[[], None]:
            def skipped() -> None:
                pytest.skip("hypothesis is not installed")

            skipped.__name__, skipped.__qualname__ = test.__name__, test.__qualname__
            skipped.__doc__, skipped.__module__ = test.__doc__, test.__module__
            return skipped

        return wrap

    def settings(*args: Any, **kwargs: Any) -> Callable[[Any], Any]:
        return lambda test: test

    stub = types.ModuleType("hypothesis")
    strategies = types.ModuleType("hypothesis.strategies")
    strategies.__getattr__ = lambda name: _AnyStrategy()  # type: ignore[method-assign]
    stub.given, stub.settings, stub.strategies = given, settings, strategies  # type: ignore[attr-defined]
    sys.modules["hypothesis"], sys.modules["hypothesis.strategies"] = stub, strategies


try:
    import hypothesis  # noqa: F401
except ModuleNotFoundError:
    _install_hypothesis_stub()

ORACLE_PATH = Path(__file__).parent / "oracle" / "sim.py"
REPO_ROOT = Path(__file__).resolve().parents[2]
RULES_DIR = REPO_ROOT / "rules"  # the rules text, one note per rule (rules/README.md)

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
