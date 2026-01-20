import time
from statistics import mean
from pathlib import Path

from board import WiiBalanceBoard


SAMPLE_TIME_SEC = 5.0
CONFIG_FILE = Path(__file__).parent / "config.py"


class BoardCalibration:
    def __init__(self):
        self.zero_offset = 0.0
        self.scale = 1.0

    def measure_average(self, board: WiiBalanceBoard, duration: float):
        samples = []
        start = time.time()

        for sample in board.read_samples():
            samples.append(sample["total"])
            if time.time() - start >= duration:
                break

        return mean(samples)

    def write_config(self):
        text = CONFIG_FILE.read_text()

        def replace_value(name, value):
            nonlocal text
            text = text.replace(
                f"{name} = ",
                f"{name} = {value}\n# ",
                1
            ).replace(
                f"{name} = {value}\n# ",
                f"{name} = {value}\n",
                1
            )

        replace_value("CALIBRATION_ZERO_OFFSET", f"{self.zero_offset:.2f}")
        replace_value("CALIBRATION_SCALE", f"{self.scale:.6f}")

        CONFIG_FILE.write_text(text)

    def calibrate(self):
        board = WiiBalanceBoard()
        board.connect()

        try:
            print("\n=== Wii Balance Board Calibration ===\n")

            input("Step OFF the board completely. Press ENTER when ready...")
            print("Measuring zero offset...")
            self.zero_offset = self.measure_average(board, SAMPLE_TIME_SEC)
            print(f"Zero offset (raw): {self.zero_offset:.2f}\n")

            input("Step ON the board and stand still. Press ENTER when ready...")
            body_raw = self.measure_average(board, SAMPLE_TIME_SEC)
            print(f"Body weight raw average: {body_raw:.2f}")

            weight_kg = float(
                input("Enter your body weight in kg (e.g. 82.5): ")
            )

            self.scale = weight_kg / (body_raw - self.zero_offset)

            print("\nWriting calibration to config.py...")
            self.write_config()

            print("Calibration complete.")
            print(f"ZERO_OFFSET = {self.zero_offset:.2f}")
            print(f"SCALE       = {self.scale:.6f}")

        finally:
            board.close()


if __name__ == "__main__":
    calib = BoardCalibration()
    calib.calibrate()
