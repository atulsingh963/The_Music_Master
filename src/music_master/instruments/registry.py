from music_master.instruments.base import (
    AvailabilityState,
    InstrumentCategory,
    InstrumentDefinition,
)


class InstrumentRegistry:
    """Catalogue and metadata manager for all planned and available instruments."""

    def __init__(self) -> None:
        self._instruments: dict[str, InstrumentDefinition] = {}
        self._register_default_catalog()

    def _register_default_catalog(self) -> None:
        catalog = [
            # Indian Classical
            InstrumentDefinition(
                "harmonium",
                "Harmonium",
                InstrumentCategory.INDIAN_CLASSICAL,
                AvailabilityState.AVAILABLE,
                "Hand-pumped reed organ with warm dual-reed timbre and drone support.",
                "Multi-Harmonic Synthesizer",
                20,
            ),
            InstrumentDefinition(
                "tabla",
                "Tabla",
                InstrumentCategory.INDIAN_CLASSICAL,
                AvailabilityState.PLANNED,
                "Classical Indian twin percussion drums (Dayan & Bayan).",
                "Sampled / Synthesis",
                116,
            ),
            InstrumentDefinition(
                "sitar",
                "Sitar",
                InstrumentCategory.INDIAN_CLASSICAL,
                AvailabilityState.PLANNED,
                "Plucked string instrument with sympathetic strings and resonant meend.",
                "SoundFont",
                104,
            ),
            InstrumentDefinition(
                "tanpura",
                "Tanpura",
                InstrumentCategory.INDIAN_CLASSICAL,
                AvailabilityState.PLANNED,
                "Long-necked plucked string drone instrument.",
                "SoundFont / Synthesis",
                104,
            ),
            InstrumentDefinition(
                "bansuri",
                "Bansuri",
                InstrumentCategory.INDIAN_CLASSICAL,
                AvailabilityState.PLANNED,
                "Traditional side-blown bamboo flute.",
                "SoundFont",
                73,
            ),
            InstrumentDefinition(
                "veena",
                "Veena",
                InstrumentCategory.INDIAN_CLASSICAL,
                AvailabilityState.PLANNED,
                "Ancient plucked string instrument of Carnatic music.",
                "SoundFont",
                105,
            ),
            InstrumentDefinition(
                "dholak",
                "Dholak",
                InstrumentCategory.INDIAN_CLASSICAL,
                AvailabilityState.PLANNED,
                "Two-headed hand drum used in folk and devotional music.",
                "Sampled",
                116,
            ),
            InstrumentDefinition(
                "mridangam",
                "Mridangam",
                InstrumentCategory.INDIAN_CLASSICAL,
                AvailabilityState.PLANNED,
                "Primary rhythmic accompaniment in Carnatic music.",
                "Sampled",
                116,
            ),
            InstrumentDefinition(
                "sarangi",
                "Sarangi",
                InstrumentCategory.INDIAN_CLASSICAL,
                AvailabilityState.PLANNED,
                "Bowed string instrument with rich resonant harmonics.",
                "SoundFont",
                110,
            ),
            InstrumentDefinition(
                "shehnai",
                "Shehnai",
                InstrumentCategory.INDIAN_CLASSICAL,
                AvailabilityState.PLANNED,
                "Quadruple-reed wind instrument.",
                "SoundFont",
                111,
            ),
            InstrumentDefinition(
                "santoor",
                "Santoor",
                InstrumentCategory.INDIAN_CLASSICAL,
                AvailabilityState.PLANNED,
                "Trapezoid-shaped hammered dulcimer.",
                "SoundFont",
                15,
            ),
            InstrumentDefinition(
                "manjira",
                "Manjira",
                InstrumentCategory.INDIAN_CLASSICAL,
                AvailabilityState.PLANNED,
                "Hand cymbals for devotional rhythm.",
                "Sampled",
                118,
            ),
            InstrumentDefinition(
                "ghatam",
                "Ghatam",
                InstrumentCategory.INDIAN_CLASSICAL,
                AvailabilityState.PLANNED,
                "Clay pot percussion instrument.",
                "Sampled",
                115,
            ),
            # Western Keyboard
            InstrumentDefinition(
                "grand_piano",
                "Grand Piano",
                InstrumentCategory.WESTERN_KEYBOARD,
                AvailabilityState.AVAILABLE,
                "Concert grand acoustic piano with full dynamic range.",
                "Harmonic Synthesis / SoundFont",
                0,
            ),
            InstrumentDefinition(
                "upright_piano",
                "Upright Piano",
                InstrumentCategory.WESTERN_KEYBOARD,
                AvailabilityState.PLANNED,
                "Intimate upright acoustic piano tone.",
                "SoundFont",
                0,
            ),
            InstrumentDefinition(
                "electric_piano",
                "Electric Piano",
                InstrumentCategory.WESTERN_KEYBOARD,
                AvailabilityState.AVAILABLE,
                "Classic vintage tines and electronic bells.",
                "FM Synthesis",
                4,
            ),
            InstrumentDefinition(
                "organ",
                "Organ",
                InstrumentCategory.WESTERN_KEYBOARD,
                AvailabilityState.AVAILABLE,
                "Rich drawbar organ with vibrato.",
                "Additive Synthesis",
                16,
            ),
            InstrumentDefinition(
                "celesta",
                "Celesta",
                InstrumentCategory.WESTERN_KEYBOARD,
                AvailabilityState.PLANNED,
                "Struck idiophone operated by keyboard.",
                "SoundFont",
                8,
            ),
            InstrumentDefinition(
                "harpsichord",
                "Harpsichord",
                InstrumentCategory.WESTERN_KEYBOARD,
                AvailabilityState.PLANNED,
                "Baroque plucked keyboard string instrument.",
                "SoundFont",
                6,
            ),
            # Strings
            InstrumentDefinition(
                "acoustic_guitar",
                "Acoustic Guitar",
                InstrumentCategory.STRINGS,
                AvailabilityState.PLANNED,
                "Steel string acoustic guitar.",
                "SoundFont",
                25,
            ),
            InstrumentDefinition(
                "electric_guitar",
                "Electric Guitar",
                InstrumentCategory.STRINGS,
                AvailabilityState.PLANNED,
                "Solid body electric guitar.",
                "SoundFont",
                27,
            ),
            InstrumentDefinition(
                "bass_guitar",
                "Bass Guitar",
                InstrumentCategory.STRINGS,
                AvailabilityState.PLANNED,
                "4-string electric bass.",
                "SoundFont",
                33,
            ),
            InstrumentDefinition(
                "violin",
                "Violin",
                InstrumentCategory.STRINGS,
                AvailabilityState.PLANNED,
                "Solo and ensemble acoustic violin.",
                "SoundFont",
                40,
            ),
            InstrumentDefinition(
                "cello",
                "Cello",
                InstrumentCategory.STRINGS,
                AvailabilityState.PLANNED,
                "Deep resonant cello strings.",
                "SoundFont",
                42,
            ),
            # Percussion & Electronic
            InstrumentDefinition(
                "acoustic_drum_kit",
                "Acoustic Drum Kit",
                InstrumentCategory.PERCUSSION,
                AvailabilityState.PLANNED,
                "Standard studio rock/jazz drum kit.",
                "Sampled",
                118,
            ),
            InstrumentDefinition(
                "analog_synth",
                "Analog Synthesizer",
                InstrumentCategory.ELECTRONIC,
                AvailabilityState.AVAILABLE,
                "Subtractive analog synthesizer with resonant filter.",
                "Subtractive Synthesis",
                80,
            ),
        ]
        for inst in catalog:
            self._instruments[inst.id] = inst

    def get_all(self) -> list[InstrumentDefinition]:
        return list(self._instruments.values())

    def get_by_id(self, inst_id: str) -> InstrumentDefinition | None:
        return self._instruments.get(inst_id)

    def get_available(self) -> list[InstrumentDefinition]:
        return [
            inst
            for inst in self._instruments.values()
            if inst.availability == AvailabilityState.AVAILABLE
        ]
