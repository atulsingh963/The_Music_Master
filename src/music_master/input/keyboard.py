import logging
from typing import Dict, Set

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QKeyEvent

from music_master.input.key_mapping import (
    KeyboardProfile,
    get_harmonium_default_profile,
    get_piano_default_profile,
)

logger = logging.getLogger(__name__)


class KeyboardController(QObject):
    """Handles laptop keyboard events, translates keys to MIDI notes, and maintains active state."""

    note_on_signal = Signal(int, int)  # note, velocity
    note_off_signal = Signal(int)  # note
    panic_signal = Signal()
    octave_changed_signal = Signal(int)  # new octave offset
    transpose_changed_signal = Signal(int)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.profiles: Dict[str, KeyboardProfile] = {
            "harmonium": get_harmonium_default_profile(),
            "grand_piano": get_piano_default_profile(),
            "piano": get_piano_default_profile(),
        }
        self.active_profile_name = "harmonium"
        self.octave_offset = 0
        self.transpose_offset = 0
        self.velocity = 100

        # Track currently held keys to prevent OS key-repeat from triggering duplicate note_on
        self._held_keys: Set[str] = set()
        self._key_to_active_note: Dict[str, int] = {}

    def set_profile(self, name: str) -> None:
        if name in self.profiles:
            self.panic()
            self.active_profile_name = name

    def get_active_profile(self) -> KeyboardProfile:
        return self.profiles.get(self.active_profile_name, self.profiles["harmonium"])

    def set_octave_offset(self, offset: int) -> None:
        self.octave_offset = max(-3, min(3, offset))
        self.octave_changed_signal.emit(self.octave_offset)

    def change_octave(self, delta: int) -> None:
        self.set_octave_offset(self.octave_offset + delta)

    def set_transpose_offset(self, offset: int) -> None:
        self.transpose_offset = max(-12, min(12, offset))
        self.transpose_changed_signal.emit(self.transpose_offset)

    def change_transpose(self, delta: int) -> None:
        self.set_transpose_offset(self.transpose_offset + delta)

    def panic(self) -> None:
        """Release all held keys and send panic signal."""
        for note in list(self._key_to_active_note.values()):
            self.note_off_signal.emit(note)
        self._held_keys.clear()
        self._key_to_active_note.clear()
        self.panic_signal.emit()

    def handle_key_press(self, event: QKeyEvent) -> bool:
        """Processes key press. Returns True if handled by controller, False if ignored."""
        if event.isAutoRepeat():
            return True  # Ignore auto-repeat duplicates

        text = event.text().upper()
        if not text:
            return False

        if text in self._held_keys:
            return True

        profile = self.get_active_profile()
        midi_note = profile.get_note(text, self.octave_offset, self.transpose_offset)

        if midi_note is not None:
            self._held_keys.add(text)
            self._key_to_active_note[text] = midi_note
            self.note_on_signal.emit(midi_note, self.velocity)
            return True

        return False

    def handle_key_release(self, event: QKeyEvent) -> bool:
        """Processes key release."""
        if event.isAutoRepeat():
            return True

        text = event.text().upper()
        if text in self._held_keys:
            self._held_keys.remove(text)
            midi_note = self._key_to_active_note.pop(text, None)
            if midi_note is not None:
                self.note_off_signal.emit(midi_note)
            return True

        return False
