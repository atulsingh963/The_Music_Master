"""Western and Indian scale representations, interval calculations, and scale generator."""

from dataclasses import dataclass
from typing import Dict, List, Optional

from music_master.theory.notes import NOTE_NAMES


@dataclass
class ScaleDefinition:
    id: str
    name: str
    category: str  # Western / Indian Thaat / Exotic
    intervals: List[int]  # Semitone offsets from tonic, e.g. [0, 2, 4, 5, 7, 9, 11]
    description: str = ""

    def get_notes(self, root_note: str = "C") -> List[str]:
        """Returns the list of pitch names for this scale from the given root note."""
        clean_root = root_note.upper().strip()
        if clean_root not in NOTE_NAMES:
            raise ValueError(f"Invalid root note: {root_note}")
        root_idx = NOTE_NAMES.index(clean_root)
        return [NOTE_NAMES[(root_idx + interval) % 12] for interval in self.intervals]

    def get_midi_notes(self, root_midi: int = 60, octaves: int = 1) -> List[int]:
        """Returns MIDI note numbers spanning the requested number of octaves."""
        notes = []
        for oct_idx in range(octaves):
            base = root_midi + (oct_idx * 12)
            for interval in self.intervals:
                notes.append(base + interval)
        # Add finishing tonic at the top
        notes.append(root_midi + (octaves * 12))
        return sorted(list(set(notes)))

    def contains_midi(self, root_midi: int, check_midi: int) -> bool:
        """Checks if a given MIDI note is in this scale."""
        semitone = (check_midi - root_midi) % 12
        return semitone in self.intervals


# Standard Western Scales
WESTERN_SCALES: Dict[str, ScaleDefinition] = {
    "major": ScaleDefinition(
        id="major",
        name="Major (Ionian)",
        category="Western",
        intervals=[0, 2, 4, 5, 7, 9, 11],
        description="Standard diatonic major scale (W-W-H-W-W-W-H).",
    ),
    "natural_minor": ScaleDefinition(
        id="natural_minor",
        name="Natural Minor (Aeolian)",
        category="Western",
        intervals=[0, 2, 3, 5, 7, 8, 10],
        description="Standard natural minor scale (W-H-W-W-H-W-W).",
    ),
    "harmonic_minor": ScaleDefinition(
        id="harmonic_minor",
        name="Harmonic Minor",
        category="Western",
        intervals=[0, 2, 3, 5, 7, 8, 11],
        description="Minor scale with raised 7th leading tone.",
    ),
    "melodic_minor": ScaleDefinition(
        id="melodic_minor",
        name="Melodic Minor (Ascending)",
        category="Western",
        intervals=[0, 2, 3, 5, 7, 9, 11],
        description="Jazz melodic minor scale with raised 6th and 7th.",
    ),
    "pentatonic_major": ScaleDefinition(
        id="pentatonic_major",
        name="Pentatonic Major",
        category="Western",
        intervals=[0, 2, 4, 7, 9],
        description="5-note major scale omitting degrees 4 and 7.",
    ),
    "pentatonic_minor": ScaleDefinition(
        id="pentatonic_minor",
        name="Pentatonic Minor",
        category="Western",
        intervals=[0, 3, 5, 7, 10],
        description="5-note blues/minor scale omitting degrees 2 and 6.",
    ),
    "blues": ScaleDefinition(
        id="blues",
        name="Blues Scale",
        category="Western",
        intervals=[0, 3, 5, 6, 7, 10],
        description="Hexatonic minor pentatonic scale plus flattened fifth (blue note).",
    ),
    "chromatic": ScaleDefinition(
        id="chromatic",
        name="Chromatic",
        category="Western",
        intervals=list(range(12)),
        description="All 12 equal temperament semitones.",
    ),
    "dorian": ScaleDefinition(
        id="dorian",
        name="Dorian Mode",
        category="Western",
        intervals=[0, 2, 3, 5, 7, 9, 10],
        description="Second mode of the major scale (natural 6th).",
    ),
    "mixolydian": ScaleDefinition(
        id="mixolydian",
        name="Mixolydian Mode",
        category="Western",
        intervals=[0, 2, 4, 5, 7, 9, 10],
        description="Fifth mode of the major scale (flat 7th).",
    ),
    "phrygian": ScaleDefinition(
        id="phrygian",
        name="Phrygian Mode",
        category="Western",
        intervals=[0, 1, 3, 5, 7, 8, 10],
        description="Third mode of the major scale (flat 2nd).",
    ),
    "lydian": ScaleDefinition(
        id="lydian",
        name="Lydian Mode",
        category="Western",
        intervals=[0, 2, 4, 6, 7, 9, 11],
        description="Fourth mode of the major scale (raised 4th).",
    ),
    "locrian": ScaleDefinition(
        id="locrian",
        name="Locrian Mode",
        category="Western",
        intervals=[0, 1, 3, 5, 6, 8, 10],
        description="Seventh mode of the major scale (diminished 5th).",
    ),
}

