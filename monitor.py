import json
import math
import os
import sys
import time
import threading
from pathlib import Path

from PIL import Image, ImageDraw
import pystray

STATUS_FILE = Path(__file__).parent / "status.json"
PID_FILE = Path(__file__).parent / "monitor.pid"

STATUS_COLORS = {
    "idle": (128, 128, 128),
    "running": (255, 200, 0),
    "done": (0, 200, 0),
    "confirm": (255, 80, 0),
    "error": (255, 0, 0),
}

LABELS = {
    "idle": "Claude - Idle",
    "running": "Claude - Running",
    "done": "Claude - Done",
    "confirm": "Claude - Confirm Needed",
    "error": "Claude - Error",
}

BREATH = {
    "idle":    False,
    "running": True,
    "done":    False,
    "confirm": True,
    "error":   False,
}

BREATH_PERIOD = 2.0     # seconds for one full breathe cycle
BREATH_MIN = 0.25        # dimmest brightness factor


def lerp_color(rgb, factor):
    return tuple(int(c * factor) for c in rgb)


def create_icon(rgb):
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    r = 6
    draw.ellipse([r, r, size - r, size - r], fill=rgb)
    return img


def read_status():
    try:
        if STATUS_FILE.exists():
            data = json.loads(STATUS_FILE.read_text(encoding="utf-8"))
            s = data.get("status", "idle")
            if s in STATUS_COLORS:
                return s
    except Exception:
        pass
    return "idle"


def on_quit(icon):
    PID_FILE.unlink(missing_ok=True)
    icon.stop()


def main():
    if PID_FILE.exists():
        old_pid = PID_FILE.read_text().strip()
        print(f"Monitor already running (PID {old_pid}). Stop it first.")
        sys.exit(1)

    PID_FILE.write_text(str(os.getpid()))

    state = {"status": "idle", "phase_start": time.time()}
    stop_event = threading.Event()

    icon = create_icon(STATUS_COLORS["idle"])
    tray = pystray.Icon("claude-status", icon, LABELS["idle"])
    tray.menu = pystray.Menu(pystray.MenuItem("Quit", lambda _: on_quit(tray)))

    def anim_loop():
        last_check = 0.0
        while not stop_event.is_set():
            now = time.time()

            # poll status file every 500ms
            if now - last_check > 0.5:
                new = read_status()
                if new != state["status"]:
                    state["status"] = new
                    state["phase_start"] = now
                last_check = now

            color = STATUS_COLORS[state["status"]]

            if BREATH.get(state["status"], False):
                elapsed = now - state["phase_start"]
                phase = (elapsed % BREATH_PERIOD) / BREATH_PERIOD
                # sin wave: 0..1..0
                factor = BREATH_MIN + (1.0 - BREATH_MIN) * 0.5 * (1.0 - math.cos(phase * 2 * math.pi))
                color = lerp_color(color, factor)

            tray.icon = create_icon(color)
            tray.title = LABELS[state["status"]]
            time.sleep(1 / 30)

    t = threading.Thread(target=anim_loop, daemon=True)
    t.start()
    tray.run()
    stop_event.set()


if __name__ == "__main__":
    main()
