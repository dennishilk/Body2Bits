#!/usr/bin/env python3
"""
DoomFit – Wii Balance Board → Keyboard
Stable movement + stomp fire

- Lean = WASD
- Standing = full stop
- Stomp (hard weight impulse) = Fire (BTN_LEFT)

Author: Dennis Hilk
"""

from evdev import InputDevice, list_devices, ecodes, UInput
import time, json, os, sys
from collections import deque

# ================= CONFIG =================
CALIBRATION_TIME = 15

# Movement tuning (stable & calm)
STAND_LOCK_ZONE = 0.22
MOVE_THRESHOLD = 0.50
HOLD_TIME = 0.35
SMOOTHING = 20

# Weight
WEIGHT_MIN = 22

# Stomp (fire)
Z_SMOOTHING = 25
STOMP_DELTA = 18
STOMP_COOLDOWN = 0.5

CAL_FILE = os.path.expanduser("~/.doomfit_calibration.json")
# =========================================

KEY_FORWARD = ecodes.KEY_W
KEY_BACK    = ecodes.KEY_S
KEY_LEFT    = ecodes.KEY_A
KEY_RIGHT   = ecodes.KEY_D
KEY_FIRE    = ecodes.BTN_LEFT

state = {
    KEY_FORWARD: 0,
    KEY_BACK:    0,
    KEY_LEFT:    0,
    KEY_RIGHT:   0,
}

move_timer = {k: 0.0 for k in state}

Z = 0
last_stomp_time = 0.0

def find_board():
    for path in list_devices():
        try:
            dev = InputDevice(path)
            if "RVL-WBC" in dev.name or "Nintendo" in dev.name:
                return dev
        except:
            pass
    return None

def set_key(ui, key, pressed):
    if state[key] != pressed:
        state[key] = pressed
        ui.write(ecodes.EV_KEY, key, pressed)
        ui.syn()

def release_all(ui):
    for k in state:
        set_key(ui, k, 0)
        move_timer[k] = 0.0

# ---------- Board ----------
board = find_board()
if not board:
    print("❌ Wii Balance Board not found")
    sys.exit(1)

board.grab()

# ---------- Calibration ----------
if "--recalibrate" in sys.argv or not os.path.exists(CAL_FILE):
    print(f"🧍 Calibration running ({CALIBRATION_TIME}s). Stand still.")
    xs, ys = deque(), deque()
    start = time.time()

    for e in board.read_loop():
        if e.type == ecodes.EV_ABS:
            if e.code == 16: xs.append(e.value)
            if e.code == 17: ys.append(e.value)
        if time.time() - start >= CALIBRATION_TIME:
            break

    neutral_x = sum(xs) / len(xs)
    neutral_y = sum(ys) / len(ys)

    print("➡️ Lean forward clearly (2s)")
    ys_dir = deque()
    start = time.time()

    for e in board.read_loop():
        if e.type == ecodes.EV_ABS and e.code == 17:
            ys_dir.append(e.value)
        if time.time() - start >= 2:
            break

    y_dir = -1 if sum(ys_dir)/len(ys_dir) < neutral_y else 1

    with open(CAL_FILE, "w") as f:
        json.dump({"nx": neutral_x, "ny": neutral_y, "yd": y_dir}, f)

    print("✅ Calibration saved")

else:
    with open(CAL_FILE) as f:
        data = json.load(f)
        neutral_x, neutral_y, y_dir = data["nx"], data["ny"], data["yd"]
    print("✅ Calibration loaded")

# ---------- Virtual Keyboard ----------
ui = UInput(
    {ecodes.EV_KEY: [KEY_FORWARD, KEY_BACK, KEY_LEFT, KEY_RIGHT, KEY_FIRE]},
    name="DoomFit-WBB",
)

sx, sy = deque(maxlen=SMOOTHING), deque(maxlen=SMOOTHING)
sz = deque(maxlen=Z_SMOOTHING)

print("🎮 DoomFit active – Lean = Move | Stomp = Fire")

try:
    for e in board.read_loop():
        if e.type != ecodes.EV_ABS:
            continue

        if e.code == 16:
            sx.append(e.value)
        elif e.code == 17:
            sy.append(e.value)
        elif e.code in (18, 19):
            Z = e.value
            sz.append(e.value)

        if Z < WEIGHT_MIN:
            release_all(ui)
            continue

        if len(sx) < SMOOTHING or len(sy) < SMOOTHING:
            continue

        nx = ((sum(sx) / len(sx)) - neutral_x) / 128
        ny = (((sum(sy) / len(sy)) - neutral_y) / 128) * y_dir

        # ---------- Standing ----------
        if abs(nx) < STAND_LOCK_ZONE and abs(ny) < STAND_LOCK_ZONE:
            release_all(ui)
            continue

        now = time.time()

        # ---------- Stomp = Fire ----------
        if len(sz) == Z_SMOOTHING:
            z_base = sum(sz) / len(sz)
            if (Z - z_base) > STOMP_DELTA and now - last_stomp_time > STOMP_COOLDOWN:
                ui.write(ecodes.EV_KEY, KEY_FIRE, 1)
                ui.syn()
                ui.write(ecodes.EV_KEY, KEY_FIRE, 0)
                ui.syn()
                last_stomp_time = now

        # ---------- Movement ----------
        def handle(axis, key, positive):
            active = axis > MOVE_THRESHOLD if positive else axis < -MOVE_THRESHOLD
            if active:
                if move_timer[key] == 0:
                    move_timer[key] = now
                elif now - move_timer[key] >= HOLD_TIME:
                    set_key(ui, key, 1)
            else:
                move_timer[key] = 0
                set_key(ui, key, 0)

        handle(ny, KEY_FORWARD, True)
        handle(ny, KEY_BACK, False)
        handle(nx, KEY_RIGHT, True)
        handle(nx, KEY_LEFT, False)

        time.sleep(0.006)

except KeyboardInterrupt:
    print("\n👋 DoomFit stopped")

finally:
    board.ungrab()
    ui.close()
