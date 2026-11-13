"""MIDI Studio UI page for device discovery, hardware input routing, and MIDI file import/export."""

import os

from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from music_master.audio.engine import AudioEngine
from music_master.midi.file import MidiFileManager, NoteEvent
from music_master.midi.manager import MidiManager


class MidiStudioPage(QWidget):
    """MIDI Studio control page."""

    def __init__(
        self,
        audio_engine: AudioEngine,
        midi_manager: MidiManager,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.audio_engine = audio_engine
        self.midi_manager = midi_manager
        self.loaded_events: list[NoteEvent] = []

        self._init_ui()
        self._setup_midi_routing()

    def _init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(28, 24, 28, 24)
        main_layout.setSpacing(16)

        # 1. Header
        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("MIDI STUDIO & DEVICE MANAGER")
        title.setStyleSheet("font-size: 20px; font-weight: 700; color: #F8FAFC;")
        subtitle = QLabel(
            "Hardware Controller Routing, Standard MIDI File Reader/Writer & Event Log"
        )
        subtitle.setStyleSheet("font-size: 13px; color: #94A3B8;")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header.addLayout(title_box)
        header.addStretch()
        main_layout.addLayout(header)

        # 2. Hardware Devices Section
        dev_frame = QFrame()
        dev_frame.setStyleSheet("background-color: #1E293B; border-radius: 8px; padding: 14px;")
        dev_layout = QVBoxLayout(dev_frame)
        dev_layout.setSpacing(12)

        dev_title = QLabel("HARDWARE MIDI PORTS")
        dev_title.setStyleSheet("font-size: 13px; font-weight: 700; color: #38BDF8;")
        dev_layout.addWidget(dev_title)

        ports_layout = QHBoxLayout()
        ports_layout.setSpacing(16)

        # MIDI Input selection
        in_box = QVBoxLayout()
        in_lbl = QLabel("MIDI Input Device:")
        in_lbl.setStyleSheet("color: #CBD5E1; font-weight: 600;")
        self.in_combo = QComboBox()
        self.in_combo.setMinimumWidth(220)
        in_box.addWidget(in_lbl)
        in_box.addWidget(self.in_combo)
        ports_layout.addLayout(in_box)

        self.btn_connect_in = QPushButton("Connect Input")
        self.btn_connect_in.setStyleSheet(
            "background-color: #0284C7; color: white; padding: 8px 16px; border-radius: 6px; font-weight: 600; margin-top: 18px;"
        )
        self.btn_connect_in.clicked.connect(self._toggle_input_connect)
        ports_layout.addWidget(self.btn_connect_in)

        # MIDI Output selection
        out_box = QVBoxLayout()
        out_lbl = QLabel("MIDI Output Device:")
        out_lbl.setStyleSheet("color: #CBD5E1; font-weight: 600;")
        self.out_combo = QComboBox()
        self.out_combo.setMinimumWidth(220)
        out_box.addWidget(out_lbl)
        out_box.addWidget(self.out_combo)
        ports_layout.addLayout(out_box)

        self.btn_connect_out = QPushButton("Connect Output")
        self.btn_connect_out.setStyleSheet(
            "background-color: #334155; color: white; padding: 8px 16px; border-radius: 6px; font-weight: 600; margin-top: 18px;"
        )
        self.btn_connect_out.clicked.connect(self._toggle_output_connect)
        ports_layout.addWidget(self.btn_connect_out)

        self.btn_refresh = QPushButton("🔄 Rescan Devices")
        self.btn_refresh.setStyleSheet(
            "background-color: #334155; color: #CBD5E1; padding: 8px 14px; border-radius: 6px; margin-top: 18px;"
        )
        self.btn_refresh.clicked.connect(self._refresh_device_lists)
        ports_layout.addWidget(self.btn_refresh)

        dev_layout.addLayout(ports_layout)
        main_layout.addWidget(dev_frame)

        # 3. Standard MIDI File Manager Section
        file_frame = QFrame()
        file_frame.setStyleSheet("background-color: #1E293B; border-radius: 8px; padding: 14px;")
        file_layout = QVBoxLayout(file_frame)
        file_layout.setSpacing(12)

        file_title = QLabel("STANDARD MIDI FILES (.MID)")
        file_title.setStyleSheet("font-size: 13px; font-weight: 700; color: #38BDF8;")
        file_layout.addWidget(file_title)

        file_actions = QHBoxLayout()
        file_actions.setSpacing(12)

        self.btn_import = QPushButton("📂 Import MIDI File")
        self.btn_import.setStyleSheet(
            "background-color: #334155; color: white; padding: 8px 16px; border-radius: 6px; font-weight: 600;"
        )
        self.btn_import.clicked.connect(self._import_midi_file)
        file_actions.addWidget(self.btn_import)

        self.btn_export = QPushButton("💾 Export Example MIDI")
        self.btn_export.setStyleSheet(
            "background-color: #334155; color: white; padding: 8px 16px; border-radius: 6px; font-weight: 600;"
        )
        self.btn_export.clicked.connect(self._export_midi_file)
        file_actions.addWidget(self.btn_export)

        self.lbl_file_status = QLabel("No MIDI file loaded")
        self.lbl_file_status.setStyleSheet("color: #94A3B8; font-size: 12px; margin-left: 10px;")
        file_actions.addWidget(self.lbl_file_status)
        file_actions.addStretch()

        file_layout.addLayout(file_actions)
        main_layout.addWidget(file_frame)

        # 4. MIDI Activity Event Log Monitor
        log_frame = QFrame()
        log_frame.setStyleSheet("background-color: #0F172A; border-radius: 8px; padding: 12px;")
        log_layout = QVBoxLayout(log_frame)

        log_header = QHBoxLayout()
        log_title = QLabel("REAL-TIME MIDI EVENT MONITOR")
        log_title.setStyleSheet("font-size: 12px; font-weight: 700; color: #38BDF8;")
        log_header.addWidget(log_title)
        log_header.addStretch()

        btn_clear_log = QPushButton("Clear Log")
        btn_clear_log.setStyleSheet(
            "background-color: #1E293B; color: #94A3B8; font-size: 11px; padding: 4px 10px; border-radius: 4px;"
        )
        self.log_list = QListWidget()
        btn_clear_log.clicked.connect(lambda: self.log_list.clear())
        log_header.addWidget(btn_clear_log)
        log_layout.addLayout(log_header)

        self.log_list.setStyleSheet(
            "background-color: #020617; color: #10B981; font-family: monospace; font-size: 11px; border: 1px solid #1E293B; border-radius: 6px;"
        )
        self.log_list.setFixedHeight(180)
        log_layout.addWidget(self.log_list)

        main_layout.addWidget(log_frame)
        main_layout.addStretch()

        self._refresh_device_lists()

    def _setup_midi_routing(self) -> None:
        """Connect incoming MIDI messages to AudioEngine and Event Log."""

        def on_note_on(note: int, vel: int, ch: int) -> None:
            self.audio_engine.note_on(note, velocity=vel)
            self._log_event(f"NOTE ON  | Note: {note:3d} | Vel: {vel:3d} | Ch: {ch:2d}")

        def on_note_off(note: int, ch: int) -> None:
            self.audio_engine.note_off(note)
            self._log_event(f"NOTE OFF | Note: {note:3d} | Ch: {ch:2d}")

        def on_cc(cc: int, val: int, ch: int) -> None:
            if cc == 64:  # Sustain pedal
                self.audio_engine.set_sustain(val >= 64)
                self._log_event(f"SUSTAIN  | Val:  {val:3d} | Ch: {ch:2d}")
            else:
                self._log_event(f"CC {cc:3d}   | Val:  {val:3d} | Ch: {ch:2d}")

        self.midi_manager.register_note_on_callback(on_note_on)
        self.midi_manager.register_note_off_callback(on_note_off)
        self.midi_manager.register_control_change_callback(on_cc)

    def _log_event(self, text: str) -> None:
        self.log_list.addItem(text)
        if self.log_list.count() > 200:
            self.log_list.takeItem(0)
        self.log_list.scrollToBottom()

    def _refresh_device_lists(self) -> None:
        self.midi_manager.refresh_devices()
        self.in_combo.clear()
        if not self.midi_manager.input_devices:
            self.in_combo.addItem("No MIDI Input Devices Found")
            self.btn_connect_in.setEnabled(False)
        else:
            for dev in self.midi_manager.input_devices:
                self.in_combo.addItem(f"{dev.name} (Port {dev.id})", dev.id)
            self.btn_connect_in.setEnabled(True)

        self.out_combo.clear()
        if not self.midi_manager.output_devices:
            self.out_combo.addItem("No MIDI Output Devices Found")
            self.btn_connect_out.setEnabled(False)
        else:
            for dev in self.midi_manager.output_devices:
                self.out_combo.addItem(f"{dev.name} (Port {dev.id})", dev.id)
            self.btn_connect_out.setEnabled(True)

    def _toggle_input_connect(self) -> None:
        if self.midi_manager.current_input_device_id is not None:
            self.midi_manager.close_input_device()
            self.btn_connect_in.setText("Connect Input")
            self.btn_connect_in.setStyleSheet(
                "background-color: #0284C7; color: white; padding: 8px 16px; border-radius: 6px; font-weight: 600; margin-top: 18px;"
            )
            self._log_event("MIDI Input Device Disconnected.")
        else:
            dev_id = self.in_combo.currentData()
            if dev_id is not None and self.midi_manager.open_input_device(int(dev_id)):
                self.btn_connect_in.setText("Disconnect Input")
                self.btn_connect_in.setStyleSheet(
                    "background-color: #DC2626; color: white; padding: 8px 16px; border-radius: 6px; font-weight: 600; margin-top: 18px;"
                )
                self._log_event(f"MIDI Input Device Connected: {self.in_combo.currentText()}")
            else:
                self._log_event("Failed to open MIDI Input Device.")

    def _toggle_output_connect(self) -> None:
        if self.midi_manager.current_output_device_id is not None:
            self.midi_manager.close_output_device()
            self.btn_connect_out.setText("Connect Output")
            self.btn_connect_out.setStyleSheet(
                "background-color: #334155; color: white; padding: 8px 16px; border-radius: 6px; font-weight: 600; margin-top: 18px;"
            )
            self._log_event("MIDI Output Device Disconnected.")
        else:
            dev_id = self.out_combo.currentData()
            if dev_id is not None and self.midi_manager.open_output_device(int(dev_id)):
                self.btn_connect_out.setText("Disconnect Output")
                self.btn_connect_out.setStyleSheet(
                    "background-color: #DC2626; color: white; padding: 8px 16px; border-radius: 6px; font-weight: 600; margin-top: 18px;"
                )
                self._log_event(f"MIDI Output Device Connected: {self.out_combo.currentText()}")
            else:
                self._log_event("Failed to open MIDI Output Device.")

    def _import_midi_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Open MIDI File", "", "MIDI Files (*.mid *.midi)"
        )
        if path:
            try:
                events = MidiFileManager.read_midi_file(path)
                self.loaded_events = events
                filename = os.path.basename(path)
                self.lbl_file_status.setText(f"Loaded '{filename}' ({len(events)} note events)")
                self._log_event(f"Successfully loaded '{filename}' ({len(events)} note events)")
            except Exception as e:
                QMessageBox.warning(self, "Error Loading MIDI", str(e))

    def _export_midi_file(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Save MIDI File", "project_track.mid", "MIDI Files (*.mid)"
        )
        if path:
            try:
                # If no events imported, create a musical arpeggio demo sequence to export
                events_to_save = self.loaded_events
                if not events_to_save:
                    scale_notes = [60, 64, 67, 72, 71, 67, 64, 60]
                    events_to_save = [
                        NoteEvent(note=n, velocity=90, start_time=i * 0.25, duration=0.22)
                        for i, n in enumerate(scale_notes)
                    ]
                MidiFileManager.write_midi_file(path, events_to_save)
                filename = os.path.basename(path)
                self.lbl_file_status.setText(
                    f"Exported '{filename}' ({len(events_to_save)} note events)"
                )
                self._log_event(f"Saved MIDI file to '{path}'")
            except Exception as e:
                QMessageBox.warning(self, "Error Saving MIDI", str(e))
