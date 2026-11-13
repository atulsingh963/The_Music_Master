"""Quantization utility for MIDI note timing and musical grids."""

from typing import List

from music_master.midi.file import NoteEvent


class NoteQuantizer:
    """Quantizes note start times and lengths to musical subdivisions."""

    GRID_SUBDIVISIONS = {
        "1/1": 4.0,  # whole note (4 beats)
        "1/2": 2.0,  # half note (2 beats)
        "1/4": 1.0,  # quarter note (1 beat)
        "1/8": 0.5,  # eighth note
        "1/16": 0.25,  # sixteenth note
        "1/32": 0.125,  # 32nd note
        "1/8T": 1.0 / 3.0,  # eighth triplet
        "1/16T": 1.0 / 6.0,  # sixteenth triplet
    }

    @classmethod
    def quantize_notes(
        cls,
        notes: List[NoteEvent],
        grid: str = "1/16",
        bpm: float = 120.0,
        strength: float = 1.0,
        quantize_duration: bool = False,
    ) -> List[NoteEvent]:
        """Quantizes note start times towards the nearest grid subdivision.

        strength ranges from 0.0 (no change) to 1.0 (strict snap).
        """
        beat_dur = 60.0 / bpm
        subdivision_beats = cls.GRID_SUBDIVISIONS.get(grid, 0.25)
        step_seconds = subdivision_beats * beat_dur

        quantized_list: List[NoteEvent] = []
        for n in notes:
            # Nearest grid point
            nearest_idx = round(n.start_time / step_seconds)
            target_start = nearest_idx * step_seconds
            new_start = n.start_time + (target_start - n.start_time) * strength

            new_dur = n.duration
            if quantize_duration:
                dur_steps = max(1, round(n.duration / step_seconds))
                target_dur = dur_steps * step_seconds
                new_dur = max(0.02, n.duration + (target_dur - n.duration) * strength)

            quantized_list.append(
                NoteEvent(
                    note=n.note,
                    velocity=n.velocity,
                    start_time=max(0.0, new_start),
                    duration=new_dur,
                    channel=n.channel,
                )
            )

        quantized_list.sort(key=lambda x: x.start_time)
        return quantized_list
