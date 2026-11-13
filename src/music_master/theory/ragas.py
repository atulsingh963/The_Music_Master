"""Data-driven Raga definitions, Aroha/Avaroha analysis, Vadi/Samvadi, and Pakad."""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class Raga:
    id: str
    name: str
    thaat: str
    aroha: str  # Ascending swaras, e.g. "S R G M P D N S'"
    avaroha: str  # Descending swaras, e.g. "S' N D P M G R S"
    vadi: str  # Primary sonant note
    samvadi: str  # Secondary consonant note
    time_of_day: str  # Traditional prahar / time of day
    notes_semitones: List[int]  # Semitones included in scale [0-11]
    pakad: str = ""  # Identifying musical phrase / catchphrase
    rasa: str = ""  # Dominant emotion/mood (Shringara, Bhakti, etc.)
    description: str = ""

    def validate_note(self, semitone: int) -> bool:
        """Checks if a given semitone (0-11 relative to tonic) is valid in this raga."""
        return (semitone % 12) in self.notes_semitones

    def is_in_aroha(self, swara_symbol: str) -> bool:
        """Checks if swara symbol is explicitly mentioned in aroha phrase."""
        clean = swara_symbol.strip()
        tokens = self.aroha.split()
        return clean in tokens or any(t.startswith(clean) for t in tokens)

    def is_in_avaroha(self, swara_symbol: str) -> bool:
        """Checks if swara symbol is explicitly mentioned in avaroha phrase."""
        clean = swara_symbol.strip()
        tokens = self.avaroha.split()
        return clean in tokens or any(t.startswith(clean) for t in tokens)


