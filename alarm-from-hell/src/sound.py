import subprocess
import time
import threading
import random
from pathlib import Path

import config


ASSETS_DIR = Path(__file__).parent.parent / "assets"
ALARM_WAV = ASSETS_DIR / "alarm.wav"


class AlarmSound:
    """
    WAV-based alarm using SoX.
    Escalation controls:
    - volume
    - playback speed
    - pause compression
    """

    def __init__(self):
        self._thread = None
        self._running = False
        self.escalation = 0
        self._process = None

    def start(self, escalation_level: int):
        self.escalation = escalation_level
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._process:
            self._process.terminate()
            self._process = None

    def _run(self):
        while self._running:
            e = self.escalation

            # Escalation parameters
            volume = min(1.0, 0.6 + e * 0.12)
            speed = min(1.6, 1.0 + e * 0.12)

            # random micro-variation prevents habituation
            speed += random.uniform(-0.03, 0.03)

            cmd = [
                "play",
                "-q",
                str(ALARM_WAV),
                "vol", f"{volume}",
                "speed", f"{speed}",
            ]

            try:
                self._process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                self._process.wait()
            except Exception:
                pass

            # Pause shrinks with escalation
            base_gap = 0.4
            gap = max(0.05, base_gap - e * 0.08)
            time.sleep(gap)
