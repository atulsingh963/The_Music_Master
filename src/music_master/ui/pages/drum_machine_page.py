"""Drum Machine UI page featuring 16-step sequencer, drum pads, kit selection, and transport controls."""

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from music_master.audio.engine import AudioEngine
from music_master.instruments.percussion.drum_synthesizer import DRUM_PADS


class DrumMachinePage(QWidget):
    """Drum machine control page with visual step sequencer and velocity-sensitive pads."""

    def __init__(self, audio_engine: AudioEngine, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.audio_engine = audio_engine
        self.drum_engine = audio_engine.drum_engine
        self.sequencer = audio_engine.drum_sequencer

        self.step_buttons: dict[tuple[str, int], QPushButton] = {}
        self.current_cursor_step: int = -1

        self._init_ui()

        # Connect sequencer step callback to UI timer update
        self.sequencer.step_callback = self._on_step_triggered

        # UI poll timer to update sequencer visual step head safely in Qt main thread
        self.poll_timer = QTimer(self)
        self.poll_timer.timeout.connect(self._update_step_cursor)
        self.poll_timer.start(30)

    def _init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(28, 24, 28, 24)
        main_layout.setSpacing(16)

        # 1. Header
        header_layout = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("DRUM MACHINE & SEQUENCER")
        title.setStyleSheet("font-size: 20px; font-weight: 700; color: #F8FAFC;")
        subtitle = QLabel("16-Step Rhythm Sequencer & Multi-Kit Electronic/Acoustic Drums")
        subtitle.setStyleSheet("font-size: 13px; color: #94A3B8;")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header_layout.addLayout(title_box)
        header_layout.addStretch()

        # Kit Type Switcher
        kit_label = QLabel("Drum Kit:")
        kit_label.setStyleSheet("color: #94A3B8; font-weight: 600;")
        self.kit_combo = QComboBox()
        self.kit_combo.addItems(["Acoustic Drum Kit", "Electronic 808/909"])
        self.kit_combo.currentIndexChanged.connect(self._on_kit_changed)
        header_layout.addWidget(kit_label)
        header_layout.addWidget(self.kit_combo)

        # Pattern Preset Switcher
        preset_label = QLabel("Pattern Preset:")
        preset_label.setStyleSheet("color: #94A3B8; font-weight: 600; margin-left: 12px;")
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(["Electro / Rock", "Rock Beat", "Hip-Hop", "House 4/4"])
        self.preset_combo.currentIndexChanged.connect(self._on_preset_changed)
        header_layout.addWidget(preset_label)
        header_layout.addWidget(self.preset_combo)

        main_layout.addLayout(header_layout)

        # 2. Transport & Sequencer Controls
        transport_frame = QFrame()
        transport_frame.setStyleSheet(
            "background-color: #1E293B; border-radius: 8px; padding: 10px;"
        )
        transport_layout = QHBoxLayout(transport_frame)
        transport_layout.setContentsMargins(12, 8, 12, 8)
        transport_layout.setSpacing(14)

        # Play / Pause / Stop
        self.play_btn = QPushButton("▶ Play")
        self.play_btn.setCheckable(True)
        self.play_btn.setStyleSheet(
            "background-color: #059669; color: white; font-weight: 700; padding: 8px 16px; border-radius: 6px;"
        )
        self.play_btn.clicked.connect(self._toggle_play)
        transport_layout.addWidget(self.play_btn)

        self.stop_btn = QPushButton("⏹ Stop")
        self.stop_btn.setStyleSheet(
            "background-color: #334155; color: white; font-weight: 600; padding: 8px 16px; border-radius: 6px;"
        )
        self.stop_btn.clicked.connect(self._stop_sequencer)
        transport_layout.addWidget(self.stop_btn)

        self.clear_btn = QPushButton("Clear Pattern")
        self.clear_btn.setStyleSheet(
            "background-color: #334155; color: #CBD5E1; padding: 8px 14px; border-radius: 6px;"
        )
        self.clear_btn.clicked.connect(self._clear_pattern)
        transport_layout.addWidget(self.clear_btn)

        # BPM
        bpm_label = QLabel("BPM:")
        bpm_label.setStyleSheet("color: #CBD5E1; font-weight: 600;")
        self.bpm_spin = QSpinBox()
        self.bpm_spin.setRange(40, 240)
        self.bpm_spin.setValue(int(self.sequencer.bpm))
        self.bpm_spin.valueChanged.connect(self._on_bpm_changed)
        transport_layout.addWidget(bpm_label)
        transport_layout.addWidget(self.bpm_spin)

        # Pitch knob / slider
        pitch_label = QLabel("Tuning:")
        pitch_label.setStyleSheet("color: #CBD5E1; font-weight: 600; margin-left: 12px;")
        self.pitch_slider = QSlider(Qt.Orientation.Horizontal)
        self.pitch_slider.setRange(50, 150)
        self.pitch_slider.setValue(100)
        self.pitch_slider.setFixedWidth(120)
        self.pitch_slider.valueChanged.connect(self._on_pitch_changed)
        transport_layout.addWidget(pitch_label)
        transport_layout.addWidget(self.pitch_slider)

        transport_layout.addStretch()
        main_layout.addWidget(transport_frame)

        # 3. Interactive Drum Pads
        pads_label = QLabel("QUICK TRIGGER DRUM PADS")
        pads_label.setStyleSheet(
            "font-size: 13px; font-weight: 700; color: #38BDF8; margin-top: 6px;"
        )
        main_layout.addWidget(pads_label)

        pads_frame = QFrame()
        pads_frame.setStyleSheet("background-color: #0F172A; border-radius: 8px; padding: 8px;")
        pads_layout = QHBoxLayout(pads_frame)
        pads_layout.setSpacing(10)

        for pad in DRUM_PADS:
            btn = QPushButton(f"{pad.name}\n(MIDI {pad.midi_note})")
            btn.setFixedHeight(54)
            btn.setStyleSheet(
                "background-color: #1E293B; color: #F1F5F9; font-size: 11px; font-weight: 600; border: 1px solid #334155; border-radius: 6px;"
            )
            btn.pressed.connect(lambda pid=pad.id: self._on_pad_pressed(pid))
            pads_layout.addWidget(btn)

        main_layout.addWidget(pads_frame)

        # 4. 16-Step Sequencer Grid
        grid_label = QLabel("16-STEP SEQUENCER MATRIX")
        grid_label.setStyleSheet(
            "font-size: 13px; font-weight: 700; color: #38BDF8; margin-top: 8px;"
        )
        main_layout.addWidget(grid_label)

        grid_frame = QFrame()
        grid_frame.setStyleSheet("background-color: #0F172A; border-radius: 8px; padding: 12px;")
        grid_layout = QGridLayout(grid_frame)
        grid_layout.setSpacing(4)

        # Step header numbers (1 to 16)
        for step in range(16):
            step_lbl = QLabel(f"{step + 1}")
            step_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            step_lbl.setStyleSheet(
                f"color: {'#38BDF8' if step % 4 == 0 else '#64748B'}; font-size: 11px; font-weight: {'700' if step % 4 == 0 else '400'};"
            )
            grid_layout.addWidget(step_lbl, 0, step + 1)

        # Grid rows for each pad
        for row_idx, pad in enumerate(DRUM_PADS):
            row_label = QLabel(pad.name)
            row_label.setStyleSheet(
                "color: #E2E8F0; font-size: 12px; font-weight: 600; min-width: 90px;"
            )
            grid_layout.addWidget(row_label, row_idx + 1, 0)

            for col_idx in range(16):
                sbtn = QPushButton()
                sbtn.setFixedSize(28, 26)
                sbtn.setCheckable(True)
                # Group 4 beats visually
                is_bar_beat = (col_idx // 4) % 2 == 0
                base_color = "#1E293B" if is_bar_beat else "#162032"
                sbtn.setStyleSheet(
                    f"background-color: {base_color}; border: 1px solid #334155; border-radius: 3px;"
                )

                # Set initial state from default pattern
                is_active = self.sequencer.grid[pad.id][col_idx].active
                sbtn.setChecked(is_active)
                if is_active:
                    sbtn.setStyleSheet(
                        "background-color: #38BDF8; border: 1px solid #0284C7; border-radius: 3px;"
                    )

                sbtn.clicked.connect(
                    lambda checked, pid=pad.id, c=col_idx, btn=sbtn, ibb=is_bar_beat: (
                        self._on_grid_step_toggled(pid, c, checked, btn, ibb)
                    )
                )
                self.step_buttons[(pad.id, col_idx)] = sbtn
                grid_layout.addWidget(sbtn, row_idx + 1, col_idx + 1)

        main_layout.addWidget(grid_frame)
        main_layout.addStretch()

    def _on_pad_pressed(self, pad_id: str) -> None:
        self.drum_engine.trigger_pad(pad_id, velocity=0.9)

    def _on_grid_step_toggled(
        self, pad_id: str, col_idx: int, checked: bool, btn: QPushButton, is_bar_beat: bool
    ) -> None:
        self.sequencer.set_step(pad_id, col_idx, checked, velocity=0.85)
        if checked:
            btn.setStyleSheet(
                "background-color: #38BDF8; border: 1px solid #0284C7; border-radius: 3px;"
            )
        else:
            base_color = "#1E293B" if is_bar_beat else "#162032"
            btn.setStyleSheet(
                f"background-color: {base_color}; border: 1px solid #334155; border-radius: 3px;"
            )

    def _toggle_play(self) -> None:
        if self.play_btn.isChecked():
            self.sequencer.play()
            self.play_btn.setText("⏸ Pause")
            self.play_btn.setStyleSheet(
                "background-color: #EAB308; color: black; font-weight: 700; padding: 8px 16px; border-radius: 6px;"
            )
        else:
            self.sequencer.pause()
            self.play_btn.setText("▶ Play")
            self.play_btn.setStyleSheet(
                "background-color: #059669; color: white; font-weight: 700; padding: 8px 16px; border-radius: 6px;"
            )

    def _stop_sequencer(self) -> None:
        self.sequencer.stop()
        self.play_btn.setChecked(False)
        self.play_btn.setText("▶ Play")
        self.play_btn.setStyleSheet(
            "background-color: #059669; color: white; font-weight: 700; padding: 8px 16px; border-radius: 6px;"
        )
        self._update_all_step_styles(-1)

    def _clear_pattern(self) -> None:
        self.sequencer.clear_pattern()
        self._refresh_grid_ui()

    def _on_bpm_changed(self, value: int) -> None:
        self.sequencer.set_bpm(float(value))

    def _on_pitch_changed(self, value: int) -> None:
        factor = value / 100.0
        self.drum_engine.set_pitch_factor(factor)

    def _on_kit_changed(self, idx: int) -> None:
        kit_type = "acoustic" if idx == 0 else "electronic"
        self.drum_engine.set_kit_type(kit_type)

    def _on_preset_changed(self, idx: int) -> None:
        presets = ["default", "rock", "hiphop", "house"]
        self.sequencer.load_preset(presets[idx])
        self._refresh_grid_ui()

    def _refresh_grid_ui(self) -> None:
        for pad in DRUM_PADS:
            for step in range(16):
                btn = self.step_buttons.get((pad.id, step))
                if btn:
                    is_active = self.sequencer.grid[pad.id][step].active
                    btn.setChecked(is_active)
                    is_bar_beat = (step // 4) % 2 == 0
                    if is_active:
                        btn.setStyleSheet(
                            "background-color: #38BDF8; border: 1px solid #0284C7; border-radius: 3px;"
                        )
                    else:
                        base_color = "#1E293B" if is_bar_beat else "#162032"
                        btn.setStyleSheet(
                            f"background-color: {base_color}; border: 1px solid #334155; border-radius: 3px;"
                        )

    def _on_step_triggered(self, step_idx: int) -> None:
        self.current_cursor_step = step_idx

    def _update_step_cursor(self) -> None:
        if not self.sequencer.is_playing:
            return
        step = self.current_cursor_step
        self._update_all_step_styles(step)

    def _update_all_step_styles(self, active_col: int) -> None:
        for pad in DRUM_PADS:
            for step in range(16):
                btn = self.step_buttons.get((pad.id, step))
                if not btn:
                    continue
                is_active = self.sequencer.grid[pad.id][step].active
                is_current = step == active_col
                is_bar_beat = (step // 4) % 2 == 0

                if is_current:
                    if is_active:
                        btn.setStyleSheet(
                            "background-color: #F43F5E; border: 2px solid #FDA4AF; border-radius: 3px;"
                        )
                    else:
                        btn.setStyleSheet(
                            "background-color: #475569; border: 2px solid #94A3B8; border-radius: 3px;"
                        )
                else:
                    if is_active:
                        btn.setStyleSheet(
                            "background-color: #38BDF8; border: 1px solid #0284C7; border-radius: 3px;"
                        )
                    else:
                        base_color = "#1E293B" if is_bar_beat else "#162032"
                        btn.setStyleSheet(
                            f"background-color: {base_color}; border: 1px solid #334155; border-radius: 3px;"
                        )
