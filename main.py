"""
Wispr Clone — Entry Point
Startet das Dashboard und verbindet alle Komponenten.
"""
import threading
import time
import numpy as np

import config as cfg
from recorder import Recorder
from transcriber import Transcriber
from injector import inject
from hotkey import HotkeyListener
from floating_btn import FloatingButton
import ai_cleanup
import dashboard


class WisprClone:
    def __init__(self):
        self.conf = cfg.load()
        self.recorder = Recorder(sample_rate=self.conf["recording"]["sample_rate"])
        self.transcriber = Transcriber(
            model_size=self.conf["whisper_model"],
            language=self.conf.get("language"),
        )
        self._processing = False
        self._wave_thread: threading.Thread | None = None
        self._wave_active = False
        self.float_btn = FloatingButton(
            on_press_cb=self.on_hotkey_press,
            on_release_cb=self.on_hotkey_release,
        )

    def on_hotkey_press(self):
        if self._processing:
            return
        print("[Wispr] Aufnahme gestartet ...")
        dashboard.set_status("recording", "Spreche jetzt ...")
        self.recorder.start()
        self._start_wave_feed()

    def on_hotkey_release(self):
        self._stop_wave_feed()
        dashboard.set_status("processing", "Transkribiere ...")
        print("[Wispr] Aufnahme gestoppt, transkribiere ...")

        audio = self.recorder.stop()
        min_dur = self.conf["recording"]["min_duration"]
        sr = self.conf["recording"]["sample_rate"]

        if audio.size < int(min_dur * sr):
            print("[Wispr] Aufnahme zu kurz, ignoriert.")
            dashboard.set_status("idle", "Halte den Hotkey gedrückt um zu sprechen")
            return

        self._processing = True
        try:
            text = self.transcriber.transcribe(audio, sr)
            print(f"[Wispr] Transkript: {text!r}")

            if self.conf.get("ai_cleanup") and self.conf.get("groq_api_key"):
                text = ai_cleanup.cleanup(
                    text,
                    api_key=self.conf["groq_api_key"],
                    language=self.conf.get("language", "de"),
                )
                print(f"[Wispr] Nach KI-Bereinigung: {text!r}")

            if text:
                inject(text)
                dashboard.add_transcript(text)
        finally:
            self._processing = False
            self.float_btn.set_idle()
            dashboard.set_status("idle", "Halte den Hotkey gedrückt um zu sprechen")

    def _start_wave_feed(self):
        """Sendet Live-Audiopegel ans Dashboard während der Aufnahme."""
        self._wave_active = True

        def feed():
            while self._wave_active:
                audio_chunk = self.recorder.get_latest_level()
                dashboard.push_wave_level(audio_chunk)
                time.sleep(0.05)

        self._wave_thread = threading.Thread(target=feed, daemon=True)
        self._wave_thread.start()

    def _stop_wave_feed(self):
        self._wave_active = False

    def run(self):
        print("[Wispr] Gestartet. Hotkey:", self.conf["hotkey"])

        listener = HotkeyListener(
            hotkey_str=self.conf["hotkey"],
            on_press_cb=self.on_hotkey_press,
            on_release_cb=self.on_hotkey_release,
        )
        listener.start()
        self.float_btn.start()

        # Dashboard im Hauptthread starten (blockiert bis Fenster geschlossen)
        try:
            dashboard.start(self)
        finally:
            listener.stop()
            print("[Wispr] Beendet.")


if __name__ == "__main__":
    app = WisprClone()
    app.run()
