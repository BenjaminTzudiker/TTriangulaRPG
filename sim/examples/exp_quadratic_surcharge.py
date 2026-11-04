"""Example plugin: a quadratic on-turn surcharge. An experiment, not a rule.

Each action costs +slope x (actions already taken)^2 instead of +1 per action, so base-2
steps cost 2, 3, 6, 11... instead of 2, 3, 4, 5. It is one of the surcharge shapes the
engine plan lists for F1 and F8. Try it from sim/:

    se table 8 --plugin examples/exp_quadratic_surcharge.py \
        --ruleset examples/exp_quadratic_surcharge.toml

A plugin variant subclasses the component kind's base class (here SurchargeRule), which
supplies the packet citations; override `cites` if the idea answers a different rule.
"""

from dataclasses import dataclass

from stamina_engine.rules.components.surcharge import SurchargeRule
from stamina_engine.rules.registry import register


@register("surcharge", "exp_quadratic")
@dataclass(frozen=True)
class QuadraticSurcharge(SurchargeRule):
    slope: int = 1

    def surcharge(self, prior_actions: int) -> int:
        return self.slope * prior_actions * prior_actions
