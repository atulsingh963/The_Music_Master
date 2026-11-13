"""Algorithmic multi-harmonic synthesizer for strings, winds, brass, bass, and vocal/world instruments."""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass
class InstrumentPreset:
    """Acoustic synthesis profile specifying harmonics, envelope, and vibrato/noise parameters."""

    id: str
    name: str
    category: str
    attack_time: float
    decay_time: float
    sustain_level: float
    release_time: float
    harmonics: List[Tuple[float, float]]  # (harmonic_multiplier, relative_amplitude)
    noise_ratio: float = 0.0  # Breath / chiff / friction noise ratio
    vibrato_rate: float = 5.0  # Hz
    vibrato_depth: float = 0.0  # Semitones or frequency fraction


class AcousticSynthRegistry:
    """Defines calibrated acoustic physical synthesis presets for western and world instruments."""

    PRESETS: Dict[str, InstrumentPreset] = {
        # --- Indian & World Winds ---
        "bansuri": InstrumentPreset(
            id="bansuri",
            name="Bansuri Bamboo Flute",
            category="Indian Classical",
            attack_time=0.04,
            decay_time=0.1,
            sustain_level=0.9,
            release_time=0.18,
            harmonics=[(1.0, 0.7), (2.0, 0.22), (3.0, 0.06), (4.0, 0.02)],
            noise_ratio=0.08,  # characteristic bamboo breath
            vibrato_rate=5.5,
            vibrato_depth=0.015,
        ),
        "concert_flute": InstrumentPreset(
            id="concert_flute",
            name="Concert Flute",
            category="Wind",
            attack_time=0.03,
            decay_time=0.08,
            sustain_level=0.92,
            release_time=0.15,
            harmonics=[(1.0, 0.75), (2.0, 0.18), (3.0, 0.05), (4.0, 0.02)],
            noise_ratio=0.05,
            vibrato_rate=5.8,
            vibrato_depth=0.01,
        ),
        # --- Brass ---
        "trumpet": InstrumentPreset(
            id="trumpet",
            name="Trumpet",
            category="Wind",
            attack_time=0.025,
            decay_time=0.06,
            sustain_level=0.85,
            release_time=0.12,
            harmonics=[
                (1.0, 0.35),
                (2.0, 0.30),
                (3.0, 0.20),
                (4.0, 0.10),
                (5.0, 0.05),
            ],
            noise_ratio=0.01,
            vibrato_rate=6.0,
            vibrato_depth=0.008,
        ),
        "trombone": InstrumentPreset(
            id="trombone",
            name="Trombone",
            category="Wind",
            attack_time=0.04,
            decay_time=0.08,
            sustain_level=0.88,
            release_time=0.15,
            harmonics=[(1.0, 0.45), (2.0, 0.30), (3.0, 0.15), (4.0, 0.07), (5.0, 0.03)],
            noise_ratio=0.01,
        ),
        # --- Strings ---
        "violin": InstrumentPreset(
            id="violin",
            name="Violin",
            category="Strings",
            attack_time=0.06,
            decay_time=0.1,
            sustain_level=0.92,
            release_time=0.22,
            harmonics=[
                (1.0, 0.40),
                (2.0, 0.28),
                (3.0, 0.16),
                (4.0, 0.09),
                (5.0, 0.05),
                (6.0, 0.02),
            ],
            noise_ratio=0.03,  # bow friction
            vibrato_rate=5.5,
            vibrato_depth=0.02,
        ),
        "cello": InstrumentPreset(
            id="cello",
            name="Cello",
            category="Strings",
            attack_time=0.08,
            decay_time=0.12,
            sustain_level=0.90,
            release_time=0.28,
            harmonics=[
                (1.0, 0.48),
                (2.0, 0.26),
                (3.0, 0.14),
                (4.0, 0.08),
                (5.0, 0.04),
            ],
            noise_ratio=0.02,
            vibrato_rate=5.0,
            vibrato_depth=0.018,
        ),
        "acoustic_guitar": InstrumentPreset(
            id="acoustic_guitar",
            name="Acoustic Guitar",
            category="Strings",
            attack_time=0.008,
            decay_time=1.4,
            sustain_level=0.12,
            release_time=0.25,
            harmonics=[(1.0, 0.55), (2.0, 0.25), (3.0, 0.12), (4.0, 0.05), (5.0, 0.03)],
        ),
        "electric_guitar": InstrumentPreset(
            id="electric_guitar",
            name="Electric Guitar",
            category="Strings",
            attack_time=0.006,
            decay_time=2.0,
            sustain_level=0.25,
            release_time=0.20,
            harmonics=[(1.0, 0.40), (2.0, 0.30), (3.0, 0.18), (4.0, 0.08), (5.0, 0.04)],
        ),
        "bass_guitar": InstrumentPreset(
            id="bass_guitar",
            name="Electric Bass Guitar",
            category="Strings",
            attack_time=0.01,
            decay_time=1.8,
            sustain_level=0.20,
            release_time=0.25,
            harmonics=[(1.0, 0.70), (2.0, 0.22), (3.0, 0.06), (4.0, 0.02)],
        ),
        # --- World & Vocal ---
        "erhu": InstrumentPreset(
            id="erhu",
            name="Chinese Erhu",
            category="World",
            attack_time=0.05,
            decay_time=0.08,
            sustain_level=0.90,
            release_time=0.20,
            harmonics=[(1.0, 0.45), (2.0, 0.25), (3.0, 0.18), (4.0, 0.08), (5.0, 0.04)],
            vibrato_rate=6.2,
            vibrato_depth=0.025,
        ),
        "koto": InstrumentPreset(
            id="koto",
            name="Japanese Koto",
            category="World",
            attack_time=0.005,
            decay_time=1.2,
            sustain_level=0.08,
            release_time=0.3,
            harmonics=[(1.0, 0.50), (2.0, 0.28), (3.0, 0.14), (4.0, 0.05), (5.0, 0.03)],
        ),
        "choir": InstrumentPreset(
            id="choir",
            name="Choir Aah",
            category="Vocal and Ambient",
            attack_time=0.15,
            decay_time=0.2,
            sustain_level=0.95,
            release_time=0.45,
            harmonics=[(1.0, 0.40), (2.0, 0.35), (3.0, 0.15), (4.0, 0.08), (5.0, 0.02)],
            noise_ratio=0.04,
            vibrato_rate=4.8,
            vibrato_depth=0.015,
        ),
        "vocal_pad": InstrumentPreset(
            id="vocal_pad",
            name="Atmospheric Vocal Pad",
            category="Vocal and Ambient",
            attack_time=0.30,
            decay_time=0.3,
            sustain_level=0.98,
            release_time=0.60,
            harmonics=[(0.5, 0.2), (1.0, 0.4), (1.5, 0.2), (2.0, 0.15), (3.0, 0.05)],
            vibrato_rate=3.5,
            vibrato_depth=0.01,
        ),
    }

    @classmethod
    def get_preset(cls, instrument_id: str) -> Optional[InstrumentPreset]:
        return cls.PRESETS.get(instrument_id)
