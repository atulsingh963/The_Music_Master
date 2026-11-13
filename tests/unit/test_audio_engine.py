import numpy as np

from music_master.audio.engine import AudioEngine, Voice, midi_to_freq


def test_midi_to_freq():
    assert abs(midi_to_freq(69) - 440.0) < 1e-4  # A4 = 440 Hz
    assert abs(midi_to_freq(60) - 261.6255) < 1e-2  # Middle C
    assert abs(midi_to_freq(57) - 220.0) < 1e-4  # A3 = 220 Hz


def test_voice_render():
    voice = Voice(midi_note=60, velocity=100, sample_rate=44100, instrument_id="harmonium")
    samples = voice.render(512)
    assert len(samples) == 512
    assert samples.dtype == np.float32
    assert not np.isnan(samples).any()
    assert not np.isinf(samples).any()


def test_voice_release():
    voice = Voice(midi_note=60, velocity=100, sample_rate=44100, instrument_id="harmonium")
    voice.trigger_release()
    assert voice.is_releasing is True
    # Render until release decays
    for _ in range(30):
        voice.render(512)
    assert voice.is_dead is True


def test_audio_engine_polyphony_and_render():
    engine = AudioEngine(sample_rate=44100, buffer_size=256, polyphony=4)
    # Trigger 3 notes
    engine.note_on(60, 100)
    engine.note_on(64, 90)
    engine.note_on(67, 85)
    assert len(engine.active_voices) == 3

    block = engine.render_block(256)
    assert block.shape == (256, 2)
    assert block.dtype == np.float32
    # Output should contain sound
    assert np.max(np.abs(block)) > 0.0


def test_audio_engine_panic():
    engine = AudioEngine()
    engine.note_on(60, 100)
    engine.note_on(64, 100)
    engine.panic()
    assert len(engine.active_voices) == 0
    assert len(engine.sustained_voices) == 0
