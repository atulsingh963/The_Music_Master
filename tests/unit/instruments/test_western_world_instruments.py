"""Unit tests for Phase 7 & 9 instruments: Western and World synthesis engines."""

import numpy as np

from music_master.audio.engine import AudioEngine
from music_master.instruments.acoustic_synth import AcousticSynthRegistry
from music_master.instruments.base import AvailabilityState
from music_master.instruments.registry import InstrumentRegistry


def test_acoustic_synth_presets_defined():
    expected_instruments = [
        "bansuri",
        "concert_flute",
        "trumpet",
        "trombone",
        "violin",
        "cello",
        "acoustic_guitar",
        "electric_guitar",
        "bass_guitar",
        "erhu",
        "koto",
        "choir",
        "vocal_pad",
    ]
    for inst_id in expected_instruments:
        preset = AcousticSynthRegistry.get_preset(inst_id)
        assert preset is not None, f"Missing preset for {inst_id}"
        assert preset.attack_time > 0.0
        assert preset.release_time > 0.0
        assert len(preset.harmonics) >= 3


def test_instrument_registry_availability():
    registry = InstrumentRegistry()
    available = {inst.id: inst for inst in registry.get_available()}

    # Verify newly activated instruments are available
    for key in ["bansuri", "violin", "trumpet", "acoustic_guitar", "choir", "erhu"]:
        assert key in available
        assert available[key].availability == AvailabilityState.AVAILABLE


def test_audio_engine_renders_new_instruments():
    engine = AudioEngine(sample_rate=44100)

    test_insts = [
        "bansuri",
        "violin",
        "trumpet",
        "acoustic_guitar",
        "bass_guitar",
        "choir",
        "erhu",
    ]
    for inst in test_insts:
        engine.set_instrument(inst)
        engine.note_on(60, velocity=100)
        block = engine.render_block(512)

        # Output should be non-silent float32 stereo
        assert block.shape == (512, 2)
        assert block.dtype == np.float32
        assert np.max(np.abs(block)) > 0.001

        engine.note_off(60)
        engine.panic()
