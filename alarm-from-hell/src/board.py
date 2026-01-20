import time
from evdev import InputDevice, list_devices, ecodes


class WiiBalanceBoard:
    """
    evdev-based Wii Balance Board reader.

    Exposes raw sensor values:
    - tl, tr, bl, br
    - total (sum)
    """

    AXES = {
        ecodes.ABS_HAT0X: "tl",
        ecodes.ABS_HAT0Y: "tr",
        ecodes.ABS_HAT1X: "bl",
        ecodes.ABS_HAT1Y: "br",
    }

    def __init__(self):
        self.dev = None
        self.values = {
            "tl": 0,
            "tr": 0,
            "bl": 0,
            "br": 0,
        }

    def connect(self):
        for path in list_devices():
            dev = InputDevice(path)
            name = dev.name.lower()
            if "balance" in name and "wii" in name:
                self.dev = dev
                return
        raise RuntimeError("Wii Balance Board not found (evdev)")

    def close(self):
        if self.dev:
            self.dev.close()

    def read_samples(self):
        """
        Generator yielding sensor snapshots:
        {
          'tl': int,
          'tr': int,
          'bl': int,
          'br': int,
          'total': int
        }
        """
        for event in self.dev.read_loop():
            if event.type == ecodes.EV_ABS and event.code in self.AXES:
                key = self.AXES[event.code]
                self.values[key] = event.value

                yield {
                    "tl": self.values["tl"],
                    "tr": self.values["tr"],
                    "bl": self.values["bl"],
                    "br": self.values["br"],
                    "total": (
                        self.values["tl"]
                        + self.values["tr"]
                        + self.values["bl"]
                        + self.values["br"]
                    ),
                }


# -----------------------------
# Simple test harness
# -----------------------------
if __name__ == "__main__":
    board = WiiBalanceBoard()

    print("Connecting to Wii Balance Board (evdev)...")
    board.connect()
    print(f"Connected: {board.dev.path} ({board.dev.name})\n")

    try:
        last_print = time.time()
        for sample in board.read_samples():
            now = time.time()
            if now - last_print > 0.1:  # ~10 Hz output
                print(
                    f"TL={sample['tl']:6d} "
                    f"TR={sample['tr']:6d} "
                    f"BL={sample['bl']:6d} "
                    f"BR={sample['br']:6d} "
                    f"| TOTAL={sample['total']:7d}"
                )
                last_print = now
    except KeyboardInterrupt:
        print("\nStopping.")
    finally:
        board.close()
