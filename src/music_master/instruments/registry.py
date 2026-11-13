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
                AvailabilityState.AVAILABLE,
                "Classical Indian twin percussion drums (Dayan & Bayan).",
                "Acoustic Physical Modeling",
                116,
            ),
            InstrumentDefinition(
                "sitar",
                "Sitar",
                InstrumentCategory.INDIAN_CLASSICAL,
                AvailabilityState.AVAILABLE,
                "Plucked string instrument with sympathetic strings and resonant meend.",
                "Javari Resonant Synthesizer",
                104,
            ),
            InstrumentDefinition(
                "tanpura",
                "Tanpura",
                InstrumentCategory.INDIAN_CLASSICAL,
                AvailabilityState.AVAILABLE,
                "Long-necked plucked string drone instrument.",
                "Continuous Multi-String Acoustic Drone",
                104,
            ),
            InstrumentDefinition(
                "bansuri",
                "Bansuri",
                InstrumentCategory.INDIAN_CLASSICAL,
                AvailabilityState.AVAILABLE,
                "Traditional side-blown bamboo flute.",
                "Acoustic Physical Modeling",
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
                AvailabilityState.AVAILABLE,
                "Steel string acoustic guitar with rich harmonics.",
                "Acoustic Physical Modeling",
                25,
            ),
            InstrumentDefinition(
                "electric_guitar",
                "Electric Guitar",
                InstrumentCategory.STRINGS,
                AvailabilityState.AVAILABLE,
                "Solid body electric guitar with sustained overdrive.",
                "Harmonic Modeling",
                27,
            ),
            InstrumentDefinition(
                "bass_guitar",
                "Bass Guitar",
                InstrumentCategory.STRINGS,
                AvailabilityState.AVAILABLE,
                "4-string electric bass with punchy low register.",
                "Sub-Bass Modeling",
                33,
            ),
            InstrumentDefinition(
                "violin",
                "Violin",
                InstrumentCategory.STRINGS,
                AvailabilityState.AVAILABLE,
                "Solo and ensemble acoustic violin with expressive vibrato.",
                "Bowed Physical Modeling",
                40,
            ),
            InstrumentDefinition(
                "cello",
                "Cello",
                InstrumentCategory.STRINGS,
                AvailabilityState.AVAILABLE,
                "Deep resonant cello strings with warm wooden resonance.",
                "Bowed Physical Modeling",
                42,
            ),
            # Wind
            InstrumentDefinition(
                "concert_flute",
                "Concert Flute",
                InstrumentCategory.WIND,
                AvailabilityState.AVAILABLE,
                "Western concert silver flute with breath harmonics.",
                "Acoustic Physical Modeling",
                73,
            ),
            InstrumentDefinition(
                "trumpet",
                "Trumpet",
                InstrumentCategory.WIND,
                AvailabilityState.AVAILABLE,
                "Bright orchestral brass trumpet.",
                "Brass Harmonic Synthesis",
                56,
            ),
            InstrumentDefinition(
                "trombone",
                "Trombone",
                InstrumentCategory.WIND,
                AvailabilityState.AVAILABLE,
                "Warm tenor slide trombone.",
                "Brass Harmonic Synthesis",
                57,
            ),
            # World
            InstrumentDefinition(
                "erhu",
                "Chinese Erhu",
                InstrumentCategory.WORLD,
                AvailabilityState.AVAILABLE,
                "Traditional two-stringed bowed musical instrument.",
                "Acoustic Physical Modeling",
                110,
            ),
            InstrumentDefinition(
                "koto",
                "Japanese Koto",
                InstrumentCategory.WORLD,
                AvailabilityState.AVAILABLE,
                "Traditional Japanese plucked half-tube zither.",
                "Plucked Physical Modeling",
                107,
            ),
            # Vocal
            InstrumentDefinition(
                "choir",
                "Choir Aah",
                InstrumentCategory.VOCAL,
                AvailabilityState.AVAILABLE,
                "Full choral ensemble vocal choir.",
                "Formant Synthesis",
                52,
            ),
            InstrumentDefinition(
                "vocal_pad",
                "Atmospheric Vocal Pad",
                InstrumentCategory.VOCAL,
                AvailabilityState.AVAILABLE,
                "Ethereal cinematic ambient vocal wash.",
                "Atmospheric Formant Pad",
                53,
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
