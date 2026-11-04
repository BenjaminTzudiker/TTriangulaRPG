"""The shared block agent: the exact solver, memoized (ENGINE_PLAN, agent family 1)."""

from fractions import Fraction
from functools import lru_cache

from stamina_engine.agents.decisions import BlocksRequest
from stamina_engine.rules.block_solver import DEFAULT_W, BlockChoice, best_block
from stamina_engine.rules.exchange import Blocks
from stamina_engine.rules.ruleset import RuleSet

cites = ("Packet: Blocking", "Ledger CB-3", "Ledger CB-4", "Ledger GM-1")


@lru_cache(maxsize=1 << 18)
def cached_best_block(
    damage: int,
    crit_dice: int,
    defense: int,
    armor: int,
    stamina: int,
    hp: int,
    rules: RuleSet,
    w: Fraction = DEFAULT_W,
    prior_perfect: int = 0,
) -> BlockChoice:
    return best_block(damage, crit_dice, defense, armor, stamina, hp, rules, w, prior_perfect)


def solver_blocks(request: BlocksRequest, rules: RuleSet, w: Fraction = DEFAULT_W) -> Blocks:
    """Minimize w x injury + stamina, never taking an avoidable incapacitation."""
    return cached_best_block(
        request.damage,
        request.crit_dice,
        request.defense,
        request.armor,
        request.stamina,
        request.observation.me.hp,
        rules,
        w,
        request.prior_perfect,
    ).blocks
