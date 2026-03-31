import os
import yaml

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.yaml")

_defaults = {
    "hotkey": "<ctrl>+<shift>+space",
    "whisper_model": "base",
    "language": "de",
    "ai_cleanup": False,
    "groq_api_key": "",
    "recording": {
        "sample_rate": 16000,
        "min_duration": 0.3,
    },
}


def load() -> dict:
    if not os.path.exists(CONFIG_PATH):
        return _defaults.copy()
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    # Deep merge mit defaults
    merged = _defaults.copy()
    merged.update(data)
    if "recording" in data:
        merged["recording"] = {**_defaults["recording"], **data["recording"]}
    return merged
