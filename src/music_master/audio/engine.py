import math
from typing import Any, Dict, List

import numpy as np

from music_master.instruments.indian.tabla import TablaSynthesizer
from music_master.instruments.indian.tanpura import TanpuraDroneEngine
from music_master.instruments.percussion.drum_synthesizer import DrumMachineEngine
from music_master.instruments.percussion.sequencer import DrumSequencer
from music_master.mixer.track import MixerEngine
from music_master.theory.metronome import MetronomeEngine
from music_master.theory.tuning import TuningEngine


def midi_to_freq(midi_note: int) -> float:
    """Converts a MIDI note number (0-127) to frequency in Hz (A4 = 69 = 440Hz)."""
    return float(440.0 * (2.0 ** ((midi_note - 69) / 12.0)))


class Voice:
    """Represents a single active polyphonic note voice."""

    def __init__(
        self,
        midi_note: int,
        velocity: float,
        sample_rate: int,
        instrument_id: str = "harmonium",
        freq: float | None = None,
    ) -> None:
        self.midi_note = midi_note
        self.freq = freq if freq is not None else midi_to_freq(midi_note)
        self.velocity = max(0.0, min(1.0, velocity / 127.0 if velocity > 1 else velocity))
        self.sample_rate = sample_rate
        self.instrument_id = instrument_id

        # Phase tracking
        self.phase = 0.0
        self.phase_step = (2.0 * math.pi * self.freq) / self.sample_rate

        # Envelope parameters (Attack, Decay, Sustain level, Release time)
        self.is_releasing = False
        self.is_dead = False
        self.env_level = 0.0

        # Configure voice timbre based on instrument
        if instrument_id == "harmonium":
            # Harmonium reed: rapid attack, sustained sound, dual-reed harmonics
            self.attack_time = 0.03
            self.decay_time = 0.05
            self.sustain_level = 0.95
            self.release_time = 0.12
            self.harmonics = [(1.0, 0.5), (2.0, 0.35), (3.0, 0.15), (4.0, 0.05)]
        elif instrument_id == "sitar":
            # Sitar: fast plucked attack, metallic buzzing jawari resonance, slow decay
            self.attack_time = 0.008
            self.decay_time = 1.6
            self.sustain_level = 0.10
            self.release_time = 0.3
            self.harmonics = [
                (1.0, 0.45),
                (2.0, 0.25),
                (3.0, 0.18),
                (4.0, 0.12),
                (5.0, 0.08),
                (6.0, 0.05),
            ]
        elif instrument_id == "grand_piano":
            # Acoustic Piano: percussive attack, natural exponential decay
            self.attack_time = 0.005
            self.decay_time = 1.8
            self.sustain_level = 0.15
            self.release_time = 0.25
            self.harmonics = [(1.0, 0.6), (2.0, 0.25), (3.0, 0.1), (4.0, 0.05)]
        elif instrument_id == "electric_piano":
            # FM / Bell tine
            self.attack_time = 0.01
            self.decay_time = 0.8
            self.sustain_level = 0.3
            self.release_time = 0.2
            self.harmonics = [(1.0, 0.5), (2.0, 0.1), (7.0, 0.2), (14.0, 0.1)]
        elif instrument_id == "organ":
            # Drawbar organ: instant attack, full sustain
            self.attack_time = 0.01
            self.decay_time = 0.01
            self.sustain_level = 1.0
            self.release_time = 0.05
            self.harmonics = [(0.5, 0.3), (1.0, 0.4), (2.0, 0.2), (4.0, 0.1)]
        else:
            # Default analog synth
            self.attack_time = 0.02
            self.decay_time = 0.1
            self.sustain_level = 0.7
            self.release_time = 0.15
            self.harmonics = [(1.0, 0.7), (2.0, 0.2), (3.0, 0.1)]

        self.samples_elapsed = 0

    def trigger_release(self) -> None:
        self.is_releasing = True

    def render(self, num_frames: int) -> np.ndarray:
        """Renders float32 audio samples for this voice."""
        if self.is_dead:
            return np.zeros(num_frames, dtype=np.float32)

        # Time vector for phase
        t = np.arange(num_frames, dtype=np.float64)
        phases = self.phase + t * self.phase_step
        self.phase = (phases[-1] + self.phase_step) % (2.0 * math.pi)

        # Generate harmonics
        signal = np.zeros(num_frames, dtype=np.float64)
        for mult, weight in self.harmonics:
            signal += weight * np.sin(phases * mult)

        # Compute envelope progression
        envelope = np.zeros(num_frames, dtype=np.float32)
        attack_frames = int(self.attack_time * self.sample_rate)
        decay_frames = int(self.decay_time * self.sample_rate)
        release_frames = max(1, int(self.release_time * self.sample_rate))

        for i in range(num_frames):
            if not self.is_releasing:
                if self.samples_elapsed < attack_frames:
                    # Attack phase
                    self.env_level = float(self.samples_elapsed) / max(1, attack_frames)
                elif self.samples_elapsed < (attack_frames + decay_frames):
                    # Decay phase
                    decay_progress = float(self.samples_elapsed - attack_frames) / max(
                        1, decay_frames
                    )
                    self.env_level = 1.0 - (1.0 - self.sustain_level) * decay_progress
                else:
                    # Sustain phase
                    self.env_level = self.sustain_level
                self.samples_elapsed += 1
            else:
                # Release phase: decay from current env_level
                self.env_level -= 1.0 / release_frames
                if self.env_level <= 0.0:
                    self.env_level = 0.0
                    self.is_dead = True

            envelope[i] = self.env_level

        output = (signal * envelope * self.velocity).astype(np.float32)
        return output


