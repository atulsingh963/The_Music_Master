# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-11-14

### Added
- **Core Architecture & Package Setup**: Configured package metadata, dependencies, Ruff, Mypy, and Pytest configs.
- **Audio Synthesis Engine**: Real-time multi-harmonic polyphonic synthesis engine with sounddevice streaming, buffer configuration, ADSR envelope shaping, and soft limiter protection.
- **Input & Keyboard Mapping**: Deduplicated keyboard controller supporting Harmonium Sargam and Piano chromatic profiles, octave shifts, transpose, sustain pedal, and panic control.
- **Instrument Catalogue**: Comprehensive 25+ instrument registry with authentic availability state tracking (`Available`, `Installed`, `Missing Sound Library`, `Experimental`, `Planned`).
- **Interactive UI & Themes**: PySide6 dark-themed desktop studio with sidebar navigation, Dashboard, Harmonium studio, Piano studio, Instrument Library, and Virtual Keyboard representation.
- **Music Theory Foundation**: Sargam converter, Saptak models, Western note mapping, and initial data-driven Raga presets (Yaman, Bhairav, Bhairavi, Kafi, Bageshri, Malkauns, Durga, Khamaj).
- **Test Suite**: Automated unit and GUI test coverage for audio rendering, note triggers, profiles, and UI navigation.
