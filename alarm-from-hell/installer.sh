#!/usr/bin/env bash
set -e

echo "==========================================="
echo " Alarm from Hell – Installer By Dennis Hilk"
echo "==========================================="
echo

# ---- Basic sanity check ----
if [ "$EUID" -ne 0 ]; then
  echo "[INFO] This installer needs sudo privileges."
  echo "       You may be asked for your password."
  echo
fi

# ---- Update package lists ----
echo "[INFO] Updating package lists..."
sudo apt update

# ---- Install system dependencies ----
echo "[INFO] Installing system dependencies..."

sudo apt install -y \
  python3 \
  python3-pip \
  python3-evdev \
  sox \
  libsox-fmt-alsa \
  bluez \
  bluez-tools \
  bluetooth \
  pulseaudio-utils

# ---- Verify Python ----
echo
echo "[INFO] Verifying Python installation..."
python3 --version

# ---- Info block ----
echo
echo "--------------------------------------"
echo " Wii Balance Board Setup"
echo "--------------------------------------"
echo
echo "IMPORTANT:"
echo "- Pair the Wii Balance Board using your DESKTOP Bluetooth UI."
echo "- Avoid using bluetoothctl if possible."
echo "- After pairing, step on the board once to wake it up."
echo
echo "Quick test:"
echo "  cd src"
echo "  python3 board.py"
echo

# ---- Calibration hint ----
echo "--------------------------------------"
echo " Calibration (Recommended)"
echo "--------------------------------------"
echo
echo "Before first use, run:"
echo "  python3 src/calibration.py"
echo

# ---- Start hint ----
echo "--------------------------------------"
echo " Starting the Alarm"
echo "--------------------------------------"
echo
echo "Example:"
echo "  python3 src/alarm.py --in 8h"
echo "  python3 src/alarm.py --in 8h10m"
echo

echo "--------------------------------------"
echo " Installation complete."
echo "--------------------------------------"
echo
echo "This alarm does not ring."
echo "It demands compliance."
echo
