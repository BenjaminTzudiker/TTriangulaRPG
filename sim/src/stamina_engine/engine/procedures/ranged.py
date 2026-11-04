"""Ranged attacks and drawing weapons (Packet: Ranged Attacks, Aim, Range Bands, Cover,
Drawing Weapons; Opportunity Attacks: shooting in melee).

A shot, following the packet's steps (readings in the Assumptions register):
1. Declare the target: an enemy within the weapon's long range that isn't in total cover.
2-3. Pay the flat shot cost and buy aim steps (actions: the surcharge applies).
4. Roll: the weapon's damage plus each aim step. Too few aims for the range band: it misses.
5. The target may dive for cover with off-turn movement; its OAs resolve first. Total cover
   at the end of a dive counts as three-quarters.
6. The target blocks with Ranged Defense, or Melee Defense if the shooter is within its
   reach (judged after the dive); cover adds to either.
7. Armor, crits, injury.
Then, if the shooter is within any enemy's reach, every enemy threatening it may make an
opportunity attack, lowest initiative first; these can't be avoided by paying (as written).
"""

from stamina_engine.agents.decisions import AimRequest, DiveRequest, DrawOption, Move
from stamina_engine.engine.battle import Battle
from stamina_engine.engine.events import (
    AttackRolled,
    Dived,
    OpportunityProvoked,
    ShotDeclared,
    ShotMissed,
)
from stamina_engine.engine.procedures.melee import armor_and_crits, declare_blocks, lose_hp
from stamina_engine.engine.procedures.movement import avoid, move, move_options
from stamina_engine.engine.procedures.opportunity import OAContext, opportunity_attack, reach_cap
from stamina_engine.grid.battlefield import Cell
from stamina_engine.grid.geometry import distance
from stamina_engine.grid.los import Cover, cover
from stamina_engine.grid.threat import body, threatened_by
from stamina_engine.model.state import CombatantState
from stamina_engine.rules.exchange import roll_shot
from stamina_engine.rules.pricing import Quote

cites = (
    "Packet: Ranged Attacks",
    "Packet: Aim",
    "Packet: Range Bands",
    "Packet: Cover",
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
        band = b.rules.ranged.band(distance(c.pos, o.pos, b.rules.grid), weapon.ranges)
        if band != "beyond" and cover_from(b, c, o) < Cover.TOTAL:
            out.append(o.id)
    return tuple(out)


def point_blank(b: Battle, target: CombatantState, shooter: CombatantState) -> bool:
    """Is the shooter within the target's melee reach?"""
    if b.field is None or target.pos is None or shooter.pos is None:
        return False
    me = body(target.id, target.team, target.pos, target.gear, target.active)
    return shooter.pos in threatened_by(b.field, b.rules.grid, me)


def shoot(b: Battle, shooter: CombatantState, target: CombatantState) -> None:
    weapon = shooter.gear.weapon
    assert (
        weapon is not None and weapon.ranged and shooter.pos is not None and target.pos is not None
    )
    r = b.rules.ranged
    with b.context.frame(f"shot {shooter.id}->{target.id}"):
        band = r.band(distance(shooter.pos, target.pos, b.rules.grid), weapon.ranges)
        level = cover_from(b, shooter, target)
        required = r.required_aims(band)
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
        )
        aims = b.broker.aim(request)
        b.ops.emit(ShotDeclared(shooter.id, target.id, aims, band, int(level)))
        b.ops.spend(shooter, quotes[aims], "shot")
        b.ops.use_weapon(shooter, bow=True)
        if aims < required:
            b.ops.emit(ShotMissed(shooter.id, target.id, f"{band} range needs {required} aims"))
        else:
            fin = shooter.gear.attributes.FIN
            attack = roll_shot(
                weapon, aims, fin, band, b.rules, b.dice.dice(f"attack:{shooter.id}")
            )
            faces = tuple(f for s in attack.steps for f in s.faces)
            b.ops.emit(AttackRolled(shooter.id, faces, attack.total, attack.crit_dice))
            level = dive(b, shooter, target, attack.total, attack.crit_dice, level)
            if b.outcome is None:
                bonus = r.cover_bonus(int(level))
                gear = target.gear
                base = (
                    gear.melee_defense if point_blank(b, target, shooter) else gear.ranged_defense
                )
                blocks = declare_blocks(b, shooter, target, attack, base + bonus, True, bonus)
                outcome = armor_and_crits(b, shooter, target, attack, blocks, base + bonus)
                lose_hp(b, target, outcome)
    if b.outcome is None and shooter.active:
        point_blank_oas(b, shooter)


def dive(
    b: Battle,
    shooter: CombatantState,
    target: CombatantState,
    damage: int,
    crit_dice: int,
    level: Cover,
) -> Cover:
    """Step 5: the target may dive with off-turn movement. Returns the cover the shot faces."""
    if not target.active or b.field is None:
        return level
    moves = move_options(b, target, on_turn=False)
    if moves is None:
        return level
    r = b.rules.ranged
    after = {d: r.dive_cover(int(cover_from(b, shooter, target, d))) for d in moves.destinations}
    request = DiveRequest(
        target.id,
        b.observe(target.id),
        b.context.path(),
        shooter.id,
        damage,
        crit_dice,
        int(level),
        moves,
        after,
    )
    answer = b.broker.dive(request)
    if not isinstance(answer, Move):
        return level
    with b.context.frame(f"dive {target.id}"):
        move(b, target, answer.path, on_turn=False)
    new = Cover(r.dive_cover(int(cover_from(b, shooter, target))))
    b.ops.emit(Dived(target.id, int(new)))
    return new


def point_blank_oas(b: Battle, shooter: CombatantState) -> None:
    """Shooting within an enemy's reach provokes from every enemy threatening the shooter,
    once the shot has resolved."""
    if not b.rules.opportunity.attacks_allowed() or shooter.pos is None:
        return
    threatening = b.arena.threatening(b.state, shooter, shooter.pos)
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
