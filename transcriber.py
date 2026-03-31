"""Transkription via faster-whisper (lokal, offline)."""
import numpy as np
from faster_whisper import WhisperModel


class Transcriber:
    def __init__(self, model_size: str = "base", language: str | None = "de"):
        self.language = language or None
        print(f"[Transcriber] Lade Modell '{model_size}' ...")
        self.model = WhisperModel(model_size, device="cpu", compute_type="int8")
        print("[Transcriber] Modell geladen.")

    def transcribe(self, audio: np.ndarray, sample_rate: int = 16000) -> str:
        if audio.size == 0:
            return ""
        segments, _ = self.model.transcribe(
            audio,
            language=self.language,
            beam_size=5,
            vad_filter=True,
        )
        text = " ".join(seg.text.strip() for seg in segments)
        return text.strip()
