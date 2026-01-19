# Body2Bits

<p align="center">
  <img src="assets/banner.png" alt="Body2Bits Banner" width="100%">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/status-experimental-orange" />
  <img src="https://img.shields.io/badge/platform-linux-blue" />
  <img src="https://img.shields.io/badge/input-weird_hardware-purple" />
  <img src="https://img.shields.io/badge/python-evdev%20%2F%20uinput-green" />
  <img src="https://img.shields.io/badge/license-MIT-lightgrey" />
</p>

<p align="center">
  <strong>Human body as a game controller.</strong><br>
  Linux, weird hardware, classic games.
</p>

---
▶️ Input Is Lava 🔥 (https://www.youtube.com/@dennis_hilk)
---
Body2Bits is an experimental project that explores using the human body  
as a game controller on Linux.  
Unconventional input devices, physical movement, and classic games.

## How it works

1. **Input device:** The Wii Balance Board provides weight and balance data.
2. **Linux input layer:** `evdev` reads the raw device events, while `uinput` exposes a virtual keyboard.
3. **Mapping:** Movements are translated into key presses for classic games.
4. **Calibration:** A persistent calibration profile keeps the experience consistent between sessions.

## Status

🧪 **Experimental / Work in Progress**  
Initial prototype created on **2026-01-19**.

## Current Prototype

- Wii Balance Board as input device
- Linux (evdev / uinput)
- Physical movement mapped to keyboard input
- Persistent calibration support
