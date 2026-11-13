# Music Master

**Your Keyboard. Your Instruments. Your Music.**

Music Master is a standalone desktop virtual musical studio engineered in Python and PySide6. It transforms a standard laptop or desktop keyboard into a responsive musical controller while providing authentic Indian classical and Western instrument playback, music theory tools, audio routing, and studio workflows.

---

## 1. Overview & Vision
Music Master is designed from the ground up for low latency, polyphonic instrument performance, and deep Indian and Western music theory exploration.

### Key Highlights
- **Play with Laptop Keyboard:** Full multi-octave and accidental mappings with panic and repeat safeguards.
- **Indian Classical Music:** Built-in Harmonium studio with Sargam (`Sa Re Ga Ma Pa Dha Ni`), Mandra/Madhya/Tara Saptak, and editable Ragas (Yaman, Bhairav, Bhairavi, Kafi, etc.).
- **Western Instruments:** Concert Grand Piano with responsive velocity envelopes, drawbar organs, and synths.
- **Instrument Catalogue & Availability States:** Honest state tracking (`Available`, `Installed`, `Missing Sound Library`, `Experimental`, `Planned`).
- **Real-Time Audio Engine:** Polyphonic synthesis with configurable sample rate, frame buffer, and sounddevice streaming.
- **Extensible Architecture:** Strict separation between audio rendering, event orchestration, database persistence, and UI.

---

## 2. Supported Instruments

| Instrument | Family | Engine / Sound Source | Availability Status |
| :--- | :--- | :--- | :--- |
| **Harmonium** | Indian Classical | Multi-Harmonic Reed Synthesis | **Available** |
| **Grand Piano** | Western Keyboard | Harmonic Envelope Synthesis | **Available** |
| **Electric Piano**| Western Keyboard | FM / Tine Synthesis | **Available** |
| **Organ** | Western Keyboard | Additive Synthesis | **Available** |
| **Analog Synthesizer**| Electronic | Subtractive Filter Synthesis | **Available** |
| **Tabla** | Indian Classical | Dual Drum Model | *Planned* |
| **Sitar** | Indian Classical | Sympathetic String Model | *Planned* |
| **Tanpura** | Indian Classical | Drone Oscillator | *Planned* |
| **Bansuri** | Indian Classical | Flute Resonator | *Planned* |
| **Veena** | Indian Classical | Plucked Model | *Planned* |
| **Acoustic Guitar** | Strings | SoundFont / Physical Model | *Planned* |
| **Violin** | Strings | SoundFont / Physical Model | *Planned* |
| **Drum Kit** | Percussion | Sampled Studio Kit | *Planned* |

---

## 3. Keyboard Controls

### Harmonium Sargam Mode (Base: C4)
- **White Keys (Shuddha Swaras):**
  - `A` = Sa
  - `S` = Re
  - `D` = Ga
  - `F` = Ma
  - `G` = Pa
  - `H` = Dha
  - `J` = Ni
  - `K` = Ṡa (Tara Saptak)
  - `L` = Ṙe (Tara Saptak)
  - `;` = Ġa (Tara Saptak)
- **Black Keys (Vikrit Swaras):**
  - `W` = re (komal)
  - `E` = ga (komal)
  - `T` = ma' (tivra)
  - `Y` = dha (komal)
  - `U` = ni (komal)
  - `O` = ṙe (komal, Tara)
  - `P` = ġa (komal, Tara)

### Piano Chromatic Mode (Base: C4)
- **White Keys:** `A` (C4), `S` (D4), `D` (E4), `F` (F4), `G` (G4), `H` (A4), `J` (B4), `K` (C5), `L` (D5), `;` (E5)
- **Black Keys:** `W` (C#4), `E` (D#4), `T` (F#4), `Y` (G#4), `U` (A#4), `O` (C#5), `P` (D#5)

### Global Shortcuts
- **`Up` / `Down`**: Shift active octave up or down (+/- 3 octaves)
- **`Space`**: Sustain pedal / Drone hold
- **`Esc`**: Panic (Stop all ringing notes immediately)

---

## 4. Installation & Setup

### Prerequisites
- Python 3.10+ (tested on Python 3.13)
- Windows 10/11 (macOS / Linux support in roadmap)

### Quick Start
```bash
# Clone the repository
git clone https://github.com/your-org/Music-Master.git
cd Music-Master

# Install dependencies and package in editable mode
pip install -e ".[dev]"

# Run test suite
pytest -v

# Run quality checks
ruff check .
mypy src/

# Launch Music Master
python main.py
```

---

## 5. Project Architecture

```
Music-Master/
|-- main.py                      # Application bootstrap
|-- pyproject.toml               # Package specifications, ruff & mypy configuration
|-- requirements.txt             # Direct dependencies
|-- README.md                    # Project documentation
|-- LICENSE                      # MIT License
|-- CHANGELOG.md                 # Version history
|
|-- src/music_master/
|   |-- app.py                   # Qt application lifecycle
|   |-- config.py                # Pydantic configuration schemas
|   |-- audio/                   # Low-latency audio synthesis, rendering & device streaming
|   |-- core/                    # Application state and event dispatcher
|   |-- input/                   # Keyboard mapping, key event deduplication & controllers
|   |-- instruments/             # Catalogue registry and instrument definitions
|   |-- theory/                  # Indian sargam/ragas and Western music theory models
|   |-- ui/                      # PySide6 desktop views, themes, and interactive virtual keyboards
|   |-- utils/                   # Path management and structured logging
|
|-- tests/
|   |-- unit/                    # Fast audio, mapping, theory, and registry unit tests
|   |-- ui/                      # PySide6 headless UI and navigation tests
|
|-- soundfonts/                  # Directory for user-installed SF2 soundfonts
```

---

## 6. License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
