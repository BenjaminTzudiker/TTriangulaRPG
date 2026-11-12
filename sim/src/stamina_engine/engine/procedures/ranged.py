"""Ranged attacks and drawing weapons (Packet: Ranged Attacks, Procedure, Aim, Range Bands,
Cover, Drawing Weapons; Opportunity Attacks: shooting in melee).

A shot, following the packet's steps (readings in the Assumptions register):
1. Declare the target: an enemy the weapon can reach (v0.9: within long range; linear
   bands: any, if the wielder's band width is above 0) that isn't in total cover. Note who
   threatens the shooter now, for the point-blank OAs.
2. Pay the shot and buy aim steps (Pricing: a flat shot cost, or from 0.10.0 an action).
3. Roll: the weapon's damage, any free aim dice and each aim step. v0.9: too few aims for
   the range band and it misses.
4. The target may react with one off-turn move (dive for cover, close in, back away), of
   at most ranged.reaction_purchases purchases if capped; OAs that move provokes resolve
   first. Total cover at the end counts as three-quarters.
5. The range penalty (linear bands), from the target's square after its reaction or at
   declaration (ranged.range_measured). The target blocks with Ranged Defense (plus
   ranged.reaction_bonus if it moved) or, if the shooter is within its reach, Melee
   Defense; cover adds to either. Reach is judged after the reaction or at declaration
   (ranged.defense_timing; ranged.swap_single_purchase).
6. Armor less Piercing and critical dice, the aim limit, the crit effect, injury.
7. If the shooter is within any enemy's reach, every enemy threatening it may make an
   opportunity attack, lowest initiative first (from 0.10.0, only those that also
   threatened it at step 1); these can't be avoided by paying (as written).
"""

from collections.abc import Callable
from dataclasses import replace

from stamina_engine.agents.decisions import AimRequest, DiveRequest, DrawOption, Move
from stamina_engine.engine.battle import Battle
from stamina_engine.engine.events import (
    AttackRolled,
    Dived,
    OpportunityProvoked,
    RangePenalized,
    ShotDeclared,
    ShotMissed,
)
from stamina_engine.engine.procedures.melee import (
    armor_and_crits,
    declare_blocks,
    faced_armor,
    lose_hp,
)
from stamina_engine.engine.procedures.movement import avoid, move, move_options
from stamina_engine.engine.procedures.opportunity import OAContext, opportunity_attack, reach_cap
from stamina_engine.grid.battlefield import Cell
from stamina_engine.grid.geometry import distance
from stamina_engine.grid.los import Cover, cover
from stamina_engine.grid.threat import body, threatened_by
from stamina_engine.model.state import CombatantState
from stamina_engine.rules.exchange import AttackRoll, roll_shot
from stamina_engine.rules.pricing import Quote

cites = (
    "Packet: Ranged Attacks",
    "Packet: Procedure",
    "Packet: Aim",
    "Packet: Range Bands",
    "Packet: Cover",
    "Packet: Ranged Defense",
    "Packet: Weapon Properties",
    "Packet: Triggers",
    "Packet: Drawing Weapons",
    "Ledger RG-1",
    "Ledger RG-2",
    "Ledger RG-3",
    "Ledger RG-4",
    "Ledger MV-3",
)


def _others(b: Battle, *skip: CombatantState) -> list[Cell]:
    ids = {c.id for c in skip}
    return [c.pos for c in b.state.combatants if c.pos is not None and c.id not in ids]


def cover_from(
    b: Battle, shooter: CombatantState, target: CombatantState, at: Cell | None = None
) -> Cover:
    assert b.field is not None and shooter.pos is not None
    spot = at if at is not None else target.pos
    assert spot is not None
    return cover(b.field, b.rules.grid, shooter.pos, spot, _others(b, shooter, target))


def shot_targets(b: Battle, c: CombatantState) -> tuple[str, ...]:
    """Enemies its ranged weapon can target now, if the shot itself is affordable."""
    weapon = c.gear.weapon
    if b.field is None or c.pos is None or weapon is None or not weapon.ranged:
        return ()
    if b.pricing.ranged_attack(weapon.base, 0, c.trackers).total > c.stamina:
        return ()
    out = []
    for o in b.state.enemies_of(c):
        if not o.active or o.pos is None:
            continue
        band = b.rules.ranged.band(
            distance(c.pos, o.pos, b.rules.grid), weapon.ranges, weapon.band_width
        )
        if band != "beyond" and cover_from(b, c, o) < Cover.TOTAL:
            out.append(o.id)
    return tuple(out)


def point_blank(
    b: Battle, target: CombatantState, shooter: CombatantState, at: Cell | None = None
) -> bool:
    """Is the shooter within the target's melee reach (with the target at `at`, if given)?"""
    spot = at if at is not None else target.pos
    if b.field is None or spot is None or shooter.pos is None:
        return False
    me = body(target.id, target.team, spot, target.gear, target.active)
    return shooter.pos in threatened_by(b.field, b.rules.grid, me)


