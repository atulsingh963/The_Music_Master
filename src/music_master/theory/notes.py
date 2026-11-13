from dataclasses import dataclass
from typing import List


@dataclass
class Swara:
    name: str  # e.g., "Sa", "Re", "Ga"
    semitone: int  # 0 to 11 relative to tonic
    is_vikrit: bool  # True for komal/tivra
    western_note: str  # e.g. "C", "Db", "D"


SWARAS: List[Swara] = [
    Swara("Sa", 0, False, "C"),
    Swara("re (komal)", 1, True, "C#"),
    Swara("Re", 2, False, "D"),
    Swara("ga (komal)", 3, True, "D#"),
    Swara("Ga", 4, False, "E"),
    Swara("Ma", 5, False, "F"),
    Swara("ma' (tivra)", 6, True, "F#"),
    Swara("Pa", 7, False, "G"),
    Swara("dha (komal)", 8, True, "G#"),
    Swara("Dha", 9, False, "A"),
    Swara("ni (komal)", 10, True, "A#"),
    Swara("Ni", 11, False, "B"),
]

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def midi_to_note_name(midi_note: int) -> str:
    """Returns Western note name with octave, e.g. 60 -> 'C4'."""
    note = NOTE_NAMES[midi_note % 12]
    octave = (midi_note // 12) - 1
    return f"{note}{octave}"


def midi_to_swara(midi_note: int, tonic_midi: int = 60) -> str:
    """Returns Sargam swara name relative to tonic."""
    semitone = (midi_note - tonic_midi) % 12
    saptak_shift = (midi_note - tonic_midi) // 12

    base_name = SWARAS[semitone].name
    if saptak_shift > 0:
        return f"Ṡ{base_name[1:]}" if len(base_name) > 1 else f"Ṡ{base_name}"  # Tara saptak
    elif saptak_shift < 0:
        return f"Ṣ{base_name[1:]}" if len(base_name) > 1 else f"Ṣ{base_name}"  # Mandra saptak
    return base_name
