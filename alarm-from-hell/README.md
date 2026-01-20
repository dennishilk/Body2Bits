# Alarm from Hell 😈

<p align="center">
  <img src="https://img.shields.io/badge/status-experimental-orange" />
  <img src="https://img.shields.io/badge/platform-linux-blue" />
  <img src="https://img.shields.io/badge/input-wii_balance_board-purple" />
  <img src="https://img.shields.io/badge/python-3.x-green" />
  <img src="https://img.shields.io/badge/license-MIT-lightgrey" />
</p>


**Alarm from Hell** is a Linux alarm clock that does not ring.

It **demands physical compliance**.

To stop the alarm, you must:
- stand on a Wii Balance Board
- perform a configurable number of squats
- then stand perfectly still for a configurable amount of time

If you stop, leave the board, or move too early, the alarm escalates.

No snooze button.  
No negotiation.

---

## What This Is

- A physical alarm clock
- A Body2Bits experiment
- Linux + Bluetooth + evdev + sound
- Surprisingly effective and slightly sadistic

This is not a fitness app.  
This is a wake-up protocol.

---

## Requirements

### Hardware
- Nintendo Wii Balance Board
- Bluetooth-capable Linux machine

### Software
- Linux
- Python 3
- sox
- python3-evdev

---

## Installation

```bash
git clone https://github.com/yourname/alarm-from-hell.git
cd alarm-from-hell
chmod +x installer.sh
./installer.sh
```
The installer installs required system packages, does not enable autostart, and does not modify system configuration silently.

Pairing the Wii Balance Board
Pair the Wii Balance Board using your desktop Bluetooth UI.
Avoid using bluetoothctl if possible.

After pairing, step on the board once to wake it up.

Quick test:
```bash
cd src
python3 board.py
```
If values change while standing on the board, the connection works.

Calibration (Recommended)
Before first use:
```bash
python3 src/calibration.py
```
Calibration measures zero offset and body weight and writes the values automatically to src/config.py.


## Difficulty can be changed via `PRESET` in `src/config.py`
(`easy`, `normal`, `hell`).

---


Starting the Alarm
Start the alarm using a relative delay before going to bed:
```bash
python3 src/alarm.py --in 8h
python3 src/alarm.py --in 8h10m
python3 src/alarm.py --in 1h30m
```
### Supported Time Units

You can start the alarm using relative time delays.

Supported units:
- `h` = hours
- `m` = minutes
- `s` = seconds

Combinations like 8h10m are supported.

---

### Configuration

All configuration is done in:

```text
src/config.py
REQUIRED_SQUATS = 10
REQUIRED_STILL_TIME_SEC = 30.0
MIN_WEIGHT_KG = 20.0
```
No other code needs to be changed.

---

### What Happens

- Alarm starts with sound and fullscreen terminal output

- Get on the board

- Perform squats

- Stand perfectly still

- Silence

Any attempt to stop, step off the board, or move too early will escalate the alarm.

---

### Warning ⚠️

This project is loud, annoying, and physically demanding.

Do not use if you:

have joint or heart problems

have neighbors you like

expect a gentle wake-up
