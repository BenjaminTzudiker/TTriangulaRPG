"""The timing-context stack: where the battle is when a decision is asked (for example
"round 2 > turn ana > attack ana->bors > blocks bors"). Agents receive it with every request,
and the decision log records it, which is how nested-window ordering becomes measurable."""

from collections.abc import Iterator
from contextlib import contextmanager


class TimingContext:
    def __init__(self) -> None:
        self._frames: list[str] = []

    @contextmanager
    def frame(self, name: str) -> Iterator[None]:
        self._frames.append(name)
        try:
            yield
        finally:
            self._frames.pop()

    def path(self) -> tuple[str, ...]:
        return tuple(self._frames)
