from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from music_master.input.keyboard import KeyboardController
from music_master.theory.ragas import INITIAL_RAGAS
from music_master.ui.widgets.virtual_keyboard import VirtualKeyboardWidget


class HarmoniumPage(QWidget):
    """Harmonium playing studio with sargam mapping, raga guide, and drone controls."""

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

        # Header bar
        header_card = QFrame()
        header_card.setProperty("class", "Card")
        h_layout = QHBoxLayout(header_card)
        h_layout.setContentsMargins(16, 12, 16, 12)

        title = QLabel("Harmonium Studio")
        title.setStyleSheet("font-size: 18px; font-weight: 700; color: #FFFFFF;")
        h_layout.addWidget(title)

        h_layout.addSpacing(20)

        # Raga selector
        raga_lbl = QLabel("Guide Raga:")
        self.raga_combo = QComboBox()
        self.raga_combo.addItem("Select Raga (Optional)")
        for raga in INITIAL_RAGAS:
            self.raga_combo.addItem(f"{raga.name} ({raga.thaat})", raga)
        self.raga_combo.currentIndexChanged.connect(self._on_raga_selected)
        h_layout.addWidget(raga_lbl)
        h_layout.addWidget(self.raga_combo)

        h_layout.addStretch()

        # Octave shift buttons
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

        # Raga Info Display Panel
        self.info_panel = QFrame()
        self.info_panel.setProperty("class", "Card")
        info_layout = QHBoxLayout(self.info_panel)
        info_layout.setContentsMargins(16, 10, 16, 10)
        self.lbl_aroha = QLabel("Aroha: -")
        self.lbl_avaroha = QLabel("Avaroha: -")
        self.lbl_prahar = QLabel("Time: Any")
        self.lbl_aroha.setStyleSheet("color: #38BDF8; font-weight: 600;")
        self.lbl_avaroha.setStyleSheet("color: #A78BFA; font-weight: 600;")
        self.lbl_prahar.setStyleSheet("color: #94A3B8;")

        info_layout.addWidget(self.lbl_aroha)
        info_layout.addSpacing(20)
        info_layout.addWidget(self.lbl_avaroha)
        info_layout.addStretch()
        info_layout.addWidget(self.lbl_prahar)
        layout.addWidget(self.info_panel)

        # Virtual Keyboard representation
        self.virtual_keyboard = VirtualKeyboardWidget(start_midi=48, num_keys=37)  # C3 to C6
        self._update_keyboard_labels()
        layout.addWidget(self.virtual_keyboard)

        # Controls & Shortcut Guide Card
        guide_card = QFrame()
        guide_card.setProperty("class", "Card")
        g_layout = QVBoxLayout(guide_card)
        g_layout.setContentsMargins(16, 14, 16, 14)

        g_title = QLabel("Laptop Keyboard Sargam Controls")
        g_title.setProperty("class", "CardTitle")
        g_layout.addWidget(g_title)

        shortcuts_text = QLabel(
            "<b>White Keys (Shuddha Swaras):</b> [A]=Sa, [S]=Re, [D]=Ga, [F]=Ma, [G]=Pa, [H]=Dha, [J]=Ni, [K]=Ṡa, [L]=Ṙe<br>"
            "<b>Black Keys (Vikrit Swaras):</b> [W]=re (komal), [E]=ga (komal), [T]=ma' (tivra), [Y]=dha (komal), [U]=ni (komal)<br>"
            "<b>Quick Controls:</b> [Up/Down]=Octave Shift, [Space]=Sustain / Drone, [Esc]=Panic (Stop all notes)"
        )
        shortcuts_text.setStyleSheet("color: #94A3B8; font-size: 12px; margin-top: 4px;")
        g_layout.addWidget(shortcuts_text)
        layout.addWidget(guide_card)

        layout.addStretch()

        # Connect controller signals
        self.keyboard_controller.octave_changed_signal.connect(self._on_octave_changed)

    def _update_keyboard_labels(self) -> None:
        # Base tonic C4 = 60
        labels = {
            60: "A: Sa",
            61: "W: re",
            62: "S: Re",
            63: "E: ga",
            64: "D: Ga",
            65: "F: Ma",
            66: "T: ma'",
            67: "G: Pa",
            68: "Y: dha",
            69: "H: Dha",
            70: "U: ni",
            71: "J: Ni",
            72: "K: Ṡa",
            73: "O: ṙe",
            74: "L: Ṙe",
            75: "P: ġa",
            76: ";: Ġa",
        }
        self.virtual_keyboard.set_key_labels(labels)

    def _on_octave_changed(self, offset: int) -> None:
        self.lbl_oct_val.setText(f"{offset:+d}" if offset != 0 else "0")

    def _on_raga_selected(self, index: int) -> None:
        data = self.raga_combo.currentData()
        if data:
            self.lbl_aroha.setText(f"Aroha: {data.aroha}")
            self.lbl_avaroha.setText(f"Avaroha: {data.avaroha}")
            self.lbl_prahar.setText(
                f"Prahar: {data.time_of_day} | Vadi: {data.vadi}, Samvadi: {data.samvadi}"
            )
        else:
            self.lbl_aroha.setText("Aroha: -")
            self.lbl_avaroha.setText("Avaroha: -")
            self.lbl_prahar.setText("Time: Any")
