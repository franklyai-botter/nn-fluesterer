"""
Floating Push-to-Talk Button — immer sichtbar auf dem Desktop.
Links halten = Aufnahme, loslassen = Transkription.
Kann per Drag verschoben werden.
"""
import tkinter as tk
import threading
import math
import time


class FloatingButton:
    SIZE = 72
    PADDING = 6

    def __init__(self, on_press_cb, on_release_cb):
        self._on_press = on_press_cb
        self._on_release = on_release_cb
        self._recording = False
        self._processing = False
        self._drag_x = 0
        self._drag_y = 0
        self._anim_angle = 0
        self._root: tk.Tk | None = None
        self._canvas: tk.Canvas | None = None
        self._thread: threading.Thread | None = None

    def start(self):
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        root = tk.Tk()
        self._root = root
        s = self.SIZE

        root.overrideredirect(True)
        root.attributes("-topmost", True)
        root.attributes("-transparentcolor", "#010101")
        root.configure(bg="#010101")
        root.resizable(False, False)

        # Position: unten rechts
        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        x = sw - s - 30
        y = sh - s - 80
        root.geometry(f"{s}x{s}+{x}+{y}")

        canvas = tk.Canvas(root, width=s, height=s, bg="#010101",
                           highlightthickness=0, bd=0)
        canvas.pack()
        self._canvas = canvas

        # Drag
        canvas.bind("<ButtonPress-3>",   self._drag_start)
        canvas.bind("<B3-Motion>",       self._drag_move)

        # Record on left click
        canvas.bind("<ButtonPress-1>",   self._btn_press)
        canvas.bind("<ButtonRelease-1>", self._btn_release)

        self._draw_idle()
        self._animate()
        root.mainloop()

    # ── Drawing ──

    def _draw_idle(self):
        c = self._canvas
        if not c:
            return
        s = self.SIZE
        c.delete("all")
        cx, cy = s // 2, s // 2
        r = s // 2 - self.PADDING

        # Outer glow ring
        c.create_oval(cx-r-4, cy-r-4, cx+r+4, cy+r+4,
                      outline="#003344", width=2, fill="")
        # Main circle
        c.create_oval(cx-r, cy-r, cx+r, cy+r,
                      fill="#0d1b2a", outline="#00d4ff", width=2)
        # Mic icon
        self._draw_mic(c, cx, cy, color="#00d4ff")

    def _draw_recording(self):
        c = self._canvas
        if not c:
            return
        s = self.SIZE
        c.delete("all")
        cx, cy = s // 2, s // 2
        r = s // 2 - self.PADDING

        # Pulsing glow (mehrere Ringe)
        pulse = abs(math.sin(self._anim_angle))
        for i, alpha in enumerate([0.15, 0.25, 0.5]):
            pr = r + 8 - i * 3 + int(pulse * 5)
            shade = int(alpha * 255)
            color = f"#ff{shade:02x}{shade:02x}" if i < 2 else "#ff3366"
            c.create_oval(cx-pr, cy-pr, cx+pr, cy+pr,
                          outline=color, width=1 + i, fill="")

        # Main circle — rot
        c.create_oval(cx-r, cy-r, cx+r, cy+r,
                      fill="#1a0010", outline="#ff3366", width=3)
        # Mic icon — rot
        self._draw_mic(c, cx, cy, color="#ff3366")

        # REC dot
        rd = 5
        c.create_oval(cx+14, cy-20, cx+14+rd*2, cy-20+rd*2,
                      fill="#ff3366", outline="")

    def _draw_processing(self):
        c = self._canvas
        if not c:
            return
        s = self.SIZE
        c.delete("all")
        cx, cy = s // 2, s // 2
        r = s // 2 - self.PADDING

        # Spinning arc
        start = int(self._anim_angle * 180 / math.pi) % 360
        c.create_oval(cx-r, cy-r, cx+r, cy+r,
                      fill="#001122", outline="#003344", width=1)
        c.create_arc(cx-r-2, cy-r-2, cx+r+2, cy+r+2,
                     start=start, extent=240,
                     outline="#00d4ff", width=3, style="arc")
        # Mic icon — cyan dim
        self._draw_mic(c, cx, cy, color="#005566")

    def _draw_mic(self, c, cx, cy, color):
        # Body
        c.create_rectangle(cx-7, cy-14, cx+7, cy+2,
                            fill=color, outline="", width=0)
        # Round top
        c.create_arc(cx-7, cy-22, cx+7, cy-10,
                     start=0, extent=180, fill=color, outline="")
        # Stand arc
        c.create_arc(cx-12, cy-6, cx+12, cy+14,
                     start=180, extent=180,
                     outline=color, width=2, style="arc", fill="")
        # Stand line
        c.create_line(cx, cy+14, cx, cy+20, fill=color, width=2)
        # Base
        c.create_line(cx-7, cy+20, cx+7, cy+20, fill=color, width=2)

    def _animate(self):
        if not self._root:
            return
        self._anim_angle += 0.1
        if self._recording:
            self._draw_recording()
        elif self._processing:
            self._draw_processing()
        self._root.after(50, self._animate)

    # ── Events ──

    def _btn_press(self, event):
        if self._processing:
            return
        self._recording = True
        self._draw_recording()
        threading.Thread(target=self._on_press, daemon=True).start()

    def _btn_release(self, event):
        if not self._recording:
            return
        self._recording = False
        self._processing = True
        self._draw_processing()
        threading.Thread(target=self._release_wrapper, daemon=True).start()

    def _release_wrapper(self):
        self._on_release()
        self._processing = False

    def _drag_start(self, event):
        self._drag_x = event.x_root - self._root.winfo_x()
        self._drag_y = event.y_root - self._root.winfo_y()

    def _drag_move(self, event):
        x = event.x_root - self._drag_x
        y = event.y_root - self._drag_y
        self._root.geometry(f"+{x}+{y}")

    # ── External state updates ──

    def set_idle(self):
        self._recording = False
        self._processing = False
        if self._root:
            self._root.after(0, self._draw_idle)

    def set_processing(self):
        self._processing = True
        self._recording = False
