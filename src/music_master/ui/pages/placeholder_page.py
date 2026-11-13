from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget


class PlaceholderPage(QWidget):
    """Reusable page placeholder for roadmap modules pending implementation."""

    def __init__(
        self, title: str, description: str, milestone_info: str, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QFrame()
        card.setProperty("class", "Card")
        card.setMinimumWidth(500)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(32, 32, 32, 32)
        card_layout.setSpacing(12)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("font-size: 20px; font-weight: 700; color: #FFFFFF;")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl_desc = QLabel(description)
        lbl_desc.setWordWrap(True)
        lbl_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_desc.setStyleSheet("color: #94A3B8; font-size: 13px;")

        lbl_badge = QLabel(f"Status: {milestone_info}")
        lbl_badge.setStyleSheet(
            "background-color: #27272A; color: #F59E0B; border: 1px solid #D97706; "
            "border-radius: 4px; padding: 4px 10px; font-weight: 600; font-size: 11px;"
        )
        lbl_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card_layout.addWidget(lbl_title)
        card_layout.addWidget(lbl_desc)
        card_layout.addSpacing(10)
        card_layout.addWidget(lbl_badge)

        layout.addWidget(card)
