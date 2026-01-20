#!/usr/bin/env bash
set -e

echo "============================================="
echo " Alarm from Hell – Uninstaller By Dennis Hilk"
echo "============================================="
echo

echo "[INFO] This will remove system packages installed by installer.sh."
echo "[INFO] It will NOT:"
echo "  - delete project files"
echo "  - remove Bluetooth pairings"
echo "  - modify user configuration"
echo

read -p "Continue? [y/N] " confirm
if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
  echo "Aborted."
  exit 0
fi

echo
echo "[INFO] Removing system packages..."

sudo apt remove -y \
  python3-evdev \
  sox \
  libsox-fmt-alsa \
  bluez-tools \
  pulseaudio-utils

echo
echo "[INFO] Running autoremove..."
sudo apt autoremove -y

echo
echo "--------------------------------------"
echo " Uninstall complete."
echo "--------------------------------------"
echo
echo "Note:"
echo "- Bluetooth pairings were NOT removed."
echo "- Python 3 itself was NOT removed."
echo "- Project files are untouched."
echo
echo "You can safely delete the project directory manually if desired."
echo
