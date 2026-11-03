"""Engine error types."""


class EngineError(Exception):
    """Base class for every error the engine raises."""


class RulesError(EngineError):
    """A request the rules don't allow, such as an unaffordable or illegal choice."""


class Unaffordable(RulesError):
    """A cost exceeds the stamina available, or an opportunity attack exceeds its cap."""


class BudgetError(RulesError):
    """A build spends more Expertise or Ability Points than its level allows."""


class ConfigError(EngineError):
    """A RuleSet, build or data file is malformed or names something unknown."""


class ScriptExhausted(EngineError):
    """Scripted dice ran out of faces."""
