import logging
import sys

from PySide6.QtWidgets import QApplication

from music_master.audio.audio_stream import AudioStream
from music_master.audio.engine import AudioEngine
from music_master.config import Config
from music_master.input.keyboard import KeyboardController
from music_master.instruments.registry import InstrumentRegistry
from music_master.ui.themes.theme import DARK_THEME_QSS
from music_master.ui.windows.main_window import MainWindow
from music_master.utils.logging import setup_logging

logger = logging.getLogger(__name__)


def main() -> int:
    config = Config()
    setup_logging(config)
    logger.info("Starting Music Master v%s...", config.version)

    app = QApplication(sys.argv)
    app.setApplicationName(config.app_name)
    app.setStyleSheet(DARK_THEME_QSS)

    # Initialize audio engine and manager
    audio_engine = AudioEngine(
        sample_rate=config.audio.sample_rate,
        buffer_size=config.audio.buffer_size,
        channels=config.audio.channels,
        polyphony=config.audio.polyphony,
        master_volume=config.audio.master_volume,
    )
    audio_stream = AudioStream(audio_engine)
    keyboard_controller = KeyboardController()
    instrument_registry = InstrumentRegistry()

    window = MainWindow(
        config=config,
        audio_engine=audio_engine,
        audio_stream=audio_stream,
        keyboard_controller=keyboard_controller,
        instrument_registry=instrument_registry,
    )

    if config.ui.start_maximized:
        window.showMaximized()
    else:
        window.show()

    logger.info("Music Master window shown successfully.")
    return app.exec()