def blocks_in_melee(
    b: Battle,
    shooter: CombatantState,
    target: CombatantState,
    declared: bool,
    purchases: int,
    at: Cell | None = None,
) -> bool:
    """Does the target block with Melee Defense (Packet: Ranged Defense, point-blank
    shots)? declared: whether the shooter was within its reach when the shot was declared;
    purchases: the off-turn purchases its reaction took. Judged after the reaction (with the
    target at `at`, if given) unless ranged.defense_timing says at declaration; under
    ranged.swap_single_purchase, a swap that took more than one purchase doesn't count."""
    r = b.rules.ranged
    if not r.defense_after_reaction():
        return declared
    now = point_blank(b, target, shooter, at)
    if now != declared and purchases > 1 and r.swap_needs_single_purchase():
        return declared
    return now


def shot_defense(
    b: Battle,
    shooter: CombatantState,
    target: CombatantState,
    level: int,
    moved: bool,
    melee: bool,
) -> int:
    """The defense a shot faces, cover included (Packet: Defenses, Cover): Melee Defense if
    melee (see blocks_in_melee), else Ranged Defense, plus the reaction bonus if the target
    moved in reaction to this shot (Ranged Defense only, as the packet lists it; Assumptions
    register)."""
    r = b.rules.ranged
    gear = target.gear
    if melee:
        base = gear.melee_defense
    else:
        base = gear.ranged_defense + (r.reaction_defense() if moved else 0)
    return base + r.cover_bonus(level)


