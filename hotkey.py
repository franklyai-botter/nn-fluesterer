"""Globaler Hotkey: Hold-to-Record via pynput."""
import threading
from pynput import keyboard


class HotkeyListener:
    def __init__(self, hotkey_str: str, on_press_cb, on_release_cb):
        """
        hotkey_str: z.B. "<ctrl>+<shift>+space"
        on_press_cb:   wird aufgerufen wenn Hotkey gedrückt wird
        on_release_cb: wird aufgerufen wenn Hotkey losgelassen wird
        """
        self._hotkey_str = hotkey_str
        self._on_press = on_press_cb
        self._on_release = on_release_cb
        self._listener: keyboard.Listener | None = None
        self._pressed_keys: set = set()
        self._hotkey_keys = self._parse_hotkey(hotkey_str)
        self._recording = False
        self._lock = threading.Lock()

    def _parse_hotkey(self, hotkey_str: str) -> set:
        """Konvertiert '<ctrl>+<shift>+space' zu einem Set von pynput-Keys."""
        parts = hotkey_str.split("+")
        keys = set()
        for part in parts:
            part = part.strip()
            if part.startswith("<") and part.endswith(">"):
                key_name = part[1:-1]
                try:
                    keys.add(getattr(keyboard.Key, key_name))
                except AttributeError:
                    pass
            else:
                keys.add(keyboard.KeyCode.from_char(part))
        return keys

    def _normalize(self, key) -> object:
        """Normalisiert ctrl_l/ctrl_r → ctrl etc."""
        try:
            if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                return keyboard.Key.ctrl
            if key == keyboard.Key.shift_l or key == keyboard.Key.shift_r:
                return keyboard.Key.shift
            if key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
                return keyboard.Key.alt
        except Exception:
            pass
        return key

    def _on_key_press(self, key):
        key = self._normalize(key)
        with self._lock:
            self._pressed_keys.add(key)
            if self._hotkey_keys.issubset(self._pressed_keys) and not self._recording:
                self._recording = True
                threading.Thread(target=self._on_press, daemon=True).start()

    def _on_key_release(self, key):
        key = self._normalize(key)
        with self._lock:
            self._pressed_keys.discard(key)
            if self._recording and not self._hotkey_keys.issubset(self._pressed_keys):
                self._recording = False
                threading.Thread(target=self._on_release, daemon=True).start()

    def start(self):
        self._listener = keyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release,
        )
        self._listener.start()

    def stop(self):
        if self._listener:
            self._listener.stop()
