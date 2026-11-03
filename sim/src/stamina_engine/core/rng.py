"""Seeded random streams. Engine code never uses the global random module."""

import hashlib
import random


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


class Streams:
    """Independent named streams from one master seed (one per battle, sweep cell, ...)."""

    def __init__(self, master_seed: int) -> None:
        self.master_seed = master_seed

    def dice(self, name: str) -> SeededDice:
        return SeededDice(derive_seed(self.master_seed, name))
