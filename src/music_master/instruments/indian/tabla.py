"""Tabla acoustic physical modeling synthesis engine (Dayan & Bayan bols)."""

import math
from dataclasses import dataclass
from typing import Dict, List

import numpy as np


@dataclass
class TablaBolDefinition:
    id: str
    name: str
    drum: str  # "dayan" (treble drum), "bayan" (bass drum), or "both" (joint bol)
    base_freq: float  # Base resonant pitch
    pitch_bend: float  # Pitch glide amount (+/- Hz or curve)
    damping: float  # Decay factor (higher = shorter decay)
    noise_ratio: float  # Percussive slap noise fraction
    harmonic_weights: List[float]  # Overtones (Syahi harmonic mode weights)
    default_midi_key: int  # Standard MIDI/Virtual keyboard trigger note


# Acoustic physical modeling parameters for the core authentic Tabla bols
BOL_DEFINITIONS: Dict[str, TablaBolDefinition] = {
    # Joint / Open bols (Dayan + Bayan simultaneously)
    "dha": TablaBolDefinition(
        id="dha",
        name="Dha",
        drum="both",
        base_freq=145.0,
        pitch_bend=25.0,  # Bayan modulation glide
        damping=6.0,
        noise_ratio=0.08,
        harmonic_weights=[0.6, 0.4, 0.25, 0.15],
        default_midi_key=60,  # C4
    ),
    "dhin": TablaBolDefinition(
        id="dhin",
        name="Dhin",
        drum="both",
        base_freq=150.0,
        pitch_bend=20.0,
        damping=7.0,
        noise_ratio=0.05,
        harmonic_weights=[0.65, 0.35, 0.2, 0.1],
        default_midi_key=62,  # D4
    ),
    # Bayan (Bass drum / Dagga) individual bols
    "ge": TablaBolDefinition(
        id="ge",
        name="Ge (Ghe)",
        drum="bayan",
        base_freq=95.0,
        pitch_bend=30.0,  # Bass modulation slide with palm pressure
        damping=5.0,
        noise_ratio=0.03,
        harmonic_weights=[0.8, 0.2, 0.08],
        default_midi_key=64,  # E4
    ),
    "ke": TablaBolDefinition(
        id="ke",
        name="Ke (Ka / Kat)",
        drum="bayan",
        base_freq=120.0,
        pitch_bend=0.0,
        damping=35.0,  # Closed flat slap, deadened decay
        noise_ratio=0.60,
        harmonic_weights=[0.3, 0.1],
        default_midi_key=65,  # F4
    ),
    # Dayan (Right-hand treble drum) individual bols
    "na": TablaBolDefinition(
        id="na",
        name="Na (Ta)",
        drum="dayan",
        base_freq=293.66,  # D4 tuned Dayan rim strike (Kinhar/Chat)
        pitch_bend=0.0,
        damping=14.0,
        noise_ratio=0.18,
        harmonic_weights=[0.5, 0.4, 0.2, 0.15],
        default_midi_key=67,  # G4
    ),
    "tin": TablaBolDefinition(
        id="tin",
        name="Tin",
        drum="dayan",
        base_freq=293.66,
        pitch_bend=0.0,
        damping=10.0,  # Resonant ringing strike on Sur
        noise_ratio=0.06,
        harmonic_weights=[0.7, 0.3, 0.1],
        default_midi_key=69,  # A4
    ),
    "ti": TablaBolDefinition(
        id="ti",
        name="Ti (Te)",
        drum="dayan",
        base_freq=260.0,
        pitch_bend=0.0,
        damping=40.0,  # Closed center strike on Syahi (deadened)
        noise_ratio=0.45,
        harmonic_weights=[0.2, 0.1],
        default_midi_key=71,  # B4
    ),
    "ra": TablaBolDefinition(
        id="ra",
        name="Ra",
        drum="dayan",
        base_freq=250.0,
        pitch_bend=0.0,
        damping=38.0,
        noise_ratio=0.40,
        harmonic_weights=[0.2, 0.1],
        default_midi_key=72,  # C5
    ),
    "tu": TablaBolDefinition(
        id="tu",
        name="Tu (Tun)",
        drum="dayan",
        base_freq=293.66,
        pitch_bend=0.0,
        damping=8.0,  # Open singing resonant strike on central Syahi
        noise_ratio=0.04,
        harmonic_weights=[0.75, 0.3, 0.15],
        default_midi_key=74,  # D5
    ),
}


