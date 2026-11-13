from typing import List, Set

from PySide6.QtCore import QRect, Qt, Signal
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QWidget


class VirtualKeyboardWidget(QWidget):
    """Interactive visual piano/harmonium keyboard showing active notes and key triggers."""

    note_pressed = Signal(int)
    note_released = Signal(int)

    def __init__(
        self, start_midi: int = 48, num_keys: int = 36, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.start_midi = start_midi
        self.num_keys = num_keys
        self.active_notes: Set[int] = set()
        self.key_labels: dict[int, str] = {}

        self.setMinimumHeight(150)
        self.setSizeIncrement(1, 0)
        self._white_keys: List[int] = []
        self._black_keys: List[int] = []
        self._calculate_keys()

    def set_range(self, start_midi: int, num_keys: int) -> None:
        self.start_midi = start_midi
        self.num_keys = num_keys
        self._calculate_keys()
        self.update()

    def set_key_labels(self, labels: dict[int, str]) -> None:
        self.key_labels = labels
        self.update()

    def set_note_active(self, midi_note: int, active: bool) -> None:
        if active:
            self.active_notes.add(midi_note)
        else:
            self.active_notes.discard(midi_note)
        self.update()

    def clear_active_notes(self) -> None:
        self.active_notes.clear()
        self.update()

    def _is_black(self, midi_note: int) -> bool:
        return (midi_note % 12) in [1, 3, 6, 8, 10]

    def _calculate_keys(self) -> None:
        self._white_keys = []
        self._black_keys = []
        for note in range(self.start_midi, self.start_midi + self.num_keys):
            if self._is_black(note):
                self._black_keys.append(note)
            else:
                self._white_keys.append(note)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        num_white = len(self._white_keys)
        if num_white == 0:
            return

        white_width = w / num_white
        black_width = white_width * 0.65
        black_height = h * 0.62

        # Draw white keys
        white_rects: dict[int, QRect] = {}
        for idx, note in enumerate(self._white_keys):
            x = int(idx * white_width)
            kw = int((idx + 1) * white_width) - x
            rect = QRect(x, 0, kw, h)
            white_rects[note] = rect

            # Color
            if note in self.active_notes:
                painter.setBrush(QBrush(QColor("#38BDF8")))  # bright cyan for active
            else:
                painter.setBrush(QBrush(QColor("#FAFAFA")))

            painter.setPen(QPen(QColor("#27272A"), 1))
            painter.drawRoundedRect(rect, 2, 2)

            # Draw labels if available
            label = self.key_labels.get(note)
            if label:
                painter.setPen(QColor("#334155"))
                font = QFont("Segoe UI", 9, QFont.Weight.Bold)
                painter.setFont(font)
                painter.drawText(
                    rect.adjusted(0, 0, 0, -10),
                    Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter,
                    label,
                )

        # Draw black keys
        white_idx_map = {note: idx for idx, note in enumerate(self._white_keys)}
        for note in self._black_keys:
            # Position relative to previous white key
            prev_white = note - 1
            if prev_white in white_idx_map:
                w_idx = white_idx_map[prev_white]
                bx = int((w_idx + 1) * white_width - (black_width / 2.0))
                b_rect = QRect(bx, 0, int(black_width), int(black_height))

                if note in self.active_notes:
                    painter.setBrush(QBrush(QColor("#0284C7")))
                else:
                    painter.setBrush(QBrush(QColor("#18181B")))

                painter.setPen(QPen(QColor("#09090B"), 1))
                painter.drawRoundedRect(b_rect, 3, 3)

                label = self.key_labels.get(note)
                if label:
                    painter.setPen(QColor("#E2E8F0"))
                    font = QFont("Segoe UI", 8)
                    painter.setFont(font)
                    painter.drawText(
                        b_rect.adjusted(0, 0, 0, -6),
                        Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter,
                        label,
                    )
