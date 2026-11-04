"""What an agent can work out about the grid from its observation: bodies, threat, where
enemies could get to, how many could engage a square, and what an OA would cost it.

Everything here reads only the Observation (positions are public; stamina is the observer's
estimate when hidden) and the RuleSet, never battle state.

Approximations (agent conventions, not rules):
- An enemy's reach next turn is what its free movement alone gets it to.
- An enemy's OA is priced as if its off-turn track were empty (others' trackers aren't
  observed), so the estimate can run a little high.
"""

from dataclasses import dataclass, replace
from fractions import Fraction
from functools import lru_cache

from stamina_engine.agents.decisions import CombatantView, MoveOptions, Observation
from stamina_engine.agents.estimates import Target, exact_estimate
from stamina_engine.core.errors import Unaffordable
from stamina_engine.grid.battlefield import Battlefield, Cell
from stamina_engine.grid.geometry import distance, reach_cells
from stamina_engine.grid.los import Cover, cover
from stamina_engine.grid.pathing import Passage, Reach, Route, best_of, cheapest_routes, reachable
from stamina_engine.grid.threat import Body, body, melee_weapons, threatened_by
from stamina_engine.model.derive import WeaponProfile
from stamina_engine.rules.block_solver import best_block
from stamina_engine.rules.pricing import FRESH, Pricing
from stamina_engine.rules.ruleset import RuleSet

cites = ("Packet: Triggers", "Packet: Making Opportunity Attacks", "Packet: On-Turn Movement")


def bodies_from(obs: Observation) -> tuple[Body, ...]:
    """Every placed creature, in initiative order (the order threat lists use)."""
    views = {v.id: v for v in (obs.me, *obs.others)}
    order = [cid for cid in obs.order if cid in views] + [
        cid for cid in views if cid not in obs.order
    ]
    out = []
    for cid in order:
        v = views[cid]
        if v.pos is not None:
            out.append(body(v.id, v.team, v.pos, v.gear, v.status == "active"))
    return tuple(out)


def attack_squares(field: Battlefield, rules: RuleSet, reach: int, target: Cell) -> frozenset[Cell]:
    """Squares from which a weapon of this reach threatens target (lines are symmetric)."""
    return reach_cells(field, target, reach, rules.grid)


