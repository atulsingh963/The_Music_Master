import logging

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from music_master.audio.audio_stream import AudioStream
from music_master.audio.engine import AudioEngine
from music_master.config import Config
from music_master.input.keyboard import KeyboardController
from music_master.instruments.registry import InstrumentRegistry
from music_master.ui.pages.dashboard_page import DashboardPage
from music_master.ui.pages.harmonium_page import HarmoniumPage
from music_master.ui.pages.indian_instruments_page import IndianInstrumentsPage
from music_master.ui.pages.instrument_library_page import InstrumentLibraryPage
from music_master.ui.pages.music_theory_page import MusicTheoryPage
from music_master.ui.pages.piano_page import PianoPage
from music_master.ui.pages.placeholder_page import PlaceholderPage

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main application window for Music Master studio."""

    def __init__(
        self,
        config: Config,
        audio_engine: AudioEngine,
        audio_stream: AudioStream,
        keyboard_controller: KeyboardController,
        instrument_registry: InstrumentRegistry,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.config = config
        self.audio_engine = audio_engine
        self.audio_stream = audio_stream
        self.keyboard_controller = keyboard_controller
        self.instrument_registry = instrument_registry

        self.setWindowTitle(f"{config.app_name} v{config.version} - Studio")
        self.resize(config.ui.window_width, config.ui.window_height)

        self._init_ui()
        self._connect_signals()

    def _init_ui(self) -> None:
        # Central widget container
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Left Sidebar
        sidebar_frame = QFrame()
        sidebar_frame.setObjectName("SidebarFrame")
        sidebar_frame.setFixedWidth(210)
        sidebar_layout = QVBoxLayout(sidebar_frame)
        sidebar_layout.setContentsMargins(12, 16, 12, 16)
        sidebar_layout.setSpacing(6)

        # Logo / App Title
        app_title = QLabel("MUSIC MASTER")
        app_title.setStyleSheet("font-size: 16px; font-weight: 800; color: #38BDF8; padding: 4px;")
        app_tagline = QLabel("Virtual Studio")
        app_tagline.setStyleSheet(
            "font-size: 11px; color: #64748B; padding-left: 4px; margin-bottom: 12px;"
        )
        sidebar_layout.addWidget(app_title)
        sidebar_layout.addWidget(app_tagline)

        # Nav Buttons
        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)

        self.pages_stack = QStackedWidget()

        nav_items = [
            ("Dashboard", self._create_dashboard_page),
            ("Harmonium", self._create_harmonium_page),
            ("Piano", self._create_piano_page),
            ("Indian Studio", self._create_indian_studio_page),
            ("Instrument Library", self._create_library_page),
            (
                "Drum Machine",
                lambda: PlaceholderPage(
                    "Drum Machine",
                    "Acoustic and electronic rhythm kits with step sequencer.",
                    "Phase 8",
                ),
            ),
            (
                "Keyboard Mapper",
                lambda: PlaceholderPage(
                    "Keyboard Mapper",
                    "Interactive key binding remapper and controller profile manager.",
                    "Phase 4/7",
                ),
            ),
            ("Music Theory", self._create_music_theory_page),
            (
                "Mixer",
                lambda: PlaceholderPage(
                    "Studio Mixer",
                    "Multi-track volume, pan, EQ, reverb, and compression.",
                    "Phase 11",
                ),
            ),
            (
                "Recorder",
                lambda: PlaceholderPage(
                    "Audio & MIDI Recorder",
                    "Non-destructive recording, overdub, and WAV/MIDI export.",
                    "Phase 13",
                ),
            ),
            (
                "MIDI Studio",
                lambda: PlaceholderPage(
                    "MIDI Studio",
                    "Hardware MIDI keyboard setup, routing, and channel mapping.",
                    "Phase 12",
                ),
            ),
            (
                "Settings",
                lambda: PlaceholderPage(
                    "Settings",
                    "Audio buffer, sample rate, latency configuration, and appearance.",
                    "Phase 1/15",
                ),
            ),
        ]

        for idx, (label, factory) in enumerate(nav_items):
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setProperty("class", "NavButton")
            self.nav_group.addButton(btn, idx)
            sidebar_layout.addWidget(btn)

            # Lazy or immediate page build
            page_widget = factory()
            self.pages_stack.addWidget(page_widget)

            if idx == 0:
                btn.setChecked(True)

        sidebar_layout.addStretch()

        # Panic button in sidebar
        self.btn_panic = QPushButton("PANIC (Esc)")
        self.btn_panic.setProperty("class", "DangerButton")
        self.btn_panic.clicked.connect(self.keyboard_controller.panic)
        sidebar_layout.addWidget(self.btn_panic)

        main_layout.addWidget(sidebar_frame)

        # 2. Right Workspace (Header + Stacked Pages)
        workspace_layout = QVBoxLayout()
        workspace_layout.setContentsMargins(0, 0, 0, 0)
        workspace_layout.setSpacing(0)

        # Top Header Bar
        header_frame = QFrame()
        header_frame.setObjectName("HeaderFrame")
        header_frame.setFixedHeight(54)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 0, 20, 0)

        self.lbl_active_mode = QLabel("Dashboard")
        self.lbl_active_mode.setObjectName("HeaderTitle")
        header_layout.addWidget(self.lbl_active_mode)
        header_layout.addStretch()

        # Audio stream status toggle
        self.btn_audio_toggle = QPushButton("Audio: Stopped")
        self.btn_audio_toggle.setProperty("class", "SecondaryButton")
        self.btn_audio_toggle.clicked.connect(self._toggle_audio_stream)
        header_layout.addWidget(self.btn_audio_toggle)

        workspace_layout.addWidget(header_frame)
        workspace_layout.addWidget(self.pages_stack)
        main_layout.addLayout(workspace_layout)

        # 3. Status Bar
        status_bar = QStatusBar(self)
        self.setStatusBar(status_bar)
        self.status_lbl_device = QLabel("Audio: Ready")
        self.status_lbl_buffer = QLabel(f"Buffer: {self.audio_engine.buffer_size} frames")
        self.status_lbl_rate = QLabel(f"Rate: {self.audio_engine.sample_rate} Hz")
        self.status_lbl_voices = QLabel("Active Voices: 0")

        status_bar.addWidget(self.status_lbl_device, 1)
        status_bar.addPermanentWidget(self.status_lbl_voices)
        status_bar.addPermanentWidget(self.status_lbl_buffer)
        status_bar.addPermanentWidget(self.status_lbl_rate)

        # Navigation switch handler
        self.nav_group.idClicked.connect(self._on_navigation_changed)

    def _create_dashboard_page(self) -> QWidget:
        return DashboardPage(self)

    def _create_harmonium_page(self) -> QWidget:
        self.harmonium_page = HarmoniumPage(self.keyboard_controller, self)
        return self.harmonium_page

    def _create_indian_studio_page(self) -> QWidget:
        self.indian_page = IndianInstrumentsPage(self.audio_engine, self.keyboard_controller, self)
        return self.indian_page

    def _create_piano_page(self) -> QWidget:
        self.piano_page = PianoPage(self.keyboard_controller, self)
        return self.piano_page

    def _create_library_page(self) -> QWidget:
        return InstrumentLibraryPage(self.instrument_registry, self)

    def _create_music_theory_page(self) -> QWidget:
        self.theory_page = MusicTheoryPage(self.audio_engine, self.keyboard_controller, self)
        return self.theory_page

    def _connect_signals(self) -> None:
        self.keyboard_controller.note_on_signal.connect(self._on_note_on)
        self.keyboard_controller.note_off_signal.connect(self._on_note_off)
        self.keyboard_controller.panic_signal.connect(self._on_panic)

    def _toggle_audio_stream(self) -> None:
        if self.audio_stream.is_active():
            self.audio_stream.stop()
            self.btn_audio_toggle.setText("Audio: Stopped")
            self.btn_audio_toggle.setStyleSheet("")
            self.status_lbl_device.setText("Audio: Stopped")
        else:
            success = self.audio_stream.start(self.config.audio.device_id)
            if success:
                self.btn_audio_toggle.setText("Audio: Running")
                self.btn_audio_toggle.setStyleSheet("background-color: #059669; color: white;")
                self.status_lbl_device.setText("Audio: Active (sounddevice output)")
            else:
                self.status_lbl_device.setText("Audio: Failed to open device")

    def _on_navigation_changed(self, button_id: int) -> None:
        self.pages_stack.setCurrentIndex(button_id)
        btn = self.nav_group.button(button_id)
        mode_text = btn.text() if btn else "Studio"
        self.lbl_active_mode.setText(mode_text)

        # Automatically select instrument according to page
        if mode_text == "Harmonium":
            self.audio_engine.set_instrument("harmonium")
            self.keyboard_controller.set_profile("harmonium")
        elif mode_text == "Piano":
            self.audio_engine.set_instrument("grand_piano")
            self.keyboard_controller.set_profile("grand_piano")
        elif mode_text == "Indian Studio":
            # Retain currently chosen Indian lead instrument (Harmonium or Sitar)
            if hasattr(self, "indian_page"):
                chosen_inst = self.indian_page.inst_combo.currentData() or "harmonium"
                self.audio_engine.set_instrument(chosen_inst)
            else:
                self.audio_engine.set_instrument("harmonium")
            self.keyboard_controller.set_profile("harmonium")

    def _on_note_on(self, note: int, velocity: int) -> None:
        self.audio_engine.note_on(note, velocity)
        self.status_lbl_voices.setText(f"Active Voices: {len(self.audio_engine.active_voices)}")
        if hasattr(self, "harmonium_page"):
            self.harmonium_page.virtual_keyboard.set_note_active(note, True)
        if hasattr(self, "piano_page"):
            self.piano_page.virtual_keyboard.set_note_active(note, True)
        if hasattr(self, "indian_page"):
            self.indian_page.virtual_keyboard.set_note_active(note, True)
        if hasattr(self, "theory_page"):
            self.theory_page.virtual_keyboard.set_note_active(note, True)

    def _on_note_off(self, note: int) -> None:
        self.audio_engine.note_off(note)
        self.status_lbl_voices.setText(f"Active Voices: {len(self.audio_engine.active_voices)}")
        if hasattr(self, "harmonium_page"):
            self.harmonium_page.virtual_keyboard.set_note_active(note, False)
        if hasattr(self, "piano_page"):
            self.piano_page.virtual_keyboard.set_note_active(note, False)
        if hasattr(self, "indian_page"):
            self.indian_page.virtual_keyboard.set_note_active(note, False)
        if hasattr(self, "theory_page"):
            self.theory_page.virtual_keyboard.set_note_active(note, False)

    def _on_panic(self) -> None:
        self.audio_engine.panic()
        self.status_lbl_voices.setText("Active Voices: 0")
        if hasattr(self, "harmonium_page"):
            self.harmonium_page.virtual_keyboard.clear_active_notes()
        if hasattr(self, "piano_page"):
            self.piano_page.virtual_keyboard.clear_active_notes()
        if hasattr(self, "indian_page"):
            self.indian_page.virtual_keyboard.clear_active_notes()
        if hasattr(self, "theory_page"):
            self.theory_page.virtual_keyboard.clear_active_notes()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self.keyboard_controller.panic()
            event.accept()
            return
        if event.key() == Qt.Key.Key_Space:
            self.audio_engine.set_sustain(True)
            event.accept()
            return
        if event.key() == Qt.Key.Key_Up:
            self.keyboard_controller.change_octave(1)
            event.accept()
            return
        if event.key() == Qt.Key.Key_Down:
            self.keyboard_controller.change_octave(-1)
            event.accept()
            return

        handled = self.keyboard_controller.handle_key_press(event)
        if not handled:
            super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Space:
            self.audio_engine.set_sustain(False)
            event.accept()
            return

        handled = self.keyboard_controller.handle_key_release(event)
        if not handled:
            super().keyReleaseEvent(event)

    def changeEvent(self, event) -> None:
        # Stop all held notes on focus loss
        if event.type() == event.Type.ActivationChange and not self.isActiveWindow():
            self.keyboard_controller.panic()
        super().changeEvent(event)

    def closeEvent(self, event) -> None:
        self.audio_stream.stop()
        self.keyboard_controller.panic()
        super().closeEvent(event)
