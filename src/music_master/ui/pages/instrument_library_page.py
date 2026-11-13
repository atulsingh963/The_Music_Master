from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from music_master.instruments.base import AvailabilityState
from music_master.instruments.registry import InstrumentRegistry


class InstrumentLibraryPage(QWidget):
    """Browse catalog of planned and available instruments."""

    def __init__(self, registry: InstrumentRegistry, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.registry = registry
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header controls
        hdr_layout = QHBoxLayout()
        title = QLabel("Instrument Catalogue")
        title.setStyleSheet("font-size: 20px; font-weight: 700; color: #FFFFFF;")
        hdr_layout.addWidget(title)
        hdr_layout.addStretch()

        filter_lbl = QLabel("Filter:")
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All Instruments", "Available Only", "Planned Only"])
        self.filter_combo.currentTextChanged.connect(self._populate_table)
        hdr_layout.addWidget(filter_lbl)
        hdr_layout.addWidget(self.filter_combo)
        layout.addLayout(hdr_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["Name", "Category", "Status", "Engine / Sound Source", "Description"]
        )
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.horizontalHeader().setSectionResizeMode(
            3, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #18181B;
                gridline-color: #27272A;
                border: 1px solid #27272A;
                border-radius: 6px;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #27272A;
                color: #A1A1AA;
                font-weight: 600;
                padding: 6px;
                border: none;
            }
        """)
        layout.addWidget(self.table)

        self._populate_table()

    def _populate_table(self) -> None:
        filter_mode = self.filter_combo.currentText()
        instruments = self.registry.get_all()

        filtered = []
        for inst in instruments:
            if filter_mode == "Available Only" and inst.availability != AvailabilityState.AVAILABLE:
                continue
            if filter_mode == "Planned Only" and inst.availability != AvailabilityState.PLANNED:
                continue
            filtered.append(inst)

        self.table.setRowCount(len(filtered))
        for row, inst in enumerate(filtered):
            name_item = QTableWidgetItem(inst.name)
            cat_item = QTableWidgetItem(inst.category.value)
            status_item = QTableWidgetItem(inst.availability.value)
            source_item = QTableWidgetItem(inst.sound_source)
            desc_item = QTableWidgetItem(inst.description)

            if inst.availability == AvailabilityState.AVAILABLE:
                status_item.setForeground(Qt.GlobalColor.green)
            else:
                status_item.setForeground(Qt.GlobalColor.darkYellow)

            self.table.setItem(row, 0, name_item)
            self.table.setItem(row, 1, cat_item)
            self.table.setItem(row, 2, status_item)
            self.table.setItem(row, 3, source_item)
            self.table.setItem(row, 4, desc_item)
