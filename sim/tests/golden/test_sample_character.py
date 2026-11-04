"""Packet: Quick Reference, Sample Character; plus the review's stated build numbers."""

from fractions import Fraction

from stamina_engine.model.build import load_build
from stamina_engine.model.derive import derive
from stamina_engine.rules.ruleset import v0_9


def test_sample_character() -> None:
    p = derive(load_build("l1_sample"), v0_9())
    lo = p.main
    assert (p.hp_max, p.stamina_max, p.recovery, p.strain_max) == (8, 14, 4, 6)
    assert (lo.melee_defense, lo.ranged_defense, lo.dodge_defense) == (4, 3, 1)
    assert (lo.armor, lo.movement, lo.squares_per_purchase) == (2, 6, 2)
    assert lo.initiative_bonus == 1
    assert lo.oa_cap == 2
    w = lo.weapon
    assert w is not None
    assert (w.name, w.grip, w.base, str(w.damage)) == ("longsword", "one", 2, "1d8 + 3")
    assert [f for f in range(1, 9) if v0_9().crit.is_crit(f, 8, w.crit_widen)] == [7, 8]


def test_review_builds() -> None:
    """Review Appendix A, Assumptions paragraph."""
    rules = v0_9()

    def stats(name: str) -> tuple[int, int, int, int, int]:
        p = derive(load_build(name), rules)
        return p.hp_max, p.stamina_max, p.recovery, p.main.melee_defense, p.main.armor

    assert stats("l30_sample") == (9, 21, 7, 6, 2)
    assert stats("l30_strbrute")[0] == 11
    assert stats("l30_strbrute")[3:] == (4, 3)
    assert stats("l30_duelist")[0] == 6
    assert stats("l30_duelist")[3:] == (5, 0)
    assert stats("l99_sample")[:4] == (12, 38, 14, 6)
    duelist = derive(load_build("l30_duelist"), rules).main.weapon
    assert duelist is not None
    assert Fraction(duelist.damage.mean_x2, 2) == Fraction(25, 2)
    assert duelist.damage.chosen == ("AGI", "FIN")


def test_archer_and_casters() -> None:
    rules = v0_9()
    archer = derive(load_build("l1_archer"), rules)
    assert archer.loadout("bow").melee_defense == 1  # no melee weapon wielded
    assert archer.loadout("blade").melee_defense == 3  # quick-drawn shortsword
    assert archer.loadout("bow").ranged_defense == 1
    assert derive(load_build("l1_caster_dagger"), rules).main.melee_defense == 2
    assert derive(load_build("l1_caster_unarmed"), rules).main.melee_defense == 1
