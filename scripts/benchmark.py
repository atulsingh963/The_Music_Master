"""Performance and CPU benchmark for Music Master real-time audio pipeline."""

import time

from music_master.audio.engine import AudioEngine


def benchmark_audio_rendering():
    """Profiles the real-time synthesis loop to ensure CPU usage remains comfortably below buffer budget."""
    sample_rate = 44100
    buffer_size = 512
    # Buffer time limit in seconds: 512 / 44100 = 0.0116s (11.6ms)
    max_budget_seconds = buffer_size / sample_rate

    engine = AudioEngine(sample_rate=sample_rate, buffer_size=buffer_size)

    # Enable multiple simultaneous sound engines: Metronome, Drums, Tanpura, Tabla, and Polyphonic voices
    engine.tanpura.set_tonic(60)
    engine.tanpura.set_pattern("pa")
    engine.tanpura.start()
    engine.metronome.set_bpm(130.0)
    engine.metronome.start()
    engine.drum_sequencer.play()

    # Trigger 8 active voices
    for note in [60, 64, 67, 71, 72, 76, 79, 83]:
        engine.note_on(note, velocity=100)

    # Warm-up
    for _ in range(10):
        engine.render_block(buffer_size)

    # Measure 100 blocks
    num_blocks = 100
    start = time.perf_counter()
    for _ in range(num_blocks):
        engine.render_block(buffer_size)
    elapsed = time.perf_counter() - start

    time_per_block = elapsed / num_blocks
    cpu_load_percent = (time_per_block / max_budget_seconds) * 100.0

    print(f"\n[BENCHMARK] Time per {buffer_size}-frame block: {time_per_block*1000.0:.3f} ms")
    print(f"[BENCHMARK] Buffer budget: {max_budget_seconds*1000.0:.3f} ms")
    print(f"[BENCHMARK] Estimated Audio Thread CPU Load: {cpu_load_percent:.1f}%")

    # Audio rendering should easily run within real-time budget (< 50% CPU load on modern machines)
    assert time_per_block < max_budget_seconds, "Audio engine exceeded real-time budget!"


if __name__ == "__main__":
    benchmark_audio_rendering()
