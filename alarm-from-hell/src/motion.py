import time
from collections import deque
from enum import Enum, auto

import config


class MotionEvent(Enum):
    STOMP = auto()
    SQUAT = auto()
    STILLNESS = auto()
    NONE = auto()


class MotionDetector:
    """
    Detects motion events from calibrated weight samples (kg).
    """

    def __init__(self):
        # recent samples (time, kg)
        self.samples = deque(maxlen=30)

        # stomp detection
        self.last_stomp_time = 0.0

        # squat detection
        self.in_squat = False
        self.squat_min_weight = None

        # stillness
        self.last_movement_time = time.time()

    def update(self, weight_kg: float, timestamp: float) -> MotionEvent:
        self.samples.append((timestamp, weight_kg))

        if len(self.samples) < 5:
            return MotionEvent.NONE

        # -----------------------------
        # STOMP detection (windowed peak)
        # -----------------------------
        window = [
            w for (t, w) in self.samples
            if timestamp - t <= 0.15
        ]

        if len(window) >= 3:
            w_min = min(window)
            w_max = max(window)

            if (
                (w_max - w_min) >= config.STOMP_DELTA_KG
                and (timestamp - self.last_stomp_time) >= config.STOMP_COOLDOWN_SEC
            ):
                self.last_stomp_time = timestamp
                self.last_movement_time = timestamp
                return MotionEvent.STOMP

        # -----------------------------
        # Baseline (standing weight)
        # -----------------------------
        baseline = sum(w for _, w in self.samples) / len(self.samples)

        # -----------------------------
        # SQUAT detection
        # -----------------------------
        if not self.in_squat:
            if weight_kg < baseline - config.STILLNESS_TOLERANCE_KG:
                self.in_squat = True
                self.squat_min_weight = weight_kg
                self.last_movement_time = timestamp
        else:
            if weight_kg < self.squat_min_weight:
                self.squat_min_weight = weight_kg

            if weight_kg >= baseline - (config.STILLNESS_TOLERANCE_KG / 2):
                self.in_squat = False
                self.squat_min_weight = None
                self.last_movement_time = timestamp
                return MotionEvent.SQUAT

        # -----------------------------
        # STILLNESS detection
        # -----------------------------
        delta = abs(weight_kg - self.samples[-2][1])

        if delta > config.STILLNESS_TOLERANCE_KG:
            self.last_movement_time = timestamp
            return MotionEvent.NONE

        if (timestamp - self.last_movement_time) >= config.REQUIRED_STILL_TIME_SEC:
            return MotionEvent.STILLNESS

        return MotionEvent.NONE


# -----------------------------
# Test harness
# -----------------------------
if __name__ == "__main__":
    from board import WiiBalanceBoard

    board = WiiBalanceBoard()
    board.connect()

    detector = MotionDetector()

    print("Motion detector test running.")
    print("Try: stomp hard, squat slow, stand still.\n")

    try:
        for sample in board.read_samples():
            kg = config.raw_to_kg(sample["total"])
            ts = time.time()

            event = detector.update(kg, ts)
            if event != MotionEvent.NONE:
                print(f"{event.name:9} | {kg:6.1f} kg")

    except KeyboardInterrupt:
        print("\nStopping.")
    finally:
        board.close()
