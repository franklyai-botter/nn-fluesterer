"""Kleines always-on-top Fenster das anzeigt ob gerade aufgenommen wird."""
import threading
import tkinter as tk


class Overlay:
    def __init__(self):
        self._root: tk.Tk | None = None
        self._thread: threading.Thread | None = None
        self._visible = False

    def show(self):
        if self._visible:
            return
        self._visible = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def hide(self):
        self._visible = False
        if self._root:
            try:
                self._root.after(0, self._root.destroy)
            except Exception:
                pass
        self._root = None

    def _run(self):
        self._root = tk.Tk()
        root = self._root

        root.overrideredirect(True)       # kein Fensterrahmen
        root.attributes("-topmost", True) # immer im Vordergrund
        root.attributes("-alpha", 0.85)

        # Position: unten rechts
        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()
        w, h = 130, 36
        x = screen_w - w - 20
        y = screen_h - h - 60
        root.geometry(f"{w}x{h}+{x}+{y}")

        frame = tk.Frame(root, bg="#1a1a2e", padx=8, pady=6)
        frame.pack(fill="both", expand=True)

        label = tk.Label(
            frame,
            text="  REC",
            bg="#1a1a2e",
            fg="#ff4757",
            font=("Segoe UI", 13, "bold"),
        )
        label.pack(side="left")

        # Pulsieren simulieren
        self._animate(label, root)
        root.mainloop()

    def _animate(self, label: tk.Label, root: tk.Tk, step: int = 0):
        if not self._visible:
            return
        colors = ["#ff4757", "#ff6b81"]
        label.config(fg=colors[step % 2])
        root.after(500, lambda: self._animate(label, root, step + 1))
