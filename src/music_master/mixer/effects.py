"""Audio Effects: Reverb, Delay, 3-Band Equalizer, Limiter."""

import math

import numpy as np
import scipy.signal


class AudioEffect:
    """Base class for real-time stereo audio effects."""

    def __init__(self, sample_rate: int = 44100) -> None:
        self.sample_rate = sample_rate
        self.enabled: bool = True

    def process(self, input_signal: np.ndarray) -> np.ndarray:
        """Processes input buffer (shape (N, 2) or (N,)). Returns processed buffer."""
        if not self.enabled:
            return input_signal
        return self._apply(input_signal)

    def _apply(self, input_signal: np.ndarray) -> np.ndarray:
        return input_signal

    def reset(self) -> None:
        """Reset internal delay lines / filter memories."""
        pass


class DelayEffect(AudioEffect):
    """Stereo ping-pong / feedback delay effect."""

    def __init__(
        self,
        sample_rate: int = 44100,
        delay_time: float = 0.25,
        feedback: float = 0.35,
        mix: float = 0.3,
    ) -> None:
        super().__init__(sample_rate)
        self.delay_time = max(0.01, min(2.0, delay_time))
        self.feedback = max(0.0, min(0.95, feedback))
        self.mix = max(0.0, min(1.0, mix))

        # Max 2 seconds delay buffer
        max_samples = int(self.sample_rate * 2.0)
        self.buffer = np.zeros((max_samples, 2), dtype=np.float32)
        self.write_pos = 0

    def reset(self) -> None:
        self.buffer.fill(0.0)
        self.write_pos = 0

    def set_parameters(
        self,
        delay_time: float | None = None,
        feedback: float | None = None,
        mix: float | None = None,
    ) -> None:
        if delay_time is not None:
            self.delay_time = max(0.01, min(2.0, delay_time))
        if feedback is not None:
            self.feedback = max(0.0, min(0.95, feedback))
        if mix is not None:
            self.mix = max(0.0, min(1.0, mix))

    def _apply(self, input_signal: np.ndarray) -> np.ndarray:
        num_frames = len(input_signal)
        if num_frames == 0:
            return input_signal

        # Normalize to stereo
        if input_signal.ndim == 1:
            dry = np.column_stack((input_signal, input_signal))
        else:
            dry = input_signal

        delay_samples = int(self.delay_time * self.sample_rate)
        buf_len = len(self.buffer)

        # Fast vectorized path when buffer block size is <= delay_samples
        if num_frames <= delay_samples:
            read_indices = (
                np.arange(
                    self.write_pos - delay_samples, self.write_pos - delay_samples + num_frames
                )
            ) % buf_len
            delayed = self.buffer[read_indices]
            # Ping-pong cross channels
            wet = np.column_stack((delayed[:, 1], delayed[:, 0]))

            write_indices = (np.arange(self.write_pos, self.write_pos + num_frames)) % buf_len
            self.buffer[write_indices] = dry + delayed * self.feedback
            self.write_pos = (self.write_pos + num_frames) % buf_len
        else:
            # Fallback for very small delay times
            wet = np.zeros_like(dry)
            for i in range(num_frames):
                read_pos = (self.write_pos - delay_samples) % buf_len
                del_sample = self.buffer[read_pos]

                wet[i, 0] = del_sample[1]
                wet[i, 1] = del_sample[0]

                self.buffer[self.write_pos] = dry[i] + del_sample * self.feedback
                self.write_pos = (self.write_pos + 1) % buf_len

        return (dry * (1.0 - self.mix) + wet * self.mix).astype(np.float32)


