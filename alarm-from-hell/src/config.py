"""
Configuration for Alarm from Hell
"""

# -----------------------------
# Calibration (AUTO-GENERATED)
# -----------------------------
# These values are written by calibration.py
# Do not edit manually unless you know what you are doing.

CALIBRATION_ZERO_OFFSET = 322.00
0.0
CALIBRATION_SCALE = 0.010231
1.0

# -----------------------------
# Weight detection
# -----------------------------

MIN_WEIGHT_KG = 20.0

# -----------------------------
# Squat / Stomp requirements
# -----------------------------

REQUIRED_SQUATS = 8
STOMP_DELTA_KG = 25.0
STOMP_COOLDOWN_SEC = 0.6

# -----------------------------
# Stillness phase
# -----------------------------

REQUIRED_STILL_TIME_SEC = 5.0
STILLNESS_TOLERANCE_KG = 1.5

# -----------------------------
# Escalation
# -----------------------------

ESCALATION_SQUAT_PENALTY = 2
ESCALATION_VOLUME_STEP = 0.15
ESCALATION_FREQUENCY_STEP = 120

# -----------------------------
# Debug
# -----------------------------

DEBUG_PRINT_STATE = True


def raw_to_kg(raw_total: float) -> float:
    return (raw_total - CALIBRATION_ZERO_OFFSET) * CALIBRATION_SCALE
