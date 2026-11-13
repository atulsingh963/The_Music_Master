"""Interactive Piano Roll Editor widget for visualizing, editing, and quantizing MIDI notes."""

from typing import List, Optional

from PySide6.QtCore import QPoint, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QFont, QMouseEvent, QPainter, QPaintEvent, QPen, QWheelEvent
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from music_master.midi.file import NoteEvent
from music_master.studio.quantizer import NoteQuantizer


class PianoRollCanvas(QWidget):
    """Grid canvas where MIDI notes are drawn, created, moved, and resized."""

    notes_changed = Signal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.notes: List[NoteEvent] = []
        self.bpm: float = 120.0
        self.grid_snap: str = "1/16"
        self.pixels_per_second: float = 120.0
        self.row_height: int = 20

        # Note range: 24 (C1) to 96 (C7) = 72 notes
        self.min_pitch = 24
        self.max_pitch = 96
        self.total_pitches = self.max_pitch - self.min_pitch + 1

        self.playback_position: float = 0.0

        # Mouse interaction state
        self._dragging_note_idx: Optional[int] = None
        self._resizing_note_idx: Optional[int] = None
        self._drag_start_pos: QPoint = QPoint()
        self._initial_note_start: float = 0.0
        self._initial_note_dur: float = 0.0
        self._initial_note_pitch: int = 60

        # Drawing styling
        self.grid_line_color = QColor(45, 55, 72)
        self.beat_line_color = QColor(74, 85, 104)
        self.bar_line_color = QColor(113, 128, 150)
        self.white_key_row = QColor(26, 32, 44)
        self.black_key_row = QColor(20, 24, 33)
        self.note_color = QColor(56, 189, 248)
        self.note_selected_color = QColor(245, 158, 11)
        self.playhead_color = QColor(239, 68, 68)

    def set_notes(self, notes: List[NoteEvent]) -> None:
        self.notes = notes
        self.update()

    def get_notes(self) -> List[NoteEvent]:
        return self.notes

    def set_bpm(self, bpm: float) -> None:
        self.bpm = max(20.0, bpm)
        self.update()

    def set_grid_snap(self, snap: str) -> None:
        self.grid_snap = snap

    def set_playback_position(self, pos: float) -> None:
        self.playback_position = pos
        self.update()

    def _pitch_to_y(self, pitch: int) -> float:
        """High pitch at top (y=0), low pitch at bottom."""
        row = self.max_pitch - pitch
        return row * self.row_height

    def _y_to_pitch(self, y: float) -> int:
        row = int(y // self.row_height)
        pitch = self.max_pitch - row
        return max(self.min_pitch, min(self.max_pitch, pitch))

    def _time_to_x(self, seconds: float) -> float:
        return seconds * self.pixels_per_second

    def _x_to_time(self, x: float) -> float:
        return max(0.0, x / self.pixels_per_second)

    def _is_black_key(self, pitch: int) -> bool:
        return (pitch % 12) in (1, 3, 6, 8, 10)

    def _pitch_name(self, pitch: int) -> str:
        names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        octave = (pitch // 12) - 1
        return f"{names[pitch % 12]}{octave}"

    def snap_time(self, t: float) -> float:
        subdiv = NoteQuantizer.GRID_SUBDIVISIONS.get(self.grid_snap, 0.25)
        step = subdiv * (60.0 / self.bpm)
        return round(t / step) * step

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)

        width = self.width()
        height = self.total_pitches * self.row_height

        # 1. Pitch Rows
        for pitch in range(self.min_pitch, self.max_pitch + 1):
            y = self._pitch_to_y(pitch)
            bg_col = self.black_key_row if self._is_black_key(pitch) else self.white_key_row
            painter.fillRect(QRectF(0, y, width, self.row_height), bg_col)
            painter.setPen(QPen(self.grid_line_color, 1))
            painter.drawLine(0, int(y + self.row_height), width, int(y + self.row_height))

        # 2. Vertical Beat & Bar Lines
        beat_dur = 60.0 / self.bpm
        max_time = self._x_to_time(width) + 1.0
        num_beats = int(max_time / beat_dur) + 1

        for b in range(num_beats):
            t = b * beat_dur
            x = int(self._time_to_x(t))
            if b % 4 == 0:
                painter.setPen(QPen(self.bar_line_color, 1.5))
            else:
                painter.setPen(QPen(self.beat_line_color, 1))
            painter.drawLine(x, 0, x, height)

        # 3. Draw Notes
        for i, n in enumerate(self.notes):
            note_x = self._time_to_x(n.start_time)
            w = max(4.0, self._time_to_x(n.duration))
            y = self._pitch_to_y(n.note)
            h = self.row_height - 2

            # Note body
            col = self.note_selected_color if i == self._dragging_note_idx else self.note_color
            painter.fillRect(QRectF(note_x, y + 1, w, h), col)

            # Note border
            painter.setPen(QPen(QColor(15, 23, 42), 1))
            painter.drawRect(QRectF(note_x, y + 1, w, h))

            # Note name text if width allows
            if w > 24:
                painter.setPen(QColor(15, 23, 42))
                painter.setFont(QFont("Arial", 8, QFont.Weight.Bold))
                painter.drawText(int(note_x + 4), int(y + 14), self._pitch_name(n.note))

        # 4. Playback Cursor Line
        cursor_x = int(self._time_to_x(self.playback_position))
        painter.setPen(QPen(self.playhead_color, 2))
        painter.drawLine(cursor_x, 0, cursor_x, height)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        pos = event.position()
        pitch = self._y_to_pitch(pos.y())
        t = self._x_to_time(pos.x())

        # Check if clicked on an existing note
        found_idx = None
        resize_mode = False
        for i, n in enumerate(self.notes):
            if n.note == pitch:
                if n.start_time <= t <= (n.start_time + n.duration):
                    found_idx = i
                    # If clicked near right edge, treat as resize
                    note_end_x = self._time_to_x(n.start_time + n.duration)
                    if abs(pos.x() - note_end_x) < 8:
                        resize_mode = True
                    break

        if event.button() == Qt.MouseButton.LeftButton:
            if found_idx is not None:
                if resize_mode:
                    self._resizing_note_idx = found_idx
                    self._initial_note_dur = self.notes[found_idx].duration
                else:
                    self._dragging_note_idx = found_idx
                    self._initial_note_start = self.notes[found_idx].start_time
                    self._initial_note_pitch = self.notes[found_idx].note
                self._drag_start_pos = pos.toPoint()
            else:
                # Add new note at snapped position
                snap_t = self.snap_time(t)
                dur = (60.0 / self.bpm) * NoteQuantizer.GRID_SUBDIVISIONS.get(self.grid_snap, 0.25)
                new_note = NoteEvent(
                    note=pitch,
                    velocity=100,
                    start_time=snap_t,
                    duration=dur,
                )
                self.notes.append(new_note)
                self.notes.sort(key=lambda x: x.start_time)
                self.notes_changed.emit()
            self.update()

        elif event.button() == Qt.MouseButton.RightButton:
            # Delete note under cursor
            if found_idx is not None:
                self.notes.pop(found_idx)
                self.notes_changed.emit()
                self.update()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        pos = event.position()
        delta_x = pos.x() - self._drag_start_pos.x()
        delta_seconds = delta_x / self.pixels_per_second

        if self._dragging_note_idx is not None and self._dragging_note_idx < len(self.notes):
            n = self.notes[self._dragging_note_idx]
            new_start = max(0.0, self._initial_note_start + delta_seconds)
            new_pitch = self._y_to_pitch(pos.y())
            n.start_time = self.snap_time(new_start)
            n.note = int(new_pitch)
            self.notes_changed.emit()
            self.update()

        elif self._resizing_note_idx is not None and self._resizing_note_idx < len(self.notes):
            n = self.notes[self._resizing_note_idx]
            new_dur = max(0.05, self._initial_note_dur + delta_seconds)
            n.duration = new_dur
            self.notes_changed.emit()
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self._dragging_note_idx = None
        self._resizing_note_idx = None
        self.update()

    def wheelEvent(self, event: QWheelEvent) -> None:
        # Ctrl + Wheel for horizontal zoom
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.pixels_per_second = min(400.0, self.pixels_per_second * 1.15)
            else:
                self.pixels_per_second = max(30.0, self.pixels_per_second / 1.15)
            self.update()
        else:
            super().wheelEvent(event)


class PianoRollWidget(QWidget):
    """Complete Piano Roll component with transport controls, grid snap, and quantization."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Toolbar
        toolbar = QFrame()
        toolbar.setStyleSheet("background-color: #1E293B; border-radius: 6px; padding: 4px;")
        t_layout = QHBoxLayout(toolbar)
        t_layout.setContentsMargins(8, 4, 8, 4)
        t_layout.setSpacing(12)

        # Quantize Snap Combo
        t_layout.addWidget(QLabel("Grid Snap:"))
        self.snap_combo = QComboBox()
        self.snap_combo.addItems(["1/4", "1/8", "1/16", "1/32", "1/8T", "1/16T"])
        self.snap_combo.setCurrentText("1/16")
        self.snap_combo.currentTextChanged.connect(self._on_snap_changed)
        t_layout.addWidget(self.snap_combo)

        # Quantize Button
        self.btn_quantize = QPushButton("Quantize All")
        self.btn_quantize.setStyleSheet(
            "background-color: #0284C7; color: white; padding: 4px 10px; border-radius: 4px;"
        )
        self.btn_quantize.clicked.connect(self._on_quantize_clicked)
        t_layout.addWidget(self.btn_quantize)

        # Clear Notes
        self.btn_clear = QPushButton("Clear All Notes")
        self.btn_clear.setStyleSheet(
            "background-color: #DC2626; color: white; padding: 4px 10px; border-radius: 4px;"
        )
        self.btn_clear.clicked.connect(self._on_clear_clicked)
        t_layout.addWidget(self.btn_clear)

        t_layout.addStretch()

        # Zoom Controls
        t_layout.addWidget(QLabel("Zoom:"))
        self.btn_zoom_in = QPushButton("+")
        self.btn_zoom_in.setFixedWidth(30)
        self.btn_zoom_in.clicked.connect(lambda: self._adjust_zoom(1.2))
        t_layout.addWidget(self.btn_zoom_in)

        self.btn_zoom_out = QPushButton("-")
        self.btn_zoom_out.setFixedWidth(30)
        self.btn_zoom_out.clicked.connect(lambda: self._adjust_zoom(0.8))
        t_layout.addWidget(self.btn_zoom_out)

        layout.addWidget(toolbar)

        # Canvas
        self.canvas = PianoRollCanvas(self)
        self.canvas.setMinimumHeight(450)
        layout.addWidget(self.canvas)

    def _on_snap_changed(self, snap: str) -> None:
        self.canvas.set_grid_snap(snap)

    def _on_quantize_clicked(self) -> None:
        current_notes = self.canvas.get_notes()
        quantized = NoteQuantizer.quantize_notes(
            current_notes, grid=self.canvas.grid_snap, bpm=self.canvas.bpm
        )
        self.canvas.set_notes(quantized)

    def _on_clear_clicked(self) -> None:
        self.canvas.set_notes([])

    def _adjust_zoom(self, factor: float) -> None:
        self.canvas.pixels_per_second = max(
            30.0, min(500.0, self.canvas.pixels_per_second * factor)
        )
        self.canvas.update()
