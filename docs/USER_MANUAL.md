# Music Master User Manual

## Overview
**Music Master** transforms your PC/laptop keyboard into a musical instrument studio.
It features low-latency acoustic physical modeling synthesis, Indian classical raga & tala systems, a 16-step drum machine, a multi-track studio mixer, a MIDI device interface, a recording timeline, and an interactive Piano Roll editor.

---

## 1. Quick Start & Navigation

Launch Music Master from the terminal or packaged executable:
```bash
python main.py
```

### Studio Pages:
1. **Dashboard**: Studio system status, active voice counters, audio device manager, and quick presets.
2. **Harmonium**: Melodic dual-reed organ with Indian sargam keyboard mapping (A=Sa, S=Re, D=Ga...).
3. **Piano**: 88-key grand and electric piano interface with octave switching and sustain pedal.
4. **Indian Studio**: Authentic Tabla bol synthesizers (Dha, Dhin, Ge, Ke, Na...) and Tanpura continuous acoustic drone.
5. **Instrument Library**: Complete planned and available instrument catalogue with live state tracking.
6. **Drum Machine**: 16-step velocity-sensitive drum sequencer with 8 drum voices (Kick, Snare, Hi-Hats, Toms, Clap, Cowbell).
7. **Music Theory**: Western scales, chord generator with inversions, circle of fifths, 8 classical Ragas, Indian Talas, and Metronome.
8. **Mixer**: 5-channel console (Master, Synth, Drums, Tanpura, Tabla, Metronome) with 3-band parametric EQ, Stereo Delay, Reverb, and Limiter.
9. **Recorder & Piano Roll**: Real-time MIDI & audio recording, timeline playback, quantizer, visual piano roll grid, project save/load (`.mmp` / `.mmpz`), and WAV/MP3 export.
10. **MIDI Studio**: Plug-and-play USB MIDI keyboard discovery and bidirectional message routing.
11. **Sensor Studio**: Motion tilt and key typing velocity approximation for expressive pitch bend, modulation, and filter cutoff.

---

## 2. Keyboard Controller Shortcuts
- **Keys A - K / Number Row**: Melodic note triggers according to active mapping.
- **Spacebar**: Sustain pedal hold.
- **Esc**: Panic / Stop all active notes immediately.
- **Up / Down Arrows**: Octave shift.
- **Left / Right Arrows**: Transpose semitones.

---

## 3. Recording and Export
- Click **● REC** to record performances live.
- Use **Count-in** to enable a 1-bar pre-roll metronome click.
- Double-click or drag on the **Piano Roll** grid to add, delete (right-click), move, or resize notes.
- Click **Export WAV** or **Export MP3** to render high-fidelity audio tracks.
