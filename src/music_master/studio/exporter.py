"""Audio export engine supporting lossless WAV and standard MP3 via FFmpeg."""

import logging
import os
import shutil
import subprocess
import tempfile
import wave

import numpy as np

logger = logging.getLogger(__name__)


class AudioExporter:
    """Exports float32 audio buffers or rendered project stems to WAV and MP3."""

    @staticmethod
    def export_wav(
        filepath: str,
        audio_data: np.ndarray,
        sample_rate: int = 44100,
        bit_depth: int = 16,
    ) -> None:
        """Exports stereo or mono float32 numpy array to standard uncompressed WAV file."""
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)

        if audio_data.ndim == 1:
            channels = 1
            audio_data = audio_data.reshape(-1, 1)
        else:
            channels = audio_data.shape[1]

        # Normalize and convert float32 [-1.0, 1.0] to int16
        clipped = np.clip(audio_data, -1.0, 1.0)
        int16_data = (clipped * 32767.0).astype(np.int16)

        with wave.open(filepath, "wb") as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(sample_rate)
            wf.writeframes(int16_data.tobytes())

        logger.info(f"Exported WAV file: {filepath} ({len(int16_data)} frames)")

    @staticmethod
    def export_mp3(
        filepath: str,
        audio_data: np.ndarray,
        sample_rate: int = 44100,
        bitrate: str = "320k",
    ) -> None:
        """Exports audio buffer to MP3 using ffmpeg encoder if available, with graceful WAV fallback."""
        ffmpeg_bin = shutil.which("ffmpeg")
        if not ffmpeg_bin:
            fallback_wav = os.path.splitext(filepath)[0] + ".wav"
            logger.warning(
                f"FFmpeg not found in PATH! Falling back to uncompressed WAV: {fallback_wav}"
            )
            AudioExporter.export_wav(fallback_wav, audio_data, sample_rate)
            return

        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)

        # Write intermediate WAV to temp file, then encode
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wav:
            tmp_wav_path = tmp_wav.name

        try:
            AudioExporter.export_wav(tmp_wav_path, audio_data, sample_rate)
            cmd = [
                ffmpeg_bin,
                "-y",  # overwrite
                "-i",
                tmp_wav_path,
                "-b:a",
                bitrate,
                filepath,
            ]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode != 0:
                raise RuntimeError(
                    f"FFmpeg failed with exit code {result.returncode}: {result.stderr}"
                )
            logger.info(f"Exported MP3 file: {filepath} ({bitrate})")
        finally:
            if os.path.exists(tmp_wav_path):
                os.remove(tmp_wav_path)
