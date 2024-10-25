from dataclasses import dataclass
from enum import IntEnum
from typing import List, Protocol


@dataclass
class Vec2:
    """Represents a 2D vector or coordinate."""

    x: float
    y: float


class Button(IntEnum):
    """Button states."""

    Button1 = 1
    Button2 = 2
    Button3 = 4  # OR'd bitmask for multiple buttons


class Modifier(IntEnum):
    """Key modifier states."""

    None_ = 0
    Shift = 1
    Control = 2
    Alt = 4
    Meta = 8
    Super = 16
    CapLock = 32
    NumLock = 64
    ScrollLock = 128


class ContentType(IntEnum):
    """Content types for drag-and-drop events."""

    UnknownObject = 0
    BadObject = 1
    FileObject = 2
    URLObject = 3
    TextObject = 4


class Event(Protocol):
    """Interface for the Event object with type checking."""

    def pointer(self) -> Vec2:
        """Returns the location of the pointer relative to the view."""
        ...

    def relativePointer(self) -> Vec2:
        """Returns the location of the pointer relative to the current widget or view."""
        ...

    def reference(self) -> Vec2:
        """Returns the location of the initial button down during dragging."""
        ...

    def domain(self) -> Vec2:
        """Returns the size of the view."""
        ...

    def subDomain(self) -> Vec2:
        """Returns the size of the current widget, if present."""
        ...

    def buttons(self) -> int:
        """Returns an int bitmask of pressed buttons."""
        ...

    def modifiers(self) -> int:
        """Returns an int bitmask of active modifiers."""
        ...

    def key(self) -> int:
        """Returns the keysym value as an int."""
        ...

    def name(self) -> str:
        """Returns the name of the event."""
        ...

    def contents(self) -> str:
        """Returns the string content of the event."""
        ...

    def contentsArray(self) -> List[str]:
        """Returns ancillary information as a list of strings."""
        ...

    def sender(self) -> str:
        """Returns the name of the sender."""
        ...

    def contentType(self) -> ContentType:
        """Returns the type of the event's content."""
        ...

    def timeStamp(self) -> float:
        """Returns the timestamp of the event."""
        ...

    def reject(self) -> None:
        """Rejects the event to pass it to the next binding."""
        ...

    def setReturnContent(self, content: str) -> None:
        """Sets the return content for events with contents."""
        ...
