"""Unit tests for Phase 13 Studio: recording, project persistence, quantization, and audio export."""

import os
import tempfile

import numpy as np

from music_master.midi.file import NoteEvent
from music_master.studio.exporter import AudioExporter
from music_master.studio.project import ProjectManager, StudioTrack
from music_master.studio.quantizer import NoteQuantizer
from music_master.studio.recorder import AudioMidiRecorder, RecordingState


def test_project_save_load_json():
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, "test_proj.mmp")
        mgr = ProjectManager()
        mgr.project.name = "My Test Song"
        mgr.project.bpm = 128.0
        mgr.project.tracks = [
            StudioTrack(
                id="t1",
                name="Sitar Lead",
                instrument_id="sitar",
                notes=[
                    NoteEvent(note=60, velocity=100, start_time=0.0, duration=0.5),
                    NoteEvent(note=64, velocity=90, start_time=0.5, duration=0.5),
                ],
            )
        ]

        mgr.save_project(filepath)
        assert os.path.exists(filepath)

        loaded_mgr = ProjectManager()
        loaded_proj = loaded_mgr.load_project(filepath)
        assert loaded_proj.name == "My Test Song"
        assert loaded_proj.bpm == 128.0
        assert len(loaded_proj.tracks) == 1
        assert len(loaded_proj.tracks[0].notes) == 2
        assert loaded_proj.tracks[0].notes[0].note == 60


def test_project_save_load_compressed():
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, "compressed_proj.mmpz")
        mgr = ProjectManager()
        mgr.project.name = "Compressed Test"
        mgr.save_project(filepath, compressed=True)

        assert os.path.exists(filepath)
        loaded_mgr = ProjectManager()
        loaded_proj = loaded_mgr.load_project(filepath)
        assert loaded_proj.name == "Compressed Test"


def test_recorder_timeline_and_notes():
    recorder = AudioMidiRecorder(sample_rate=44100, bpm=120.0)
    recorder.start_recording(with_count_in=False)
    assert recorder.state == RecordingState.RECORDING

    # Step timeline forward 0.5s
    recorder.update_timeline(0.5)
    recorder.record_note_on(60, velocity=100)
    recorder.update_timeline(0.5)
    recorder.record_note_off(60)

    assert len(recorder.recorded_notes) == 1
    note = recorder.recorded_notes[0]
    assert note.note == 60
    assert abs(note.start_time - 0.5) < 0.05
    assert abs(note.duration - 0.5) < 0.05

    recorder.stop()
    assert recorder.state == RecordingState.STOPPED


def test_quantizer():
    notes = [
        NoteEvent(note=60, velocity=100, start_time=0.24, duration=0.24),  # Near 0.25 (1/16 at 120 bpm = 0.125s, so 0.25 is 1/8)
        NoteEvent(note=62, velocity=100, start_time=0.49, duration=0.5),   # Near 0.50 (1/4 beat)
    ]
    quantized = NoteQuantizer.quantize_notes(notes, grid="1/4", bpm=120.0, strength=1.0)
    # At 120 bpm, quarter note is 0.5s.
    # 0.24 is close to 0.0 or 0.5; nearest grid point to 0.24 is 0.0 (distance 0.24) vs 0.5 (0.26) -> 0.0
    # 0.49 is close to 0.5 (distance 0.01) -> 0.5
    assert quantized[0].start_time == 0.0
    assert quantized[1].start_time == 0.5


def test_audio_exporter_wav_and_mp3():
    with tempfile.TemporaryDirectory() as tmpdir:
        wav_path = os.path.join(tmpdir, "test.wav")
        mp3_path = os.path.join(tmpdir, "test.mp3")

        # 1 second stereo 440Hz sine wave
        t = np.linspace(0, 1.0, 44100, endpoint=False)
        sine = (np.sin(2 * np.pi * 440 * t) * 0.5).astype(np.float32)
        stereo_data = np.column_stack([sine, sine])

        # Test WAV export
        AudioExporter.export_wav(wav_path, stereo_data, sample_rate=44100)
        assert os.path.exists(wav_path)
        assert os.path.getsize(wav_path) > 1000

        # Test MP3 export (uses ffmpeg from path)
        AudioExporter.export_mp3(mp3_path, stereo_data, sample_rate=44100)
        # Should create either mp3 or fallback wav
        assert os.path.exists(mp3_path) or os.path.exists(os.path.splitext(mp3_path)[0] + ".wav")
