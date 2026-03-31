"""Text in das aktive Fenster einfügen via Clipboard + Paste-Shortcut."""
import time
import platform
import pyperclip
from pynput.keyboard import Controller, Key


_keyboard = Controller()


def inject(text: str):
    if not text:
        return

    # Alten Clipboard-Inhalt sichern
    try:
        old = pyperclip.paste()
    except Exception:
        old = ""

    pyperclip.copy(text)
    time.sleep(0.05)  # kurz warten bis Clipboard befüllt ist

    # Paste-Shortcut senden
    if platform.system() == "Darwin":
        with _keyboard.pressed(Key.cmd):
            _keyboard.press("v")
            _keyboard.release("v")
    else:
        with _keyboard.pressed(Key.ctrl):
            _keyboard.press("v")
            _keyboard.release("v")

    time.sleep(0.1)  # warten bis Paste abgeschlossen

    # Alten Clipboard-Inhalt wiederherstellen
    try:
        pyperclip.copy(old)
    except Exception:
        pass
