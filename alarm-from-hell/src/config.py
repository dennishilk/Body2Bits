"""
Configuration for Alarm from Hell
"""

# =====================================================
# Difficulty preset
# =====================================================
# Choose one:
#   "easy"   – forgiving, demo-friendly
#   "normal" – realistic, physically demanding
#   "hell"   – strict, punishing, no mercy
PRESET = "normal"


# =====================================================
# Calibration (AUTO-GENERATED)
# =====================================================
# These values are written by calibration.py
# Do NOT edit manually unless you know what you are doing.

CALIBRATION_ZERO_OFFSET = 322.00
CALIBRATION_SCALE = 0.010231


def raw_to_kg(raw_total: float) -> float:
    return (raw_total - CALIBRATION_ZERO_OFFSET) * CALIBRATION_SCALE


# =====================================================
# Preset definitions
# =====================================================

PRESETS = {
    "easy": {
        # Weight detection
        "MIN_WEIGHT_KG": 15.0,

        # Squat / stomp
        "REQUIRED_SQUATS": 5,
        "STOMP_DELTA_KG": 20.0,
        "STOMP_COOLDOWN_SEC": 0.5,

        # Stillness
        "REQUIRED_STILL_TIME_SEC": 8.0,
        "STILLNESS_TOLERANCE_KG": 2.0,
    },

    "normal": {
        # Weight detection
        "MIN_WEIGHT_KG": 20.0,

        # Squat / stomp
        "REQUIRED_SQUATS": 8,
        "STOMP_DELTA_KG": 25.0,
        "STOMP_COOLDOWN_SEC": 0.6,

        # Stillness
        "REQUIRED_STILL_TIME_SEC": 15.0,
        "STILLNESS_TOLERANCE_KG": 1.5,
    },

    "hell": {
        # Weight detection
        "MIN_WEIGHT_KG": 25.0,

        # Squat / stomp
        "REQUIRED_SQUATS": 12,
        "STOMP_DELTA_KG": 35.0,
        "STOMP_COOLDOWN_SEC": 0.9,

        # Stillness
        "REQUIRED_STILL_TIME_SEC": 30.0,
        "STILLNESS_TOLERANCE_KG": 0.8,
    },
}


# =====================================================
# Apply selected preset
# =====================================================

if PRESET not in PRESETS:
    raise ValueError(
        f"Invalid PRESET '{PRESET}'. "
        f"Choose one of: {', '.join(PRESETS.keys())}"
    )

_cfg = PRESETS[PRESET]

MIN_WEIGHT_KG = _cfg["MIN_WEIGHT_KG"]

REQUIRED_SQUATS = _cfg["REQUIRED_SQUATS"]
STOMP_DELTA_KG = _cfg["STOMP_DELTA_KG"]
STOMP_COOLDOWN_SEC = _cfg["STOMP_COOLDOWN_SEC"]

REQUIRED_STILL_TIME_SEC = _cfg["REQUIRED_STILL_TIME_SEC"]
STILLNESS_TOLERANCE_KG = _cfg["STILLNESS_TOLERANCE_KG"]


# =====================================================
# Escalation (global, not preset-specific)
# =====================================================

ESCALATION_SQUAT_PENALTY = 2
ESCALATION_VOLUME_STEP = 0.15
ESCALATION_FREQUENCY_STEP = 120


# =====================================================
# Debug
# =====================================================

DEBUG_PRINT_STATE = True
