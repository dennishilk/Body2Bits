#!/usr/bin/env python3

"""
evdev reader for Wii Balance Board
Keeps last known sensor state (non-blocking usage)
"""

from evdev import InputDevice, list_devices, ecodes
import threading

DEVICE_KEYWORDS = [
    "balance board",
    "wii remote balance",
]

ABS_MAP = {
    ecodes.ABS_X: "top_left",
    ecodes.ABS_Y: "top_right",
    ecodes.ABS_Z: "bottom_left",
    ecodes.ABS_RX: "bottom_right",
}


class BalanceBoardEvdev:
    def __init__(self):
        self.dev = self._find_device()
        self.values = {
            "top_left": 0,
            "top_right": 0,
            "bottom_left": 0,
            "bottom_right": 0,
        }

        print(f"[evdev] using device: {self.dev.path}")
        print(f"[evdev] name: {self.dev.name}")

        self._start_reader_thread()

    def _find_device(self):
        for path in list_devices():
            dev = InputDevice(path)
            name = (dev.name or "").lower()
            for kw in DEVICE_KEYWORDS:
                if kw in name:
                    return dev
        raise RuntimeError("Wii Balance Board not found")

    def _start_reader_thread(self):
        t = threading.Thread(target=self._reader, daemon=True)
        t.start()

    def _reader(self):
        for event in self.dev.read_loop():
            if event.type == ecodes.EV_ABS and event.code in ABS_MAP:
                self.values[ABS_MAP[event.code]] = event.value

    def snapshot(self):
        """Return a copy of the latest sensor values"""
        return dict(self.values)
