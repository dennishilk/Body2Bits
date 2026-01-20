# Body2Bits

<p align="center">
  <img src="banner.png" alt="Body2Bits Banner" width="100%">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/status-experimental-orange" />
  <img src="https://img.shields.io/badge/platform-linux-blue" />
  <img src="https://img.shields.io/badge/input-weird_hardware-purple" />
  <img src="https://img.shields.io/badge/python-evdev%20%2F%20uinput-green" />
  <img src="https://img.shields.io/badge/license-MIT-lightgrey" />
</p>

<p align="center">
  <strong>Human body as an input device.</strong><br>
  Linux, weird hardware, experimental input projects.
</p>

---

▶️ **Input Is Lava 🔥**  
https://www.youtube.com/@dennis_hilk

---

## Overview

Body2Bits is an experimental Linux project space exploring a simple question:

**What happens when the human body becomes the input device?**

Instead of keyboards, mice, or gamepads, these projects use:
- weight
- balance
- motion
- physical presence

as first-class input signals.

The focus is not fitness or health.  
The focus is **control, feedback, and consequences**.

This repository contains small, opinionated experiments that combine:
- Linux
- weird hardware
- raw sensor data
- slightly unhinged ideas

All projects aim to be:
- technically transparent
- reproducible
- visually demonstrable
- and interesting to watch (especially when they fail)

---

## 🧪 Projects

### DoomFit
Play Doom using a Wii Balance Board.

Movement is controlled by weight shifts, stomps, and balance.  
Yes, it works. No, it’s not comfortable.

→ `doom-fit/`

---

### Alarm from Hell 😈
An alarm clock that cannot be snoozed.

The alarm stops only if:
- your body steps onto a Wii Balance Board
- you perform required physical actions
- and remain still afterward

Leaving the board or stopping early escalates the alarm.

→ `alarm-from-hell/`

---

## Philosophy

Body2Bits intentionally avoids machine learning where possible.

Human movement is already loud in raw sensor data.  
Thresholds, deltas, and simple physics are often enough.

If a system cannot explain *why* it reacts,  
it should not control your body.

---

## Status

Highly experimental.  
Occasionally sadistic.  
Always honest.

Linux only.
