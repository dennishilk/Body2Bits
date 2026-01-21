import json
import os
import time
from collections import deque

CAL_FILE = os.path.expanduser("~/.neverball_fit_calibration.json")
DT = 0.05

def wait(msg):
    input(f"\n>>> {msg} – ENTER drücken <<<\n")

def sample(board, compute_xy, duration):
    xs, ys = deque(), deque()
    start = time.time()

    while time.time() - start < duration:
        s = board.snapshot()
        x, y, _ = compute_xy(s)
        xs.append(x)
        ys.append(y)
        time.sleep(DT)

    return sum(xs)/len(xs), sum(ys)/len(ys)

def run_calibration(board, compute_xy):
    print("\n=== NEVERBALL-FIT CALIBRATION ===")

    wait("Auf das Board stellen & ruhig stehen (NEUTRAL)")
    nx, ny = sample(board, compute_xy, 3.0)

    wait("Deutlich NACH VORNE lehnen")
    _, fwd = sample(board, compute_xy, 2.0)

    wait("Deutlich NACH HINTEN lehnen")
    _, back = sample(board, compute_xy, 2.0)

    wait("Deutlich NACH LINKS lehnen")
    left, _ = sample(board, compute_xy, 2.0)

    wait("Deutlich NACH RECHTS lehnen")
    right, _ = sample(board, compute_xy, 2.0)

    cal = {
        "neutral_x": nx,
        "neutral_y": ny,
        "min_x": left,
        "max_x": right,
        "min_y": back,
        "max_y": fwd,
    }

    with open(CAL_FILE, "w") as f:
        json.dump(cal, f, indent=2)

    print("\n[cal] Calibration gespeichert:", CAL_FILE)
    return cal

def load_calibration():
    if not os.path.exists(CAL_FILE):
        return None
    with open(CAL_FILE) as f:
        return json.load(f)