# Bhatkhande's 10 Parent Thaats of Hindustani Classical Music
THAATS: Dict[str, ScaleDefinition] = {
    "bilawal": ScaleDefinition(
        id="bilawal",
        name="Bilawal Thaat",
        category="Indian Thaat",
        intervals=[0, 2, 4, 5, 7, 9, 11],
        description="Equivalent to Western Major/Ionian (All Shuddha Swaras: S R G M P D N).",
    ),
    "kalyan": ScaleDefinition(
        id="kalyan",
        name="Kalyan Thaat",
        category="Indian Thaat",
        intervals=[0, 2, 4, 6, 7, 9, 11],
        description="Equivalent to Western Lydian (Tivra Ma: S R G M' P D N).",
    ),
    "khamaj": ScaleDefinition(
        id="khamaj",
        name="Khamaj Thaat",
        category="Indian Thaat",
        intervals=[0, 2, 4, 5, 7, 9, 10],
        description="Equivalent to Western Mixolydian (Komal Ni: S R G M P D n).",
    ),
    "kafi": ScaleDefinition(
        id="kafi",
        name="Kafi Thaat",
        category="Indian Thaat",
        intervals=[0, 2, 3, 5, 7, 9, 10],
        description="Equivalent to Western Dorian (Komal Ga and Komal Ni: S R g M P D n).",
    ),
    "asavari": ScaleDefinition(
        id="asavari",
        name="Asavari Thaat",
        category="Indian Thaat",
        intervals=[0, 2, 3, 5, 7, 8, 10],
        description="Equivalent to Western Natural Minor/Aeolian (Komal Ga, Dha, Ni: S R g M P d n).",
    ),
    "bhairav": ScaleDefinition(
        id="bhairav",
        name="Bhairav Thaat",
        category="Indian Thaat",
        intervals=[0, 1, 4, 5, 7, 8, 11],
        description="Komal Re and Komal Dha (Double Harmonic / Mayamalavagowla: S r G M P d N).",
    ),
    "bhairavi": ScaleDefinition(
        id="bhairavi",
        name="Bhairavi Thaat",
        category="Indian Thaat",
        intervals=[0, 1, 3, 5, 7, 8, 10],
        description="Equivalent to Western Phrygian (All Komal: S r g M P d n).",
    ),
    "todi": ScaleDefinition(
        id="todi",
        name="Todi Thaat",
        category="Indian Thaat",
        intervals=[0, 1, 3, 6, 7, 8, 11],
        description="Komal Re, Komal Ga, Tivra Ma, Komal Dha (S r g M' P d N).",
    ),
    "poorvi": ScaleDefinition(
        id="poorvi",
        name="Poorvi Thaat",
        category="Indian Thaat",
        intervals=[0, 1, 4, 6, 7, 8, 11],
        description="Komal Re, Tivra Ma, Komal Dha (S r G M' P d N).",
    ),
    "marwa": ScaleDefinition(
        id="marwa",
        name="Marwa Thaat",
        category="Indian Thaat",
        intervals=[0, 1, 4, 6, 9, 11],
        description="Komal Re, Tivra Ma, Shuddha Dha, Shuddha Ni, No Pa (S r G M' D N). Hexatonic thaat.",
    ),
}


def get_all_scales() -> Dict[str, ScaleDefinition]:
    """Returns combined collection of all western scales and thaats."""
    all_scales = {}
    all_scales.update(WESTERN_SCALES)
    all_scales.update(THAATS)
    return all_scales


def find_scale(scale_id: str) -> Optional[ScaleDefinition]:
    """Look up a scale or thaat by ID (case-insensitive)."""
    normalized = scale_id.strip().lower()
    return get_all_scales().get(normalized)
