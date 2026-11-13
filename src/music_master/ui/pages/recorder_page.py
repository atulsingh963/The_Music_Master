"""Recorder & Piano Roll Studio Page for Music Master."""

import os
from typing import Optional

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from music_master.audio.engine import AudioEngine
from music_master.studio.exporter import AudioExporter
from music_master.studio.piano_roll import PianoRollWidget
from music_master.studio.project import ProjectManager, StudioTrack
from music_master.studio.recorder import AudioMidiRecorder, RecordingState


class RecorderPianoRollPage(QWidget):
    """Full-featured studio page uniting recording, timeline playback, piano roll editing, and export."""

    def __init__(
        self,
        audio_engine: AudioEngine,
        recorder: AudioMidiRecorder,
        project_manager: ProjectManager,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.audio_engine = audio_engine
        self.recorder = recorder
        self.project_manager = project_manager

        self._init_ui()
        self._setup_timer()
        self.recorder.state_changed_callbacks.append(self._on_recorder_state_changed)

    def _init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        # Header Title
        title_label = QLabel("Studio Recorder & Piano Roll")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #F8FAFC;")
        main_layout.addWidget(title_label)

        # 1. Transport Bar
        transport_frame = QFrame()
        transport_frame.setStyleSheet(
            "background-color: #0F172A; border: 1px solid #334155; border-radius: 8px; padding: 6px;"
        )
        t_layout = QHBoxLayout(transport_frame)
        t_layout.setContentsMargins(12, 8, 12, 8)
        t_layout.setSpacing(12)

        self.btn_rec = QPushButton("● REC")
        self.btn_rec.setStyleSheet(
            "background-color: #DC2626; color: white; font-weight: bold; padding: 6px 14px; border-radius: 4px;"
        )
        self.btn_rec.clicked.connect(self._toggle_record)
        t_layout.addWidget(self.btn_rec)

        self.btn_play = QPushButton("▶ PLAY")
        self.btn_play.setStyleSheet(
            "background-color: #10B981; color: white; font-weight: bold; padding: 6px 14px; border-radius: 4px;"
        )
        self.btn_play.clicked.connect(self._toggle_play)
        t_layout.addWidget(self.btn_play)

        self.btn_stop = QPushButton("■ STOP")
        self.btn_stop.setStyleSheet(
            "background-color: #475569; color: white; font-weight: bold; padding: 6px 14px; border-radius: 4px;"
        )
        self.btn_stop.clicked.connect(self._stop)
        t_layout.addWidget(self.btn_stop)

        # Timeline indicator
        self.timeline_label = QLabel("00:00.00")
        self.timeline_label.setStyleSheet(
            "font-size: 16px; font-family: monospace; font-weight: bold; color: #38BDF8; padding: 0 10px;"
        )
        t_layout.addWidget(self.timeline_label)

        # Status indicator
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("font-size: 13px; color: #94A3B8; padding-right: 12px;")
        t_layout.addWidget(self.status_label)

        # BPM Control
        t_layout.addWidget(QLabel("BPM:"))
        self.bpm_spin = QSpinBox()
        self.bpm_spin.setRange(40, 240)
        self.bpm_spin.setValue(int(self.recorder.bpm))
        self.bpm_spin.valueChanged.connect(self._on_bpm_changed)
        t_layout.addWidget(self.bpm_spin)

        # Metronome Count-in check
        self.btn_count_in = QPushButton("Count-in: 1 Bar")
        self.btn_count_in.setCheckable(True)
        self.btn_count_in.setChecked(True)
        self.btn_count_in.clicked.connect(self._toggle_count_in)
        t_layout.addWidget(self.btn_count_in)

        # Overdub toggle
        self.btn_overdub = QPushButton("Overdub: ON")
        self.btn_overdub.setCheckable(True)
        self.btn_overdub.setChecked(True)
        self.btn_overdub.clicked.connect(self._toggle_overdub)
        t_layout.addWidget(self.btn_overdub)

        t_layout.addStretch()

        # Project Persistence & Audio Export Buttons
        self.btn_save_proj = QPushButton("Save Project")
        self.btn_save_proj.setStyleSheet(
            "background-color: #334155; color: white; padding: 6px 10px; border-radius: 4px;"
        )
        self.btn_save_proj.clicked.connect(self._save_project)
        t_layout.addWidget(self.btn_save_proj)

        self.btn_load_proj = QPushButton("Open Project")
        self.btn_load_proj.setStyleSheet(
            "background-color: #334155; color: white; padding: 6px 10px; border-radius: 4px;"
        )
        self.btn_load_proj.clicked.connect(self._load_project)
        t_layout.addWidget(self.btn_load_proj)

        self.btn_export_wav = QPushButton("Export WAV")
        self.btn_export_wav.setStyleSheet(
            "background-color: #0284C7; color: white; font-weight: bold; padding: 6px 10px; border-radius: 4px;"
        )
        self.btn_export_wav.clicked.connect(self._export_wav)
        t_layout.addWidget(self.btn_export_wav)

        self.btn_export_mp3 = QPushButton("Export MP3")
        self.btn_export_mp3.setStyleSheet(
            "background-color: #7C3AED; color: white; font-weight: bold; padding: 6px 10px; border-radius: 4px;"
        )
        self.btn_export_mp3.clicked.connect(self._export_mp3)
        t_layout.addWidget(self.btn_export_mp3)

        main_layout.addWidget(transport_frame)

        # 2. Piano Roll Editor
        self.piano_roll = PianoRollWidget(self)
        self.piano_roll.canvas.notes_changed.connect(self._on_notes_edited)
        main_layout.addWidget(self.piano_roll, 1)

    def _setup_timer(self) -> None:
        self.update_timer = QTimer(self)
        self.update_timer.setInterval(30)  # ~33 fps
        self.update_timer.timeout.connect(self._on_timer_tick)
        self.update_timer.start()

    def _on_timer_tick(self) -> None:
        self.recorder.update_timeline(0.03)

        # Format timeline seconds: MM:SS.cc
        pos = self.recorder.timeline_position
        mins = int(pos // 60)
        secs = int(pos % 60)
        centi = int((pos * 100) % 100)
        self.timeline_label.setText(f"{mins:02d}:{secs:02d}.{centi:02d}")

        self.piano_roll.canvas.set_playback_position(pos)

    def _toggle_record(self) -> None:
        if self.recorder.state == RecordingState.RECORDING:
            self.recorder.stop()
        else:
            with_ci = self.btn_count_in.isChecked()
            self.recorder.start_recording(with_count_in=with_ci)

    def _toggle_play(self) -> None:
        if self.recorder.state == RecordingState.PLAYING:
            self.recorder.pause()
        else:
            self.recorder.start_playback()

    def _stop(self) -> None:
        self.recorder.stop()
        self.recorder.set_timeline_position(0.0)
        # Synchronize recorded notes with piano roll
        if self.recorder.recorded_notes:
            self.piano_roll.canvas.set_notes(list(self.recorder.recorded_notes))

    def _on_bpm_changed(self, val: int) -> None:
        self.recorder.set_bpm(float(val))
        self.piano_roll.canvas.set_bpm(float(val))
        self.audio_engine.metronome.set_bpm(float(val))
        self.audio_engine.drum_sequencer.set_bpm(float(val))

    def _toggle_count_in(self) -> None:
        self.recorder.count_in_bars = 1 if self.btn_count_in.isChecked() else 0
        self.btn_count_in.setText(
            f"Count-in: {'1 Bar' if self.btn_count_in.isChecked() else 'OFF'}"
        )

    def _toggle_overdub(self) -> None:
        is_on = self.btn_overdub.isChecked()
        self.recorder.overdub = is_on
        self.btn_overdub.setText(f"Overdub: {'ON' if is_on else 'OFF'}")

    def _on_recorder_state_changed(self, state: RecordingState) -> None:
        if state == RecordingState.COUNT_IN:
            self.status_label.setText(f"Count-in ({self.recorder.count_in_remaining_beats})...")
            self.btn_rec.setText("● COUNT")
        elif state == RecordingState.RECORDING:
            self.status_label.setText("Recording...")
            self.btn_rec.setText("■ REC")
        elif state == RecordingState.PLAYING:
            self.status_label.setText("Playing...")
            self.btn_play.setText("❚❚ PAUSE")
        elif state == RecordingState.PAUSED:
            self.status_label.setText("Paused")
            self.btn_play.setText("▶ PLAY")
        else:
            self.status_label.setText("Stopped")
            self.btn_rec.setText("● REC")
            self.btn_play.setText("▶ PLAY")

    def _on_notes_edited(self) -> None:
        # Sync piano roll edits to recorded buffer
        self.recorder.recorded_notes = list(self.piano_roll.canvas.get_notes())

    def _save_project(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Project", "", "Music Master Project (*.mmp *.mmpz)"
        )
        if path:
            # Put notes into track 0
            if not self.project_manager.project.tracks:
                self.project_manager.project.tracks.append(
                    StudioTrack(
                        id="track-1",
                        name="Lead Track",
                        instrument_id=self.audio_engine.current_instrument_id,
                    )
                )
            self.project_manager.project.tracks[0].notes = self.piano_roll.canvas.get_notes()
            self.project_manager.project.bpm = self.recorder.bpm
            self.project_manager.save_project(path)
            QMessageBox.information(self, "Project Saved", f"Project saved successfully to {path}")

    def _load_project(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Project", "", "Music Master Project (*.mmp *.mmpz)"
        )
        if path and os.path.exists(path):
            proj = self.project_manager.load_project(path)
            self.bpm_spin.setValue(int(proj.bpm))
            if proj.tracks and proj.tracks[0].notes:
                self.piano_roll.canvas.set_notes(proj.tracks[0].notes)
                self.recorder.recorded_notes = list(proj.tracks[0].notes)
            QMessageBox.information(self, "Project Loaded", f"Loaded '{proj.name}' successfully.")

    def _export_wav(self) -> None:
        audio = self.recorder.get_recorded_audio()
        if audio is None or len(audio) == 0:
            QMessageBox.warning(
                self,
                "No Audio Data",
                "No recorded audio found. Please record a performance before exporting.",
            )
            return

        path, _ = QFileDialog.getSaveFileName(self, "Export WAV Audio", "output.wav", "WAV (*.wav)")
        if path:
            AudioExporter.export_wav(path, audio, self.audio_engine.sample_rate)
            QMessageBox.information(self, "Export Complete", f"Exported audio to {path}")

    def _export_mp3(self) -> None:
        audio = self.recorder.get_recorded_audio()
        if audio is None or len(audio) == 0:
            QMessageBox.warning(
                self,
                "No Audio Data",
                "No recorded audio found. Please record a performance before exporting.",
            )
            return

        path, _ = QFileDialog.getSaveFileName(self, "Export MP3 Audio", "output.mp3", "MP3 (*.mp3)")
        if path:
            AudioExporter.export_mp3(path, audio, self.audio_engine.sample_rate)
            QMessageBox.information(self, "Export Complete", f"Exported MP3 audio to {path}")
