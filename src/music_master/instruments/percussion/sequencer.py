"""16-Step Drum Sequencer engine for rhythmic pattern creation and playback."""

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

import numpy as np

from music_master.instruments.percussion.drum_synthesizer import DRUM_PADS, DrumMachineEngine


@dataclass
class SequencerStep:
    active: bool = False
    velocity: float = 0.85


class DrumSequencer:
    """16-step grid sequencer driving drum engine sound generation."""

    NUM_STEPS = 16

    def __init__(
        self,
        drum_engine: DrumMachineEngine,
        bpm: float = 120.0,
        sample_rate: int = 44100,
    ) -> None:
        self.drum_engine = drum_engine
        self.sample_rate = sample_rate
        self.bpm = bpm
        self.is_playing: bool = False

        # Grid: pad_id -> list of 16 steps
        self.grid: Dict[str, List[SequencerStep]] = {
            pad.id: [SequencerStep() for _ in range(self.NUM_STEPS)] for pad in DRUM_PADS
        }

        self.current_step: int = 0
        self.samples_per_step: int = int((60.0 / self.bpm / 4.0) * self.sample_rate)
        self.sample_counter: int = 0
        self.step_callback: Optional[Callable[[int], None]] = None

        self._load_default_pattern()

    def set_bpm(self, bpm: float) -> None:
        self.bpm = max(30.0, min(300.0, bpm))
        self.samples_per_step = max(1, int((60.0 / self.bpm / 4.0) * self.sample_rate))

    def play(self) -> None:
        self.is_playing = True
        self.sample_counter = 0

    def pause(self) -> None:
        self.is_playing = False

    def stop(self) -> None:
        self.is_playing = False
        self.current_step = 0
        self.sample_counter = 0
        if self.step_callback:
            self.step_callback(0)

    def toggle_step(self, pad_id: str, step_idx: int) -> bool:
        if pad_id in self.grid and 0 <= step_idx < self.NUM_STEPS:
            self.grid[pad_id][step_idx].active = not self.grid[pad_id][step_idx].active
            return self.grid[pad_id][step_idx].active
        return False

    def set_step(self, pad_id: str, step_idx: int, active: bool, velocity: float = 0.85) -> None:
        if pad_id in self.grid and 0 <= step_idx < self.NUM_STEPS:
            self.grid[pad_id][step_idx].active = active
            self.grid[pad_id][step_idx].velocity = max(0.0, min(1.0, velocity))

    def clear_pattern(self) -> None:
        for pad_id in self.grid:
            for step in self.grid[pad_id]:
                step.active = False

    def _load_default_pattern(self) -> None:
        """Loads a classic four-on-the-floor electro/rock pattern."""
        self.clear_pattern()
        # Four on floor Kick: 0, 4, 8, 12
        for step in [0, 4, 8, 12]:
            self.set_step("kick", step, True, 0.95)
        # Snare / Clap on 4 and 12
        self.set_step("snare", 4, True, 0.85)
        self.set_step("snare", 12, True, 0.85)
        self.set_step("clap", 12, True, 0.75)
        # Closed Hi-Hat on eighth notes: 0, 2, 4, 6, 8, 10, 12, 14
        for step in range(0, 16, 2):
            self.set_step("hihat_closed", step, True, 0.65)
        # Open Hi-Hat off-beat: 6, 14
        self.set_step("hihat_open", 6, True, 0.70)
        self.set_step("hihat_open", 14, True, 0.70)

    def load_preset(self, preset_name: str) -> None:
        self.clear_pattern()
        if preset_name == "rock":
            for s in [0, 6, 8]:
                self.set_step("kick", s, True, 0.9)
            for s in [4, 12]:
                self.set_step("snare", s, True, 0.9)
            for s in range(0, 16, 2):
                self.set_step("hihat_closed", s, True, 0.7)
            self.set_step("crash", 0, True, 0.75)
        elif preset_name == "hiphop":
            for s in [0, 3, 10]:
                self.set_step("kick", s, True, 0.95)
            for s in [4, 12]:
                self.set_step("snare", s, True, 0.9)
                self.set_step("clap", s, True, 0.6)
            for s in range(16):
                self.set_step("hihat_closed", s, True, 0.6 if s % 2 == 0 else 0.4)
            self.set_step("hihat_open", 14, True, 0.65)
        elif preset_name == "house":
            for s in [0, 4, 8, 12]:
                self.set_step("kick", s, True, 0.95)
            for s in [4, 12]:
                self.set_step("clap", s, True, 0.85)
            for s in [2, 6, 10, 14]:
                self.set_step("hihat_open", s, True, 0.8)
            for s in range(0, 16, 2):
                self.set_step("hihat_closed", s, True, 0.5)
        else:
            self._load_default_pattern()

    def process_frames(self, num_frames: int) -> np.ndarray:
        """Processes clock timing, triggers steps when step boundary is crossed, and renders drum audio."""
        if not self.is_playing:
            return self.drum_engine.render_block(num_frames)

        frames_left = num_frames
        total_audio = np.zeros(num_frames, dtype=np.float32)
        offset = 0

        while frames_left > 0:
            frames_until_step = self.samples_per_step - self.sample_counter
            if frames_until_step <= frames_left:
                # Render up to step boundary
                if frames_until_step > 0:
                    total_audio[offset : offset + frames_until_step] = (
                        self.drum_engine.render_block(frames_until_step)
                    )
                    offset += frames_until_step
                    frames_left -= frames_until_step

                # Trigger current step
                for pad_id, steps in self.grid.items():
                    step = steps[self.current_step]
                    if step.active:
                        self.drum_engine.trigger_pad(pad_id, velocity=step.velocity)

                # Callback for UI step cursor
                if self.step_callback:
                    self.step_callback(self.current_step)

                # Advance step
                self.current_step = (self.current_step + 1) % self.NUM_STEPS
                self.sample_counter = 0
            else:
                # Render rest of buffer
                total_audio[offset : offset + frames_left] = self.drum_engine.render_block(
                    frames_left
                )
                self.sample_counter += frames_left
                frames_left = 0

        return total_audio
