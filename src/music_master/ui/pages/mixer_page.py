"""Studio Mixer UI page with multi-track strips, master fader, meters, EQ, Reverb, Delay, and Limiter."""

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
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
from music_master.mixer.track import MixerTrack


class TrackStripWidget(QFrame):
    """Channel strip widget for a single mixer track."""

    def __init__(self, track: MixerTrack, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.track = track
        self.setStyleSheet(
            "TrackStripWidget { background-color: #1E293B; border-radius: 8px; border: 1px solid #334155; }"
        )
        self.setFixedWidth(125)
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 12, 8, 12)
        layout.setSpacing(8)

        # Track name
        name_lbl = QLabel(self.track.name)
        name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_lbl.setStyleSheet("font-weight: 700; color: #38BDF8; font-size: 12px;")
        layout.addWidget(name_lbl)

        # Mute / Solo buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(4)
        self.mute_btn = QPushButton("M")
        self.mute_btn.setCheckable(True)
        self.mute_btn.setFixedSize(28, 26)
        self.mute_btn.setStyleSheet(
            "QPushButton { background-color: #334155; color: #CBD5E1; font-weight: 700; border-radius: 3px; }"
            "QPushButton:checked { background-color: #DC2626; color: white; }"
        )
        self.mute_btn.clicked.connect(self._on_mute_toggled)
        btn_layout.addWidget(self.mute_btn)

        self.solo_btn = QPushButton("S")
        self.solo_btn.setCheckable(True)
        self.solo_btn.setFixedSize(28, 26)
        self.solo_btn.setStyleSheet(
            "QPushButton { background-color: #334155; color: #CBD5E1; font-weight: 700; border-radius: 3px; }"
            "QPushButton:checked { background-color: #EAB308; color: black; }"
        )
        self.solo_btn.clicked.connect(self._on_solo_toggled)
        btn_layout.addWidget(self.solo_btn)
        layout.addLayout(btn_layout)

        # Pan slider
        pan_lbl = QLabel("PAN")
        pan_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pan_lbl.setStyleSheet("color: #64748B; font-size: 10px; font-weight: 600;")
        layout.addWidget(pan_lbl)

        self.pan_slider = QSlider(Qt.Orientation.Horizontal)
        self.pan_slider.setRange(-100, 100)
        self.pan_slider.setValue(int(self.track.pan * 100))
        self.pan_slider.valueChanged.connect(self._on_pan_changed)
        layout.addWidget(self.pan_slider)

        # Fader & Meter layout
        fader_layout = QHBoxLayout()
        fader_layout.setSpacing(6)

        # Vertical volume fader
        self.vol_slider = QSlider(Qt.Orientation.Vertical)
        self.vol_slider.setRange(0, 120)
        self.vol_slider.setValue(int(self.track.volume * 100))
        self.vol_slider.setFixedHeight(160)
        self.vol_slider.valueChanged.connect(self._on_vol_changed)
        fader_layout.addWidget(self.vol_slider)

        # Dual peak meter
        meter_box = QHBoxLayout()
        meter_box.setSpacing(2)
        self.meter_l = QProgressBar()
        self.meter_l.setOrientation(Qt.Orientation.Vertical)
        self.meter_l.setRange(0, 100)
        self.meter_l.setTextVisible(False)
        self.meter_l.setFixedWidth(6)
        self.meter_l.setFixedHeight(160)
        self.meter_l.setStyleSheet("QProgressBar::chunk { background-color: #10B981; }")

        self.meter_r = QProgressBar()
        self.meter_r.setOrientation(Qt.Orientation.Vertical)
        self.meter_r.setRange(0, 100)
        self.meter_r.setTextVisible(False)
        self.meter_r.setFixedWidth(6)
        self.meter_r.setFixedHeight(160)
        self.meter_r.setStyleSheet("QProgressBar::chunk { background-color: #10B981; }")

        meter_box.addWidget(self.meter_l)
        meter_box.addWidget(self.meter_r)
        fader_layout.addLayout(meter_box)

        layout.addLayout(fader_layout)

        # Volume dB readout
        self.vol_readout = QLabel(f"{int(self.track.volume * 100)}%")
        self.vol_readout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.vol_readout.setStyleSheet("color: #94A3B8; font-size: 11px;")
        layout.addWidget(self.vol_readout)

    def _on_mute_toggled(self, checked: bool) -> None:
        self.track.mute = checked

    def _on_solo_toggled(self, checked: bool) -> None:
        self.track.solo = checked

    def _on_pan_changed(self, val: int) -> None:
        self.track.pan = val / 100.0

    def _on_vol_changed(self, val: int) -> None:
        self.track.volume = val / 100.0
        self.vol_readout.setText(f"{val}%")

    def update_meter(self) -> None:
        # Scale 0.0 - 1.0 to 0 - 100
        val_l = min(100, int(self.track.meter.peak_l * 100))
        val_r = min(100, int(self.track.meter.peak_r * 100))
        self.meter_l.setValue(val_l)
        self.meter_r.setValue(val_r)


