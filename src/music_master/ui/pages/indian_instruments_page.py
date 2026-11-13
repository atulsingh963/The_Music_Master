"""Indian Instruments Hub page: Tanpura Drone control, Tabla bol pads & Tala accompaniment, and Sitar studio."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from music_master.audio.engine import AudioEngine
from music_master.input.keyboard import KeyboardController
from music_master.instruments.indian.tabla import BOL_DEFINITIONS
from music_master.theory.talas import TALAS, Tala
from music_master.ui.widgets.virtual_keyboard import VirtualKeyboardWidget


class IndianInstrumentsPage(QWidget):
    """Integrated Indian Classical music studio supporting Tanpura, Tabla, and Sitar."""

    def __init__(
        self,
        audio_engine: AudioEngine,
        keyboard_controller: KeyboardController,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.audio_engine = audio_engine
        self.keyboard_controller = keyboard_controller
        self._init_ui()

    def _init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(14)

        # Header Card
        header_card = QFrame()
        header_card.setProperty("class", "Card")
        h_layout = QHBoxLayout(header_card)
        h_layout.setContentsMargins(16, 12, 16, 12)

        title = QLabel("Indian Classical Studio")
        title.setStyleSheet("font-size: 20px; font-weight: 700; color: #38BDF8;")
        h_layout.addWidget(title)

        h_layout.addSpacing(20)

        # Active Melodic Instrument Toggle
        inst_lbl = QLabel("Lead Instrument:")
        self.inst_combo = QComboBox()
        self.inst_combo.addItem("Harmonium (Reed)", "harmonium")
        self.inst_combo.addItem("Sitar (Plucked & Jawari)", "sitar")
        self.inst_combo.currentIndexChanged.connect(self._on_instrument_changed)
        h_layout.addWidget(inst_lbl)
        h_layout.addWidget(self.inst_combo)

        h_layout.addStretch()

        # Octave adjustment
        oct_lbl = QLabel("Octave:")
        self.btn_oct_down = QPushButton("-1")
        self.btn_oct_down.setProperty("class", "SecondaryButton")
        self.btn_oct_down.clicked.connect(lambda: self.keyboard_controller.change_octave(-1))

        self.lbl_oct_val = QLabel("0")
        self.lbl_oct_val.setStyleSheet(
            "font-weight: 700; color: #38BDF8; min-width: 20px; text-align: center;"
        )

        self.btn_oct_up = QPushButton("+1")
        self.btn_oct_up.setProperty("class", "SecondaryButton")
        self.btn_oct_up.clicked.connect(lambda: self.keyboard_controller.change_octave(1))

        h_layout.addWidget(oct_lbl)
        h_layout.addWidget(self.btn_oct_down)
        h_layout.addWidget(self.lbl_oct_val)
        h_layout.addWidget(self.btn_oct_up)

        main_layout.addWidget(header_card)

        # Split Section: Tanpura Drone on Left, Tabla Rhythm Studio on Right
        panels_row = QHBoxLayout()
        panels_row.setSpacing(14)

        # 1. TANPURA DRONE CARD
        tanpura_card = QFrame()
        tanpura_card.setProperty("class", "Card")
        t_layout = QVBoxLayout(tanpura_card)
        t_layout.setContentsMargins(16, 14, 16, 14)
        t_layout.setSpacing(10)

        t_title = QLabel("Tanpura Drone Synthesis")
        t_title.setStyleSheet("font-size: 15px; font-weight: 700; color: #F59E0B;")
        t_layout.addWidget(t_title)

        # Controls Row: Tonic & Tuning Pattern
        row1 = QHBoxLayout()
        lbl_tonic = QLabel("Sa (Tonic):")
        self.tanpura_tonic_combo = QComboBox()
        for idx, name in enumerate(
            ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        ):
            self.tanpura_tonic_combo.addItem(f"{name} (Kharaj)", 48 + idx)
        self.tanpura_tonic_combo.currentIndexChanged.connect(self._on_tanpura_tonic_changed)
        row1.addWidget(lbl_tonic)
        row1.addWidget(self.tanpura_tonic_combo)

        lbl_pattern = QLabel("String 1:")
        self.tanpura_pattern_combo = QComboBox()
        self.tanpura_pattern_combo.addItem("Pa - Sa - Sa - Sa (Standard)", "pa")
        self.tanpura_pattern_combo.addItem("Ma - Sa - Sa - Sa (Tivra/Shuddha Ma)", "ma")
        self.tanpura_pattern_combo.addItem("Ni - Sa - Sa - Sa (Komal/Shuddha Ni)", "ni")
        self.tanpura_pattern_combo.currentIndexChanged.connect(self._on_tanpura_pattern_changed)
        row1.addWidget(lbl_pattern)
        row1.addWidget(self.tanpura_pattern_combo)
        t_layout.addLayout(row1)

        # Tanpura Tempo & Volume sliders
        row2 = QHBoxLayout()
        lbl_speed = QLabel("Pluck Speed:")
        self.tanpura_speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.tanpura_speed_slider.setRange(12, 45)
        self.tanpura_speed_slider.setValue(24)
        self.tanpura_speed_slider.valueChanged.connect(
            lambda v: self.audio_engine.tanpura.set_tempo(float(v))
        )
        row2.addWidget(lbl_speed)
        row2.addWidget(self.tanpura_speed_slider)

        lbl_tvol = QLabel("Drone Vol:")
        self.tanpura_vol_slider = QSlider(Qt.Orientation.Horizontal)
        self.tanpura_vol_slider.setRange(0, 100)
        self.tanpura_vol_slider.setValue(75)
        self.tanpura_vol_slider.valueChanged.connect(
            lambda v: self.audio_engine.tanpura.set_volume(v / 100.0)
        )
        row2.addWidget(lbl_tvol)
        row2.addWidget(self.tanpura_vol_slider)
        t_layout.addLayout(row2)

        # Tanpura Start/Stop Toggle
        self.btn_tanpura_toggle = QPushButton("Start Tanpura Drone")
        self.btn_tanpura_toggle.setProperty("class", "PrimaryButton")
        self.btn_tanpura_toggle.setStyleSheet(
            "background-color: #D97706; color: #FFFFFF; font-weight: 700;"
        )
        self.btn_tanpura_toggle.clicked.connect(self._toggle_tanpura)
        t_layout.addWidget(self.btn_tanpura_toggle)
        t_layout.addStretch()

        panels_row.addWidget(tanpura_card, 1)

        # 2. TABLA RHYTHM STUDIO CARD
        tabla_card = QFrame()
        tabla_card.setProperty("class", "Card")
        tb_layout = QVBoxLayout(tabla_card)
        tb_layout.setContentsMargins(16, 14, 16, 14)
        tb_layout.setSpacing(10)

        tb_title = QLabel("Tabla Drum Pads & Tala Rhythm")
        tb_title.setStyleSheet("font-size: 15px; font-weight: 700; color: #10B981;")
        tb_layout.addWidget(tb_title)

        # Tala Selector
        tala_row = QHBoxLayout()
        tala_lbl = QLabel("Tala Cycle:")
        self.tala_combo = QComboBox()
        for t_obj in TALAS.values():
            self.tala_combo.addItem(f"{t_obj.name} ({t_obj.matras} Matras)", t_obj)
        self.tala_combo.currentIndexChanged.connect(self._on_tala_selected)
        tala_row.addWidget(tala_lbl)
        tala_row.addWidget(self.tala_combo)
        tb_layout.addLayout(tala_row)

        # Tala display sequence bar
        self.tala_theka_lbl = QLabel("Theka: " + " - ".join(TALAS["teental"].theka_bols))
        self.tala_theka_lbl.setWordWrap(True)
        self.tala_theka_lbl.setStyleSheet("color: #38BDF8; font-size: 11px;")
        tb_layout.addWidget(self.tala_theka_lbl)

        # Interactive Tabla Bol Trigger Pads
        pads_grid = QGridLayout()
        pads_grid.setSpacing(6)

        bol_list = list(BOL_DEFINITIONS.values())
        for idx, bdef in enumerate(bol_list):
            pad_btn = QPushButton(f"{bdef.name}\n({bdef.drum.capitalize()})")
            pad_btn.setProperty("class", "SecondaryButton")
            pad_btn.setStyleSheet(
                "padding: 8px 4px; font-weight: 700; "
                + (
                    "border-left: 3px solid #10B981;"
                    if bdef.drum == "dayan"
                    else "border-left: 3px solid #38BDF8;"
                )
            )
            bol_id = bdef.id
            pad_btn.clicked.connect(
                lambda _, bid=bol_id: self.audio_engine.tabla.trigger_bol(bid, 0.9)
            )
            r = idx // 3
            c = idx % 3
            pads_grid.addWidget(pad_btn, r, c)

        tb_layout.addLayout(pads_grid)
        panels_row.addWidget(tabla_card, 1)

        main_layout.addLayout(panels_row)

        # Virtual Keyboard for Sitar / Harmonium Lead Playing
        self.virtual_keyboard = VirtualKeyboardWidget(start_midi=48, num_keys=37)
        self._update_keyboard_labels()
        main_layout.addWidget(self.virtual_keyboard)

        # Connect keyboard controller signals
        self.keyboard_controller.octave_changed_signal.connect(self._on_octave_changed)
        self.virtual_keyboard.note_pressed.connect(self._on_virtual_key_pressed)
        self.virtual_keyboard.note_released.connect(self._on_virtual_key_released)

    def _on_instrument_changed(self) -> None:
        inst_id = self.inst_combo.currentData()
        self.audio_engine.set_instrument(inst_id)

    def _toggle_tanpura(self) -> None:
        if self.audio_engine.tanpura.is_active:
            self.audio_engine.tanpura.stop()
            self.btn_tanpura_toggle.setText("Start Tanpura Drone")
            self.btn_tanpura_toggle.setStyleSheet(
                "background-color: #D97706; color: #FFFFFF; font-weight: 700;"
            )
        else:
            self.audio_engine.tanpura.start()
            self.btn_tanpura_toggle.setText("Stop Tanpura Drone")
            self.btn_tanpura_toggle.setStyleSheet(
                "background-color: #EF4444; color: #FFFFFF; font-weight: 700;"
            )

    def _on_tanpura_tonic_changed(self) -> None:
        midi = self.tanpura_tonic_combo.currentData()
        self.audio_engine.tanpura.set_tonic(midi)

    def _on_tanpura_pattern_changed(self) -> None:
        pattern = self.tanpura_pattern_combo.currentData()
        self.audio_engine.tanpura.set_pattern(pattern)

    def _on_tala_selected(self) -> None:
        tala: Tala = self.tala_combo.currentData()
        if tala:
            self.tala_theka_lbl.setText("Theka: " + " - ".join(tala.theka_bols))

    def _on_octave_changed(self, new_octave: int) -> None:
        self.lbl_oct_val.setText(f"{new_octave:+d}" if new_octave != 0 else "0")

    def _update_keyboard_labels(self) -> None:
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
        }
        self.virtual_keyboard.set_key_labels(labels)

    def _on_virtual_key_pressed(self, midi_note: int) -> None:
        self.audio_engine.note_on(midi_note, 100)

    def _on_virtual_key_released(self, midi_note: int) -> None:
        self.audio_engine.note_off(midi_note)