class AudioEngine:
    """Core real-time audio synthesis and output engine."""

    def __init__(
        self,
        sample_rate: int = 44100,
        buffer_size: int = 512,
        channels: int = 2,
        polyphony: int = 64,
        master_volume: float = 0.85,
    ) -> None:
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.channels = channels
        self.polyphony = polyphony
        self.master_volume = master_volume

        self.active_voices: Dict[int, Voice] = {}
        self.sustained_voices: List[Voice] = []
        self.sustain_pedal: bool = False
        self.current_instrument_id: str = "harmonium"
        self._is_running = False

        # Integrated auxiliary engines: Tanpura Drone, Tabla Synthesizer, Metronome, Tuning, Drums, Mixer
        self.tanpura = TanpuraDroneEngine(sample_rate=self.sample_rate)
        self.tabla = TablaSynthesizer(sample_rate=self.sample_rate)
        self.metronome = MetronomeEngine(sample_rate=self.sample_rate)
        self.tuning = TuningEngine()
        self.drum_engine = DrumMachineEngine(sample_rate=self.sample_rate)
        self.drum_sequencer = DrumSequencer(
            drum_engine=self.drum_engine, bpm=120.0, sample_rate=self.sample_rate
        )
        self.mixer = MixerEngine(sample_rate=self.sample_rate)
        self.recorder: Any = None

    def start(self) -> None:
        self._is_running = True

    def stop(self) -> None:
        self.panic()
        self.tanpura.stop()
        self.metronome.stop()
        self.drum_sequencer.stop()
        self._is_running = False

    def is_running(self) -> bool:
        return self._is_running

    def set_instrument(self, instrument_id: str) -> None:
        self.current_instrument_id = instrument_id

    def note_on(self, midi_note: int, velocity: int = 100) -> None:
        """Trigger note_on for given MIDI note (0-127)."""
        # If currently playing Tabla, route note keys to tabla bols
        if self.current_instrument_id == "tabla":
            bol_mapping = {
                60: "dha",
                62: "dhin",
                64: "ge",
                65: "ke",
                67: "na",
                69: "tin",
                71: "ti",
                72: "ra",
                74: "tu",
            }
            bol_name = bol_mapping.get(midi_note, "dha")
            self.tabla.trigger_bol(bol_name, velocity=velocity / 127.0)
            return
        # If already playing, release existing voice cleanly into releasing queue
        if midi_note in self.active_voices:
            old_voice = self.active_voices.pop(midi_note)
            old_voice.trigger_release()
            self.sustained_voices.append(old_voice)

        # Enforce polyphony limit
        if len(self.active_voices) >= self.polyphony:
            oldest_note = next(iter(self.active_voices))
            oldest_voice = self.active_voices.pop(oldest_note)
            oldest_voice.trigger_release()
            self.sustained_voices.append(oldest_voice)

        tuned_freq = self.tuning.get_frequency(midi_note)
        voice = Voice(
            midi_note=midi_note,
            velocity=velocity,
            sample_rate=self.sample_rate,
            instrument_id=self.current_instrument_id,
            freq=tuned_freq,
        )
        self.active_voices[midi_note] = voice

    def note_off(self, midi_note: int) -> None:
        """Trigger note_off for given MIDI note."""
        if midi_note in self.active_voices:
            voice = self.active_voices.pop(midi_note)
            if self.sustain_pedal:
                self.sustained_voices.append(voice)
            else:
                voice.trigger_release()
                self.sustained_voices.append(voice)

    def set_sustain(self, active: bool) -> None:
        self.sustain_pedal = active
        if not active:
            # Release all sustained voices
            for voice in self.sustained_voices:
                voice.trigger_release()

    def panic(self) -> None:
        """Stop all notes immediately."""
        self.active_voices.clear()
        self.sustained_voices.clear()
        self.tanpura.stop()
        self.metronome.stop()
        self.drum_sequencer.stop()
        self.drum_engine.stop_all()

    def render_block(self, num_frames: int) -> np.ndarray:
        """Renders an audio frame block of stereo float32 samples [-1.0, 1.0] through the mixer."""
        synth_out = np.zeros(num_frames, dtype=np.float32)

        # Render active notes
        dead_notes = []
        for note, voice in self.active_voices.items():
            synth_out += voice.render(num_frames)
            if voice.is_dead:
                dead_notes.append(note)
        for note in dead_notes:
            del self.active_voices[note]

        # Render sustained / releasing notes
        surviving_sustained = []
        for voice in self.sustained_voices:
            synth_out += voice.render(num_frames)
            if not voice.is_dead:
                surviving_sustained.append(voice)
        self.sustained_voices = surviving_sustained

        # Render individual sound generator tracks
        tanpura_out = self.tanpura.render_block(num_frames)
        tabla_out = self.tabla.render_block(num_frames)
        metronome_out = self.metronome.process_frames(num_frames)
        drums_out = self.drum_sequencer.process_frames(num_frames)

        # Route through mixer engine
        track_buffers = {
            "synth": synth_out,
            "drums": drums_out,
            "tanpura": tanpura_out,
            "tabla": tabla_out,
            "metronome": metronome_out,
        }

        master_stereo = self.mixer.mix_tracks(track_buffers, num_frames)

        # Master volume and engine volume scale
        master_stereo *= self.master_volume

        # Limiting protection
        np.clip(master_stereo, -0.98, 0.98, out=master_stereo)

        if hasattr(self, "recorder") and self.recorder is not None:
            self.recorder.record_audio_block(master_stereo)

        if self.channels == 2:
            return master_stereo
        return master_stereo[:, 0:1]
