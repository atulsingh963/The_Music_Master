"""Unit tests for Phase 12 MIDI Manager and MIDI File import/export."""

import os

from music_master.midi.file import MidiFileManager, NoteEvent
from music_master.midi.manager import MidiManager


def test_midi_manager_discovery() -> None:
    manager = MidiManager()
    # Devices list may be 0 or more depending on hardware, but shouldn't error
    assert isinstance(manager.input_devices, list)
    assert isinstance(manager.output_devices, list)


def test_midi_manager_callback_routing() -> None:
    manager = MidiManager()
    received_notes = []

    def on_note_on(n: int, v: int, c: int) -> None:
        received_notes.append((n, v, c))

    manager.register_note_on_callback(on_note_on)
    for cb in manager._note_on_callbacks:
        cb(60, 100, 0)

    assert len(received_notes) == 1
    assert received_notes[0] == (60, 100, 0)


def test_midi_file_write_and_read(tmp_path: str) -> None:
    filepath = os.path.join(str(tmp_path), "test_melody.mid")

    original_events = [
        NoteEvent(note=60, velocity=100, start_time=0.0, duration=0.5, channel=0),
        NoteEvent(note=64, velocity=90, start_time=0.5, duration=0.5, channel=0),
        NoteEvent(note=67, velocity=95, start_time=1.0, duration=0.5, channel=0),
    ]

    MidiFileManager.write_midi_file(filepath, original_events, bpm=120.0)
    assert os.path.exists(filepath)

    loaded_events = MidiFileManager.read_midi_file(filepath)
    assert len(loaded_events) == 3
    assert loaded_events[0].note == 60
    assert loaded_events[1].note == 64
    assert loaded_events[2].note == 67
    assert loaded_events[0].velocity == 100
    assert abs(loaded_events[0].start_time - 0.0) < 0.05
    assert abs(loaded_events[1].start_time - 0.5) < 0.05
    assert abs(loaded_events[2].start_time - 1.0) < 0.05
