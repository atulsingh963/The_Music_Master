"""Western chord structures, chord types, inversions, and Roman numeral harmonic analysis."""

from dataclasses import dataclass
from typing import Dict, List, Optional

from music_master.theory.notes import NOTE_NAMES


@dataclass
class ChordFormula:
    name: str
    symbol: str
    intervals: List[int]  # Semitones from root
    quality: str  # major, minor, diminished, augmented, dominant, suspended


CHORD_FORMULAS: Dict[str, ChordFormula] = {
    "maj": ChordFormula("Major Triad", "", [0, 4, 7], "major"),
    "min": ChordFormula("Minor Triad", "m", [0, 3, 7], "minor"),
    "dim": ChordFormula("Diminished Triad", "dim", [0, 3, 6], "diminished"),
    "aug": ChordFormula("Augmented Triad", "aug", [0, 4, 8], "augmented"),
    "sus2": ChordFormula("Suspended 2nd", "sus2", [0, 2, 7], "suspended"),
    "sus4": ChordFormula("Suspended 4th", "sus4", [0, 5, 7], "suspended"),
    "7": ChordFormula("Dominant 7th", "7", [0, 4, 7, 10], "dominant"),
    "maj7": ChordFormula("Major 7th", "maj7", [0, 4, 7, 11], "major"),
    "min7": ChordFormula("Minor 7th", "m7", [0, 3, 7, 10], "minor"),
    "m7b5": ChordFormula("Half-Diminished 7th", "m7b5", [0, 3, 6, 10], "diminished"),
    "dim7": ChordFormula("Diminished 7th", "dim7", [0, 3, 6, 9], "diminished"),
    "add9": ChordFormula("Added 9th", "add9", [0, 4, 7, 14], "major"),
    "9": ChordFormula("Dominant 9th", "9", [0, 4, 7, 10, 14], "dominant"),
}


@dataclass
class Chord:
    root: str
    formula: ChordFormula
    inversion: int = 0  # 0 = root, 1 = 1st, 2 = 2nd, etc.

    @property
    def name(self) -> str:
        inv_str = f" / {self.notes[0]}" if self.inversion > 0 else ""
        return f"{self.root}{self.formula.symbol}{inv_str}"

    @property
    def notes(self) -> List[str]:
        root_idx = NOTE_NAMES.index(self.root.upper().strip())
        raw_notes = [NOTE_NAMES[(root_idx + interval) % 12] for interval in self.formula.intervals]
        if self.inversion == 0:
            return raw_notes
        inv = self.inversion % len(raw_notes)
        return raw_notes[inv:] + raw_notes[:inv]

    def get_midi_notes(self, root_midi: int = 60) -> List[int]:
        """Calculates MIDI note numbers applying root position and inversion shifts."""
        base_midi_notes = [root_midi + interval for interval in self.formula.intervals]
        if self.inversion == 0:
            return sorted(base_midi_notes)

        inv = self.inversion % len(base_midi_notes)
        # Invert: shift lower voices up by one octave (12 semitones)
        inverted = []
        for i, midi in enumerate(base_midi_notes):
            if i < inv:
                inverted.append(midi + 12)
            else:
                inverted.append(midi)
        return sorted(inverted)


def create_chord(root: str, chord_type: str = "maj", inversion: int = 0) -> Optional[Chord]:
    """Factory to create a chord instance by root note and type symbol."""
    root_clean = root.upper().strip()
    if root_clean not in NOTE_NAMES:
        return None
    type_clean = chord_type.strip().lower()
    formula = CHORD_FORMULAS.get(type_clean)
    if not formula:
        return None
    return Chord(root=root_clean, formula=formula, inversion=inversion)
