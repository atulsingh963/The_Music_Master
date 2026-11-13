from dataclasses import dataclass, field

from music_master.config import Config
from music_master.core.events import EventBus


@dataclass
class ApplicationState:
    config: Config
    event_bus: EventBus = field(default_factory=EventBus)
    active_instrument_id: str = "harmonium"
    current_octave_offset: int = 0
    current_transpose_offset: int = 0
    sustain_active: bool = False
    active_notes: set[int] = field(default_factory=set)
    is_recording: bool = False
