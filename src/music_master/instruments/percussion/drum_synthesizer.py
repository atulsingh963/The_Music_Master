"""Percussion sound synthesizers and drum voice generators."""

import math
from dataclasses import dataclass
from typing import Dict, List

import numpy as np


@dataclass
class DrumPadDefinition:
    id: str
    name: str
    midi_note: int  # Standard General MIDI drum note
    category: str  # "kick", "snare", "hihat", "clap", "tom", "rim", "crash"
    decay: float  # seconds


DRUM_PADS: List[DrumPadDefinition] = [
    DrumPadDefinition(id="kick", name="Kick Drum", midi_note=36, category="kick", decay=0.45),
    DrumPadDefinition(id="rim", name="Rimshot", midi_note=37, category="rim", decay=0.10),
    DrumPadDefinition(id="snare", name="Snare Drum", midi_note=38, category="snare", decay=0.30),
    DrumPadDefinition(id="clap", name="Hand Clap", midi_note=39, category="clap", decay=0.25),
    DrumPadDefinition(id="tom_low", name="Low Tom", midi_note=45, category="tom", decay=0.40),
    DrumPadDefinition(
        id="hihat_closed", name="Closed Hat", midi_note=42, category="hihat", decay=0.08
    ),
    DrumPadDefinition(id="tom_mid", name="Mid Tom", midi_note=47, category="tom", decay=0.35),
    DrumPadDefinition(id="hihat_open", name="Open Hat", midi_note=46, category="hihat", decay=0.40),
    DrumPadDefinition(id="tom_high", name="High Tom", midi_note=50, category="tom", decay=0.30),
    DrumPadDefinition(id="crash", name="Crash Cymbal", midi_note=49, category="crash", decay=1.20),
]


class ActiveDrumVoice:
    """Represents an actively rendering synthesized drum voice."""

    def __init__(
        self,
        pad: DrumPadDefinition,
        velocity: float,
        sample_rate: int,
        kit_type: str = "acoustic",
        pitch_factor: float = 1.0,
    ) -> None:
        self.pad = pad
        self.velocity = max(0.0, min(1.0, velocity))
        self.sample_rate = sample_rate
        self.kit_type = kit_type
        self.pitch_factor = max(0.2, min(3.0, pitch_factor))

        self.duration_seconds = pad.decay
        self.total_frames = int(self.duration_seconds * sample_rate)
        self.current_frame = 0
        self.is_dead = False
        self.phase = 0.0

    def render(self, num_frames: int) -> np.ndarray:
        if self.is_dead:
            return np.zeros(num_frames, dtype=np.float32)

        frames_to_render = min(num_frames, self.total_frames - self.current_frame)
        t = (self.current_frame + np.arange(frames_to_render)) / float(self.sample_rate)

        category = self.pad.category
        if category == "kick":
            audio = self._render_kick(t, frames_to_render)
        elif category == "snare":
            audio = self._render_snare(t, frames_to_render)
        elif category == "hihat":
            audio = self._render_hihat(t, frames_to_render)
        elif category == "clap":
            audio = self._render_clap(t, frames_to_render)
        elif category == "tom":
            audio = self._render_tom(t, frames_to_render)
        elif category == "rim":
            audio = self._render_rim(t, frames_to_render)
        elif category == "crash":
            audio = self._render_crash(t, frames_to_render)
        else:
            audio = np.zeros(frames_to_render, dtype=np.float32)

        audio = (audio * self.velocity).astype(np.float32)

        self.current_frame += frames_to_render
        if self.current_frame >= self.total_frames:
            self.is_dead = True

        if frames_to_render < num_frames:
            pad = np.zeros(num_frames - frames_to_render, dtype=np.float32)
            return np.concatenate((audio, pad))

        return audio

    def _render_kick(self, t: np.ndarray, num_frames: int) -> np.ndarray:
        # Electronic 808/909 vs acoustic kick: rapid downward pitch glide + soft click
        if self.kit_type == "electronic":
            start_freq = 160.0 * self.pitch_factor
            end_freq = 48.0 * self.pitch_factor
            decay_rate = 7.0
        else:
            start_freq = 130.0 * self.pitch_factor
            end_freq = 55.0 * self.pitch_factor
            decay_rate = 9.0

        freq = end_freq + (start_freq - end_freq) * np.exp(-t * 28.0)
        phases = 2.0 * math.pi * np.cumsum(freq) / float(self.sample_rate) + self.phase
        self.phase = phases[-1] % (2.0 * math.pi)

        sine = np.sin(phases)
        # Add transient beater click
        click = np.random.uniform(-1.0, 1.0, num_frames) * np.exp(-t * 120.0) * 0.25
        env = np.exp(-t * decay_rate)
        # Soft saturation drive
        raw = (sine + click) * env
        return np.tanh(raw * 1.5)

    def _render_snare(self, t: np.ndarray, num_frames: int) -> np.ndarray:
        # Snare: body tone (tuned sine) + snappy white noise with bandpass/decay
        body_freq = (185.0 if self.kit_type == "electronic" else 205.0) * self.pitch_factor
        freq_env = body_freq * (1.0 + 0.5 * np.exp(-t * 40.0))
        phases = 2.0 * math.pi * np.cumsum(freq_env) / float(self.sample_rate) + self.phase
        self.phase = phases[-1] % (2.0 * math.pi)

        tone = np.sin(phases) * np.exp(-t * 18.0)
        noise = np.random.uniform(-1.0, 1.0, num_frames)
        noise_env = np.exp(-t * 14.0)
        noise_comp = noise * noise_env * 0.8
        return (tone * 0.5 + noise_comp) * 0.9

    def _render_hihat(self, t: np.ndarray, num_frames: int) -> np.ndarray:
        # Metallic cluster tones + shaped high noise
        decay_rate = 35.0 if "closed" in self.pad.id else 8.0
        noise = np.random.uniform(-1.0, 1.0, num_frames)
        # Metallic ringing square/sine mix
        f1 = 2800.0 * self.pitch_factor
        f2 = 4100.0 * self.pitch_factor
        f3 = 6200.0 * self.pitch_factor
        metal = (
            np.sin(2.0 * math.pi * f1 * t)
            + np.sin(2.0 * math.pi * f2 * t)
            + np.sin(2.0 * math.pi * f3 * t)
        ) * 0.2
        env = np.exp(-t * decay_rate)
        return (noise * 0.8 + metal) * env * 0.7

    def _render_clap(self, t: np.ndarray, num_frames: int) -> np.ndarray:
        # Hand clap: multiple short pre-bursts (rebounding hands) followed by sustained diffuse burst
        noise = np.random.uniform(-1.0, 1.0, num_frames)
        env = np.zeros(num_frames, dtype=np.float64)
        burst_offsets = [0.0, 0.012, 0.024, 0.036]
        for offset in burst_offsets:
            mask = t >= offset
            if np.any(mask):
                local_t = t[mask] - offset
                env[mask] += np.exp(-local_t * 80.0) * 0.4
        # Main sustain tail
        main_mask = t >= 0.036
        if np.any(main_mask):
            local_t = t[main_mask] - 0.036
            env[main_mask] += np.exp(-local_t * 18.0) * 0.7
        return noise * env * 0.8

    def _render_tom(self, t: np.ndarray, num_frames: int) -> np.ndarray:
        # Toms: low, mid, high tuned descending resonant sine + light skin transient
        base_f = 90.0 if "low" in self.pad.id else (135.0 if "mid" in self.pad.id else 180.0)
        base_f *= self.pitch_factor
        freq_env = base_f * (1.0 + 0.6 * np.exp(-t * 22.0))
        phases = 2.0 * math.pi * np.cumsum(freq_env) / float(self.sample_rate) + self.phase
        self.phase = phases[-1] % (2.0 * math.pi)

        skin_transient = np.random.uniform(-1.0, 1.0, num_frames) * np.exp(-t * 60.0) * 0.2
        tone = np.sin(phases) * np.exp(-t * 8.5)
        return (tone + skin_transient) * 0.85

    def _render_rim(self, t: np.ndarray, num_frames: int) -> np.ndarray:
        # High wood/metal click with rapid decay
        freq = 1100.0 * self.pitch_factor
        tone = np.sin(2.0 * math.pi * freq * t) * np.exp(-t * 70.0)
        noise = np.random.uniform(-1.0, 1.0, num_frames) * np.exp(-t * 90.0) * 0.5
        return (tone * 0.8 + noise) * 0.9

    def _render_crash(self, t: np.ndarray, num_frames: int) -> np.ndarray:
        # Wide-spectrum crash cymbal with long decaying shimmer
        noise = np.random.uniform(-1.0, 1.0, num_frames)
        f_shimmer = 5200.0 * self.pitch_factor
        shimmer = np.sin(2.0 * math.pi * f_shimmer * t) * 0.2
        env = np.exp(-t * 2.8)
        return (noise * 0.8 + shimmer) * env * 0.65


