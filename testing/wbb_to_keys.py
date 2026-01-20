#!/usr/bin/env python3
"""
DoomFit by Dennis Hilk

"""

from evdev import InputDevice, list_devices, ecodes, UInput
import time, json, os, sys
from collections import deque

# ================= CONFIG =================
CALIBRATION_TIME = 15

STAND_LOCK_ZONE  = 0.50   # calm
STILL_DEADZONE   = 0.30
MOVE_THRESHOLD   = 0.80
STOP_THRESHOLD   = 0.65

WEIGHT_MIN = 25
SMOOTHING  = 45
HOLD_TIME  = 0.80

CAL_FILE = os.path.expanduser("~/.doomfit_calibration.json")
# =========================================

KEY_FORWARD = ecodes.KEY_W
KEY_BACK    = ecodes.KEY_S
KEY_LEFT    = ecodes.KEY_A
KEY_RIGHT   = ecodes.KEY_D

state = {
    KEY_FORWARD: 0,
    KEY_BACK:    0,
    KEY_LEFT:    0,
    KEY_RIGHT:   0,
}

move_timer = {
    KEY_FORWARD: 0.0,
    KEY_BACK:    0.0,
    KEY_LEFT:    0.0,
    KEY_RIGHT:   0.0,
}

Z = 0

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
    print("Wii Balance Board not found")
    sys.exit(1)

board.grab()

# ---------- Calibration ----------
if "--recalibrate" in sys.argv or not os.path.exists(CAL_FILE):
    print(f"Calibration running ({CALIBRATION_TIME}s). Stand still.")
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

    print("Lean forward clearly (2s)")
    ys_dir = deque()
    start = time.time()

    for e in board.read_loop():
        if e.type == ecodes.EV_ABS and e.code == 17:
            ys_dir.append(e.value)
        if time.time() - start >= 2:
            break

    y_dir = -1 if sum(ys_dir)/len(ys_dir) < neutral_y else 1

    with open(CAL_FILE, "w") as f:
        json.dump({"nx":neutral_x,"ny":neutral_y,"yd":y_dir}, f)

    print("Calibration saved")

else:
    with open(CAL_FILE) as f:
        data = json.load(f)
        neutral_x, neutral_y, y_dir = data["nx"], data["ny"], data["yd"]
    print("Calibration loaded")

# ---------- Virtual Keyboard ----------
ui = UInput(
    { ecodes.EV_KEY: [KEY_FORWARD, KEY_BACK, KEY_LEFT, KEY_RIGHT] },
    name="DoomFit-WBB"
)

sx, sy = deque(maxlen=SMOOTHING), deque(maxlen=SMOOTHING)

print("DoomFit active – standing is now very calm")

try:
    for e in board.read_loop():
        if e.type == ecodes.EV_ABS:
            if e.code == 16: sx.append(e.value)
            elif e.code == 17: sy.append(e.value)
            elif e.code in (18,19): Z = e.value

            if Z < WEIGHT_MIN:
                release_all(ui)
                continue

            if len(sx) < SMOOTHING or len(sy) < SMOOTHING:
                continue

            nx = ((sum(sx)/len(sx)) - neutral_x) / 128
            ny = (((sum(sy)/len(sy)) - neutral_y) / 128) * y_dir

            # ---------- HARD STANDING LOCK ----------
            if abs(nx) < STAND_LOCK_ZONE and abs(ny) < STAND_LOCK_ZONE:
                release_all(ui)
                continue

            now = time.time()

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

        time.sleep(0.005)

except KeyboardInterrupt:
    pass

finally:
    board.ungrab()
    ui.close()
