"""Integer helpers for game math. The packet's "round" means round half up."""

import math
from fractions import Fraction


def round_half_up(x: Fraction | int) -> int:
    """Round half up, as the packet means by "round" (Packet: Stamina)."""
    return math.floor(Fraction(x) + Fraction(1, 2))


def round_half_even(x: Fraction | int) -> int:
    """Round half to even, as Python's round() does. Used only to reproduce the review."""
    return round(Fraction(x))


def tri(n: int) -> int:
    """Triangular number: 1 + 2 + ... + n (Packet: Quick Reference, Triangular Numbers)."""
    return n * (n + 1) // 2 if n > 0 else 0


def odd_count(value: int) -> int:
    """How many of 1, 3, 5 are at or below value (Packet: Attribute Bonus Table, odd column).

    A negative value counts 0, so penalized attributes never widen anything.
    """
    return 0 if value <= 0 else (value + 1) // 2


def even_count(value: int, step: int = 2) -> int:
    """How many multiples of step are at or below value (Attribute Bonus Table, even columns).

    step is 2 normally, 3 in medium armor and 4 in heavy armor.
    """
    return 0 if value < 0 else value // step
