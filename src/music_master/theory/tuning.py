"""Tuning calculations, reference standards (A440 vs custom), Just Intonation, and Indian Shrutis."""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class TuningSystem:
    id: str
    name: str
    description: str
    ratios: List[float]  # Frequency ratios for the 12 chromatic degrees relative to root (1.0)


# Standard 12-TET (Twelve-Tone Equal Temperament)
TET_12_RATIOS = [2.0 ** (i / 12.0) for i in range(12)]

# Just Intonation (5-limit Ptolemaic scale)
JUST_INTONATION_RATIOS = [
    1.0,  # Unison (1/1)
    16.0 / 15.0,  # Minor second (16/15)
    9.0 / 8.0,  # Major second (9/8)
    6.0 / 5.0,  # Minor third (6/5)
    5.0 / 4.0,  # Major third (5/4)
    4.0 / 3.0,  # Perfect fourth (4/3)
    45.0 / 32.0,  # Augmented fourth / Tritone (45/32)
    3.0 / 2.0,  # Perfect fifth (3/2)
    8.0 / 5.0,  # Minor sixth (8/5)
    5.0 / 3.0,  # Major sixth (5/3)
    9.0 / 5.0,  # Minor seventh (9/5)
    15.0 / 8.0,  # Major seventh (15/8)
]

# Indian 22-Shruti system (Gandharva/Bharata ratios for 12 selected swaras)
INDIAN_SHRUTI_12_RATIOS = [
    1.0,  # Sa (Shadja) 1/1
    256.0 / 243.0,  # Komal Rishabh (Komal Re)
    9.0 / 8.0,  # Shuddha Rishabh (Re)
    32.0 / 27.0,  # Komal Gandhar (Komal Ga)
    5.0 / 4.0,  # Shuddha Gandhar (Ga)
    4.0 / 3.0,  # Shuddha Madhyam (Ma)
    45.0 / 32.0,  # Tivra Madhyam (Tivra Ma)
    3.0 / 2.0,  # Pancham (Pa)
    128.0 / 81.0,  # Komal Dhaivat (Komal Dha)
    5.0 / 3.0,  # Shuddha Dhaivat (Dha)
    16.0 / 9.0,  # Komal Nishad (Komal Ni)
    15.0 / 8.0,  # Shuddha Nishad (Ni)
]

# Pythagorean Tuning (pure 3:2 fifths)
PYTHAGOREAN_RATIOS = [
    1.0,
    256.0 / 243.0,
    9.0 / 8.0,
    32.0 / 27.0,
    81.0 / 64.0,
    4.0 / 3.0,
    729.0 / 512.0,
    3.0 / 2.0,
    128.0 / 81.0,
    27.0 / 16.0,
    16.0 / 9.0,
    243.0 / 128.0,
]

TUNING_SYSTEMS: Dict[str, TuningSystem] = {
    "12-tet": TuningSystem(
        "12-tet",
        "12-Tone Equal Temperament",
        "Standard modern tuning dividing octave into 12 logarithmic equal semitones.",
        TET_12_RATIOS,
    ),
    "just_intonation": TuningSystem(
        "just_intonation",
        "Just Intonation (5-Limit)",
        "Acoustically pure intervals based on small integer frequency ratios.",
        JUST_INTONATION_RATIOS,
    ),
    "indian_shruti": TuningSystem(
        "indian_shruti",
        "Indian 22-Shruti Selection",
        "Traditional natural harmonic ratios used for Hindustani and Carnatic swaras.",
        INDIAN_SHRUTI_12_RATIOS,
    ),
    "pythagorean": TuningSystem(
        "pythagorean",
        "Pythagorean Tuning",
        "System based on a cycle of acoustically pure fifths (ratio 3:2).",
        PYTHAGOREAN_RATIOS,
    ),
}


class TuningEngine:
    """Calculates exact frequencies for MIDI notes based on A4 reference and tuning system."""

    def __init__(
        self,
        reference_pitch: float = 440.0,
        system_id: str = "12-tet",
        tonic_midi: int = 60,  # Middle C
    ) -> None:
        self.reference_pitch = reference_pitch
        self.system_id = system_id
        self.tonic_midi = tonic_midi
        self.tuning_system = TUNING_SYSTEMS.get(system_id, TUNING_SYSTEMS["12-tet"])

    def set_reference_pitch(self, pitch_hz: float) -> None:
        if 400.0 <= pitch_hz <= 480.0:
            self.reference_pitch = pitch_hz

    def set_system(self, system_id: str) -> None:
        if system_id in TUNING_SYSTEMS:
            self.system_id = system_id
            self.tuning_system = TUNING_SYSTEMS[system_id]

    def set_tonic(self, tonic_midi: int) -> None:
        self.tonic_midi = tonic_midi

    def get_frequency(self, midi_note: int) -> float:
        """Calculates precise frequency in Hz for given MIDI note under active tuning."""
        if self.system_id == "12-tet":
            # Standard formula: f = A4 * 2^((midi - 69) / 12)
            return float(self.reference_pitch * (2.0 ** ((midi_note - 69) / 12.0)))

        # For temperaments with fixed key center / ratios relative to tonic:
        # Calculate tonic frequency in 12-TET relative to reference_pitch
        tonic_freq = self.reference_pitch * (2.0 ** ((self.tonic_midi - 69) / 12.0))
        semitone_offset = midi_note - self.tonic_midi
        octave = semitone_offset // 12
        degree = semitone_offset % 12

        ratio = self.tuning_system.ratios[degree]
        return float(tonic_freq * (2.0**octave) * ratio)
