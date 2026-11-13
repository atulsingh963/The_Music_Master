from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QVBoxLayout, QWidget


class DashboardPage(QWidget):
    """Main dashboard overview page."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # Welcome banner
        banner = QFrame()
        banner.setProperty("class", "Card")
        banner_layout = QVBoxLayout(banner)
        banner_layout.setContentsMargins(20, 20, 20, 20)

        welcome_title = QLabel("Welcome to Music Master")
        welcome_title.setStyleSheet("font-size: 22px; font-weight: 700; color: #FFFFFF;")
        subtitle = QLabel("Your Keyboard. Your Instruments. Your Music.")
        subtitle.setStyleSheet("font-size: 14px; color: #38BDF8;")
        desc = QLabel(
            "Standalone virtual musical studio featuring authentic Indian and Western instruments, "
            "low-latency keyboard input engine, music theory tools, and full production capabilities."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #94A3B8; margin-top: 8px;")

        banner_layout.addWidget(welcome_title)
        banner_layout.addWidget(subtitle)
        banner_layout.addWidget(desc)
        layout.addWidget(banner)

        # Feature highlights grid
        grid = QGridLayout()
        grid.setSpacing(16)

        cards_data = [
            (
                "Harmonium & Classical",
                "Authentic Indian harmonium with natural reed harmonics, sargam display, and thaat presets.",
            ),
            (
                "Grand Piano",
                "Full 88-key mapped acoustic piano with responsive velocity layers and sustain control.",
            ),
            (
                "Keyboard Mapper",
                "Custom key bindings for laptop keyboards, switchable octaves, and transpose controls.",
            ),
            (
                "Music Theory Hub",
                "Interactive Indian raga scales, Western chord modes, talas, and circle of fifths.",
            ),
            (
                "Mixer & Effects",
                "Multi-channel instrument mixer with reverb, delay, chorus, and master limiter.",
            ),
            (
                "MIDI Studio",
                "External hardware controller connection, live recording, and standard MIDI export.",
            ),
        ]

        for idx, (title, text) in enumerate(cards_data):
            row = idx // 2
            col = idx % 2
            card = QFrame()
            card.setProperty("class", "Card")
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(16, 16, 16, 16)

            lbl_title = QLabel(title)
            lbl_title.setProperty("class", "CardTitle")
            lbl_desc = QLabel(text)
            lbl_desc.setWordWrap(True)
            lbl_desc.setStyleSheet("color: #94A3B8; font-size: 12px; margin-top: 4px;")

            card_layout.addWidget(lbl_title)
            card_layout.addWidget(lbl_desc)
            card_layout.addStretch()
            grid.addWidget(card, row, col)

        layout.addLayout(grid)
        layout.addStretch()
