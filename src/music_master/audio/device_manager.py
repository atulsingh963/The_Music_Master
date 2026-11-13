import logging
from dataclasses import dataclass
from typing import List

logger = logging.getLogger(__name__)


@dataclass
class AudioDeviceInfo:
    id: int
    name: str
    max_input_channels: int
    max_output_channels: int
    default_samplerate: float
    is_default_output: bool = False


class AudioDeviceManager:
    """Queries and manages host audio devices."""

    @staticmethod
    def get_output_devices() -> List[AudioDeviceInfo]:
        devices: List[AudioDeviceInfo] = []
        try:
            import sounddevice as sd

            dev_list = sd.query_devices()
            default_out = (
                sd.default.device[1] if isinstance(sd.default.device, (list, tuple)) else None
            )

            for idx, dev in enumerate(dev_list):
                if dev["max_output_channels"] > 0:
                    devices.append(
                        AudioDeviceInfo(
                            id=idx,
                            name=dev["name"],
                            max_input_channels=dev["max_input_channels"],
                            max_output_channels=dev["max_output_channels"],
                            default_samplerate=dev["default_samplerate"],
                            is_default_output=(idx == default_out),
                        )
                    )
        except Exception as e:
            logger.warning("Could not query sound devices: %s", e)
        return devices
