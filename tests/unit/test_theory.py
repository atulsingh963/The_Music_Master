from music_master.theory.notes import midi_to_note_name, midi_to_swara
from music_master.theory.ragas import INITIAL_RAGAS


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


def test_initial_ragas_loaded():
    assert len(INITIAL_RAGAS) >= 8
    yaman = next(r for r in INITIAL_RAGAS if r.name.startswith("Yaman"))
    assert yaman.thaat == "Kalyan"
    assert yaman.vadi == "Ga"
