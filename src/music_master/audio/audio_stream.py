import logging
from typing import Optional

logger = logging.getLogger(__name__)


class AudioStream:
    """Manages sounddevice OutputStream for hardware playback."""

    def __init__(self, audio_engine) -> None:
        self.engine = audio_engine
        self.stream = None
        self._is_active = False

    def start(self, device_id: Optional[int] = None) -> bool:
        """Starts the real-time audio output stream."""
        try:
            import sounddevice as sd

            def audio_callback(outdata, frames, time_info, status):
                if status:
                    logger.warning("Audio stream status: %s", status)
                try:
                    block = self.engine.render_block(frames)
                    outdata[:] = block
                except Exception as e:
                    logger.exception("Error rendering audio block: %s", e)
                    outdata.fill(0)

            stream = sd.OutputStream(
                samplerate=self.engine.sample_rate,
                blocksize=self.engine.buffer_size,
                channels=self.engine.channels,
                dtype="float32",
                device=device_id,
                callback=audio_callback,
            )
            stream.start()
            self.stream = stream
            self.engine.start()
            self._is_active = True
            logger.info(
                "Audio stream started successfully (Sample Rate: %d, Buffer: %d)",
                self.engine.sample_rate,
                self.engine.buffer_size,
            )
            return True
        except Exception as e:
            logger.error("Failed to start sounddevice audio stream: %s", e)
            self._is_active = False
            return False

    def stop(self) -> None:
        """Stops the audio output stream."""
        if self.stream is not None:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception as e:
                logger.error("Error closing audio stream: %s", e)
            self.stream = None
        self.engine.stop()
        self._is_active = False
        logger.info("Audio stream stopped.")

    def is_active(self) -> bool:
        return self._is_active