class MixerPage(QWidget):
    """Main Studio Mixer interface page."""

    def __init__(self, audio_engine: AudioEngine, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.audio_engine = audio_engine
        self.mixer = audio_engine.mixer
        self.track_strips: list[TrackStripWidget] = []

        self._init_ui()

        # Meter polling timer
        self.meter_timer = QTimer(self)
        self.meter_timer.timeout.connect(self._refresh_meters)
        self.meter_timer.start(40)

    def _init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(28, 24, 28, 24)
        main_layout.setSpacing(16)

        # Header
        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("STUDIO MIXER & AUDIO EFFECTS")
        title.setStyleSheet("font-size: 20px; font-weight: 700; color: #F8FAFC;")
        subtitle = QLabel(
            "Multi-Track Console, Peak/RMS Metering, 3-Band EQ, Delay, Reverb & Limiter"
        )
        subtitle.setStyleSheet("font-size: 13px; color: #94A3B8;")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header.addLayout(title_box)
        header.addStretch()
        main_layout.addLayout(header)

        # Center Section: Channel Strips + Master Strip + Effects Panel
        content_layout = QHBoxLayout()
        content_layout.setSpacing(16)

        # 1. Channel Strips
        tracks_box = QHBoxLayout()
        tracks_box.setSpacing(10)
        for track in self.mixer.tracks.values():
            strip = TrackStripWidget(track)
            self.track_strips.append(strip)
            tracks_box.addWidget(strip)

        content_layout.addLayout(tracks_box)

        # 2. Master Channel Strip
        master_strip = QFrame()
        master_strip.setStyleSheet(
            "background-color: #0F172A; border-radius: 8px; border: 2px solid #38BDF8;"
        )
        master_strip.setFixedWidth(135)
        master_layout = QVBoxLayout(master_strip)
        master_layout.setContentsMargins(8, 12, 8, 12)
        master_layout.setSpacing(8)

        m_name = QLabel("MASTER BUS")
        m_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        m_name.setStyleSheet("font-weight: 800; color: #38BDF8; font-size: 13px;")
        master_layout.addWidget(m_name)

        # Master Fader & Meters
        mf_layout = QHBoxLayout()
        mf_layout.setSpacing(6)

        self.master_vol_slider = QSlider(Qt.Orientation.Vertical)
        self.master_vol_slider.setRange(0, 120)
        self.master_vol_slider.setValue(int(self.mixer.master_volume * 100))
        self.master_vol_slider.setFixedHeight(190)
        self.master_vol_slider.valueChanged.connect(self._on_master_vol_changed)
        mf_layout.addWidget(self.master_vol_slider)

        meter_box = QHBoxLayout()
        meter_box.setSpacing(2)
        self.master_meter_l = QProgressBar()
        self.master_meter_l.setOrientation(Qt.Orientation.Vertical)
        self.master_meter_l.setRange(0, 100)
        self.master_meter_l.setTextVisible(False)
        self.master_meter_l.setFixedWidth(8)
        self.master_meter_l.setFixedHeight(190)
        self.master_meter_l.setStyleSheet("QProgressBar::chunk { background-color: #38BDF8; }")

        self.master_meter_r = QProgressBar()
        self.master_meter_r.setOrientation(Qt.Orientation.Vertical)
        self.master_meter_r.setRange(0, 100)
        self.master_meter_r.setTextVisible(False)
        self.master_meter_r.setFixedWidth(8)
        self.master_meter_r.setFixedHeight(190)
        self.master_meter_r.setStyleSheet("QProgressBar::chunk { background-color: #38BDF8; }")

        meter_box.addWidget(self.master_meter_l)
        meter_box.addWidget(self.master_meter_r)
        mf_layout.addLayout(meter_box)

        master_layout.addLayout(mf_layout)

        self.master_vol_lbl = QLabel(f"{int(self.mixer.master_volume * 100)}%")
        self.master_vol_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.master_vol_lbl.setStyleSheet("color: #F8FAFC; font-weight: 700; font-size: 12px;")
        master_layout.addWidget(self.master_vol_lbl)

        content_layout.addWidget(master_strip)

        # 3. Master Insert Effects Rack
        fx_panel = QFrame()
        fx_panel.setStyleSheet(
            "background-color: #1E293B; border-radius: 8px; border: 1px solid #334155; padding: 12px;"
        )
        fx_layout = QVBoxLayout(fx_panel)
        fx_layout.setSpacing(12)

        fx_title = QLabel("MASTER BUS INSERT EFFECTS")
        fx_title.setStyleSheet("font-size: 13px; font-weight: 700; color: #38BDF8;")
        fx_layout.addWidget(fx_title)

        # 3-Band EQ Controls
        eq_group = QGroupBox("3-Band Equalizer")
        eq_group.setStyleSheet(
            "QGroupBox { color: #E2E8F0; font-weight: 600; border: 1px solid #334155; border-radius: 6px; margin-top: 10px; padding-top: 10px; }"
        )
        eq_layout = QHBoxLayout(eq_group)

        # Low Gain
        low_box = QVBoxLayout()
        low_lbl = QLabel("Low (250Hz)")
        low_lbl.setStyleSheet("color: #94A3B8; font-size: 10px;")
        self.low_slider = QSlider(Qt.Orientation.Horizontal)
        self.low_slider.setRange(-15, 15)
        self.low_slider.setValue(0)
        self.low_slider.valueChanged.connect(self._on_eq_changed)
        low_box.addWidget(low_lbl)
        low_box.addWidget(self.low_slider)
        eq_layout.addLayout(low_box)

        # Mid Gain
        mid_box = QVBoxLayout()
        mid_lbl = QLabel("Mid (1.2kHz)")
        mid_lbl.setStyleSheet("color: #94A3B8; font-size: 10px;")
        self.mid_slider = QSlider(Qt.Orientation.Horizontal)
        self.mid_slider.setRange(-15, 15)
        self.mid_slider.setValue(0)
        self.mid_slider.valueChanged.connect(self._on_eq_changed)
        mid_box.addWidget(mid_lbl)
        mid_box.addWidget(self.mid_slider)
        eq_layout.addLayout(mid_box)

        # High Gain
        high_box = QVBoxLayout()
        high_lbl = QLabel("High (4kHz)")
        high_lbl.setStyleSheet("color: #94A3B8; font-size: 10px;")
        self.high_slider = QSlider(Qt.Orientation.Horizontal)
        self.high_slider.setRange(-15, 15)
        self.high_slider.setValue(0)
        self.high_slider.valueChanged.connect(self._on_eq_changed)
        high_box.addWidget(high_lbl)
        high_box.addWidget(self.high_slider)
        eq_layout.addLayout(high_box)

        fx_layout.addWidget(eq_group)

        # Reverb Controls
        rev_group = QGroupBox("Reverb Processor")
        rev_group.setStyleSheet(
            "QGroupBox { color: #E2E8F0; font-weight: 600; border: 1px solid #334155; border-radius: 6px; margin-top: 10px; padding-top: 10px; }"
        )
        rev_layout = QHBoxLayout(rev_group)

        self.rev_enable = QCheckBox("Enable")
        self.rev_enable.setChecked(self.mixer.master_reverb.enabled)
        self.rev_enable.toggled.connect(lambda v: setattr(self.mixer.master_reverb, "enabled", v))
        rev_layout.addWidget(self.rev_enable)

        rev_mix_box = QVBoxLayout()
        rev_mix_lbl = QLabel("Mix")
        rev_mix_lbl.setStyleSheet("color: #94A3B8; font-size: 10px;")
        self.rev_mix_slider = QSlider(Qt.Orientation.Horizontal)
        self.rev_mix_slider.setRange(0, 100)
        self.rev_mix_slider.setValue(int(self.mixer.master_reverb.mix * 100))
        self.rev_mix_slider.valueChanged.connect(
            lambda v: self.mixer.master_reverb.set_parameters(mix=v / 100.0)
        )
        rev_mix_box.addWidget(rev_mix_lbl)
        rev_mix_box.addWidget(self.rev_mix_slider)
        rev_layout.addLayout(rev_mix_box)

        rev_room_box = QVBoxLayout()
        rev_room_lbl = QLabel("Room Size")
        rev_room_lbl.setStyleSheet("color: #94A3B8; font-size: 10px;")
        self.rev_room_slider = QSlider(Qt.Orientation.Horizontal)
        self.rev_room_slider.setRange(10, 95)
        self.rev_room_slider.setValue(int(self.mixer.master_reverb.room_size * 100))
        self.rev_room_slider.valueChanged.connect(
            lambda v: self.mixer.master_reverb.set_parameters(room_size=v / 100.0)
        )
        rev_room_box.addWidget(rev_room_lbl)
        rev_room_box.addWidget(self.rev_room_slider)
        rev_layout.addLayout(rev_room_box)

        fx_layout.addWidget(rev_group)

        # Delay Controls
        delay_group = QGroupBox("Delay / Echo")
        delay_group.setStyleSheet(
            "QGroupBox { color: #E2E8F0; font-weight: 600; border: 1px solid #334155; border-radius: 6px; margin-top: 10px; padding-top: 10px; }"
        )
        delay_layout = QHBoxLayout(delay_group)

        self.delay_enable = QCheckBox("Enable")
        self.delay_enable.setChecked(self.mixer.master_delay.enabled)
        self.delay_enable.toggled.connect(lambda v: setattr(self.mixer.master_delay, "enabled", v))
        delay_layout.addWidget(self.delay_enable)

        delay_mix_box = QVBoxLayout()
        delay_mix_lbl = QLabel("Mix")
        delay_mix_lbl.setStyleSheet("color: #94A3B8; font-size: 10px;")
        self.delay_mix_slider = QSlider(Qt.Orientation.Horizontal)
        self.delay_mix_slider.setRange(0, 100)
        self.delay_mix_slider.setValue(int(self.mixer.master_delay.mix * 100))
        self.delay_mix_slider.valueChanged.connect(
            lambda v: self.mixer.master_delay.set_parameters(mix=v / 100.0)
        )
        delay_mix_box.addWidget(delay_mix_lbl)
        delay_mix_box.addWidget(self.delay_mix_slider)
        delay_layout.addLayout(delay_mix_box)

        delay_time_box = QVBoxLayout()
        delay_time_lbl = QLabel("Time (ms)")
        delay_time_lbl.setStyleSheet("color: #94A3B8; font-size: 10px;")
        self.delay_time_slider = QSlider(Qt.Orientation.Horizontal)
        self.delay_time_slider.setRange(50, 1000)
        self.delay_time_slider.setValue(int(self.mixer.master_delay.delay_time * 1000))
        self.delay_time_slider.valueChanged.connect(
            lambda v: self.mixer.master_delay.set_parameters(delay_time=v / 1000.0)
        )
        delay_time_box.addWidget(delay_time_lbl)
        delay_time_box.addWidget(self.delay_time_slider)
        delay_layout.addLayout(delay_time_box)

        fx_layout.addWidget(delay_group)

        fx_layout.addStretch()
        content_layout.addWidget(fx_panel)

        main_layout.addLayout(content_layout)
        main_layout.addStretch()

    def _on_master_vol_changed(self, val: int) -> None:
        vol = val / 100.0
        self.mixer.master_volume = vol
        self.master_vol_lbl.setText(f"{val}%")

    def _on_eq_changed(self) -> None:
        self.mixer.master_eq.set_gains(
            low_db=float(self.low_slider.value()),
            mid_db=float(self.mid_slider.value()),
            high_db=float(self.high_slider.value()),
        )

    def _refresh_meters(self) -> None:
        for strip in self.track_strips:
            strip.update_meter()

        val_l = min(100, int(self.mixer.master_meter.peak_l * 100))
        val_r = min(100, int(self.mixer.master_meter.peak_r * 100))
        self.master_meter_l.setValue(val_l)
        self.master_meter_r.setValue(val_r)
