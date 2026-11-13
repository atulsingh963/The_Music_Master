from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from music_master.input.keyboard import KeyboardController
from music_master.ui.widgets.virtual_keyboard import VirtualKeyboardWidget


class PianoPage(QWidget):
    """Grand Piano studio with responsive virtual keyboard and velocity control."""

    def __init__(
        self, keyboard_controller: KeyboardController, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.keyboard_controller = keyboard_controller
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header controls
        header_card = QFrame()
        header_card.setProperty("class", "Card")
        h_layout = QHBoxLayout(header_card)
        h_layout.setContentsMargins(16, 12, 16, 12)

        title = QLabel("Grand Piano Studio")
        title.setStyleSheet("font-size: 18px; font-weight: 700; color: #FFFFFF;")
        h_layout.addWidget(title)

        h_layout.addStretch()

        # Octave controls
        oct_lbl = QLabel("Octave:")
        self.btn_oct_down = QPushButton("-1 (Down)")
        self.btn_oct_down.setProperty("class", "SecondaryButton")
        self.btn_oct_down.clicked.connect(lambda: self.keyboard_controller.change_octave(-1))

        self.lbl_oct_val = QLabel("0")
        self.lbl_oct_val.setStyleSheet(
            "font-weight: 700; color: #38BDF8; min-width: 20px; text-align: center;"
        )

        self.btn_oct_up = QPushButton("+1 (Up)")
        self.btn_oct_up.setProperty("class", "SecondaryButton")
        self.btn_oct_up.clicked.connect(lambda: self.keyboard_controller.change_octave(1))

        h_layout.addWidget(oct_lbl)
        h_layout.addWidget(self.btn_oct_down)
        h_layout.addWidget(self.lbl_oct_val)
        h_layout.addWidget(self.btn_oct_up)

        layout.addWidget(header_card)

        # Piano Virtual Keyboard representation (49 keys from C3=48 to C7=96)
        self.virtual_keyboard = VirtualKeyboardWidget(start_midi=48, num_keys=49)
        self._update_piano_labels()
        layout.addWidget(self.virtual_keyboard)

        # Guide card
        guide_card = QFrame()
        guide_card.setProperty("class", "Card")
        g_layout = QVBoxLayout(guide_card)
        g_layout.setContentsMargins(16, 14, 16, 14)

        g_title = QLabel("Piano Keyboard Shortcuts")
        g_title.setProperty("class", "CardTitle")
        g_layout.addWidget(g_title)

        shortcuts_text = QLabel(
            "<b>White Keys:</b> [A]=C4, [S]=D4, [D]=E4, [F]=F4, [G]=G4, [H]=A4, [J]=B4, [K]=C5, [L]=D5, [;]=E5<br>"
            "<b>Black Keys:</b> [W]=C#4, [E]=D#4, [T]=F#4, [Y]=G#4, [U]=A#4, [O]=C#5, [P]=D#5<br>"
            "<b>Pedal & Panic:</b> [Space]=Sustain Pedal, [Esc]=Panic (Stop all notes)"
        )
        shortcuts_text.setStyleSheet("color: #94A3B8; font-size: 12px; margin-top: 4px;")
        g_layout.addWidget(shortcuts_text)
        layout.addWidget(guide_card)

        layout.addStretch()

        self.keyboard_controller.octave_changed_signal.connect(self._on_octave_changed)

    def _update_piano_labels(self) -> None:
        labels = {
            60: "A: C4",
            61: "W: C#",
            62: "S: D4",
            63: "E: D#",
            64: "D: E4",
            65: "F: F4",
            66: "T: F#",
            67: "G: G4",
            68: "Y: G#",
            69: "H: A4",
            70: "U: A#",
            71: "J: B4",
            72: "K: C5",
            73: "O: C#",
            74: "L: D5",
            75: "P: D#",
            76: ";: E5",
        }
        self.virtual_keyboard.set_key_labels(labels)

    def _on_octave_changed(self, offset: int) -> None:
        self.lbl_oct_val.setText(f"{offset:+d}" if offset != 0 else "0")
