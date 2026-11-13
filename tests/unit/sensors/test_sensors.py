"""Unit tests for Phase 14 Sensor & Accessibility module."""

import time

from music_master.sensors.engine import SensorEngine, SensorType


def test_sensor_engine_fallback_detection():
    engine = SensorEngine()
    assert len(engine.detected_sensors) > 0
    # On environments without hardware, fallback should be present
    assert engine.is_hardware_available or SensorType.KEYBOARD_FALLBACK in engine.detected_sensors


def test_sensor_engine_processing_and_calibration():
    engine = SensorEngine()
    engine.calibrate(x=0.1, y=0.1, z=0.0)

    # Process reading
    reading = engine.process_sensor_input(raw_x=0.5, raw_y=0.1, raw_z=0.4)
    assert abs(reading.x - 0.4) < 1e-4
    assert abs(reading.y - 0.0) < 1e-4
    assert abs(reading.z - 0.4) < 1e-4

    assert abs(engine.pitch_bend - 0.4) < 1e-4
    assert abs(engine.expression - 0.5) < 1e-4
    assert abs(engine.modulation - 0.4) < 1e-4


def test_velocity_approximation():
    engine = SensorEngine()

    # First call sets initial time
    engine.approximate_velocity()

    # Fast follow up (<0.08s)
    time.sleep(0.02)
    vel_fast = engine.approximate_velocity()
    assert vel_fast >= 100

    # Slower follow up (>0.3s)
    time.sleep(0.32)
    vel_slow = engine.approximate_velocity()
    assert vel_slow <= 75
