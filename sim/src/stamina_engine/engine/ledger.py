"""The public ledger: each creature's stamina as any observer can reconstruct it when stamina
is hidden but builds are known. It reads only public events and recomputes what they imply
from public facts (maximum stamina from level and HP, the recovery formula), never a
creature's hidden state."""

from stamina_engine.engine.events import DebtPaid, Event, Indebted, Injured, Recovered, Spent
from stamina_engine.model.state import BattleState
from stamina_engine.rules.ruleset import RuleSet

cites = ("Packet: Commitment", "Packet: Stamina", "Review F6")


class PublicLedger:
    def __init__(self, state: BattleState, rules: RuleSet) -> None:
        self.rules = rules
        self.profiles = {c.id: c.profile for c in state.combatants}
        self.hp = {c.id: c.hp for c in state.combatants}
        self.estimate = {c.id: c.profile.start_stamina for c in state.combatants}
        self.paid_debt = {c.id: 0 for c in state.combatants}  # this recovery's debt payment

    def _max(self, who: str) -> int:
        return self.rules.resources.max_stamina(self.hp[who], self.profiles[who].level)

    def observe(self, event: Event) -> None:
        if isinstance(event, Spent):  # every spend is declared, with a public price
            self.estimate[event.who] -= event.amount
        elif isinstance(event, Indebted):  # the shortfall was owed, not paid
            self.estimate[event.who] += event.owed
        elif isinstance(event, DebtPaid):
            self.paid_debt[event.who] = event.amount
        elif isinstance(event, Recovered):  # recovery happened: its amount is known
            gained = self.profiles[event.who].recovery - self.paid_debt[event.who]
            self.paid_debt[event.who] = 0
            self.estimate[event.who] = min(self._max(event.who), self.estimate[event.who] + gained)
        elif isinstance(event, Injured):  # wounds are visible; the new maximum follows
            self.hp[event.who] = event.hp_after
            self.estimate[event.who] = min(self.estimate[event.who], self._max(event.who))
