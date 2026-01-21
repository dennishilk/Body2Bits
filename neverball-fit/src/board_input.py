#!/usr/bin/env python3

"""
Wii Balance Board input reader for neverball-fit
"""

import time

class BalanceBoard:
    def __init__(self):
        self.connected = False

    def connect(self):
        print("[board] waiting for Wii Balance Board...")
        # Bluetooth HID logic goes here
        self.connected = True
        print("[board] connected")

    def read_weights(self):
        """
        Return raw weight data:
        {
            'top_left': kg,
            'top_right': kg,
            'bottom_left': kg,
            'bottom_right': kg
        }
        """
        return {
            "top_left": 0.0,
            "top_right": 0.0,
            "bottom_left": 0.0,
            "bottom_right": 0.0,
        }


if __name__ == "__main__":
    board = BalanceBoard()
    board.connect()

    while True:
        data = board.read_weights()
        print(data)
        time.sleep(0.1)
