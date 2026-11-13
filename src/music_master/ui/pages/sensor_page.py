"""Sensor Studio Page for testing motion tilt, keyboard velocity approximation, and expression mapping."""

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from music_master.audio.engine import AudioEngine
from music_master.sensors.engine import SensorEngine, SensorReading


class SensorStudioPage(QWidget):
    """UI for inspecting motion sensors, calibrating resting position, and testing fallback controls."""

    def __init__(
        self,
        audio_engine: AudioEngine,
        sensor_engine: SensorEngine,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.audio_engine = audio_engine
        self.sensor_engine = sensor_engine

        self._init_ui()
        self.sensor_engine.reading_callbacks.append(self._on_sensor_reading)

    def _init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(14)

        # Header Title
        title = QLabel("Sensor Studio & Accessibility")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #F8FAFC;")
        main_layout.addWidget(title)

        subtitle = QLabel(
            "Hardware accelerometer/orientation detection with responsive fallback expression controls."
        )
        subtitle.setStyleSheet("font-size: 13px; color: #94A3B8;")
        main_layout.addWidget(subtitle)

        # 1. Device Hardware Status Card
        status_card = QFrame()
        status_card.setStyleSheet(
            "background-color: #0F172A; border: 1px solid #334155; border-radius: 8px; padding: 12px;"
        )
        sc_layout = QHBoxLayout(status_card)

        hw_status_text = (
            "Hardware Sensors: ACTIVE"
            if self.sensor_engine.is_hardware_available
            else "Hardware Sensors: NOT DETECTED (Graceful Fallback Mode Active)"
        )
        self.lbl_hw_status = QLabel(hw_status_text)
        self.lbl_hw_status.setStyleSheet(
            "font-weight: bold; font-size: 14px; color: "
            + ("#10B981;" if self.sensor_engine.is_hardware_available else "#F59E0B;")
        )
        sc_layout.addWidget(self.lbl_hw_status)
        sc_layout.addStretch()

        self.btn_calibrate = QPushButton("Calibrate Zero Reference")
        self.btn_calibrate.setStyleSheet(
            "background-color: #0284C7; color: white; padding: 6px 14px; border-radius: 4px;"
        )
        self.btn_calibrate.clicked.connect(self._on_calibrate_clicked)
        sc_layout.addWidget(self.btn_calibrate)

        main_layout.addWidget(status_card)

        # 2. Expression Visualizers & Manual Fallback Sliders
        sliders_box = QGroupBox("Live Expression & Motion Controls")
        s_layout = QGridLayout(sliders_box)
        s_layout.setSpacing(12)

        # Pitch Bend (-1.0 to 1.0)
        s_layout.addWidget(QLabel("Pitch Bend (Tilt X):"), 0, 0)
        self.slider_pitch_bend = QSlider(Qt.Orientation.Horizontal)
        self.slider_pitch_bend.setRange(-100, 100)
        self.slider_pitch_bend.setValue(0)
        self.slider_pitch_bend.valueChanged.connect(self._on_manual_pitch_bend)
        s_layout.addWidget(self.slider_pitch_bend, 0, 1)
        self.lbl_pitch_val = QLabel("0.00")
        self.lbl_pitch_val.setFixedWidth(40)
        s_layout.addWidget(self.lbl_pitch_val, 0, 2)

        # Expression / Filter Cutoff (0.0 to 1.0)
        s_layout.addWidget(QLabel("Filter / Expression (Tilt Y):"), 1, 0)
        self.slider_expr = QSlider(Qt.Orientation.Horizontal)
        self.slider_expr.setRange(0, 100)
        self.slider_expr.setValue(50)
        self.slider_expr.valueChanged.connect(self._on_manual_expression)
        s_layout.addWidget(self.slider_expr, 1, 1)
        self.lbl_expr_val = QLabel("0.50")
        self.lbl_expr_val.setFixedWidth(40)
        s_layout.addWidget(self.lbl_expr_val, 1, 2)

        # Modulation (0.0 to 1.0)
        s_layout.addWidget(QLabel("Modulation / Vibrato (Tilt Z):"), 2, 0)
        self.slider_mod = QSlider(Qt.Orientation.Horizontal)
        self.slider_mod.setRange(0, 100)
        self.slider_mod.setValue(0)
        self.slider_mod.valueChanged.connect(self._on_manual_modulation)
        s_layout.addWidget(self.slider_mod, 2, 1)
        self.lbl_mod_val = QLabel("0.00")
        self.lbl_mod_val.setFixedWidth(40)
        s_layout.addWidget(self.lbl_mod_val, 2, 2)

        main_layout.addWidget(sliders_box)

        # 3. Dynamic Key Velocity Approximation Card
        vel_card = QGroupBox("Key Velocity Approximation")
        v_layout = QVBoxLayout(vel_card)

        vel_desc = QLabel(
            "Measures inter-key typing tempo to approximate velocity dynamically (fast phrases hit higher velocities)."
        )
        vel_desc.setStyleSheet("color: #94A3B8; font-size: 12px;")
        v_layout.addWidget(vel_desc)

        self.vel_progress = QProgressBar()
        self.vel_progress.setRange(0, 127)
        self.vel_progress.setValue(100)
        self.vel_progress.setFormat("Last Estimated Velocity: %v / 127")
        self.vel_progress.setStyleSheet(
            "QProgressBar { background-color: #1E293B; border-radius: 4px; height: 20px; text-align: center; color: white; }"
            "QProgressBar::chunk { background-color: #38BDF8; border-radius: 4px; }"
        )
        v_layout.addWidget(self.vel_progress)

        main_layout.addWidget(vel_card)
        main_layout.addStretch()

    def _on_calibrate_clicked(self) -> None:
        self.sensor_engine.calibrate(0.0, 0.0, 0.0)
        self.slider_pitch_bend.setValue(0)
        self.slider_expr.setValue(50)
        self.slider_mod.setValue(0)

    def _on_manual_pitch_bend(self, val: int) -> None:
        norm = val / 100.0
        self.sensor_engine.pitch_bend = norm
        self.lbl_pitch_val.setText(f"{norm:.2f}")

    def _on_manual_expression(self, val: int) -> None:
        norm = val / 100.0
        self.sensor_engine.expression = norm
        self.lbl_expr_val.setText(f"{norm:.2f}")

    def _on_manual_modulation(self, val: int) -> None:
        norm = val / 100.0
        self.sensor_engine.modulation = norm
        self.lbl_mod_val.setText(f"{norm:.2f}")

    def _on_sensor_reading(self, reading: SensorReading) -> None:
        self.slider_pitch_bend.blockSignals(True)
        self.slider_expr.blockSignals(True)
        self.slider_mod.blockSignals(True)

        self.slider_pitch_bend.setValue(int(reading.x * 100))
        self.slider_expr.setValue(int(((reading.y + 1.0) / 2.0) * 100))
        self.slider_mod.setValue(int(abs(reading.z) * 100))

        self.lbl_pitch_val.setText(f"{reading.x:.2f}")
        self.lbl_expr_val.setText(f"{((reading.y + 1.0) / 2.0):.2f}")
        self.lbl_mod_val.setText(f"{abs(reading.z):.2f}")

        self.slider_pitch_bend.blockSignals(False)
        self.slider_expr.blockSignals(False)
        self.slider_mod.blockSignals(False)
