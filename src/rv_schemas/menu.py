from dataclasses import astuple, dataclass
from typing import Any, Callable

from .event import Event


@dataclass
class MenuItem:
    label: str
    actionHook: Callable[[Event], None] | None = None
    hotkey: str | None = None
    stateHook: Callable[[], int] | None = None

    def tuple(self) -> tuple[str, Callable[[Event], None], str, Callable[[], int]]:
        return astuple(self)
