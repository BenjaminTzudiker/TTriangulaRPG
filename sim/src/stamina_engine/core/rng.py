"""Seeded random streams. Engine code never uses the global random module."""

import hashlib
import random
from typing import Protocol

from stamina_engine.core.dice import DiceSource


def derive_seed(master_seed: int, name: str) -> int:
    """A 64-bit seed for the named stream, stable across processes and platforms."""
    digest = hashlib.sha256(f"{master_seed}:{name}".encode()).digest()
    return int.from_bytes(digest[:8], "big")


class SeededDice:
    """A dice source backed by its own random.Random instance."""

    def __init__(self, seed: int) -> None:
        self._rng = random.Random(seed)

    def roll(self, size: int) -> int:
        return self._rng.randint(1, size)


class DiceProvider(Protocol):
    """Hands out the dice source for a purpose ("initiative", "attack:<id>", ...)."""

    def dice(self, name: str) -> DiceSource: ...


class Streams:
    """Independent named streams from one master seed (one per battle, sweep cell, ...).

    Asking for the same name again returns the same stream, continuing its sequence.
    """

    def __init__(self, master_seed: int) -> None:
        self.master_seed = master_seed
        self._streams: dict[str, SeededDice] = {}

    def dice(self, name: str) -> SeededDice:
        if name not in self._streams:
            self._streams[name] = SeededDice(derive_seed(self.master_seed, name))
        return self._streams[name]


class SharedStream:
    """Every purpose draws from one stream seeded directly with seed, in call order.

    This is lockstep mode: the review's simulator drew every die from one global stream,
    so feeding both the same seed makes them see identical faces.
    """

    def __init__(self, seed: int) -> None:
        self.seed = seed
        self._dice = SeededDice(seed)

    def dice(self, name: str) -> SeededDice:
        return self._dice
