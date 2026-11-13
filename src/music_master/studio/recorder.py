"""Real-time MIDI and audio recording engine with overdub and metronome count-in support."""

import enum
import logging
import time
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np

from music_master.midi.file import NoteEvent

logger = logging.getLogger(__name__)


class RecordingState(enum.Enum):
    STOPPED = "stopped"
    COUNT_IN = "count_in"
    RECORDING = "recording"
    PLAYING = "playing"
    PAUSED = "paused"


class AudioMidiRecorder:
    """Coordinates timeline playback, MIDI note recording, audio recording, and overdub."""

    def __init__(self, sample_rate: int = 44100, bpm: float = 120.0) -> None:
        self.sample_rate = sample_rate
        self.bpm = bpm
        self.state = RecordingState.STOPPED

        # Timeline
        self.timeline_position: float = 0.0  # in seconds
        self._playback_start_wall_time: Optional[float] = None
        self._recording_start_timeline_pos: float = 0.0

        # Metronome count-in
        self.count_in_bars: int = 1
        self.time_signature_num: int = 4
        self.count_in_remaining_beats: int = 0
        self._last_count_in_beat_time: float = 0.0

        # Overdub mode: if True, recorded events append to existing track notes; if False, overwrite
        self.overdub: bool = True

        # Active unclosed notes during recording: (channel, note) -> (start_time, velocity)
        self._active_record_notes: Dict[Tuple[int, int], Tuple[float, int]] = {}

        # Recorded note buffer
        self.recorded_notes: List[NoteEvent] = []

        # Audio stream recording buffer (float32 stereo blocks)
        self._audio_record_enabled: bool = True
        self._recorded_audio_blocks: List[np.ndarray] = []

        # Listeners / callbacks for UI updates
        self.state_changed_callbacks: List[Callable[[RecordingState], None]] = []

    def set_bpm(self, bpm: float) -> None:
        self.bpm = max(20.0, min(300.0, bpm))

    def set_timeline_position(self, pos: float) -> None:
        self.timeline_position = max(0.0, pos)

    def _set_state(self, new_state: RecordingState) -> None:
        if self.state != new_state:
            self.state = new_state
            for cb in self.state_changed_callbacks:
                try:
                    cb(new_state)
                except Exception as e:
                    logger.exception(f"Error in state callback: {e}")

    def start_recording(self, with_count_in: bool = True) -> None:
        """Starts recording, optionally waiting through a metronome count-in."""
        if not self.overdub:
            self.recorded_notes.clear()
            self._recorded_audio_blocks.clear()

        self._active_record_notes.clear()
        self._recording_start_timeline_pos = self.timeline_position

        if with_count_in and self.count_in_bars > 0:
            self.count_in_remaining_beats = self.count_in_bars * self.time_signature_num
            self._last_count_in_beat_time = time.time()
            self._set_state(RecordingState.COUNT_IN)
        else:
            self.count_in_remaining_beats = 0
            self._playback_start_wall_time = time.time()
            self._set_state(RecordingState.RECORDING)

    def start_playback(self) -> None:
        """Plays the current recorded / project sequence from timeline_position."""
        self._playback_start_wall_time = time.time()
        self._set_state(RecordingState.PLAYING)

    def pause(self) -> None:
        if self.state in (RecordingState.RECORDING, RecordingState.PLAYING):
            self.stop_all_active_notes()
            self._set_state(RecordingState.PAUSED)

    def stop(self) -> None:
        self.stop_all_active_notes()
        self._set_state(RecordingState.STOPPED)

    def record_note_on(self, note: int, velocity: int = 100, channel: int = 0) -> None:
        """Called by KeyboardController or MIDI manager when a note begins."""
        if self.state != RecordingState.RECORDING:
            return

        key = (channel, note)
        # Note start relative to timeline
        self._active_record_notes[key] = (self.timeline_position, velocity)

    def record_note_off(self, note: int, channel: int = 0) -> None:
        """Called when a note ends."""
        if self.state != RecordingState.RECORDING:
            return

        key = (channel, note)
        if key in self._active_record_notes:
            start_t, vel = self._active_record_notes.pop(key)
            dur = max(0.02, self.timeline_position - start_t)
            ev = NoteEvent(
                note=note,
                velocity=vel,
                start_time=start_t,
                duration=dur,
                channel=channel,
            )
            self.recorded_notes.append(ev)

    def stop_all_active_notes(self) -> None:
        """Finalize any lingering active notes."""
        if self._active_record_notes:
            for (channel, note), (start_t, vel) in list(self._active_record_notes.items()):
                dur = max(0.05, self.timeline_position - start_t)
                self.recorded_notes.append(
                    NoteEvent(
                        note=note,
                        velocity=vel,
                        start_time=start_t,
                        duration=dur,
                        channel=channel,
                    )
                )
            self._active_record_notes.clear()

    def record_audio_block(self, audio_data: np.ndarray) -> None:
        """Captures rendered output audio frames while recording."""
        if self.state == RecordingState.RECORDING and self._audio_record_enabled:
            self._recorded_audio_blocks.append(audio_data.copy())

    def update_timeline(self, delta_seconds: float) -> None:
        """Steps timeline forward during playback or recording."""
        if self.state == RecordingState.COUNT_IN:
            # Handle count in beat countdown
            beat_interval = 60.0 / self.bpm
            now = time.time()
            if now - self._last_count_in_beat_time >= beat_interval:
                self.count_in_remaining_beats -= 1
                self._last_count_in_beat_time = now
                if self.count_in_remaining_beats <= 0:
                    self._playback_start_wall_time = time.time()
                    self._set_state(RecordingState.RECORDING)

        elif self.state in (RecordingState.RECORDING, RecordingState.PLAYING):
            self.timeline_position += delta_seconds

    def get_recorded_audio(self) -> Optional[np.ndarray]:
        """Returns the accumulated float32 recorded audio array (stereo)."""
        if not self._recorded_audio_blocks:
            return None
        return np.vstack(self._recorded_audio_blocks)
