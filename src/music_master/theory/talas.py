"""Indian Tala (rhythm cycle) definitions, Matra divisions, Vibhags, and Bols."""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class Matra:
    number: int
    bol: str  # Syllable, e.g. "Dha", "Dhin", "Tin", "Ta"
    is_sam: bool = False  # 1st beat (Sam / +)
    is_tali: bool = False  # Clap
    is_khali: bool = False  # Wave / empty beat (0)
    vibhag_index: int = 0  # Group index


@dataclass
class Tala:
    id: str
    name: str
    matras: int  # Total number of beats in cycle (Avartan)
    vibhag_structure: List[int]  # e.g., [4, 4, 4, 4] for Teental
    claps: List[int]  # 1-indexed matras with tali/clap
    khali: List[int]  # 1-indexed matras with wave/khali
    theka_bols: List[str]  # Standard rhythmic syllables per matra
    description: str = ""

    def get_cycle(self) -> List[Matra]:
        """Builds structured Matra list representing the complete rhythmic cycle."""
        result: List[Matra] = []
        current_vibhag = 0
        vibhag_countdown = (
            self.vibhag_structure[0] if self.vibhag_structure else len(self.theka_bols)
        )

        for i, bol in enumerate(self.theka_bols):
            matra_num = i + 1
            if vibhag_countdown == 0 and current_vibhag + 1 < len(self.vibhag_structure):
                current_vibhag += 1
                vibhag_countdown = self.vibhag_structure[current_vibhag]

            is_sam = matra_num == 1
            is_khali = matra_num in self.khali
            is_tali = (matra_num in self.claps) and not is_khali

            result.append(
                Matra(
                    number=matra_num,
                    bol=bol,
                    is_sam=is_sam,
                    is_tali=is_tali,
                    is_khali=is_khali,
                    vibhag_index=current_vibhag,
                )
            )
            vibhag_countdown -= 1

        return result


# Standard Indian Classical Talas
TALAS: Dict[str, Tala] = {
    "teental": Tala(
        id="teental",
        name="Teental (Tintal)",
        matras=16,
        vibhag_structure=[4, 4, 4, 4],
        claps=[1, 5, 13],
        khali=[9],
        theka_bols=[
            "Dha",
            "Dhin",
            "Dhin",
            "Dha",
            "Dha",
            "Dhin",
            "Dhin",
            "Dha",
            "Dha",
            "Tin",
            "Tin",
            "Ta",
            "Ta",
            "Dhin",
            "Dhin",
            "Dha",
        ],
        description="The most fundamental and prominent 16-beat tala of Hindustani music.",
    ),
    "ektaal": Tala(
        id="ektaal",
        name="Ektaal",
        matras=12,
        vibhag_structure=[2, 2, 2, 2, 2, 2],
        claps=[1, 5, 9, 11],
        khali=[3, 7],
        theka_bols=[
            "Dhin",
            "Dhin",
            "DhaGe",
            "TiRaKiTa",
            "Tu",
            "Na",
            "Kat",
            "Ta",
            "DhaGe",
            "TiRaKiTa",
            "Dhi",
            "Na",
        ],
        description="12-beat classical cycle frequently used in vilambit and drut khayal.",
    ),
    "jhaptal": Tala(
        id="jhaptal",
        name="Jhaptal",
        matras=10,
        vibhag_structure=[2, 3, 2, 3],
        claps=[1, 3, 8],
        khali=[6],
        theka_bols=["Dhi", "Na", "Dhi", "Dhi", "Na", "Ti", "Na", "Dhi", "Dhi", "Na"],
        description="Asymmetrical 10-beat cycle with distinct 2-3-2-3 subdivision.",
    ),
    "rupak": Tala(
        id="rupak",
        name="Rupak Tala",
        matras=7,
        vibhag_structure=[3, 2, 2],
        claps=[4, 6],
        khali=[1],  # Rupak is uniquely known for beginning on Khali
        theka_bols=["Tin", "Tin", "Na", "Dhin", "Na", "Dhin", "Na"],
        description="7-beat cycle famously starting with Khali on the first beat (Sam).",
    ),
    "keherwa": Tala(
        id="keherwa",
        name="Keherwa",
        matras=8,
        vibhag_structure=[4, 4],
        claps=[1],
        khali=[5],
        theka_bols=["Dha", "Ge", "Na", "Ti", "Na", "Ka", "Dhi", "Na"],
        description="Lively 8-beat rhythm ubiquitous in semi-classical, ghazal, and folk.",
    ),
    "dadra": Tala(
        id="dadra",
        name="Dadra",
        matras=6,
        vibhag_structure=[3, 3],
        claps=[1],
        khali=[4],
        theka_bols=["Dha", "Dhi", "Na", "Dha", "Tu", "Na"],
        description="Light classical 6-beat cycle with syncopated lilt.",
    ),
    "chautal": Tala(
        id="chautal",
        name="Chautal (Char Taal)",
        matras=12,
        vibhag_structure=[2, 2, 2, 2, 2, 2],
        claps=[1, 5, 9, 11],
        khali=[3, 7],
        theka_bols=[
            "Dha",
            "Dha",
            "Din",
            "Ta",
            "KiTe",
            "Dha",
            "Din",
            "Ta",
            "TiTe",
            "KaTa",
            "GaDi",
            "GeNe",
        ],
        description="Solemn 12-beat tala primarily accompanying ancient Dhrupad singing on Pakhawaj.",
    ),
}


def get_tala(tala_id: str) -> Optional[Tala]:
    return TALAS.get(tala_id.strip().lower())
