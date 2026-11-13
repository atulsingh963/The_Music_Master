"""Motion, orientation, and keyboard expression mapping engine with fallback."""

import enum
import logging
import platform
import time
from dataclasses import dataclass
from typing import Callable, List

logger = logging.getLogger(__name__)


class SensorType(enum.Enum):
    ACCELEROMETER = "accelerometer"
    GYROSCOPE = "gyroscope"
    ORIENTATION = "orientation"
    HINGE_ANGLE = "hinge_angle"
    KEYBOARD_FALLBACK = "keyboard_fallback"


@dataclass
class SensorReading:
    sensor_type: SensorType
    x: float = 0.0  # Pitch / Tilt X (-1.0 to 1.0)
    y: float = 0.0  # Roll / Tilt Y (-1.0 to 1.0)
    z: float = 0.0  # Yaw / Tilt Z (-1.0 to 1.0)
    timestamp: float = 0.0


class SensorEngine:
    """Detects available system sensors and handles expression mappings (pitch bend, filter, vibrato)."""

    def __init__(self) -> None:
        self.is_hardware_available = False
        self.detected_sensors: List[SensorType] = []
        self._active_mapping = {
            "tilt_x": "pitch_bend",  # left/right tilt -> pitch bend
            "tilt_y": "filter_cutoff",  # forward/back tilt -> filter / expression
            "tilt_z": "modulation",  # rotation -> vibrato modulation
        }

        # Expression values (-1.0 to 1.0 or 0.0 to 1.0)
        self.pitch_bend: float = 0.0
        self.expression: float = 0.0
        self.modulation: float = 0.0

        # Calibration offsets
        self.offset_x: float = 0.0
        self.offset_y: float = 0.0
        self.offset_z: float = 0.0

        # Key velocity tracking for keyboard approximation (duration between key strokes)
        self._last_key_press_time: float = 0.0

        self.reading_callbacks: List[Callable[[SensorReading], None]] = []
        self.detect_hardware()

    def detect_hardware(self) -> None:
        """Probes OS/hardware for accelerometer / gyro sensors."""
        self.detected_sensors.clear()

        # On Windows, Windows.Devices.Sensors can be queried via WinRT if available
        if platform.system() == "Windows":
            try:
                # Test WinRT availability without crashing
                import winsdk.windows.devices.sensors as win_sensors  # type: ignore

                accel = win_sensors.Accelerometer.get_default()
                if accel:
                    self.detected_sensors.append(SensorType.ACCELEROMETER)
                gyro = win_sensors.Gyrometer.get_default()
                if gyro:
                    self.detected_sensors.append(SensorType.GYROSCOPE)
            except Exception:
                # Expected when winsdk is not present or device is a desktop PC without sensors
                pass

        if self.detected_sensors:
            self.is_hardware_available = True
        else:
            self.is_hardware_available = False
            # Always enable software / keyboard fallback
            self.detected_sensors.append(SensorType.KEYBOARD_FALLBACK)

    def calibrate(self, x: float = 0.0, y: float = 0.0, z: float = 0.0) -> None:
        """Sets current sensor resting position as zero reference."""
        self.offset_x = x
        self.offset_y = y
        self.offset_z = z

    def process_sensor_input(self, raw_x: float, raw_y: float, raw_z: float) -> SensorReading:
        """Normalizes and maps raw tilt values into musical control parameters."""
        calibrated_x = max(-1.0, min(1.0, raw_x - self.offset_x))
        calibrated_y = max(-1.0, min(1.0, raw_y - self.offset_y))
        calibrated_z = max(-1.0, min(1.0, raw_z - self.offset_z))

        # Map to musical expressions
        self.pitch_bend = calibrated_x
        self.expression = max(0.0, min(1.0, (calibrated_y + 1.0) / 2.0))
        self.modulation = abs(calibrated_z)

        reading = SensorReading(
            sensor_type=SensorType.ACCELEROMETER
            if self.is_hardware_available
            else SensorType.KEYBOARD_FALLBACK,
            x=calibrated_x,
            y=calibrated_y,
            z=calibrated_z,
            timestamp=time.time(),
        )

        for cb in self.reading_callbacks:
            try:
                cb(reading)
            except Exception as e:
                logger.exception(f"Error in sensor callback: {e}")

        return reading

    def approximate_velocity(self) -> int:
        """Calculates dynamic velocity based on typing speed intervals (key press delta)."""
        now = time.time()
        delta = now - self._last_key_press_time
        self._last_key_press_time = now

        # Faster key hits (< 0.08s) imply high velocity; slower hits (> 0.3s) imply gentle/piano velocity
        if delta < 0.08:
            velocity = 120
        elif delta < 0.15:
            velocity = 100
        elif delta < 0.25:
            velocity = 85
        else:
            velocity = 70

        return velocity

    def trigger_key_pitch_bend(self, semitones: float) -> None:
        """Allows keyboard keys (e.g. Left/Right arrow or custom key) to pitch bend."""
        self.pitch_bend = max(-1.0, min(1.0, semitones / 2.0))

    def trigger_key_modulation(self, depth: float) -> None:
        """Allows keyboard keys to trigger modulation wheel values."""
        self.modulation = max(0.0, min(1.0, depth))
