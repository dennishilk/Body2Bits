#!/usr/bin/env python3

import sys
import time
from pathlib import Path

# --- make project root importable ---
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.evdev_reader import BalanceBoardEvdev
from src.balance_math import center_of_mass
from src.neverball_input import NeverballController
from src.calibration import run_calibration, load_calibration


# --- helpers -------------------------------------------------

def clamp(v: float) -> float:
    if v < -1.0:
        return -1.0
    if v > 1.0:
        return 1.0
    return v


def scale(v: float, vmin: float, vmax: float) -> float:
    """
    Scale a value into [-1..1] based on calibrated min/max.
    Handles asymmetric ranges and avoids division by zero.
    """
    if v < 0 and vmin != 0:
        return v / abs(vmin)
    if v > 0 and vmax != 0:
        return v / abs(vmax)
    return 0.0


# --- main ----------------------------------------------------

def main():
    board = BalanceBoardEvdev()
    ctrl = NeverballController()

    # load or run calibration
    cal = load_calibration()
    if "--recalibrate" in sys.argv or cal is None:
        cal = run_calibration(board, center_of_mass)
    else:
        print("[cal] Calibration loaded")

    # main loop
    while True:
        values = board.snapshot()
        x, y, active = center_of_mass(values)

        # nobody on board → absolute stillstand
        if not active:
            ctrl.update(0.0, 0.0)
            time.sleep(0.02)
            continue

        # remove neutral offset
        x -= cal["neutral_x"]
        y -= cal["neutral_y"]

        # scale to [-1..1] using calibrated extremes
        x = scale(x, cal["min_x"], cal["max_x"])
        y = scale(y, cal["min_y"], cal["max_y"])

        ctrl.update(clamp(x), clamp(y))
        time.sleep(0.02)


if __name__ == "__main__":
    main()