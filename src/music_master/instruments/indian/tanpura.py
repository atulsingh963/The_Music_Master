"""Tanpura continuous multi-string drone acoustic synthesis engine."""

import math
from typing import List

import numpy as np


class TanpuraDroneEngine:
    """Acoustically synthesizes authentic continuous 4-string Tanpura drone.

    Standard Hindustani Tanpura string patterns:
    - First string: Pa (Pancham, ratio 1.5) or Ma (Teevra/Shuddha Ma) or Ni (Nishad)
    - Second string: Sa (Tara Sa, octave higher, ratio 2.0)
    - Third string: Sa (Tara Sa, octave higher, ratio 2.0)
    - Fourth string: Sa (Mandra Sa / Kharaj, root tonic, ratio 1.0)

    Includes the characteristic 'Javari' thread buzzing overtone spectrum.
    """

    def __init__(
        self,
        sample_rate: int = 44100,
        tonic_midi: int = 48,  # C3 base Kharaj
        pattern_type: str = "pa",  # "pa", "ma", or "ni"
        tempo_bpm: float = 24.0,  # Pluck cycle speed (approx 1 pluck every 2.5s)
    ) -> None:
        self.sample_rate = sample_rate
        self.tonic_midi = tonic_midi
        self.pattern_type = pattern_type
        self.tempo_bpm = max(10.0, min(60.0, tempo_bpm))
        self.volume = 0.75
        self.is_active = False

        # Internal sequencer state
        self.current_string_index = 0
        self.samples_per_pluck = int((60.0 / self.tempo_bpm) * self.sample_rate)
        self.sample_counter = 0

        # Active string audio voices
        self._active_plucks: List[_TanpuraPluck] = []

    def set_tonic(self, midi_note: int) -> None:
        self.tonic_midi = max(36, min(72, midi_note))

    def set_pattern(self, pattern_type: str) -> None:
        if pattern_type.lower() in ("pa", "ma", "ni"):
            self.pattern_type = pattern_type.lower()

    def set_tempo(self, bpm: float) -> None:
        self.tempo_bpm = max(10.0, min(60.0, bpm))
        self.samples_per_pluck = max(1, int((60.0 / self.tempo_bpm) * self.sample_rate))

    def set_volume(self, volume: float) -> None:
        self.volume = max(0.0, min(1.0, volume))

    def start(self) -> None:
        self.is_active = True
        self.current_string_index = 0
        self.sample_counter = 0
        self._trigger_next_string()

    def stop(self) -> None:
        self.is_active = False
        self._active_plucks.clear()

    def _get_string_frequency(self, string_idx: int) -> float:
        base_freq = 440.0 * (2.0 ** ((self.tonic_midi - 69) / 12.0))
        # String 0: First string (Pa, Ma, or Ni)
        if string_idx == 0:
            if self.pattern_type == "pa":
                return base_freq * 1.5  # Pa
            elif self.pattern_type == "ma":
                return base_freq * (4.0 / 3.0)  # Shuddha Ma
            else:
                return base_freq * (15.0 / 8.0)  # Shuddha Ni (in mandra/middle)
        # Strings 1 and 2: Jodi strings (Middle Sa)
        elif string_idx in (1, 2):
            return base_freq * 2.0  # Middle Sa (octave above base Kharaj)
        # String 3: Kharaj (Root Sa)
        else:
            return base_freq * 1.0

    def _trigger_next_string(self) -> None:
        freq = self._get_string_frequency(self.current_string_index)
        pluck = _TanpuraPluck(freq=freq, sample_rate=self.sample_rate)
        self._active_plucks.append(pluck)

        # Move to next string in the 4-string cycle
        self.current_string_index = (self.current_string_index + 1) % 4

    def render_block(self, num_frames: int) -> np.ndarray:
        output = np.zeros(num_frames, dtype=np.float32)
        if not self.is_active:
            return output

        # Render active string resonances
        surviving = []
        for pluck in self._active_plucks:
            output += pluck.render(num_frames)
            if not pluck.is_dead:
                surviving.append(pluck)
        self._active_plucks = surviving

        # Advance string sequence timing
        self.sample_counter += num_frames
        while self.sample_counter >= self.samples_per_pluck:
            self.sample_counter -= self.samples_per_pluck
            self._trigger_next_string()

        output *= self.volume
        return output


class _TanpuraPluck:
    """Single plucked tanpura string simulation with rich Javari thread resonance."""

    def __init__(self, freq: float, sample_rate: int) -> None:
        self.freq = freq
        self.sample_rate = sample_rate
        self.phase = 0.0
        self.phase_step = (2.0 * math.pi * self.freq) / self.sample_rate

        self.duration_seconds = 7.0  # Long sustained resonance
        self.total_frames = int(self.duration_seconds * self.sample_rate)
        self.current_frame = 0
        self.is_dead = False

        # Javari bridge overtone spectrum (broad harmonic content)
        self.harmonics = [
            (1.0, 0.40),
            (2.0, 0.28),
            (3.0, 0.22),
            (4.0, 0.15),
            (5.0, 0.12),
            (6.0, 0.09),
            (7.0, 0.06),
            (8.0, 0.04),
        ]

    def render(self, num_frames: int) -> np.ndarray:
        if self.is_dead:
            return np.zeros(num_frames, dtype=np.float32)

        frames_to_render = min(num_frames, self.total_frames - self.current_frame)
        t = np.arange(frames_to_render, dtype=np.float64)
        phases = self.phase + t * self.phase_step
        self.phase = (phases[-1] + self.phase_step) % (2.0 * math.pi)

        # String tone
        signal = np.zeros(frames_to_render, dtype=np.float64)
        for h_mult, h_weight in self.harmonics:
            signal += h_weight * np.sin(phases * h_mult)

        # Decay envelope: gentle pluck attack, slow exponential decay with shimmer
        time_sec = (self.current_frame + t) / float(self.sample_rate)
        env = np.exp(-time_sec * 0.65) * (1.0 - np.exp(-time_sec * 50.0))

        # Modulating Javari swirl
        shimmer = 1.0 + 0.08 * np.sin(2.0 * math.pi * 3.5 * time_sec)
        pluck_audio = (signal * env * shimmer).astype(np.float32)

        self.current_frame += frames_to_render
        if self.current_frame >= self.total_frames:
            self.is_dead = True

        if frames_to_render < num_frames:
            pad = np.zeros(num_frames - frames_to_render, dtype=np.float32)
            return np.concatenate((pluck_audio, pad))

        return pluck_audio
