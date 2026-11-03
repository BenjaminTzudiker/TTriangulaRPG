"""Dice pools and dice sources: seeded, or scripted for tests."""

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Protocol

from stamina_engine.core.errors import ConfigError, ScriptExhausted


@dataclass(frozen=True)
class Dice:
    """count dice of the given size, such as 2d6."""

    count: int
    size: int

    def __post_init__(self) -> None:
        if self.count < 0 or self.size < 1:
            raise ConfigError(f"bad dice {self.count}d{self.size}")

    def __str__(self) -> str:
        return f"{self.count}d{self.size}"

    @property
    def mean_x2(self) -> int:
        """Twice the mean, kept integer: count * (size + 1)."""
        return self.count * (self.size + 1)


class DiceSource(Protocol):
    """Anything that can roll one die."""

    def roll(self, size: int) -> int: ...


def roll(dice: Dice, source: DiceSource) -> tuple[int, ...]:
    """Roll every die in the pool, in order."""
    return tuple(source.roll(dice.size) for _ in range(dice.count))


class ScriptedDice:
    """Returns the given faces in order. Raises if a face doesn't fit the die or runs out."""

    def __init__(self, faces: Iterable[int]) -> None:
        self._faces = list(faces)
        self._next = 0

    def roll(self, size: int) -> int:
        if self._next >= len(self._faces):
            raise ScriptExhausted(f"scripted dice used up after {len(self._faces)} faces")
        face = self._faces[self._next]
        if not 1 <= face <= size:
            raise ConfigError(f"scripted face {face} doesn't fit a d{size}")
        self._next += 1
        return face

    @property
    def remaining(self) -> int:
        return len(self._faces) - self._next