class ReverbEffect(AudioEffect):
    """Freeverb-style algorithmic reverb using 4 comb filters and 2 all-pass filters."""

    def __init__(
        self,
        sample_rate: int = 44100,
        room_size: float = 0.6,
        damping: float = 0.2,
        mix: float = 0.25,
    ) -> None:
        super().__init__(sample_rate)
        self.room_size = max(0.0, min(0.98, room_size))
        self.damping = max(0.0, min(1.0, damping))
        self.mix = max(0.0, min(1.0, mix))

        # Scaled delay line lengths in samples
        scale = sample_rate / 44100.0
        self.comb_lens = [
            int(1116 * scale),
            int(1188 * scale),
            int(1277 * scale),
            int(1356 * scale),
        ]
        self.comb_buffers = [np.zeros(length, dtype=np.float32) for length in self.comb_lens]
        self.comb_indices = [0] * 4
        self.comb_filters = [0.0] * 4

        self.allpass_lens = [int(556 * scale), int(441 * scale)]
        self.allpass_buffers = [np.zeros(length, dtype=np.float32) for length in self.allpass_lens]
        self.allpass_indices = [0] * 2

    def reset(self) -> None:
        for b in self.comb_buffers:
            b.fill(0.0)
        self.comb_indices = [0] * len(self.comb_indices)
        self.comb_filters = [0.0] * len(self.comb_filters)
        for b in self.allpass_buffers:
            b.fill(0.0)
        self.allpass_indices = [0] * len(self.allpass_indices)

    def set_parameters(
        self, room_size: float | None = None, damping: float | None = None, mix: float | None = None
    ) -> None:
        if room_size is not None:
            self.room_size = max(0.0, min(0.98, room_size))
        if damping is not None:
            self.damping = max(0.0, min(1.0, damping))
        if mix is not None:
            self.mix = max(0.0, min(1.0, mix))

    def _apply(self, input_signal: np.ndarray) -> np.ndarray:
        num_frames = len(input_signal)
        if num_frames == 0 or self.mix <= 0.001:
            return input_signal

        if input_signal.ndim == 1:
            dry = np.column_stack((input_signal, input_signal))
        else:
            dry = input_signal

        mono_in = 0.5 * (dry[:, 0] + dry[:, 1])
        wet_out = np.zeros(num_frames, dtype=np.float32)

        # Process parallel comb filters
        feedback = 0.7 + 0.28 * self.room_size
        damp = self.damping
        one_minus_damp = 1.0 - damp

        for c in range(4):
            buf = self.comb_buffers[c]
            blen = self.comb_lens[c]
            idx = self.comb_indices[c]
            filter_store = self.comb_filters[c]

            for i in range(num_frames):
                out_val = buf[idx]
                filter_store = out_val * one_minus_damp + filter_store * damp
                buf[idx] = mono_in[i] + filter_store * feedback
                wet_out[i] += out_val
                idx += 1
                if idx >= blen:
                    idx = 0

            self.comb_indices[c] = idx
            self.comb_filters[c] = filter_store

        wet_out *= 0.25

        # Series all-pass filters
        for a in range(2):
            buf = self.allpass_buffers[a]
            blen = self.allpass_lens[a]
            idx = self.allpass_indices[a]

            for i in range(num_frames):
                buf_val = buf[idx]
                in_val = wet_out[i]
                wet_out[i] = -in_val + buf_val
                buf[idx] = in_val + buf_val * 0.5
                idx += 1
                if idx >= blen:
                    idx = 0

            self.allpass_indices[a] = idx

        # Slight decorrelation for stereo width
        wet_stereo = np.column_stack((wet_out, np.roll(wet_out, 12)))
        return (dry * (1.0 - self.mix) + wet_stereo * self.mix).astype(np.float32)


