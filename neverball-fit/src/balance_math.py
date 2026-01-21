"""
Math utilities for balance board processing
"""

MIN_ACTIVE_WEIGHT = 8000  # raw units, empirisch gut


def total_weight(s):
    return (
        s["top_left"]
        + s["top_right"]
        + s["bottom_left"]
        + s["bottom_right"]
    )


def center_of_mass(s):
    total = total_weight(s)

    # ❌ Nobody on board → no movement
    if total < MIN_ACTIVE_WEIGHT:
        return 0.0, 0.0, False

    left = s["top_left"] + s["bottom_left"]
    right = s["top_right"] + s["bottom_right"]
    top = s["top_left"] + s["top_right"]
    bottom = s["bottom_left"] + s["bottom_right"]

    x = (right - left) / total
    y = (top - bottom) / total

    return x, y, True