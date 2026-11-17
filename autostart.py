"""
Autostart einrichten oder entfernen.
Legt einen Registry-Eintrag an damit NN-Flüsterer mit Windows startet.

Verwendung:
  python autostart.py install    -> Autostart aktivieren
  python autostart.py remove     -> Autostart deaktivieren
  python autostart.py status     -> Status anzeigen
"""
import sys
import os
import winreg

APP_NAME = "NNFluesterer"
REG_KEY  = r"Software\Microsoft\Windows\CurrentVersion\Run"


def get_launch_cmd() -> str:
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}"'
    pythonw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
    main_py = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py")
    return f'"{pythonw}" "{main_py}"'


def install():
    cmd = get_launch_cmd()
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_KEY, 0, winreg.KEY_SET_VALUE) as key:
        winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, cmd)
    print(f"[Autostart] Aktiviert: {cmd}")


def remove():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_KEY, 0, winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, APP_NAME)
        print("[Autostart] Entfernt.")
    except FileNotFoundError:
        print("[Autostart] War nicht eingerichtet.")


def status():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_KEY) as key:
            val, _ = winreg.QueryValueEx(key, APP_NAME)
        print(f"[Autostart] Aktiv -> {val}")
    except FileNotFoundError:
        print("[Autostart] Nicht eingerichtet.")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    {"install": install, "remove": remove, "status": status}.get(cmd, status)()
