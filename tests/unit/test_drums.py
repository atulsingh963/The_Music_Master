"""Unit tests for Phase 8 Percussion, Drum Machine, and 16-step Sequencer."""

import numpy as np

from music_master.instruments.percussion.drum_synthesizer import (
    DRUM_PADS,
    ActiveDrumVoice,
    DrumMachineEngine,
)
from music_master.instruments.percussion.sequencer import DrumSequencer


def test_drum_pads_definition() -> None:
    assert len(DRUM_PADS) >= 7
    categories = {pad.category for pad in DRUM_PADS}
    assert "kick" in categories
    assert "snare" in categories
    assert "hihat" in categories
    assert "clap" in categories
    assert "tom" in categories
    assert "rim" in categories
    assert "crash" in categories


def test_active_drum_voice_rendering() -> None:
    sample_rate = 44100
    for pad in DRUM_PADS:
        voice = ActiveDrumVoice(
            pad=pad,
            velocity=0.8,
            sample_rate=sample_rate,
            kit_type="acoustic",
        )
        audio = voice.render(512)
        assert len(audio) == 512
        assert audio.dtype == np.float32
        assert not np.isnan(audio).any()
        assert not np.isinf(audio).any()
        assert np.max(np.abs(audio)) > 0.0, f"Pad {pad.name} produced silent output"


def test_electronic_kit_voice_rendering() -> None:
    sample_rate = 44100
    kick_pad = next(p for p in DRUM_PADS if p.category == "kick")
    voice = ActiveDrumVoice(
        pad=kick_pad,
        velocity=0.9,
        sample_rate=sample_rate,
        kit_type="electronic",
        pitch_factor=1.2,
    )
    audio = voice.render(1024)
    assert len(audio) == 1024
    assert np.max(np.abs(audio)) > 0.0


def test_drum_machine_engine_triggers() -> None:
    engine = DrumMachineEngine(sample_rate=44100)
    assert len(engine.active_voices) == 0

    engine.trigger_pad("kick", velocity=0.9)
    assert len(engine.active_voices) == 1

    engine.trigger_note(38, velocity=0.85)  # Snare
    assert len(engine.active_voices) == 2

    audio = engine.render_block(512)
    assert len(audio) == 512
    assert np.max(np.abs(audio)) > 0.0

    engine.stop_all()
    assert len(engine.active_voices) == 0


def test_drum_sequencer_controls_and_playback() -> None:
    engine = DrumMachineEngine(sample_rate=44100)
    seq = DrumSequencer(drum_engine=engine, bpm=120.0, sample_rate=44100)

    # Test toggling step
    initial = seq.grid["kick"][0].active
    toggled = seq.toggle_step("kick", 0)
    assert toggled != initial
    assert seq.grid["kick"][0].active == toggled

    # Test BPM change
    seq.set_bpm(140.0)
    assert seq.bpm == 140.0

    # Test Play / Stop
    assert not seq.is_playing
    seq.play()
    assert seq.is_playing

    # Render blocks through clock
    steps_hit = []
    seq.step_callback = lambda s: steps_hit.append(s)

    audio = seq.process_frames(seq.samples_per_step * 3)
    assert len(audio) == seq.samples_per_step * 3
    assert len(steps_hit) >= 2

    seq.stop()
    assert not seq.is_playing
    assert seq.current_step == 0


def test_drum_sequencer_presets() -> None:
    engine = DrumMachineEngine(sample_rate=44100)
    seq = DrumSequencer(drum_engine=engine, bpm=120.0, sample_rate=44100)

    for preset in ["rock", "hiphop", "house"]:
        seq.load_preset(preset)
        active_steps = sum(1 for pad in seq.grid for s in seq.grid[pad] if s.active)
        assert active_steps > 0