def _purchases(target: CombatantState, squares: int) -> int:
    """Off-turn purchases a reaction of this many squares takes."""
    per = max(1, target.gear.squares_per_purchase)
    return -(-squares // per)


def shoot(b: Battle, shooter: CombatantState, target: CombatantState) -> None:
    weapon = shooter.gear.weapon
    assert (
        weapon is not None and weapon.ranged and shooter.pos is not None and target.pos is not None
    )
    r = b.rules.ranged
    grid = b.rules.grid
    declared: tuple[str, ...] | None = None
    with b.context.frame(f"shot {shooter.id}->{target.id}"):
        at_declaration = distance(shooter.pos, target.pos, grid)
        band = r.band(at_declaration, weapon.ranges, weapon.band_width)
        level = cover_from(b, shooter, target)
        required = r.required_aims(band)
        if b.rules.opportunity.point_blank_needs_declared():
            declared = b.arena.threatening(b.state, shooter, shooter.pos)
        melee_at_declaration = point_blank(b, target, shooter)
        quotes: list[Quote] = []
        while True:
            q = b.pricing.ranged_attack(weapon.base, len(quotes), shooter.trackers)
            if q.total > shooter.stamina:
                break
            quotes.append(q)
        request = AimRequest(
            shooter.id,
            b.observe(shooter.id),
            b.context.path(),
            target.id,
            band,
            int(level),
            required,
            tuple(quotes),
            r.range_penalty(at_declaration, weapon.band_width),
        )
        aims = b.broker.aim(request)
        b.ops.emit(ShotDeclared(shooter.id, target.id, aims, band, int(level)))
        b.ops.spend(shooter, quotes[aims], "shot")
        b.ops.use_weapon(shooter, bow=True)
        if aims < required:
            b.ops.emit(ShotMissed(shooter.id, target.id, f"{band} range needs {required} aims"))
        else:
            fin = shooter.gear.attributes.FIN
            rolled = roll_shot(
                weapon, aims, fin, band, b.rules, b.dice.dice(f"attack:{shooter.id}")
            )
            origin = shooter.pos

            def at(cell: Cell | None) -> AttackRoll:
                """The roll with the range penalty for the target at cell (None: where it
                is now), or at declaration if range isn't measured after the reaction."""
                spot = cell if cell is not None else target.pos
                assert spot is not None
                d = distance(origin, spot, grid) if r.measures_after_reaction() else at_declaration
                return replace(
                    rolled, penalty=rolled.penalty + r.range_penalty(d, weapon.band_width)
                )

            attack = at(None)
            faces = tuple(f for s in attack.steps for f in s.faces)
            b.ops.emit(AttackRolled(shooter.id, faces, attack.total, attack.crit_dice))
            level, squares = dive(b, shooter, target, attack, level, at, melee_at_declaration)
            moved = squares > 0
            if b.outcome is None:
                attack = at(None)
                if r.uses_band_width():
                    assert target.pos is not None
                    d = distance(origin, target.pos, grid)
                    b.ops.emit(
                        RangePenalized(
                            shooter.id,
                            target.id,
                            d,
                            r.band(d, weapon.ranges, weapon.band_width),
                            attack.penalty,
                        )
                    )
                melee = blocks_in_melee(
                    b, shooter, target, melee_at_declaration, _purchases(target, squares)
                )
                defense = shot_defense(b, shooter, target, int(level), moved, melee)
                bonus = r.cover_bonus(int(level))
                blocks = declare_blocks(
                    b,
                    shooter,
                    target,
                    attack,
                    defense,
                    True,
                    bonus,
                    faced_armor(target, weapon),
                    attack.limit,
                )
                outcome = armor_and_crits(
                    b, shooter, target, attack, blocks, defense, pierce=weapon.piercing
                )
                lose_hp(b, target, outcome)
    if b.outcome is None and shooter.active:
        point_blank_oas(b, shooter, declared)


def dive(
    b: Battle,
    shooter: CombatantState,
    target: CombatantState,
    attack: AttackRoll,
    level: Cover,
    at: Callable[[Cell | None], AttackRoll],
    declared_melee: bool = False,
) -> tuple[Cover, int]:
    """Step 4: the target may react with off-turn movement (at most
    ranged.reaction_purchases purchases, if capped). Returns the cover the shot then faces
    and how many squares the target moved. The request's per-square data assumes the
    fewest purchases that reach each square."""
    if not target.active or b.field is None:
        return level, 0
    r = b.rules.ranged
    cap = r.reaction_purchase_cap()
    most = None if cap is None else cap * max(1, target.gear.squares_per_purchase)
    moves = move_options(b, target, on_turn=False, max_squares=most)
    if moves is None:
        return level, 0
    after = {d: r.dive_cover(int(cover_from(b, shooter, target, d))) for d in moves.destinations}
    weapon = shooter.gear.weapon
    assert weapon is not None
    rich = r.measures_after_reaction() or r.reaction_defense() > 0

    def melee(d: Cell | None, squares: int) -> bool:
        return blocks_in_melee(b, shooter, target, declared_melee, _purchases(target, squares), d)

    request = DiveRequest(
        target.id,
        b.observe(target.id),
        b.context.path(),
        shooter.id,
        attack.total,
        attack.crit_dice,
        int(level),
        moves,
        after,
        shot_defense(b, shooter, target, int(level), False, melee(None, 0)) if rich else None,
        {d: at(d).total for d in moves.destinations} if rich else {},
        (
            {
                d: shot_defense(b, shooter, target, after[d], True, melee(d, n))
                for d, n in moves.destinations.items()
            }
            if rich
            else {}
        ),
        faced_armor(target, weapon) if rich else None,
        attack.limit,
    )
    answer = b.broker.dive(request)
    if not isinstance(answer, Move) or not answer.path:
        return level, 0
    with b.context.frame(f"dive {target.id}"):
        move(b, target, answer.path, on_turn=False)
    new = Cover(r.dive_cover(int(cover_from(b, shooter, target))))
    b.ops.emit(Dived(target.id, int(new)))
    return new, len(answer.path)


def point_blank_oas(
    b: Battle, shooter: CombatantState, declared: tuple[str, ...] | None = None
) -> None:
    """Shooting within an enemy's reach provokes from every enemy threatening the shooter,
    once the shot has resolved; with declared given (0.10.0), only from those that also
    threatened it when the shot was declared."""
    if not b.rules.opportunity.attacks_allowed() or shooter.pos is None:
        return
    threatening = b.arena.threatening(b.state, shooter, shooter.pos)
    if declared is not None:
        threatening = tuple(e for e in threatening if e in declared)
    if not threatening:
        return
    if b.rules.off_turn.order_mode() == "ascending_initiative":
        threatening = tuple(reversed(threatening))
    square = shooter.pos
    with b.context.frame(f"point-blank {shooter.id}"):
        b.ops.emit(OpportunityProvoked(shooter.id, square, threatening))
        caps = tuple(reach_cap(b, b.state.get(e), square) for e in threatening)
        paid: tuple[str, ...] = ()
        if b.rules.opportunity.point_blank_avoid():
            paid = avoid(b, shooter, square, threatening, caps, True)
        oa = OAContext()
        for eid, cap in zip(threatening, caps, strict=True):
            oa.left_within(eid, cap, paid=eid in paid)
        for eid in threatening:
            if eid in paid:
                continue
            if b.outcome is not None or not shooter.active:
                return
            enemy = b.state.get(eid)
            if enemy.active:
                opportunity_attack(b, enemy, shooter, square, oa)


# --- drawing weapons ------------------------------------------------------------------


def draw_options(b: Battle, c: CombatantState, on_turn: bool) -> tuple[DrawOption, ...]:
    if not c.active:
        return ()
    out = []
    current = c.gear
    for lo in c.profile.loadouts:
        q = b.pricing.draw(
            current, lo, on_turn=on_turn, used_weapon=c.used_weapon, bow_hands=c.bow_hands
        )
        if q is not None and q.total <= c.stamina:
            out.append(DrawOption(lo.name, q))
    return tuple(out)


def draw(b: Battle, c: CombatantState, loadout: str, on_turn: bool) -> None:
    q = b.pricing.draw(
        c.gear,
        c.profile.loadout(loadout),
        on_turn=on_turn,
        used_weapon=c.used_weapon,
        bow_hands=c.bow_hands,
    )
    assert q is not None
    if q.total:
        b.ops.spend(c, q, "draw")
    b.ops.draw(c, loadout, q.total)
