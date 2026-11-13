from dataclasses import dataclass
from enum import Enum


class InstrumentCategory(Enum):
    INDIAN_CLASSICAL = "Indian Classical"
    WESTERN_KEYBOARD = "Western Keyboard"
    STRINGS = "Strings"
    WIND = "Wind"
    PERCUSSION = "Percussion"
    ELECTRONIC = "Electronic"
    WORLD = "World"
    VOCAL = "Vocal and Ambient"


class AvailabilityState(Enum):
    AVAILABLE = "Available"
    INSTALLED = "Installed"
    MISSING_SOUND_LIBRARY = "Missing Sound Library"
    EXPERIMENTAL = "Experimental"
    PLANNED = "Planned"


@dataclass
class InstrumentDefinition:
    id: str
    name: str
    category: InstrumentCategory
    availability: AvailabilityState
    description: str
    sound_source: str = "Synthesis"
    default_midi_program: int = 0
