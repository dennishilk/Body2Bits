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

Body2Bits is an experimental project exploring the human body as an input device on Linux.

Instead of traditional controllers, Body2Bits uses physical movement, balance, and weight as primary input signals.  
The goal is not realism or efficiency, but playful, sometimes absurd, and often surprising human–computer interaction.

This project intentionally blends:

- unconventional hardware  
- physical interaction  
- minimal software layers  
- a bit of controlled chaos  

---

## How it works

### Input devices

Primarily the **Wii Balance Board**, providing raw weight and balance data.  
Additional devices (e.g. Wii Remote, cameras, sensors) may be explored later.

### Linux input layer

Raw data is read via **evdev**.  
A virtual input device is exposed using **uinput**, allowing compatibility with existing software.

### Mapping

Physical actions such as leaning, standing still, squatting, or weight shifts are translated into keyboard or mouse input.

### Calibration

A persistent calibration profile ensures consistent behavior across sessions, even with different body weights or setups.

---
## 🔥 Alarm from Hell

A sadistic alarm clock that cannot be snoozed.

The alarm stops only if you:
- step onto a Wii Balance Board
- perform physical actions (stomps / squats)
- remain still afterward

Leaving the board resets or escalates the alarm.

→ `alarm-from-hell/`


## Status

🧪 **Experimental / Work in Progress**  
Initial prototype created on **2026-01-19**

Expect:

- rapid iteration  
- broken ideas  
- weird but fun results  

Stability is not the goal. Exploration is.

---

## Current Prototype

- Wii Balance Board as primary input device  
- Linux (`evdev` / `uinput`)  
- Physical movement mapped to keyboard input  
- Persistent calibration support  
