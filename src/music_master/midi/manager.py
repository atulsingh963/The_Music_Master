"""MIDI Device discovery and input/output message handling."""

import logging
import platform
from dataclasses import dataclass
from typing import Any, Callable, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class MidiDeviceInfo:
    id: int
    name: str
    is_input: bool
    is_output: bool


class MidiManager:
    """Manages MIDI hardware device discovery, input callbacks, and output routing."""

    def __init__(self) -> None:
        self.input_devices: List[MidiDeviceInfo] = []
        self.output_devices: List[MidiDeviceInfo] = []
        self.current_input_device_id: Optional[int] = None
        self.current_output_device_id: Optional[int] = None

        self._note_on_callbacks: List[
            Callable[[int, int, int], None]
        ] = []  # note, velocity, channel
        self._note_off_callbacks: List[Callable[[int, int], None]] = []  # note, channel
        self._control_change_callbacks: List[
            Callable[[int, int, int], None]
        ] = []  # cc, val, channel

        self._winmm: Any = None
        self._h_midi_in: Any = None
        self._h_midi_out: Any = None
        self._winmm_cb: Any = None

        self._init_backend()
        self.refresh_devices()

    def _init_backend(self) -> None:
        if platform.system() == "Windows":
            try:
                import ctypes

                self._winmm = ctypes.windll.winmm
            except Exception as e:
                logger.warning(f"Could not load winmm MIDI backend: {e}")

    def refresh_devices(self) -> None:
        """Scan system for available MIDI input and output devices."""
        self.input_devices.clear()
        self.output_devices.clear()

        if self._winmm:
            import ctypes
            from ctypes import wintypes

            class MIDIINCAPSW(ctypes.Structure):
                _fields_ = [
                    ("wMid", wintypes.WORD),
                    ("wPid", wintypes.WORD),
                    ("vDriverVersion", wintypes.DWORD),
                    ("szPname", wintypes.WCHAR * 32),
                    ("dwSupport", wintypes.DWORD),
                ]

            class MIDIOUTCAPSW(ctypes.Structure):
                _fields_ = [
                    ("wMid", wintypes.WORD),
                    ("wPid", wintypes.WORD),
                    ("vDriverVersion", wintypes.DWORD),
                    ("szPname", wintypes.WCHAR * 32),
                    ("wTechnology", wintypes.WORD),
                    ("wVoices", wintypes.WORD),
                    ("wNotes", wintypes.WORD),
                    ("wChannelMask", wintypes.WORD),
                    ("dwSupport", wintypes.DWORD),
                ]

            num_in = self._winmm.midiInGetNumDevs()
            for i in range(num_in):
                in_caps = MIDIINCAPSW()
                if (
                    self._winmm.midiInGetDevCapsW(i, ctypes.byref(in_caps), ctypes.sizeof(in_caps))
                    == 0
                ):
                    self.input_devices.append(
                        MidiDeviceInfo(
                            id=i, name=str(in_caps.szPname), is_input=True, is_output=False
                        )
                    )

            num_out = self._winmm.midiOutGetNumDevs()
            for i in range(num_out):
                out_caps = MIDIOUTCAPSW()
                if (
                    self._winmm.midiOutGetDevCapsW(
                        i, ctypes.byref(out_caps), ctypes.sizeof(out_caps)
                    )
                    == 0
                ):
                    self.output_devices.append(
                        MidiDeviceInfo(
                            id=i, name=str(out_caps.szPname), is_input=False, is_output=True
                        )
                    )

        logger.info(
            f"MIDI Devices discovered: {len(self.input_devices)} inputs, {len(self.output_devices)} outputs"
        )

    def register_note_on_callback(self, cb: Callable[[int, int, int], None]) -> None:
        self._note_on_callbacks.append(cb)

    def register_note_off_callback(self, cb: Callable[[int, int], None]) -> None:
        self._note_off_callbacks.append(cb)

    def register_control_change_callback(self, cb: Callable[[int, int, int], None]) -> None:
        self._control_change_callbacks.append(cb)

    def open_input_device(self, device_id: int) -> bool:
        """Opens a MIDI input device and starts listening for MIDI messages."""
        if not self._winmm:
            return False

        self.close_input_device()

        import ctypes
        from ctypes import wintypes

        MIM_DATA = 0x3C3
        CALLBACK_FUNCTION = 0x00030000

        MIDIINPROC = ctypes.WINFUNCTYPE(
            None,
            wintypes.HANDLE,
            wintypes.UINT,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
        )

        def _midi_callback(hMidiIn, wMsg, dwInstance, dwParam1, dwParam2):  # type: ignore
            if wMsg == MIM_DATA:
                msg = dwParam1 & 0xFFFFFF
                status = msg & 0xFF
                data1 = (msg >> 8) & 0xFF
                data2 = (msg >> 16) & 0xFF

                cmd = status & 0xF0
                channel = status & 0x0F

                if cmd == 0x90:  # Note On
                    if data2 > 0:
                        for on_cb in self._note_on_callbacks:
                            on_cb(data1, data2, channel)
                    else:
                        for off_cb in self._note_off_callbacks:
                            off_cb(data1, channel)
                elif cmd == 0x80:  # Note Off
                    for off_cb in self._note_off_callbacks:
                        off_cb(data1, channel)
                elif cmd == 0xB0:  # Control Change
                    for cc_cb in self._control_change_callbacks:
                        cc_cb(data1, data2, channel)

        self._winmm_cb = MIDIINPROC(_midi_callback)
        h_in = wintypes.HANDLE()

        res = self._winmm.midiInOpen(
            ctypes.byref(h_in),
            device_id,
            self._winmm_cb,
            0,
            CALLBACK_FUNCTION,
        )
        if res == 0:
            self._h_midi_in = h_in
            self._winmm.midiInStart(self._h_midi_in)
            self.current_input_device_id = device_id
            return True

        return False

    def close_input_device(self) -> None:
        if self._winmm and self._h_midi_in:
            self._winmm.midiInStop(self._h_midi_in)
            self._winmm.midiInReset(self._h_midi_in)
            self._winmm.midiInClose(self._h_midi_in)
            self._h_midi_in = None
            self.current_input_device_id = None

    def open_output_device(self, device_id: int) -> bool:
        if not self._winmm:
            return False

        self.close_output_device()

        import ctypes
        from ctypes import wintypes

        h_out = wintypes.HANDLE()
        res = self._winmm.midiOutOpen(ctypes.byref(h_out), device_id, 0, 0, 0)
        if res == 0:
            self._h_midi_out = h_out
            self.current_output_device_id = device_id
            return True
        return False

    def close_output_device(self) -> None:
        if self._winmm and self._h_midi_out:
            self._winmm.midiOutReset(self._h_midi_out)
            self._winmm.midiOutClose(self._h_midi_out)
            self._h_midi_out = None
            self.current_output_device_id = None

    def send_short_message(self, status: int, data1: int, data2: int) -> None:
        if self._winmm and self._h_midi_out:
            msg = (status & 0xFF) | ((data1 & 0xFF) << 8) | ((data2 & 0xFF) << 16)
            self._winmm.midiOutShortMsg(self._h_midi_out, msg)

    def send_note_on(self, note: int, velocity: int = 100, channel: int = 0) -> None:
        status = 0x90 | (channel & 0x0F)
        self.send_short_message(status, note & 0x7F, velocity & 0x7F)

    def send_note_off(self, note: int, velocity: int = 0, channel: int = 0) -> None:
        status = 0x80 | (channel & 0x0F)
        self.send_short_message(status, note & 0x7F, velocity & 0x7F)
