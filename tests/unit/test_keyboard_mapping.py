from music_master.input.key_mapping import get_harmonium_default_profile, get_piano_default_profile
from music_master.input.keyboard import KeyboardController


def test_harmonium_profile_mapping():
    profile = get_harmonium_default_profile()
    # A = Sa (60)
    assert profile.get_note("A") == 60
    assert profile.get_label("A") == "Sa"
    # S = Re (62)
    assert profile.get_note("S") == 62
    # W = komal Re (61)
    assert profile.get_note("W") == 61
    # Octave shift +1
    assert profile.get_note("A", octave_shift=1) == 72
    # Transpose +2
    assert profile.get_note("A", transpose_shift=2) == 62


def test_piano_profile_mapping():
    profile = get_piano_default_profile()
    assert profile.get_note("A") == 60
    assert profile.get_note("W") == 61
    assert profile.get_note("K") == 72


def test_keyboard_controller_state():
    controller = KeyboardController()
    assert controller.active_profile_name == "harmonium"

    received_notes = []
    controller.note_on_signal.connect(lambda note, vel: received_notes.append((note, vel)))

    # Direct profile note resolution
    note = controller.get_active_profile().get_note("A")
    assert note == 60

    controller.change_octave(1)
    assert controller.octave_offset == 1
    note_shifted = controller.get_active_profile().get_note("A", controller.octave_offset)
    assert note_shifted == 72
