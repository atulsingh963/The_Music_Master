"""Precise audio metronome engine supporting standard and Indian laya subdivisions."""

import math
from typing import Callable, Optional

import numpy as np


class MetronomeEngine:
    """Generates audio click clicks and pulse timing for rhythmic practice and recording."""

    def __init__(
        self,
        sample_rate: int = 44100,
        bpm: float = 120.0,
        beats_per_bar: int = 4,
        accent_first_beat: bool = True,
    ) -> None:
        self.sample_rate = sample_rate
        self.bpm = max(20.0, min(360.0, bpm))
        self.beats_per_bar = max(1, beats_per_bar)
        self.accent_first_beat = accent_first_beat

        self.is_active = False
        self.current_beat = 0
        self.samples_per_beat = int((60.0 / self.bpm) * self.sample_rate)
        self.sample_counter = 0

        # Pre-synthesize high and normal click buffers (50ms blips)
        self.high_click = self._generate_click_buffer(freq=1200.0, duration=0.04)
        self.low_click = self._generate_click_buffer(freq=800.0, duration=0.035)

        self.active_click_buffer: Optional[np.ndarray] = None
        self.click_offset = 0
        self.on_beat_callback: Optional[Callable[[int, bool], None]] = None

    def _generate_click_buffer(self, freq: float, duration: float) -> np.ndarray:
        frames = int(duration * self.sample_rate)
        t = np.linspace(0, duration, frames, endpoint=False)
        sine = np.sin(2.0 * math.pi * freq * t)
        # Fast exponential decay envelope
        env = np.exp(-t * 90.0)
        return (sine * env * 0.75).astype(np.float32)

    def set_bpm(self, bpm: float) -> None:
        self.bpm = max(20.0, min(360.0, bpm))
        self.samples_per_beat = max(1, int((60.0 / self.bpm) * self.sample_rate))

    def set_time_signature(self, beats_per_bar: int) -> None:
        self.beats_per_bar = max(1, beats_per_bar)

    def start(self) -> None:
        self.is_active = True
        self.current_beat = 0
        self.sample_counter = 0
        self._trigger_beat()

    def stop(self) -> None:
        self.is_active = False
        self.active_click_buffer = None
        self.click_offset = 0

    def _trigger_beat(self) -> None:
        is_accent = (self.current_beat == 0) and self.accent_first_beat
        self.active_click_buffer = self.high_click if is_accent else self.low_click
        self.click_offset = 0

        if self.on_beat_callback:
            self.on_beat_callback(self.current_beat, is_accent)

    def process_frames(self, num_frames: int) -> np.ndarray:
        """Renders click audio and updates beat positions for the given buffer block."""
        output = np.zeros(num_frames, dtype=np.float32)
        if not self.is_active:
            return output

        for i in range(num_frames):
            if self.sample_counter >= self.samples_per_beat:
                self.sample_counter = 0
                self.current_beat = (self.current_beat + 1) % self.beats_per_bar
                self._trigger_beat()

            if self.active_click_buffer is not None:
                if self.click_offset < len(self.active_click_buffer):
                    output[i] += self.active_click_buffer[self.click_offset]
                    self.click_offset += 1
                else:
                    self.active_click_buffer = None

            self.sample_counter += 1

        return output