# Comprehensive Initial Hindustani Raga Presets
INITIAL_RAGAS: List[Raga] = [
    Raga(
        id="yaman",
        name="Yaman (Kalyan)",
        thaat="Kalyan",
        aroha="'N R G M' D N S'",
        avaroha="S' N D P M' G R S",
        vadi="Ga",
        samvadi="Ni",
        time_of_day="First quarter of night (6 PM - 9 PM)",
        notes_semitones=[0, 2, 4, 6, 7, 9, 11],
        pakad="'N R G, M' D N S', R' N D P, M' G R S",
        rasa="Shringara (Romantic, Peaceful, Devotional)",
        description="One of the most fundamental evening ragas featuring Tivra Madhyam and prominent Gandhar.",
    ),
    Raga(
        id="bhairav",
        name="Bhairav",
        thaat="Bhairav",
        aroha="S r G M P d N S'",
        avaroha="S' N d P M G r S",
        vadi="Dha",
        samvadi="Re",
        time_of_day="Early morning (dawn / first prahar)",
        notes_semitones=[0, 1, 4, 5, 7, 8, 11],
        pakad="S G M P, d-- P, G M r-- S",
        rasa="Bhakti & Gambhir (Devotion, Solemnity, Awe)",
        description="Majestic morning raga characterized by oscillating andolan on Komal Rishabh and Komal Dhaivat.",
    ),
    Raga(
        id="bhairavi",
        name="Bhairavi",
        thaat="Bhairavi",
        aroha="S r g M P d n S'",
        avaroha="S' n d P M g r S",
        vadi="Ma",
        samvadi="Sa",
        time_of_day="Morning / traditionally concluded at end of concert",
        notes_semitones=[0, 1, 3, 5, 7, 8, 10],
        pakad="M P d P, g M r S",
        rasa="Karuna & Shringara (Pathos, Tenderness, Farewell)",
        description="All four vikrit swaras are komal; queen of morning ragas, often performed in semi-classical thumri.",
    ),
    Raga(
        id="kafi",
        name="Kafi",
        thaat="Kafi",
        aroha="S R g M P D n S'",
        avaroha="S' n D P M g R S",
        vadi="Pa",
        samvadi="Sa",
        time_of_day="Late night / Anytime in spring (Hori/Holi)",
        notes_semitones=[0, 2, 3, 5, 7, 9, 10],
        pakad="S R R g, M P, D n P",
        rasa="Ananda & Shringara (Joy, Spring celebration)",
        description="Features Komal Gandhar and Komal Nishad, deeply associated with folk and springtime festivals.",
    ),
    Raga(
        id="bageshri",
        name="Bageshri",
        thaat="Kafi",
        aroha="S g M D n S'",
        avaroha="S' n D, M P D, M g, R S",
        vadi="Ma",
        samvadi="Sa",
        time_of_day="Midnight (second/third prahar of night)",
        notes_semitones=[0, 2, 3, 5, 7, 9, 10],
        pakad="S n' D' S, M, g M D, n D M",
        rasa="Viraha (Longing, Deep Romantic Yearning)",
        description="Audav-Sampurna raga omitting Re and Pa in ascent, creating an atmosphere of quiet nocturnal contemplation.",
    ),
    Raga(
        id="malkauns",
        name="Malkauns",
        thaat="Bhairavi",
        aroha="S g M d n S'",
        avaroha="S' n d M g S",
        vadi="Ma",
        samvadi="Sa",
        time_of_day="Late night / Midnight",
        notes_semitones=[0, 3, 5, 8, 10],
        pakad="g M d n d M, g M g S",
        rasa="Veera & Gambhir (Meditative, Introspective, Serene)",
        description="Ancient pentatonic (Audav) scale completely omitting Re and Pa; deeply spiritual and profound.",
    ),
    Raga(
        id="durga",
        name="Durga",
        thaat="Bilawal",
        aroha="S R M P D S'",
        avaroha="S' D P M R S",
        vadi="Dha",
        samvadi="Re",
        time_of_day="Late evening (second prahar of night)",
        notes_semitones=[0, 2, 5, 7, 9],
        pakad="M P D, M R, 'D S",
        rasa="Shanta & Prasanna (Serene, Bright, Innocent Joy)",
        description="Five-note pentatonic scale using Shuddha swaras without Ga and Ni.",
    ),
    Raga(
        id="khamaj",
        name="Khamaj",
        thaat="Khamaj",
        aroha="S G M P D N S'",
        avaroha="S' n D P M G R S",
        vadi="Ga",
        samvadi="Ni",
        time_of_day="Late evening (second quarter of night)",
        notes_semitones=[0, 2, 4, 5, 7, 9, 10, 11],
        pakad="G M P D, n D P, M G",
        rasa="Shringara & Hasya (Sensual, Playful, Romantic)",
        description="Uses Shuddha Nishad in ascent and Komal Nishad in descent; prominent in semi-classical thumri.",
    ),
    Raga(
        id="desh",
        name="Desh",
        thaat="Khamaj",
        aroha="S R M P N S'",
        avaroha="S' n D P M G R S",
        vadi="Re",
        samvadi="Pa",
        time_of_day="Second quarter of night / Monsoon season",
        notes_semitones=[0, 2, 4, 5, 7, 9, 10, 11],
        pakad="R M P N S', R' n D P, M G R S",
        rasa="Deshbhakti & Shringara (Patriotic devotion, Rain, Longing)",
        description="Beloved seasonal and patriotic raga associated with Indian independence ('Vande Mataram').",
    ),
    Raga(
        id="bhupali",
        name="Bhupali (Bhoop)",
        thaat="Kalyan",
        aroha="S R G P D S'",
        avaroha="S' D P G R S",
        vadi="Ga",
        samvadi="Dha",
        time_of_day="First quarter of night (7 PM - 10 PM)",
        notes_semitones=[0, 2, 4, 7, 9],
        pakad="G R S 'D S R G, P G D P G R S",
        rasa="Shanta & Bhakti (Peaceful, Reverent, Calm)",
        description="Pentatonic scale omitting Ma and Ni; identical notes to major pentatonic with profound Indian aesthetics.",
    ),
]


class RagaRegistry:
    """Manages data-driven query and validation of Indian ragas."""

    def __init__(self) -> None:
        self._ragas: Dict[str, Raga] = {r.id: r for r in INITIAL_RAGAS}

    def get_all(self) -> List[Raga]:
        return list(self._ragas.values())

    def get(self, raga_id: str) -> Optional[Raga]:
        return self._ragas.get(raga_id.strip().lower())

    def add_custom_raga(self, raga: Raga) -> None:
        self._ragas[raga.id] = raga

    def validate_swara_sequence(self, raga_id: str, semitones: List[int]) -> bool:
        """Validates whether a sequence of played note intervals conforms to the raga."""
        raga = self.get(raga_id)
        if not raga:
            return False
        return all(raga.validate_note(st) for st in semitones)