class DrumMachineEngine:
    """Drum machine engine supporting acoustic and electronic kits and polyphonic drum voices."""

    def __init__(self, sample_rate: int = 44100) -> None:
        self.sample_rate = sample_rate
        self.kit_type: str = "acoustic"  # "acoustic" or "electronic"
        self.active_voices: List[ActiveDrumVoice] = []
        self.pads_by_id: Dict[str, DrumPadDefinition] = {p.id: p for p in DRUM_PADS}
        self.pads_by_note: Dict[int, DrumPadDefinition] = {p.midi_note: p for p in DRUM_PADS}
        self.pitch_factor: float = 1.0
        self.volume: float = 0.9

    def set_kit_type(self, kit: str) -> None:
        if kit in ("acoustic", "electronic"):
            self.kit_type = kit

    def set_pitch_factor(self, factor: float) -> None:
        self.pitch_factor = max(0.5, min(2.0, factor))

    def trigger_pad(self, pad_id: str, velocity: float = 0.9) -> None:
        pad = self.pads_by_id.get(pad_id)
        if pad is not None:
            voice = ActiveDrumVoice(
                pad=pad,
                velocity=velocity,
                sample_rate=self.sample_rate,
                kit_type=self.kit_type,
                pitch_factor=self.pitch_factor,
            )
            self.active_voices.append(voice)

    def trigger_note(self, midi_note: int, velocity: float = 0.9) -> None:
        pad = self.pads_by_note.get(midi_note)
        if pad is not None:
            self.trigger_pad(pad.id, velocity=velocity)

    def stop_all(self) -> None:
        self.active_voices.clear()

    def render_block(self, num_frames: int) -> np.ndarray:
        if not self.active_voices:
            return np.zeros(num_frames, dtype=np.float32)

        output = np.zeros(num_frames, dtype=np.float32)
        surviving_voices: List[ActiveDrumVoice] = []

        for voice in self.active_voices:
            output += voice.render(num_frames)
            if not voice.is_dead:
                surviving_voices.append(voice)

        self.active_voices = surviving_voices
        return output * self.volume