class Equalizer3Band(AudioEffect):
    """3-Band Biquad Equalizer: Low shelf, Peaking mid, High shelf using fast SciPy filtering."""

    def __init__(
        self,
        sample_rate: int = 44100,
        low_gain_db: float = 0.0,
        mid_gain_db: float = 0.0,
        high_gain_db: float = 0.0,
    ) -> None:
        super().__init__(sample_rate)
        self.low_gain_db = low_gain_db
        self.mid_gain_db = mid_gain_db
        self.high_gain_db = high_gain_db

        # Low band (Low shelf / peak @ 250 Hz)
        self.low_cutoff = 250.0
        # Mid band (Peaking filter @ 1200 Hz, Q=1.0)
        self.mid_freq = 1200.0
        self.mid_q = 1.0
        # High band (High shelf / peak @ 4000 Hz)
        self.high_cutoff = 4000.0

        # Direct Form II Transposed filter states for stereo: shape (2, 2)
        self.state_low = np.zeros((2, 2), dtype=np.float64)
        self.state_mid = np.zeros((2, 2), dtype=np.float64)
        self.state_high = np.zeros((2, 2), dtype=np.float64)

    def reset(self) -> None:
        self.state_low.fill(0.0)
        self.state_mid.fill(0.0)
        self.state_high.fill(0.0)

    def set_gains(
        self,
        low_db: float | None = None,
        mid_db: float | None = None,
        high_db: float | None = None,
    ) -> None:
        if low_db is not None:
            self.low_gain_db = max(-24.0, min(18.0, low_db))
        if mid_db is not None:
            self.mid_gain_db = max(-24.0, min(18.0, mid_db))
        if high_db is not None:
            self.high_gain_db = max(-24.0, min(18.0, high_db))

    def _calc_peaking_coeffs(
        self, f0: float, gain_db: float, q: float
    ) -> tuple[np.ndarray, np.ndarray]:
        A = 10.0 ** (gain_db / 40.0)
        w0 = 2.0 * math.pi * f0 / self.sample_rate
        alpha = math.sin(w0) / (2.0 * q)
        cos_w0 = math.cos(w0)

        b0 = 1.0 + alpha * A
        b1 = -2.0 * cos_w0
        b2 = 1.0 - alpha * A
        a0 = 1.0 + alpha / A
        a1 = -2.0 * cos_w0
        a2 = 1.0 - alpha / A

        b = np.array([b0 / a0, b1 / a0, b2 / a0], dtype=np.float64)
        a = np.array([1.0, a1 / a0, a2 / a0], dtype=np.float64)
        return b, a

    def _apply(self, input_signal: np.ndarray) -> np.ndarray:
        if (
            abs(self.low_gain_db) < 0.05
            and abs(self.mid_gain_db) < 0.05
            and abs(self.high_gain_db) < 0.05
        ):
            return input_signal

        if input_signal.ndim == 1:
            sig = np.column_stack((input_signal, input_signal))
        else:
            sig = input_signal.copy()

        # Apply low shelf / peaking
        if abs(self.low_gain_db) >= 0.05:
            b_low, a_low = self._calc_peaking_coeffs(self.low_cutoff, self.low_gain_db, 0.7)
            sig_out, self.state_low = scipy.signal.lfilter(
                b_low, a_low, sig, axis=0, zi=self.state_low
            )
            sig = sig_out.astype(np.float32)

        # Apply mid peaking
        if abs(self.mid_gain_db) >= 0.05:
            b_mid, a_mid = self._calc_peaking_coeffs(self.mid_freq, self.mid_gain_db, self.mid_q)
            sig_out, self.state_mid = scipy.signal.lfilter(
                b_mid, a_mid, sig, axis=0, zi=self.state_mid
            )
            sig = sig_out.astype(np.float32)

        # Apply high shelf / peaking
        if abs(self.high_gain_db) >= 0.05:
            b_high, a_high = self._calc_peaking_coeffs(self.high_cutoff, self.high_gain_db, 0.7)
            sig_out, self.state_high = scipy.signal.lfilter(
                b_high, a_high, sig, axis=0, zi=self.state_high
            )
            sig = sig_out.astype(np.float32)

        return sig.astype(np.float32)


class PeakLimiter(AudioEffect):
    """Brickwall lookahead / soft saturating peak limiter."""

    def __init__(
        self,
        sample_rate: int = 44100,
        threshold_db: float = -0.5,
        release_ms: float = 50.0,
    ) -> None:
        super().__init__(sample_rate)
        self.threshold = 10.0 ** (threshold_db / 20.0)
        self.release_factor = math.exp(-1.0 / (sample_rate * (release_ms / 1000.0)))
        self.envelope = 0.0

    def reset(self) -> None:
        self.envelope = 0.0

    def _apply(self, input_signal: np.ndarray) -> np.ndarray:
        if input_signal.ndim == 1:
            sig = np.column_stack((input_signal, input_signal))
        else:
            sig = input_signal.copy()

        num_frames = len(sig)
        peaks = np.maximum(np.abs(sig[:, 0]), np.abs(sig[:, 1]))
        gains = np.ones(num_frames, dtype=np.float32)
        env = self.envelope

        for i in range(num_frames):
            peak = peaks[i]
            if peak > env:
                env = peak
            else:
                env = peak + (env - peak) * self.release_factor
            if env > self.threshold:
                gains[i] = self.threshold / (env + 1e-9)

        self.envelope = env
        out = np.tanh(sig * gains[:, np.newaxis])
        return out.astype(np.float32)
