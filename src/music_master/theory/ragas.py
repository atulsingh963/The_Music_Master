from dataclasses import dataclass
from typing import List


@dataclass
class Raga:
    name: str
    thaat: str
    aroha: str  # Ascending swaras
    avaroha: str  # Descending swaras
    vadi: str  # Primary note
    samvadi: str  # Secondary note
    time_of_day: str  # Traditional prahar
    notes_semitones: List[int]  # semitones included in scale


INITIAL_RAGAS: List[Raga] = [
    Raga(
        "Yaman (Kalyan)",
        "Kalyan",
        "N' R G M' D N S'",
        "S' N D P M' G R S",
        "Ga",
        "Ni",
        "First quarter of night",
        [0, 2, 4, 6, 7, 9, 11],
    ),
    Raga(
        "Bhairav",
        "Bhairav",
        "S r G M P d N S'",
        "S' N d P M G r S",
        "Dha",
        "Re",
        "Early morning (dawn)",
        [0, 1, 4, 5, 7, 8, 11],
    ),
    Raga(
        "Bhairavi",
        "Bhairavi",
        "S r g M P d n S'",
        "S' n d P M g r S",
        "Ma",
        "Sa",
        "Morning / concluding",
        [0, 1, 3, 5, 7, 8, 10],
    ),
    Raga(
        "Kafi",
        "Kafi",
        "S R g M P D n S'",
        "S' n D P M g R S",
        "Pa",
        "Sa",
        "Late night",
        [0, 2, 3, 5, 7, 9, 10],
    ),
    Raga(
        "Bageshri",
        "Kafi",
        "S g M D n S'",
        "S' n D M g R S",
        "Ma",
        "Sa",
        "Midnight",
        [0, 2, 3, 5, 9, 10],
    ),
    Raga(
        "Malkauns",
        "Bhairavi",
        "S g M d n S'",
        "S' n d M g S",
        "Ma",
        "Sa",
        "Late night",
        [0, 3, 5, 8, 10],
    ),
    Raga(
        "Durga",
        "Bilawal",
        "S R M P D S'",
        "S' D P M R S",
        "Dha",
        "Re",
        "Late evening",
        [0, 2, 5, 7, 9],
    ),
    Raga(
        "Khamaj",
        "Khamaj",
        "S G M P D N S'",
        "S' n D P M G R S",
        "Ga",
        "Ni",
        "Late evening",
        [0, 2, 4, 5, 7, 9, 10, 11],
    ),
]
