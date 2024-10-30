from dataclasses import dataclass, fields
from typing import Callable

from .event import Event


@dataclass
class MenuItem:
    label: str
    actionHook: Callable[[Event], None] | None = None
    hotkey: str | None = None
    stateHook: Callable[[], int] | None = None

    def tuple(self) -> tuple[str, Callable[[Event], None], str, Callable[[], int]]:
        # dataclasses.astuple() returns a deep copy which breaks the callback hooks, so we roll our own
        return tuple(self.__dict__[field.name] for field in fields(self))
