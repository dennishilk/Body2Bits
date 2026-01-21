#!/usr/bin/env python3
"""
Wii Balance Board Reader – FINAL
--------------------------------
- evdev only (no pygame)
- 4 sensor mapping (codes 16–19)
- tare / calibration
- computes X/Y center of mass
- writes clean data for Snake-Fit
"""

import time
import json
from evdev import InputDevice, list_devices, ecodes

STATE_FILE = "/tmp/snakefit_wbb.json"

# Sensor mapping from your logs
SENSORS = {
    16: "tl",  # top left
    17: "tr",  # top right
    18: "bl",  # bottom left
    19: "br",  # bottom right
}

def find_board():
    for p in list_devices():
        d = InputDevice(p)
        if "Nintendo Wii Remote Balance Board" in d.name:
            print("[WBB] Using", d.path, d.name)
            return d
    raise RuntimeError("Wii Balance Board not found")

def main():
    dev = find_board()

    raw = {"tl": 0, "tr": 0, "bl": 0, "br": 0}
    tare = raw.copy()

    print("[WBB] Stand still for calibration…")
    time.sleep(2.0)
    tare = raw.copy()
    print("[WBB] Tare complete:", tare)

    while True:
        e = dev.read_one()
        if e is None:
            time.sleep(0.005)
            continue

        if e.type == ecodes.EV_ABS and e.code in SENSORS:
            raw[SENSORS[e.code]] = e.value

            # calibrated values
            tl = raw["tl"] - tare["tl"]
            tr = raw["tr"] - tare["tr"]
            bl = raw["bl"] - tare["bl"]
            br = raw["br"] - tare["br"]

            # center of mass
            x = (tr + br) - (tl + bl)
            y = (tl + tr) - (bl + br)

            data = {
                "x": x,
                "y": y,
                "raw": raw,
            }

            with open(STATE_FILE, "w") as f:
                json.dump(data, f)

if __name__ == "__main__":
    main()
