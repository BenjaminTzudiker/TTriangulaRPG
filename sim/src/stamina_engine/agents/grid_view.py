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

from stamina_engine.agents.decisions import CombatantView, MoveOptions, Observation
from stamina_engine.agents.estimates import Target, exact_estimate
from stamina_engine.core.errors import Unaffordable
from stamina_engine.grid.battlefield import Battlefield, Cell
from stamina_engine.grid.geometry import reach_cells
from stamina_engine.grid.pathing import Passage, Reach, Route, cheapest_path, reachable
from stamina_engine.grid.threat import Body, body, melee_weapons, threatening
from stamina_engine.model.derive import WeaponProfile
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

    @property
    def me(self) -> CombatantView:
        return self.obs.me

    def enemies(self) -> tuple[CombatantView, ...]:
        return tuple(v for v in self.obs.enemies() if v.status == "active" and v.pos is not None)

    def threatening(self, cell: Cell) -> tuple[str, ...]:
        """Enemies of mine that threaten cell, in initiative order."""
        return threatening(self.field, self.rules.grid, self.bodies, self.me.team, cell)

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

    # --- paths -----------------------------------------------------------------------

    def route(
        self,
        moves: MoveOptions,
        goals: list[Cell],
        limit: int,
        leave_price: Fraction | int = 1,
    ) -> Route | None:
        """The cheapest path to any goal within limit squares: movement stamina plus
        leave_price per threatening enemy on each square left."""
        prices = moves.price_by_length

        def leave(c: Cell) -> Fraction | int:
            return leave_price * len(self.threatening(c))

        def length(n: int) -> int | None:
            return prices[n] if n < len(prices) and n <= limit else None

        passage = Passage(moves.no_entry, moves.no_stop)
        return cheapest_path(
            self.field, self.rules.grid, moves.start, goals, passage, leave, length, limit
        )
