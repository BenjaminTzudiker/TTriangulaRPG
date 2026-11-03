"""Component registry: (kind, variant) -> class, plus dict conversion for TOML.

Every rule the fix order may change is a component. A variant is a frozen dataclass whose
fields are int, bool or str parameters, registered under its kind with @register.
"""

import dataclasses
import typing
from collections.abc import Callable, Mapping
from typing import ClassVar, TypeVar

from stamina_engine.core.errors import ConfigError

KINDS: tuple[str, ...] = (
    "crit",
    "surcharge",
    "blocks",
    "defenses",
    "resources",
    "wounds",
    "movement",
    "off_turn",
    "opportunity",
    "ranged",
    "turn_order",
    "dying",
    "information",
    "grid",
)

Scalar = int | bool | str


class Component:
    """Base for every rule component. Subclasses are frozen dataclasses."""

    kind: ClassVar[str]
    variant: ClassVar[str]
    cites: ClassVar[tuple[str, ...]]
    allowed: ClassVar[Mapping[str, frozenset[str]]] = {}

    def __post_init__(self) -> None:
        for name, values in self.allowed.items():
            value = getattr(self, name)
            if value not in values:
                raise ConfigError(
                    f"{self.kind}.{name} = {value!r}; expected one of {sorted(values)}"
                )


_REGISTRY: dict[tuple[str, str], type[Component]] = {}

C = TypeVar("C", bound=type[Component])


def register(kind: str, variant: str) -> Callable[[C], C]:
    """Class decorator: register a component variant under (kind, variant)."""

    def deco(cls: C) -> C:
        if kind not in KINDS:
            raise ConfigError(f"unknown component kind {kind!r}")
        if (kind, variant) in _REGISTRY:
            raise ConfigError(f"{kind}/{variant} registered twice")
        if not dataclasses.is_dataclass(cls):
            raise ConfigError(f"{cls.__name__} must be a frozen dataclass")
        cls.kind = kind
        cls.variant = variant
        _REGISTRY[(kind, variant)] = cls
        return cls

    return deco


def registered() -> dict[tuple[str, str], type[Component]]:
    return dict(_REGISTRY)


def lookup(kind: str, variant: str) -> type[Component]:
    try:
        return _REGISTRY[(kind, variant)]
    except KeyError:
        known = sorted(v for k, v in _REGISTRY if k == kind)
        raise ConfigError(f"no {kind} variant {variant!r}; known: {known}") from None


def params(component: Component) -> dict[str, Scalar]:
    """The component's parameters, in field order."""
    assert dataclasses.is_dataclass(component)
    return {f.name: getattr(component, f.name) for f in dataclasses.fields(component)}


def to_dict(component: Component) -> dict[str, Scalar]:
    return {"kind": component.variant, **params(component)}


def _check_types(cls: type[Component], values: Mapping[str, object]) -> None:
    hints = typing.get_type_hints(cls)
    names = {f.name for f in dataclasses.fields(cls)}  # type: ignore[arg-type]
    for name, value in values.items():
        if name not in names:
            raise ConfigError(f"{cls.kind}/{cls.variant} has no parameter {name!r}")
        expected = hints[name]
        ok = isinstance(value, expected) and (expected is bool or not isinstance(value, bool))
        if not ok:
            raise ConfigError(f"{cls.kind}.{name} must be {expected.__name__}, got {value!r}")


def from_dict(kind: str, data: Mapping[str, object], base: Component | None = None) -> Component:
    """Build a component from TOML data. Without "kind", the base's variant is kept."""
    variant = data.get("kind", base.variant if base is not None else None)
    if not isinstance(variant, str):
        raise ConfigError(f"{kind} needs a 'kind'")
    cls = lookup(kind, variant)
    values = {k: v for k, v in data.items() if k != "kind"}
    _check_types(cls, values)
    if base is not None and type(base) is cls:
        return dataclasses.replace(base, **values)  # type: ignore[type-var]
    return cls(**values)
