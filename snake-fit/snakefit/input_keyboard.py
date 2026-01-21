"""
Snake-Fit – Keyboard Input
=========================

Simple, reliable keyboard fallback.
No timing, no magic – just directions.
"""

import snakefit.config as cfg


class KeyboardInput:
    def __init__(self):
        self.last_direction = None

    def get_direction(self, key_state):
        """
        key_state: dict like {"UP": bool, "DOWN": bool, ...}
        returns: direction string or None
        """

        direction = None

        if key_state.get("UP"):
            direction = "UP"
        elif key_state.get("DOWN"):
            direction = "DOWN"
        elif key_state.get("LEFT"):
            direction = "LEFT"
        elif key_state.get("RIGHT"):
            direction = "RIGHT"

        if direction is None:
            return None

        # Prevent 180° turns (classic Snake rule)
        if not cfg.ALLOW_REVERSE and self.last_direction:
            if (
                (direction == "UP" and self.last_direction == "DOWN") or
                (direction == "DOWN" and self.last_direction == "UP") or
                (direction == "LEFT" and self.last_direction == "RIGHT") or
                (direction == "RIGHT" and self.last_direction == "LEFT")
            ):
                return None

        self.last_direction = direction
        return direction