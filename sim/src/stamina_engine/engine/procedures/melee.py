"""A melee attack, as the packet's eight steps (Packet: Attack Procedure).

An opportunity attack (M2) is this procedure with off-turn pricing and the OA cap.
"""

from stamina_engine.agents.decisions import BlocksRequest, Commitment
from stamina_engine.engine.battle import Battle
from stamina_engine.engine.events import (
    AttackDeclared,
    AttackResolved,
    AttackRolled,
    BlocksDeclared,
)
from stamina_engine.model.derive import WeaponProfile
from stamina_engine.model.state import CombatantState
from stamina_engine.rules.block_solver import block_options
from stamina_engine.rules.exchange import AttackRoll, Blocks, Outcome, resolve, roll_attack
from stamina_engine.rules.pricing import Quote

cites = (
    "Packet: Attack Procedure",
    "Packet: Melee Attacks",
    "Packet: Actions and the On-Turn Surcharge",
    "Packet: Blocking",
    "Packet: Armor",
    "Packet: Critical Hits",
    "Ledger CB-1",
    "Ledger CB-2",
    "Ledger CB-3",
    "Ledger CB-4",
    "Ledger CB-6",
    "Ledger CB-7",
)


def melee_attack(b: Battle, attacker: CombatantState, target: CombatantState) -> None:
    """Step 1, declaring the target, came with the TurnCommand."""
    weapon = attacker.gear.weapon
    assert weapon is not None
    with b.context.frame(f"attack {attacker.id}->{target.id}"):
        steps = declare_steps(b, attacker, target, weapon)
        if steps is None:
            return
        attack = roll(b, attacker, weapon, steps)
        reactions(b, attacker, target)
        blocks = declare_blocks(b, attacker, target, attack)
        outcome = armor_and_crits(b, attacker, target, attack, blocks)
        lose_hp(b, target, outcome)


def declare_steps(
    b: Battle, attacker: CombatantState, target: CombatantState, weapon: WeaponProfile
) -> int | None:
    """Step 2: declare every step before rolling, and pay base + the on-turn surcharge each."""
    quotes: list[Quote] = []
    while True:
        quote = b.pricing.melee_attack(
            weapon.base, len(quotes) + 1, attacker.trackers, light=weapon.light
        )
        if quote.total > attacker.stamina:
            break
        quotes.append(quote)
    request = Commitment(
        attacker.id,
        b.observe(attacker.id),
        b.context.path(),
        target.id,
        tuple(quotes),
    )
    steps = b.broker.commitment(request)
    if steps == 0:
        return None  # declaration withdrawn
    b.ops.emit(AttackDeclared(attacker.id, target.id, steps))
    b.ops.spend(attacker, quotes[steps - 1], "attack")
    b.ops.use_weapon(attacker)
    return steps


def roll(b: Battle, attacker: CombatantState, weapon: WeaponProfile, steps: int) -> AttackRoll:
    """Step 3: roll and total; note the critical dice."""
    attack = roll_attack(weapon, steps, b.rules.crit, b.dice.dice(f"attack:{attacker.id}"))
    faces = tuple(f for s in attack.steps for f in s.faces)
    b.ops.emit(AttackRolled(attacker.id, faces, attack.total, attack.crit_dice))
    return attack


def reactions(b: Battle, attacker: CombatantState, target: CombatantState) -> None:
    """Step 4: reactions such as diving for cover. None apply to melee in M1."""


def prior_perfect(b: Battle, target: CombatantState, attacker: CombatantState) -> int:
    """Perfect blocks already counted toward this attack's escalation, by blocks.reset:
    0 in v0.9, where every attack starts over."""
    mode = b.rules.blocks.reset
    round_ = b.state.round
    if mode == "per_attacker_round":
        return target.perfect_blocks.get((attacker.id, round_), 0)
    if mode == "per_round":
        return sum(n for (_, r), n in target.perfect_blocks.items() if r == round_)
    return 0


def declare_blocks(
    b: Battle,
    attacker: CombatantState,
    target: CombatantState,
    attack: AttackRoll,
    defense: int | None = None,
    ranged: bool = False,
    cover: int = 0,
) -> Blocks:
    """Step 5: the defender sees the total and the critical dice, then declares blocks.
    An incapacitated defender can't block (Assumptions register). defense defaults to Melee
    Defense; a ranged attack passes Ranged (or Melee) Defense plus its cover bonus."""
    if not target.active:
        return Blocks()
    gear = target.gear
    defense = gear.melee_defense if defense is None else defense
    prior = prior_perfect(b, target, attacker)
    options = block_options(
        attack.total,
        attack.crit_dice,
        defense,
        gear.armor,
        target.stamina,
        b.rules,
        prior,
        ranged,
    )
    request = BlocksRequest(
        target.id,
        b.observe(target.id),
        b.context.path(),
        attacker.id,
        attack.total,
        attack.crit_dice,
        defense,
        gear.armor,
        target.stamina,
        prior,
        options.affordable,
        options.nondominated,
        ranged,
        cover,
    )
    blocks = b.broker.blocks(request)
    b.ops.emit(BlocksDeclared(target.id, blocks.perfect, blocks.grazing, prior))
    quote = b.pricing.blocks(blocks.perfect, blocks.grazing, prior_perfect=prior, ranged=ranged)
    if quote.total:
        b.ops.spend(target, quote, "block")
    b.ops.count_perfect_blocks(target, attacker.id, b.state.round, blocks.perfect)
    return blocks


def armor_and_crits(
    b: Battle,
    attacker: CombatantState,
    target: CombatantState,
    attack: AttackRoll,
    blocks: Blocks,
    defense: int | None = None,
) -> Outcome:
    """Steps 6 and 7: armor (less 1 per critical die), then the crit effect."""
    gear = target.gear
    defense = gear.melee_defense if defense is None else defense
    outcome = resolve(attack.total, attack.crit_dice, defense, gear.armor, blocks, b.rules)
    b.ops.emit(
        AttackResolved(
            attacker.id,
            target.id,
            outcome.damage,
            outcome.crit_dice,
            outcome.through_blocks,
            outcome.leaked,
            outcome.armor_applied,
            outcome.injury,
        )
    )
    return outcome


def lose_hp(b: Battle, target: CombatantState, outcome: Outcome) -> None:
    """Step 8: the defender loses that much HP; the fight may end here."""
    b.ops.injure(target, outcome.injury)
    b.check_end()
