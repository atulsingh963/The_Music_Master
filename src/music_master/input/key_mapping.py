from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class KeyMapping:
    key_name: str
    midi_note_offset: int  # semitone offset from base note
    label: str  # e.g., "Sa", "Re", "C", "D"


class KeyboardProfile:
    """Represents a mapping profile between keyboard keys and musical note offsets."""

    def __init__(self, name: str, description: str, base_midi_note: int = 60) -> None:
        self.name = name
        self.description = description
        self.base_midi_note = base_midi_note
        self.mappings: Dict[str, KeyMapping] = {}

    def add_mapping(self, key: str, semitone_offset: int, label: str) -> None:
        self.mappings[key.upper()] = KeyMapping(key.upper(), semitone_offset, label)

    def get_note(self, key: str, octave_shift: int = 0, transpose_shift: int = 0) -> Optional[int]:
        mapping = self.mappings.get(key.upper())
        if mapping is None:
            return None
        midi = (
            self.base_midi_note + mapping.midi_note_offset + (octave_shift * 12) + transpose_shift
        )
        return max(0, min(127, midi))

    def get_label(self, key: str) -> Optional[str]:
        mapping = self.mappings.get(key.upper())
        return mapping.label if mapping else None


def get_harmonium_default_profile() -> KeyboardProfile:
    """Default Sargam mapping for Harmonium:
    A = Sa (C4/60)
    W = komal Re (Db4/61)
    S = Re (D4/62)
    E = komal Ga (Eb4/63)
    D = Ga (E4/64)
    F = Ma (F4/65)
    T = tivra Ma (F#4/66)
    G = Pa (G4/67)
    Y = komal Dha (Ab4/68)
    H = Dha (A4/69)
    U = komal Ni (Bb4/70)
    J = Ni (B4/71)
    K = Tar Sa (C5/72)
    O = komal Re (Db5/73)
    L = Tar Re (D5/74)
    P = komal Ga (Eb5/75)
    ; = Tar Ga (E5/76)
    """
    profile = KeyboardProfile(
        "Harmonium Sargam",
        "Standard Indian Sargam layout centered at C4 (Madhya Saptak)",
        base_midi_note=60,
    )
    # White keys / Shuddha swaras
    profile.add_mapping("A", 0, "Sa")
    profile.add_mapping("S", 2, "Re")
    profile.add_mapping("D", 4, "Ga")
    profile.add_mapping("F", 5, "Ma")
    profile.add_mapping("G", 7, "Pa")
    profile.add_mapping("H", 9, "Dha")
    profile.add_mapping("J", 11, "Ni")
    profile.add_mapping("K", 12, "Ṡa")
    profile.add_mapping("L", 14, "Ṙe")
    profile.add_mapping(";", 16, "Ġa")

    # Black keys / Vikrit swaras
    profile.add_mapping("W", 1, "re")
    profile.add_mapping("E", 3, "ga")
    profile.add_mapping("T", 6, "ma'")
    profile.add_mapping("Y", 8, "dha")
    profile.add_mapping("U", 10, "ni")
    profile.add_mapping("O", 13, "ṙe")
    profile.add_mapping("P", 15, "ġa")
    return profile


def get_piano_default_profile() -> KeyboardProfile:
    """Western keyboard layout:
    Number row: secondary octave
    Middle row (A-L): C4 to E5
    """
    profile = KeyboardProfile(
        "Piano Chromatic", "Standard western 2-octave keyboard mapping", base_midi_note=60
    )
    # Lower octave (row A-K)
    profile.add_mapping("A", 0, "C4")
    profile.add_mapping("W", 1, "C#4")
    profile.add_mapping("S", 2, "D4")
    profile.add_mapping("E", 3, "D#4")
    profile.add_mapping("D", 4, "E4")
    profile.add_mapping("F", 5, "F4")
    profile.add_mapping("T", 6, "F#4")
    profile.add_mapping("G", 7, "G4")
    profile.add_mapping("Y", 8, "G#4")
    profile.add_mapping("H", 9, "A4")
    profile.add_mapping("U", 10, "A#4")
    profile.add_mapping("J", 11, "B4")
    profile.add_mapping("K", 12, "C5")
    profile.add_mapping("O", 13, "C#5")
    profile.add_mapping("L", 14, "D5")
    profile.add_mapping("P", 15, "D#5")
    profile.add_mapping(";", 16, "E5")
    return profile
