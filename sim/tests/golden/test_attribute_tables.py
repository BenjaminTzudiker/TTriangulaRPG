"""Packet: Quick Reference, Attribute Bonus Table and Triangular Numbers."""

from stamina_engine.core.mathx import even_count, odd_count, tri

# value: (odd, even normal, even medium, even heavy)
ATTRIBUTE_BONUS_TABLE = {
    0: (0, 0, 0, 0),
    1: (1, 0, 0, 0),
    2: (1, 1, 0, 0),
    3: (2, 1, 1, 0),
    4: (2, 2, 1, 1),
    5: (3, 2, 1, 1),
    6: (3, 3, 2, 1),
}


def test_attribute_bonus_table() -> None:
    for value, (odd, normal, medium, heavy) in ATTRIBUTE_BONUS_TABLE.items():
        assert odd_count(value) == odd
        assert even_count(value, 2) == normal
        assert even_count(value, 3) == medium
        assert even_count(value, 4) == heavy


def test_triangular_numbers() -> None:
    assert [tri(n) for n in range(1, 11)] == [1, 3, 6, 10, 15, 21, 28, 36, 45, 55]
