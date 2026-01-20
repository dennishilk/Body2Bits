#!/usr/bin/env python3
"""
by Dennis Hilk

Mapping:
- D-Pad Left  -> Turn left
- D-Pad Right -> Turn right
- D-Pad Up    -> Look up
- D-Pad Down  -> Look down
- B (Trigger) -> Fire
- A           -> Jump
- Home        -> Exit script
"""

from evdev import InputDevice, list_devices, ecodes, UInput
import sys
import time

# ================= CONFIG =================

# Doom / FPS key bindings
KEY_TURN_LEFT  = ecodes.KEY_LEFT
KEY_TURN_RIGHT = ecodes.KEY_RIGHT
KEY_LOOK_UP    = ecodes.KEY_PAGEUP
KEY_LOOK_DOWN  = ecodes.KEY_PAGEDOWN

KEY_FIRE = ecodes.KEY_LEFTCTRL
KEY_JUMP = ecodes.KEY_SPACE

EXIT_KEY = ecodes.KEY_HOME

# Small delay to avoid busy looping
LOOP_DELAY = 0.005

# =========================================


def find_wiimote():
    for path in list_devices():
        try:
            dev = InputDevice(path)
            name = dev.name.lower()
            if "nintendo" in name and "rvl-cnt" in name:
                return dev
        except OSError:
            pass
    return None


wiimote = find_wiimote()
if not wiimote:
    print("Wiimote not found (evdev)")
    sys.exit(1)

print(f"Using Wiimote device: {wiimote.path}")
print(f"Device name         : {wiimote.name}")

wiimote.grab()

ui = UInput(
    {
        ecodes.EV_KEY: [
            KEY_TURN_LEFT,
            KEY_TURN_RIGHT,
            KEY_LOOK_UP,
            KEY_LOOK_DOWN,
            KEY_FIRE,
            KEY_JUMP,
        ]
    },
    name="Body2Bits-Wiimote",
)

print("Wiimote active:")
print("  D-Pad Left/Right -> Turn")
print("  D-Pad Up/Down    -> Look")
print("  B                -> Fire")
print("  A                -> Jump")
print("  Home             -> Exit")

try:
    for event in wiimote.read_loop():
        if event.type != ecodes.EV_KEY:
            continue

        value = event.value  # 1 = press, 0 = release

        # D-Pad
        if event.code == ecodes.BTN_DPAD_LEFT:
            ui.write(ecodes.EV_KEY, KEY_TURN_LEFT, value)
        elif event.code == ecodes.BTN_DPAD_RIGHT:
            ui.write(ecodes.EV_KEY, KEY_TURN_RIGHT, value)
        elif event.code == ecodes.BTN_DPAD_UP:
            ui.write(ecodes.EV_KEY, KEY_LOOK_UP, value)
        elif event.code == ecodes.BTN_DPAD_DOWN:
            ui.write(ecodes.EV_KEY, KEY_LOOK_DOWN, value)

        # Buttons
        elif event.code == ecodes.BTN_TR2:  # B trigger
            ui.write(ecodes.EV_KEY, KEY_FIRE, value)
        elif event.code == ecodes.BTN_SOUTH:  # A button
            ui.write(ecodes.EV_KEY, KEY_JUMP, value)
        elif event.code == EXIT_KEY and value == 1:
            break

        ui.syn()
        time.sleep(LOOP_DELAY)

except KeyboardInterrupt:
    pass

finally:
    wiimote.ungrab()
    ui.close()
    print("Wiimote script stopped")
