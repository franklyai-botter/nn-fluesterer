"""Mikrofon-Aufnahme: sammelt Audio solange is_recording True ist."""
import threading
import numpy as np
import sounddevice as sd


class Recorder:
    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        self._frames: list[np.ndarray] = []
        self._stream: sd.InputStream | None = None
        self._lock = threading.Lock()

    def start(self):
        self._frames = []
        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype="float32",
            callback=self._callback,
        )
        self._stream.start()

    def stop(self) -> np.ndarray:
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None
        with self._lock:
            if not self._frames:
                return np.array([], dtype="float32")
            return np.concatenate(self._frames, axis=0).flatten()

    def get_latest_level(self) -> float:
        """RMS-Pegel des zuletzt aufgenommenen Chunks (0.0–1.0)."""
        with self._lock:
            if not self._frames:
                return 0.0
            chunk = self._frames[-1].flatten()
        rms = float(np.sqrt(np.mean(chunk ** 2)))
        return min(1.0, rms * 8)  # skaliert für sichtbare Ausschläge

    def _callback(self, indata: np.ndarray, frames, time, status):
        with self._lock:
            self._frames.append(indata.copy())