@dataclass
class Board:
    """One decision's view of the grid, with caches for the queries agents repeat."""

    obs: Observation
    rules: RuleSet

    def __post_init__(self) -> None:
        assert self.obs.field is not None
        self.field: Battlefield = self.obs.field
        self.bodies = bodies_from(self.obs)
        self.pricing = Pricing(self.rules)
        self._reach: dict[tuple[str, Cell | None], Reach] = {}
        self._engagers: dict[tuple[Cell, bool], int] = {}
        self._routes: dict[tuple[Cell, int, Fraction | int], dict[Cell, Route]] = {}
        threats: dict[Cell, list[str]] = {}
        for b in self.bodies:  # initiative order, so each list is too
            if b.team != self.me.team:
                for cell in threatened_by(self.field, self.rules.grid, b):
                    threats.setdefault(cell, []).append(b.id)
        self._threats = {c: tuple(ids) for c, ids in threats.items()}

    @property
    def me(self) -> CombatantView:
        return self.obs.me

    def enemies(self) -> tuple[CombatantView, ...]:
        return tuple(v for v in self.obs.enemies() if v.status == "active" and v.pos is not None)

    def threatening(self, cell: Cell) -> tuple[str, ...]:
        """Enemies of mine that threaten cell, in initiative order."""
        return self._threats.get(cell, ())

    def free_reach(self, v: CombatantView, me_at: Cell | None = None) -> Reach:
        """Where v could get to on its next turn with free movement alone, with the observer
        standing on me_at (its own square if None)."""
        key = (v.id, me_at)
        if key not in self._reach:
            assert v.pos is not None
            bodies = self.bodies
            if me_at is not None:
                bodies = tuple(replace(b, pos=me_at) if b.id == self.me.id else b for b in bodies)
            passage = Passage.for_mover(self.rules.grid, v.id, v.team, bodies)
            self._reach[key] = reachable(
                self.field, self.rules.grid, v.pos, passage, v.gear.movement
            )
        return self._reach[key]

    def engagers(self, cell: Cell, moved: bool = False) -> int:
        """How many enemies could attack the observer next turn if it stood on cell: each
        needs its own square it can reach (free movement) from which its main weapon reaches
        cell. With moved, the observer is taken to have moved there (its old square is
        empty and it blocks the new one)."""
        key = (cell, moved)
        if key in self._engagers:
            return self._engagers[key]
        taken: set[Cell] = set()
        count = 0
        for e in self.enemies():
            weapon = e.gear.weapon
            if weapon is None or weapon.ranged:
                continue
            reach = self.free_reach(e, cell if moved else None)
            spots = sorted(attack_squares(self.field, self.rules, weapon.reach, cell))
            for s in spots:
                if s in taken or s == cell:
                    continue
                here = s == e.pos
                stoppable = s in reach.steps and s not in reach.passage.no_stop
                if here or stoppable:
                    taken.add(s)
                    count += 1
                    break
        self._engagers[key] = count
        return count

    # --- opportunity attacks against me ----------------------------------------------

    def oa_options(self, enemy: CombatantView, square: Cell) -> list[tuple[WeaponProfile, int]]:
        """The enemy's weapons that reach square and the most steps each could take."""
        if enemy.pos is None or enemy.status != "active":
            return []
        out = []
        fin = enemy.gear.attributes.FIN
        for w in melee_weapons(enemy.gear):
            if square not in reach_cells(self.field, enemy.pos, w.reach, self.rules.grid):
                continue
            cap = self.pricing.oa_cap(fin, w.base)
            k = 0
            while True:
                try:
                    self.pricing.opportunity_attack(
                        w.base, k + 1, FRESH, cap, stamina=enemy.stamina
                    )
                except Unaffordable:
                    break
                k += 1
            if k:
                out.append((w, k))
        return out

    def oa_value(self, enemy: CombatantView, square: Cell, w: Fraction) -> Fraction:
        """What the enemy's best OA on me would cost me: block stamina + w x injury, exact."""
        me = self.me
        target = Target(me.gear.melee_defense, me.gear.armor, me.stamina, me.hp)
        best = Fraction(0)
        for weapon, steps in self.oa_options(enemy, square):
            e = exact_estimate(weapon, steps, target, self.rules, w)
            best = max(best, Fraction(e.cost) + w * Fraction(e.injury))
        return best

    def attack_squares_of(self, v: CombatantView, cell: Cell) -> frozenset[Cell]:
        """Squares from which v's main weapon would reach cell."""
        weapon = v.gear.weapon
        if weapon is None or weapon.ranged:
            return frozenset()
        return attack_squares(self.field, self.rules, weapon.reach, cell)

    def attack_spots(self, cell: Cell) -> frozenset[Cell]:
        """Squares the observer would threaten from cell with its ready melee weapons."""
        out: frozenset[Cell] = frozenset()
        for w in melee_weapons(self.me.gear):
            out |= reach_cells(self.field, cell, w.reach, self.rules.grid)
        return out

    # --- shots -----------------------------------------------------------------------

    def cover_at(self, shooter: Cell, target: Cell, skip: tuple[str, ...] = ()) -> Cover:
        """Cover a creature at target would have from shooter, other creatures counting."""
        others = [b.pos for b in self.bodies if b.id not in skip and b.pos not in (shooter, target)]
        return cover(self.field, self.rules.grid, shooter, target, others)

    def shot_exposure(self, cell: Cell) -> int:
        """How exposed the observer would be at cell to enemy shooters holding a bow: 2 per
        shooter in range with no cover, 1 with half cover, 0 otherwise."""
        total = 0
        for e in self.enemies():
            weapon = e.gear.weapon
            if weapon is None or not weapon.ranged or e.pos is None:
                continue
            band = self.rules.ranged.band(distance(e.pos, cell, self.rules.grid), weapon.ranges)
            if band == "beyond":
                continue
            level = self.cover_at(e.pos, cell, (e.id, self.me.id))
            total += max(0, 2 - int(level))
        return total

    # --- paths -----------------------------------------------------------------------

    def routes(
        self, moves: MoveOptions, limit: int, leave_price: Fraction | int = 1
    ) -> dict[Cell, Route]:
        """The cheapest path to every square within limit squares: movement stamina plus
        leave_price per threatening enemy on each square left."""
        key = (moves.start, limit, leave_price)
        if key not in self._routes:
            prices = moves.price_by_length

            def leave(c: Cell) -> Fraction | int:
                return leave_price * len(self.threatening(c))

            def length(n: int) -> int | None:
                return prices[n] if n < len(prices) and n <= limit else None

            passage = Passage(moves.no_entry, moves.no_stop)
            self._routes[key] = cheapest_routes(
                self.field, self.rules.grid, moves.start, passage, leave, length, limit
            )
        return self._routes[key]

    def route(
        self,
        moves: MoveOptions,
        goals: list[Cell],
        limit: int,
        leave_price: Fraction | int = 1,
    ) -> Route | None:
        """The cheapest path to any goal (least total, then shorter, then first listed)."""
        return best_of(self.routes(moves, limit, leave_price), goals)


# --- ranged estimates -----------------------------------------------------------------


@lru_cache(maxsize=1 << 14)
def shot_value(
    weapon: WeaponProfile,
    aims: int,
    finesse: int,
    band: str,
    defense: int,
    armor: int,
    stamina: int,
    hp: int,
    rules: RuleSet,
    w: Fraction,
) -> tuple[Fraction, Fraction, Fraction]:
    """(expected injury, expected stamina the target spends, P(down)) for one shot, exactly,
    against the target's best blocks."""
    from stamina_engine.analysis.ranged import respond, shot

    r = respond(shot(weapon, aims, finesse, band, rules), defense, armor, stamina, hp, rules, w)
    return r.injury, r.stamina, r.p_down


def block_score(
    damage: int,
    crit_dice: int,
    defense: int,
    armor: int,
    stamina: int,
    hp: int,
    rules: RuleSet,
    w: Fraction,
) -> Fraction:
    """What blocking a known roll costs: stamina + w x injury, with a big penalty for going
    down (the block solver never takes an avoidable incapacitation)."""
    choice = best_block(
        damage, crit_dice, defense, armor, max(stamina, 0), hp, rules, w, ranged=True
    )
    return choice.score + (100 * w if choice.incapacitated else 0)


def is_shooter(view: CombatantView) -> bool:
    return any(lo.weapon is not None and lo.weapon.ranged for lo in view.profile.loadouts)


def ranged_loadout(view: CombatantView) -> str | None:
    for lo in view.profile.loadouts:
        if lo.weapon is not None and lo.weapon.ranged:
            return lo.name
    return None
