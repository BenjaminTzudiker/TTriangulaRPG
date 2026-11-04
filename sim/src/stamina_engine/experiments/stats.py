"""Intervals for reports: Wilson for rates, normal for means, paired for comparisons.
Reporting arithmetic, not game math, so floats are fine here."""

import math
from collections.abc import Sequence
from dataclasses import dataclass

Z95 = 1.959963984540054


@dataclass(frozen=True)
class Interval:
    estimate: float
    low: float
    high: float
    n: int

    def __str__(self) -> str:
        return f"{self.estimate:.3f} [{self.low:.3f}, {self.high:.3f}]"

    def pct(self) -> str:
        return f"{100 * self.estimate:.1f}% [{100 * self.low:.1f}, {100 * self.high:.1f}]"

    def contains(self, value: float) -> bool:
        return self.low <= value <= self.high


def wilson(successes: int, n: int, z: float = Z95) -> Interval:
    if n == 0:
        return Interval(math.nan, 0.0, 1.0, 0)
    p = successes / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return Interval(p, max(0.0, centre - half), min(1.0, centre + half), n)


def mean_interval(values: Sequence[float], z: float = Z95) -> Interval:
    n = len(values)
    if n == 0:
        return Interval(math.nan, math.nan, math.nan, 0)
    m = sum(values) / n
    if n == 1:
        return Interval(m, m, m, 1)
    sd = math.sqrt(sum((v - m) ** 2 for v in values) / (n - 1))
    half = z * sd / math.sqrt(n)
    return Interval(m, m - half, m + half, n)


def paired_difference(a: Sequence[float], b: Sequence[float], z: float = Z95) -> Interval:
    """b - a over trials that share seeds: the mean per-trial difference and its interval."""
    if len(a) != len(b):
        raise ValueError("paired samples must be the same length")
    return mean_interval([y - x for x, y in zip(a, b, strict=True)], z)


def median(values: Sequence[float]) -> float:
    s = sorted(values)
    n = len(s)
    if n == 0:
        return math.nan
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2
