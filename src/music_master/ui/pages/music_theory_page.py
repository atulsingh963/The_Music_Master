"""Music Theory Page: Comprehensive exploration of Western scales, chords, Hindustani Thaats & Ragas, Tala cycles, and tuning systems."""

from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from music_master.audio.engine import AudioEngine
from music_master.input.keyboard import KeyboardController
from music_master.theory.chords import CHORD_FORMULAS, create_chord
from music_master.theory.notes import NOTE_NAMES
from music_master.theory.ragas import INITIAL_RAGAS, Raga
from music_master.theory.scales import THAATS, WESTERN_SCALES, ScaleDefinition
from music_master.theory.talas import TALAS, Tala
from music_master.theory.tuning import TUNING_SYSTEMS
from music_master.ui.widgets.virtual_keyboard import VirtualKeyboardWidget


class MusicTheoryPage(QWidget):
    """Integrated interactive music theory explorer for Indian and Western systems."""

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

        # Header Bar
        header_card = QFrame()
        header_card.setProperty("class", "Card")
        h_layout = QHBoxLayout(header_card)
        h_layout.setContentsMargins(16, 12, 16, 12)

        title = QLabel("Music Theory Hub")
        title.setStyleSheet("font-size: 20px; font-weight: 700; color: #38BDF8;")
        h_layout.addWidget(title)

        h_layout.addStretch()

        # Integrated Metronome Control in Header
        metro_box = QHBoxLayout()
        lbl_metro = QLabel("Metronome:")
        self.spin_bpm = QSpinBox()
        self.spin_bpm.setRange(30, 300)
        self.spin_bpm.setValue(120)
        self.spin_bpm.valueChanged.connect(lambda v: self.audio_engine.metronome.set_bpm(float(v)))

        self.btn_metro_toggle = QPushButton("Start Metronome")
        self.btn_metro_toggle.setProperty("class", "SecondaryButton")
        self.btn_metro_toggle.clicked.connect(self._toggle_metronome)

        metro_box.addWidget(lbl_metro)
        metro_box.addWidget(self.spin_bpm)
        metro_box.addWidget(self.btn_metro_toggle)
        h_layout.addLayout(metro_box)

        main_layout.addWidget(header_card)

        # Theory Tabs: 1. Ragas & Thaats, 2. Western Scales & Chords, 3. Talas, 4. Tuning Systems
        self.tabs = QTabWidget()

        self._build_ragas_tab()
        self._build_western_tab()
        self._build_talas_tab()
        self._build_tuning_tab()

        main_layout.addWidget(self.tabs, 1)

        # Shared Virtual Keyboard for note / chord / scale auditioning
        self.virtual_keyboard = VirtualKeyboardWidget(start_midi=48, num_keys=37)
        main_layout.addWidget(self.virtual_keyboard)

        self.virtual_keyboard.note_pressed.connect(lambda m: self.audio_engine.note_on(m, 100))
        self.virtual_keyboard.note_released.connect(lambda m: self.audio_engine.note_off(m))

    def _build_ragas_tab(self) -> None:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        ctrl_row = QHBoxLayout()
        lbl_select = QLabel("Select Raga:")
        self.raga_combo = QComboBox()
        for raga in INITIAL_RAGAS:
            self.raga_combo.addItem(f"{raga.name} ({raga.thaat} Thaat)", raga)
        self.raga_combo.currentIndexChanged.connect(self._on_raga_selected)
        ctrl_row.addWidget(lbl_select)
        ctrl_row.addWidget(self.raga_combo)

        ctrl_row.addSpacing(20)
        lbl_thaat = QLabel("Or Select Parent Thaat:")
        self.thaat_combo = QComboBox()
        for thaat in THAATS.values():
            self.thaat_combo.addItem(f"{thaat.name}", thaat)
        self.thaat_combo.currentIndexChanged.connect(self._on_thaat_selected)
        ctrl_row.addWidget(lbl_thaat)
        ctrl_row.addWidget(self.thaat_combo)

        ctrl_row.addStretch()
        layout.addLayout(ctrl_row)

        # Raga Info Display Box
        info_frame = QFrame()
        info_frame.setProperty("class", "Card")
        info_layout = QVBoxLayout(info_frame)
        info_layout.setSpacing(8)

        self.lbl_raga_name = QLabel("Raga: Yaman (Kalyan)")
        self.lbl_raga_name.setStyleSheet("font-size: 16px; font-weight: 700; color: #38BDF8;")
        self.lbl_raga_aroha = QLabel("Aroha: 'N R G M' D N S'")
        self.lbl_raga_avaroha = QLabel("Avaroha: S' N D P M' G R S")
        self.lbl_raga_vadi = QLabel("Vadi: Ga | Samvadi: Ni | Time: First quarter of night")
        self.lbl_raga_pakad = QLabel("Pakad: 'N R G, M' D N S', R' N D P, M' G R S")
        self.lbl_raga_desc = QLabel(
            "Description: One of the most fundamental evening ragas featuring Tivra Madhyam and prominent Gandhar."
        )
        self.lbl_raga_desc.setWordWrap(True)

        for w in [
            self.lbl_raga_name,
            self.lbl_raga_aroha,
            self.lbl_raga_avaroha,
            self.lbl_raga_vadi,
            self.lbl_raga_pakad,
            self.lbl_raga_desc,
        ]:
            info_layout.addWidget(w)

        layout.addWidget(info_frame)

        # Scale Degree Highlight Button
        btn_highlight = QPushButton("Highlight Raga Swaras On Keyboard")
        btn_highlight.setProperty("class", "SecondaryButton")
        btn_highlight.clicked.connect(self._highlight_current_raga)
        layout.addWidget(btn_highlight)

        layout.addStretch()
        self.tabs.addTab(tab, "Indian Ragas & Thaats")

    def _build_western_tab(self) -> None:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        row1 = QHBoxLayout()
        lbl_root = QLabel("Root Note:")
        self.root_combo = QComboBox()
        for n in NOTE_NAMES:
            self.root_combo.addItem(n)
        row1.addWidget(lbl_root)
        row1.addWidget(self.root_combo)

        lbl_scale = QLabel("Scale:")
        self.scale_combo = QComboBox()
        for s_def in WESTERN_SCALES.values():
            self.scale_combo.addItem(s_def.name, s_def)
        row1.addWidget(lbl_scale)
        row1.addWidget(self.scale_combo)

        btn_show_scale = QPushButton("Play & Highlight Scale")
        btn_show_scale.setProperty("class", "SecondaryButton")
        btn_show_scale.clicked.connect(self._play_scale)
        row1.addWidget(btn_show_scale)
        row1.addStretch()
        layout.addLayout(row1)

        # Chord Section
        chord_group = QGroupBox("Chords & Inversions")
        cg_layout = QVBoxLayout(chord_group)
        crow = QHBoxLayout()

        lbl_ch_type = QLabel("Chord Type:")
        self.chord_type_combo = QComboBox()
        for c_id, c_form in CHORD_FORMULAS.items():
            self.chord_type_combo.addItem(f"{c_form.name} ({c_form.symbol or 'maj'})", c_id)
        crow.addWidget(lbl_ch_type)
        crow.addWidget(self.chord_type_combo)

        lbl_inv = QLabel("Inversion:")
        self.inversion_combo = QComboBox()
        self.inversion_combo.addItem("Root Position (0)", 0)
        self.inversion_combo.addItem("1st Inversion", 1)
        self.inversion_combo.addItem("2nd Inversion", 2)
        self.inversion_combo.addItem("3rd Inversion", 3)
        crow.addWidget(lbl_inv)
        crow.addWidget(self.inversion_combo)

        btn_play_chord = QPushButton("Arpeggiate / Play Chord")
        btn_play_chord.setProperty("class", "PrimaryButton")
        btn_play_chord.clicked.connect(self._play_chord)
        crow.addWidget(btn_play_chord)
        crow.addStretch()
        cg_layout.addLayout(crow)

        self.lbl_chord_result = QLabel("Chord Notes: C - E - G")
        self.lbl_chord_result.setStyleSheet("color: #38BDF8; font-weight: 600; font-size: 14px;")
        cg_layout.addWidget(self.lbl_chord_result)
        layout.addWidget(chord_group)

        layout.addStretch()
        self.tabs.addTab(tab, "Western Scales & Chords")

    def _build_talas_tab(self) -> None:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        t_row = QHBoxLayout()
        t_lbl = QLabel("Select Tala:")
        self.theory_tala_combo = QComboBox()
        for tala in TALAS.values():
            self.theory_tala_combo.addItem(f"{tala.name} ({tala.matras} Matras)", tala)
        self.theory_tala_combo.currentIndexChanged.connect(self._on_theory_tala_changed)
        t_row.addWidget(t_lbl)
        t_row.addWidget(self.theory_tala_combo)
        t_row.addStretch()
        layout.addLayout(t_row)

        # Tala Details Panel
        t_panel = QFrame()
        t_panel.setProperty("class", "Card")
        tp_layout = QVBoxLayout(t_panel)
        tp_layout.setSpacing(8)

        self.lbl_tt_name = QLabel("Tala: Teental (16 Matras)")
        self.lbl_tt_name.setStyleSheet("font-size: 16px; font-weight: 700; color: #10B981;")
        self.lbl_tt_div = QLabel(
            "Vibhag Structure: 4 + 4 + 4 + 4 | Claps (Tali): 1, 5, 13 | Wave (Khali): 9"
        )
        self.lbl_tt_theka = QLabel("Theka Bols:\n" + " - ".join(TALAS["teental"].theka_bols))
        self.lbl_tt_theka.setWordWrap(True)
        self.lbl_tt_theka.setStyleSheet("color: #38BDF8; font-weight: 600;")
        self.lbl_tt_desc = QLabel(f"Description: {TALAS['teental'].description}")
        self.lbl_tt_desc.setWordWrap(True)

        for w in [self.lbl_tt_name, self.lbl_tt_div, self.lbl_tt_theka, self.lbl_tt_desc]:
            tp_layout.addWidget(w)

        layout.addWidget(t_panel)
        layout.addStretch()
        self.tabs.addTab(tab, "Indian Talas & Laya")

    def _build_tuning_tab(self) -> None:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        ctrl_row = QHBoxLayout()
        lbl_sys = QLabel("Tuning System:")
        self.tuning_sys_combo = QComboBox()
        for sys_id, sys_obj in TUNING_SYSTEMS.items():
            self.tuning_sys_combo.addItem(sys_obj.name, sys_id)
        self.tuning_sys_combo.currentIndexChanged.connect(self._on_tuning_system_changed)
        ctrl_row.addWidget(lbl_sys)
        ctrl_row.addWidget(self.tuning_sys_combo)

        ctrl_row.addSpacing(20)
        lbl_ref = QLabel("A4 Reference (Hz):")
        self.ref_spin = QSpinBox()
        self.ref_spin.setRange(415, 466)
        self.ref_spin.setValue(440)
        self.ref_spin.valueChanged.connect(
            lambda v: self.audio_engine.tuning.set_reference_pitch(float(v))
        )
        ctrl_row.addWidget(lbl_ref)
        ctrl_row.addWidget(self.ref_spin)

        ctrl_row.addStretch()
        layout.addLayout(ctrl_row)

        self.lbl_tuning_desc = QLabel(
            "Standard modern tuning dividing octave into 12 logarithmic equal semitones."
        )
        self.lbl_tuning_desc.setWordWrap(True)
        self.lbl_tuning_desc.setStyleSheet("color: #94A3B8; font-size: 13px;")
        layout.addWidget(self.lbl_tuning_desc)

        layout.addStretch()
        self.tabs.addTab(tab, "Tuning & Temperament")

    def _toggle_metronome(self) -> None:
        if self.audio_engine.metronome.is_active:
            self.audio_engine.metronome.stop()
            self.btn_metro_toggle.setText("Start Metronome")
            self.btn_metro_toggle.setStyleSheet("")
        else:
            self.audio_engine.metronome.start()
            self.btn_metro_toggle.setText("Stop Metronome")
            self.btn_metro_toggle.setStyleSheet("background-color: #EF4444; color: #FFFFFF;")

    def _on_raga_selected(self) -> None:
        raga: Raga = self.raga_combo.currentData()
        if not raga:
            return
        self.lbl_raga_name.setText(f"Raga: {raga.name} ({raga.thaat} Thaat)")
        self.lbl_raga_aroha.setText(f"Aroha: {raga.aroha}")
        self.lbl_raga_avaroha.setText(f"Avaroha: {raga.avaroha}")
        self.lbl_raga_vadi.setText(
            f"Vadi: {raga.vadi} | Samvadi: {raga.samvadi} | Time: {raga.time_of_day}"
        )
        self.lbl_raga_pakad.setText(f"Pakad: {raga.pakad}")
        self.lbl_raga_desc.setText(f"Description: {raga.description}")

    def _on_thaat_selected(self) -> None:
        thaat: ScaleDefinition = self.thaat_combo.currentData()
        if not thaat:
            return
        self.lbl_raga_name.setText(f"Parent Thaat: {thaat.name}")
        self.lbl_raga_desc.setText(f"Description: {thaat.description}")

    def _highlight_current_raga(self) -> None:
        raga: Raga = self.raga_combo.currentData()
        if not raga:
            return
        base = 60
        for midi in range(48, 85):
            semitone = (midi - base) % 12
            self.virtual_keyboard.set_note_active(midi, semitone in raga.notes_semitones)

    def _play_scale(self) -> None:
        root_name = self.root_combo.currentText()
        scale: ScaleDefinition = self.scale_combo.currentData()
        if not scale:
            return
        root_idx = NOTE_NAMES.index(root_name)
        root_midi = 60 + root_idx
        midi_notes = scale.get_midi_notes(root_midi=root_midi, octaves=1)

        for midi in range(48, 85):
            self.virtual_keyboard.set_note_active(midi, midi in midi_notes)

    def _play_chord(self) -> None:
        root = self.root_combo.currentText()
        chord_id = self.chord_type_combo.currentData()
        inv = self.inversion_combo.currentData()
        chord = create_chord(root=root, chord_type=chord_id, inversion=inv)
        if not chord:
            return
        self.lbl_chord_result.setText(f"{chord.name} Notes: {' - '.join(chord.notes)}")

        root_idx = NOTE_NAMES.index(root)
        midi_notes = chord.get_midi_notes(root_midi=60 + root_idx)

        self.virtual_keyboard.clear_active_notes()
        for midi in midi_notes:
            self.virtual_keyboard.set_note_active(midi, True)
            self.audio_engine.note_on(midi, 95)

    def _on_theory_tala_changed(self) -> None:
        tala: Tala = self.theory_tala_combo.currentData()
        if not tala:
            return
        self.lbl_tt_name.setText(f"Tala: {tala.name} ({tala.matras} Matras)")
        divs = " + ".join(str(v) for v in tala.vibhag_structure)
        claps = ", ".join(str(c) for c in tala.claps)
        khali = ", ".join(str(k) for k in tala.khali)
        self.lbl_tt_div.setText(
            f"Vibhag Structure: {divs} | Claps (Tali): {claps} | Wave (Khali): {khali}"
        )
        self.lbl_tt_theka.setText("Theka Bols:\n" + " - ".join(tala.theka_bols))
        self.lbl_tt_desc.setText(f"Description: {tala.description}")

    def _on_tuning_system_changed(self) -> None:
        sys_id = self.tuning_sys_combo.currentData()
        if sys_id:
            self.audio_engine.tuning.set_system(sys_id)
            sys_obj = TUNING_SYSTEMS.get(sys_id)
            if sys_obj:
                self.lbl_tuning_desc.setText(sys_obj.description)
