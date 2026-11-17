"""
pywebview Dashboard-Bridge.
Verbindet Python-Backend mit dem HTML-Frontend.
"""
import os
import json
import threading
import time
import webview
import config as cfg


_window: webview.Window | None = None
_app_ref = None  # Referenz auf NNFluesterer-Instanz


class Api:
    """Methoden die vom JavaScript aufgerufen werden können."""

    def ui_ready(self):
        """Wird aufgerufen wenn das HTML geladen ist."""
        if _app_ref:
            conf = cfg.load()
            call_js(f"loadConfig({json.dumps(conf)})")

    def save_config(self, json_str: str):
        """Speichert Einstellungen aus dem Dashboard."""
        try:
            data = json.loads(json_str)
        except Exception:
            return
        # YAML neu schreiben
        import yaml
        conf_path = os.path.join(os.path.dirname(__file__), "config.yaml")
        existing = cfg.load()
        existing.update({
            "hotkey":        data.get("hotkey", existing["hotkey"]),
            "whisper_model": data.get("whisper_model", existing["whisper_model"]),
            "language":      data.get("language") or None,
            "ai_cleanup":    bool(data.get("ai_cleanup", False)),
            "groq_api_key":  data.get("groq_api_key", ""),
        })
        with open(conf_path, "w", encoding="utf-8") as f:
            yaml.dump(existing, f, allow_unicode=True, default_flow_style=False)


def call_js(code: str):
    """Führt JavaScript im Dashboard-Fenster aus (thread-safe)."""
    if _window:
        try:
            _window.evaluate_js(code)
        except Exception:
            pass


def set_status(state: str, sub: str = ""):
    """state: 'idle' | 'recording' | 'processing'"""
    sub_escaped = sub.replace("'", "\\'")
    call_js(f"updateStatus('{state}', '{sub_escaped}')")


def add_transcript(text: str):
    """Neues Transkript ins Dashboard eintragen."""
    import datetime
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    text_escaped = text.replace("\\", "\\\\").replace("'", "\\'")
    call_js(f"addTranscript('{text_escaped}', '{ts}')")


def push_wave_level(level: float):
    """Audio-Pegel ans Dashboard senden (0.0–1.0)."""
    call_js(f"updateWaveform({level:.3f})")


def start(app_instance):
    """Startet das pywebview-Fenster im Hauptthread (blockiert)."""
    global _window, _app_ref
    _app_ref = app_instance

    import sys
    base = sys._MEIPASS if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(base, "dashboard", "index.html")
    api = Api()

    _window = webview.create_window(
        title="NN-Flüsterer",
        url=f"file:///{html_path.replace(os.sep, '/')}",
        js_api=api,
        width=960,
        height=620,
        min_size=(700, 480),
        background_color="#050b14",
        frameless=False,
    )

    webview.start(debug=False)
