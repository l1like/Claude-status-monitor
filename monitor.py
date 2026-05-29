import json
import math
import os
import sys
import time
import threading
import winreg
from pathlib import Path

from PIL import Image, ImageDraw
import pystray

if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent

STATUS_FILE = BASE_DIR / "status.json"
PID_FILE = BASE_DIR / "monitor.pid"

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

AUTOSTART_REG_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
AUTOSTART_REG_NAME = "ClaudeStatusMonitor"


def get_autostart():
    """检查是否已设置开机自启"""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, AUTOSTART_REG_KEY)
        winreg.QueryValueEx(key, AUTOSTART_REG_NAME)
        winreg.CloseKey(key)
        return True
    except FileNotFoundError:
        return False


def set_autostart(enabled):
    """设置或取消开机自启"""
    key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER, AUTOSTART_REG_KEY, 0, winreg.KEY_SET_VALUE
    )
    if enabled:
        exe_path = str(BASE_DIR / "monitor.exe")
        winreg.SetValueEx(key, AUTOSTART_REG_NAME, 0, winreg.REG_SZ, exe_path)
    else:
        try:
            winreg.DeleteValue(key, AUTOSTART_REG_NAME)
        except FileNotFoundError:
            pass
    winreg.CloseKey(key)


def on_toggle_autostart(icon, item):
    new_state = not item.checked
    set_autostart(new_state)
    item.checked = new_state


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
    tray.menu = pystray.Menu(
        pystray.MenuItem(
            "开机自启",
            on_toggle_autostart,
            checked=lambda item: get_autostart(),
        ),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("退出", lambda _: on_quit(tray)),
    )

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
