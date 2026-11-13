from PySide6.QtCore import Qt

from music_master.audio.audio_stream import AudioStream
from music_master.audio.engine import AudioEngine
from music_master.config import Config
from music_master.input.keyboard import KeyboardController
from music_master.instruments.registry import InstrumentRegistry
from music_master.ui.windows.main_window import MainWindow


def test_main_window_creation(qtbot):
    config = Config()
    audio_engine = AudioEngine()
    audio_stream = AudioStream(audio_engine)
    keyboard_controller = KeyboardController()
    registry = InstrumentRegistry()

    window = MainWindow(
        config=config,
        audio_engine=audio_engine,
        audio_stream=audio_stream,
        keyboard_controller=keyboard_controller,
        instrument_registry=registry,
    )
    qtbot.addWidget(window)

    assert window.windowTitle().startswith("Music Master")
    assert window.pages_stack.count() >= 10
    assert window.pages_stack.currentIndex() == 0


def test_main_window_navigation_switch(qtbot):
    config = Config()
    audio_engine = AudioEngine()
    audio_stream = AudioStream(audio_engine)
    keyboard_controller = KeyboardController()
    registry = InstrumentRegistry()

    window = MainWindow(
        config=config,
        audio_engine=audio_engine,
        audio_stream=audio_stream,
        keyboard_controller=keyboard_controller,
        instrument_registry=registry,
    )
    qtbot.addWidget(window)

    # Harmonium button is index 1
    btn_harmonium = window.nav_group.button(1)
    assert btn_harmonium is not None
    qtbot.mouseClick(btn_harmonium, Qt.MouseButton.LeftButton)

    assert window.pages_stack.currentIndex() == 1
    assert audio_engine.current_instrument_id == "harmonium"
    assert keyboard_controller.active_profile_name == "harmonium"

    # Piano button is index 2
    btn_piano = window.nav_group.button(2)
    assert btn_piano is not None
    qtbot.mouseClick(btn_piano, Qt.MouseButton.LeftButton)

    assert window.pages_stack.currentIndex() == 2
    assert audio_engine.current_instrument_id == "grand_piano"
    assert keyboard_controller.active_profile_name == "grand_piano"

    # Indian Studio button is index 3
    btn_indian = window.nav_group.button(3)
    assert btn_indian is not None
    qtbot.mouseClick(btn_indian, Qt.MouseButton.LeftButton)

    assert window.pages_stack.currentIndex() == 3
    assert keyboard_controller.active_profile_name == "harmonium"
    assert hasattr(window, "indian_page")

    # Music Theory button is index 6
    btn_theory = window.nav_group.button(6)
    assert btn_theory is not None
    qtbot.mouseClick(btn_theory, Qt.MouseButton.LeftButton)

    assert window.pages_stack.currentIndex() == 6
    assert hasattr(window, "theory_page")