class TablaSynthesizer:
    """Synthesizes tabla strikes dynamically using modal membrane and cavity simulation."""

    def __init__(self, sample_rate: int = 44100, dayan_pitch_hz: float = 293.66) -> None:
        self.sample_rate = sample_rate
        self.dayan_pitch_hz = dayan_pitch_hz
        self._active_sounds: List[_TablaHit] = []

    def set_dayan_pitch(self, pitch_hz: float) -> None:
        """Tunes the fundamental pitch of the Dayan treble drum."""
        if 180.0 <= pitch_hz <= 440.0:
            self.dayan_pitch_hz = pitch_hz

    def trigger_bol(self, bol_id: str, velocity: float = 0.9) -> None:
        """Trigger a tabla stroke by bol identifier."""
        bol_def = BOL_DEFINITIONS.get(bol_id.lower())
        if not bol_def:
            return

        hit = _TablaHit(
            bol=bol_def,
            velocity=max(0.1, min(1.0, velocity)),
            dayan_tuned_pitch=self.dayan_pitch_hz,
            sample_rate=self.sample_rate,
        )
        self._active_sounds.append(hit)

    def render_block(self, num_frames: int) -> np.ndarray:
        output = np.zeros(num_frames, dtype=np.float32)
        surviving = []
        for hit in self._active_sounds:
            output += hit.render(num_frames)
            if not hit.is_dead:
                surviving.append(hit)
        self._active_sounds = surviving
        return output


class _TablaHit:
    """Renders a single percussion strike based on membrane acoustics."""

    def __init__(
        self,
        bol: TablaBolDefinition,
        velocity: float,
        dayan_tuned_pitch: float,
        sample_rate: int,
    ) -> None:
        self.bol = bol
        self.velocity = velocity
        self.sample_rate = sample_rate

        # Calibrate base frequency: if Dayan, scale relative to Dayan pitch
        if bol.drum in ("dayan", "both"):
            self.freq = dayan_tuned_pitch if bol.drum == "dayan" else bol.base_freq
        else:
            self.freq = bol.base_freq

        self.duration_seconds = 1.2
        self.total_frames = int(self.duration_seconds * sample_rate)
        self.current_frame = 0
        self.is_dead = False
        self.phase = 0.0

    def render(self, num_frames: int) -> np.ndarray:
        if self.is_dead:
            return np.zeros(num_frames, dtype=np.float32)

        frames_to_render = min(num_frames, self.total_frames - self.current_frame)
        t = (self.current_frame + np.arange(frames_to_render)) / float(self.sample_rate)

        # Bayan frequency pitch modulation (characteristic upward/downward bend)
        freq_curve = self.freq + self.bol.pitch_bend * np.exp(-t * 12.0)
        phases = 2.0 * math.pi * np.cumsum(freq_curve) / float(self.sample_rate) + self.phase
        self.phase = phases[-1] % (2.0 * math.pi)

        # Modal harmonic ring (Syahi tuned circular membrane modes)
        tonal = np.zeros(frames_to_render, dtype=np.float64)
        for idx, weight in enumerate(self.bol.harmonic_weights):
            harmonic_multiplier = 1.0 + idx * 0.98  # Near-harmonic circular membrane modes
            tonal += weight * np.sin(phases * harmonic_multiplier)

        # Slap noise transient
        noise = np.random.uniform(-1.0, 1.0, frames_to_render)
        noise_env = np.exp(-t * 60.0)
        noise_component = noise * noise_env * self.bol.noise_ratio

        # Amplitude decay envelope
        decay = np.exp(-t * self.bol.damping)
        audio = (
            (tonal * (1.0 - self.bol.noise_ratio) + noise_component) * decay * self.velocity
        ).astype(np.float32)

        self.current_frame += frames_to_render
        if self.current_frame >= self.total_frames:
            self.is_dead = True

        if frames_to_render < num_frames:
            pad = np.zeros(num_frames - frames_to_render, dtype=np.float32)
            return np.concatenate((audio, pad))

        return audio
