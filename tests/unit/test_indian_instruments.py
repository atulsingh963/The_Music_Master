"""Comprehensive unit tests for Indian instruments: Tanpura drone, Tabla synthesis, bols, and audio engine integration."""

import numpy as np

from music_master.audio.engine import AudioEngine
from music_master.instruments.indian.tabla import BOL_DEFINITIONS, TablaSynthesizer
from music_master.instruments.indian.tanpura import TanpuraDroneEngine


def test_tanpura_initialization_and_tuning():
    tanpura = TanpuraDroneEngine(
        sample_rate=44100, tonic_midi=48, pattern_type="pa", tempo_bpm=24.0
    )
    assert not tanpura.is_active
    assert tanpura.tonic_midi == 48
    assert tanpura.pattern_type == "pa"

    # Test tuning parameter changes
    tanpura.set_tonic(60)
    assert tanpura.tonic_midi == 60
    tanpura.set_pattern("ma")
    assert tanpura.pattern_type == "ma"
    tanpura.set_pattern("ni")
    assert tanpura.pattern_type == "ni"

    # Invalid pattern should be safely ignored
    tanpura.set_pattern("invalid_pattern")
    assert tanpura.pattern_type == "ni"


def test_tanpura_audio_rendering():
    tanpura = TanpuraDroneEngine(sample_rate=44100, tonic_midi=48)
    # When stopped, output is silence
    silent_block = tanpura.render_block(512)
    assert np.all(silent_block == 0.0)

    # Start drone
    tanpura.start()
    assert tanpura.is_active

    # Render audio blocks
    audio_block = tanpura.render_block(1024)
    assert len(audio_block) == 1024
    assert np.any(audio_block != 0.0)
    assert np.max(np.abs(audio_block)) <= 1.0

    # Stop drone
    tanpura.stop()
    assert not tanpura.is_active
    stopped_block = tanpura.render_block(512)
    assert np.all(stopped_block == 0.0)


def test_tabla_bol_definitions():
    assert "dha" in BOL_DEFINITIONS
    assert "dhin" in BOL_DEFINITIONS
    assert "ge" in BOL_DEFINITIONS
    assert "ke" in BOL_DEFINITIONS
    assert "na" in BOL_DEFINITIONS
    assert "tin" in BOL_DEFINITIONS
    assert "ti" in BOL_DEFINITIONS
    assert "ra" in BOL_DEFINITIONS
    assert "tu" in BOL_DEFINITIONS

    dha = BOL_DEFINITIONS["dha"]
    assert dha.drum == "both"
    ge = BOL_DEFINITIONS["ge"]
    assert ge.drum == "bayan"
    na = BOL_DEFINITIONS["na"]
    assert na.drum == "dayan"


def test_tabla_synthesizer_rendering():
    synth = TablaSynthesizer(sample_rate=44100)
    silent_block = synth.render_block(256)
    assert np.all(silent_block == 0.0)

    # Trigger Dayan bol
    synth.trigger_bol("na", velocity=0.8)
    block1 = synth.render_block(1024)
    assert np.any(block1 != 0.0)
    assert np.max(np.abs(block1)) <= 1.0

    # Trigger Bayan bol
    synth.trigger_bol("ge", velocity=0.9)
    block2 = synth.render_block(1024)
    assert np.any(block2 != 0.0)


def test_audio_engine_with_indian_instruments():
    engine = AudioEngine(sample_rate=44100, buffer_size=256)
    engine.start()

    # Sitar instrument playback
    engine.set_instrument("sitar")
    engine.note_on(60, 90)
    block = engine.render_block(512)
    assert block.shape == (512, 2)
    assert np.any(block != 0.0)
    engine.note_off(60)

    # Tabla routing through engine
    engine.set_instrument("tabla")
    engine.note_on(60, 100)  # C4 -> "dha"
    tabla_block = engine.render_block(512)
    assert np.any(tabla_block != 0.0)

    # Tanpura drone mixed with engine
    engine.tanpura.start()
    mixed_block = engine.render_block(512)
    assert np.any(mixed_block != 0.0)

    # Verify tuning engine integration with voice rendering
    engine.tuning.set_reference_pitch(442.0)
    engine.set_instrument("sitar")
    engine.note_on(69, 100)  # A4
    voice_a4 = engine.active_voices[69]
    assert abs(voice_a4.freq - 442.0) < 1e-4

    engine.panic()
    assert not engine.tanpura.is_active
