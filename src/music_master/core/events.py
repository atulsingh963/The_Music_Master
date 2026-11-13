from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Callable


class EventType(Enum):
    NOTE_ON = auto()
    NOTE_OFF = auto()
    PANIC = auto()
    SUSTAIN = auto()
    OCTAVE_CHANGE = auto()
    TRANSPOSE_CHANGE = auto()
    INSTRUMENT_CHANGED = auto()
    AUDIO_DEVICE_CHANGED = auto()


@dataclass
class Event:
    event_type: EventType
    data: dict[str, Any]


class EventBus:
    """Central event dispatcher for decoupled communication between audio, UI, and input."""

    def __init__(self) -> None:
        self._listeners: dict[EventType, list[Callable[[Event], None]]] = {}

    def subscribe(self, event_type: EventType, callback: Callable[[Event], None]) -> None:
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        if callback not in self._listeners[event_type]:
            self._listeners[event_type].append(callback)

    def unsubscribe(self, event_type: EventType, callback: Callable[[Event], None]) -> None:
        if event_type in self._listeners and callback in self._listeners[event_type]:
            self._listeners[event_type].remove(callback)

    def publish(self, event: Event) -> None:
        if event.event_type in self._listeners:
            for listener in list(self._listeners[event.event_type]):
                try:
                    listener(event)
                except Exception:
                    # In audio or UI workflows, individual listener errors should not break notification loop
                    pass
