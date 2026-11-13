"""Multi-track audio mixing console with metering, pan, volume, mute/solo, and insert effects."""

from dataclasses import dataclass
from typing import Dict, Optional

import numpy as np

from music_master.mixer.effects import DelayEffect, Equalizer3Band, PeakLimiter, ReverbEffect


@dataclass
class ChannelMeter:
    peak_l: float = 0.0
    peak_r: float = 0.0
    rms_l: float = 0.0
    rms_r: float = 0.0


class MixerTrack:
    """Represents a single audio mixing channel."""

    def __init__(self, track_id: str, name: str, sample_rate: int = 44100) -> None:
        self.track_id = track_id
        self.name = name
        self.sample_rate = sample_rate

        self.volume: float = 0.85  # 0.0 to 1.2
        self.pan: float = 0.0  # -1.0 (Left) to +1.0 (Right)
        self.mute: bool = False
        self.solo: bool = False

        # Channel effects
        self.eq = Equalizer3Band(sample_rate=sample_rate)
        self.reverb = ReverbEffect(sample_rate=sample_rate)
        self.reverb.enabled = False  # Disabled by default on individual tracks
        self.delay = DelayEffect(sample_rate=sample_rate)
        self.delay.enabled = False

        self.meter = ChannelMeter()

    def process_block(self, audio: np.ndarray) -> np.ndarray:
        """Processes input buffer for this channel, updates meters, returns stereo output."""
        num_frames = len(audio)
        if num_frames == 0:
            return np.zeros((0, 2), dtype=np.float32)

        # Ensure stereo
        if audio.ndim == 1:
            stereo = np.column_stack((audio, audio))
        elif audio.shape[1] == 1:
            stereo = np.column_stack((audio[:, 0], audio[:, 0]))
        else:
            stereo = audio.copy()

        # Apply channel EQ
        if self.eq.enabled:
            stereo = self.eq.process(stereo)

        # Apply channel delay
        if self.delay.enabled:
            stereo = self.delay.process(stereo)

        # Apply channel reverb
        if self.reverb.enabled:
            stereo = self.reverb.process(stereo)

        # Apply volume
        stereo *= self.volume

        # Apply Pan (-1.0 to 1.0) using constant power panning
        # pan=-1 => L=1, R=0; pan=0 => L=0.707, R=0.707; pan=1 => L=0, R=1
        pan_angle = (self.pan + 1.0) * (np.pi / 4.0)  # 0 to pi/2
        gain_l = float(np.cos(pan_angle))
        gain_r = float(np.sin(pan_angle))
        stereo[:, 0] *= gain_l
        stereo[:, 1] *= gain_r

        # Calculate peak and RMS meters
        self._update_meter(stereo)

        return stereo.astype(np.float32)

    def _update_meter(self, stereo: np.ndarray) -> None:
        if len(stereo) == 0:
            return
        self.meter.peak_l = float(np.max(np.abs(stereo[:, 0])))
        self.meter.peak_r = float(np.max(np.abs(stereo[:, 1])))
        self.meter.rms_l = float(np.sqrt(np.mean(stereo[:, 0] ** 2)))
        self.meter.rms_r = float(np.sqrt(np.mean(stereo[:, 1] ** 2)))


class MixerEngine:
    """Master audio mixer managing multiple tracks, master bus, and master limiter."""

    def __init__(self, sample_rate: int = 44100) -> None:
        self.sample_rate = sample_rate
        self.tracks: Dict[str, MixerTrack] = {}
        self.master_volume: float = 0.85
        self.master_meter = ChannelMeter()

        # Master insert effects
        self.master_eq = Equalizer3Band(sample_rate=sample_rate)
        self.master_reverb = ReverbEffect(sample_rate=sample_rate)
        self.master_delay = DelayEffect(sample_rate=sample_rate)
        self.master_limiter = PeakLimiter(sample_rate=sample_rate, threshold_db=-0.3)

        self._setup_default_tracks()

    def _setup_default_tracks(self) -> None:
        default_tracks = [
            ("synth", "Synth / Keys"),
            ("drums", "Drum Machine"),
            ("tanpura", "Tanpura Drone"),
            ("tabla", "Tabla"),
            ("metronome", "Metronome"),
        ]
        for tid, name in default_tracks:
            self.tracks[tid] = MixerTrack(tid, name, sample_rate=self.sample_rate)

    def get_track(self, track_id: str) -> Optional[MixerTrack]:
        return self.tracks.get(track_id)

    def set_track_volume(self, track_id: str, volume: float) -> None:
        track = self.get_track(track_id)
        if track:
            track.volume = max(0.0, min(1.5, volume))

    def set_track_pan(self, track_id: str, pan: float) -> None:
        track = self.get_track(track_id)
        if track:
            track.pan = max(-1.0, min(1.0, pan))

    def set_track_mute(self, track_id: str, mute: bool) -> None:
        track = self.get_track(track_id)
        if track:
            track.mute = mute

    def set_track_solo(self, track_id: str, solo: bool) -> None:
        track = self.get_track(track_id)
        if track:
            track.solo = solo

    def mix_tracks(self, track_buffers: Dict[str, np.ndarray], num_frames: int) -> np.ndarray:
        """Mixes audio buffers from all active tracks down to a stereo master bus with master effects."""
        master_bus = np.zeros((num_frames, 2), dtype=np.float32)

        # Check if any track is soloed
        any_solo = any(t.solo for t in self.tracks.values())

        for tid, track in self.tracks.items():
            if any_solo and not track.solo:
                # Track is skipped if another track is soloed
                track.meter.peak_l = 0.0
                track.meter.peak_r = 0.0
                track.meter.rms_l = 0.0
                track.meter.rms_r = 0.0
                continue
            if track.mute:
                track.meter.peak_l = 0.0
                track.meter.peak_r = 0.0
                track.meter.rms_l = 0.0
                track.meter.rms_r = 0.0
                continue

            buf = track_buffers.get(tid)
            if buf is not None and len(buf) > 0:
                track_out = track.process_block(buf)
                master_bus += track_out
            else:
                track.meter.peak_l = 0.0
                track.meter.peak_r = 0.0
                track.meter.rms_l = 0.0
                track.meter.rms_r = 0.0

        # Master bus volume
        master_bus *= self.master_volume

        # Master EQ
        if self.master_eq.enabled:
            master_bus = self.master_eq.process(master_bus)

        # Master Delay
        if self.master_delay.enabled:
            master_bus = self.master_delay.process(master_bus)

        # Master Reverb
        if self.master_reverb.enabled:
            master_bus = self.master_reverb.process(master_bus)

        # Master Limiter
        if self.master_limiter.enabled:
            master_bus = self.master_limiter.process(master_bus)

        # Master meter update
        self._update_master_meter(master_bus)

        return master_bus

    def _update_master_meter(self, stereo: np.ndarray) -> None:
        if len(stereo) == 0:
            return
        self.master_meter.peak_l = float(np.max(np.abs(stereo[:, 0])))
        self.master_meter.peak_r = float(np.max(np.abs(stereo[:, 1])))
        self.master_meter.rms_l = float(np.sqrt(np.mean(stereo[:, 0] ** 2)))
        self.master_meter.rms_r = float(np.sqrt(np.mean(stereo[:, 1] ** 2)))
