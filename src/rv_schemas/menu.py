from typing import Callable, NamedTuple

from .event import Event


class MenuItem(NamedTuple):
    label: str
    actionHook: Callable[[Event]] | None = None
    hotkey: str | None = None
    stateHook: Callable[..., int] | None = None
