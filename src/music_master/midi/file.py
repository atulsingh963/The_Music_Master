"""Standard MIDI file import, export, and track sequence management."""

import os
from dataclasses import dataclass
from typing import List

import mido


@dataclass
class NoteEvent:
    note: int
    velocity: int
    start_time: float  # seconds
    duration: float  # seconds
    channel: int = 0


class MidiFileManager:
    """Handles reading and writing standard MIDI files (.mid)."""

    @staticmethod
    def read_midi_file(filepath: str) -> List[NoteEvent]:
        """Parses a standard MIDI file into a list of NoteEvent objects."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")

        mid = mido.MidiFile(filepath)
        events: List[NoteEvent] = []

        # Track active note-ons to match with note-offs: (channel, note) -> (start_time, velocity)
        active_notes: dict[tuple[int, int], tuple[float, int]] = {}
        current_time = 0.0

        for msg in mid:
            current_time += msg.time
            if msg.type == "note_on" and msg.velocity > 0:
                active_notes[(msg.channel, msg.note)] = (current_time, msg.velocity)
            elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
                key = (msg.channel, msg.note)
                if key in active_notes:
                    start_t, vel = active_notes.pop(key)
                    dur = max(0.01, current_time - start_t)
                    events.append(
                        NoteEvent(
                            note=msg.note,
                            velocity=vel,
                            start_time=start_t,
                            duration=dur,
                            channel=msg.channel,
                        )
                    )

        # Handle unclosed notes
        for (channel, note), (start_t, vel) in active_notes.items():
            events.append(
                NoteEvent(
                    note=note,
                    velocity=vel,
                    start_time=start_t,
                    duration=0.5,
                    channel=channel,
                )
            )

        events.sort(key=lambda e: e.start_time)
        return events

    @staticmethod
    def write_midi_file(
        filepath: str,
        events: List[NoteEvent],
        ticks_per_beat: int = 480,
        bpm: float = 120.0,
    ) -> None:
        """Writes a list of NoteEvent objects into a standard Type-0 MIDI file."""
        mid = mido.MidiFile(ticks_per_beat=ticks_per_beat)
        track = mido.MidiTrack()
        mid.tracks.append(track)

        tempo = mido.bpm2tempo(bpm)
        track.append(mido.MetaMessage("set_tempo", tempo=tempo, time=0))

        # Flatten NoteEvents into distinct note_on and note_off messages with absolute times
        timed_messages: List[tuple[float, mido.Message]] = []

        for e in events:
            on_msg = mido.Message(
                "note_on",
                channel=e.channel,
                note=e.note,
                velocity=e.velocity,
            )
            off_msg = mido.Message(
                "note_off",
                channel=e.channel,
                note=e.note,
                velocity=0,
            )
            timed_messages.append((e.start_time, on_msg))
            timed_messages.append((e.start_time + e.duration, off_msg))

        # Sort by timestamp, putting note_offs before note_ons if simultaneous
        def sort_key(item: tuple[float, mido.Message]) -> tuple[float, int]:
            t, m = item
            order = 0 if m.type == "note_off" else 1
            return (t, order)

        timed_messages.sort(key=sort_key)

        # Convert absolute seconds to delta ticks
        last_time_sec = 0.0
        for sec, msg in timed_messages:
            delta_sec = max(0.0, sec - last_time_sec)
            delta_ticks = int(mido.second2tick(delta_sec, ticks_per_beat, tempo))
            msg.time = delta_ticks
            track.append(msg)
            last_time_sec = sec

        mid.save(filepath)
