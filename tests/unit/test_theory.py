"""Unit tests for Scales, Chords, Ragas, Talas, Tuning, and Metronome engine."""

import numpy as np

from music_master.theory.chords import CHORD_FORMULAS, create_chord
from music_master.theory.metronome import MetronomeEngine
from music_master.theory.notes import midi_to_note_name, midi_to_swara
from music_master.theory.ragas import RagaRegistry
from music_master.theory.scales import THAATS, WESTERN_SCALES
from music_master.theory.talas import TALAS, get_tala
from music_master.theory.tuning import TUNING_SYSTEMS, TuningEngine


def test_notes_western_conversion():
    assert midi_to_note_name(60) == "C4"
    assert midi_to_note_name(69) == "A4"
    assert midi_to_note_name(72) == "C5"


def test_notes_sargam_conversion():
    assert midi_to_swara(60) == "Sa"
    assert midi_to_swara(62) == "Re"
    assert midi_to_swara(64) == "Ga"
    assert midi_to_swara(65) == "Ma"
    assert midi_to_swara(67) == "Pa"
    assert midi_to_swara(69) == "Dha"
    assert midi_to_swara(71) == "Ni"


def test_scales_and_thaats():
    assert len(WESTERN_SCALES) >= 10
    major = WESTERN_SCALES["major"]
    assert major.get_notes("C") == ["C", "D", "E", "F", "G", "A", "B"]
    c_midi = major.get_midi_notes(root_midi=60, octaves=1)
    assert c_midi == [60, 62, 64, 65, 67, 69, 71, 72]
    assert major.contains_midi(60, 64)  # E is in C major
    assert not major.contains_midi(60, 63)  # Eb is not

    # Bhatkhande 10 Thaats
    assert len(THAATS) == 10
    assert "bilawal" in THAATS
    assert "kalyan" in THAATS
    assert "bhairav" in THAATS
    assert "bhairavi" in THAATS
    assert "todi" in THAATS
    assert "marwa" in THAATS

    kalyan = THAATS["kalyan"]
    assert kalyan.intervals == [0, 2, 4, 6, 7, 9, 11]  # Tivra Ma (6)


def test_chords_and_inversions():
    assert "maj" in CHORD_FORMULAS
    assert "min" in CHORD_FORMULAS
    assert "7" in CHORD_FORMULAS

    # C Major Triad
    c_maj = create_chord(root="C", chord_type="maj", inversion=0)
    assert c_maj is not None
    assert c_maj.notes == ["C", "E", "G"]
    assert c_maj.get_midi_notes(root_midi=60) == [60, 64, 67]

    # C Major 1st Inversion (E - G - C)
    c_maj_inv1 = create_chord(root="C", chord_type="maj", inversion=1)
    assert c_maj_inv1 is not None
    assert c_maj_inv1.notes == ["E", "G", "C"]
    assert c_maj_inv1.get_midi_notes(root_midi=60) == [64, 67, 72]

    # A Minor 7th
    a_min7 = create_chord(root="A", chord_type="min7")
    assert a_min7 is not None
    assert a_min7.notes == ["A", "C", "E", "G"]


def test_ragas_and_validation():
    registry = RagaRegistry()
    assert len(registry.get_all()) >= 8

    yaman = registry.get("yaman")
    assert yaman is not None
    assert yaman.thaat == "Kalyan"
    assert yaman.vadi == "Ga"
    assert yaman.validate_note(6)  # Tivra Ma
    assert not yaman.validate_note(5)  # Shuddha Ma not in Yaman scale

    # Validate note sequence
    assert registry.validate_swara_sequence("yaman", [0, 2, 4, 6, 7])
    assert not registry.validate_swara_sequence("yaman", [0, 1, 3])  # Komal Re/Ga not in Yaman


def test_talas():
    assert len(TALAS) >= 6
    teental = get_tala("teental")
    assert teental is not None
    assert teental.matras == 16
    assert teental.vibhag_structure == [4, 4, 4, 4]
    cycle = teental.get_cycle()
    assert len(cycle) == 16
    assert cycle[0].is_sam
    assert cycle[0].bol == "Dha"
    assert cycle[8].is_khali  # 9th beat (index 8) is Khali

    rupak = get_tala("rupak")
    assert rupak is not None
    assert rupak.matras == 7
    rupak_cycle = rupak.get_cycle()
    assert rupak_cycle[0].is_khali  # Rupak Sam is Khali


def test_tuning_engine():
    assert "12-tet" in TUNING_SYSTEMS
    assert "just_intonation" in TUNING_SYSTEMS
    assert "indian_shruti" in TUNING_SYSTEMS

    engine = TuningEngine(reference_pitch=440.0, system_id="12-tet")
    assert abs(engine.get_frequency(69) - 440.0) < 1e-4  # A4 = 440 Hz
    assert abs(engine.get_frequency(60) - 261.625) < 0.1  # C4 ~= 261.63 Hz

    # Change to Indian Shruti tuning
    engine.set_system("indian_shruti")
    engine.set_tonic(60)  # C4 as Sa
    sa_freq = engine.get_frequency(60)
    pa_freq = engine.get_frequency(67)  # G4 = Pa (ratio 3/2 = 1.5)
    assert abs((pa_freq / sa_freq) - 1.5) < 1e-4


def test_metronome_engine():
    metro = MetronomeEngine(sample_rate=44100, bpm=120.0, beats_per_bar=4)
    assert not metro.is_active

    metro.start()
    assert metro.is_active

    # Render 1 second of audio
    audio = metro.process_frames(44100)
    assert len(audio) == 44100
    assert np.any(audio != 0.0)

    metro.stop()
    assert not metro.is_active
    silence = metro.process_frames(512)
    assert np.all(silence == 0.0)
