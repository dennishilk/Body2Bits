"""
Snake-Fit – Wii Balance Board Input (IPC)
Reads processed X/Y values from wbb_reader.py
"""

import json
import snakefit.config as cfg

STATE_FILE = "/tmp/snakefit_wbb.json"

class WiiBoardInput:
    def __init__(self):
        self.last_x = 0.0
        self.last_y = 0.0
        self.last_input_time = 0

    def get_direction(self):
        try:
            with open(STATE_FILE, "r") as f:
                data = json.load(f)
                x = float(data.get("x", 0.0))
                y = float(data.get("y", 0.0))
        except Exception:
            return None

        self.last_x = x
        self.last_y = y

        # Deadzone
        if abs(x) < cfg.DEADZONE_X and abs(y) < cfg.DEADZONE_Y:
            return None

        # Cooldown
        import time
        now = int(time.time() * 1000)
        if now - self.last_input_time < cfg.INPUT_COOLDOWN_MS:
            return None

        self.last_input_time = now

        # Direction decision
        if abs(x) > abs(y):
            return "RIGHT" if x > 0 else "LEFT"
        else:
            return "UP" if y > 0 else "DOWN"
