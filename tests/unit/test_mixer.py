"""Unit tests for Phase 11 Mixer Engine and Audio Effects."""

import numpy as np

from music_master.mixer.effects import DelayEffect, Equalizer3Band, PeakLimiter, ReverbEffect
from music_master.mixer.track import MixerEngine, MixerTrack


def test_delay_effect() -> None:
    delay = DelayEffect(sample_rate=44100, delay_time=0.1, feedback=0.4, mix=0.5)
    impulse = np.zeros((10000, 2), dtype=np.float32)
    impulse[0, :] = 1.0

    out = delay.process(impulse)
    assert out.shape == (10000, 2)
    assert not np.isnan(out).any()

    # Echo should appear at ~4410 samples
    delay_sample = int(0.1 * 44100)
    assert np.max(np.abs(out[delay_sample - 5 : delay_sample + 5])) > 0.1

    # Reset
    delay.reset()
    assert np.all(delay.buffer == 0.0)


def test_reverb_effect() -> None:
    reverb = ReverbEffect(sample_rate=44100, room_size=0.7, damping=0.2, mix=0.5)
    impulse = np.zeros((44100, 2), dtype=np.float32)
    impulse[0, :] = 1.0

    out = reverb.process(impulse)
    assert out.shape == (44100, 2)
    assert not np.isnan(out).any()
    # Tail should ring out beyond 5000 samples
    assert np.max(np.abs(out[3000:8000])) > 0.001


def test_equalizer_3band() -> None:
    eq = Equalizer3Band(sample_rate=44100)
    signal = np.random.uniform(-0.5, 0.5, (1024, 2)).astype(np.float32)

    # Flat EQ returns close to original
    flat_out = eq.process(signal)
    assert flat_out.shape == (1024, 2)

    # Boost low
    eq.set_gains(low_db=6.0, mid_db=0.0, high_db=-6.0)
    boost_out = eq.process(signal)
    assert boost_out.shape == (1024, 2)
    assert not np.isnan(boost_out).any()


def test_peak_limiter() -> None:
    limiter = PeakLimiter(sample_rate=44100, threshold_db=-1.0)
    loud_signal = np.full((1024, 2), 5.0, dtype=np.float32)

    out = limiter.process(loud_signal)
    assert np.max(np.abs(out)) <= 1.0


def test_mixer_track_panning_and_volume() -> None:
    track = MixerTrack("test_track", "Test", sample_rate=44100)
    audio = np.ones((512,), dtype=np.float32)

    # Center pan
    track.pan = 0.0
    track.volume = 1.0
    out = track.process_block(audio)
    assert out.shape == (512, 2)
    # Balanced L and R
    assert np.isclose(out[0, 0], out[0, 1], atol=1e-3)
    assert track.meter.peak_l > 0.0

    # Hard left pan
    track.pan = -1.0
    out_left = track.process_block(audio)
    assert out_left[0, 0] > 0.8
    assert np.isclose(out_left[0, 1], 0.0, atol=1e-3)


def test_mixer_engine_solo_and_mute() -> None:
    mixer = MixerEngine(sample_rate=44100)
    num_frames = 256
    track_buffers = {
        "synth": np.full((num_frames,), 0.5, dtype=np.float32),
        "drums": np.full((num_frames,), 0.5, dtype=np.float32),
    }

    # Normal mix
    out_normal = mixer.mix_tracks(track_buffers, num_frames)
    assert out_normal.shape == (num_frames, 2)
    assert mixer.master_meter.peak_l > 0.0

    # Mute drums
    mixer.set_track_mute("drums", True)
    out_muted = mixer.mix_tracks(track_buffers, num_frames)
    assert np.max(np.abs(out_muted)) < np.max(np.abs(out_normal))
    mixer.set_track_mute("drums", False)

    # Solo drums
    mixer.set_track_solo("drums", True)
    mixer.mix_tracks(track_buffers, num_frames)
    synth_track = mixer.get_track("synth")
    drums_track = mixer.get_track("drums")
    assert synth_track is not None and synth_track.meter.peak_l == 0.0
    assert drums_track is not None and drums_track.meter.peak_l > 0.0
